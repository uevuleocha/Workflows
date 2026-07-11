# Delegate This — Adoption Guide

`delegate-this` divides a substantial objective — a build, a migration, a research effort, a backlog — among multiple agents, dispatches clear assignments, tracks returns, and integrates the result without losing the parent objective.

It has two modes:

- **Mode A — Cross-platform.** The orchestrator cannot message other coding-agent platforms directly, so it writes one durable delegation record containing shared context plus a self-contained assignment packet per platform. You carry that file to each platform.
- **Mode B — Within-platform.** The orchestrator drives the host's own native subagents directly. No record is created merely to dispatch.

**Delegation is not a synonym for parallelism.** Serial, parallel, and mixed execution waves are all first-class.

## Calls Other Skills

**This skill depends on other skills.** That is why this README exists — the house rule is that any skill which calls other skills carries a README naming what it calls, so an adopter knows what else to bring along.

| Skill                 | When it is called                           | If unavailable                                      |
|-----------------------|---------------------------------------------|-----------------------------------------------------|
| `imp-upd-plan`        | To author a parent or mini **plan**         | Pause, warn, author inline only if the user says so |
| `imp-upd-task`        | To author a parent or mini **task**         | Pause, warn, author inline only if the user says so |
| `finalize-delegation` | To close the record when work is integrated | Stop. Leave `_dispatched`; install and run it       |

**There is no manual lifecycle fallback.** If `finalize-delegation` is unavailable, the
record stays `_dispatched` exactly where it is. Install or load the skill — from the
local master, or by re-running `global-sync` — and then run it. Never move, rename, or
otherwise close a delegation record by hand: doing so skips the return-and-integration
verification and the parent-pointer repair, which is precisely how records get orphaned.

`delegate-this` calls those skills. **They never call it.** `imp-upd-plan` and `imp-upd-task` carry only a thin `Delegation` pointer field that defaults to `N/A` — no routing logic, no packet schema, no delegation workflow. That one-way boundary is deliberate: adopt `delegate-this` without them and it degrades gracefully; adopt them without it and they never notice.

If you adopt `delegate-this`, adopt `imp-upd-plan`, `imp-upd-task`, and `finalize-delegation` too.

## The Compulsory Parent Rule (Mode A only)

**A Mode A delegation must always have a parent plan and/or task. A plan or task need not have a delegation.**

This asymmetry is the spine of the design. Without it, a dispatched record has nothing to hang from and can be silently orphaned once the real work finishes. With it, the parent's `Delegation` field is a tripwire: when `finalize-plan` or `finalize-task` closes the parent, it sees the pointer and prompts you to run `finalize-delegation`.

If no parent exists when you invoke Mode A, `delegate-this` will create one with you before dispatching anything.

**Mode B is parent-optional.** It writes no durable record, so there is nothing to orphan. Reuse a parent if one exists; never manufacture one just to satisfy the rule.

## Lifecycle

A delegation is a lifecycle artifact, sibling to plans (`_active` → `_finalized`) and tasks (`_pending` → `_done`):

```text
Dispatched:  <Workspace>\Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md
Completed:   <Workspace>\Archive\Historical\Delegations\<Subject>\N.) <Topic>_completed.md
```

The record's **content** is immutable after dispatch — packets are never rewritten. Its **state** is not, which is what the suffix tracks. Only `finalize-delegation` performs the rename and the move; **there is no manual fallback.** If it is unavailable, the record stays `_dispatched` and you install the skill.

Subject folders are never numbered. `N` is assigned once, calculated across **both** the Live and Historical Subject folders, and never renumbered or reclaimed.

## Platforms

The maintained platform identities are Claude Code, Codex, zCode, Hermes, and Antigravity. **This is not a list of platforms available on any given run.** Mode A always asks which are authorized right now — subscriptions lapse, limits are hit, and some work is too sensitive for some platforms.

Routing factors, standing preferences, cost gates, and the model-recommendation policy live in `references/routing-and-cost-policy.md`. That file is where an adopter should edit platform policy, not `SKILL.md`.

## Resources

- `SKILL.md` — the procedure
- `references/mode-a-delegation-template.md` — the durable record's shape
- `references/assignment-packet-template.md` — the 19 required packet fields
- `references/routing-and-cost-policy.md` — routing factors, cost gate, model policy

## Adoption Prompt

Give this prompt to your agent:

```text
Read this README and the skill's SKILL.md, then read references/routing-and-cost-policy.md.
Help me adapt the platform list, the standing preference order, and the cost rules to the
coding-agent platforms I actually use. Confirm my workspace has an Archive/ folder before
the first Mode A run. Do not assume the original maintainer's platform set or paths.
```
