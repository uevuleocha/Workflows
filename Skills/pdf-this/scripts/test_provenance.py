#!/usr/bin/env python3
"""Regression checks for pdf-this Agent Provenance presentation."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("pdf_this.py")
SPEC = importlib.util.spec_from_file_location("pdf_this", MODULE_PATH)
assert SPEC and SPEC.loader
pdf_this = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pdf_this)

SOURCE = """# Provenance Fixture

## Agent Provenance

| Field | Value |
|---|---|
| Content owner | Uzo |
| Original writing agent | Codex Agent |
| Original writing LLM | GPT-5.1-Codex |
| Created | 2026-08-03 |
| Artifact role | A deliberately long role value that verifies professional wrapping and stable provenance-table column widths. |
| PDF rendition agent | Conversion Agent |

## Agent Change Log

| Date and Time | Agent | Model | Action | Scope |
|---|---|---|---|---|
| 2026-08-03 | Codex Agent | Not recorded | Created | Created fixture. |
"""

STRUCTURED = [
    ["Content owner", "Uzo"],
    ["Original writing agent", "Codex Agent"],
    ["Original writing LLM", "GPT-5.1-Codex"],
    ["Created", "2026-08-03"],
    ["Artifact role", "Structured provenance fixture"],
]

HTML_SOURCE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Browser Fixture</title></head><body><h1>Browser Fixture</h1><section><h2>Agent Provenance</h2><div class="provenance-table-wrap" role="region" aria-label="Agent provenance"><table class="provenance-table"><caption>Durable artifact ownership and role</caption><thead><tr><th scope="col">Field</th><th scope="col">Value</th></tr></thead><tbody><tr><th scope="row">Content owner</th><td>Uzo</td></tr><tr><th scope="row">Original writing agent</th><td>Codex Agent</td></tr><tr><th scope="row">Original writing LLM</th><td>GPT-5.1-Codex</td></tr><tr><th scope="row">Created</th><td>2026-08-03</td></tr><tr><th scope="row">Artifact role</th><td>Faithful browser conversion fixture</td></tr><tr><th scope="row">PDF rendition agent</th><td>Conversion Agent</td></tr></tbody></table></div></section></body></html>"""


def assert_rejected(action, expected: str) -> None:
    try:
        action()
    except ValueError as error:
        assert expected in str(error), str(error)
    else:
        raise AssertionError(f"Expected rejection containing: {expected}")


