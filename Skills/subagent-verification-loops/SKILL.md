---
name: subagent-verification-loops
description: Independently verify an existing artifact through a reviewer-and-resolver loop, then report confirmed findings without automatically applying changes. Use only when the user explicitly invokes /subagent-verification-loops.
---

# Subagent Verification Loops

Review an existing artifact with fresh context, adjudicate the findings, and propose resolutions. Keep verification separate from implementation.

## Project Contract

Follow the host project's canonical contract, such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`. Its safety rules, path limits, approval requirements, and product-code workflow remain in force.

Invoking this skill authorizes review only. It does not authorize file edits, product-code changes, command execution, or global skill sync.

## Invocation

Run this workflow only when the user explicitly invokes:

- `/subagent-verification-loops`

Do not activate from phrases such as "verify this", "review this", "second opinion", or similar natural-language requests unless the slash command is present.

## Required Inputs

Identify:

- the artifact to verify
- the original requirements or contract
- relevant surrounding context
- requested review depth, if specified

Read only the context needed to judge the artifact. Ask for missing requirements when their absence would make the review speculative.

## Capability Check

Use genuinely independent reviewer agents when the active environment provides subagent or multi-agent tools.

If independent agents are unavailable:

- state that a true subagent loop cannot run in the current environment
- offer a clearly labeled single-agent independent review pass
- do not describe a role-played pass as independent multi-agent verification

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `reviewer_model` | `environment default` | Available model used for the fresh reviewer |
| `resolver_model` | `reviewer model` | Available model used for resolution |
| `max_loops` | `1` | Review cycles; maximum `2` |
| `severity_threshold` | `minor` | Lowest severity included in proposed corrections |
| `apply_changes` | `false` | This skill never applies changes by itself |
| `durable_report` | `false` | Save a report only when explicitly requested |

Do not promise unavailable models. Never use a permission-bypass mode for reviewer or resolver agents.

## Workflow

### 1. Prepare the review packet

Give the reviewer the artifact, requirements, and minimum necessary context. Do not include the implementer's hidden reasoning, intended verdict, suspected defects, or proposed fixes.

### 2. Run the independent reviewer

Ask the reviewer to assess:

1. correctness against requirements
2. missing cases and failure modes
3. security and data-safety risks
4. consistency with surrounding patterns
5. unnecessary complexity
6. missing or weak verification evidence

Require this structure:

- `VERDICT`: `PASS`, `ISSUES_FOUND`, or `CRITICAL`
- findings ordered by severity
- location or section
- concrete evidence
- recommended correction
- uncertainties or items requiring manual verification

The reviewer must not edit files.

Use this prompt shape:

```text
You are an independent senior reviewer. You did not create the artifact.

ORIGINAL REQUIREMENTS:
{requirements}

ARTIFACT TO REVIEW:
{artifact}

RELEVANT CONTEXT:
{minimum surrounding context}

Review for:
1. correctness against requirements
2. edge cases and failure modes
3. security and data-safety risks
4. consistency with surrounding patterns
5. unnecessary complexity
6. missing verification evidence

Respond exactly with:
VERDICT: PASS | ISSUES_FOUND | CRITICAL

ISSUES:
- SEVERITY: critical | major | minor | nit
  LOCATION: {file:line or section}
  PROBLEM: {specific defect}
  EVIDENCE: {why it is a real issue}
  RECOMMENDED CORRECTION: {smallest safe correction}

SIMPLIFICATIONS:
- {supported simplification, if any}

UNCERTAINTIES:
- {item requiring manual verification}

SUMMARY: {concise overall assessment}

Do not edit files or execute commands. Do not invent issues merely to produce findings.
```

### 3. Adjudicate the review

The orchestrating agent must check every finding against the artifact and requirements. Reject unsupported findings instead of forwarding them as fact.

If the verdict is:

- `PASS`: report that no verified issue was found
- `ISSUES_FOUND`: continue to a resolver pass
- `CRITICAL`: report the critical risk immediately and do not apply a fix

### 4. Run the resolver

Give the resolver the original artifact plus the adjudicated findings. Ask it to classify each finding as:

- `ACCEPTED`: valid, with the smallest safe correction
- `DECLINED`: unsupported or harmful, with reasoning
- `NEEDS_USER_DECISION`: valid tradeoff without one objectively correct answer

