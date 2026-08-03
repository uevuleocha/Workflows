# North Star

`north-star` creates or reopens a durable `IN PROGRESS` artifact under
`Archive/Live/North Stars/<Subject>/`, keeps one objective authoritative across
continuous or phased work, and records every pursued agent turn as one
helper-timed ledger entry. Every unpaused active turn opens a provisional
full-turn safety-net timer; precise authoritative pursuit timing remains the
preferred ledger source and discards the provisional timer when it succeeds.
Waiting between turns is never counted. Each handoff reports the latest pursuit
and helper-computed grand total exactly once. Fallback pursuits are disclosed.

When the objective and every verification item are proven,
`finalize-north-star` closes the current pursuit, changes the lifecycle to
`FINALIZED`, and moves the same numbered artifact to Historical.

## Related skills

- `finalize-north-star` is the only workflow allowed to finalize and archive a
  live North Star, and its receipt reports the latest pursuit plus grand total.
  It refuses finalization with open authoritative or provisional timing.
- Adopt and sync `north-star` and `finalize-north-star` together.
- Native platform goal features are optional companions, never dependencies.

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable
artifacts while this skill retains content and workflow ownership.
