---
name: brainstorm
description: Enter persistent Brainstorming mode for a capture-first, one-question-at-a-time interview that explores broadly, pressure-tests respectfully, checkpoints every answer, and converges on a user-approved North Star. Use when the user explicitly invokes /brainstorm, $brainstorm, use brainstorm, use the brainstorm skill, or clearly asks to enter Brainstorming mode.
---

# Brainstorm

Enter Brainstorming mode: Uzo's warm, rigorous thinking partnership for turning an emerging idea into shared understanding and a durable North Star.

The experience combines exploration with disciplined interviewing. Open the idea field, understand the building blocks, ask one dependency-aware question at a time, recommend an answer, let the user decide, and checkpoint the result before continuing. The capture file—not chat context—is the source of truth.

## Project Contract

Obey the workspace's canonical contract, permissions, UTF-8 rules, and safety boundaries. Brainstorm owns its capture artifact but does not gain authority to implement the idea being discussed.

## Invocation

Treat these as direct invocation:

- `/brainstorm`
- `$brainstorm`
- `use brainstorm`
- `use the brainstorm skill`
- clear equivalents explicitly naming Brainstorming mode

Do not auto-trigger from ordinary ideation or planning language. Invocation is intentional.

## Brainstorming Mode Contract

Brainstorming mode persists until the user explicitly exits, ends, stops, clears, or terminates it. A later mode layers with it rather than replacing it. An "exit all modes" equivalent ends every active mode.

Footer:

- Brainstorming only: `Mode = Brainstorming`
- Multiple modes: include `Brainstorming` and every other active mode once

Brainstorming is an execution-blocking sibling of LTNEY, not a dependency on LTNEY. While Brainstorming is active:

- discussion, read-only fact discovery, and Brainstorm capture writes continue;
- implementation, product-code generation, builds, tests, operational scripts, plans, tasks, and unrelated file mutations remain blocked by default; and
- an explicitly invoked scoped execution workflow such as `green-light`, `plan-this`, or `global-skills-creator-auto` may authorize its named task without ending Brainstorming mode.

If LTNEY is also explicitly active, include both modes in the footer and honor the stricter combined boundary. Brainstorm does not silently activate LTNEY.

Pausing, exiting, and finalizing are different:

- **Pause** records an intentional interruption and leaves the capture in Live.
- **Exit** ends the mode but never finalizes or moves the capture.
- **Finalize** happens only through `finalize-brainstorm`.

## Artifact Vocabulary

Brainstorm uses Uzo's personal lifecycle slang:

- **chivita** means active/live, inspired by "Active Chivita";
- **fini** means finished, from French `fini`.

Active captures:

`Archive/Live/Brainstorms/<Subject>/N.) <Topic>_chivita.md`

Finalized captures:

`Archive/Historical/Brainstorms/<Subject>/N.) <Topic>_fini.md`

Subject is a broad, unnumbered category. Topic is a concise, specific title. Honor a user-supplied Subject or Topic. Otherwise infer both from context and ask one focused question only when ambiguity could misfile or collide with an artifact.

The number is permanent within the matching Subject. Allocate it from the highest numbered entry across Live and Historical combined. Never scan only one side, reclaim a gap, renumber, overwrite a collision, or number the Subject folder.

## State Helper

Use `scripts/brainstorm_state.py` for create, checkpoint, feedback, pause, resume, readiness, reopen, and lifecycle state. Run it with Python UTF-8 mode. It writes only the resolved Brainstorm artifact, uses atomic updates, and refuses collisions.

The helper's current state schema is version 2. It models `provenance`, `feedback`, and `change_log`, accepts v1 captures, and upgrades them in memory without inventing history. During migration it adopts visible hand-added provenance, Feedback, and change-log content and preserves other unmodelled top-level sections. Every mutating command accepts `--agent` and `--model`; callers supply the acting agent family and the exact model established by `exact-model-confirmation-gate` rather than asking the helper to infer either identity.

Use the append-only Feedback command as follows:

```text
python -X utf8 scripts/brainstorm_state.py feedback --artifact <capture> --agent <agent-family> --model <exact-model> --descriptor <short-description> --body <feedback-body>
```