The resolver proposes corrections only. It must not edit files.

Use this prompt shape:

```text
You are an independent senior engineer resolving adjudicated review findings.

ORIGINAL REQUIREMENTS:
{requirements}

ORIGINAL ARTIFACT:
{artifact}

ADJUDICATED FINDINGS:
{verified_findings}

For every finding, respond with:
- FINDING: {identifier}
  DECISION: ACCEPTED | DECLINED | NEEDS_USER_DECISION
  REASON: {evidence-based rationale}
  PROPOSED CORRECTION: {smallest safe correction, or none}

Then provide a coherent corrected-state proposal sufficient for later authorized implementation.

Do not edit files or execute commands. Do not expand scope beyond the verified findings.
```

### 5. Re-verify when warranted

For complex or high-risk artifacts, run one additional reviewer pass against the proposed corrected state. Maximum: two review rounds.

If material issues remain after two rounds, stop and report that a deeper design or requirements decision is needed.

### 6. Deliver the result

Report:

- final verdict
- verified issue count by severity
- accepted, declined, and user-decision findings
- most important risk or correction
- remaining uncertainty
- whether the artifact is ready for the next phase

Default output is chat only. Create a durable report only when the user explicitly asks and the host project permits it.

Use this verification-report shape in chat or for the optional durable report:

```markdown
# Subagent Verification Report

**Artifact**: {artifact}
**Requirements**: {requirements reference}
**Rounds**: {completed rounds}
**Final Verdict**: {PASS | ISSUES_FOUND | CRITICAL}

## Issues
| # | Severity | Location | Problem | Resolution Status |
|---|----------|----------|---------|-------------------|
| 1 | {severity} | {location} | {problem} | {Accepted / Declined / User Decision} |

## Simplifications
{Supported simplifications or `None`}

## Proposed Corrections
{Non-mutating correction proposals}

## Uncertainties
{Manual verification still required}

## Reviewer Summary
{Independent review summary}

## Resolver Notes
{Accepted, declined, and unresolved reasoning}

## Readiness
{Ready for next phase | Corrections required | User decision required}
```

When durable output is requested, use a host-approved working-artifact path. Do not hard-code `active/verification/`.

## Product-Code Handling

For product source files:

- preserve any manual-copy or surgical-delivery workflow in the project contract
- never apply reviewer or resolver changes directly unless a separate authorized workflow permits it
- distinguish verified defects from optional refactors
- keep suggested changes tightly scoped to the reviewed requirements

## Boundaries

Do:

- preserve fresh reviewer context
- ground findings in evidence
- adjudicate reviewer claims before reporting them
- keep review and implementation separate
- disclose when true independent agents are unavailable

Do not:

- auto-trigger this skill
- auto-apply reviewer or resolver output
- grant bypass permissions to reviewer agents
- create reports by default
- invent defects to justify the workflow
- treat consensus between agents as proof without checking the artifact

## Edge Cases

- **Requirements are missing:** ask for them or mark affected conclusions unverified.
- **Artifact is too large:** split it by coherent ownership boundary and preserve cross-boundary risks.
- **Reviewer hallucinates an issue:** decline it with evidence.
- **Reviewer and resolver disagree:** the orchestrating agent adjudicates; unresolved tradeoffs go to the user.
- **Another agent may be editing the same file:** stop before any later write workflow and follow the host project's one-editor rule.

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule
to any user-requested durable verification or resolution record.

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

This skill owns reviewer/resolver execution, confirmed findings, and optional
verification-report content. When a durable report is requested and the skill is
co-invoked with `html-this` or `pdf-this`, save only the requested `.html` or
`.pdf` report unless the user requests multiple formats. Preserve
machine-readable state in its required native format.

Same-stem report variants are one logical artifact and must be updated
consistently. This section overrides Markdown-only optional-report examples only
during a co-invoked format run.

## Validation

After creating or updating this skill:

- confirm only `/subagent-verification-loops` activates it
- confirm reviewer and resolver passes are non-mutating
- confirm product-code and project-contract boundaries remain explicit
- confirm the unavailable-subagent fallback is honestly labeled
- confirm configuration, reviewer prompt, resolver prompt, and report shape remain intact
- validate the folder with the installed `quick_validate.py` in UTF-8 mode
