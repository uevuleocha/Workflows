---
name: verify-this
description: "Confirm that work done by an implementation agent actually met its goals and definitions of done — read the contract, diff the implementation, and write a new feedback subsection into the durable artifact so the orchestrator is never blocked waiting. Use when the user explicitly invokes /verify-this, use verify-this, asks to verify the work, asks to check that goals/DoD were met, asks to confirm an implementation agent did the work well, or hands the orchestrator back to verify a prompt/plan/task that another agent implemented. Anti-over-sabi by design — report unmet goals and blatant defects, never hunt edge cases or nitpick."
---

# Verify This

Confirm that work done by an implementation agent actually met its goals and Definitions of Done. This is a **confirmation** workflow, not an audit. The default posture is "did the implementation do what we asked, well?" — not "what can I find wrong?"

The defining property of this skill is its **anti-over-sabi discipline** (see below). Verification is fast, goal-focused, and returns the orchestrator to work without making them wait.

## The Anti-Over-Sabi Discipline (Governing Frame)

"Over-sabi" is Nigerian slang for doing more than was asked — over-engineering, manufacturing edge cases, inventing hypothetical failure modes, or grading style. Agents tend to drift into this when told to "verify" because finding issues *looks* diligent. **It is not diligence here. It is scope creep.**

This skill is governed by the opposite discipline:

- **Verify against the stated goals, DoD, and contract only.** If the work met the goals and Definitions of Done, it **passes**. Do not invent additional criteria.
- **Report only three things as findings:**
  1. **Unmet goals or DoD** — a stated requirement that was not satisfied.
  2. **Blatant defects** — something that breaks the work, undermines it, or will fail in normal use. Not hypothetical, not edge-case: actually broken.
  3. **Anything the user or contract explicitly asked you to check.**
- **Never hunt edge cases, nitpick style, or propose optional improvements.** A speculative issue is not a finding; it is over-sabi. Style, naming, formatting, or aesthetic preferences are never findings unless a goal or DoD explicitly governs them.
- **When in doubt, do not report it as a finding.** Note genuine uncertainty plainly (e.g. "I could not confirm X because Y"), but do not escalate it to a defect.
- **Diligence is welcome; scope expansion is not.** Checking whether the implementation actually works as the goals describe is diligence. Searching for problems the goals never asked about is scope expansion. The line is the contract.

This frame is the reason this skill exists separately from `inspect` (which audits) and `subagent-verification-loops` (which runs a heavy independent review). Keep it pure.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and product-code workflow defined there apply unchanged.

This skill's unique authority is the **feedback writeback** — appending a new dated subsection to a durable artifact's feedback section. That is a bounded mutating action this skill is explicitly authorized to perform when the user invoked verification. It does not broaden authority to edit the artifact's goals, contract, plan, task, or any non-feedback content. Appending the matching row to the artifact's `## Agent Change Log` is part of the writeback, not a broadening of it: the feedback subsection is a material change to a durable artifact and the workspace contract requires every material change to be recorded in the artifact's own append-only change log. The writeback still never touches the artifact's goals, contract, plan, task, `## Agent Provenance`, or any existing change-log row.

## Invocation

Treat these as direct invocation and begin the verification workflow:

- `/verify-this`
- `use verify-this`
- `use the verify-this skill`
- `verify the work`
- `verify what [Agent B / the implementation agent] did`
- `confirm the goals were met`
- `confirm the definitions of done were met`
- `check that [implementation] met [contract/DoD/North Star]`
- clear equivalents asking to confirm that implemented work met its goals

## Relationship To Sibling Skills

| Skill                         | Posture               | Weight        | When                            |
| ----------------------------- | --------------------- | ------------- | ------------------------------- |
| `verify-this` (this skill)    | Confirm goals/DoD     | Light, 1 pass | "Did Agent B do what we asked?" |
| `inspect`                     | Read-only audit       | Light, 1 pass | "Audit target for defects"      |
| `subagent-verification-loops` | Indep. review+resolve | Heavy, 1-2 rd | "Deep indep. review + fixes"    |

Full posture and when text:

- `verify-this`: confirm goals/DoD met; anti-over-sabi; writes feedback by default. When: "Did the implementation agent actually do what we asked?"
- `inspect`: read-only; Mode B audits for issues/quality. When: "Read/understand/audit this target for defects."
- `subagent-verification-loops`: independent reviewer+resolver, issue-finding. When: "I want a genuinely independent deep review with proposed corrections."

