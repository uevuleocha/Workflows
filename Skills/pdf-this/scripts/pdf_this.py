#!/usr/bin/env python3
"""Professional PDF durable-artifact conversion with embedded source recovery."""

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
import textwrap
from typing import Iterable

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4, LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        KeepTogether,
        ListFlowable,
        ListItem,
        PageTemplate,
        Paragraph,
        Preformatted,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError as exc:  # pragma: no cover - dependency preflight
    raise SystemExit(
        f"missing dependency: {exc.name or exc}; "
        "install with: python -m pip install pypdf reportlab"
    ) from exc


FORMAT_BY_SUFFIX = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".csv": "csv",
    ".json": "json",
    ".html": "html",
    ".htm": "html",
}
SOURCE_PREFIX = "pdf-this-source."
HTML_PACKET_ID = "html-this-source"
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


def load_structured_provenance(path: Path | None) -> list[list[str]] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Structured provenance JSON must be one Field-to-Value object")
    rows = [[str(key), str(value)] for key, value in payload.items()]
    validate_provenance_rows(["Field", "Value"], rows, enforce_exact_model=True)
    return rows


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
    table = tables[0]
    headers = [
        html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
        for value in re.findall(r'<th\b[^>]*scope=["\']col["\'][^>]*>(.*?)</th>', table, re.I | re.S)
    ]
    rows = []
    for match in re.finditer(
        r'<tr\b[^>]*>\s*<th\b[^>]*scope=["\']row["\'][^>]*>(.*?)</th>\s*<td\b[^>]*>(.*?)</td>\s*</tr>',
        table,
        re.I | re.S,
    ):
        rows.append([
            html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip(),
            html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip(),
        ])
    validate_provenance_rows(headers, rows)
    return rows


def require_creation_provenance(
    source: str,
    source_format: str,
    structured_rows: list[list[str]] | None,
    exemption_reason: str | None,
) -> list[list[str]] | None:
    if exemption_reason:
        return None
    if source_format == "html":
        native_rows = html_provenance_rows(source)
        if structured_rows and native_rows:
            raise ValueError(
                "Structured provenance cannot be combined with source-native canonical provenance"
            )
        if native_rows:
            return None
        raise ValueError(
            "New first-party durable HTML artifacts require a canonical semantic "
            "Agent Provenance table in the source HTML; --provenance-json cannot "
            "be injected into the browser-print path"
        )
    native_rows = markdown_provenance_rows(source) if source_format == "markdown" else None
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


def safe_text(value: str) -> str:
    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2705": "[Complete]",
        "\u2713": "yes",
        "\u2714": "yes",
        "\u26a0\ufe0f": "[Warning]",
        "\u26a0": "[Warning]",
        "\U0001f7e3": "[Purple]",
        "\U0001f7e2": "[Green]",
        "\U0001f7e1": "[Yellow]",
        "\U0001f534": "[Red]",
        "\U0001f31f": "[Star]",
        "\U0001f320": "[Star]",
        "\U0001f4ab": "[Star]",
        "\u2728": "[Star]",
        "\u2726": "[Star]",
        "\u2727": "[Star]",
        "\u2734\ufe0f": "[Star]",
        "\u2734": "[Star]",
        "\U0001f3ad": "",
        "\u2192": "->",
        "\u2190": "<-",
        "\u2194": "<->",
        "\u2022": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def paragraph_markup(value: str) -> str:
    escaped = html.escape(safe_text(value), quote=False)
    escaped = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<link href="\2" color="#176b9f">\1</link>',
        escaped,
    )
    return escaped


def wrap_preformatted(value: str, width: int = 94) -> str:
    wrapped: list[str] = []
    for line in safe_text(value).splitlines():
        indent = re.match(r"^\s*", line).group(0)
        available = max(24, width - len(indent))
        chunks = textwrap.wrap(
            line[len(indent) :],
            width=available,
            replace_whitespace=False,
            drop_whitespace=False,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""]
        wrapped.extend(indent + chunk.rstrip() for chunk in chunks)
    return "\n".join(wrapped)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


