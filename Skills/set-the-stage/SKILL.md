---
name: set-the-stage
description: Review the current work, discussion, user-pointed targets, or relevant durable artifacts and tell the user exactly what remains to reach the goal or finish verification, with one focused section per subject. Use when the user invokes /set-the-stage, $set-the-stage, set=the=stage, use set-the-stage, asks to set the stage, or requests a context-aware briefing on what is left to do. Durable artifacts may supply context but are never required.
---

# Set The Stage

Tell the user where each current subject stands and what is still needed to finish it. Use the evidence already available; do not turn the briefing into a new plan, durable artifact, or implementation pass.

## Relationship to workspace-setup

`workspace-setup` uses this skill to present setup and parity findings to the user before executing any workspace changes. When `workspace-setup` invokes this skill, treat the inspection results as the subjects to brief on — but `set-the-stage` remains read-only and owns only the briefing shape, never the audit or execution.

## Project Contract

Obey the active workspace contract, permissions, safety rules, and current mode. This skill is read-only by default and does not broaden authority.

## Invocation

Treat these as direct invocation:

- `/set-the-stage`
- `$set-the-stage`
- `set=the=stage`
- `use set-the-stage`
- `use the set-the-stage skill`
- `set the stage`
- clear equivalents asking for a context-aware account of what remains

If the current subject is evident, proceed without asking the user to restate it. If several subjects are active, cover each one separately.

## Resolve The Subjects

Determine the briefing scope in this order:

1. subjects or targets the user explicitly names;
2. material the user points at in the current request;
3. durable artifacts already active in the conversation;
4. work being implemented, verified, discussed, or handed off in the current context.

Group closely related material under one clear subject name. Keep genuinely independent goals separate. Do not force every file, phase, or artifact into its own section when they belong to the same outcome.

Ask one short scope question only when multiple plausible interpretations would produce materially different briefings and the context cannot resolve them. A lack of a durable artifact is never a reason to ask or stop.

## Review The Current State

For each subject, review only the context needed to answer what remains:

- the stated goal, requested outcome, or apparent finish line;
- completed work supported by conversation, files, artifacts, tests, or user confirmation;
- incomplete implementation, decisions, dependencies, or handoffs;
- required verification that has not yet produced evidence;
- blockers, risks, or unknowns that prevent a completion claim; and
- the most direct next action.

Read a relevant durable artifact when the user points to it or it is already the authoritative context. When a durable artifact is authoritative for a subject, read that subject's section in full before briefing it; do not brief from recollection or a partial excerpt. This full-read requirement is limited to the authoritative subject section and does not authorize reading unrelated sections or searching the wider repository. Otherwise use the conversation and current work.

Do not search broadly for more work merely to make the briefing longer.

## Decide What Is Left

Use evidence, not optimism or checklist appearance.

- Treat a completed action as done only when the available context supports it.
- Keep implementation work distinct from verification work.
- Identify dependencies between remaining items. If one item cannot begin until another item or condition is complete, state that blocking relationship in words; list order alone is not an adequate dependency signal.
- Identify a decision as remaining only when it genuinely blocks or changes the outcome.
- Phrase items that wait on the user explicitly, for example `awaiting your decision on X` or `awaiting your input on Y`, so the briefing always shows what is left for the user.
- Label an uncertain item as unknown instead of inventing status.
- If the goal is already met, say that nothing substantive remains and name any final confirmation or deliberate lifecycle close that is still needed.
- If the finish line itself is unclear, state the smallest missing definition needed to establish it.

Do not silently expand the original goal, prescribe optional polish as mandatory, or repeat already completed work as pending.

## Output

Create exactly one section for each resolved subject. One subject gets one section; several subjects get one section each. Every section must emit all six fields below — never omit a field. Field order is fixed as shown and the labels are verbatim; do not paraphrase, rename, or restructure them. When a field has no content, write the placeholder instead of dropping the line: `None identified` for **Dependencies:**, **Verification still needed:**, **Blockers or unknowns:**, and **Best next move:**; `Nothing substantive remains for this subject.` for **What is left:**. Use this compact shape:

```markdown
## [Subject]

**Current position:** [brief evidence-based status]

**What is left:**

1. [remaining action, decision, or dependency]
2. [next remaining item]

**Dependencies:** [state each blocking relationship in words, or `None identified`]

**Verification still needed:**

- [unproven check or acceptance evidence]

**Blockers or unknowns:** [items, or `None identified`]

**Best next move:** [single most direct next action]
```

When nothing remains, replace the numbered list with:

```text
Nothing substantive remains for this subject.
```

Lead with the useful status, keep the wording concrete, and order remaining items by dependency and practical execution sequence. Ordering supports the briefing but does not replace the explicit **Dependencies:** field. Do not add an aggregate summary that merely repeats the subject sections.

## Durable Artifact Boundary

Durable artifacts are optional evidence sources, not a dependency or output. Running this skill does not:

- create, update, rename, move, finalize, or reopen a durable artifact;
- add a backlink, status marker, or reference inside an artifact;
- require the current work to have been documented durably; or
- replace the lifecycle skill that owns an artifact.

If a durable artifact is authoritative, report what its goal, checklist, and evidence say remains. Leave all artifact changes to its owning workflow.

## Boundaries

Do:

- infer the subject and finish line from available context when reasonable;
- distinguish remaining work, verification, blockers, and unknowns;
- use one section per logical subject; and
- give the user a clear next move.

Do not:

- edit files, execute the remaining work, or mark anything complete;
- create a plan, task, report, prompt, summary, or other durable artifact;
- audit unrelated workspace areas;
- duplicate an entire artifact or conversation in the response; or
- claim completion without evidence.

If the user also asks to perform the remaining work, finish this briefing first and then continue through the appropriate authorized workflow.

## Validation

When creating or updating this skill:

- validate the folder-style skill with `quick_validate.py` in Python UTF-8 mode (`-X utf8`);
- confirm a single-subject request produces exactly one subject section;
- confirm a multi-subject request produces one section per subject;
- confirm chat-only context works without a durable artifact;
- confirm a blocked item explicitly states in words which item or condition blocks it instead of relying on list order;
- confirm every subject section emits all six fields in the fixed order with verbatim labels, using `None identified` or `Nothing substantive remains for this subject.` as placeholders instead of omitting any field;
- confirm items awaiting the user's decision or input are phrased explicitly as such;
- confirm an authoritative artifact-backed subject is briefed only after its subject section has been read in full, without widening into unrelated sections or broad repository searching; and
- confirm artifact-backed context remains read-only and creates no linkage.
