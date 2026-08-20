# Finalize Report — Adoption Guide

`finalize-report` is the closing half of the report lifecycle opened by `report-this`.

```text
report-this      → Archive\Live\Reports\<Subject>\N.) <Topic>_pending.md
finalize-report  → Archive\Historical\Reports\<Subject>\N.) <Topic>_reported.md
```

It verifies completion evidence, changes the dismissible footer to `REPORTED ✅`, renames the suffix, and performs a true Live-to-Historical move. It preserves the Subject, permanent number, title, and official body.

The terminal state never splits into sent versus read. Revisions and reopening belong exclusively to `report-this`.

When a report is finalized, its send-ready staged copy (created by `report-this` under `tmp\<subject>-reports-send-ready\`) is deleted, and the staging folder is removed once it empties.

## Optional artifact formats

Pairs with `html-this` and `pdf-this` so every existing format sibling is finalized together without changing the owning lifecycle gate.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
