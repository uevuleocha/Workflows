#!/usr/bin/env python3
"""Check and safely align Markdown pipe tables by Unicode display width."""

from __future__ import annotations

import argparse
import codecs
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

UNICODE_VERSION = "17.0.0"
DEFAULT_CELL_CAP = 80
DEFAULT_TABLE_CAP = 120


class OperationalError(RuntimeError):
    """An environment or I/O error that prevents a trustworthy result."""


@dataclass(frozen=True)
class Finding:
    code: str
    line: int
    message: str

    def as_dict(self) -> dict[str, object]:
        return {"code": self.code, "line": self.line, "message": self.message}


@dataclass
class Row:
    line_index: int
    prefix: str
    cells: list[str]
    outer_left: bool
    outer_right: bool
    suffix: str
    newline: str


@dataclass
class Table:
    rows: list[Row]
    delimiter_index: int


def _width_function():
    try:
        import wcwidth
    except ImportError as exc:
        raise OperationalError(
            "wcwidth is required; raw character count is unsafe; "
            "install with: python -m pip install wcwidth"
        ) from exc
    versions = set(wcwidth.list_versions())
    if UNICODE_VERSION not in versions:
        raise OperationalError(
            f"wcwidth lacks required Unicode data {UNICODE_VERSION} "
            f"(upgrade with: python -m pip install --upgrade wcwidth); "
            f"available={sorted(versions)}"
        )

    def width(text: str) -> int:
        value = wcwidth.wcswidth(text, unicode_version=UNICODE_VERSION)
        if value < 0:
            raise OperationalError("unsupported control character in table cell")
        return value

    return width


