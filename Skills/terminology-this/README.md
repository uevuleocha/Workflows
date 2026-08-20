# Terminology This - Adoption Guide

Creates new Terminology documents and adds terms to existing ones using a real definition, an analogy, and a for-dummies explanation for every term. Invoke with `/terminology-this`, `terminology-this: <term>`, or a clear request to create or extend a terminology reference.

## Related skills

- Requires `doc-this` as the durable documentation owner.
- Requires `exact-model-confirmation-gate` before the first model-attributed durable write in a stable session.
- Ships with `markdown-table-aligner`; `doc-this` invokes it at the file-write boundary when tables are present.
- Prefers `analogy` and `for-dummies` for the two plain-language passes, with inline fallbacks when either is unavailable.

