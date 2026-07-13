# Report This — Adoption Guide

`report-this` creates, updates, and reopens durable reports. It supports Mode A
platform/issue reports and Mode B analytical/professional reports while sharing
one lifecycle with `finalize-report`.

```text
report-this      → Archive\Live\Reports\<Subject>\N.) <Topic>_pending.md
finalize-report  → Archive\Historical\Reports\<Subject>\N.) <Topic>_reported.md
```

Adopt `report-this` and `finalize-report` together. The creator owns reopening;
the finalizer owns closure. Both preserve the Subject and permanent number.

Reports intentionally have no top workflow header. A dismissible footer at the
bottom contains the lifecycle marker and dates so the official body remains
send-ready after the footer is removed.

Mode A uses `references/mode-a-template.md`; Mode B uses
`references/mode-b-template.md`; both use
`references/dismissible-footer.md`.