def _newline_of(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n") or line.endswith("\r"):
        return line[:-1], line[-1]
    return line, ""


def _pipe_positions(text: str) -> tuple[list[int], bool]:
    positions: list[int] = []
    code_run = 0
    i = 0
    while i < len(text):
        char = text[i]
        if char == "`":
            j = i
            while j < len(text) and text[j] == "`":
                j += 1
            run = j - i
            if code_run == 0:
                code_run = run
            elif run == code_run:
                code_run = 0
            i = j
            continue
        if char == "|" and code_run == 0:
            backslashes = 0
            j = i - 1
            while j >= 0 and text[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                positions.append(i)
        i += 1
    return positions, code_run != 0


def _parse_row(line: str, line_index: int) -> Row | None:
    body, newline = _newline_of(line)
    if "\t" in body:
        return None
    prefix_match = re.match(r"^[ ]{0,3}", body)
    prefix = prefix_match.group(0) if prefix_match else ""
    core = body[len(prefix) :]
    stripped = core.rstrip(" ")
    candidate_positions, unclosed_code = _pipe_positions(stripped)
    if unclosed_code:
        return None
    right = bool(candidate_positions) and candidate_positions[-1] == len(stripped) - 1
    suffix = core[len(stripped) :] if right else ""
    if right:
        core = stripped
    positions, _ = _pipe_positions(core)
    if not positions:
        return None
    left = positions[0] == 0
    start = 1 if left else 0
    end = len(core) - 1 if right else len(core)
    interior = [p for p in positions if start <= p < end]
    cells: list[str] = []
    cursor = start
    for position in interior:
        cells.append(core[cursor:position].strip(" "))
        cursor = position + 1
    cells.append(core[cursor:end].strip(" "))
    if len(cells) < 2:
        return None
    return Row(line_index, prefix, cells, left, right, suffix, newline)


def _has_unclosed_code_span(line: str) -> bool:
    body, _ = _newline_of(line)
    _, unclosed = _pipe_positions(body)
    return unclosed


def _delimiter_styles(row: Row) -> list[tuple[bool, bool]] | None:
    styles: list[tuple[bool, bool]] = []
    for cell in row.cells:
        value = cell.strip()
        if not re.fullmatch(r":?-{3,}:?", value):
            return None
        styles.append((value.startswith(":"), value.endswith(":")))
    return styles


def _looks_delimiterish(row: Row | None) -> bool:
    if row is None:
        return False
    return all(bool(c) and set(c.strip()) <= {"-", ":"} and "-" in c for c in row.cells)


def _fence_transition(line: str, active: tuple[str, int] | None) -> tuple[str, int] | None:
    body, _ = _newline_of(line)
    if active is None:
        match = re.match(r"^[ ]{0,3}(`{3,}|~{3,})", body)
        if match:
            marker = match.group(1)
            return marker[0], len(marker)
        return None
    char, length = active
    if re.fullmatch(rf"[ ]{{0,3}}{re.escape(char)}{{{length},}}[ ]*", body):
        return None
    return active


def find_tables(lines: list[str]) -> tuple[list[Table], list[Finding]]:
    tables: list[Table] = []
    findings: list[Finding] = []
    fenced = [False] * len(lines)
    active: tuple[str, int] | None = None
    for i, line in enumerate(lines):
        was_active = active is not None
        next_active = _fence_transition(line, active)
        is_transition = next_active != active
        fenced[i] = was_active or is_transition
        active = next_active

    i = 0
    while i + 1 < len(lines):
        if fenced[i] or fenced[i + 1]:
            i += 1
            continue
        header = _parse_row(lines[i], i)
        delimiter = _parse_row(lines[i + 1], i + 1)
        if header is None and "|" in lines[i] and _has_unclosed_code_span(lines[i]) and _looks_delimiterish(delimiter):
            findings.append(Finding("malformed_table", i + 1, "unclosed inline-code span in candidate header"))
            i += 2
            continue
        styles = _delimiter_styles(delimiter) if delimiter else None
        if header and _looks_delimiterish(delimiter) and (
            styles is None or len(header.cells) != len(delimiter.cells)
        ):
            findings.append(Finding("malformed_table", i + 1, "ambiguous or inconsistent delimiter row"))
            i += 2
            continue
        if not header or not delimiter or styles is None or len(header.cells) != len(delimiter.cells):
            i += 1
            continue
        if (header.outer_left, header.outer_right) != (delimiter.outer_left, delimiter.outer_right):
            findings.append(Finding("malformed_table", i + 1, "outer-pipe style differs across header and delimiter"))
            i += 2
            continue
        rows = [header, delimiter]
        j = i + 2
        while j < len(lines) and not fenced[j]:
            row = _parse_row(lines[j], j)
            if row is None:
                break
            if len(row.cells) != len(header.cells) or (row.outer_left, row.outer_right) != (
                header.outer_left,
                header.outer_right,
            ):
                findings.append(Finding("malformed_table", j + 1, "inconsistent table row"))
                break
            rows.append(row)
            j += 1
        tables.append(Table(rows, 1))
        i = max(j, i + 2)
    return tables, findings


def _render_table(table: Table, width) -> tuple[list[str], list[Finding]]:
    findings: list[Finding] = []
    delimiter = table.rows[table.delimiter_index]
    styles = _delimiter_styles(delimiter)
    assert styles is not None
    column_widths: list[int] = []
    for column, style in enumerate(styles):
        left, right = style
        minimum = 3 + int(left) + int(right)
        values = [width(row.cells[column]) for idx, row in enumerate(table.rows) if idx != table.delimiter_index]
        for idx, value in enumerate(values):
            if value > DEFAULT_CELL_CAP:
                source_row = table.rows[idx if idx < table.delimiter_index else idx + 1]
                findings.append(
                    Finding("cell_over_cap", source_row.line_index + 1, f"column {column + 1} is {value} display columns")
                )
        column_widths.append(max([minimum, *values]))

    rendered_width = sum(column_widths) + 3 * (len(column_widths) - 1)
    if table.rows[0].outer_left:
        rendered_width += 2
    if table.rows[0].outer_right:
        rendered_width += 2
    if rendered_width > DEFAULT_TABLE_CAP:
        findings.append(
            Finding("table_over_cap", table.rows[0].line_index + 1, f"table is {rendered_width} display columns")
        )
    if findings:
        return [], findings

    output: list[str] = []
    for row_index, row in enumerate(table.rows):
        cells: list[str] = []
        for column, target in enumerate(column_widths):
            if row_index == table.delimiter_index:
                left, right = styles[column]
                hyphens = target - int(left) - int(right)
                value = (":" if left else "") + ("-" * hyphens) + (":" if right else "")
            else:
                value = row.cells[column]
                value += " " * (target - width(value))
            cells.append(value)
        inner = " | ".join(cells)
        rendered = row.prefix
        if row.outer_left:
            rendered += "| "
        rendered += inner
        if row.outer_right:
            rendered += " |"
        output.append(rendered + row.suffix + row.newline)
    return output, findings


def transform(text: str) -> tuple[str, list[Finding]]:
    width = _width_function()
    lines = text.splitlines(keepends=True)
    tables, findings = find_tables(lines)
    replacements: dict[int, str] = {}
    for table in tables:
        rendered, table_findings = _render_table(table, width)
        findings.extend(table_findings)
        if table_findings:
            continue
        for row, replacement in zip(table.rows, rendered):
            replacements[row.line_index] = replacement
            if lines[row.line_index] != replacement:
                findings.append(Finding("needs_alignment", row.line_index + 1, "safe padding differs"))
    output = "".join(replacements.get(i, line) for i, line in enumerate(lines))
    return output, findings


def _read_utf8(path: Path) -> tuple[str, bool]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise OperationalError(str(exc)) from exc
    bom = data.startswith(codecs.BOM_UTF8)
    payload = data[len(codecs.BOM_UTF8) :] if bom else data
    try:
        return payload.decode("utf-8"), bom
    except UnicodeDecodeError as exc:
        raise OperationalError(f"input is not valid UTF-8: {exc}") from exc


def _emit(findings: Iterable[Finding], as_json: bool) -> None:
    payload = [finding.as_dict() for finding in findings]
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for finding in payload:
            print(f"{finding['code']} line {finding['line']}: {finding['message']}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "format"):
        sub = subparsers.add_parser(name)
        sub.add_argument("source", type=Path)
        sub.add_argument("--json", action="store_true")
        if name == "format":
            sub.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        source = args.source.resolve()
        text, bom = _read_utf8(source)
        formatted, findings = transform(text)
        blockers = [f for f in findings if f.code != "needs_alignment"]
        if args.command == "check":
            _emit(findings, args.json)
            return 1 if findings else 0
        output = args.output.resolve()
        if output == source:
            raise OperationalError("output must differ from source")
        if output.exists():
            raise OperationalError("output already exists; refusing overwrite")
        if blockers:
            _emit(findings, args.json)
            return 1
        data = formatted.encode("utf-8")
        if bom:
            data = codecs.BOM_UTF8 + data
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        _emit([], args.json)
        return 0
    except OperationalError as exc:
        print(f"operational_error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"operational_error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