This skill does **not** require `inspect` or `subagent-verification-loops` to be loaded. They are complementary, not coupled. If the user wants a deeper audit, point them to `inspect` Mode B; if they want independent multi-agent review with proposed fixes, point them to `subagent-verification-loops`.

## Required Inputs

Identify, in order of precedence:

1. **The verification target** — the implemented work to confirm. A file, a folder, a code batch, a diff, a built artifact, or a named scope the user points at.
2. **The goals / contract / DoD** — what "done" was defined to mean. Sources, in priority order:
   - an embedded **Prompt Contract** (GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, FAILURE);
   - a **Verification Checklist** in the artifact;
   - a plan's, task's, report's, or North Star's stated goals and Definitions of Done;
   - explicit user-stated criteria in the current request.
3. **The feedback-writeback target** — the durable artifact that will receive the new dated feedback subsection (see No-Don't-Make-Me-Wait below).
4. **Context** — any plan, task, prompt, or conversation framing needed to understand the implementation intent.

Ask only for what is genuinely missing. If the target and contract are already clear from context, do not interrogate the user.

## Verification Workflow

### 1. Load the contract

Read the artifact that defines the goals, DoD, and (if present) the Prompt Contract and Verification Checklist. Extract the explicit criteria. If multiple sources exist, the Prompt Contract's DEFINITION OF DONE is authoritative; the Verification Checklist records how it was evidenced.

Do not invent criteria the contract does not state. The contract is the only source of truth for "done."

### 2. Read the implementation

Diff or read the verification target against the contract's intent. Focus on:

- Are the goals satisfied as described?
- Is each Definition of Done item met with real evidence (not just a claim)?
- Does the implementation actually do what the contract says it should do?
- Are there blatant defects that break or undermine the work in normal use?

Read only what the contract requires. Do not audit beyond scope.

### 3. Classify the result

Produce a verdict:

- **PASS** — goals and DoD met; no blatant defects.
- **CHANGES NEEDED** — one or more goals or DoD items unmet, or a blatant defect found. This is the iteration trigger.
- **BLOCKED** — verification could not complete (e.g. target missing, contract unreadable, evidence unavailable). State exactly what is missing.

Do not invent a fourth verdict. Do not use "PASS with notes" to smuggle in nitpicks — if the only things to say are optional improvements, the verdict is PASS and those go unsaid.

### 4. Write the feedback subsection (No-Don't-Make-Me-Wait — by default)

**This is the core differentiator.** The moment verification is done, write the result back to the durable artifact so the orchestrator is never blocked waiting for a chat reply.

#### Writeback target resolution

Resolve the writeback target in this order:

1. **Explicit user-named artifact** — if the user said "write the feedback to [X]," use X.
2. **The artifact used to verify** — if the user did not name one, write to the durable artifact that supplied the goals/contract/DoD (the prompt, plan, task, or North Star in context).
3. **Fallback: pause and ask.** If there is no durable artifact in context and the user gave no explicit target, pause and offer the user three options:
   - (a) name a durable artifact to write the feedback into;
   - (b) have the agent create a lightweight verification artifact (only with user approval); or
   - (c) deliver the feedback in-chat ("in-house") only, no file written.

Do not guess. Do not create a new artifact without approval. The fallback exists precisely so the orchestrator is never silently blocked.

#### Where in the artifact

Append a **new dated subsection** under the artifact's existing `## Feedback Section` (create the section if the artifact has none). Use this shape:

```markdown
## Feedback Section

### Feedback N — [YYYY-MM-DD] — [Verifying Agent Family] Agent — Verification

**Verification target:** [file/folder/scope verified]
**Goals/DoD source:** [Prompt Contract / Verification Checklist / plan / task / North Star]
**Verdict:** PASS ✅ | CHANGES NEEDED ⚠️ | BLOCKED 🚫

[For PASS] Goals and Definitions of Done met. No blatant defects found.
The implementation is sound and ready for finalization.

[For CHANGES NEEDED] Goals/DoD not fully met. Required changes:
- [unmet goal or DoD item, with specific location]
- [blatant defect, with specific location and why it breaks normal use]

[For BLOCKED] Verification could not complete:
- [exactly what is missing and why it blocks confirmation]

[Optional — genuine uncertainty only] Unable to confirm: [item], because [reason].
```

**`N` is the next free number in that artifact's Feedback Section**, continuing the existing sequence — read the last `### Feedback N` heading and add one. Start at 1 when the section is empty. Never renumber earlier entries, never reuse a number, and never edit an existing subsection; a correction is a new entry. This grammar is shared by every artifact-authoring skill in the workspace, so a verification entry sits in the same numbered sequence as an implementer's entry and the exchange reads in order.

When the target is a North Star, do **not** hand-write the subsection. Its Feedback Section is helper-owned state and a hand-written entry is discarded on the next mutation; append through `north_star_state.py feedback-add` instead, which numbers the entry for you.

**Change-log row.** The writeback is a material change: in the same pass, append one row to the artifact's `## Agent Change Log` — five columns `Date and Time | Agent | Model | Action | Scope`, timestamp read from the machine clock at write time in `YYYY-MM-DD-HH:mm:ss`, never estimated. If the artifact carries no change log at all, note that absence in the feedback subsection as a genuine uncertainty rather than fabricating the section. Where the artifact's owning helper manages its change log through encoded state, append through that helper's own command instead of hand-editing; the North Star rule above is one instance of this.

Use the agent-family label truthfully (`Codex Agent`, `Claude Agent`, `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`). If a sub-agent the orchestrator spawned performed the verification, credit that sub-agent's family in the heading, not the orchestrator's.

#### Verdict markers (use exactly)

| Verdict           | Marker              | When                                        |
| ----------------- | ------------------- | ------------------------------------------- |
| Pass              | `PASS ✅`           | Goals + DoD met, no blatant defects         |
| Ready-to-finalize | `READY ✅`          | Final verification pass before finalization |
| Changes needed    | `CHANGES NEEDED ⚠️` | Goals/DoD unmet or blatant defect           |
| Blocked           | `BLOCKED 🚫`        | Verification could not complete             |

- **`PASS ✅`** is the everyday confirmation. Goals met, work sound.
- **`READY ✅`** is reserved for the **final verification pass** — when this is the last review before finalization and everything is confirmed good. It signals "the durable artifact is now ready for finalization; everything is good." Use green ticks (`✅`) with it, always.
- **`CHANGES NEEDED ⚠️`** triggers the iteration loop back to the implementation agent.
- **`BLOCKED 🚫`** means verification could not complete at all — distinguish it clearly from CHANGES NEEDED.

A failed verification (CHANGES NEEDED) writes feedback just like a pass — that is the iteration loop. The implementation agent reads the feedback subsection and iterates.

### 5. Prompt the user

After writing the feedback subsection, **always** tell the user in chat:

- which artifact received the new feedback subsection;
- the verdict and marker;
- (for CHANGES NEEDED) the required changes in one or two lines;
- (for PASS/READY) that the work is confirmed and (for READY) ready for finalization.

This is the only chat output that is mandatory every run. It exists so the user and orchestrator always know a verification completed and where to look, without having to ask.

## No-Don't-Make-Me-Wait — Why It Is By Default

The orchestrator agent (or a sub-agent it spawns) performs the verification. The moment that work is done, the result is written into the durable artifact's feedback section. The orchestrator then prompts the user that feedback was added.

This means:

- The orchestrator does its job and finishes without waiting on the user.
- If the user has questions or wants explanations, they can ask while the orchestrator has already moved on or is standing by.
- In the worst case, the user and the agent simply iterate by updating the feedback section.
- The orchestrator always tells the user it added a feedback subsection — the one mandatory chat output — so nothing happens silently.

This is the default behavior. It does not require the user to opt in per run.

## Provenance In The Feedback Subsection

Every feedback subsection this skill writes carries its verifying-agent-family label and the date in its heading (see the writeback shape above). This is lightweight provenance — who verified and when — sufficient for the iteration loop. It does not replace the artifact's own `## Agent Provenance` or `## Agent Change Log`, which the artifact's owning skill already manages.

Do not inject full provenance blocks into feedback subsections. Do not edit the artifact's `## Agent Provenance` table — that is the owning skill's responsibility. The `## Agent Change Log` is the opposite case: appending its new row is required (see the writeback step); rewriting, renumbering, or reordering earlier rows remains forbidden. If the artifact lacks provenance entirely, note it as a genuine uncertainty in the feedback subsection and move on; do not retroactively author provenance for a work you did not create.

## Boundaries

Do:

- verify against the stated goals, DoD, and contract only;
- read and diff the implementation, not the whole repository;
- report unmet goals, blatant defects, and explicitly requested checks;
- write a new dated feedback subsection by default (No-Don't-Make-Me-Wait);
- append the artifact's `## Agent Change Log` row recording the writeback, without touching earlier rows;
- always prompt the user that feedback was added;
- use the verdict markers exactly as defined;
- credit the verifying sub-agent's family truthfully.

Do not:

- hunt edge cases, nitpick style, or propose optional improvements as findings;
- invent criteria the contract does not state;
- expand verification into a full audit — point to `inspect` Mode B if the user wants that;
- expand into independent multi-agent review — point to `subagent-verification-loops` for that;
- edit the artifact's goals, contract, plan, task, or non-feedback content;
- edit the artifact's `## Agent Provenance` table;
- create a new artifact without explicit user approval;
- claim the work passed without real evidence each DoD item was met;
- claim the work failed on speculative or hypothetical grounds;
- block the orchestrator waiting for the user before writing feedback.

## Output Format

Lead with the verdict. Then the evidence. Then the writeback confirmation.

```text
Verification of [target]: [PASS ✅ | CHANGES NEEDED ⚠️ | BLOCKED 🚫 | READY ✅]

[For PASS/READY] Confirmed:
- [goal/DoD item met, with evidence]
- [goal/DoD item met, with evidence]

[For CHANGES NEEDED] Not met:
- [goal/DoD item, with specific location and why]
- [blatant defect, with specific location and why it breaks normal use]

[For BLOCKED] Could not complete:
- [exactly what is missing]

Feedback subsection written to [artifact path] under ## Feedback Section.

[For READY] The durable artifact is now ready for finalization; everything is good.
```

Keep it tight. The artifact's feedback subsection carries the detail; chat carries the verdict and the pointer.

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

This rule is **emitted into** every artifact this skill produces, adjacent to the DEFINITION OF DONE or Verification Checklist it governs — not buried in a trailing notes section. The executing agent must read it inside the artifact it was handed, without consulting any workspace contract.

## In-Pass And Deferred Real-World Verification

**In-Pass And Deferred Real-World Verification.** Classify every verification item before saving or finalizing an artifact:

- **In-Pass Verification:** evidence the executing agent can produce safely in the current pass, including deterministic tests, fixtures, simulations, and mock scenarios. These items remain blocking completion criteria and follow Checklist Tick Discipline.
- **Deferred Real-World Verification:** evidence that genuinely requires later live use, elapsed time, user adoption, or an external event. Put only these items in a separate `## Deferred Real-World Verification` checklist. They are non-blocking for finalization and may remain unticked after all in-pass completion criteria are met. State the future trigger and evidence required for each item.

Never defer an item the current agent can safely verify now merely to claim completion. Omit the deferred section when no genuine deferred item exists.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;

- confirm the `## Checklist Tick Discipline` section is present and its rule text is unmodified;
- confirm the `## In-Pass And Deferred Real-World Verification` section is present; immediately verifiable items remain blocking and any genuine later-use items are isolated under a non-blocking `## Deferred Real-World Verification` checklist with their trigger and required evidence;
- confirm the `## No Invented Sync Constraints` section is present, and that a produced artifact contains **no** invented sync constraint in its DEFINITION OF DONE, Verification Checklist, CONSTRAINTS, or FAILURE sections;
- confirm a newly produced artifact actually carries the Checklist Tick Discipline rule verbatim, since the section can survive in this skill while the template silently loses it;

After a verification run, confirm and report:

- the verification target read or diffed;
- the goals/DoD source used (Prompt Contract / Verification Checklist / plan / task / North Star);
- the verdict and marker, with evidence for each confirmed or unmet item;
- the feedback subsection was written to a resolved writeback target (or the fallback pause fired and what the user chose);
- confirm the writeback's Agent Change Log row was appended, or its absence noted as an uncertainty;
- the user was prompted that feedback was added;
- no over-sabi: no speculative findings, no style nitpicks, no optional improvements reported as findings;
- no edits were made to non-feedback content or the artifact's provenance table.

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`). Read the result from the exit code with stdout and stderr captured separately: exit `0` is valid; exit `1` with empty stderr is invalid; exit `1` with non-empty stderr means the validator crashed and validity is unknown. Never merge the streams.
