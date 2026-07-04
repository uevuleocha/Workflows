# Finalize Task — Adoption Guide

Finalizes pending workspace housekeeping/admin task files: verifies Definition of Done evidence,
applies completed styling, and renames `_pending.md` to `_done.md`.

## Dependency

`finalize-task` has a soft dependency on the `prompt-contracts` skill. It reads and verifies the
Prompt Contract that `imp-upd-task` embedded in the task — walking each DEFINITION OF DONE item and
FAILURE condition before finalizing (see the `## Prompt Contract Review` section in `SKILL.md`). For
tasks created under the current workflow, the Definition of Done lives in the contract's DEFINITION OF
DONE clause. It does not need to invoke `prompt-contracts` itself, and it falls back gracefully for
older tasks that still carry a standalone `## Definition of Done` section.

**If you adopted `finalize-task` from Uzo (U-Z-O), adopt it together with `imp-upd-task` and
`prompt-contracts`.** The three form the task lifecycle: `imp-upd-task` writes the contract,
`prompt-contracts` defines its shape, and `finalize-task` verifies against it.

For the general mechanism, see the workspace's `Documentation/` folder,
`3.) Skill-to-Skill Calls — Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill pairs with `imp-upd-task` and understands the
`prompt-contracts` contract format; make sure all three are installed in the same agent installs
(Codex / Claude / Antigravity). Use my OS path conventions and ask before creating missing folders.
```