class VisibleHTML(HTMLParser):
    BLOCKS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "div",
        "figcaption",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "p",
        "section",
        "table",
        "tr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        elif not self.hidden and tag in self.BLOCKS:
            self.parts.append("\n")
        elif not self.hidden and tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        elif not self.hidden and tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)

    def text(self) -> str:
        joined = "".join(self.parts)
        joined = re.sub(r"[ \t]+", " ", joined)
        joined = re.sub(r"\n\s*\n\s*\n+", "\n\n", joined)
        return joined.strip() + "\n"


def extract_html_packet(document: str) -> tuple[str, str] | None:
    pattern = (
        rf'<script[^>]+id=["\']{re.escape(HTML_PACKET_ID)}["\'][^>]*>'
        rf"\s*([A-Za-z0-9+/=]+)\s*</script>"
    )
    match = re.search(pattern, document, flags=re.IGNORECASE)
    if not match:
        return None
    packet = json.loads(base64.b64decode(match.group(1)).decode("utf-8"))
    source = base64.b64decode(packet["content_b64"]).decode("utf-8")
    return source, str(packet["format"])


def normalize_source(source: str, source_format: str) -> tuple[str, str]:
    if source_format != "html":
        return source, source_format
    packet = extract_html_packet(source)
    if packet:
        return packet
    parser = VisibleHTML()
    parser.feed(source)
    return parser.text(), "text"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ArtifactTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            textColor=colors.HexColor("#101720"),
            alignment=TA_LEFT,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ArtifactMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#586574"),
            spaceAfter=18,
        )
    )
    for name, size, leading, color, before, after in [
        ("H1x", 18, 22, "#101720", 20, 8),
        ("H2x", 14, 18, "#6540a8", 17, 6),
        ("H3x", 11.5, 15, "#101720", 13, 5),
    ]:
        styles.add(
            ParagraphStyle(
                name=name,
                parent=styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=size,
                leading=leading,
                textColor=colors.HexColor(color),
                spaceBefore=before,
                spaceAfter=after,
                keepWithNext=True,
            )
        )
    styles.add(
        ParagraphStyle(
            name="BodyX",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=14.4,
            textColor=colors.HexColor("#18212b"),
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="QuoteX",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9.4,
            leading=14,
            leftIndent=14,
            rightIndent=8,
            borderColor=colors.HexColor("#e0af68"),
            borderWidth=0,
            borderPadding=8,
            backColor=colors.HexColor("#f6f7f9"),
            spaceBefore=6,
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeX",
            fontName="Courier",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#18212b"),
            backColor=colors.HexColor("#f2f4f7"),
            borderColor=colors.HexColor("#d5dde5"),
            borderWidth=0.5,
            borderPadding=8,
            spaceBefore=5,
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallX",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.6,
            leading=10,
            textColor=colors.HexColor("#586574"),
            alignment=TA_CENTER,
        )
    )
    return styles


