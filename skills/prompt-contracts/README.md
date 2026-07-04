# Prompt Contracts — Adoption Guide

Defines a 5-part engineering spec (GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE) before
implementation so "done" has zero ambiguity. On its own it delivers the contract in chat and writes
no standalone contract file.

## Depended on by

Other skills call `prompt-contracts` as a mandatory or verifying step. If you adopt any of these,
adopt `prompt-contracts` too:

| Skill | How it uses `prompt-contracts` |
|---|---|
| `imp-upd-plan` | Hard — embeds a Prompt Contract in every plan (`## Prompt Contract Integration`) |
| `imp-upd-task` | Hard — embeds a Prompt Contract in every task; the contract holds the task's Definition of Done |
| `finalize-plan` | Soft — verifies the embedded contract before finalizing (`## Prompt Contract Review`) |
| `finalize-task` | Soft — verifies the embedded contract before finalizing (`## Prompt Contract Review`) |

When invoked by `imp-upd-plan` or `imp-upd-task`, the calling skill embeds the contract into that
plan/task artifact under a `## Prompt Contract` section. `prompt-contracts` itself still writes no
standalone contract file.

For the general mechanism, see the workspace's `Documentation/` folder,
`3.) Skill-to-Skill Calls — Pattern and Registry.md`.
