---
name: agent-chatrooms
description: Run a structured discussion among independent agents with distinct roles, then synthesize consensus, disagreements, and a recommended decision. Use only when the user explicitly invokes /agent-chatrooms.
---

# Agent Chatrooms

Use independent agents to debate a defined question across structured rounds. The orchestrating agent moderates the discussion and produces the final synthesis.

## Project Contract

Follow the host project's canonical contract, such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`. Its safety rules, approval gates, path limits, and product-code workflow remain unchanged.

This is a discussion and decision-support workflow. Invoking it does not authorize implementation, file edits, product-code generation, or operational commands.

## Invocation

Run this workflow only when the user explicitly invokes:

- `/agent-chatrooms`

Do not activate from phrases such as "debate this", "have agents discuss", "chatroom", or similar natural language unless the slash command is present.

## Required Inputs

Determine:

- the question or decision to debate
- relevant facts and constraints
- agent count, default `3`
- round count, default `3`
- model preference, default environment default
- user-specified roles, if any
- whether durable output is wanted, default `false`

Ask for clarification when the question is too broad to produce a decision.

### Intake Template

Before starting the debate, confirm the run shape by presenting this template for the user to fill and return:

```text
Chatroom Setup - Fill or Delegate!
a.) Question/Decision to debate = ?
b.) Key facts and constraints the agents should know = ?
c.) Number of agents = ? (default 3)
d.) Number of rounds = ? (default 3)
e.) Model = ? (default: environment default)
f.) Roles = ? (name them, or say "auto" to let the orchestrator pick)
g.) Durable output = ? (default no; "yes" saves a timestamped run folder)
```

Template rules:

- Any field the user leaves as `?`, blank, `auto`, `infer`, `default`, `you choose`, or a clear equivalent is delegated: use the default or the orchestrating agent's best judgment.
- Pre-fill any field the user already answered in their invocation message and do not re-ask it.
- When the invocation message already supplies the question plus enough context, skip the template entirely and confirm the effective run shape in a single line (agents, rounds, model, roles, durable) before starting.
- The intake is a confirmation step, not an interrogation. Never block a quick debate behind unanswered optional fields.

## Capability Check

Use genuinely independent agents when the active environment provides multi-agent or subagent tools.

If independent agents are unavailable:

- explain that a true agent chatroom cannot run
- offer a clearly labeled single-agent role simulation
- do not present simulated roles as independent agents

## Role Selection

Use the user's roles exactly when provided. Otherwise choose roles that create useful tension.

Common sets:

- engineering: architect, pragmatist, risk reviewer
- product: user advocate, business strategist, implementation engineer
- strategy: opportunity advocate, skeptic, synthesizer

Avoid redundant roles that are likely to repeat the same position.

## Configuration

| Parameter             | Default               | Description                                                  |
| --------------------- | --------------------- | ------------------------------------------------------------ |
| `N`                   | `3`                   | Number of participating agents; minimum `2`                  |
| `R`                   | `3`                   | Maximum debate rounds                                        |
| `model`               | `environment default` | Participant model unless the user specifies an available one |
| `roles`               | `auto`                | User-specified roles or domain-appropriate automatic roles   |
| `durable`             | `false`               | Whether to save structured state and a report                |
| `output_dir`          | `tmp\agent-chatrooms` | Base directory for durable run folders                       |
| `stop_on_convergence` | `true`                | Stop early when proposals align at high confidence           |

Do not promise a model that the active environment does not expose. If the user names an unavailable model, explain the limitation and use an agreed alternative.

## Workflow

### 1. Frame the room

Give every agent the same:

- problem statement
- confirmed context
- constraints
- expected response format

Give each agent only its distinct role and framing. Do not tell agents the desired conclusion.

Maintain this state in memory. If `durable` is explicitly enabled, save the same shape to a host-approved working path:

```json
{
  "problem": "{problem statement}",
  "context": "{confirmed context and constraints}",
  "configuration": {
    "agent_count": 3,
    "max_rounds": 3,
    "model": "{available model or environment default}",
    "stop_on_convergence": true
  },
  "agents": [
    {"name": "Agent A", "role": "{role}", "framing": "{role description}"},
    {"name": "Agent B", "role": "{role}", "framing": "{role description}"},
    {"name": "Agent C", "role": "{role}", "framing": "{role description}"}
  ],
  "rounds": [],
  "final_output": null
}
```

### 2. Opening round

Ask each agent for:

- position
- reasoning
- concrete proposal
- principal risks
- confidence from 1 to 10

Run agents in parallel when supported.

Use this prompt shape:

```text
You are {role}: {role_description}

PROBLEM:
{problem}

CONFIRMED CONTEXT:
{context}

CONSTRAINTS:
{constraints}

This is Round 1 of a structured multi-agent debate. Take a clear position and make your reasoning inspectable.

Respond exactly with:
POSITION: {one-sentence stance}
REASONING:
- {key point}
- {key point}
- {key point}
PROPOSAL: {concrete recommendation}
CONCERNS:
- {principal risk}
CONFIDENCE: {1-10}

Do not edit files or execute commands.
```

### 3. Debate rounds

For each later round, provide the complete prior discussion and require each agent to:

- address the strongest counterargument
- state agreements and concessions
- state remaining disagreements
- refine its proposal
- update confidence

Do not allow agents to merely repeat their opening position.

Use this prompt shape:

