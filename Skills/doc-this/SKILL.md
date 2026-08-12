---
name: doc-this
description: Create or update durable documentation in the nested Live Documentation tree using a user-selected or context-appropriate category, the workspace house style, and per-Subject numbering. Use when the user invokes /doc-this or asks to create durable documentation.
---

# Doc This

Create or update durable reference, architecture, or how-to documentation in:

```text
<root>\Archive\Live\Documentation\<category>\<Subject>\N.) <Title>.md
```

`doc-this` is a lifecycle-free cousin: documentation is born Live and stays Live. It has no finalizer and no Historical move.

## Project Contract

Follow the workspace's canonical contract. Preserve UTF-8, user data, approval gates, and public-repository safety rules.

## Invocation

Treat these as direct invocation:

- `/doc-this`, `use doc-this`, or `use the doc-this skill`
- `make a documentation file`, `document this`, or `write this up as documentation`
- clear equivalents requesting a durable documentation artifact

If the user wants a plan, task, report, prompt, or summary, route to `plan-this`, `task-this`, `report-this`, `prompt-this`, or `session-summary` respectively.

## Category And Subject

Use any appropriate, unnumbered top-level category. An explicit user-provided category always wins. Otherwise infer a sensible broad category from context; ask only when the category is genuinely ambiguous and a wrong choice would materially affect placement.

Useful defaults and examples include `Personal`, `Resources`, and `Articles`, but they are not an exhaustive allowlist. Do not force an artifact into one of these categories when another category better matches the user's intent.

Then select a broad, reusable Subject folder. Folders are never numbered. Avoid creating a unique Subject for every file.

## House Style

Every document uses:

1. `# <Title>`.
2. `**What this is:**` followed by one orienting paragraph.
3. `---` divider.
4. Topic-appropriate `##` sections, with dividers between major groups when useful.
5. `## One-Line Summary` containing one bold recap paragraph.

Use analogy or for-dummies layering only when the user explicitly requests it.

## Permanent Path And Numbering

- Destination: `Archive\Live\Documentation\<category>\<Subject>\N.) <Title>.md`.
- Subject folders and category folders are never numbered.
- Compute `N` from numbered files in that exact category/Subject folder only, starting at `1` and using one past the highest existing number.
- Never overwrite, renumber, or reclaim an existing document number.
- Before writing, list the target folder and confirm the file you believe holds the highest number actually exists there. Never assert `N` from memory, from an earlier turn, or by analogy to the same document's number in a sibling workspace -- each workspace numbers independently, so one logical document legitimately carries different numbers in different workspaces.
- When closing a numbering gap outside Migration Mode, grep the workspace for references to the old `N.) <Title>` paths and repair them in the same pass; use `git mv` for tracked files so history is preserved.
- `Archive\Live\Reference\` does not exist and must never be used.

## Required Inputs

Infer these from context when safe: title/topic, source material, category, Subject, target workspace (current by default), and optional analogy/for-dummies layering (off by default). Preserve any explicit user-provided category.

## Workflow

1. Determine title, source, category, Subject, and target workspace. Use an explicit user category; otherwise infer a broad category and ask only when a materially important ambiguity remains.
2. Inspect the exact category/Subject folder and calculate the next number.
3. Compose the full draft in house style.
4. Ask how to proceed with an interactive question when available: Draft first (recommended), Make the artifact immediately, or Other.
5. On approval, create the needed unnumbered folders and write the UTF-8 file.
6. Report the category, Subject, assigned number, and path.

If no interactive tool exists, ask the same proceed question in chat and wait. Do not skip this choice unless the user already explicitly instructed immediate creation.

## Legacy Migration Offer

When old documentation exists at top-level `Documentation\` or loose under a flat `Archive\Live\Documentation\`, offer a preservation-first migration:

1. Inventory all files and collision-check `Archive\Live\Documentation\Personal\Legacy\`.
2. Move every pre-existing document into `Personal\Legacy\` as a true move, preserving UTF-8 and content; renumber cleanly `1..n` by prior order only when the migration is authorized.
3. Scan and suggest category/Subject destinations, but let the user approve or edit the mapping before arranging files.
4. Renumber `1..n` within each approved destination and repair affected links.
5. Ask permission before deleting an empty Legacy folder. Never delete a non-empty Legacy folder.

If categorization, order, or a collision is ambiguous, stop rather than guess.

## Boundaries

Do not create a documentation lifecycle/finalizer, write outside `Archive\Live\Documentation\`, use the phantom Reference path, categorize by source against the user's explicit choice, create a unique Subject for every file, overwrite a file, silently reconcile Legacy, or delete Legacy without explicit permission. Do not treat `Personal`, `Resources`, and `Articles` as an exhaustive category allowlist.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

Use the aligner's read-only `check` first. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. For safe padding-only findings, run `format` to a distinct nonexistent staged path, review the diff, adopt it, and rerun `check`. Resolve overflow, malformed, or ambiguous findings manually; stop on operational failure. Confirm the dependency is available before the final write, and never silently replace it with raw character counting. The portable rule below remains compulsory.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable artifact or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.


## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to durable documentation and every later material documentation edit.

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

This skill owns documentation content, category, Subject, title, numbering, location, and update semantics. When co-invoked with `html-this` or `pdf-this`, run this workflow normally but save only the requested `.html` or `.pdf` artifact unless the user requests multiple formats. Keep every required documentation section; hand only serialization and format validation to the format skill.

Same-stem `.md`, `.html`, and `.pdf` siblings are one logical document and one numbering entry. Update all existing siblings together. This section overrides `.md`-only path examples only during a co-invoked format run.

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

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

- confirm a newly produced artifact carries a `## Feedback Section` immediately above its `## Agent Change Log`, present even when empty, using the numbered `### Feedback N` grammar;

After create/update, confirm the expected path exists; the selected or inferred category was honored; category and Subject are unnumbered; numbering is correct within the exact category/Subject folder; house style is intact; no file was overwritten; and UTF-8 was preserved.

After migration, confirm no docs remain loose above category folders, numbering is clean in Legacy/destinations, and before/after inventories match by content.

When updating this skill, run `quick_validate.py` with Python `-X utf8` and keep stdout and stderr separate.
