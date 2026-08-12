#!/usr/bin/env python3
"""Deterministic HTML durable-artifact conversion with embedded source recovery."""

from __future__ import annotations

import argparse
import base64
import csv
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - dependency gate exercised by CLI
    PdfReader = None


PACKET_ID = "html-this-source"
FORMAT_BY_SUFFIX = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".csv": "csv",
    ".json": "json",
    ".html": "html",
    ".htm": "html",
    ".pdf": "pdf",
}

CANONICAL_PROVENANCE_FIELDS = (
    "Content owner",
    "Original writing agent",
    "Original writing LLM",
    "Created",
    "Artifact role",
)
AMBIGUOUS_MODEL_IDENTITIES = {
    "chatgpt",
    "claude",
    "codex",
    "gemini",
    "gpt",
}
GPT_FAMILY_ONLY_RE = re.compile(r"^gpt[- ]?5(?:\.\d+)?$", re.I)


def validate_exact_model_identity(value: str) -> None:
    """Reject known family-only or agent-family substitutions on new writes."""
    model = value.strip()
    folded = model.casefold()
    if folded == "not recorded":
        return
    if (
        not model
        or folded in AMBIGUOUS_MODEL_IDENTITIES
        or GPT_FAMILY_ONLY_RE.fullmatch(model)
        or folded.endswith(" agent")
    ):
        raise ValueError(
            "Model identity must be a full exact model name or the honest "
            "Not recorded fallback; family-only and agent-family labels are invalid"
        )

def validate_provenance_rows(
    headers: list[str], rows: list[list[str]], *, enforce_exact_model: bool = False
) -> None:
    """Require exactly one ordered, non-empty row per canonical fact."""
    if [cell.casefold() for cell in headers] != ["field", "value"]:
        raise ValueError("Agent Provenance must use a two-column Field | Value table")
    if len(rows) < len(CANONICAL_PROVENANCE_FIELDS):
        raise ValueError("Agent Provenance table is missing one or more canonical facts")
    normalized = []
    for row in rows:
        if len(row) != 2 or not row[0].strip() or not row[1].strip():
            raise ValueError("Agent Provenance rows require non-empty Field and Value cells")
        normalized.append(row[0].strip().casefold())
    expected = [field.casefold() for field in CANONICAL_PROVENANCE_FIELDS]
    if normalized[: len(expected)] != expected:
        raise ValueError("Agent Provenance canonical rows must use the required identity and order")
    for field in expected:
        if normalized.count(field) != 1:
            raise ValueError("Agent Provenance canonical rows must appear exactly once")
    if enforce_exact_model:
        validate_exact_model_identity(rows[2][1])


def markdown_provenance_rows(source: str) -> list[list[str]] | None:
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    sections = [
        index
        for index, line in enumerate(lines)
        if re.fullmatch(r"#{1,6}\s+Agent Provenance\s*", line.strip(), re.I)
    ]
    if len(sections) > 1:
        raise ValueError("Artifact must contain exactly one Agent Provenance section")
    for index in sections:
        cursor = index + 1
        while cursor < len(lines) and not lines[cursor].strip():
            cursor += 1
        if cursor + 1 >= len(lines) or "|" not in lines[cursor] or not is_table_separator(lines[cursor + 1]):
            raise ValueError("Agent Provenance must be presented as a Field | Value table")
        headers = split_table_row(lines[cursor])
        cursor += 2
        rows: list[list[str]] = []
        while cursor < len(lines) and "|" in lines[cursor] and lines[cursor].strip():
            rows.append(split_table_row(lines[cursor]))
            cursor += 1
        validate_provenance_rows(headers, rows)
        return rows
    return None


