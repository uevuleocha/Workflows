# Finalize Session — Adoption Guide

Runs `session-name` and `session-summary` together in one pass so a single invocation both labels the chat and saves the durable recap. It is a thin orchestrator: it owns input routing, dependency preflight, resume behavior, and the combined receipt — nothing else.

The one compulsory input is the **chat-session identifier** (`39`, `39a`). One unlabeled number always means that identifier, never the summary file number. Optional Subject, Topic, summary number, and Directory are passed to `session-summary` only when supplied.

`finalize-session` is suggestion-and-artifact orchestration only. It never renames, closes, archives, or deletes the actual platform chat.

## Required child skills

Both must be loaded; the wrapper stops before any partial execution if either is missing.

| Child skill       | What it owns                                                       |
|-------------------|--------------------------------------------------------------------|
| `session-name`    | The eight grounded chat-label suggestions and all naming rules      |
| `session-summary` | The durable summary artifact, numbering, ACTS shape, and receipt    |

Both children remain independently invocable with unchanged behavior. Use `session-name` alone for names only, or `session-summary` alone for the recap only.
