#!/usr/bin/env python3
"""Regression checks for html-this Agent Provenance presentation."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("html_this.py")
SPEC = importlib.util.spec_from_file_location("html_this", MODULE_PATH)
assert SPEC and SPEC.loader
html_this = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(html_this)

SOURCE = """# Provenance Fixture

## Agent Provenance

| Field | Value |
|---|---|
| Content owner | Uzo |
| Original writing agent | Codex Agent |
| Created | 2026-08-03 |
| Artifact role | A deliberately long role value that verifies wrapping without changing the exact embedded native source packet. |
| HTML rendition agent | Conversion Agent |

## Agent Change Log

- 2026-08-03 — Codex Agent — Created fixture.
"""

STRUCTURED = [
    ["Content owner", "Uzo"],
    ["Original writing agent", "Codex Agent"],
    ["Created", "2026-08-03"],
    ["Artifact role", "Structured provenance fixture"],
]


def assert_rejected(action, expected: str) -> None:
    try:
        action()
    except ValueError as error:
        assert expected in str(error), str(error)
    else:
        raise AssertionError(f"Expected rejection containing: {expected}")


def main() -> int:
    body = html_this.render_markdown(SOURCE, "Provenance Fixture")
    document = html_this.build_document(
        body, SOURCE, "markdown", "Provenance Fixture", "Test Artifact", "Current"
    )
    assert '<table class="provenance-table">' in document
    assert '<th scope="col">Field</th>' in document
    assert '<th scope="row">Content owner</th>' in document
    assert '<th scope="row">HTML rendition agent</th>' in document
    assert "<td>Conversion Agent</td>" in document
    assert 'aria-label="Agent provenance"' in document
    assert "provenance-table-wrap" in document
    assert "@media (max-width:680px)" in document
    assert "@media print" in document
    assert "<dl>" not in body
    packet = html_this.extract_source_packet_bytes(document)
    assert packet == (SOURCE.encode("utf-8"), "markdown", "utf-8")
    inspection = html_this.inspect_html(document)
    assert inspection["structure_valid"]
    assert inspection["provenance_table"]
    assert inspection["provenance_canonical_rows"]
    assert not inspection["provenance_definition_list"]

    assert html_this.markdown_provenance_rows(SOURCE)
    duplicate_native = SOURCE + "\n" + SOURCE.split("## Agent Provenance", 1)[1].split("## Agent Change Log", 1)[0].join(("## Agent Provenance", ""))
    assert_rejected(
        lambda: html_this.require_creation_provenance(duplicate_native, "markdown", None, None),
        "exactly one Agent Provenance section",
    )
    assert_rejected(
        lambda: html_this.require_creation_provenance(SOURCE, "markdown", STRUCTURED, None),
        "cannot be combined",
    )
    assert_rejected(
        lambda: html_this.require_creation_provenance("# Missing", "markdown", None, None),
        "require canonical Agent Provenance",
    )
    for source_format, payload in (
        ("text", "plain text"),
        ("csv", "name,value\na,b\n"),
        ("json", "{}"),
    ):
        assert_rejected(
            lambda source_format=source_format, payload=payload: html_this.require_creation_provenance(
                payload, source_format, None, None
            ),
            "require canonical Agent Provenance",
        )
        assert html_this.require_creation_provenance(
            payload, source_format, STRUCTURED, None
        ) == STRUCTURED

    for bad_rows in (
        STRUCTURED[:3],
        [STRUCTURED[0], STRUCTURED[0], *STRUCTURED[2:]],
        [STRUCTURED[1], STRUCTURED[0], *STRUCTURED[2:]],
        [STRUCTURED[0], ["Original writer", "Codex Agent"], *STRUCTURED[2:]],
        [*STRUCTURED[:3], ["Artifact role", ""]],
    ):
        assert_rejected(
            lambda bad_rows=bad_rows: html_this.validate_provenance_rows(
                ["Field", "Value"], bad_rows
            ),
            "Agent Provenance",
        )

    injected = html_this.provenance_table_html(STRUCTURED)
    assert '<th scope="row">Original writing agent</th>' in injected
    assert_rejected(
        lambda: html_this.require_creation_provenance(injected + injected, "html", None, None),
        "exactly one canonical provenance table",
    )
    assert_rejected(
        lambda: html_this.require_creation_provenance(injected, "html", STRUCTURED, None),
        "cannot be combined",
    )
    assert html_this.require_creation_provenance(
        "excluded", "text", None, "Schema-sensitive export"
    ) is None

    loose = "## Agent Provenance\n\nContent owner: Uzo\n"
    assert_rejected(
        lambda: html_this.render_markdown(loose),
        "Field | Value table",
    )

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "fixture.html"
        html_this.atomic_write(output, document.encode("utf-8"), False)
        assert output.read_text(encoding="utf-8") == document
        for source_format, payload in (
            ("text", "plain text"),
            ("csv", "name,value\na,b\n"),
            ("json", "{}"),
        ):
            structured_document = html_this.build_document(
                html_this.provenance_table_html(STRUCTURED)
                + "\n"
                + html_this.render_source(payload, source_format),
                payload,
                source_format,
                f"Structured {source_format}",
                "Test Artifact",
                "Current",
            )
            structured_inspection = html_this.inspect_html(structured_document)
            assert structured_inspection["provenance_canonical_rows"]
            assert html_this.extract_source_packet_bytes(structured_document) == (
                payload.encode("utf-8"),
                source_format,
                "utf-8",
            )
    print("html provenance regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
