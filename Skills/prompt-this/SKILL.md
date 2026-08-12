---
name: prompt-this
description: Create or update a durable, structured prompt file with a pending lifecycle, saved under Archive\Live\Prompts\ in a broad Subject folder as "N.) Topic_pending.md" in Title Case, with fixed recognizable headings, a mandatory embedded Prompt Contract, a Verification Checklist, and Parent Plan / Parent Task / Delegation pointers. Also reopens an executed prompt from Historical back to Live, renaming its suffix from _executed back to _pending. Use when the user asks for /prompt-this, prompt-this, make a prompt, create a prompt, update the prompt, save this as a prompt, prompt file, reopen a prompt, or clear equivalents asking for a durable prompt artifact. This skill never finalizes a prompt; finalize-prompt owns that.
---

# Prompt This

Turn the user's request into a **durable, structured prompt file** — one an agent can be handed later and execute without reconstructing intent.

`prompt-this` is the third member of the lifecycle family:

| Artifact | Create / update | Finalize          | Lifecycle          |
|----------|-----------------|-------------------|--------------------|
| Plan     | `plan-this`  | `finalize-plan`   | active → finalized |
| Task     | `task-this`  | `finalize-task`   | pending → done     |
| Prompt   | `prompt-this`   | `finalize-prompt` | pending → executed |

This skill owns **creation, update, and reopen** only. It never marks a prompt executed and never moves a file Live → Historical. That belongs to `finalize-prompt`.

If the user wants a quick prompt "in chat", "in house", or clearly says they do not want a durable file, provide it in chat and state plainly that no file was created.

## Project Contract

This skill operates under the project's canonical contract (e.g. `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`). Safety rules, path scope, and approval gates defined there apply unchanged.

## UTF-8 Rule

Write every prompt file, template, and helper text in UTF-8. Never rely on the Windows default encoding.

## Invocation

Treat these as direct invocation and begin the workflow:

- `/prompt-this`
- `prompt-this`
- `use prompt-this`
- `make a prompt`
- `create a prompt`
- `update the prompt`
- `save this as a prompt`
- `prompt file`
- `reopen that prompt`
- clear equivalents asking for a durable prompt file, a prompt revision, or a reopen

**When not to use this skill:**

- The user wants an implementation plan → `plan-this`.
- The user wants a housekeeping/admin task → `task-this`.
- The user wants documentation → `doc-this`.
- The user wants to **close** a prompt → `finalize-prompt`. Direct them there; do not finalize here.

## Prompt Contract Integration (Mandatory)

Every prompt created or updated with this skill **must** carry a Prompt Contract authored through the `prompt-contracts` skill. This is compulsory at every depth, including compact prompts. This skill and `prompt-contracts` travel together; if you ever share this skill, ship that one with it.

On every create and every update:

1. **Invoke `prompt-contracts`** to author the contract in its canonical structure: GOAL, CONSTRAINTS, FORMAT, DEFINITION OF DONE, FAILURE. Pre-fill it from the prompt's intent, scope, and any related plan/task so the user restates nothing.
   - Standard prompts: full 5-part contract.
   - Compact prompts: the minimal form (GOAL + DEFINITION OF DONE + FAILURE) is acceptable unless the user asks for the full form.
2. **In-chat display is off by default.** Do not paste the Prompt Contract into chat unless the user opts in during creation or later asks to see it. Suppressing chat display never permits an omitted or weakened embedded contract. When the user does opt in, paste the full contract block as an explicit exception to the "do not paste the artifact into chat" rule.
3. **Embed the exact same contract verbatim** into the prompt file under `## Prompt Contract`.
4. **The contract travels with the prompt.** Because it is embedded, the consuming agent already has the scope, the done-criteria, and the failure conditions the moment it opens the file. It never re-derives them.
5. The contract's DEFINITION OF DONE is the authoritative completion gate that `finalize-prompt` checks.

On any later update, re-derive or revise the contract to match the new scope and refresh the `## Prompt Contract` section in the file. Re-show the updated contract in chat only if the user has opted in or asks to see it.

**Availability guard.** Before authoring, confirm `prompt-contracts` is loaded.

