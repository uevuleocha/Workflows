---
name: html-this
description: Create, convert, read, inspect, verify, or recover polished self-contained HTML durable artifacts while preserving content ownership and lifecycle. Supports Markdown/plain text/CSV/JSON, page-faithful and accessible PDF-to-HTML conversion with exact binary source embedding, HTML-to-Markdown recovery, and sibling operation with pdf-this. Use when the user invokes /html-this, $html-this, use html-this, asks for an HTML version/copy, asks to convert a PDF to HTML, asks to inspect or verify HTML, asks to save a durable artifact as HTML, or asks to recover Markdown from an html-this file.
---

# HTML This

Operate as the personal HTML durable-artifact surface and the format sibling of `pdf-this`. This skill owns HTML serialization, responsive presentation, exact text or binary source embedding and recovery, HTML inspection, accessibility, and format-specific verification. A co-invoked artifact producer still owns content, placement, numbering, lifecycle, and evidence.

Read `references/durable-format-protocol.md` before writing, updating, converting, reopening, or finalizing a format-managed artifact.

## Project Contract

Obey the active workspace contract, permissions, UTF-8 requirements, numbering rules, Archive layout, and lifecycle gates. Never replace an operationally required source, database, configuration, backup, or machine-consumed file with HTML merely because it is durable.

## Invocation

Treat these as direct invocation:

- `/html-this`, `$html-this`, or `use html-this`
- `make an HTML version/copy of this`
- `save this durable artifact as HTML`
- `convert this PDF to HTML`
- `read`, `inspect`, or `verify this HTML`
- `turn this html-this artifact back into Markdown`

## Modes

Select the mode from clear intent without asking.

### Mode A - Existing artifact to HTML sibling

Convert Markdown, plain text, CSV, JSON, or PDF beside its source. Preserve the source and the identical directory, permanent number, topic, and lifecycle stem:

```text
1.) Topic_pending.md
1.) Topic_pending.html
```

The siblings are one logical artifact and consume one numbering entry. Route PDF input through Mode F.

### Mode B - Co-invoked HTML-only creation

The producer runs its complete content, path, numbering, lifecycle, and validation workflow. `html-this` alone owns serialization. Save exactly one durable `.html` unless several formats were requested, keep intermediates only in an approved temporary area, and embed the exact native text or binary source.

### Mode C - HTML to Markdown

Preserve the HTML and create the same-stem `.md` sibling. Prefer exact recovery from the embedded source packet. When the packet contains a PDF, extract its text into page-labelled Markdown and disclose that the semantic Markdown cannot preserve exact page appearance. For unrelated HTML, perform best-effort semantic conversion and disclose CSS, SVG, and layout limitations.

### Mode D - Standalone explanatory HTML

For a presentation-first artifact outside another durable workflow, default to:

```text
<workspace>/Archive/Historical/HTMLs/<Subject>/N.) <Topic>.html
```

The Subject is unnumbered. Compute `N` across existing numbered files in that Subject. Use another in-workspace path only when specified by the user or contract.

### Mode E - Update or lifecycle participation

Treat same-stem `.md`, `.html`, and `.pdf` files as one artifact set. Preflight all sources and destinations, stage regenerations, apply lifecycle/content changes to every member, and stop rather than knowingly split their state. The owning skill controls completion evidence and lifecycle language.

### Mode F - PDF to self-contained HTML

Preserve the PDF and create a self-contained, responsive HTML sibling. Embed the exact original PDF bytes in the HTML source packet. When Poppler is available, render every PDF page to an inline PNG so the HTML preserves page appearance. Pair each page image with page-labelled, accessible extracted text so readers, search, assistive technology, and later Markdown recovery retain semantics.

When page rendering is unavailable, produce a clearly labelled semantic rendition from extracted text and disclose that exact page appearance was not preserved. Never describe semantic extraction alone as a faithful visual copy. Signed, fillable, image-only, or complex PDFs remain preserved byte-for-byte in the source packet even when their interactive behavior cannot exist in HTML.

### Mode G - Read, inspect, render, or verify HTML

Inspect without editing unless a change is separately requested. Confirm one doctype and document root, UTF-8 and viewport metadata, a non-empty title, balanced structure, self-contained assets, embedded-source integrity, semantic headings, visible links, image alternative text, keyboard focus, responsiveness, and print behavior as relevant. Render in a browser when visual fidelity matters.

## HTML House Style

Every generated HTML artifact is:

