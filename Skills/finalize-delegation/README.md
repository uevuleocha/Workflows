# Finalize Delegation — Adoption Guide

`finalize-delegation` closes a dispatched delegation: it verifies every assignment returned **and was integrated**, inspects **every** named parent plan and/or task, renames `_dispatched` → `_completed`, moves the record from `Archive\Live\Delegations\` to `Archive\Historical\Delegations\`, and repairs **every** named parent's `Delegation` pointer.

It is the closing half of a lifecycle that `delegate-this` opens. On its own it does nothing — there is no delegation to close.

## Part Of A System

This skill is meaningless in isolation, which is why this README exists — the house rule is that a skill entangled with other skills carries a README naming them.

| Skill           | Relationship                                                    |
| --------------- | --------------------------------------------------------------- |
| `delegate-this` | Creates the `_dispatched` record this skill closes              |
| `finalize-plan` | Prompts the user to run this skill when it closes a parent plan |
| `finalize-task` | Prompts the user to run this skill when it closes a parent task |
| `plan-this`     | Authors the parent plan carrying the `Delegation` pointer       |
| `task-this`     | Authors the parent task carrying the `Delegation` pointer       |

The dependency direction is strict and one-way. `delegate-this` calls the plan/task skills; the plan/task skills never call it. `finalize-plan` and `finalize-task` **prompt** for this skill but never invoke it and never touch a delegation file. Adopt `finalize-delegation` alongside `delegate-this`, or neither.

## The Lifecycle

```text
delegate-this        →  Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md
finalize-delegation  →  Archive\Historical\Delegations\<Subject>\N.) <Topic>_completed.md
```

`N` is preserved across the move. Subject folders are never numbered on either side. The record's **content** is immutable — assignment packets are never rewritten, because they are what the receiving agents actually acted on. Only the status line, the lifecycle line, the Assignment Overview's status cells, and a `## Notes` entry change. **Every lowercase child prefix** (`Na.)`, `Nb.)`, …) on the delegation's mini artifacts and return reports is preserved verbatim — never stripped or renumbered.

## Return-Report Freeze

Closing the delegation **freezes the entire session-summary / return-report family**. Every return report (files ending in `Report.md` at the reserved child prefixes) and its append-only `## Feedback` ledger becomes a closed historical artifact — no further feedback may be appended after the delegation is `_completed`. The orchestrator/master summary is likewise frozen. This skill does not rewrite the reports; it only enforces the freeze.

## Two Gates That Will Stop You

**The parent gate.** A Mode A delegation always has a parent plan and/or task — sometimes both. This skill inspects **every** named parent, not just the first. If any is still open, it will not close the delegation silently — it asks, because a parent is what proves the returned work was integrated. Each open parent needs its **own** override; one does not cover another. A parent that is missing or unreadable stops the skill outright.

**Returned ≠ integrated.** An assignment that came back is not an assignment that landed. The skill walks the Assignment Overview row by row and requires evidence of both. Dispatch is neither.

## Adoption Prompt

Give this prompt to your agent:

```text
Read this README and the skill's SKILL.md, then read delegate-this's SKILL.md and its
references/mode-a-delegation-template.md so you understand the record shape this skill
closes. Confirm my workspace has Archive\Live\Delegations\ and Archive\Historical\
before the first run. Do not assume the original maintainer's paths.
```

## Optional artifact formats

Pairs with `html-this` and `pdf-this` so every existing format sibling is finalized together without changing the owning lifecycle gate.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
