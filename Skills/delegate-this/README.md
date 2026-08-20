# Delegate This — Adoption Guide

`delegate-this` divides a substantial objective — a build, a migration, a research effort, a backlog — among multiple agents, dispatches clear assignments, tracks returns, and integrates the result without losing the parent objective.

It has two modes:

- **Mode A — Cross-platform.** The orchestrator cannot message other coding-agent platforms directly, so it writes one durable delegation record containing shared context plus a self-contained assignment packet per platform. You carry that file to each platform.
- **Mode B — Within-platform.** The orchestrator drives the host's own native subagents directly. No record is created merely to dispatch.

**Delegation is not a synonym for parallelism.** Serial, parallel, and mixed execution waves are all first-class.

## Artifact Families and Child Numbering

A Mode A dispatch creates linked **families of artifacts** that all live under one **execution workspace** (resolved before anything is created). Each family has its **own numeric anchor** from its own Subject namespace — the anchors need not match; explicit paths connect the families:

- **Plan/Task family** — parent plan and/or task (`N.)`, e.g. `1.)`) plus mini artifacts (`1a.)`, `1b.)` … `1e.)`), inheriting the Plan/Task master `N`.
- **Delegation record** — its own `N.` from the Delegation Subject namespace (e.g. `1.)`, independent of the Plan number).
- **Summary family** — orchestrator/master summary (`N.)`, e.g. `9.`) plus one delegated **return report** per assignment (`9a.)`, `9b.)` … `9e.`), inheriting the Summary master `N`. Return-report filenames end in `Report.md`.

Each anchor is calculated across its own combined Live + Historical namespace. The orchestrator **reserves every child prefix before dispatch** and writes each exact reserved prefix into the assignment overview, the mini-artifact table, the return-report table, and each packet. "Create a mini plan later" without a reserved prefix is not allowed. `plan-this`, `task-this`, and `session-summary` understand this grammar enough to allocate the next suffix within their own family and obey a reserved prefix — they do not absorb the delegation workflow.

## Mandatory Return Reports

Every returning assignment writes a **return report** (ending in `Report.md`) using session-summary structure plus an **append-only `## Feedback` ledger**. Report content and earlier feedback entries are immutable; feedback is appendable only while the delegation is active; the whole report (and its ledger) freezes when `finalize-delegation` closes the delegation.

## Per-Packet Checkpoint Policy

Every packet carries an explicit **Checkpoint Policy**: where execution stops (default: complete the packet continuously; only `USER CHECKPOINT` midpoints pause), whether sync is allowed (default for skill work: centralized sync), and what deliverables must be returned first.

## Centralized Synchronization (Skill Work)

For multi-agent skill work in one Workflows repository, the default is **centralized synchronization**: workers edit and validate local masters and return deliverables; the orchestrator runs one final global-sync + parity pass after review. Workers never pause merely to ask about sync. Explicit user override wins.

## Provider-Neutral Hermes Routing

Hermes is routed by **capability, trust, and tools**, not a fixed provider label. `delegate-this` asks which provider/model Hermes currently uses and which quota pool it shares, routes by capability/trust/tools, schedules by quota, and never permanently binds or downgrades Hermes based on GLM, OpenAI, Codex, or zCode. Pay-as-you-go providers always require explicit approval.

## Calls Other Skills

**This skill depends on other skills.** That is why this README exists — the house rule is that any skill which calls other skills carries a README naming what it calls, so an adopter knows what else to bring along.

| Skill                 | Called for              | If unavailable                     |
| --------------------- | ----------------------- | ---------------------------------- |
| `plan-this`           | Parent or mini plan     | Pause; inline only with approval   |
| `task-this`           | Parent or mini task     | Pause; inline only with approval   |
| `finalize-delegation` | Integrated-work closure | Leave `_dispatched`; install skill |

**There is no manual lifecycle fallback.** If `finalize-delegation` is unavailable, the record stays `_dispatched` exactly where it is. Install or load the skill — from the local master, or by re-running `global-sync` — and then run it. Never move, rename, or otherwise close a delegation record by hand: doing so skips the return-and-integration verification and the parent-pointer repair, which is precisely how records get orphaned.

`delegate-this` calls those skills. **They never call it.** `plan-this` and `task-this` carry only a thin `Delegation` pointer field that defaults to `N/A` — no routing logic, no packet schema, no delegation workflow. That one-way boundary is deliberate: adopt `delegate-this` without them and it degrades gracefully; adopt them without it and they never notice.

If you adopt `delegate-this`, adopt `plan-this`, `task-this`, and `finalize-delegation` too.

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
- `references/mode-a-delegation-template.md` — the durable record's shape (execution workspace, child numbering, family tables, checkpoint policy)
- `references/assignment-packet-template.md` — the 21 required packet fields, including reserved child prefix, return report, and Checkpoint Policy
- `references/routing-and-cost-policy.md` — routing factors, cost gate, model policy, provider-neutral Hermes routing

## Adoption Prompt

Give this prompt to your agent:

```text
Read this README and the skill's SKILL.md, then read references/routing-and-cost-policy.md.
Help me adapt the platform list, the standing preference order, and the cost rules to the
coding-agent platforms I actually use. Confirm my workspace has an Archive/ folder before
the first Mode A run. Do not assume the original maintainer's platform set or paths.
```

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only human-readable artifacts while this skill retains content and workflow ownership.
## Deterministic table dependency

Adopt `markdown-table-aligner` with this skill. It supplies the deterministic final padding pass for file-based Markdown tables; the portable rule remains the content and fallback contract.

## Exact model dependency

- Requires `exact-model-confirmation-gate` before the first model-attributed durable-artifact write in each stable session.
