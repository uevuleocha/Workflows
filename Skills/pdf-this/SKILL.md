---
name: pdf-this
description: Create, convert, read, inspect, render, verify, fill, flatten, or recover professional PDF artifacts while preserving durable-artifact ownership and lifecycle. Supports Markdown/plain text/CSV/JSON, faithful browser-rendered HTML and report exports, PDF-to-Markdown recovery, layout review, and validated AcroForms. Use when the user invokes /pdf-this, $pdf-this, use pdf-this, asks for a PDF version/copy, asks to inspect or verify a PDF, asks to fill or flatten a PDF form, asks to convert HTML or a report to PDF, or asks to recover Markdown from a pdf-this file.
---

# PDF This

Operate as the personal general-purpose PDF surface while preserving the durable
artifact features shared with `html-this`. This skill owns PDF serialization,
renderer selection, page design, exact-source attachment and recovery, PDF
inspection, form handling, and PDF-specific verification. A co-invoked artifact
producer still owns content, placement, numbering, lifecycle, and evidence.

Read `references/durable-format-protocol.md` before writing, updating,
converting, reopening, or finalizing a format-managed artifact.

## Project Contract

Obey the active workspace contract, permissions, UTF-8 requirements, numbering
rules, Archive layout, and lifecycle gates. Never substitute PDF for an
operationally required source, database, configuration, backup, or
machine-consumed file.

## Invocation

Treat these as direct invocation:

- `/pdf-this`, `$pdf-this`, or `use pdf-this`
- `make a PDF version/copy of this`
- `save this durable artifact as PDF`
- `convert this HTML/report/dashboard export to PDF`
- `read`, `inspect`, `render`, or `verify this PDF`
- `fill this PDF form` or `flatten this completed form`
- `turn this pdf-this artifact back into Markdown`

## Modes

Select the mode from clear intent without asking.

### Mode A - Existing artifact to PDF sibling

Convert Markdown, plain text, CSV, JSON, or HTML beside its source. Preserve the
source and the identical directory, permanent number, topic, and lifecycle stem:

```text
1.) Topic_pending.md
1.) Topic_pending.pdf
```

The siblings are one logical artifact and consume one numbering entry. Route
HTML through Mode G rather than rebuilding it as plain text.

### Mode B - Co-invoked PDF-only creation

The producer runs its complete content, path, numbering, lifecycle, and evidence
workflow. `pdf-this` alone owns serialization. Save exactly one durable `.pdf`
unless several formats were requested, leave native intermediates only in an
approved temporary area, and attach the exact native source for recovery.

### Mode C - PDF to Markdown

Preserve the PDF and create the same-stem `.md` sibling. Prefer the embedded
source attachment. When the attachment is HTML containing an `html-this` source
packet, recover that nested source first. For unrelated PDFs, extract text
best-effort and disclose that layout, diagrams, columns, and styling may not
round-trip exactly.

### Mode D - Standalone explanatory PDF

For a presentation-first PDF outside another durable workflow, default to:

```text
<workspace>/Archive/Historical/PDFs/<Subject>/N.) <Topic>.pdf
```

The Subject is unnumbered. Compute `N` across existing numbered files in that
Subject. Use another in-workspace path only when specified by the user or
contract.

### Mode E - Update or lifecycle participation

Treat same-stem `.md`, `.html`, and `.pdf` files as one artifact set. Preflight
all sources and destinations, stage regenerations, apply lifecycle/content
changes to every member, and stop rather than knowingly split their state. The
owning skill controls completion evidence and lifecycle language.

### Mode F - Read, inspect, render, or verify an existing PDF

Use `pypdf` or `pdfplumber` for semantic extraction and inventory, and Poppler
for visual review. Inspect page count and sizes, metadata, searchability,
attachments, fields, widgets, signatures, and appearance streams as relevant.
Do not mistake successful text extraction for proof of layout fidelity. This
mode is read-only unless the user separately requests a change.

### Mode G - Faithful HTML, report, or dashboard export to PDF

Use a static HTML file/export as the source of truth. Reject a live MCP app
shell, blob stub, sign-in page, redirect page, incomplete viewer, or boot shell
that does not contain the report. Obtain the matching static export first.

Print the static source with Chrome, Edge, Chromium, or an equivalent browser
renderer so CSS, selectable text, charts, tables, images, and print styles are
preserved. Do not redraw a report from memory or silently replace browser
rendering with the semantic ReportLab layout. After printing, attach the exact
HTML source with `pypdf` so recovery and durable ownership remain intact.

If no faithful renderer exists, stop with the missing capability and source
path. Do not hand off a degraded reconstruction as an exact conversion.

### Mode H - Fill and validate AcroForms

Preserve the source form. Keep the result interactive by default; flatten only
when explicitly requested. Before filling, inspect both canonical AcroForm
fields and page `/Widget` annotations, follow `/Parent` and `/Kids`, and reject
ambiguous distinct objects sharing a field name. Reattach only genuinely
orphaned widgets.

After writing, reopen the PDF. Interactive output must retain expected fields,
values, effective widget values, and non-empty normal appearance streams.
Flattened output must contain no widget annotations and no AcroForm field tree.
Never flatten a signed PDF without a separate explicit signature decision.

## Renderer Selection