def html_provenance_rows(source: str) -> list[list[str]] | None:
    tables = re.findall(
        r'<table\b[^>]*class=["\'][^"\']*\bprovenance-table\b[^"\']*["\'][^>]*>(.*?)</table>',
        source,
        re.I | re.S,
    )
    if len(tables) > 1:
        raise ValueError("Artifact must contain exactly one canonical provenance table")
    if not tables:
        return None
    markup = tables[0]
    headers = [
        html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
        for value in re.findall(r'<th\b[^>]*scope=["\']col["\'][^>]*>(.*?)</th>', markup, re.I | re.S)
    ]
    rows = [
        [
            html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip(),
            html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip(),
        ]
        for match in re.finditer(
            r'<tr\b[^>]*>\s*<th\b[^>]*scope=["\']row["\'][^>]*>(.*?)</th>\s*<td\b[^>]*>(.*?)</td>\s*</tr>',
            markup,
            re.I | re.S,
        )
    ]
    validate_provenance_rows(headers, rows)
    return rows


def load_structured_provenance(path: Path | None) -> list[list[str]] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Structured provenance JSON must be one Field-to-Value object")
    rows = [[str(key), str(value)] for key, value in payload.items()]
    validate_provenance_rows(["Field", "Value"], rows, enforce_exact_model=True)
    return rows


def provenance_table_html(rows: list[list[str]]) -> str:
    validate_provenance_rows(["Field", "Value"], rows)
    body = "".join(
        f'<tr><th scope="row">{inline_markup(field)}</th><td>{inline_markup(value)}</td></tr>'
        for field, value in rows
    )
    return (
        '<section class="provenance-section"><h2>Agent Provenance</h2>'
        '<div class="table-scroll provenance-table-wrap" role="region" '
        'aria-label="Agent provenance" tabindex="0"><table class="provenance-table">'
        '<caption>Durable artifact ownership and role</caption><thead><tr>'
        '<th scope="col">Field</th><th scope="col">Value</th></tr></thead><tbody>'
        + body
        + "</tbody></table></div></section>"
    )


def require_creation_provenance(
    source: str | bytes,
    source_format: str,
    structured_rows: list[list[str]] | None,
    exemption_reason: str | None,
) -> list[list[str]] | None:
    if exemption_reason:
        return None
    native_rows = None
    if source_format == "markdown" and isinstance(source, str):
        native_rows = markdown_provenance_rows(source)
    elif source_format == "html" and isinstance(source, str):
        native_rows = html_provenance_rows(source)
    if structured_rows and native_rows:
        raise ValueError(
            "Structured provenance cannot be combined with source-native canonical provenance"
        )
    if structured_rows:
        return structured_rows
    if native_rows:
        return None
    raise ValueError(
        "New first-party durable artifacts require canonical Agent Provenance; "
        "provide it in Markdown/HTML, use --provenance-json, or document an "
        "excluded operational/schema-sensitive input with --provenance-exempt-reason"
    )


def inline_markup(value: str) -> str:
    escaped = html.escape(value, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<a href="\2">\1</a>',
        escaped,
    )
    return escaped


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def suppress_matching_markdown_title(source: str, document_title: str | None) -> str:
    """Hide one leading H1 when the document chrome already renders that title.

    The embedded source remains byte-for-byte unchanged; suppression affects
    presentation only.
    """
    if not document_title:
        return source
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        match = re.fullmatch(r"#\s+(.+)", line.strip())
        if match and match.group(1).strip().casefold() == document_title.strip().casefold():
            del lines[index]
        break
    return "\n".join(lines)