- If it is NOT available, pause and tell the user:
  > The `prompt-contracts` skill is not loaded. It is required to author the mandatory Prompt Contract for this prompt. Please make it available, or tell me to continue without it.
- If the user insists, produce the 5-part contract inline from the known format, embed and show it the same way, and note in the final report that the dedicated skill was unavailable.
- Never silently skip the Prompt Contract.

---

## Directory Layout and Lifecycle

A prompt's lifecycle is expressed by **location, an in-file `Status:` line, and a filename suffix** — the suffix is `_pending` while the prompt is Live and `_executed` once it is finalized.

```text
Pending:   <Workspace>\Archive\Live\Prompts\<Subject>\N.) <Topic>_pending.md
Executed:  <Workspace>\Archive\Historical\Prompts\<Subject>\N.) <Topic>_executed.md
```

- `<Workspace>` is the **active workspace root**. If `Archive\Live\Prompts\` does not exist, create it when file creation is allowed. Never hardcode a specific machine's path.
- **Subject** is the broad category — the school-subject sense ("math"). **Subject folders are never numbered.** Keep Subjects deliberately broad so you do not end up with one folder per file.
- **Topic** is the specific thing ("polynomials"). It becomes the filename Topic, ahead of the `_pending` suffix.
- Only `finalize-prompt` moves a prompt Live → Historical, changes PENDING → EXECUTED, or renames the suffix `_pending` → `_executed`. **There is no manual move/finalization fallback.**
- `prompt-this` may move a prompt Historical → Live, but only as a deliberate **reopen** (see `Reopen Behavior`).

### The `N.)` number

**`N` is lifecycle-agnostic and permanent.**

Use an explicit **pre-write snapshot**. Do not recompute the maximum after the file exists.

1. **Before writing**, scan **both** matching Subject folders — Live and Historical — and record the highest existing numeric prefix as `previous_max`. Use `0` when neither side has a numbered file.
2. Assign **`N = previous_max + 1`**.
3. **Before writing**, confirm no existing file across the combined Subject namespace already owns `N`.
4. **After writing**, confirm the new file carries `N`, that `N` equals the captured `previous_max + 1`, and that no *second* file across Live and Historical owns that number.

> **Why the snapshot.** Once the new file exists it is part of the union, so recomputing `max(Live ∪ Historical)` returns `N` itself — and `max + 1` would wrongly demand `N + 1`. Capture `previous_max` before the write and validate against the captured value, never against a fresh maximum.

> **Why both sides, and why two levels deep.** Scanning only the Live side silently reuses a number already held by an executed prompt that has moved to Historical. And because the Subject layer makes the tree two levels deep, a top-level listing of `Archive\Live\Prompts\` returns folder names and **zero** `.md` files — you must descend into the Subject folder on **both** sides.

Assign `N` once. Never reclaim gaps. Never renumber during finalization or reopen.

### Filename shape

```text
N.) <Topic>_pending.md
```

- **Title Case with spaces for the Topic**, matching the workspace's existing prompt files. Only the lifecycle suffix (`_pending`) keeps its underscore form.
- **The filename Topic must not contain the word "prompt".** The `Prompts\` folder already says what it is. Plans do not say "plan"; tasks do not say "task".
  - **Exception:** if the user explicitly intends to share this prompt publicly, they may opt in to including "prompt" in that one filename. Never the default.

---

## Subject and Topic Resolution

Do not present blank fields, and do not interrogate the user. **Infer first, then confirm.**

1. List the existing Subject folders under `Archive\Live\Prompts\` and `Archive\Historical\Prompts\`.
2. Choose the best-matching existing Subject, or propose a new **broad** one when nothing fits.
3. Derive the Topic from the request.
4. Capture `previous_max` across **both** Subject folders and set `N = previous_max + 1` (see `The N.) number`). Confirm nothing already owns `N`.
5. Present the pre-filled block and let the user green-light it whole or overwrite one line:

```text
Here are my inferred values — green-light to use them as-is, or change any single line:

