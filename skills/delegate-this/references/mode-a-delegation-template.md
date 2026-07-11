# Mode A Delegation Record Template

The durable record created when work is dispatched to external coding-agent platforms.

**Path (dispatched):**

```text
<Workspace>\Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md
```

**Path (after `finalize-delegation`):**

```text
<Workspace>\Archive\Historical\Delegations\<Subject>\N.) <Topic>_completed.md
```

Subject folders are never numbered.

`N` is **lifecycle-agnostic and permanent**: calculate it as one greater than the highest numeric prefix found across **both** the Live and Historical Delegations folders for that Subject. Checking only Live will silently reuse a number already held by a completed record. Assign `N` once — never reclaim gaps, never renumber during finalization, never change it on reopen.

Only `finalize-delegation` performs the rename and move. There is no manual fallback.

The record's **content is immutable after dispatch**. Its **state is not** — that is what the suffix tracks. Do not routinely rewrite packets after dispatch; actual model choices and results belong in handoffs, session summaries, or the parent artifact.

---

## Record

```markdown
# <Topic> — Delegation

Status: DISPATCHED 🚀 — dispatched <YYYY-MM-DD>.
Delegation lifecycle: DISPATCHED on <YYYY-MM-DD>. <One sentence: what was delegated and why.>

## Objective

<What the whole delegation is trying to achieve. The parent objective, restated once,
in terms every receiving agent can act against.>

## Parent Artifacts

| Kind        | Path                                              | Status    |
|-------------|---------------------------------------------------|-----------|
| Parent plan | `<absolute path>` or `N/A`                        | <status>  |
| Parent task | `<absolute path>` or `N/A`                        | <status>  |

At least one parent is mandatory. Each parent's `Delegation` field must name this record.

## Mini Artifacts

| Owner platform | Kind | Path                                    | Created by     |
|----------------|------|-----------------------------------------|----------------|
| <platform>     | Plan | `<path>` or `To be created after recon` | <orchestrator> |

## Shared Context

<Everything every receiving agent needs: the system's shape, the decisions already
locked, the vocabulary, the state of play. Written once here so no packet has to
repeat it.>

## Global Constraints

- Obey each host workspace's canonical contract. Delegation grants no extra authority.
- One editor per file, enforced by the Owned surfaces in each packet.
- Paid API use: <`Not authorized for this run` / `Authorized: <model>, for <packet(s)>`>
- Forbidden platforms / providers / models: <list, or `None`>
- <Any objective-wide constraint>

## Dependencies and Execution Waves

<Prose explaining what blocks what, and why the waves are ordered this way. Say
explicitly which assignments are parallel-safe and which are strictly serial.>

- **Wave 1** — <assignments>. <Parallel or serial, and why.>
- **Wave 2** — <assignments>. Blocked on: <wave 1 deliverable>.
- **Wave 3** — <assignments>.

## Assignment Overview

| Wave | Platform    | Role     | Assignment        | Rec. model | Actual model   | Parent   | Mini     | Depends on | Status     |
|------|-------------|----------|-------------------|------------|----------------|----------|----------|------------|------------|
| 1    | Claude Code | Worker   | <short>           | <model>    | User to select | `<path>` | `<path>` | None       | Dispatched |
| 2    | Codex       | Reviewer | <short>           | <model>    | User to select | `<path>` | N/A      | Wave 1     | Dispatched |

Cells are capped at 80 characters and the pipes are aligned. Where a cell would
overflow, truncate at a word boundary and add `→ see note <wave>` with the full text
directly beneath the table.

## Assignment Packets

<One packet per platform/agent, using `assignment-packet-template.md`. A receiving agent
may read the whole record, but executes only its own packet.>

## Launch Instructions

1. Open <platform> and start a session in `<workspace>`.
2. Give it this file and say: *"Read this delegation record in full, then execute only
   Packet <N>, addressed to <platform> as <role>."*
3. Select the model. The agent may counter-recommend once; you decide.
4. <Repeat per wave, in order. Do not launch a Wave 2 agent before its Wave 1
   prerequisite has returned.>

## Return and Integration Instructions

- Each agent returns its deliverable in the format its packet specifies.
- Bring every return back to the orchestrator session.
- The orchestrator reconciles returns against the parent objective, every mini artifact,
  the global constraints, and the parent's Definition of Done.
- If two agents return conflicting solutions, the orchestrator does not silently pick one.
  It surfaces the conflict, compares evidence and tradeoffs, and resolves through the user
  or an explicit integrator decision.
- **Dispatch is not completion.** The parent objective is complete only after integration
  and verification.
- When integration is verified, run `finalize-delegation` to move this record to
  `Archive\Historical\Delegations\<Subject>\` as `_completed`.

## Global Stop Conditions

Any agent stops and returns to the user immediately if:

- It would need to write outside its owned surfaces.
- A prerequisite deliverable is missing, malformed, or contradicts its packet.
- Work requires a paid API call not authorized in Global Constraints.
- Its packet conflicts with the parent artifact or this record's shared context.
- <Objective-specific tripwire>
```

---

## Parent Backlink Field

Every parent plan/task must name this record. In a `delegate-this`-aware `imp-upd-plan` or `imp-upd-task`, fill the existing field. In an older parent that predates the field, add it under `## Context`:

```markdown
**Delegation:** `<Workspace>\Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md`
```

When no delegation exists, that field reads:

```markdown
**Delegation:** N/A
```

Prompt the user before editing a parent file they did not ask you to touch.
