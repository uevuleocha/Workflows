---
name: finalize-brainstorm
description: Finalize an active Brainstorm only after evidence shows shared understanding, a user-approved North Star, complete capture, and explicit dispositions for contradictions and flags. Use when the user explicitly invokes /finalize-brainstorm, $finalize-brainstorm, use finalize-brainstorm, finalize this brainstorm, or a clear equivalent requesting Brainstorm lifecycle closure.
---

# Finalize Brainstorm

Close one exact active Brainstorm through evidence, explicit user acceptance, and a collision-safe `_chivita` to `_fini` lifecycle transition.

This skill is the exclusive finalization owner. It does not conduct the interview, create Brainstorms, invent missing answers, or repair an incomplete capture silently.

## Project Contract

Obey the workspace's canonical contract, permissions, UTF-8 rules, and safety boundaries. Finalization authority applies only to the exact Brainstorm the user asked to close.

## Invocation

Treat these as direct invocation:

- `/finalize-brainstorm`
- `$finalize-brainstorm`
- `use finalize-brainstorm`
- `finalize this brainstorm`
- clear equivalents requesting Brainstorm lifecycle closure

Do not auto-trigger because a discussion sounds complete. The user must request closure.

## Required Pair

This skill pairs with `brainstorm` and uses its deterministic helper:

`../brainstorm/scripts/brainstorm_state.py`

Resolve that sibling path from this skill's installed directory. If `brainstorm` or the helper is missing, stop and report the dependency instead of moving or rewriting the artifact manually.

## Resolve The Exact Chivita Artifact

1. Use an exact path supplied by the user when available.
2. Otherwise use the unique active artifact established by current session context.
3. Otherwise inspect the matching Live Brainstorms Subject.
4. If more than one candidate remains plausible, ask the user to choose.

The target must:

- live under `Archive/Live/Brainstorms/<Subject>/`;
- keep its permanent `N.)` prefix;
- end in `_chivita.md`; and
- contain valid Brainstorm state.

Never guess across collisions or finalize a `_fini.md` artifact again.

## Evidence Gates

Read the entire capture and inspect helper status. Finalization requires:

- a finalized North Star produced at convergence, not at opening;
- the user's confirmation of shared understanding;
- relevant decision-tree branches reviewed;
- every contradiction explicitly disposed;
- every Open Flag resolved, explicitly deferred with an owner, or accepted by the user as non-blocking;
- no flag marked blocking;
- an append-preserving Q&A and decision history;
- a clear next step or handoff; and
- current explicit user acceptance of finalization.

Do not treat a deferred or accepted flag as resolved. Preserve its real status and owner in the Historical artifact.

## Blocked Finalization

If a gate fails:

1. Do not rename, move, or mark the artifact fini.
2. Report the smallest unresolved set.
3. Return interview gaps to `brainstorm`.
4. Leave the artifact `_chivita.md` in Live.

Never invent an answer, silently accept a flag, erase a contradiction, or mark a checklist item complete merely to make finalization pass.

## Finalization Transaction

After every gate passes and the user explicitly accepts closure:

1. Reconfirm the exact source and computed destination.
2. Confirm the matching Historical Subject folder.
3. Confirm the destination does not already exist.
4. Invoke the Brainstorm helper's `finalize` command in Python UTF-8 mode.
5. Supply the user's acceptance as finalization evidence.
6. Let the helper update status, append lifecycle evidence, rename `_chivita.md` to `_fini.md`, and move Live to Historical atomically enough to refuse collisions.
7. Verify the source is absent and exactly one destination exists.
8. Report the permanent number and final absolute path.

The transition is:

`Archive/Live/Brainstorms/<Subject>/N.) <Topic>_chivita.md`

to:

`Archive/Historical/Brainstorms/<Subject>/N.) <Topic>_fini.md`

Subject, Topic, number, Q&A history, prior North Stars, contradictions, flags, and lifecycle evidence remain intact.

## Mode Closure

Successful finalization ends Brainstorming mode for that completed cycle. Other explicitly active modes remain active and retain their own footer entries.

If finalization is blocked, Brainstorming mode remains active unless the user explicitly exits it.

## Later Breakthroughs

Do not reopen from this skill. A later breakthrough invokes `brainstorm`, which owns reopening the same `_fini` artifact as `_chivita`, preserving its number and prior history.

## Boundaries

Do:

- resolve one exact artifact;
- verify every gate from current evidence;
- require explicit user acceptance;
- preserve the full history;
- refuse collisions; and
- report the final path.

Do not:

- create a Brainstorm;
- continue the interview;
- set or rewrite the North Star;
- close unresolved blockers;
- overwrite Historical content; or
- globally synchronize skills.

## Agent Provenance For Durable Artifacts

