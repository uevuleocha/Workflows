# Manifest This

Creates or updates official manifests - durable, numbered lists of things to be edited, updated, deleted, or otherwise dealt with - saved under `Archive/Historical/Manifests/<Subject>/` with `N.) <Topic>` naming and no lifecycle (always historical, like summaries). HTML by default, Markdown-only or both on request; migration skills invoke it with a Markdown default so the embedded JSON payload stays recoverable for their execution helpers.

## Related skills

- Calls `html-this` for HTML serialization (source-packet embedding and provenance rendering).
- Calls `markdown-table-aligner` on Markdown manifests and exact Markdown source packets before handoff or serialization.
- Pairs with `session-summary` (same always-historical Archive placement model).
- Called by all five `*-workspace-chat-migration` skills to create and update migration manifests.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
