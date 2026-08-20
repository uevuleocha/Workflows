# GitHub Involvement

Owns the workspace GitHub Involvements document after creation: checks tracked items (active and passive) for updates, reports what changed since the last check, moves closed items to the Done section, and runs a bounded retroactive sweep for active involvements that predate the system. It never files anything.

Invoke with `/github-involvement`, `$github-involvement`, "check my GitHub involvements," "sync the involvements list," "mark an involvement done," or "sweep GitHub history into the document."

## Related skills

- Pairs with `github-file-this`, which publishes involvements and appends them to the document; this skill never files.
- Requires `exact-model-confirmation-gate` before delegated model-attributed document writes.
