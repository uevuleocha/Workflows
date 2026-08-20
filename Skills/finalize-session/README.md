# Finalize Session — Adoption Guide

Runs `session-name`, then instructs the current agent to compare concrete session evidence against the current workspace wiki's unresolved-verification page, then creates `session-summary`, and finally offers optional temporary-file cleanup. Evidence-supported items are checked directly in their finalized source artifacts with a change-log row; deliberate unticked dispositions receive the standardized adjacent marker. Any such source edit is included in the newly created summary. Other workspace wikis are checked only when the user explicitly names them.

The one compulsory input is the **chat-session identifier** (`39`, `39a`). One unlabeled number always means that identifier, never the summary file number. Optional Subject, Topic, summary number, and Directory are passed to `session-summary` only when supplied.

After naming, reconciliation, and summarizing complete, `finalize-session` lists agent-created temporary files across all workspaces written to during the session and offers the user the choice to delete none (default), some, or all.

`finalize-session` is suggestion-and-artifact orchestration only. It never renames, closes, archives, or deletes the actual platform chat.

## Required child skills

Both must be loaded; the wrapper stops before any partial execution if either is missing.

| Child skill       | What it owns                                                     |
| ----------------- | ---------------------------------------------------------------- |
| `session-name`    | The eight grounded chat-label suggestions and all naming rules   |
| `session-summary` | The durable summary artifact, numbering, ACTS shape, and receipt |

Both children remain independently invocable with unchanged behavior. Use `session-name` alone for names only, or `session-summary` alone for the recap only.

## Related skills

- `markdown-table-aligner` — validates tables after a direct finalized-artifact edit.
- `exact-model-confirmation-gate` — resolves the exact model before a change-log write.