Finalization never replaces the original creator. Preserve the artifact's `## Agent Provenance` section exactly, including its immutable `Original writing agent` and `Original writing LLM` rows, then append a new entry to its `## Agent Change Log` naming the truthful acting agent, that agent's model, the lifecycle action, and the status/path or content scope changed. The change log is a five-column `Date and Time | Agent | Model | Action | Scope` table; stamp the new row `YYYY-MM-DD-HH:mm:ss` from the machine clock and never estimate it. Leave historical date-only rows exactly as written.

Preserve `## Agent Provenance` immediately after the artifact's opening block -- its title, status, and lifecycle lines -- and keep `## Agent Change Log` as the last section, or immediately above any section the artifact reserves for the last position.

Preserve the artifact's `## Feedback Section` exactly as found, **including an empty one**. Never prune a Feedback Section for carrying no entries, never renumber or rewrite an existing `### Feedback N` subsection, and never author a reply on another agent's behalf. It is an append-only cross-agent record, and finalization is not a reason to tidy it.

**Publication steps are never a closure gate.** A wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump must never block, defer, or fail finalization, and this skill never performs one itself. Those operations belong after the artifact reaches its final path -- finalization renames and moves the file, so syncing first leaves the wiki holding a synthesised copy of a path that no longer exists and dirties the repository again immediately. Where such an item appears in a DEFINITION OF DONE or Verification Checklist, report it, recommend a waiver, and close.

**An unticked box means not done.** Read a blank checkbox as incomplete, never as "done but awaiting confirmation." Do not supply the executing agent's ticks to make an artifact look finished. Where a box is unticked but its evidence is plainly present, report the discrepancy to the user rather than silently resolving it in either direction. Where an invented sync constraint is contradicted by the user's own authorization, report it and recommend a waiver rather than treating it as failure.

When same-stem Markdown, HTML, or PDF siblings exist, apply the same provenance history to the complete artifact set. If a legacy artifact lacks reliable creator evidence, record `Original writing agent: Not recorded` rather than guessing, and log the current finalizer's work. Do not add embedded provenance to product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill still owns every completion-evidence and closure gate. Before finalizing, discover same-stem `.md`, `.html`, and `.pdf` siblings and treat them as one Brainstorm artifact set. Preflight every destination, apply the authorized completed content/status through the applicable format skill, rename the lifecycle suffix on every sibling, and move the complete set together.

An HTML-only or PDF-only Brainstorm remains in that format; do not manufacture Markdown. Stop rather than finalize only part of a sibling set. Extension-only search and validation examples become format-neutral for this run.

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

As a finalizer, read an unticked box as **not done**. Never treat a blank box as "done, the executor was being cautious," and never supply the executor's ticks to make an artifact look complete. Where a box is unticked but its evidence is plainly present, report the discrepancy to the user rather than silently resolving it in either direction.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Non-Blocking Wiki And Git Items

**Non-Blocking Wiki And Git Items.** Do not write a wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, or FAILURE condition as a completion criterion. Those operations belong **after** the artifact is finalized: finalization renames and moves the artifact, so syncing first dirties the repository again and leaves the wiki holding a synthesised copy of a path that no longer exists. If such an operation is genuinely worth recording, record it as an explicitly non-blocking follow-up — "after finalization, run `stage-commit-push`" — never as a box whose blank state blocks closure. A finalizer must never refuse or defer closure because a sync, push, or pointer bump has not happened.

**The carve-out.** This does not apply to an artifact **whose subject is** the wiki or Git work. A plan to build `wiki-sync` legitimately carries wiki items in its DEFINITION OF DONE, because there the wiki work *is* the deliverable rather than a publication step for it. The rule targets publication steps, not subject matter. Never strip a legitimate item from an artifact that is correct as written.

Like rule 2, this binds the authoring agent and is never emitted as artifact text.

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

- confirm the `## Checklist Tick Discipline` section is present and its rule text is unmodified;
- confirm the `## No Invented Sync Constraints` section is present, and that a produced artifact contains **no** invented sync constraint in its DEFINITION OF DONE, Verification Checklist, CONSTRAINTS, or FAILURE sections;
- confirm the `## Non-Blocking Wiki And Git Items` section is present with its carve-out, and that a produced artifact contains **no** wiki-sync, push, `stage-commit-push`, or pointer-bump completion criterion;

After creating or updating this skill:

- run the paired Brainstorm lifecycle fixtures in Python UTF-8 mode;
- validate this folder with `quick_validate.py`;
- confirm missing evidence blocks closure;
- confirm a destination collision blocks closure;
- confirm successful closure produces one `_fini.md` artifact;
- confirm permanent identity and history survive finalization and reopen; and
- validate every synchronized copy with recursive byte parity.
