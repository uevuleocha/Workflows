# Finalize North Star

`finalize-north-star` verifies that an in-progress North Star reached its
objective, enforces precisely scoped pursuit ownership with no duplicate or
manufactured ledger entries, guards against open authoritative or provisional
timing, changes the lifecycle to `FINALIZED`, and moves the same numbered
artifact from Live to Historical. Its receipt reports the latest pursuit and
helper-computed grand total exactly once. Fallback pursuits remain disclosed.
If finalization is refused or deferred, the run stays active or paused and its
selected star footer remains visible.

## Related skills

- `north-star` creates, reopens, times, and maintains the live artifact and
  ships the required lifecycle helper, including the provisional turn-timer
  safety net.
- Adopt and sync `north-star` and `finalize-north-star` together.

There is no manual finalization fallback.

## Optional artifact formats

Pairs with `html-this` and `pdf-this` so every existing format sibling is
finalized together without changing the owning lifecycle gate.
