# Prompt Contracts — Adoption Guide

Defines a 5-part engineering spec (GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE) before implementation so "done" has zero ambiguity. Immediately testable evidence stays in the blocking Definition of Done; evidence that genuinely requires later use or an external event is separated into a non-blocking Deferred Real-World Verification checklist. On its own this skill delivers the contract in chat and writes no standalone contract file.

## Depended on by

Other skills call `prompt-contracts` as a mandatory or verifying step. If you adopt any of these, adopt `prompt-contracts` too:

| Skill           | How it uses `prompt-contracts`                           |
| --------------- | -------------------------------------------------------- |
| `plan-this`     | Hard - embeds a contract in every plan.                  |
| `task-this`     | Hard - embeds a contract in every task.                  |
| `north-star`    | Hard - embeds without approval; chat display is opt-in.  |
| `finalize-plan` | Soft - verifies the embedded contract before finalizing. |
| `finalize-task` | Soft - verifies the embedded contract before finalizing. |

When invoked by `plan-this` or `task-this`, the calling skill embeds the contract into that plan/task artifact under a `## Prompt Contract` section. `prompt-contracts` itself still writes no standalone contract file.

North Star is the embedded-caller blueprint: it always stores the five-part contract, never pauses for separate contract approval, and shows the contract in chat only after explicit user opt-in. In plain language, a good result meets every Definition of Done item with no active Failure; a bad result has at least one Failure, and "things to avoid" are those Failure conditions. The five canonical headers and their logic do not change.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls — Pattern and Registry.md`.
