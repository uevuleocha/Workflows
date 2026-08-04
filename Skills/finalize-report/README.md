# Finalize Report — Adoption Guide

`finalize-report` is the closing half of the report lifecycle opened by `report-this`.

```text
report-this      → Archive\Live\Reports\<Subject>\N.) <Topic>_pending.md
finalize-report  → Archive\Historical\Reports\<Subject>\N.) <Topic>_reported.md
```

It verifies completion evidence, changes the dismissible footer to `REPORTED ✅`, renames the suffix, and performs a true Live-to-Historical move. It preserves the Subject, permanent number, title, and official body.

The terminal state never splits into sent versus read. Revisions and reopening belong exclusively to `report-this`.

## Optional artifact formats

Pairs with `html-this` and `pdf-this` so every existing format sibling is finalized together without changing the owning lifecycle gate.