- one self-contained UTF-8 file with no required CDN, external font, or script;
- responsive, readable at narrow widths, and printable;
- dark by default with a `prefers-color-scheme: light` theme;
- constrained to a comfortable `1080-1180px` reading width;
- styled with clear hierarchy, panels, callouts, pills, cards, responsive tables, code blocks, page renditions, and evidence footers as appropriate;
- accessible through semantic headings, visible links, keyboard focus, alternative text, captions, and accessible extracted text; and
- source-faithful: presentation may improve, but facts, status, checklist state, evidence, and lifecycle meaning must not change.

Use inline SVG only when a diagram materially improves understanding. Do not add decorative complexity merely because HTML permits it.

## Deterministic Helper

Use `scripts/html_this.py`:

```text
python -X utf8 "<skill-dir>/scripts/html_this.py" INPUT --to html
python -X utf8 "<skill-dir>/scripts/html_this.py" INPUT.pdf --to html
python -X utf8 "<skill-dir>/scripts/html_this.py" INPUT.html --to markdown
python -X utf8 "<skill-dir>/scripts/html_this.py" INPUT.html --to inspect
```

Use `--output`, `--title`, `--artifact-kind`, `--status`, and `--force` when authorized. The helper refuses collisions by default. Complex fresh artifacts may use richer semantic HTML, but must preserve the same source packet, self-contained boundary, accessibility, and verification rules.

Every normal `--to html` creation requires canonical Agent Provenance. Markdown or HTML may carry exactly one native canonical table directly. Text, CSV, JSON, PDF, or another source without that table must provide a UTF-8 ordered JSON object through `--provenance-json`; its first four entries must be `Content owner`, `Original writing agent`, `Created`, and `Artifact role`. Reject multiple native provenance sections or tables and reject `--provenance-json` when native canonical provenance is already present, so the complete artifact contains exactly one canonical provenance table. Use `--provenance-exempt-reason` only for an identified operational, schema-sensitive, third-party, or otherwise excluded input. The reason is an explicit source-preservation exception, not a general bypass.

PDF conversion requires `pypdf` for semantic extraction and uses Poppler for page images when available. Prefer the host document runtime and do not install dependencies silently.

## Agent Provenance For Durable Artifacts

For a new standalone HTML artifact, visibly render the standard `Agent Provenance` fields near the top and an append-only `Agent Change Log` near the bottom. Preserve both in the embedded native source.

The visible provenance block must be a polished two-column `Field | Value` table containing exactly one non-empty canonical row, in this order, for `Content owner`, `Original writing agent`, `Created`, and `Artifact role`. Use semantic `<table>` markup, column headers, row headers, an accessible responsive wrapper, readable borders and spacing, long-value wrapping, narrow-screen behavior, light/dark theme compatibility, and print styling. A concise caption is encouraged. Do not use a provenance `<dl>`, loose bullets, or indented label/value pairs. Reject missing provenance, duplicate or empty canonical rows, aliases such as `Original writer`, and incorrect canonical row order. Separately labelled conversion or rendition history may follow the four canonical rows without replacing or duplicating original authorship.

For conversion of an existing artifact:

- preserve the original source creator and content owner without alteration;
- separately identify the truthful agent that created the HTML rendition;
- append a conversion entry with date, agent, source format, and target format;
- if the source has no reliable creator record, state `Not recorded` rather than guessing; and
- when format siblings are updated together, keep their provenance history semantically consistent.

When an artifact producer and this format skill are co-invoked in one turn by one agent, record that executing agent once as the original writer; skill co-invocation does not manufacture a second author. Never inject provenance into operational or schema-sensitive files merely because they are durable.

## HTML Verification

Before handoff:

1. Confirm path, extension, permanent number, topic, lifecycle suffix, and the requested durable-format count.
2. Confirm exact embedded text or binary source recovery.
3. Confirm one doctype, one `<html>` root, UTF-8 metadata, viewport metadata, a non-empty title, and valid structural balance.
4. Confirm required assets are inline, images have useful alternative text, headings remain semantic, links are visible, and keyboard focus is usable.
5. Confirm Agent Provenance uses scoped column/row headers, contains all four canonical facts, has responsive and print styling, and is not a `<dl>`.
6. For PDF conversion, confirm embedded PDF bytes are identical, page count matches, every rendered page is present when Poppler is available, and accessible extracted text accompanies the visual rendition.
7. Inspect the rendered page at desktop, narrow viewport, and print layout when browser access permits. Otherwise disclose that visual rendering was not run.
8. For an artifact set, confirm every sibling expresses the same content and lifecycle state.
9. Repair and regenerate before handoff when a check fails.

When creating or updating this skill, validate the folder with `quick_validate.py` in UTF-8 mode and smoke-test Markdown, text, CSV, JSON, PDF-to-HTML visual and semantic conversion, exact text and binary source recovery, collision refusal, structural inspection, responsive rendering, and standalone naming rules.
