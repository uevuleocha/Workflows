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

| Parameter | Default | Description |
|-----------|---------|-------------|
| `N` | `3` | Number of participating agents; minimum `2` |
| `R` | `3` | Maximum debate rounds |
| `model` | `environment default` | Model used for participants unless the user specifies an available model |
| `roles` | `auto` | User-specified roles or domain-appropriate automatic roles |
| `durable` | `false` | Whether to save structured state and a report |
| `output_dir` | `tmp\agent-chatrooms` | Base directory for durable run folders, under the host workspace's approved working-artifact location |
| `stop_on_convergence` | `true` | Stop early when proposals align at high confidence |

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

## Validation

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
