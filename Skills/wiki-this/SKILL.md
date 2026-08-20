---
name: wiki-this
description: Set up a schema-driven plain-markdown wiki in the current workspace. Use when the user invokes /wiki-this, says use wiki-this, make this workspace a wiki, set up a wiki here, initialize the workspace wiki, or asks to establish a new LLM-maintained wiki with declared read-only source roots.
---

# Wiki This

Set up a new, workspace-owned LLM wiki whose taxonomy and page formats are declared by that workspace's own `wiki/wiki-schema.md`.

This skill creates the wiki system. Use `wiki-sync` to maintain it afterward.

## Project Contract

Read and obey the current workspace's canonical contract before doing anything. Its safety, naming, encoding, approval, and direct-edit rules remain in force.

## Invocation

Treat these as direct invocation:

- `/wiki-this`
- `use wiki-this`
- `make this workspace a wiki`
- `set up a wiki here`
- `initialize the workspace wiki`

If `wiki/wiki-schema.md` already exists, do not overwrite it. Explain that the workspace already has a wiki and continue through `wiki-sync` instead. If only part of the scaffold exists, inventory it and repair missing compatible pieces autonomously; stop only when repair would overwrite or contradict established policy.

## Non-Negotiable Boundaries

- Scope is the current workspace root. Do not create a wiki elsewhere.
- Every declared source root is read-only while wearing the wiki-maintainer role: never edit, move, rename, or delete a source.
- The wiki is plain Markdown. Do not create, configure, or require an Obsidian vault; Obsidian may be an optional viewer only.
- Create no `CLAUDE.md`, `AGENTS.md`, or other workspace marker inside `wiki/`.
- Do not assume a universal taxonomy. Page types, folders, and formats must be chosen for this workspace and recorded in its schema.
- Never descend into a nested workspace while inspecting candidate sources.
- **Never infer source roots.** The user must identify every source root explicitly. Workspace inspection may validate named roots, but it may not nominate, add, broaden, or substitute a source root.

## Required Inputs

The source-root list is the one compulsory user decision. The invocation must explicitly name the existing workspace-relative paths that feed the wiki. If it does not, ask exactly one focused question and stop before inspecting candidate content or writing:

```text
Which existing workspace-relative folders should be the wiki's source roots?
I will not infer or add source roots. Once you name them, setup can continue autonomously.
```

After the source roots are supplied, infer the remaining safe design choices and report them after execution rather than pausing for routine approval:

1. Current workspace root.
2. Wiki purpose and primary readers from the workspace contract and named sources.
3. Context-appropriate page types, folders, and formats, including a light-history location and format.
4. No federation by default unless the user or workspace contract explicitly declares one.
5. Track or ignore `wiki/` through the existing wiki-follows-sources rule.
6. Run the initial full `wiki-sync` by default unless the user explicitly requests scaffold-only setup.

Do not create, move, or reorganize source directories. The user's named roots authorize reading those exact roots for wiki setup; they do not authorize inventing another root.

## Setup Workflow

### 1. Resolve and inspect the workspace

- Treat the workspace in which the skill was invoked as the scope root.
- Read its canonical contract and relevant structural documentation.
- Check for an existing `wiki/`, `wiki/wiki-schema.md`, root `CLAUDE.md`, and root `AGENTS.md`.
- Identify nested workspaces by the host workspace's marker rule. At minimum, treat child directories containing canonical agent-contract markers as separate workspaces and exclude their contents from source inspection.
- Validate only the user-named source roots. Inspect enough material inside those exact roots to derive purpose, taxonomy, identity granularity, and page formats; never inspect candidate paths in order to discover additional roots.
- When the established Hub `wiki/wiki-schema.md` is available through the workspace context or as a user-provided reference, read it as a starter example to adapt. Copy its operating concerns, not its workspace-specific roots, taxonomy, folders, or paths. If it is unavailable, do not invent a Hub path or make setup depend on it.

### 2. Derive the autonomous wiki design

After explicit source roots are known, derive and execute a compact design without another routine checkpoint. Record in the schema and report afterward:

- confirmed workspace root and the exact user-supplied source-root list;
- context-appropriate page types, folders, and page formats;
- a light-history location and page format for `wiki-sync`'s automatic historical treatment;
- the structural `wiki/unresolved-verification.md` page and its forward-only rules;
- the `wiki/coverage-contract.json` path and version-1 coverage meanings;
- the `wiki/` tree containing `wiki-schema.md`, `coverage-contract.json`, `unresolved-verification.md`, `index.md`, and `log.md`;
- exact pointer lines added to root `CLAUDE.md` and `AGENTS.md` when those files exist;
- track/ignore behavior derived from wiki-follows-sources; and
- no federation unless explicitly declared.

Derive page types from context. A software wiki, research wiki, book wiki, and business wiki may need different taxonomies. Reuse an established taxonomy only when it fits; never force one merely because another workspace uses it.

