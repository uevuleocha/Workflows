# Durable Artifact Format Protocol

This protocol is shared by `html-this`, `pdf-this`, and future format siblings.

## Ownership

The artifact-producing skill owns content, required sections, placement, permanent numbering, lifecycle status, update semantics, and completion gates. The format skill owns serialization, presentation, exact-source embedding and recovery, renderer selection, and format-specific validation.

Co-invocation never weakens either skill's requirements.

## Output Selection

- No format skill invoked: preserve the producer's native behavior.
- One format skill invoked: create only that requested durable format.
- Multiple format skills invoked: create exactly those requested formats.
- A native temporary file is allowed only in an approved temporary location and is not a durable output.
- Machine-required state stays native unless the wrapper embeds the exact source and the consuming workflow explicitly materializes a validated temporary copy.

## Identity And Numbering

Files with the same directory and filename stem but different managed extensions are one logical artifact:

```text
N.) Topic_pending.md
N.) Topic_pending.html
N.) Topic_pending.pdf
```

They share one permanent number and consume one namespace entry. Number scans must deduplicate by permanent prefix and stem so siblings do not inflate the next number.

## Source Authority And Exact Embedding

- When Markdown exists, it is the normal editable semantic source.
- When only HTML or PDF exists, that file is the source of record.
- HTML/PDF-only creation embeds the exact native source inside the single output.
- Text sources use UTF-8 packets or attachments; binary sources such as PDF use byte-preserving Base64 packets or binary attachments.
- A format crossover preserves the complete input: HTML-to-PDF attaches the exact HTML, while PDF-to-HTML embeds the exact PDF bytes.
- Nested source packets remain recoverable. For example, a PDF made from an `html-this` artifact may recover the HTML packet's original Markdown.
- Reverse conversion first recovers the embedded source. Best-effort extraction is permitted only when no suitable embedded source exists and must be disclosed.
- A semantic derivative is not an exact visual copy. Page images may preserve PDF appearance in HTML while accessible extracted text preserves semantics.

## Agent Provenance Presentation

When a first-party durable artifact carries `Agent Provenance`, visibly present its canonical facts in a two-column `Field | Value` table near the top. The rows are `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, and `Artifact role`, in that order. `Original writing LLM` names the model, not the agent family; use `Not recorded` when it was never captured and never backfill it. Use `Not recorded` rather than guessing unavailable creator evidence. Keep any conversion or rendition agent distinct from immutable original authorship.

Normal first-party creation must not silently omit provenance. Require exactly one native canonical table in Markdown/HTML input or truthful ordered structured fields for another semantic input. Reject multiple native provenance sections or tables and reject simultaneous native and structured canonical provenance so the complete artifact contains exactly one canonical table. The five canonical rows are non-empty, unique, and in the required order; `Original writer` is not an alias for `Original writing agent`, and `Original writing model` is not an alias for `Original writing LLM`. An append-only `Agent Change Log` carries five columns -- `Date and Time`, `Agent`, `Model`, `Action`, `Scope` -- with clock-read `YYYY-MM-DD-HH:mm:ss` timestamps and no backfilled historical rows. An explicit exemption reason is allowed only for an operational, schema-sensitive, third-party, or otherwise excluded source-preservation path.

Format renderers may improve the visible table presentation but must not alter the exact embedded source or attachment. HTML uses semantic column and row headers, an accessible responsive wrapper, long-value wrapping, theme-aware styling, and print-safe behavior. Semantic PDF generation uses stable field and value column widths, wrapped cells, a preserved/repeated header row, and safe page splitting. Faithful HTML-to-PDF printing preserves the source HTML table.

## Renderer Selection

Choose a renderer appropriate to the source rather than forcing one serializer onto every format:

- semantic Markdown/text/CSV/JSON may use document or HTML layout engines;
- styled HTML/report exports require a browser renderer for faithful PDF output;
- PDF-to-HTML uses page rendering for appearance plus semantic extraction for accessibility and search; and
- existing PDF or HTML inspection remains read-only unless a mutation is separately authorized.

Renderer fallbacks must preserve the same source of truth. Never reconstruct an available report or document from memory and call it a faithful conversion.

## Atomic Artifact Sets

Before update, reopen, finalization, or move:

1. Discover same-stem `.md`, `.html`, and `.pdf` siblings.
2. Confirm they describe the same artifact and lifecycle state.
3. Compute every destination and check for collisions.
4. Stage regenerated outputs in an approved temporary location.
5. Replace or move the complete set only after every member is ready.
6. Verify every expected source disappeared or remained as intended and every expected destination exists.

If the set cannot be updated safely, stop before knowingly splitting it. Never finalize one sibling while leaving another live.

## Lifecycle

Lifecycle suffixes precede the extension and change identically across siblings:

```text
Topic_pending.{md,html,pdf}    -> Topic_done.{md,html,pdf}
Topic_active.{md,html,pdf}     -> Topic_finalized.{md,html,pdf}
Topic_dispatched.{md,html,pdf} -> Topic_completed.{md,html,pdf}
```

The lifecycle-owning skill verifies completion and supplies content edits. Format skills only serialize or recover those authorized edits.

## Operational File Boundary

Do not replace source code, databases, configuration, backups, skill definitions, wiki control files, Git metadata, or other format-sensitive operational inputs. Human-readable exports may be added when requested.

For migration manifests, HTML/PDF-only storage is allowed only when exact JSON is embedded. Before a migration helper runs, recover that JSON to a temporary `.json`, validate it, use it, and remove it according to the workspace's temporary-file policy.
