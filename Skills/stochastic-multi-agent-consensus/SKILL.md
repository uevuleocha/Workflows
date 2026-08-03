---
name: stochastic-multi-agent-consensus
description: Poll independent agents with controlled framing variations, aggregate their structured answers, and report consensus, divergence, uncertainty, and outliers. Use only when the user explicitly invokes /stochastic-multi-agent-consensus.
---

# Stochastic Multi-Agent Consensus

Collect independent judgments on the same defined problem and aggregate them mechanically. Use the result as decision support, not proof.

## Project Contract

Follow the host project's canonical contract, such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`. Its safety rules, approval requirements, path scope, and product-code workflow remain in force.

Invoking this skill authorizes analysis only. It does not authorize implementation, file edits, purchases, trades, deployments, or other operational action.

## Invocation

Run this workflow only when the user explicitly invokes:

- `/stochastic-multi-agent-consensus`

Do not activate from phrases such as "get multiple opinions", "poll agents", "consensus", or similar natural language unless the slash command is present.

## Required Inputs

Determine:

- the precise question
- relevant context and constraints
- response type: ranking, recommendation, scoring, or binary
- options to evaluate, when applicable
- agent count, default `10`

Clarify vague questions before spending multiple agent calls.

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `N` | `10` | Requested independent agent count; minimum `3` |
| `model` | `environment default` | Available model used for independent responses |
| `output` | `ranking` | `ranking`, `recommendation`, `score`, or `binary` |
| `frames` | `auto` | Controlled reasoning frames selected for diversity |
| `durable_report` | `false` | Save a report only when explicitly requested |

Do not promise unavailable models. For simple binary questions, the user may explicitly choose a smaller sample of at least three.

## Capability Check

Use genuinely independent agents when the environment provides multi-agent or subagent tools.

If independent agents are unavailable:

- state that true stochastic multi-agent sampling cannot run
- offer a clearly labeled single-agent multi-perspective analysis
- do not report simulated perspectives as independent votes

## Workflow

### 1. Define one aggregation schema

Require every agent to use the same machine-comparable structure.

Examples:

- ranking: ordered options with a short rationale
- recommendation: top choices plus confidence
- scoring: numeric score per option using fixed criteria
- binary: `YES` or `NO`, confidence, and strongest reasons

Do not aggregate free-form essays without first normalizing them.

Recommended response contracts:

```text
RANKING
1. {option} - {one-sentence rationale}
2. {option} - {one-sentence rationale}
CONFIDENCE: {1-10}
```

```text
RECOMMENDATIONS
- NAME: {recommendation}
  RATIONALE: {one sentence}
  CONFIDENCE: {1-10}
```

```text
SCORING
- OPTION: {option}
  SCORE: {1-10}
  RATIONALE: {one sentence}
CONFIDENCE: {1-10}
```

```text
DECISION: YES | NO
CONFIDENCE: {1-10}
REASONS:
- {reason}
- {reason}
- {reason}
```

### 2. Create controlled variation

Keep the problem, evidence, constraints, and response schema identical. Vary only the reasoning frame.

Useful frames include:

- neutral
- risk-focused
- opportunity-focused
- contrarian
- first-principles
- user-focused
- resource-constrained
- long-term
- evidence-focused
- systems-focused

Framing diversity must not change the underlying question.

### 3. Run independent responses

Run agents in parallel when supported. Do not show agents each other's answers before they respond.

Require uncertainty and confidence to be explicit. Agents must return answers directly rather than modify files.

Use this prompt shape:

```text
{controlled_reasoning_frame}

PROBLEM:
{problem}

CONFIRMED CONTEXT:
{context}

CONSTRAINTS:
{constraints}

RESPONSE CONTRACT:
{shared_output_schema}

Analyze independently. Be concrete. State uncertainty rather than filling gaps with assumptions.
Do not edit files or execute commands.
```

### 4. Validate responses

Exclude malformed, off-topic, duplicated, or failed responses. Report the requested and effective sample sizes.

Do not silently replace failed responses with the orchestrating agent's own opinion.

### 5. Aggregate mechanically

Use the method matching the response type:

- ranking: Borda-style points, highest rank receiving the most points
- scoring: mean, median, range, and standard deviation when feasible
- binary: vote split plus confidence distribution
- recommendations: normalize equivalent ideas and count support

Classify normalized findings:

- strong consensus: at least 70% support
- mixed or divergent: 40% to 69% support
- minority: below 40% support
- unique outlier: proposed by one effective respondent