Use the Hub schema only as an adaptable example of a complete rulebook. The current workspace and the user's explicit source-root list remain authoritative. If a non-source design choice is merely debatable, choose the smallest compatible default, complete the setup, and report the choice afterward. Stop only when competing interpretations would cause material data exposure, workspace crossing, destructive replacement, or a contradictory schema.

### 3. Create the scaffold

1. Create `wiki/` at the current workspace root.
2. Create `wiki/wiki-schema.md`, `wiki/coverage-contract.json`, `wiki/unresolved-verification.md`, `wiki/index.md`, and `wiki/log.md`.
3. Create only the category folders declared by the derived schema, including its history location.
4. Add the short wiki pointer to root `CLAUDE.md` and `AGENTS.md`. If one is absent, do not invent a replacement marker or create a contract file.
5. Append an `init` entry to `log.md` using the schema's log convention.
6. Apply wiki-follows-sources to `.gitignore` only when that file and edit are inside the authorized workspace scope. Preserve unrelated ignore rules.

`coverage-contract.json` is machine-consumed and carries no agent provenance. It must mirror the schema's exact user-supplied roots, exclusions, nested-workspace markers, identity granularity, wiki path, page globs, structural-page exclusions, provenance field, and path-case policy using version `1`. The schema must name it as the authoritative machine-readable coverage contract.

`unresolved-verification.md` is a structural generated view, not a source of truth and not a checklist the user ticks. Its schema declaration must say that `wiki-sync` maintains it only from new or changed finalized durable artifacts processed after the feature exists. Each entry carries the source artifact path, the owning section, and the unticked item text. An empty page states that no unresolved items have been recorded from forward ingestions.

The schema is the single source of truth for:

- declared source roots;
- read-only role rules;
- workspace scoping and nested-workspace exclusions;
- taxonomy, folder mapping, naming, page formats, and citation rules;
- the history location and light-history page format that `wiki-sync`'s mandatory mine-and-fold plus light-history default requires. Derive one from the current workspace's taxonomy and report it afterward; do not copy a folder name from another workspace;
- index and log conventions;
- federation rules;
- the machine-readable version-1 coverage contract path and meanings;
- the structural unresolved-verification page, forward-only intake rule, and standardized adjacent disposition marker;
- sync, query, and lint behavior supported by this wiki.

### 4. Verify setup

- Confirm all created paths are inside the current workspace.
- Confirm every source path is unchanged.
- Confirm the schema and coverage contract contain exactly the user-supplied source roots and compatible identity rules.
- Confirm the schema declares a history location and light-history page format so `wiki-sync`'s mandatory default is runnable without another checkpoint.
- Confirm the schema declares `unresolved-verification.md`, the page exists, and the coverage contract excludes it from ordinary knowledge-page provenance scanning.
- Confirm `index.md` and `log.md` match the schema.
- Confirm root pointer lines resolve to `wiki/wiki-schema.md`.
- Confirm no workspace marker exists inside `wiki/`.
- Report created files and any deferred decisions.

### 5. Initial sync

Unless the user explicitly requested scaffold-only setup, invoke `wiki-sync` as a separate operation in the same invocation after setup verification. Default to `workspace-full`; preserve any narrower scope or ingest order the user supplied. Internal batching may be selected for quality, but it must remain uninterrupted and must not request a routine checkpoint.

During the initial sync, `wiki-sync` detects historical groups and applies **mine-and-fold + light history** without asking. If it believes a full page would be better, it still completes light treatment and reports the recommendation afterward; only a later explicit user instruction may convert that item. Never hardcode detection to summaries or another folder name, and never invent a history folder outside the schema.

Otherwise stop and hand off with the exact next step.

## Failure Conditions

Stop and report instead of claiming success if:

- a source was changed, moved, renamed, or deleted;
- the workspace root is ambiguous or the user did not explicitly identify the source roots;
- an existing schema would be overwritten;
- the user-supplied roots do not exist, escape the workspace, conflict with each other, or cannot be represented without guessing;
- taxonomy cannot be derived without a material contradiction or unsafe exposure;
- a nested workspace would be traversed;
- a marker file would be placed inside `wiki/`;
- setup created or required an Obsidian vault;
- ingest was truncated or reordered against the user's instruction;
- the completed scaffold lacks the version-1 coverage contract, unresolved-verification declaration, history location, or light-history page format;
- a routine design, manifest, batching, or historical-treatment approval checkpoint was introduced after the user supplied the roots.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.


## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to human-facing wiki pages whose schema permits provenance; never add it to `wiki-schema.md` or another schema-sensitive control file.

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

Report the resolved workspace root, exact user-supplied source roots, derived taxonomy, created scaffold, coverage-contract path, unresolved-verification path, pointer status, wiki-follows-sources choice, source-immutability evidence, and initial-sync result. State any autonomous assumptions and post-run recommendations without turning them into retroactive approval requests.
