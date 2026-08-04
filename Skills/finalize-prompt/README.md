# Finalize Prompt — Adoption Guide

`finalize-prompt` closes a pending prompt: it verifies every Prompt Contract **DEFINITION OF DONE** item and every **Verification Checklist** item against evidence, confirms no FAILURE condition is active, rewrites the header to `EXECUTED ✅`, and moves the file from `Archive\Live\Prompts\<Subject>\` to `Archive\Historical\Prompts\<Subject>\` — renaming its suffix `_pending` → `_executed` while its `N.)` prefix and Topic stay unchanged.

It is the closing half of a lifecycle that `prompt-this` opens. On its own it does nothing; there is no prompt to close.

## Part Of A System

This skill is meaningless in isolation, which is why this README exists — the house rule is that a skill entangled with other skills carries a README naming them.

| Skill              | Relationship                                               |
|--------------------|------------------------------------------------------------|
| `prompt-this`      | Creates the pending prompt this skill closes               |
| `prompt-this`      | Also owns **reopen** — Historical back to Live             |
| `prompt-contracts` | Authors the contract this skill checks as the closing gate |

The dependency direction is strict and one-way. `prompt-this` calls `prompt-contracts`; neither calls this skill. **You run `finalize-prompt` yourself**, when the work the prompt asked for is actually done.

Adopt `finalize-prompt` alongside `prompt-this`, or neither.

## The Lifecycle

```text
prompt-this      →  Archive\Live\Prompts\<Subject>\N.) <Topic>_pending.md          (PENDING ⌛)
finalize-prompt  →  Archive\Historical\Prompts\<Subject>\N.) <Topic>_executed.md   (EXECUTED ✅)
```

Lifecycle is expressed by **location, the in-file `Status:` line, and a filename suffix** — `_pending` while Live, `_executed` once finalized. `N` and the Topic are preserved across the move; only the suffix is renamed. Subject folders are never numbered on either side.

The `## Prompt` payload is **never rewritten.** It is the historical record of what was asked. Only the status line, the lifecycle line, the contract and checklist headings, and a dated `## Notes` entry change.

## Three Gates That Will Stop You

**The contract gate.** Every DEFINITION OF DONE item must be satisfied or explicitly deferred, and no FAILURE condition may be active. The contract is embedded in the prompt file, so the gate travels with the artifact.

**The checklist gate.** The contract *defines* success; the checklist *records* it. Both are gates, and a passing contract is **not**, by itself, evidence that the checklist passed.

The finalizer **may** check a checklist item — but only when current-session evidence, durable execution evidence, or your explicit confirmation supports it. It never assumes, invents, or silently marks an unsupported item complete. An unsupported item needs an explicit waiver or deferral with a recorded reason, or finalization stops.

**Existence is not evidence.** A prompt is never marked executed because of its age, its location, or the fact that it has been sitting there a while. Someone has to have actually done the work, and it has to be recorded.

## No Manual Fallback

**Only this skill may change PENDING → EXECUTED or move a prompt Live → Historical.**

If it is unavailable, the correct behavior is to stop: leave the prompt `PENDING` where it is, and install the skill. Never move or rename a prompt file by hand. A manual move skips the contract review and the checklist review — which is exactly how a prompt gets recorded as executed without ever having been executed.

## Reopen Is Not This Skill's Job

An executed prompt returns to `Live/` only through `prompt-this`, and only when you explicitly ask to revise, extend, rerun, or reopen it. This skill will not reopen anything, and it will refuse to finalize a prompt that already sits in `Historical/`.

## Adoption Prompt

Give this prompt to your agent:

```text
Read this README and the skill's SKILL.md, then read prompt-this's SKILL.md and its
references/prompt-template.md so you understand the artifact shape this skill closes.
Confirm my workspace has Archive\Live\Prompts\ and Archive\Historical\Prompts\ before
the first run. Do not assume the original maintainer's paths.
```

## Optional artifact formats

Pairs with `html-this` and `pdf-this` so every existing format sibling is finalized together without changing the owning lifecycle gate.