def main() -> int:
    styles = pdf_this.build_styles()
    story = pdf_this.markdown_story(SOURCE, styles, 500, "Provenance Fixture")
    tables = [item for item in story if item.__class__.__name__ == "Table"]
    # A schema-v2 artifact carries two tables: the two-column provenance table
    # and the five-column Agent Change Log. Only the first gets provenance widths.
    assert len(tables) == 2
    table = tables[0]
    assert table.repeatRows == 1
    assert [round(width, 2) for width in table._colWidths] == [170.0, 330.0]
    change_log = tables[1]
    assert len(change_log._colWidths) == 5

    assert pdf_this.markdown_provenance_rows(SOURCE)
    duplicate_native = SOURCE + "\n" + SOURCE.split("## Agent Provenance", 1)[1].split("## Agent Change Log", 1)[0].join(("## Agent Provenance", ""))
    assert_rejected(
        lambda: pdf_this.require_creation_provenance(duplicate_native, "markdown", None, None),
        "exactly one Agent Provenance section",
    )
    assert_rejected(
        lambda: pdf_this.require_creation_provenance(SOURCE, "markdown", STRUCTURED, None),
        "cannot be combined",
    )
    assert_rejected(
        lambda: pdf_this.require_creation_provenance("# Missing", "markdown", None, None),
        "require canonical Agent Provenance",
    )
    for source_format, payload in (
        ("text", "plain text"),
        ("csv", "name,value\na,b\n"),
        ("json", "{}"),
    ):
        assert_rejected(
            lambda source_format=source_format, payload=payload: pdf_this.require_creation_provenance(
                payload, source_format, None, None
            ),
            "require canonical Agent Provenance",
        )
        assert pdf_this.require_creation_provenance(
            payload, source_format, STRUCTURED, None
        ) == STRUCTURED

    # A four-row table in the pre-2026-08-11 canonical order must now be rejected:
    # it omits "Original writing LLM" and slides "Created" into its position.
    legacy_four_row = [
        STRUCTURED[0],
        STRUCTURED[1],
        STRUCTURED[3],
        STRUCTURED[4],
    ]

    for bad_rows in (
        STRUCTURED[:4],
        legacy_four_row,
        [*STRUCTURED[:2], STRUCTURED[3], STRUCTURED[2], STRUCTURED[4]],
        [STRUCTURED[0], STRUCTURED[0], *STRUCTURED[2:]],
        [STRUCTURED[1], STRUCTURED[0], *STRUCTURED[2:]],
        [STRUCTURED[0], ["Original writer", "Codex Agent"], *STRUCTURED[2:]],
        [*STRUCTURED[:2], ["Original writing model", "GPT-5.1-Codex"], *STRUCTURED[3:]],
        [*STRUCTURED[:4], ["Artifact role", ""]],
        [*STRUCTURED[:2], ["Original writing LLM", ""], *STRUCTURED[3:]],
    ):
        assert_rejected(
            lambda bad_rows=bad_rows: pdf_this.validate_provenance_rows(
                ["Field", "Value"], bad_rows
            ),
            "Agent Provenance",
        )

    for exact_model in ("GPT-5.6 Sol", "gpt-5.6-sol", "Claude Opus 5", "Not recorded"):
        rows = [*STRUCTURED[:2], ["Original writing LLM", exact_model], *STRUCTURED[3:]]
        pdf_this.validate_provenance_rows(
            ["Field", "Value"], rows, enforce_exact_model=True
        )
    for ambiguous_model in ("GPT-5", "GPT-5.6", "Claude", "Codex Agent"):
        rows = [*STRUCTURED[:2], ["Original writing LLM", ambiguous_model], *STRUCTURED[3:]]
        assert_rejected(
            lambda rows=rows: pdf_this.validate_provenance_rows(
                ["Field", "Value"], rows, enforce_exact_model=True
            ),
            "full exact model name",
        )
    assert pdf_this.html_provenance_rows(HTML_SOURCE)
    duplicate_html = HTML_SOURCE.replace("</body>", HTML_SOURCE.split("<section>", 1)[1].split("</section>", 1)[0].join(("<section>", "</section></body>")))
    assert_rejected(
        lambda: pdf_this.require_creation_provenance(duplicate_html, "html", None, None),
        "exactly one canonical provenance table",
    )
    assert_rejected(
        lambda: pdf_this.require_creation_provenance(HTML_SOURCE, "html", STRUCTURED, None),
        "cannot be combined",
    )
    assert pdf_this.require_creation_provenance(
        "excluded", "text", None, "Schema-sensitive export"
    ) is None

    loose = "## Agent Provenance\n\nContent owner: Uzo\n"
    assert_rejected(
        lambda: pdf_this.markdown_story(loose, styles, 500),
        "Field | Value table",
    )

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "fixture.pdf"
        pdf_this.create_pdf(
            output,
            SOURCE,
            "markdown",
            "Provenance Fixture",
            "Test Artifact",
            "Current",
            "letter",
            False,
        )
        recovered, source_format, exact = pdf_this.recover_pdf_source(output)
        assert exact and source_format == "markdown" and recovered == SOURCE
        inspection = pdf_this.inspect_pdf(output)
        assert inspection["pages"] >= 1
        reader = pdf_this.PdfReader(str(output))
        visible = "\n".join(page.extract_text() or "" for page in reader.pages)
        for fact in (
            "Content owner",
            "Original writing agent",
            "Original writing LLM",
            "Created",
            "Artifact role",
            "PDF rendition agent",
            "Conversion Agent",
        ):
            assert fact in visible

        for source_format, payload in (
            ("text", "plain text"),
            ("csv", "name,value\na,b\n"),
            ("json", "{}"),
        ):
            structured_output = Path(directory) / f"structured-{source_format}.pdf"
            pdf_this.create_pdf(
                structured_output,
                payload,
                source_format,
                f"Structured {source_format}",
                "Test Artifact",
                "Current",
                "letter",
                False,
                STRUCTURED,
            )
            structured_recovered, structured_format, structured_exact = (
                pdf_this.recover_pdf_source(structured_output)
            )
            assert structured_exact
            assert structured_format == source_format
            assert structured_recovered == payload
            structured_text = "\n".join(
                page.extract_text() or ""
                for page in pdf_this.PdfReader(str(structured_output)).pages
            )
            for fact in pdf_this.CANONICAL_PROVENANCE_FIELDS:
                assert fact in structured_text

        html_input = Path(directory) / "browser-fixture.html"
        browser_output = Path(directory) / "browser-fixture.pdf"
        html_input.write_text(HTML_SOURCE, encoding="utf-8")
        assert pdf_this.find_browser(), "Faithful HTML-to-PDF regression requires a browser"
        pdf_this.create_pdf_from_html(
            browser_output,
            html_input,
            HTML_SOURCE,
            "Browser Fixture",
            "Test Artifact",
            "Current",
            False,
        )
        recovered_html, recovered_format, exact_html = pdf_this.recover_pdf_source(
            browser_output
        )
        assert exact_html and recovered_format == "html" and recovered_html == HTML_SOURCE
        browser_text = "\n".join(
            page.extract_text() or ""
            for page in pdf_this.PdfReader(str(browser_output)).pages
        )
        for fact in pdf_this.CANONICAL_PROVENANCE_FIELDS:
            assert fact in browser_text
    print("pdf provenance regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
