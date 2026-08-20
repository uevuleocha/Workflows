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

| Parameter            | Default               | Description                                      |
| -------------------- | --------------------- | ------------------------------------------------ |
| `reviewer_model`     | `environment default` | Available model used for the fresh reviewer      |
| `resolver_model`     | `reviewer model`      | Available model used for resolution              |
| `max_loops`          | `1`                   | Review cycles; maximum `2`                       |
| `severity_threshold` | `minor`               | Lowest severity included in proposed corrections |
| `apply_changes`      | `false`               | This skill never applies changes by itself       |
| `durable_report`     | `false`               | Save a report only when explicitly requested     |

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

This skill applies the workspace's first-party durable-artifact provenance rule to any user-requested durable verification or resolution record.

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

This skill owns reviewer/resolver execution, confirmed findings, and optional verification-report content. When a durable report is requested and the skill is co-invoked with `html-this` or `pdf-this`, save only the requested `.html` or `.pdf` report unless the user requests multiple formats. Preserve machine-readable state in its required native format.

Same-stem report variants are one logical artifact and must be updated consistently. This section overrides Markdown-only optional-report examples only during a co-invoked format run.

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

- confirm only `/subagent-verification-loops` activates it
- confirm reviewer and resolver passes are non-mutating
- confirm product-code and project-contract boundaries remain explicit
- confirm the unavailable-subagent fallback is honestly labeled
- confirm configuration, reviewer prompt, resolver prompt, and report shape remain intact
- validate the folder with the installed `quick_validate.py` in UTF-8 mode