1. Subject: [inferred, or `NEW: <proposed broad Subject>`]
2. Topic:   [inferred]
3. Number:  [N = previous_max + 1] (previous_max captured across Live + Historical)
4. Path:    <Workspace>\Archive\Live\Prompts\[Subject]\[N].) [Topic]_pending.md
5. Depth:   Standard | Compact
```

If the user says to skip the template, infer and proceed. If a value is genuinely uninferable (rare), mark that one line `[unable to infer - please provide]` and pre-fill the rest.

---

## Required Structure

Every prompt this skill produces carries the **same** structure. This is the recognizability signature: a reader must identify a `prompt-this` artifact on sight.

Use `references/prompt-template.md` as the canonical shape. Do not reconstruct the headings from memory.

Mandatory in every prompt, standard or compact:

- `Status:` and `Prompt lifecycle:` header lines
- `## What This Prompt Is`
- `## Prompt`
- `## Context` — with **all three** fields present: `Parent Plan`, `Parent Task`, `Delegation`. Use `N/A` when a field does not apply. Never delete a field.
- `## Instructions`
- `## Prompt Contract`
- `## Verification Checklist`

`## Notes` is optional and is the **only** section a compact prompt may omit.

**Four distinct purposes. Keep them distinct:**

| Section                     | Purpose                                      |
|-----------------------------|----------------------------------------------|
| `## Prompt`                 | The executable payload, verbatim             |
| `## Instructions`           | How to run it: preconditions, inputs, safety |
| `## Prompt Contract`        | What success and failure mean                |
| `## Verification Checklist` | How success was actually evidenced           |

Do not collapse them. Do not let the contract substitute for the checklist: the contract *defines* success, the checklist *records* it.

**No `Estimated Effort` table.** The siblings mandate one; prompts do not. The Prompt Contract and Verification Checklist provide the execution controls without turning every prompt into a plan.

### The Delegation pointer

Every prompt carries `**Delegation:** N/A` under `## Context`.

It is a **pointer, and nothing more.** If the prompt belongs to a formal delegation, `delegate-this` or the orchestrator fills it. This skill contains no routing logic, no assignment-packet schema, no platform list, no subagent workflow, and **no dependency on `delegate-this` being loaded.**

---

## Create vs Update vs Reopen

**Create** when no matching pending prompt exists, the user asks for a new one, or the request is clearly separate.

**Update** when the user references an existing pending prompt, or says revise / continue / extend / add to it.

**Reopen** when the user explicitly asks to revise, extend, rerun, or reopen an **executed** prompt.

**Ask before writing** when multiple pending prompts plausibly match, or when create-vs-update is genuinely ambiguous.

### Update mode

- Preserve the existing prompt's structure and wording.
- Refresh the `## Prompt Contract`; re-show it in chat only if the user has opted in.
- Update `## Verification Checklist` items only when evidence supports it.
- Never rename the file, renumber `N`, or move it.

### Reopen Behavior

An executed prompt is **not** reopened merely because the user mentions it. The user must ask for new work or a revision.

When reopening:

1. Move the file from `Archive\Historical\Prompts\<Subject>\` back to the matching `Archive\Live\Prompts\<Subject>\`.
2. **Preserve `N.)` and the Topic exactly, and rename the suffix `_executed` → `_pending`.** No renumbering.
3. Preserve all prior execution evidence. Do not erase the executed history.
4. Restore the status and lifecycle lines to `PENDING ⌛` / `REOPENED`, keeping the earlier executed dates visible.
5. Add a dated reopen note under `## Notes`.
6. **Stop on a Live collision.** If a file with that `N.)` already exists on the Live side, do not overwrite, do not renumber — report it and ask.
7. Leave re-finalization for a later explicit `finalize-prompt` pass.

---

## Boundaries

Do:

- create only under `<Workspace>\Archive\Live\Prompts\<Subject>\`
- compute `N` across **both** Live and Historical for the Subject, and assign it once
- keep Subject folders unnumbered and broad
- infer Subject/Topic and present a pre-filled block for confirmation
- author the Prompt Contract through `prompt-contracts` and embed it verbatim; show it in chat only on user opt-in
- retain every mandatory section and all three `## Context` fields
- preserve `N.)` and the Topic, rename the suffix `_executed` → `_pending`, and preserve prior history on reopen
- stop on any path collision