def table_flowable(rows: list[list[str]], available_width: float, styles, provenance: bool = False):
    if not rows:
        return Spacer(1, 1)
    width = max(1, len(rows[0]))
    normalized = [row + [""] * (width - len(row)) for row in rows]
    cell_style = ParagraphStyle(
        "CellX",
        parent=styles["BodyX"],
        fontSize=7.7,
        leading=10,
        spaceAfter=0,
    )
    head_style = ParagraphStyle(
        "CellHeadX",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#ffffff"),
    )
    rendered = []
    for row_index, row in enumerate(normalized):
        rendered.append(
            [
                Paragraph(paragraph_markup(str(cell)), head_style if row_index == 0 else cell_style)
                for cell in row
            ]
        )
    col_widths = (
        [available_width * 0.34, available_width * 0.66]
        if provenance and width == 2
        else [available_width / width] * width
    )
    table = Table(rendered, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                *(((("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),)) if provenance else ()),
            ]
        )
    )
    return table


def suppress_matching_markdown_title(source: str, document_title: str | None) -> str:
    """Hide one leading H1 when the PDF chrome already renders that title.

    The attached source remains byte-for-byte unchanged; suppression affects
    the ReportLab presentation only.
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


def markdown_story(
    source: str,
    styles,
    available_width: float,
    document_title: str | None = None,
) -> list:
    source = suppress_matching_markdown_title(source, document_title)
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    story: list = []
    paragraph: list[str] = []
    index = 0
    in_code = False
    code_lines: list[str] = []
    current_heading = ""

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(item.strip() for item in paragraph)
            story.append(Paragraph(paragraph_markup(text), styles["BodyX"]))
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if in_code:
            if stripped.startswith("```"):
                story.append(Preformatted(wrap_preformatted("\n".join(code_lines)), styles["CodeX"]))
                code_lines.clear()
                in_code = False
            else:
                code_lines.append(line)
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            in_code = True
            index += 1
            continue

        if (
            "|" in line
            and index + 1 < len(lines)
            and is_table_separator(lines[index + 1])
        ):
            flush_paragraph()
            rows = [split_table_row(line)]
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1
            provenance = current_heading.casefold() == "agent provenance"
            if provenance:
                validate_provenance_rows(rows[0], rows[1:])
            story.extend([table_flowable(rows, available_width, styles, provenance), Spacer(1, 8)])
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            current_heading = heading.group(2).strip()
            style_name = "H1x" if level == 1 else "H2x" if level == 2 else "H3x"
            story.append(Paragraph(paragraph_markup(heading.group(2)), styles[style_name]))
            index += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            quote: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip()[1:].strip())
                index += 1
            story.append(Paragraph(paragraph_markup(" ".join(quote)), styles["QuoteX"]))
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if bullet or ordered:
            flush_paragraph()
            items: list[ListItem] = []
            ordered_mode = bool(ordered)
            while index < len(lines):
                current = lines[index].strip()
                match = (
                    re.match(r"^\d+[.)]\s+(.+)$", current)
                    if ordered_mode
                    else re.match(r"^[-*+]\s+(.+)$", current)
                )
                if not match:
                    break
                item_text = match.group(1)
                checkbox = re.match(r"^\[([ xX])\]\s+(.+)$", item_text)
                if checkbox:
                    mark = "[x]" if checkbox.group(1).lower() == "x" else "[ ]"
                    item_text = f"{mark} {checkbox.group(2)}"
                items.append(ListItem(Paragraph(paragraph_markup(item_text), styles["BodyX"])))
                index += 1
            story.append(
                ListFlowable(
                    items,
                    bulletType="1" if ordered_mode else "bullet",
                    leftIndent=18,
                    start="1" if ordered_mode else "-",
                    bulletFontName="Helvetica",
                    bulletFontSize=8,
                    spaceAfter=7,
                )
            )
            continue

        if re.fullmatch(r"([-*_])\1\1+", stripped):
            flush_paragraph()
            story.append(Spacer(1, 8))
            index += 1
            continue

        if not stripped:
            flush_paragraph()
        else:
            if current_heading.casefold() == "agent provenance":
                raise ValueError("Agent Provenance must be presented as a Field | Value table")
            paragraph.append(stripped)
        index += 1

    if in_code:
        story.append(Preformatted(wrap_preformatted("\n".join(code_lines)), styles["CodeX"]))
    flush_paragraph()
    return story


def csv_story(source: str, styles, available_width: float) -> list:
    rows = list(csv.reader(io.StringIO(source)))
    return [table_flowable(rows, available_width, styles)]


def json_story(source: str, styles, available_width: float) -> list:
    parsed = json.loads(source)
    if isinstance(parsed, list) and parsed and all(isinstance(item, dict) for item in parsed):
        keys: list[str] = []
        for item in parsed:
            for key in item:
                if key not in keys:
                    keys.append(key)
        rows = [keys]
        for item in parsed:
            row = []
            for key in keys:
                value = item.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                row.append(str(value))
            rows.append(row)
        return [table_flowable(rows, available_width, styles)]
    pretty = json.dumps(parsed, ensure_ascii=False, indent=2)
    return [Preformatted(wrap_preformatted(pretty), styles["CodeX"])]


def source_story(
    source: str,
    source_format: str,
    styles,
    available_width: float,
    document_title: str | None = None,
) -> list:
    if source_format == "markdown":
        return markdown_story(source, styles, available_width, document_title)
    if source_format == "csv":
        return csv_story(source, styles, available_width)
    if source_format == "json":
        return json_story(source, styles, available_width)
    if source_format == "html":
        parser = VisibleHTML()
        parser.feed(source)
        source = parser.text()
    return [
        Paragraph(paragraph_markup(block.replace("\n", " ")), styles["BodyX"])
        for block in re.split(r"\n\s*\n", source.strip())
        if block.strip()
    ]


def draw_page_header_footer(pdf_canvas, document) -> None:
    page_width, page_height = document.pagesize
    pdf_canvas.saveState()
    pdf_canvas.setStrokeColor(colors.HexColor("#d5dde5"))
    pdf_canvas.setLineWidth(0.35)
    pdf_canvas.line(
        0.72 * inch, page_height - 0.53 * inch,
        page_width - 0.72 * inch, page_height - 0.53 * inch,
    )
    pdf_canvas.setFont("Helvetica", 7.2)
    pdf_canvas.setFillColor(colors.HexColor("#586574"))
    if document.page > 1:
        original_title = safe_text(document.title or "Durable artifact")
        title = original_title
        max_width = page_width - 2.0 * inch
        while title and stringWidth(title + "...", "Helvetica", 7.2) > max_width:
            title = title[:-1]
        if title != original_title:
            title += "..."
        pdf_canvas.drawString(0.72 * inch, page_height - 0.40 * inch, title)
    pdf_canvas.line(0.72 * inch, 0.52 * inch, page_width - 0.72 * inch, 0.52 * inch)
    pdf_canvas.drawString(0.72 * inch, 0.35 * inch, "Durable artifact")
    pdf_canvas.drawRightString(
        page_width - 0.72 * inch, 0.35 * inch, f"Page {document.page}"
    )
    pdf_canvas.restoreState()


class ArtifactDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, pagesize, **kwargs):
        super().__init__(filename, pagesize=pagesize, **kwargs)
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="body",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="artifact", frames=[frame], onPage=draw_page_header_footer))


def create_pdf(
    target: Path,
    source: str,
    source_format: str,
    title: str,
    artifact_kind: str,
    status: str,
    page_size: str,
    force: bool,
    provenance_rows: list[list[str]] | None = None,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing output: {target}")

    page_geometry = LETTER if page_size == "letter" else A4
    handle1, raw_name = tempfile.mkstemp(prefix=".pdf-this-layout.", suffix=".pdf", dir=target.parent)
    os.close(handle1)
    handle2, final_name = tempfile.mkstemp(prefix=".pdf-this-final.", suffix=".pdf", dir=target.parent)
    os.close(handle2)
    try:
        styles = build_styles()
        doc = ArtifactDocTemplate(
            raw_name,
            pagesize=page_geometry,
            leftMargin=0.72 * inch,
            rightMargin=0.72 * inch,
            topMargin=0.72 * inch,
            bottomMargin=0.70 * inch,
            title=safe_text(title),
            author="pdf-this",
            subject=safe_text(artifact_kind),
        )
        normalized_source, normalized_format = normalize_source(source, source_format)
        story = [
            Paragraph(paragraph_markup(title), styles["ArtifactTitle"]),
            Paragraph(
                paragraph_markup(f"{artifact_kind} | {status}"),
                styles["ArtifactMeta"],
            ),
        ]
        if provenance_rows:
            story.append(Paragraph("Agent Provenance", styles["H1x"]))
            story.append(
                table_flowable(
                    [["Field", "Value"], *provenance_rows],
                    doc.width,
                    styles,
                    True,
                )
            )
            story.append(Spacer(1, 8))
        story.extend(
            source_story(
                normalized_source,
                normalized_format,
                styles,
                doc.width,
                title,
            )
        )
        story.append(Spacer(1, 14))
        story.append(
            Paragraph(
                "Self-contained durable artifact generated with pdf-this.",
                styles["SmallX"],
            )
        )
        doc.build(story)

        reader = PdfReader(raw_name)
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        attachment_name = SOURCE_PREFIX + normalized_format
        writer.add_attachment(attachment_name, normalized_source.encode("utf-8"))
        writer.add_metadata(
            {
                "/Title": safe_text(title),
                "/Author": "pdf-this",
                "/Subject": safe_text(artifact_kind),
                "/Keywords": f"pdf-this;{safe_text(status)};embedded-source",
                "/PdfThisSourceFormat": normalized_format,
            }
        )
        with open(final_name, "wb") as stream:
            writer.write(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(final_name, target)
    finally:
        for temp_path in (raw_name, final_name):
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass


def resolve_pdf_object(value):
    return value.get_object() if hasattr(value, "get_object") else value


def indirect_identity(value) -> tuple[int, int] | None:
    reference = getattr(value, "indirect_reference", None)
    if reference is None and hasattr(value, "idnum"):
        reference = value
    if reference is None:
        return None
    return int(reference.idnum), int(reference.generation)


def widget_name(widget) -> str | None:
    current = resolve_pdf_object(widget)
    visited: set[tuple[int, int]] = set()
    while current is not None:
        identity = indirect_identity(current)
        if identity and identity in visited:
            break
        if identity:
            visited.add(identity)
        if current.get("/T") is not None:
            return str(current.get("/T"))
        parent = current.get("/Parent")
        current = resolve_pdf_object(parent) if parent is not None else None
    return None


def widget_value(widget):
    current = resolve_pdf_object(widget)
    visited: set[tuple[int, int]] = set()
    while current is not None:
        identity = indirect_identity(current)
        if identity and identity in visited:
            break
        if identity:
            visited.add(identity)
        if current.get("/V") is not None:
            return current.get("/V")
        parent = current.get("/Parent")
        current = resolve_pdf_object(parent) if parent is not None else None
    return None


def enumerate_widgets(reader: PdfReader) -> list[dict[str, object]]:
    widgets: list[dict[str, object]] = []
    for page_index, page in enumerate(reader.pages, start=1):
        for reference in page.get("/Annots", []):
            annotation = resolve_pdf_object(reference)
            if annotation.get("/Subtype") != "/Widget":
                continue
            appearance = resolve_pdf_object(annotation.get("/AP")) if annotation.get("/AP") else None
            normal = resolve_pdf_object(appearance.get("/N")) if appearance and appearance.get("/N") else None
            widgets.append(
                {
                    "page": page_index,
                    "name": widget_name(reference),
                    "value": None if widget_value(reference) is None else str(widget_value(reference)),
                    "has_parent": annotation.get("/Parent") is not None,
                    "identity": indirect_identity(reference) or indirect_identity(annotation),
                    "appearance": normal is not None,
                }
            )
    return widgets


def pdf_has_signatures(reader: PdfReader) -> bool:
    fields = reader.get_fields() or {}
    if any(str(resolve_pdf_object(field).get("/FT")) == "/Sig" for field in fields.values()):
        return True
    acroform = resolve_pdf_object(reader.root_object.get("/AcroForm"))
    return bool(acroform and acroform.get("/SigFlags"))


def inspect_pdf(path: Path) -> dict[str, object]:
    reader = PdfReader(str(path))
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs require an explicitly supported password workflow")
    fields = reader.get_fields() or {}
    widgets = enumerate_widgets(reader)
    page_sizes = []
    searchable_pages = 0
    for page in reader.pages:
        width = round(float(page.mediabox.width), 2)
        height = round(float(page.mediabox.height), 2)
        page_sizes.append({"width_points": width, "height_points": height})
        if (page.extract_text() or "").strip():
            searchable_pages += 1
    metadata = {
        str(key).lstrip("/"): str(value)
        for key, value in (reader.metadata or {}).items()
        if value is not None
    }
    return {
        "input": str(path),
        "pages": len(reader.pages),
        "page_sizes": page_sizes,
        "metadata": metadata,
        "searchable_pages": searchable_pages,
        "fully_searchable": bool(reader.pages) and searchable_pages == len(reader.pages),
        "fields": len(fields),
        "widgets": len(widgets),
        "widgets_missing_appearance": sum(not item["appearance"] for item in widgets),
        "signed_or_signature_fields": pdf_has_signatures(reader),
        "attachments": [name for name, _ in iter_attachments(reader)],
        "file_size": path.stat().st_size,
    }


def find_browser() -> str | None:
    for name in ("google-chrome", "chrome", "chromium", "chromium-browser", "msedge"):
        executable = shutil.which(name)
        if executable:
            return executable
    candidates = [
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    return str(next((path for path in candidates if path.is_file()), "")) or None


def create_pdf_from_html(
    target: Path,
    input_path: Path,
    source: str,
    title: str,
    artifact_kind: str,
    status: str,
    force: bool,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing output: {target}")
    browser = find_browser()
    if not browser:
        raise RuntimeError(
            "Faithful HTML conversion requires Chrome, Edge, Chromium, or another "
            "browser renderer; no supported browser executable was found"
        )
    handle1, rendered_name = tempfile.mkstemp(
        prefix=".pdf-this-browser.", suffix=".pdf", dir=target.parent
    )
    os.close(handle1)
    os.unlink(rendered_name)
    handle2, final_name = tempfile.mkstemp(
        prefix=".pdf-this-final.", suffix=".pdf", dir=target.parent
    )
    os.close(handle2)
    try:
        with tempfile.TemporaryDirectory(prefix="pdf-this-browser-profile-") as profile:
            completed = subprocess.run(
                [
                    browser,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--no-pdf-header-footer",
                    f"--user-data-dir={profile}",
                    f"--print-to-pdf={rendered_name}",
                    input_path.as_uri(),
                ],
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
        rendered_path = Path(rendered_name)
        if completed.returncode != 0 or not rendered_path.is_file() or rendered_path.stat().st_size == 0:
            raise RuntimeError(
                "Browser print-to-PDF failed: "
                + (completed.stderr.strip() or completed.stdout.strip() or "no PDF produced")
            )
        reader = PdfReader(rendered_name)
        if not reader.pages:
            raise RuntimeError("Browser renderer produced a PDF with no pages")
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        writer.add_attachment(SOURCE_PREFIX + "html", source.encode("utf-8"))
        writer.add_metadata(
            {
                "/Title": safe_text(title),
                "/Author": "pdf-this",
                "/Subject": safe_text(artifact_kind),
                "/Keywords": f"pdf-this;{safe_text(status)};embedded-source;browser-rendered",
                "/PdfThisSourceFormat": "html",
                "/PdfThisRenderer": Path(browser).name,
            }
        )
        with open(final_name, "wb") as stream:
            writer.write(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(final_name, target)
    finally:
        for temp_path in (rendered_name, final_name):
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass


def fill_pdf_form(
    input_path: Path,
    output_path: Path,
    values: dict[str, object],
    flatten: bool,
    force: bool,
) -> dict[str, object]:
    if output_path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing output: {output_path}")
    reader = PdfReader(str(input_path))
    if reader.is_encrypted:
        raise ValueError("Encrypted forms require an explicitly supported password workflow")
    if flatten and pdf_has_signatures(reader):
        raise ValueError("Refusing to flatten a signed PDF without a separate signature decision")

    canonical_fields = reader.get_fields() or {}
    source_widgets = enumerate_widgets(reader)
    for widget in source_widgets:
        name = widget["name"]
        if not name or name not in canonical_fields or widget["has_parent"]:
            continue
        field_identity = indirect_identity(canonical_fields[name])
        if field_identity and widget["identity"] and field_identity != widget["identity"]:
            raise ValueError(
                f"Ambiguous form structure for {name!r}: canonical field and "
                "top-level widget are distinct objects"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    fields = writer.get_fields() or {}
    missing = set(values) - set(fields)
    if missing:
        writer.reattach_fields()
        fields = writer.get_fields() or {}
        missing = set(values) - set(fields)
    if missing:
        raise ValueError(f"Form fields not found after repair: {sorted(missing)}")

    values_to_write = dict(values)
    if flatten:
        values_to_write = {
            name: field.get("/V", "/Off" if field.get("/FT") == "/Btn" else "")
            for name, field in fields.items()
        }
        values_to_write.update(values)
    writer.update_page_form_field_values(
        None,
        values_to_write,
        auto_regenerate=False,
        flatten=flatten,
    )
    if flatten:
        writer.remove_annotations(subtypes="/Widget")
        writer.root_object.pop(NameObject("/AcroForm"), None)
    writer.add_metadata(
        {
            "/Author": "pdf-this",
            "/Keywords": "pdf-this;form-filled" + (";flattened" if flatten else ";interactive"),
        }
    )

    handle, temp_name = tempfile.mkstemp(
        prefix=".pdf-this-form.", suffix=".pdf", dir=output_path.parent
    )
    os.close(handle)
    try:
        with open(temp_name, "wb") as stream:
            writer.write(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, output_path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass

    reopened = PdfReader(str(output_path))
    reopened_fields = reopened.get_fields() or {}
    reopened_widgets = enumerate_widgets(reopened)
    if flatten:
        if reopened_fields or reopened_widgets or reopened.root_object.get("/AcroForm"):
            raise RuntimeError("Flattened form still contains fields or widget annotations")
    else:
        absent = set(values) - set(reopened_fields)
        if absent:
            raise RuntimeError(f"Updated fields missing after reopen: {sorted(absent)}")
        for name, expected in values.items():
            actual = reopened_fields[name].get("/V")
            if str(actual) != str(expected):
                raise RuntimeError(
                    f"Field {name!r} reopened with {actual!r}, expected {expected!r}"
                )
        expected_widgets = [item for item in reopened_widgets if item["name"] in values]
        missing_appearances = [item["name"] for item in expected_widgets if not item["appearance"]]
        if missing_appearances:
            raise RuntimeError(
                "Updated widgets have missing appearance streams: "
                + ", ".join(str(name) for name in missing_appearances)
            )
    return {
        "output": str(output_path),
        "target": "form",
        "flattened": flatten,
        "updated_fields": sorted(values),
        "verification": inspect_pdf(output_path),
    }

def iter_attachments(reader: PdfReader) -> Iterable[tuple[str, bytes]]:
    attachments = getattr(reader, "attachments", None)
    if attachments is None:
        return []
    found: list[tuple[str, bytes]] = []
    for name in attachments:
        payloads = attachments[name]
        if isinstance(payloads, bytes):
            payloads = [payloads]
        for payload in payloads:
            found.append((str(name), bytes(payload)))
    return found


def recover_pdf_source(path: Path) -> tuple[str, str, bool]:
    reader = PdfReader(str(path))
    for name, payload in iter_attachments(reader):
        if name.startswith(SOURCE_PREFIX):
            source_format = name[len(SOURCE_PREFIX) :]
            return payload.decode("utf-8"), source_format, True
    text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return text.strip() + "\n", "pdf", False


def source_to_markdown(source: str, source_format: str) -> str:
    if source_format in {"markdown", "text"}:
        return source
    if source_format in {"csv", "json"}:
        return f"```{source_format}\n{source.rstrip()}\n```\n"
    if source_format == "html":
        packet = extract_html_packet(source)
        if packet:
            nested_source, nested_format = packet
            return source_to_markdown(nested_source, nested_format)
        parser = VisibleHTML()
        parser.feed(source)
        return parser.text()
    return source


def infer_format(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    try:
        return FORMAT_BY_SUFFIX[path.suffix.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported input extension: {path.suffix}") from exc


def atomic_write_text(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing output: {path}")
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
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
    parser.add_argument(
        "--to", choices=("pdf", "markdown", "inspect", "form"), required=True
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--source-format",
        choices=("markdown", "text", "csv", "json", "html"),
    )
    parser.add_argument("--title")
    parser.add_argument("--artifact-kind", default="Durable Artifact")
    parser.add_argument("--status", default="Current")
    parser.add_argument("--provenance-json", type=Path)
    parser.add_argument("--provenance-exempt-reason")
    parser.add_argument("--page-size", choices=("letter", "a4"), default="letter")
    parser.add_argument("--values", type=Path, help="UTF-8 JSON object for --to form")
    parser.add_argument("--flatten", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if args.to == "inspect":
        result = {"target": "inspect", **inspect_pdf(input_path)}
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.to == "form":
        if not args.values:
            raise ValueError("--to form requires --values with a UTF-8 JSON object")
        values_path = args.values.resolve()
        values = json.loads(values_path.read_text(encoding="utf-8"))
        if not isinstance(values, dict):
            raise ValueError("Form values JSON must contain one object keyed by field name")
        output = (
            args.output
            or input_path.with_name(input_path.stem + "-filled.pdf")
        ).resolve()
        if output == input_path:
            raise ValueError("Input and output paths must differ")
        result = fill_pdf_form(
            input_path,
            output,
            values,
            args.flatten,
            args.force,
        )
        print(json.dumps(result, ensure_ascii=False))
        return 0

    output = (
        args.output
        or input_path.with_suffix(".pdf" if args.to == "pdf" else ".md")
    ).resolve()
    if output == input_path:
        raise ValueError("Input and output paths must differ")

    if args.to == "pdf":
        source = input_path.read_text(encoding="utf-8")
        source_format = infer_format(input_path, args.source_format)
        title = args.title or input_path.stem
        structured_rows = load_structured_provenance(
            args.provenance_json.resolve() if args.provenance_json else None
        )
        injected_rows = require_creation_provenance(
            source,
            source_format,
            structured_rows,
            args.provenance_exempt_reason,
        )
        if source_format == "html":
            create_pdf_from_html(
                output,
                input_path,
                source,
                title,
                args.artifact_kind,
                args.status,
                args.force,
            )
            normalized_source, normalized_format = source, "html"
            renderer = "browser"
        else:
            create_pdf(
                output,
                source,
                source_format,
                title,
                args.artifact_kind,
                args.status,
                args.page_size,
                args.force,
                injected_rows,
            )
            normalized_source, normalized_format = normalize_source(source, source_format)
            renderer = "reportlab"
        recovered, recovered_format, exact = recover_pdf_source(output)
        if not exact or recovered != normalized_source or recovered_format != normalized_format:
            raise RuntimeError("Embedded source attachment failed round-trip verification")
        verification = inspect_pdf(output)
        if not verification["pages"]:
            raise RuntimeError("Generated PDF has no pages")
        result = {
            "output": str(output),
            "target": "pdf",
            "pages": verification["pages"],
            "source_format": normalized_format,
            "renderer": renderer,
            "embedded_source": True,
            "exact_recovery_verified": True,
            "searchable_pages": verification["searchable_pages"],
        }
    else:
        source, source_format, exact = recover_pdf_source(input_path)
        markdown = source_to_markdown(source, source_format)
        atomic_write_text(output, markdown, args.force)
        result = {
            "output": str(output),
            "target": "markdown",
            "source_format": source_format,
            "exact_recovery": exact,
        }
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"pdf-this: {error}", file=sys.stderr)
        raise SystemExit(1)