def render_markdown(source: str, document_title: str | None = None) -> str:
    source = suppress_matching_markdown_title(source, document_title)
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    index = 0
    current_heading = ""

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline_markup(' '.join(item.strip() for item in paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>")
            list_kind = None

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                language = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
                out.append(
                    f"<pre><code{language}>{html.escape(chr(10).join(code_lines))}</code></pre>"
                )
                in_code = False
                code_lang = ""
                code_lines.clear()
            else:
                code_lines.append(line)
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            in_code = True
            code_lang = stripped[3:].strip()
            index += 1
            continue

        if (
            "|" in line
            and index + 1 < len(lines)
            and is_table_separator(lines[index + 1])
        ):
            flush_paragraph()
            close_list()
            headers = split_table_row(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1
            provenance = current_heading.casefold() == "agent provenance"
            if provenance:
                validate_provenance_rows(headers, rows)
            wrapper_class = "table-scroll provenance-table-wrap" if provenance else "table-scroll"
            table_class = ' class="provenance-table"' if provenance else ""
            region = ' role="region" aria-label="Agent provenance" tabindex="0"' if provenance else ""
            out.append(f'<div class="{wrapper_class}"{region}><table{table_class}>')
            if provenance:
                out.append('<caption>Durable artifact ownership and role</caption>')
            out.append("<thead><tr>")
            out.extend(f'<th scope="col">{inline_markup(cell)}</th>' for cell in headers)
            out.append("</tr></thead><tbody>")
            for row in rows:
                padded = row + [""] * (len(headers) - len(row))
                out.append("<tr>")
                if provenance:
                    out.append(f'<th scope="row">{inline_markup(padded[0])}</th>')
                    out.append(f"<td>{inline_markup(padded[1])}</td>")
                else:
                    out.extend(f"<td>{inline_markup(cell)}</td>" for cell in padded[: len(headers)])
                out.append("</tr>")
            out.append("</tbody></table></div>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            label = heading.group(2).strip()
            current_heading = label
            anchor = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
            out.append(f'<h{level} id="{html.escape(anchor)}">{inline_markup(label)}</h{level}>')
            index += 1
            continue

        unordered = re.match(r"^[-*+]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if unordered or ordered:
            flush_paragraph()
            wanted = "ul" if unordered else "ol"
            if list_kind != wanted:
                close_list()
                list_kind = wanted
                out.append(f"<{wanted}>")
            item = (unordered or ordered).group(1)
            checkbox = re.match(r"^\[([ xX])\]\s+(.+)$", item)
            if checkbox:
                checked = " checked" if checkbox.group(1).lower() == "x" else ""
                out.append(
                    f'<li class="check"><input type="checkbox" disabled{checked}>'
                    f"{inline_markup(checkbox.group(2))}</li>"
                )
            else:
                out.append(f"<li>{inline_markup(item)}</li>")
            index += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            close_list()
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip()[1:].strip())
                index += 1
            out.append(
                '<blockquote><p>'
                + inline_markup(" ".join(quote_lines))
                + "</p></blockquote>"
            )
            continue

        if re.fullmatch(r"([-*_])\1\1+", stripped):
            flush_paragraph()
            close_list()
            out.append("<hr>")
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            close_list()
        else:
            if current_heading.casefold() == "agent provenance":
                raise ValueError("Agent Provenance must be presented as a Field | Value table")
            paragraph.append(stripped)
        index += 1

    if in_code:
        out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    flush_paragraph()
    close_list()
    return "\n".join(out)


def render_csv(source: str) -> str:
    rows = list(csv.reader(io.StringIO(source)))
    if not rows:
        return '<div class="callout warning"><strong>Empty CSV</strong></div>'
    headers, data = rows[0], rows[1:]
    out = ['<div class="table-scroll"><table><thead><tr>']
    out.extend(f"<th>{html.escape(cell)}</th>" for cell in headers)
    out.append("</tr></thead><tbody>")
    for row in data:
        padded = row + [""] * (len(headers) - len(row))
        out.append("<tr>")
        out.extend(f"<td>{html.escape(cell)}</td>" for cell in padded[: len(headers)])
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def render_json(source: str) -> str:
    parsed = json.loads(source)
    if isinstance(parsed, list) and parsed and all(isinstance(item, dict) for item in parsed):
        keys: list[str] = []
        for item in parsed:
            for key in item:
                if key not in keys:
                    keys.append(key)
        output = ['<div class="table-scroll"><table><thead><tr>']
        output.extend(f"<th>{html.escape(str(key))}</th>" for key in keys)
        output.append("</tr></thead><tbody>")
        for item in parsed:
            output.append("<tr>")
            for key in keys:
                value = item.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                output.append(f"<td>{html.escape(str(value))}</td>")
            output.append("</tr>")
        output.append("</tbody></table></div>")
        return "\n".join(output)
    pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
    return f"<pre><code>{html.escape(pretty)}</code></pre>"


def render_text(source: str) -> str:
    blocks = re.split(r"\n\s*\n", source.strip())
    return "\n".join(f"<p>{inline_markup(block.replace(chr(10), ' '))}</p>" for block in blocks)


def render_source(source: str, source_format: str, document_title: str | None = None) -> str:
    if source_format == "markdown":
        return render_markdown(source, document_title)
    if source_format == "csv":
        return render_csv(source)
    if source_format == "json":
        return render_json(source)
    if source_format == "html":
        return source
    return render_text(source)


def source_packet(source: str | bytes, source_format: str) -> str:
    binary = isinstance(source, bytes)
    payload = source if binary else source.encode("utf-8")
    packet = {
        "schema": 2,
        "format": source_format,
        "encoding": "binary" if binary else "utf-8",
        "content_b64": base64.b64encode(payload).decode("ascii"),
    }
    encoded = base64.b64encode(
        json.dumps(packet, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    return (
        f'<script id="{PACKET_ID}" type="application/x.html-this-source">'
        f"{encoded}</script>"
    )


def extract_source_packet_bytes(document: str) -> tuple[bytes, str, str] | None:
    pattern = (
        rf'<script[^>]+id=["\']{re.escape(PACKET_ID)}["\'][^>]*>'
        rf"\s*([A-Za-z0-9+/=]+)\s*</script>"
    )
    match = re.search(pattern, document, flags=re.IGNORECASE)
    if not match:
        return None
    outer = base64.b64decode(match.group(1))
    packet = json.loads(outer.decode("utf-8"))
    if packet.get("schema") not in {1, 2}:
        raise ValueError("Unsupported html-this source packet")
    encoding = str(packet.get("encoding", "utf-8"))
    if encoding not in {"utf-8", "binary"}:
        raise ValueError("Unsupported html-this source encoding")
    source = base64.b64decode(packet["content_b64"])
    return source, str(packet["format"]), encoding


def extract_source_packet(document: str) -> tuple[str, str] | None:
    packet = extract_source_packet_bytes(document)
    if not packet:
        return None
    source, source_format, encoding = packet
    if encoding != "utf-8":
        return None
    return source.decode("utf-8"), source_format


def pdf_text(source: bytes) -> tuple[list[str], dict[str, str]]:
    if PdfReader is None:
        raise RuntimeError("PDF conversion requires pypdf from the host document runtime")
    reader = PdfReader(io.BytesIO(source))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    metadata = {
        str(key).lstrip("/"): str(value)
        for key, value in (reader.metadata or {}).items()
        if value is not None
    }
    return pages, metadata


def find_pdftoppm() -> str | None:
    executable = shutil.which("pdftoppm.exe") or shutil.which("pdftoppm")
    if executable and Path(executable).suffix.lower() == ".cmd":
        bundled = Path(executable).parents[2] / "native/poppler/Library/bin/pdftoppm.exe"
        if bundled.is_file():
            return str(bundled)
    return executable


def render_pdf_pages(input_path: Path, source: bytes) -> tuple[str, bool, int]:
    pages, metadata = pdf_text(source)
    page_images: list[bytes] = []
    renderer = find_pdftoppm()
    if renderer:
        with tempfile.TemporaryDirectory(prefix="html-this-pdf-") as temp_dir:
            prefix = Path(temp_dir) / "page"
            completed = subprocess.run(
                [renderer, "-png", "-r", "144", str(input_path), str(prefix)],
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "pdftoppm failed while rendering PDF pages: "
                    + completed.stderr.strip()
                )
            page_images = [
                page.read_bytes()
                for page in sorted(
                    Path(temp_dir).glob("page-*.png"),
                    key=lambda item: int(re.search(r"(\d+)$", item.stem).group(1)),
                )
            ]
            if len(page_images) != len(pages):
                raise RuntimeError("Rendered PDF page count does not match source PDF")

    out = ['<section class="pdf-document" aria-label="PDF page rendition">']
    if not page_images:
        out.append(
            '<div class="callout warning"><strong>Semantic rendition:</strong> '
            "page images were unavailable, so this HTML preserves extracted text "
            "but not exact page appearance.</div>"
        )
    for index, page_text_value in enumerate(pages, start=1):
        out.append(f'<article class="pdf-page" aria-labelledby="pdf-page-{index}">')
        out.append(f'<h2 id="pdf-page-{index}">Page {index}</h2>')
        if page_images:
            image_b64 = base64.b64encode(page_images[index - 1]).decode("ascii")
            out.append(
                f'<img class="pdf-page-image" src="data:image/png;base64,{image_b64}" '
                f'alt="Rendered appearance of PDF page {index}">'
            )
            out.append("<details><summary>Accessible extracted text</summary>")
        out.append(
            '<pre class="pdf-page-text"><code>'
            + html.escape(page_text_value or "[No extractable text on this page]")
            + "</code></pre>"
        )
        if page_images:
            out.append("</details>")
        out.append("</article>")
    if metadata:
        pairs = " ".join(
            f"<dt>{html.escape(key)}</dt><dd>{html.escape(value)}</dd>"
            for key, value in sorted(metadata.items())
        )
        out.append(f'<details><summary>PDF metadata</summary><dl>{pairs}</dl></details>')
    out.append("</section>")
    return "\n".join(out), bool(page_images), len(pages)

class SemanticMarkdownParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.href: str | None = None
        self.list_stack: list[str] = []
        self.in_pre = False
        self.in_script_or_style = 0
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"script", "style"}:
            self.in_script_or_style += 1
            return
        if self.in_script_or_style:
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "p":
            self.parts.append("\n\n")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "strong" or tag == "b":
            self.parts.append("**")
        elif tag == "em" or tag == "i":
            self.parts.append("*")
        elif tag == "code" and not self.in_pre:
            self.parts.append("`")
        elif tag == "pre":
            self.in_pre = True
            self.parts.append("\n\n```\n")
        elif tag in {"ul", "ol"}:
            self.list_stack.append(tag)
            self.parts.append("\n")
        elif tag == "li":
            marker = "1. " if self.list_stack and self.list_stack[-1] == "ol" else "- "
            self.parts.append("\n" + "  " * max(0, len(self.list_stack) - 1) + marker)
        elif tag == "blockquote":
            self.parts.append("\n\n> ")
        elif tag == "a":
            self.href = attrs_dict.get("href")
            self.parts.append("[")
        elif tag == "tr":
            self.row = []
        elif tag in {"th", "td"}:
            self.cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.in_script_or_style = max(0, self.in_script_or_style - 1)
            return
        if self.in_script_or_style:
            return
        if tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code" and not self.in_pre:
            self.parts.append("`")
        elif tag == "pre":
            self.parts.append("\n```\n")
            self.in_pre = False
        elif tag in {"ul", "ol"} and self.list_stack:
            self.list_stack.pop()
            self.parts.append("\n")
        elif tag == "a":
            self.parts.append(f"]({self.href})" if self.href else "]")
            self.href = None
        elif tag in {"th", "td"} and self.cell is not None and self.row is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.parts.append("\n| " + " | ".join(self.row) + " |")
            self.row = None

    def handle_data(self, data: str) -> None:
        if self.in_script_or_style:
            return
        if self.cell is not None:
            self.cell.append(data)
        else:
            self.parts.append(data)

    def markdown(self) -> str:
        result = "".join(self.parts)
        result = re.sub(r"[ \t]+\n", "\n", result)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip() + "\n"


def html_to_markdown(document: str) -> tuple[str, bool, str]:
    packet = extract_source_packet_bytes(document)
    if packet:
        source_bytes, source_format, encoding = packet
        if source_format == "pdf":
            pages, _ = pdf_text(source_bytes)
            markdown = "\n\n".join(
                f"## Page {index}\n\n{page or '[No extractable text]'}"
                for index, page in enumerate(pages, start=1)
            )
            return markdown.rstrip() + "\n", False, source_format
        if encoding == "utf-8":
            source = source_bytes.decode("utf-8")
            if source_format in {"markdown", "text"}:
                return source, True, source_format
            if source_format in {"csv", "json"}:
                return f"```{source_format}\n{source.rstrip()}\n```\n", True, source_format
            if source_format == "html":
                document = source
    parser = SemanticMarkdownParser()
    parser.feed(document)
    return parser.markdown(), False, "html"


STYLE = """
:root {
  --bg:#0e1116; --panel:#161b22; --panel2:#1c232c; --line:#2b333d;
  --ink:#e6edf3; --dim:#9aa7b4; --faint:#6e7c8c;
  --danger:#f7768e; --info:#7dcfff; --ok:#9ece6a; --warn:#e0af68; --accent:#bb9af7;
  --mono:ui-monospace,"Cascadia Mono","SFMono-Regular",Consolas,monospace;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg:#f6f8fa; --panel:#fff; --panel2:#eef2f6; --line:#d5dde5;
    --ink:#101720; --dim:#4a5663; --faint:#75828f;
    --danger:#b4233c; --info:#176b9f; --ok:#39731f; --warn:#8a5d00; --accent:#6540a8;
  }
}
* { box-sizing:border-box; min-width:0; }
html { scroll-behavior:smooth; overflow-x:hidden; }
body {
  margin:0; padding:30px 22px 80px; background:var(--bg); color:var(--ink);
  font:15px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  overflow-x:hidden;
}
.wrap { width:100%; max-width:1120px; margin:0 auto; }
.artifact-header { margin-bottom:28px; }
h1 { font-size:clamp(25px,4vw,34px); line-height:1.18; margin:0 0 7px; letter-spacing:-.025em; }
h2 { font-size:20px; margin:42px 0 10px; padding-bottom:8px; border-bottom:1px solid var(--line); }
h3 { font-size:16px; margin:25px 0 8px; color:var(--accent); }
h4,h5,h6 { margin:20px 0 7px; }
p { margin:10px 0; overflow-wrap:anywhere; }
.subtitle,.meta,.foot { color:var(--dim); }
.meta { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; font-size:12px; }
.pill {
  display:inline-block; padding:2px 9px; border:1px solid var(--line);
  background:var(--panel); border-radius:999px;
}
a { color:var(--info); text-underline-offset:2px; }
a:focus-visible { outline:2px solid var(--accent); outline-offset:3px; border-radius:2px; }
code { font-family:var(--mono); font-size:.9em; background:var(--panel2); padding:1px 5px; border-radius:4px; }
pre {
  background:#0a0d12; color:#e6edf3; border:1px solid var(--line); border-radius:8px;
  padding:14px 16px; overflow:auto; font:13px/1.55 var(--mono);
}
pre code { background:none; padding:0; }
blockquote,.callout {
  margin:16px 0; padding:13px 16px; background:var(--panel);
  border:1px solid var(--line); border-left:4px solid var(--warn); border-radius:7px;
}
ul,ol { padding-left:24px; }
li { margin:5px 0; overflow-wrap:anywhere; }
.check { list-style:none; margin-left:-20px; }
.check input { margin-right:8px; accent-color:var(--ok); }
.table-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch; margin:16px 0; }
table { border-collapse:collapse; width:100%; min-width:560px; font-size:13.5px; }
caption { padding:0 0 8px; color:var(--dim); font-size:12px; text-align:left; }
th,td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }
th {
  background:var(--panel2); color:var(--dim); font-size:12px; text-transform:uppercase;
  letter-spacing:.04em; white-space:nowrap;
}
tbody tr:hover { background:var(--panel); }
.provenance-table-wrap { width:100%; max-width:100%; overflow-x:hidden; border:1px solid var(--line); border-radius:9px; }
.provenance-table { width:100%; max-width:100%; min-width:0; table-layout:fixed; }
.provenance-table caption { padding:10px 12px 4px; }
.provenance-table th:first-child { width:34%; }
.provenance-table tbody th { background:transparent; color:var(--ink); text-transform:none; letter-spacing:0; white-space:normal; }
.provenance-table th,.provenance-table td { overflow-wrap:anywhere; word-break:normal; }
.provenance-table tbody tr:last-child th,.provenance-table tbody tr:last-child td { border-bottom:0; }
hr { border:0; border-top:1px solid var(--line); margin:30px 0; }
img,svg { max-width:100%; height:auto; }
.foot { margin-top:50px; padding-top:14px; border-top:1px solid var(--line); font-size:12px; }
.pdf-document { display:grid; gap:24px; }
.pdf-page { padding:16px; background:var(--panel); border:1px solid var(--line); border-radius:10px; }
.pdf-page h2 { margin-top:0; }
.pdf-page-image { display:block; width:100%; background:#fff; box-shadow:0 5px 22px #0005; }
.pdf-page-text { max-height:28rem; }
details summary { cursor:pointer; color:var(--info); margin:10px 0; }
dl { display:grid; grid-template-columns:minmax(8rem,auto) 1fr; gap:6px 14px; }
dt { color:var(--dim); font-weight:700; }
dd { margin:0; overflow-wrap:anywhere; }
@media (max-width:680px) {
  body { padding:22px 14px 60px; }
  h2 { margin-top:34px; }
  h1 { overflow-wrap:anywhere; }
  .provenance-table th:first-child { width:40%; }
  .provenance-table th,.provenance-table td { padding:8px; }
}
@media print {
  :root { --bg:#fff; --panel:#fff; --panel2:#f2f4f7; --line:#ccd2d8; --ink:#111; --dim:#444; }
  body { padding:0; background:#fff; color:#111; font-size:10.5pt; }
  .wrap { max-width:none; }
  a { color:#111; text-decoration:underline; }
  pre { white-space:pre-wrap; color:#111; background:#f5f5f5; break-inside:avoid; }
  table,blockquote,.callout { break-inside:avoid; }
  .provenance-table-wrap { overflow:visible; border-color:#777; }
  .provenance-table { min-width:0; }
  h1,h2,h3 { break-after:avoid; }
  .foot { display:none; }
}
""".strip()


def build_document(
    body: str,
    source: str | bytes,
    source_format: str,
    title: str,
    artifact_kind: str,
    status: str,
) -> str:
    safe_title = html.escape(title)
    safe_kind = html.escape(artifact_kind)
    safe_status = html.escape(status)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="html-this">
<meta name="artifact-kind" content="{safe_kind}">
<meta name="artifact-status" content="{safe_status}">
<title>{safe_title}</title>
<style>
{STYLE}
</style>
</head>
<body>
<main class="wrap">
<header class="artifact-header">
<h1>{safe_title}</h1>
<div class="meta"><span class="pill">{safe_kind}</span><span class="pill">{safe_status}</span></div>
</header>
{body}
<footer class="foot">Self-contained durable artifact generated with html-this.</footer>
</main>
{source_packet(source, source_format)}
</body>
</html>
"""


def inspect_html(document: str) -> dict[str, object]:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", document, re.I | re.S)
    image_tags = re.findall(r"<img\b[^>]*>", document, re.I)
    missing_alt = [tag for tag in image_tags if not re.search(r"\balt\s*=", tag, re.I)]
    external_assets = re.findall(
        r"<(?:img|script|link)\b[^>]*(?:src|href)=[\"'](https?://[^\"']+)",
        document,
        re.I,
    )
    packet = extract_source_packet_bytes(document)
    provenance_table = re.search(
        r'<table\b[^>]*class=["\'][^"\']*\bprovenance-table\b[^"\']*["\'][^>]*>(.*?)</table>',
        document,
        re.I | re.S,
    )
    provenance_markup = provenance_table.group(1) if provenance_table else ""
    provenance_rows = []
    for match in re.finditer(
        r'<tr\b[^>]*>\s*<th\b[^>]*scope=["\']row["\'][^>]*>(.*?)</th>\s*<td\b[^>]*>(.*?)</td>\s*</tr>',
        provenance_markup,
        re.I | re.S,
    ):
        provenance_rows.append([
            html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip(),
            html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip(),
        ])
    try:
        validate_provenance_rows(["Field", "Value"], provenance_rows)
        canonical_provenance = True
    except ValueError:
        canonical_provenance = False
    checks = {
        "doctype_count": len(re.findall(r"<!doctype\s+html", document, re.I)),
        "html_open_count": len(re.findall(r"<html\b", document, re.I)),
        "html_close_count": len(re.findall(r"</html\s*>", document, re.I)),
        "utf8_meta": bool(re.search(r"<meta[^>]+charset=[\"']?utf-8", document, re.I)),
        "viewport_meta": bool(re.search(r"<meta[^>]+name=[\"']viewport[\"']", document, re.I)),
        "title": html.unescape(title_match.group(1).strip()) if title_match else "",
        "embedded_source": bool(packet),
        "embedded_source_format": packet[1] if packet else None,
        "external_asset_urls": external_assets,
        "images": len(image_tags),
        "images_missing_alt": len(missing_alt),
        "provenance_table": bool(provenance_table),
        "provenance_canonical_rows": canonical_provenance,
        "provenance_definition_list": bool(
            re.search(r"<h[1-6][^>]*>\s*Agent Provenance\s*</h[1-6]>\s*<dl\b", document, re.I)
        ),
    }
    checks["structure_valid"] = bool(
        checks["doctype_count"] == 1
        and checks["html_open_count"] == 1
        and checks["html_close_count"] == 1
        and checks["utf8_meta"]
        and checks["viewport_meta"]
        and checks["title"]
        and not external_assets
        and not missing_alt
    )
    return checks


def infer_format(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    try:
        return FORMAT_BY_SUFFIX[path.suffix.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported input extension: {path.suffix}") from exc


def default_output(input_path: Path, target: str) -> Path:
    return input_path.with_suffix(".html" if target == "html" else ".md")


def atomic_write(path: Path, data: bytes, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing output: {path}")
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--to", choices=("html", "markdown", "inspect"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--source-format",
        choices=("markdown", "text", "csv", "json", "html", "pdf"),
    )
    parser.add_argument("--title")
    parser.add_argument("--artifact-kind", default="Durable Artifact")
    parser.add_argument("--status", default="Current")
    parser.add_argument("--provenance-json", type=Path)
    parser.add_argument("--provenance-exempt-reason")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if args.to == "inspect":
        document = input_path.read_text(encoding="utf-8")
        result = {"input": str(input_path), "target": "inspect", **inspect_html(document)}
        print(json.dumps(result, ensure_ascii=False))
        return 0

    output = (args.output or default_output(input_path, args.to)).resolve()
    if output == input_path:
        raise ValueError("Input and output paths must differ")

    if args.to == "html":
        source_format = infer_format(input_path, args.source_format)
        title = args.title or input_path.stem
        visual_fidelity: bool | None = None
        page_count: int | None = None
        if source_format == "pdf":
            source: str | bytes = input_path.read_bytes()
            body, visual_fidelity, page_count = render_pdf_pages(input_path, source)
        else:
            source = input_path.read_text(encoding="utf-8")
            body = render_source(source, source_format, title)
        structured_rows = load_structured_provenance(
            args.provenance_json.resolve() if args.provenance_json else None
        )
        injected_rows = require_creation_provenance(
            source,
            source_format,
            structured_rows,
            args.provenance_exempt_reason,
        )
        if injected_rows:
            body = provenance_table_html(injected_rows) + "\n" + body
        document = build_document(
            body,
            source,
            source_format,
            title,
            args.artifact_kind,
            args.status,
        )
        atomic_write(output, document.encode("utf-8"), args.force)
        recovered = extract_source_packet_bytes(document)
        expected_bytes = source if isinstance(source, bytes) else source.encode("utf-8")
        expected_encoding = "binary" if isinstance(source, bytes) else "utf-8"
        if recovered != (expected_bytes, source_format, expected_encoding):
            raise RuntimeError("Embedded source packet failed round-trip verification")
        inspection = inspect_html(document)
        if not inspection["structure_valid"]:
            raise RuntimeError("Generated HTML failed structural verification")
        result = {
            "output": str(output),
            "target": "html",
            "source_format": source_format,
            "embedded_source": True,
            "exact_recovery_verified": True,
            "structure_verified": True,
        }
        if source_format == "pdf":
            result.update(
                {
                    "pages": page_count,
                    "visual_page_rendition": visual_fidelity,
                    "accessible_text_included": True,
                }
            )
    else:
        document = input_path.read_text(encoding="utf-8")
        markdown, exact, recovered_format = html_to_markdown(document)
        atomic_write(output, markdown.encode("utf-8"), args.force)
        result = {
            "output": str(output),
            "target": "markdown",
            "source_format": recovered_format,
            "exact_recovery": exact,
        }
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"html-this: {error}", file=sys.stderr)
        raise SystemExit(1)