Do not:

- finalize a prompt, mark it EXECUTED, or move it Live → Historical — that is `finalize-prompt`
- offer or perform a manual move/finalization fallback under any circumstance
- put the word "prompt" in the filename, unless the user opts in for public sharing
- number a Subject folder, renumber `N`, or reclaim a gap
- scan only the Live side, or only the top level, when computing `N`
- add an `Estimated Effort` table
- copy delegation routing, packets, platforms, or subagent logic into this skill
- require a parent plan, parent task, or delegation to exist
- silently infer that a prompt was executed from its age or location
- paste the whole prompt file into chat (show the Prompt Contract only when the user opts in or asks to see it)

---

## Agent Provenance For Durable Artifacts

This skill applies the workspace's first-party durable-artifact provenance rule to durable prompt artifacts and every later prompt revision.

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

This skill owns prompt structure, Prompt Contract, Verification Checklist, Subject, permanent number, path, update/reopen behavior, and lifecycle. When co-invoked with `html-this` or `pdf-this`, run the full prompt workflow and save only the requested `.html` or `.pdf` artifact unless the user requests multiple formats. Preserve every canonical template heading and lifecycle field; hand only serialization to the format skill.

Treat same-stem `.md`, `.html`, and `.pdf` variants as one prompt and one numbering entry. Update or reopen the complete sibling set together. This section overrides `.md`-only extension examples only during a co-invoked format run; `_pending`/`_executed` ownership remains unchanged.

## Checklist Tick Discipline

**Checklist Tick Discipline.** The executing agent ticks every DEFINITION OF DONE and Verification Checklist box its own evidence supports, in the same pass, and states the evidence for each. Leave a box unticked only when the claim is false, unevidenced, or ambiguous — and say which and why. An unticked box means "not done," never "done but awaiting someone else's confirmation." Independent verification re-checks the ticks; it does not supply them. A tick asserts what this pass did and evidenced; it does not assert that the result is proven correct in later production use.

This rule is **emitted into** every artifact this skill produces, adjacent to the DEFINITION OF DONE or Verification Checklist it governs — not buried in a trailing notes section. The executing agent must read it inside the artifact it was handed, without consulting any workspace contract.

## No Invented Sync Constraints

**No Invented Sync Constraints.** Do not write "local master only," "no global sync in this pass," or any equivalent prohibition into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, FAILURE condition, or instruction unless the user asked for it. Sync authority belongs to the user and is granted at execution time, not predicted at authoring time. When the user later authorizes same-pass sync, an invented constraint turns a correct action into a permanently false checklist item that must be waived. If sequencing genuinely matters, express it as a default the user can override — "stop at the verified local master unless the user authorizes same-pass sync" — never as a completion criterion or failure condition.

This rule binds the authoring agent; it is **never** emitted as artifact text. Its presence is verified by the absence of invented sync constraints in produced artifacts, not by a section in them. It does not authorize syncing and does not change what counts as authorization.

## Non-Blocking Wiki And Git Items

**Non-Blocking Wiki And Git Items.** Do not write a wiki sync, a `stage-commit-push` run, a GitHub push, or a submodule pointer bump into a DEFINITION OF DONE item, Verification Checklist item, CONSTRAINT, or FAILURE condition as a completion criterion. Those operations belong **after** the artifact is finalized: finalization renames and moves the artifact, so syncing first dirties the repository again and leaves the wiki holding a synthesised copy of a path that no longer exists. If such an operation is genuinely worth recording, record it as an explicitly non-blocking follow-up — "after finalization, run `stage-commit-push`" — never as a box whose blank state blocks closure. A finalizer must never refuse or defer closure because a sync, push, or pointer bump has not happened.

**The carve-out.** This does not apply to an artifact **whose subject is** the wiki or Git work. A plan to build `wiki-sync` legitimately carries wiki items in its DEFINITION OF DONE, because there the wiki work *is* the deliverable rather than a publication step for it. The rule targets publication steps, not subject matter. Never strip a legitimate item from an artifact that is correct as written.

Like rule 2, this binds the authoring agent and is never emitted as artifact text.

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

## Exact Model Attribution