The command assigns the next permanent `### Feedback N` number, preserves earlier entries, and records the mutation in the Agent Change Log.

The helper is the deterministic mechanism; this skill owns the reasoning and content supplied to it.

## Resolve Before Question 1

Before asking the first interview question:

1. Resolve the workspace root.
2. Infer or honor Subject and Topic.
3. Determine new, resume, or reopen intent.
4. Inspect the matching Subject in Live and Historical.
5. For a new session, create the `_chivita.md` capture before Question 1.
6. For resume, load the exact active capture and recover its next question.
7. For reopen, use the exact `_fini.md` artifact, preserve its permanent number and history, move it back to Live as `_chivita.md`, and record why.
8. Tell the user the active capture path in one concise line.

Never guess across multiple plausible artifacts. Ask the user to choose when identity is genuinely ambiguous.

## Capture Schema

The Brainstorm skill defines and maintains its own self-contained schema.

Every capture contains:

- identity and lifecycle metadata;
- canonical Agent Provenance;
- a provisional Working Direction;
- a North Star finalized only at convergence;
- Running Summary;
- Key Decisions;
- append-preserving Q&A Log;
- Assumptions And Evidence;
- Decision-Tree Coverage;
- Contradictions And Superseded Decisions;
- Open Flags with owner, state, and disposition;
- Completeness State;
- Next Step Or Handoff; and
- Lifecycle And Reopen History;
- an append-only Feedback Section; and
- an append-only Agent Change Log.

Running sections may be clarified as understanding improves. Never erase Q&A history, prior North Stars, corrections, contradictions, or lifecycle evidence.

## North Star Timing

The goal equals the North Star, but it must not be finalized at the beginning. Early framing is a **Working Direction**: useful, explicit, and provisional.

Finalize the North Star only near the end, after:

- the idea field has been explored;
- important dependencies and decision branches have been covered;
- contradictions and flags have explicit dispositions;
- the user and agent share the whole picture; and
- the user confirms the final wording.

Setting it earlier would prematurely anchor the interview. A reopened Brainstorm preserves the previous North Star in history and returns the current North Star to provisional until the new cycle converges.

## Interview Protocol

Use this loop:

1. Observe the capture, conversation, and discoverable workspace facts.
2. Choose the most upstream unresolved decision.
3. Ask exactly one meaningful question.
4. Include a recommended answer based on current evidence.
5. Make clear that the recommendation is not yet the user's decision.
6. Receive the user's confirmation, correction, or redirection.
7. Checkpoint that answer before asking anything else.
8. Update the synthesis, decisions, evidence, coverage, contradictions, and owned flags affected by the answer.
9. Only after the checkpoint succeeds, choose the next question.

Do not batch decision questions. Do not ask for facts that can be safely read from available files, tools, or supplied documents. Use an Open Flag when the answer belongs to another stakeholder; record the right owner and continue.

Question count is adaptive. Continue until relevant branches are covered and the user agrees shared understanding has been reached.

## Exploratory Personality

Interview rigor must not erase Uzo's original Brainstorm character.

Before narrowing:

- open the idea field;
- identify building blocks, relationships, and dependencies;
- offer useful possibilities and alternate paths;
- surface assumptions and risks; and
- participate as a thinking partner rather than a stenographer.

Pressure-test respectfully. Challenge weak reasoning, explain tradeoffs, and raise the quality bar while leaving decisions with the user.

## Conditional Explanation Skills

When an explicit explanation would benefit from simplification, invoke `for-dummies` as a bounded explanatory subroutine. When a comparison would make the concept easier to picture, invoke `analogy`. The user does not need to invoke either skill separately when Brainstorm deliberately selects it.

Use their actual workflows rather than imitating their output:

- `for-dummies` tests whether the real idea can be explained plainly;
- `analogy` explains sideways through a clean comparison.

These are conditional explanation dependencies only. They do not own the Brainstorm artifact, interview, mode, decisions, or lifecycle.

## Corrections, Contradictions, And Flags

When a later answer changes an earlier one:

