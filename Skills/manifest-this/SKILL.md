---
name: manifest-this
description: Create or update an official manifest - a durable, numbered list of things to be edited, updated, deleted, or otherwise dealt with - saved under Archive/Historical/Manifests/ in a Subject category folder with N.) Topic naming and no lifecycle (always historical, like summaries). HTML by default, Markdown-only or both on request; migration skills pass a Markdown default. Use when the user invokes /manifest-this, $manifest-this, use manifest-this, asks to make or update a manifest, asks for an official list of items to edit/update/delete/deal with, or a caller such as a workspace-chat-migration skill needs a manifest created or updated.
---

# Manifest This

Create or update an official manifest: the durable list of record for things a user or agent needs to **edit, update, delete, or deal with**. A manifest names every item, the action it requires, and its current state, so nothing pending is left to memory.

Manifests save directly into `Archive/Historical/Manifests/<Subject>/`. They have **no lifecycle** - like session summaries, they are always historical from the moment they are saved; they never live under `Live/` and never carry pending/active status suffixes.

## Project Contract

Obey the active workspace contract, permissions, UTF-8 requirements, numbering rules, Archive layout, and durable-artifact provenance rules. When co-invoked with `html-this`, that skill owns HTML serialization and provenance rendering; this skill owns content, item grammar, placement, numbering, format selection, and lifecycle language.

## Invocation

Treat these as direct invocation:

- `/manifest-this`, `$manifest-this`, or `use manifest-this`
- `make a manifest of ...`
- `update the manifest`
- `official list of things to edit/update/delete/deal with`
- any calling skill (for example a workspace-chat-migration skill) that needs a manifest created or updated

## What A Manifest Contains

A manifest is an official numbered list. Default content shape:

- a header naming Subject, Topic, and the date;
- one numbered entry per item, each stating:
  - the **item** - what it is (file, setting, artifact, behavior);
  - the **action** required - `Edit`, `Update`, `Delete`, or `Deal with`;
  - the **state** - `Pending`, `In Progress`, `Done`, or `Deferred`;
- a status summary counting items by action and state; and
- Agent Provenance immediately after the opening block, a `Feedback Section` above the change log, and an append-only Agent Change Log as the last section.

Keep the grammar consistent with the calling workflow when one exists (migration skills use `N.) <Platform> <Topic> Manifest`).

## Format Selection

- **HTML by default**, serialized through `html-this`.
- **Markdown-only** when the user asks for "just md", "md only", or similar.
- **Both** when the user asks for both.
- **Caller-supplied default:** when a migration skill invokes this skill, the manifest default is **Markdown**, not HTML - the migration workflow recovers the embedded JSON payload for its execution helper. Any other caller keeps the HTML default unless the user overrides.

## Save Location And Naming

Default directory:

```text
<workspace_root>/Archive/Historical/Manifests/<Subject>/
```

- **Subject** is an unnumbered category folder (for example `Codex`, `Skills`, `Pipeline Alignment`). Reuse an existing Subject folder when one fits; create it when missing and file creation is allowed.
- Manifests always save under `Historical/` - never `Live/`, and never redirected to another folder as a fallback.
- **Filename:** `N.) <Topic>.<ext>`, where `N` is the next integer after the highest existing numbered file in that Subject folder. Deduplicate same-stem format siblings (`N.) Topic.md` + `N.) Topic.html` consume one number) so siblings never inflate the next number.
- **Updates preserve the number**; only the descriptive portion changes to match current scope and state.
- **Never overwrite an existing numbered file.** If the inferred number is occupied, advance to the next available integer and report the value actually used.

## Modes

### Mode A - Create

Resolve Subject, Topic, and the next `N`; build the complete manifest content; select the format (HTML default, or caller/user override); and save exactly one durable artifact unless more than one format was requested. When HTML is requested, co-invoke `html-this` (Mode B) so it owns serialization while this skill owns content, placement, and numbering.

### Mode B - Update

For an existing manifest (same Subject, same number), apply the authorized edits: add or amend entries, move item states, and append a dated change-log entry recording the acting agent, action, and concise scope. Preserve the number and the original writing agent; never rewrite the change log. Regenerate every same-stem format sibling as one atomic artifact set (see **Durable Artifact Format Handling**).

## Caller-Supplied Overrides

A caller - the user directly, or an orchestrating skill such as a migration workflow - may supply Subject, Topic, or Format explicitly. Supplied values are honored; everything not supplied is inferred under the rules above. A supplied Format overrides the default (migration skills supply Markdown). A caller-supplied number never relaxes the no-overwrite rule.

## Embedded Machine Payload