Whenever this skill writes a new model identity, appends a current-run model value, or defines a workflow that does either:

- Record the full model identity actually used when it is safely available from current runtime or session metadata. Use a specific identity such as `GPT-5.6 Sol`, `GPT-5.6 Terra`, or `Claude Opus 5`; a family-only label such as `GPT-5`, `Claude`, or `Codex Agent` is not an acceptable substitute.
- Resolve identity in this order: current runtime or session metadata; a platform-provided current-model field; only then, when unavoidable, a field-minimized configuration lookup that returns the model field alone. Apply `tread-lightly` to any potentially sensitive configuration and never display, copy, search, diff, or log the whole configuration.
- Keep the agent family and model identity separate. Never infer an exact model from an agent label, provider name, stale configuration, or model family.
- Use `Not recorded` only when the exact identity genuinely cannot be established safely. Do not replace an available exact identity with `Not recorded` merely to avoid checking current runtime metadata.
- Preserve append-only history. Never rewrite a historical provenance or change-log value solely to improve an old model label; add a truthful current correction entry when correction is required.

**Validation check:** For every model value newly written in the current run, accept a full exact identity and the honest `Not recorded` fallback, but reject known ambiguous family-only labels or agent-family substitutions. Confirm model discovery exposed only the required model field and that no historical row was rewritten.

## Validation

- confirm the `## Markdown Table Alignment` section and its validation check are present, and that every table this skill wrote is visually pipe-aligned with cells at 80 characters or fewer and ASCII-only glyphs inside cells;

- confirm the `## Checklist Tick Discipline` section is present and its rule text is unmodified;
- confirm the `## No Invented Sync Constraints` section is present, and that a produced artifact contains **no** invented sync constraint in its DEFINITION OF DONE, Verification Checklist, CONSTRAINTS, or FAILURE sections;
- confirm a newly produced artifact actually carries the Checklist Tick Discipline rule verbatim, since the section can survive in this skill while the template silently loses it;
- confirm the `## Non-Blocking Wiki And Git Items` section is present with its carve-out, and that a produced artifact contains **no** wiki-sync, push, `stage-commit-push`, or pointer-bump completion criterion;
- confirm a newly produced artifact carries a `## Feedback Section` immediately above its `## Agent Change Log`, present even when empty, using the numbered `### Feedback N` grammar;

After creating, updating, or reopening a prompt, confirm and report:

- the file exists at `<Workspace>\Archive\Live\Prompts\<Subject>\N.) <Topic>_pending.md`
- the Subject folder is unnumbered; the filename carries the `N.) ` prefix and the `_pending` suffix
- on create: the new file carries `N`, `N` equals the **captured `previous_max + 1`** (never a maximum recomputed after the write), and no second file across Live and Historical owns that number
- on update or reopen: `N` is **unchanged**
- the filename does not contain "prompt" (unless the user opted in for sharing)
- `Status:` and `Prompt lifecycle:` lines are present
- `## What This Prompt Is`, `## Prompt`, `## Context`, `## Instructions`, `## Prompt Contract`, and `## Verification Checklist` are all present
- `## Context` retains Parent Plan, Parent Task, and Delegation, using `N/A` where empty
- the Delegation field is a pointer only — no routing, packet, platform, or subagent text entered the file
- the Prompt Contract was authored via `prompt-contracts` (or the guard fired and was reported), is embedded verbatim, and was pasted into chat only if the user opted in
- no `Estimated Effort` table was added
- on reopen: the suffix was renamed `_executed` → `_pending`, prior execution evidence is preserved, a dated reopen note was added, and no collision was overwritten
- UTF-8 was used; any Markdown table is pipe-aligned with every cell at 80 characters or fewer

Report the file path and summarize the change. Do not paste the entire prompt into chat.

When creating or updating this skill itself, validate the folder-style skill with the `quick_validate.py` script that ships with your skill-creator install, running Python in UTF-8 mode (`-X utf8`). Read the result from the exit code with stdout and stderr captured **separately**: exit `0` is valid; exit `1` with empty stderr is invalid; exit `1` with non-empty stderr means the validator crashed and validity is unknown. Never merge the streams.