```text
You are {role}: {role_description}

PROBLEM:
{problem}

CONFIRMED CONTEXT AND CONSTRAINTS:
{context_and_constraints}

PREVIOUS DISCUSSION:
{all previous round entries}

This is Round {round_number}. Engage with the strongest arguments already made. Change your position when the evidence warrants it.

Respond exactly with:
AGREEMENTS:
- {what another agent got right}
DISAGREEMENTS:
- {remaining disagreement and why}
COUNTERARGUMENT RESPONSE: {response to the strongest challenge}
REFINED PROPOSAL: {updated recommendation}
CONFIDENCE: {1-10}

Do not edit files or execute commands.
```

After each round, append this state in memory or to the explicitly requested durable JSON:

```json
{
  "round": 1,
  "entries": [
    {"agent": "Agent A", "role": "Architect", "response": "...", "confidence": 8},
    {"agent": "Agent B", "role": "Pragmatist", "response": "...", "confidence": 7},
    {"agent": "Agent C", "role": "Risk Reviewer", "response": "...", "confidence": 9}
  ]
}
```

### 4. Check convergence

Stop early when proposals materially align and all active agents report confidence of at least `8`. Do not manufacture consensus when substantive disagreements remain.

### 5. Synthesize

The orchestrating agent reports:

- areas of consensus
- strongest unresolved disagreement
- tradeoffs behind that disagreement
- unresolved risks
- meaningful changes of mind
- recommended action and its rationale
- decisions that still require the user

The recommendation must be the orchestrating agent's evidence-based synthesis, not a simple majority vote.

## Output

Default output is chat only. Do not create `chat.json`, transcripts, or report files unless the user explicitly requests a durable artifact and the host project permits it.

Do not proceed from debate into implementation unless the user separately invokes or authorizes an execution workflow.

Use this report shape in chat or in the optional durable report:

```markdown
# Agent Chatroom Report

**Problem**: {problem}
**Agents**: {effective agent count}
**Rounds**: {completed rounds}
**Convergence**: {reached | not reached}

## Participants
| Agent | Role | Final Confidence |
|-------|------|------------------|
| Agent A | {role} | {confidence}/10 |
| Agent B | {role} | {confidence}/10 |
| Agent C | {role} | {confidence}/10 |

## Consensus
{Material conclusions shared by the participants}

## Key Disagreements
{Competing positions and their strongest evidence}

## Recommended Action
{Orchestrating agent's synthesis and rationale}

## Unresolved Risks
{Risks or assumptions that remain unresolved}

## Debate Highlights
{Important concessions, counterarguments, or changes of mind}

## User Decisions Required
{Questions that cannot be resolved by the debate alone}
```

### Durable Output

When the user explicitly enables `durable`, save each run to a timestamped folder mirroring the model-chat run-folder convention:

```text
<output_dir>\<YYYYMMDD-HHMMSS>\
├── conversation.json   ← the room-state JSON above, with all round entries appended and final_output filled
└── report.md           ← the report template above
```

Also write or update `<output_dir>\latest.json` as a pointer to the most recent run:

```json
{
  "latest_run": "{YYYYMMDD-HHMMSS}",
  "run_dir": "{full path to the run folder}",
  "problem": "{problem statement}",
  "convergence": "reached | not reached",
  "timestamp": "ISO-8601"
}
```

Write all durable files in UTF-8. Preserve previous run folders. Use a plain JSON pointer file, never a symlink.

When durable output is requested, choose a workspace-safe location under the host project's approved working-artifact directory (default: `tmp\agent-chatrooms` under the host workspace). Do not hard-code `active/chatroom/`.

## Boundaries

Do:

- use distinct, relevant perspectives
- preserve the full prior discussion between rounds
- report disagreement honestly
- distinguish facts, assumptions, and judgments
- disclose unavailable true multi-agent capability

Do not:

- auto-trigger this skill
- let agents edit files or execute commands
- use bypass-permission modes
- assume a specific provider or model
- create durable chatroom artifacts by default
- treat confidence scores as objective evidence

## Edge Cases

- **Fewer than two agents requested:** explain that a debate requires at least two.
- **Agents agree immediately:** stop after the opening round and report convergence.
- **Agents deadlock:** report the competing positions and the user decision required.
- **Agent goes off-topic:** exclude that contribution and disclose the effective participant count.
- **Safety-sensitive question:** include an appropriate risk or compliance perspective and preserve host-project gates.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to the optional human-readable chatroom report; schema-safe state metadata only when the state schema permits it.

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

This skill owns the discussion, structured state, report content, and durable run-folder rules. When co-invoked with `html-this` or `pdf-this`, hand only the human-readable `report.md` serialization to the format skill and create only `report.html` or `report.pdf` as requested. Keep `conversation.json` and `latest.json` native because they are machine state. A native report intermediate may exist only in an approved temporary location.

If multiple report-format siblings exist, treat them as one logical report on update. Preserve the run folder and basename, and update every sibling consistently. This section overrides `.md`-only report examples only during a co-invoked format run.

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

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

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

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;

- confirm a newly produced artifact carries a `## Feedback Section` immediately above its `## Agent Change Log`, present even when empty, using the numbered `### Feedback N` grammar;

After creating or updating this skill:

- confirm only `/agent-chatrooms` activates it
- confirm default behavior is discussion-only and chat-only
- confirm the intake template exists with fields a-g and the fill-or-delegate rules
- confirm the intake never re-asks values already supplied and never blocks quick debates
- confirm durable output remains opt-in and uses the timestamped run folder, `report.md`, and `latest.json` pointer shapes
- confirm implementation requires separate authorization
- confirm no provider-specific model or permission assumptions remain
- confirm configuration, state JSON, round-entry JSON, prompt shapes, and report shape remain intact
- validate the folder with the installed `quick_validate.py` in UTF-8 mode
