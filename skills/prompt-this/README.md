# Prompt This — Adoption Guide

`prompt-this` turns a request into a **durable, structured prompt file** — one you can hand an agent weeks later, cold, and it will know what to do, what "done" means, and what counts as failure.

It is the third member of a family:

| Artifact | Create / update | Finalize          | Lifecycle          |
|----------|-----------------|-------------------|--------------------|
| Plan     | `imp-upd-plan`  | `finalize-plan`   | active → finalized |
| Task     | `imp-upd-task`  | `finalize-task`   | pending → done     |
| Prompt   | `prompt-this`   | `finalize-prompt` | pending → executed |

## Calls Other Skills

**This skill depends on another skill.** That is why this README exists — the house rule is that any skill which calls other skills carries a README naming what it calls, so an adopter knows what else to bring along.

| Skill              | When it is called                          | If unavailable                                      |
|--------------------|--------------------------------------------|-----------------------------------------------------|
| `prompt-contracts` | On **every** create and update             | Pause, warn, author inline only if the user says so |
| `finalize-prompt`  | Never called — the user runs it separately | Tell the user; the prompt stays `PENDING`           |

`prompt-this` calls `prompt-contracts`. It does **not** call `finalize-prompt` — that skill is the user's to run, and it is the only thing that may close a prompt.

`prompt-this` has **no dependency on `delegate-this`.** Prompt files carry a `**Delegation:** N/A` pointer field and nothing more. No routing, no packets, no platforms, no subagents.

If you adopt `prompt-this`, adopt `prompt-contracts` and `finalize-prompt` too.

## What Makes a Prompt File Recognizable

The point of the fixed structure: *if you wake up one day and see a markdown file in front of you, you can tell your prompt skill made it.*

Every prompt carries the same `Status:` / `Prompt lifecycle:` header lines and the same set of headings — `## What This Prompt Is`, `## Prompt`, `## Context`, `## Instructions`, `## Prompt Contract`, `## Verification Checklist`. The canonical shape lives in `references/prompt-template.md`, and agents reuse it rather than reconstructing headings from memory.

**Four sections, four distinct jobs.** `## Prompt` is what you run. `## Instructions` is how you run it. `## Prompt Contract` is what success and failure mean. `## Verification Checklist` is how success was actually evidenced. The contract *defines* success; the checklist *records* it. Neither substitutes for the other.

## The Contract Travels With the Prompt

`prompt-contracts` authors a 5-part contract — GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, FAILURE — which is shown to you in chat **and embedded verbatim in the file**.

That embedding is the whole integration goal: the agent that eventually runs the prompt already has the scope, the done-criteria, and the failure conditions the moment it opens the file. It never re-derives them, and `finalize-prompt` has an authoritative gate to check against.

## Lifecycle

```text
Pending:   <Workspace>\Archive\Live\Prompts\<Subject>\N.) <Topic>.md
Executed:  <Workspace>\Archive\Historical\Prompts\<Subject>\N.) <Topic>.md
```

Lifecycle is expressed by **location plus the in-file `Status:` line** — there is no `_pending` / `_executed` filename suffix.

**Subject** is the broad category (the school-subject sense: "math"). **Topic** is the specific thing ("polynomials"). Subject folders are never numbered; only files carry `N.)`. Keep Subjects broad, or you end up with one folder per file.

**`N` is permanent.** Before writing, the skill captures `previous_max` — the highest numeric prefix across **both** the Live and Historical Subject folders (`0` if neither has one) — and assigns `N = previous_max + 1`. It is assigned once, and never renumbered or reclaimed: not on finalization, not on reopen.

The snapshot matters. Once the new file exists it belongs to that union, so recomputing the maximum afterward returns `N` itself — validating against a *fresh* `max + 1` would wrongly demand `N + 1`. Validation compares against the **captured** value.

Scanning only the Live side silently reuses a number already held by an executed prompt. And because the Subject layer makes the tree two levels deep, any scan must descend into the Subject folder on **both** sides.

**The filename never contains the word "prompt."** The `Prompts\` folder already says what it is, just as plan files don't say "plan." The one exception is an explicit opt-in when you intend to share a prompt publicly.

## Two Rules That Will Stop You

**Only `finalize-prompt` closes a prompt.** It alone changes PENDING → EXECUTED and moves the file Live → Historical. **There is no manual fallback.** If `finalize-prompt` is unavailable, the prompt stays `PENDING` where it is, and you install the skill. Moving it by hand skips the contract review and the checklist verification — which is how a prompt gets marked done without ever having been done.

**Reopen is `prompt-this`'s job, not the finalizer's.** An executed prompt moves Historical → Live only when you explicitly ask to revise, extend, rerun, or reopen it — never merely because you mentioned it. Prior execution evidence is preserved, `N.)` is preserved, and a collision on the Live side stops the skill rather than overwriting anything.

## Resources

- `SKILL.md` — the procedure
- `references/prompt-template.md` — the canonical artifact shape

## Adoption Prompt

Give this prompt to your agent:

```text
Read this README and the skill's SKILL.md, then read references/prompt-template.md.
Confirm my workspace has Archive\Live\Prompts\ and Archive\Historical\Prompts\, and
that prompt-contracts and finalize-prompt are installed. Show me the existing Subject
folders before creating the first prompt. Do not assume the original maintainer's paths.
```
