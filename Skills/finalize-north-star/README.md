# Finalize North Star

`finalize-north-star` verifies an in-progress North Star's complete Prompt Contract from evidence, marks only supported DoD items complete, rejects active Failure conditions or unverified Constraints and Format, enforces exactly-once timing, preserves the mandatory provenance table immediately after lifecycle, appends its attributed change-log entry, changes the lifecycle to `FINALIZED`, and moves the same numbered artifact from Live to Historical. Agent Change Log remains the final human-readable section and Base64 machine state remains last. Its receipt reports helper timing once, and the selected-star footer remains compulsory through the successful `FINALIZED THIS TURN` response.

## Related skills

- `north-star` creates, reopens, times, and maintains the live artifact and ships the required lifecycle helper, including the provisional turn-timer safety net.
- `prompt-contracts` supplies the five-part contract that this finalizer treats as its authoritative completion boundary.
- Adopt and sync `north-star` and `finalize-north-star` together.

There is no manual finalization fallback.

## Optional artifact formats

Pairs with `html-this` and `pdf-this` so every existing format sibling is finalized together without changing the owning lifecycle gate.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
