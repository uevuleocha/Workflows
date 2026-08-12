---
name: markdown-table-aligner
description: Deterministically check or align Markdown pipe tables using Unicode display width while preserving cell content and bytes outside proven tables. Use when a skill or user asks to align, normalize, validate, or repair Markdown tables, especially before a Markdown durable artifact is saved or serialized to HTML/PDF.
---

# Markdown Table Aligner

Apply a safe mechanical formatting pass to Markdown pipe tables. This skill owns padding and diagnostics only; the calling authoring skill owns table meaning, wording, row identifiers, truncation choices, overflow notes, and artifact lifecycle.

## Invocation

Use this skill when:

- a user asks to align, normalize, check, or repair Markdown tables;
- an artifact-authoring skill has staged Markdown containing tables; or
- Markdown source is about to be serialized to HTML or PDF.

Do not invoke it on pure HTML/PDF with no Markdown source or redundantly above and below another helper that already owns the same serialization boundary.

## Required Input

Resolve an existing UTF-8 Markdown source path. For formatting, also resolve a new explicit staged-output path. Never overwrite the source by default.

The script requires Python and `wcwidth` data for Unicode `17.0.0`. If that exact width dataset is unavailable, stop: raw character count is not an acceptable fallback.

## Commands

From this skill folder:

```text
python -X utf8 scripts/align_markdown_tables.py check <source.md> --json
python -X utf8 scripts/align_markdown_tables.py format <source.md> --output <staged.md> --json
python -X utf8 scripts/test_align_markdown_tables.py
```

Exit meanings:

- `0`: check is clean, or formatting produced a verified staged output.
- `1`: alignment, overflow, malformed-table, or other content findings exist.
- `2`: operational failure, such as invalid UTF-8, missing Unicode-width data, unsafe output collision, or I/O failure.

Keep stdout and stderr separate when the distinction matters. JSON findings go to stdout; operational errors go to stderr.

## Safe Workflow

1. Run `check` against the staged Markdown source.
2. If the only findings are safe padding differences, run `format` to a new output path.
3. Review the source-to-output diff. Only table-padding spaces and safe delimiter-row padding may differ.
4. Run `check` on the staged output; it must exit `0`.
5. Run `format` once more to another new path and prove byte identity with the first output.
6. Only then let the owning skill replace, save, or serialize its artifact.

An exit `0` is authoritative for deterministic monospaced Unicode alignment. Do not reject or repeatedly rewrite a clean table solely because one editor, emoji fallback font, proportional renderer, or screenshot shows a residual pixel-level offset. Pixel-perfect alignment across unlike fonts is not achievable through Markdown spaces; the helper guarantees Unicode display-column alignment under its pinned width contract.

If any table has an over-cap cell, malformed structure, unsupported control width, or ambiguous syntax, leave it unchanged and return a finding. The agent decides the editorial repair.

## Parser And Preservation Contract

The script:

- recognizes a table only from an adjacent header and valid delimiter row with consistent columns;
- supports and preserves tables with or without outer pipes;
- respects escaped pipes and pipes inside inline-code spans;
- preserves left, center, and right delimiter colons;
- skips length-aware backtick and tilde fenced code blocks;
- measures rendered width for wide glyphs, combining marks, emoji, variation selectors, and zero-width joiners;
- changes only safe cell-edge padding and delimiter-row hyphen padding;
- preserves UTF-8 BOM state, LF/CRLF endings, final-newline state, and bytes outside proven tables;
- reports cells above 80 display columns and tables above 120 display columns without rewriting them; and
- is idempotent: formatting normalized input produces byte-identical output.

## Content Ownership Boundary

This helper does not create semantic tables. It never rewrites words, truncates cells, chooses overflow pointers, creates notes, reorders rows or columns, changes headings, or finalizes artifacts. “Use the aligner to make the table” means use it for the final deterministic padding pass after the owning skill has authored the content.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the portable workspace rule:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` using that row's identifier, and place the full original text as a note below the table. Pad columns for monospaced rendered alignment. Rendered Unicode display width is authoritative; raw `|` indices are diagnostic only. Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells. Keep tables near 120 display columns by moving editorial detail to notes.

The script itself never performs the editorial truncation or note creation described above; it reports those cases for the owning agent.

## Validation

- Run `python -X utf8 scripts/test_align_markdown_tables.py` and require exit `0`.
- Run the official folder-skill `quick_validate.py` with UTF-8 mode and require exit `0`.
- Confirm the portable `## Markdown Table Alignment` section remains present.
- Confirm formatting never overwrites its input or an existing output path.
- Confirm fenced examples, prose pipes, cell text, encoding, line endings, and bytes outside proven tables remain unchanged.
- Confirm ASCII, emoji, CJK, combining-character, variation-selector, and joined-emoji fixtures align by Unicode display width.
- Confirm over-cap and malformed inputs return findings without an output file.
- Confirm a second formatting pass is byte-identical.