Use the source-appropriate lane:

- Markdown, text, CSV, JSON, or fresh semantic content -> ReportLab.
- Static HTML, reports, dashboards, and chart exports -> browser print engine.
- Existing PDF inspection -> `pypdf`/`pdfplumber` plus Poppler rendering.
- Interactive forms -> `pypdf` AcroForm workflow.
- Scanned/image-only PDFs -> visual review and best-effort semantic extraction,
  with OCR or searchability limitations disclosed.

## Deterministic Helper

Use `scripts/pdf_this.py`:

```text
python -X utf8 "<skill-dir>/scripts/pdf_this.py" INPUT --to pdf
python -X utf8 "<skill-dir>/scripts/pdf_this.py" INPUT.pdf --to markdown
python -X utf8 "<skill-dir>/scripts/pdf_this.py" INPUT.pdf --to inspect
python -X utf8 "<skill-dir>/scripts/pdf_this.py" FORM.pdf --to form --values values.json
python -X utf8 "<skill-dir>/scripts/pdf_this.py" FORM.pdf --to form --values values.json --flatten
```

Use `--output`, `--title`, `--artifact-kind`, `--status`, `--page-size`, and `--force` when authorized. The helper refuses collisions by default.

Every normal `--to pdf` creation requires canonical Agent Provenance. Markdown or HTML may carry exactly one native canonical table directly. Text, CSV, or JSON without that table must provide a UTF-8 ordered JSON object through `--provenance-json`; its first four entries must be `Content owner`, `Original writing agent`, `Created`, and `Artifact role`. Reject multiple native provenance sections or tables and reject `--provenance-json` when native canonical provenance is already present, so the complete artifact contains exactly one canonical provenance table. Use `--provenance-exempt-reason` only for an identified operational, schema-sensitive, third-party, or otherwise excluded input. The reason is an explicit source-preservation exception, not a general bypass.

Prefer the host document runtime. Semantic generation and forms require
`reportlab` and `pypdf`; richer extraction may use `pdfplumber`; visual checks
require Poppler; faithful HTML conversion requires a supported browser. Do not
install dependencies silently.

## Agent Provenance For Durable Artifacts

For a new standalone PDF artifact, visibly render the standard
`Agent Provenance` fields near the top and an append-only `Agent Change Log`
near the bottom. Preserve both in the embedded native source.

The visible provenance block must be a compact professional two-column `Field | Value` table containing exactly one non-empty canonical row, in this order, for `Content owner`, `Original writing agent`, `Created`, and `Artifact role`. Semantic generation uses stable 34/66 percent column widths, readable typography, wrapped long values, a repeated header row, and safe page splitting without clipping. Reject missing provenance, duplicate or empty canonical rows, aliases such as `Original writer`, and incorrect canonical row order. Separately labelled conversion or rendition history may follow the four canonical rows without replacing original authorship. Faithful HTML-to-PDF conversion preserves the source HTML provenance table through browser printing instead of rebuilding it.

For conversion of an existing artifact:

- preserve the original source creator and content owner without alteration;
- separately identify the truthful agent that created the PDF rendition;
- append a conversion entry with date, agent, source format, and target format;
- if the source has no reliable creator record, state `Not recorded` rather than
  guessing; and
- when format siblings are updated together, keep their provenance history
  semantically consistent.

When an artifact producer and this format skill are co-invoked in one turn by
one agent, record that executing agent once as the original writer; skill
co-invocation does not manufacture a second author. Never inject provenance into
operational or schema-sensitive files merely because they are durable.

## PDF Verification

Do not deliver until every applicable check passes:

1. Confirm the file exists, is non-empty, reopens, and has the expected page
   count and page size.
2. Confirm readable metadata and selectable/searchable text when expected.
3. Confirm the exact embedded source exists and round-trips when this skill
   created the artifact from a semantic source.
4. Confirm semantic Agent Provenance contains the four canonical facts in the
   professional two-column table, with wrapped values and no clipping or
   damaging split; confirm browser export preserves the HTML table unchanged.
5. Render every page for short PDFs and representative pages for long PDFs;
   inspect clipping, overlap, blank charts, missing tables or sources, broken
   glyphs, margins, headers, footers, numbering, and transitions. For semantic
   Markdown, confirm a leading H1 that matches the document title does not
   duplicate the first-page title, while a different H1 remains visible.
6. For report exports, reject app-only controls and leaked runtime details such
   as share/edit/refresh/publish controls, drag handles, manifest/package paths,
   validator state, widget labels, or local temporary paths.
7. For forms, perform the logical field-tree and widget checks required by
   Mode H; visual rendering alone is insufficient.
8. Confirm path, extension, permanent number, topic, lifecycle suffix, and
   sibling consistency.
9. Repair the source, renderer invocation, stylesheet, or form operation and
   regenerate before handoff when a check fails.

If visual inspection or a required dependency is unavailable, report the gap
and do not claim that check passed.

When creating or updating this skill, validate the folder with
`quick_validate.py` in UTF-8 mode and smoke-test semantic conversion,
matching-title de-duplication, faithful HTML rendering, embedded-source
recovery, collision refusal, PDF inspection,
interactive forms, explicit flattening, signature protection, multipage
numbering, and rendered page quality.