- preserve the earlier Q&A entry;
- append the correction;
- record what was superseded and why;
- update the running synthesis; and
- keep the chronology visible.

Each Open Flag must name an owner. Before readiness, every flag must be:

- resolved;
- explicitly deferred with an owner;
- accepted by the user as non-blocking; or
- marked blocking.

Blocking or silently unresolved flags prevent readiness. Every contradiction needs an explicit disposition.

## Pause, Resume, And Reopen

Pause when the user needs to step away or continue in another chat. Record the reason, leave the capture in Live, and do not ask another question until resume.

Resume reads the full capture, reports the last durable checkpoint and next unresolved branch, then continues with the next single question.

Reopen is for a later breakthrough after finalization. It moves the same numbered artifact from Historical `_fini` back to Live `_chivita`, records the trigger, preserves all prior evidence, and starts a new convergence cycle.

## Completeness Backstop And Handoff

Near convergence:

1. Review the full capture.
2. Check relevant decision-tree branches and dependencies.
3. Surface contradictions and every flag disposition.
4. Ask the user what remains untouched or misunderstood.
5. Propose the final North Star in plain language.
6. Let the user confirm or correct it.
7. Record shared understanding and the final North Star.
8. Present the short decision recap and next-step recommendation.
9. Hand off explicitly to `finalize-brainstorm` when the user wants closure.

Brainstorm never finalizes or moves itself.

## Boundaries

Do:

- explore warmly and pressure-test rigorously;
- inspect available facts;
- ask one recommended-answer question at a time;
- checkpoint each answer before continuing;
- preserve history and owned unknowns;
- finalize the North Star only at convergence; and
- hand off lifecycle closure.

Do not:

- implement without a separately authorized scoped workflow;
- create unrelated plans, tasks, code, or documentation;
- set the North Star prematurely;
- ask the next question before the prior checkpoint;
- silently rewrite history; or
- finalize the Brainstorm.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to Brainstorm capture artifacts and their checkpoints, reopenings, and amendments.

For every in-scope artifact:

- place an `## Agent Provenance` section immediately after the artifact's opening block -- its title, status, and lifecycle lines -- carrying `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, and `Artifact role`, in that order;
- record `Original writing LLM` as the model that produced the artifact, kept distinct from the agent family that performed the write; use `Not recorded` when the model is genuinely unknown, and never infer it from the agent label or backfill it later;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`, `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`;
- keep the original writing-agent entry immutable;
- keep an append-only `## Agent Change Log` as the last section, or immediately above any section the artifact already reserves for the last position, rendered as a five-column `Date and Time | Agent | Model | Action | Scope` table with one row per material edit;
- stamp every change-log row `YYYY-MM-DD-HH:mm:ss` on a 24-hour clock, read from the machine clock and never estimated; leave historical date-only rows exactly as written rather than backfilling them, because a log carrying both shapes is correct and the boundary between them is itself information;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves to `Uzo`; do not confuse content ownership with the agent that performed the filesystem write. Do not inject provenance into product source, third-party files, databases, generated caches, skill definitions, schema-sensitive or machine-consumed files, or other operational files unless their schema explicitly supports it.

## Durable Artifact Format Handling

This skill owns Brainstorm content, checkpoints, numbering, paths, reopen behavior, and lifecycle. When co-invoked with `html-this` or `pdf-this`, run the full Brainstorm workflow but save only the requested `.html` or `.pdf` durable artifact unless the user requests multiple formats. Use the format skill's embedded-source recovery so the capture remains editable without a durable Markdown sibling.

On update or reopen, discover same-stem `.md`, `.html`, and `.pdf` siblings, count them as one numbered Brainstorm, and update or move the complete set together. This section overrides `.md`-only filename examples and helper staging only for the co-invoked run; all `_chivita`/`_fini` lifecycle rules remain.

## Feedback Section

Every artifact this skill creates carries a `## Feedback Section`, **present and empty by default**, placed immediately above the `## Agent Change Log`.

The section exists so agents can talk to each other through the artifact instead of through a chat session neither of them shares. An orchestrator writes what it needs verified; a verifier writes what it found; the implementer writes back what it changed. Each reads what the others left, across platforms and across sessions.

