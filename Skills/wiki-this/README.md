# Wiki This

Sets up a schema-driven plain-Markdown wiki in the current workspace. The user must explicitly name every source root; the skill never infers one. Once those roots are known, it autonomously creates the schema, version-1 coverage contract, unresolved-verification page, history format, navigation, log, workspace pointers, and initial full sync unless scaffold-only setup was requested.

## Related skills

- `wiki-sync` — maintains and ingests an existing schema-governed wiki.

## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