Thresholds describe agreement, not correctness.

For ranking tasks with `M` options, award `M` points to first place, `M-1` to second, continuing to `1` point for last place. Do not use agent count as the ranking-point maximum unless the number of agents and options happens to match.

### 6. Interpret

Report:

- effective sample size
- strongest consensus
- most important divergence
- confidence and variance
- most useful outlier
- assumptions shared across agents
- evidence gaps that polling cannot resolve
- orchestrating agent's recommendation, if the user requested one

## Output

Default output is chat only. Create a durable consensus report only when the user explicitly requests one and the host project permits it.

Do not execute the winning option. Any implementation or operational action requires a separate authorized workflow.

Use this report shape in chat or for the optional durable report:

```markdown
# Stochastic Multi-Agent Consensus Report

**Problem**: {problem}
**Requested Agents**: {N}
**Effective Agents**: {valid response count}
**Output Type**: {ranking | recommendation | score | binary}

## Consensus
{Items with at least 70% support}

## Divergences
{Items with 40%-69% support or materially split scores}

## Minority And Outliers
{Lower-support and unique ideas, labeled clearly}

## Aggregated Results
{Ranking points, recommendation counts, score statistics, or vote split}

## Confidence And Variance
{Confidence distribution and notable disagreement}

## Shared Assumptions
{Assumptions repeated across independent responses}

## Evidence Gaps
{Questions polling alone cannot answer}

## Individual Response Summary
| Agent | Frame | Result | Confidence | Included |
|-------|-------|--------|------------|----------|
| A | {frame} | {result} | {score}/10 | Yes |

## Recommended Interpretation
{What the result supports, without treating agreement as proof}
```

When durable output is requested, use a host-approved working-artifact path. Do not hard-code `active/consensus/`.

## Boundaries

Do:

- keep prompts comparable
- preserve response independence
- use proportional thresholds
- distinguish agreement from factual verification
- disclose excluded responses and effective sample size

Do not:

- auto-trigger this skill
- use consensus to replace source verification
- fabricate agent responses when tools are unavailable
- grant agents write or bypass permissions
- assume a specific model provider
- create report files by default

## Edge Cases

- **Fewer than three agents requested:** explain that the sample is too small for meaningful consensus and require at least three.
- **Even split:** report the split as the result; do not force a winner.
- **Unanimous answer:** still inspect shared assumptions and evidence gaps.
- **High variance:** emphasize the disputed criteria instead of averaging away the disagreement.
- **Safety-critical decision:** treat the poll as advisory and require authoritative evidence or professional review where appropriate.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule
to any user-requested durable consensus artifact.

For every in-scope artifact:

- place an `## Agent Provenance` section near the top with `Content owner`,
  `Original writing agent`, `Created`, and `Artifact role`;
- use a stable truthful agent-family label such as `Codex Agent`, `Claude Agent`,
  `Antigravity Agent`, `Hermes Agent`, or `zCode Agent`;
- keep the original writing-agent entry immutable;
- keep an append-only `## Agent Change Log` near the bottom, recording the date,
  acting agent, action, and concise scope for every material edit;
- if a legacy artifact lacks reliable creator evidence, use `Not recorded` rather
  than guessing, then log the current agent's actual change; and
- treat copying or global synchronization as transport, not authorship.

Keep `Content owner` for now. In Uzo's personal artifacts it normally resolves
to `Uzo`; do not confuse content ownership with the agent that performed the
filesystem write. Do not inject provenance into product source, third-party
files, databases, generated caches, skill definitions, schema-sensitive or
machine-consumed files, or other operational files unless their schema
explicitly supports it.

## Durable Artifact Format Handling

This skill owns polling, aggregation, uncertainty analysis, and optional report
content. When a durable report is requested and the skill is co-invoked with
`html-this` or `pdf-this`, save only the requested `.html` or `.pdf`
human-readable report unless the user requests multiple formats. Preserve any
machine-readable run state in its native format.

Same-stem report variants are one logical artifact and must be updated
consistently. This section overrides Markdown-only optional-report examples only
during a co-invoked format run.

## Validation

After creating or updating this skill:

- confirm only `/stochastic-multi-agent-consensus` activates it
- confirm prompts preserve independence and a common schema
- confirm aggregation methods and proportional thresholds are explicit
- confirm consensus is not presented as proof or execution authority
- confirm configuration, response contracts, agent prompt, and report shape remain intact
- validate the folder with the installed `quick_validate.py` in UTF-8 mode