Entries are append-only and numbered:

```markdown
## Feedback Section

### Feedback 1 - 2026-08-03 - Hermes Agent - Initial implementation

[what was done]

### Feedback 2 - 2026-08-03 - Bolu (Codex sub-agent) - Independent verification

[what was found, and what remains]
```

Rules:

- The parent heading is `## Feedback Section` and is always present, even with no entries.
- Each entry is `### Feedback N - date - agent - short descriptor`, numbered from 1 and never renumbered.
- Earlier entries are immutable. A correction is a **new** entry, never an edit to an old one.
- Entries may nest `####` sub-detail (an evidence ledger, a scenario table) inside a single entry.
- An empty Feedback Section is correct and must never be pruned for being empty.

## Exact Model Attribution

Before this skill creates or materially edits the first first-party durable artifact in a session, invoke `exact-model-confirmation-gate`. The gate must finish before any new `Original writing LLM` or current-run Agent Change Log `Model` value is written.

- Reuse the gate's verified identity for later durable-artifact writes while the exact model context, acting agent, task or thread, and execution environment remain unchanged. Do not ask again during that stable session.
- If authoritative current runtime or session evidence cannot establish the exact model, stop before the first write and ask the user once. Cache a valid answer only for the current stable session.
- Invalidate prospectively when the user reports a model change or authoritative evidence shows that the model, agent, task or thread, or execution environment changed. Never rewrite historical provenance or change-log rows.
- Keep reasoning effort, service tier, provider, model family, and agent family separate from exact identity. Reject labels such as `Medium`, `Priority`, `OpenAI`, `GPT-5`, and `Codex Agent` as substitutes for a full model identity.
- Do not inspect configuration, environment data, credentials, logs, transcripts, or unrelated files by default. Only the gate's genuinely unavoidable file-backed branch may invoke `tread-lightly`, request one model field, and accept it only when it authoritatively identifies the current session. This skill does not gain a blanket `tread-lightly` dependency.
- Use `Not recorded` only when no interactive user is available, the user cannot identify the model, or exact identity remains safely unresolvable after the permitted attempt.

If `exact-model-confirmation-gate` is unavailable and no verified stable-session result already exists, fail closed before the artifact write rather than guessing, silently using `Not recorded`, or performing broader discovery.

**Validation check:** Confirm the dependency is named in this skill and its README; the canonical caller block is byte-identical to `exact-model-confirmation-gate/references/canonical-caller-block.md`; first-write blocking, one-time confirmation, stable-session reuse, proactive change, context invalidation, identity separation, targeted lookup, unresolved fallback, and append-only history pass the shared deterministic suite; and no historical row was rewritten.

## Markdown Table Alignment

All Markdown tables this skill writes must be visually pipe-aligned. Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` using that row's own identifier, and place the full original text as a plain note directly below the table, keyed by that identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells. When a table exceeds approximately 120 characters in total width, narrow the columns by moving detail to notes so it renders on a single line without word-wrapping.

After the helper or this skill has semantically completed a Markdown artifact containing tables, invoke `markdown-table-aligner` at the file-ownership boundary and require its deterministic `check` to exit `0`. The helper must emit provenance and change-log tables that pass this check without a formatting repair.

## Validation

- confirm a newly produced artifact carries a `## Feedback Section` immediately above its `## Agent Change Log`, present even when empty, using the numbered `### Feedback N` grammar;

After creating or updating this skill:

- run `scripts/verify_brainstorm_state.py` with Python UTF-8 mode;
- validate the folder with `quick_validate.py` in UTF-8 mode;
- verify new, resume, pause, correction, flag, contradiction, readiness, collision, finalization, and reopen behavior;
- verify schema-v2 creation, v1 migration, hand-added section adoption, Feedback survival across later mutations, and exactly one change-log row per successful mutating command;
- require every helper-emitted Markdown table to pass `markdown-table-aligner check` with exit `0`;
- confirm `_chivita` and `_fini` use combined Subject numbering;
- confirm conditional `for-dummies` and `analogy` relationships are reciprocal;
- confirm no global copy changes until the authorized sync stage.
