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

## Execution Workspace

The delegation family is created inside a single execution workspace, resolved
before any parent, delegation, mini, or return report is written. State it once
here; every path in this record is resolved relative to it.

```text
Execution workspace: <absolute path to the workspace root holding Archive\>
```

Create the parent plan/task, the delegation record, every mini artifact, and the
session-summary / return-report family **all under this workspace** from the
start.

---

## Child Numbering

The families use lowercase child numbering, with **separate linked anchors** per
artifact-type namespace:

- each family master / independent mini: `N.)`
- child mini artifacts and return reports: `Na.)`, `Nb.)` … `Nz.)`, then
  `Naa.)`, `Nab.)` …

**Separate anchors (do not share one number across namespaces):**

- **Plan/Task family** — master `N` from the Plan/Task Subject namespace; child
  plans/tasks inherit it. Canonical: `1.)`, children `1a.)` … `1e.)`.
- **Delegation record** — own `N` from the Delegation Subject namespace.
  Canonical: `1.)` (independent of the Plan number).
- **Summary family** — master `N` from the Summary Subject namespace; return
  reports inherit it. Canonical: `9.)`, reports `9a.)` … `9e.)`.

Each anchor is calculated across its own combined Live + Historical namespace.
Explicit paths and pointers connect the families; their numeric anchors need not
match.

The orchestrator reserves every child prefix before dispatch and writes the
exact reserved prefix into the assignment overview, the mini-artifact table, the
return-report table, and each packet. Never leave a child prefix blank or vague.

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

| Owner platform | Prefix  | Kind | Path                                       | Created by     |
|----------------|---------|------|--------------------------------------------|----------------|
| <platform>     | `Na.)`  | Plan | `<path>` or `(reserved, created after recon)` | <orchestrator> |

The prefix column carries the **exact reserved child prefix** (`1a.)`, `1b.)`,
…) from the **Plan/Task family**. Every prefix is reserved by the orchestrator
before dispatch; children inherit the Plan/Task family master `N`.

## Session-Summary / Return-Report Family

Uses the **Summary family** master `N` (from the Summary Subject namespace), not
the Plan/Task or Delegation number.

| Kind               | Prefix  | Path                                                          |
|--------------------|---------|---------------------------------------------------------------|
| Orchestrator summary | `9.)` | `<workspace>\Archive\Historical\Summaries\<Subject>\9.) <Topic>.md` |
| Return report (a)  | `9a.)`  | `...\9a.) <platform>_<packet>_Report.md`                      |
| Return report (b)  | `9b.)`  | `...\9b.) <platform>_<packet>_Report.md`                      |

Return-report filenames **end in `Report.md`** and carry the reserved child
prefix from the Summary family. Each is created (under the execution workspace's
`Archive\Historical\Summaries\<Subject>\`) when its assignment returns. A return
report uses session-summary structure plus an append-only `## Feedback` ledger.

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

| Wave | Platform    | Role     | Assignment        | Rec. model | Actual model   | Parent   | Mini     | Prefix  | Return report    | Depends on | Status     |
|------|-------------|----------|-------------------|------------|----------------|----------|----------|---------|------------------|------------|------------|
| 1    | Claude Code | Worker   | <short>           | <model>    | User to select | `<path>` | `<path>` | `1a.)`  | `9a.) …Report.md` | None       | Dispatched |
| 2    | Codex       | Reviewer | <short>           | <model>    | User to select | `<path>` | N/A      | N/A     | `9b.) …Report.md` | Wave 1     | Dispatched |

Cells are capped at 80 characters and the pipes are aligned. Where a cell would
overflow, truncate at a word boundary and add `→ see note <wave>` with the full text
directly beneath the table. `Prefix` carries the exact reserved **Plan/Task
family** child prefix (or `N/A` when the assignment creates no mini artifact);
`Return report` is the reserved path ending in `Report.md`, carrying the
**Summary family** child prefix. The two prefixes come from different families
and need not match.

## Assignment Packets

<One packet per platform/agent, using `assignment-packet-template.md`. Each
packet carries all 21 required fields, including the Checkpoint Policy and the
reserved return-report prefix. A receiving agent may read the whole record, but
executes only its own packet.>

## Checkpoint Policy (per packet)

Each packet states explicitly:

- where execution stops (default: complete the packet continuously; only
  `USER CHECKPOINT` midpoints pause for the user);
- whether sync is allowed (default for skill work: centralized sync — workers
  do not sync, the orchestrator does one final global-sync + parity pass);
- what deliverables must be returned first (the return report and named
  deliverables).

## Launch Instructions

1. Open <platform> and start a session in `<workspace>`.
2. Give it this file and say: *"Read this delegation record in full, then execute only
   Packet <N>, addressed to <platform> as <role>."*
3. Select the model. The agent may counter-recommend once; you decide.
4. <Repeat per wave, in order. Do not launch a Wave 2 agent before its Wave 1
   prerequisite has returned.>

## Return and Integration Instructions

- Each agent returns its deliverable in the format its packet specifies **and**
  writes a **return report** at its reserved child prefix under
  `<workspace>\Archive\Historical\Summaries\<Subject>\` with a filename ending
  in `Report.md`. The return report is mandatory at packet/wave completion.
- A return report uses session-summary structure plus an append-only
  `## Feedback` ledger. Existing report content and earlier feedback entries are
  immutable; feedback is appendable only while the delegation is active and
  freezes when `finalize-delegation` closes it.
- Bring every return back to the orchestrator session.
- The orchestrator reconciles returns against the parent objective, every mini artifact,
  the global constraints, and the parent's Definition of Done.
- If two agents return conflicting solutions, the orchestrator does not silently pick one.
  It surfaces the conflict, compares evidence and tradeoffs, and resolves through the user
  or an explicit integrator decision.
- **Dispatch is not completion.** The parent objective is complete only after integration
  and verification.
- When integration is verified, run `finalize-delegation` to move this record to
  `Archive\Historical\Delegations\<Subject>\` as `_completed`. Closing the
  delegation freezes every return report and its `## Feedback` ledger.

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

Every parent plan/task must name this record. In a `delegate-this`-aware `plan-this` or `task-this`, fill the existing field. In an older parent that predates the field, add it under `## Context`:

```markdown
**Delegation:** `<Workspace>\Archive\Live\Delegations\<Subject>\N.) <Topic>_dispatched.md`
```

When no delegation exists, that field reads:

```markdown
**Delegation:** N/A
```

Prompt the user before editing a parent file they did not ask you to touch.
