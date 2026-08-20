# Canonical Prompt Template

The one shape every `prompt-this` artifact takes. **Reuse it; do not reconstruct the headings from memory.** The whole point of the fixed structure is that a reader can identify a `prompt-this` file on sight, without ambiguity.

**Path:**

```text
Pending:   <Workspace>\Archive\Live\Prompts\<Subject>\N.) <Topic>_pending.md
Executed:  <Workspace>\Archive\Historical\Prompts\<Subject>\N.) <Topic>_executed.md
```

Subject folders are never numbered. Before writing, capture `previous_max` — the highest numeric prefix across **both** the Live and Historical Subject folders (`0` if neither has one) — and assign `N = previous_max + 1`. Validate against that **captured** value, never against a maximum recomputed after the write, because the new file is itself part of the union by then. `N` is assigned once and preserved through finalization and reopen.

The filename Topic is Title Case with spaces and **must not contain the word "prompt"** — unless the user explicitly opts in to share that prompt publicly. Only the lifecycle suffix (`_pending`, `_executed`) uses an underscore.

Only `finalize-prompt` moves a prompt Live → Historical and renames the suffix `_pending` → `_executed`. There is no manual fallback.

---

## The template

```markdown
# <Title>

Status: PENDING ⌛ — created <YYYY-MM-DD>.
Prompt lifecycle: PENDING on <YYYY-MM-DD>. <One sentence on what this prompt asks for.>

## What This Prompt Is

<One paragraph. What this prompt asks an agent to do, and when to run it. Written so a
fresh agent, opening this file cold, understands the job before reading the payload.>

## Prompt

<The actual prompt text — the verbatim instruction handed to the consuming agent.
This is the payload. Everything else in this file exists to serve it.>

## Context

**Parent Plan:** N/A
**Parent Task:** N/A
**Delegation:** N/A

## Instructions

<Usage notes for the consuming agent: preconditions, required inputs, safety rules,
how to run it, and what "done" looks like operationally. This is *how to use* the
payload — not the payload itself, and not the success criteria.>

## Prompt Contract

<The 5-part contract authored via `prompt-contracts`, embedded verbatim:
GOAL / CONSTRAINTS / FORMAT / DEFINITION OF DONE / FAILURE.

Compact prompts may use the minimal form: GOAL + DEFINITION OF DONE + FAILURE.

Because it is embedded here, the consuming agent already has the scope, the
done-criteria, and the failure conditions the moment it opens this file.>

## Verification Checklist

- [ ] The consuming agent verified every required deliverable.
- [ ] Every in-pass Prompt Contract DEFINITION OF DONE item is satisfied.
- [ ] No FAILURE condition remains active.
- [ ] Relevant tests, validators, inspections, or manual checks are recorded.

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

## Deferred Real-World Verification

<Optional. Include only for checks that genuinely require later live use, elapsed time,
user adoption, or an external event. Every item states its future trigger and required
evidence. Unticked items here never block finalization.>

## Notes

<Optional. Provenance, related prompts, reopen history.>

## Feedback Section

<Always present, empty by default. Any agent appends a numbered subsection:
`### Feedback N - YYYY-MM-DD - Agent - short descriptor`. Append-only; a
correction is a new entry, never an edit to an earlier one. Never prune this
section for being empty.>
## Agent Change Log

| Date and Time       | Agent        | Model         | Action  | Scope   |
|---------------------|--------------|---------------|---------|---------|
| YYYY-MM-DD-HH:mm:ss | <agent>      | <model>       | Created | <scope> |```

---

## Field rules

**`## Context` — all three fields, always.** Keep `Parent Plan`, `Parent Task`, and `Delegation` present even when empty; write `N/A`. Never delete a field. A prompt does not require a parent of any kind.

**`**Delegation:**` is a pointer and nothing more.** If the prompt belongs to a formal delegation, `delegate-this` or the orchestrator fills it. No routing rule, assignment-packet field, platform name, or subagent instruction ever enters a prompt file.

**Four sections, four distinct jobs.** Do not collapse them:

| Section                     | Answers                             |
|-----------------------------|-------------------------------------|
| `## Prompt`                 | What do I run?                      |
| `## Instructions`           | How do I run it?                    |
| `## Prompt Contract`        | What does success and failure mean? |
| `## Verification Checklist` | How was success actually evidenced? |

The contract **defines** success; the checklist **records** it. One never substitutes for the other.

**No `Estimated Effort` table.** Plans and tasks mandate one. Prompts do not — the contract and checklist carry the execution controls without turning every prompt into a plan.

---

## Compact prompts

A compact prompt uses the same path, the same `N.)` numbering, and the same lifecycle. It may:

- use the minimal Prompt Contract (GOAL + DEFINITION OF DONE + FAILURE), and
- omit `## Notes`.

That is all. **`## Notes` is the only core section a compact prompt may drop.** The optional `## Deferred Real-World Verification` section is added only when genuine later-use evidence exists. Recognizability and lifecycle pointers do not disappear merely because the payload is short.

---

## On finalization

`finalize-prompt` rewrites the header to:

```markdown
Status: EXECUTED ✅ — created <YYYY-MM-DD>, finalized <YYYY-MM-DD>.
Prompt lifecycle: EXECUTED on <YYYY-MM-DD>. <Past-tense summary.>
```

promotes `## Prompt Contract` to `## Prompt Contract ✅ Complete` once every in-pass DEFINITION OF DONE item is met, preserves any unticked `## Deferred Real-World Verification` items as explicitly non-blocking follow-up evidence, adds a dated note under `## Notes`, and moves the file to the Historical Subject folder with `N.)` and the Topic unchanged, renaming only the suffix `_pending` → `_executed`.

The `## Prompt` payload itself is **never rewritten**. It is the historical record of what was asked.