When a manifest has a machine-consumable payload (for example a migration manifest's JSON), embed the **exact native payload** inside the durable artifact:

- **Markdown:** a fenced JSON block carrying the exact payload;
- **HTML:** the `html-this` source packet carries the exact payload.

Before any consumer (for example a migration helper script) runs, **recover the payload to an approved temporary file**, validate it against the manifest schema, give only that temporary file to the consumer, and remove it per the workspace temporary-file policy. Never make the execution consumer read from the durable artifact itself. Backups, databases, transcripts, and app state always remain in their required native formats.

## Availability Guard (html-this)

When the selected format is HTML, confirm `html-this` is present in the agent's loaded skills before writing. If it is NOT available, pause and tell the user:

> The `html-this` skill is not loaded. It is required to serialize the HTML manifest. Please make it available, or tell me to create the manifest as Markdown instead.

Never hand-write the HTML as a silent substitute for `html-this`.

## Agent Provenance For Durable Artifacts

Manifests are first-party durable artifacts. Every manifest must carry:

- exactly one canonical `## Agent Provenance` table immediately after the opening block (its title, status, and lifecycle lines) with rows `Content owner`, `Original writing agent`, `Original writing LLM`, `Created`, and `Artifact role`, in that order;
- an append-only `## Agent Change Log` as the last section (or immediately above any reserved final section), rendered as a five-column `Date and Time | Agent | Model | Action | Scope` table with clock-read `YYYY-MM-DD-HH:mm:ss` timestamps and no backfilled historical rows; and
- exactly one `## Feedback Section` immediately above the change log, present and empty by default, carrying append-only numbered `### Feedback N - date - agent - descriptor` subsections.

`Original writing LLM` names the model that produced the artifact, kept distinct from the agent family that performed the write. Use `Not recorded` when the model is genuinely unknown; never infer it from the agent label and never backfill it.

Preserve the original writing agent; use a stable truthful agent-family label; use `Not recorded` when creator evidence is unavailable. Never inject provenance into operational or machine-consumed files merely because they are durable - an embedded JSON payload keeps its own schema-safe provenance.

## Durable Artifact Format Handling

Read `html-this`'s `references/durable-format-protocol.md` before creating, updating, or converting a format-managed manifest. Same-stem `.md`, `.html`, and `.pdf` files are one logical artifact and consume one number. Update every sibling consistently and stop rather than knowingly splitting their state. When only HTML or PDF exists, that file is the source of record; when Markdown exists it is the normal editable semantic source.

## Deterministic Markdown Table Aligner Integration

When this skill creates or materially edits a file containing Markdown tables, it must invoke the `markdown-table-aligner` skill after semantic content is complete and before final handoff or Markdown-to-HTML/PDF serialization.

**Availability guard.** Confirm `markdown-table-aligner` is loaded before writing the final artifact. If it is unavailable, pause and tell the user that deterministic alignment cannot run; continue with the portable manual rule only if the user explicitly approves that fallback.

For an in-scope Markdown file or staged Markdown source:

1. Run the aligner's read-only `check`.
2. Treat exit `0` as authoritative deterministic monospaced Unicode alignment. Do not reject or rework the table solely because a particular editor, emoji fallback font, or proportional renderer shows a residual pixel-level offset.
3. If exit `1` contains only safe padding findings, run `format` to a distinct nonexistent staged path, review the diff, adopt the staged result, and rerun `check`.
4. If exit `1` contains overflow, malformed, or ambiguous findings, make the editorial repair manually and rerun the helper; the script never chooses truncation text or overflow notes.
5. Exit `2` is an operational failure. Stop rather than falling back silently or treating raw character count as authoritative.
6. Preserve the complete portable Markdown Table Alignment rule below. The helper supplements it and never replaces it.

For HTML or PDF requested from Markdown, run the helper against the exact Markdown source packet before serialization. Chat-only tables continue to use the portable manual rule until block/stdin input is separately implemented.

## Markdown Table Alignment

Every Markdown table this skill writes - inside a durable manifest or into chat - must obey the workspace pipe-alignment rule, carried here so the rule stays portable after global installation:

- **All Markdown tables must be visually pipe-aligned.** Cap every cell at 80 characters, including any overflow marker. If a cell's full content would exceed 80 characters, truncate it at the nearest word boundary within the cap, append a pointer such as `-> see note [row-id]` (using that row's own identifier - its `#`, `Phase`, name, or whichever column already identifies the row), and place the full original text as a plain note directly below the table, keyed by that same identifier. Pad columns so the table is aligned in a monospaced raw-text or Markdown view. Rendered visual alignment is authoritative; raw `|` indices are diagnostic only because Unicode display width (for example emoji, arrows, or wide glyphs) can differ from raw character counts. Do not flag or rework a table solely because raw pipe indices differ when the rendered table is visually aligned. Visibly uneven columns, malformed separators, or cells above 80 characters still fail. This applies to every table an agent writes, not only Estimated Effort tables. **Prefer ASCII-only characters (`->`, `--`, `...`) inside table cells**; Unicode glyphs (arrows, em/en dashes, ellipsis) render wider than one column in most viewers and silently break pipe alignment even when raw character counts match. When a table exceeds approximately 120 characters in total width, narrow the columns (truncate cells to essentials and move detail to notes) so the table renders on a single line without word-wrapping.

**Validation check:** before handoff, review every table produced this run and confirm visual pipe alignment, the 80-character cell cap with overflow pointers, ASCII-only glyphs inside cells, and single-line rendering for wide tables. Misaligned tables are corrected before delivery.

## Verification

Before handoff:

1. Confirm path, Subject, permanent number, topic, and the requested format count.
2. Confirm every entry names its item, action, and state, and the manifest is complete for its stated scope.
3. Confirm provenance and change-log sections are present, correct, and consistent across siblings.
4. Confirm the embedded payload (when present) is the exact native source.
5. For HTML: run `html-this` verification (structure, source packet, provenance table, responsive rendering).
6. Confirm the no-overwrite rule held and the used number is reported.

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

When creating or updating this skill:

- validate the folder-style skill with `quick_validate.py` in Python UTF-8 mode (`-X utf8`);
- smoke-test create with the HTML default, Markdown-only, both formats, and an update that preserves the number;
- smoke-test the migration-context Markdown default override with exact JSON embedding and temporary `.json` recovery;
- confirm the Markdown Table Alignment section and its validation item are present (this skill writes tables); and
- confirm all global copies validate and have recursive byte parity.
