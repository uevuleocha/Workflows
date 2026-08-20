---
name: hermes-workspace-chat-migration
description: "Safely migrate Hermes Desktop chat sessions between workspaces. Use when the user asks to move/reassign Hermes chats, sessions, sidebar project grouping, working directory, or git_repo_root from one local workspace/project to another. Covers the single required state surface: the state.db sessions table (cwd + git_repo_root), with backups, one-session testing, manifests, and verification. No transcript files, no sidecar folders, no separate sidebar index — Hermes groups chats at query time from cwd resolved through project folders."
---

# Hermes Workspace Chat Migration

Migrate Hermes Desktop chat sessions from one workspace to another by rewriting the workspace-binding columns in a single SQLite table.

**Layer 1 — `state.db.sessions.{cwd, git_repo_root}` (PRIMARY — the only layer that must change).**

| Property        | Value                                            |
| --------------- | ------------------------------------------------ |
| **Location**    | `C:\Users\Admin\AppData\Local\hermes\state.db`   |
| **Table**       | `sessions`                                       |
| **Columns**     | Grouping and resume fields -> see note [Columns] |
| **Role**        | Sidebar and resume behavior -> see note [Role]   |
| **Edit method** | Transactional `UPDATE`; `PRAGMA integrity_check` |

Note [Columns]: `cwd` (TEXT) is the grouping signal and resume working directory; `git_repo_root` (TEXT) supplies auto-project fallback grouping.

Note [Role]: `cwd` drives the sidebar group through `project_folders` at query time via `project_tree.py` and sets the resumed working directory. `git_repo_root` is the Tier 2 auto-project fallback when no explicit project folder matches.

That is the entire migration. There are no transcript files to relocate (messages live in `state.db.messages` — never touched), no global-state JSON, no protobuf blobs, no separate sidebar index database, no sidecar folders, and no Electron cache to reset. Hermes is the simplest migration model of all the platforms that have migration skills.

Use this skill only for Hermes Desktop local session/workspace migration. Do not use it to edit project source code.

## Why Both `cwd` and `git_repo_root`

Hermes resolves sidebar grouping in tiers:

1. **Tier 1 — Explicit projects:** `project_tree.py` matches each session's `cwd` against `project_folders.path` by longest-path-prefix. This is the primary grouping signal.
2. **Tier 2 — Auto projects:** sessions not matched by Tier 1 group by `git_repo_root` (the repo root column), or a live git probe of `cwd`.

If only `cwd` is updated, the session will group correctly under Tier 1 (assuming the destination has a matching explicit project folder). But if that project folder is ever removed or the Tier 1 match breaks, the stale `git_repo_root` would send the session to the wrong auto-project group. Updating both columns is free insurance — both tiers agree, and the session is robustly bound to the destination.

## When `git_repo_root` Needs a Different Value Than `cwd`

In most cases, `git_repo_root` should be set to the same value as the destination `cwd`. The exception is when the destination workspace is itself a subfolder of a larger git repo. In that case, `git_repo_root` should point at the actual repo root (the nearest parent containing `.git`), while `cwd` points at the workspace folder.

The front-door workflow discovers the correct `git_repo_root` by checking what other sessions at the destination workspace use, or by probing for `.git`. The manifest carries the discovered value per session. The helper script writes whatever the manifest says — it does not impose a format or guess.

## Required Inputs

Require explicit values before applying changes:

- Source workspace path, for example `C:\Users\Admin\Uzzys Universe\Galaxies\Trading\Uzzy Ecosystem`.
- Destination workspace path, for example `C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem`.
- Session ID(s) to migrate (the session `id`, e.g. `20260707_112356_a9e41b`).
- The destination `git_repo_root` value per session (usually same as destination `cwd`; front-door discovers it).
- Confirmation that Hermes Desktop is fully closed before applying writes.

If the user only provides chat titles, first map titles to session IDs using read-only inspection of `state.db.sessions`. Do not guess when duplicate titles exist.

## Runtime Selection

This skill has two sides. Which side runs depends on the runtime context, not on the model vendor or model family.

- If the skill is being run inside Hermes Desktop / Hermes local runtime, run the **Front-Door Workflow**.
- If the skill is being run by a non-Hermes helper agent while Hermes Desktop is fully closed, run the **Execution Workflow**.

Examples:

- Codex, Claude, Antigravity, or zCode may run the **Execution Workflow** if Hermes is fully closed, even when that helper agent uses a non-Hermes model.
- Hermes itself should not run the **Execution Workflow** against live Hermes state. Hermes should run the **Front-Door Workflow**, prepare the artifacts, and stop before the closed-Hermes execution handoff.

## Safety Rules

- Start with one session when testing a new migration pattern.
- Do not modify any Hermes state while Hermes Desktop is running. The process guard checks for a running `hermes.exe` before apply and is **fail-closed**: if the probe itself fails (exception, timeout, or empty output), the helper stops rather than treating the unknown result as "not running". **The WAL guard refuses *every* non-empty `state.db-wal`, not merely a WAL whose size is changing** — a fixed-size non-empty WAL is still an application's pending work and is equally unsafe.
- Back up every touched file before mutation.
- Back up `state.db` plus its `-wal` and `-shm` sidecars before opening for write.
- Do not globally replace paths across `C:\Users\Admin\AppData\Local\hermes`.
- Edit only structured workspace metadata: the `sessions` row's `cwd` and `git_repo_root`. Do not rewrite `messages.content`, `system_prompt`, or any prose just because it mentions the old path.
- Preserve SQLite format: use transactions, `PRAGMA integrity_check`, and `PRAGMA wal_checkpoint(truncate)`.
- Keep a rollback path by preserving backups.
- Save every backup to the unified backup folder, never scattered next to originals (see **Backup Location**).
- Never touch `projects.db` — no project deletion, no project archive, no `primary_path` updates. Cleanup of dead projects is a separate manual user action, not part of this skill.

## Nested Workspaces

Workspaces are sometimes **nested inside another workspace** — e.g. a hub with sub-workspaces under it. This shape is common in some setups but is **not assumed universal** (this skill may be used anywhere).

Hermes is **structurally immune** to the nested-workspace over-rewrite class: it writes `cwd` and `git_repo_root` to the **exact** destination value (`new`) with an exact idempotency guard (`already_destination`), and never performs prefix arithmetic on the stored path. There is no prefix to double and no suffix to fabricate, so a value already at the destination is recognized and left alone regardless of whether the source and destination are nested or side by side.

## Backup Location

All backups this skill makes — whether written by the helper script's `backup()` or made manually by an agent during a one-session fix — go to a single unified folder under the Hermes directory, grouped per run:

```
C:\Users\Admin\AppData\Local\hermes\user-backups\<run-timestamp>\<original filename>
```

- Equivalent notation: `~/.hermes/user-backups/<run-timestamp>/` (where `~/.hermes` resolves to `C:\Users\Admin\AppData\Local\hermes` on this machine).
- `<run-timestamp>` is one subfolder per migration run, e.g. `hermes-workspace-chat-migration-20260708-143000`.
- Keep the original filename inside that subfolder so a whole run can be deleted as a single unit.
- Rationale: one safe, unified place. When the migration is confirmed, the user can ask an agent to delete a run's subfolder (or the whole `user-backups` folder) — nothing else needs hunting down.
- The helper script does this automatically. When backing up manually, copy into the same `~/.hermes/user-backups/<run-timestamp>/` folder.

## Manifest Storage

Building a manifest when running this skill is encouraged — it keeps a migration explicit and auditable. It is a shared concern: the **Front-Door Workflow** creates the manifest and the **Execution Workflow** consumes it. Save the manifest into the active workspace's `Archive/Historical/Manifests/Hermes/` folder (create it if missing), written workspace-relative so it works for whichever project/working directory the migration targets:

```
$WORKSPACE/Archive/Historical/Manifests/Hermes/
<workspace_root>/Archive/Historical/Manifests/Hermes/
./Archive/Historical/Manifests/Hermes/
```

All three notations mean the same thing: the `Archive/Historical/Manifests/Hermes/` folder of the workspace currently being worked in. The platform folder is determined by the chat platform being migrated, not by the agent performing the work: a Codex or Claude helper executing a Hermes migration still uses the `Hermes` folder. Once a migration is confirmed, the manifest is no longer needed — the user can ask an agent to delete it from there.

Create the manifest through the `manifest-this` skill. `manifest-this` owns the content, the sequential `N.) ` prefix (next integer after the highest existing numbered file in the `Hermes` platform folder), the migration grammar `N.) Who + Topic + What` -> `N.) <Platform> <Topic> Manifest.md` (Title Case with spaces; for example `1.) Hermes Trading Chats Manifest.md`), and the always-historical placement under `Archive/Historical/Manifests/Hermes/`. **The manifest default format for migration skills is Markdown (`.md`), not HTML** - pass the Markdown override to `manifest-this`. The Markdown manifest embeds the exact native JSON payload in a fenced block so the Execution Workflow can recover it. When updating or renaming a staged manifest, preserve its existing sequence number while changing the descriptive portion to match its current scope and state. Do not leave migration manifests unnumbered.

**Availability guard (both workflows).** Before the manifest step, confirm the `manifest-this` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `manifest-this` skill is not loaded. It is required to create or update the migration manifest. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, write the manifest by hand in the same folder with the same naming and grammar, then note in your handoff or feedback summary that the dedicated skill was unavailable.
- Never silently skip the manifest.

When a migration is staged (e.g. one-session test first, then the rest), prefer updating the existing manifest in place through the `manifest-this` skill (update mode) to reflect what is done and what remains, rather than creating a second file, unless the sessions come from more than one source workspace. One source workspace means one manifest.

## Agent Provenance For Durable Artifacts

The migration manifest is a first-party durable artifact and must carry schema-safe agent provenance. `manifest-this` renders the visible Agent Provenance table and append-only Agent Change Log in the manifest artifact; the embedded native JSON payload keeps its own top-level `agent_provenance` object containing `content_owner`, `original_writing_agent`, `original_writing_llm`, `created`, `artifact_role`, and an append-only `change_log`. Each change-log item records the clock-read `YYYY-MM-DD-HH:mm:ss` timestamp, truthful acting agent, that agent's `model`, action, and concise scope. Preserve the original writer and the original writing model permanently.

The helper for this skill accepts additional top-level manifest metadata, but never add provenance to application databases, transcripts, caches, registries, backups, or other migrated operational state. If another manifest consumer has a strict schema that rejects the metadata, keep the native execution manifest unchanged and place provenance in an approved human-readable companion instead.

`session-summary` separately owns provenance for migration handoff and execution summaries. An HTML or PDF rendition must visibly preserve the native manifest's original creator and identify the agent that performed the conversion.

## Durable Artifact Format Handling

This skill owns migration discovery, safety gates, manifest schema, execution, backups, verification, and handoff/feedback scope. When co-invoked with `html-this` or `pdf-this`, pass the requested format to `session-summary` and create only the requested human-readable handoff/feedback format.

The migration manifest is created through `manifest-this`, whose default format for migration skills is Markdown (`.md`) with the exact native JSON embedded in a fenced block. If the user explicitly requests an HTML-only or PDF-only manifest, `manifest-this` embeds the exact JSON through the format skill. Before execution, recover the JSON to an approved temporary `.json`, validate the original manifest schema, and give only that temporary file to the migration helper; remove it afterward per the workspace temporary-file policy. Backups, databases, and app state always remain in their required native formats. Treat same-stem format variants as one manifest.

## Session Summary Integration

Both workflows close by producing an explicit session summary through the `session-summary` skill — not hand-written prose. This skill and `session-summary` are meant to travel together; if you ever share this skill, ship that one with it.

**Availability guard (both workflows).** Before the summary step, confirm the `session-summary` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `session-summary` skill is not loaded. It is required to produce the migration handoff/feedback summary. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, proceed and write a plain markdown summary into the same folder with the same naming, then note in the final feedback summary that the dedicated skill was unavailable.
- Never silently skip the summary.

**Save location and naming (both workflows).** Invoke `session-summary` pre-filled so the user does not have to complete its input template:

- Directory: `<workspace_root>/Archive/Historical/Summaries/Migration/Hermes/`
- Create the `Hermes` platform folder if it does not exist.
- Sequence number: the next integer after the highest existing `N.)` file in the `Hermes` platform folder only.
- Filename templates — the migration grammar `N.) Who + Topic + What`. These override the `session-summary` skill's default filename convention: pre-fill the filename so the output uses this exact shape, with no trailing `Summary N` and no `Execution` wording.
  - Handoff, written by the front-door agent: `N.) <Front-Door Agent> <Topic> Handoff.md` — e.g. `1.) Hermes Trading Chats Handoff.md`
  - Feedback, written by the helper agent: `N.) <Helper Agent> <Topic> Feedback.md` — e.g. `2.) Codex Trading Chats Feedback.md`

**Scope of each summary.** Each side summarizes only its own portion; do not re-summarize the other side beyond referencing the handoff.

- Front-Door (Hermes) summary covers Hermes's portion of the chat: from when migration was first raised, through gathering the user's inputs, read-only discovery, manifest building, and the handoff package — everything Hermes did and gathered and everything the user asked to migrate. It is the handoff to the helper agent.
- Execution (helper agent) summary covers the helper's portion: the Hermes handoff it received, plus everything it did to apply the layer, verify, and (if needed) roll back. It is written so Hermes can review the migration afterward, alongside the user's own visual check.

## Front-Door Workflow

Use this workflow when the skill is started from Hermes Desktop / Hermes local runtime.

This is the native front door of the skill. Hermes uses it to gather user inputs, discover the real session metadata from source-of-truth files, build the manifest and handoff artifacts, and then stop before execution.

### Front-Door Inputs

Collect or confirm these user inputs up front:

- the chat titles, screenshots, or explicit session list the user wants migrated
- the destination workspace path
- any explicit exclusions

Do not ask the user to supply source workspace roots when those can be discovered from Hermes state. The user may know the destination workspace, but Hermes should discover the actual per-session source paths from the stored metadata.

### Front-Door Discovery

For the requested sessions, discover the real values from Hermes's source-of-truth database. Do not infer or guess them. See the **Read-Only Mapping Workflow** below for the step-by-step discovery procedure.

- discover session IDs from `state.db.sessions`
- discover the current `cwd` and `git_repo_root` per session
- discover old workspace roots per session (from `cwd`)
- discover the correct destination `git_repo_root` by checking what other sessions at the destination workspace use, or by probing for `.git`
- discover whether the requested sessions come from one source workspace or multiple source groups
- discover subagent children (`parent_session_id` linking to target sessions) and note them in the manifest for completeness (child rows typically have empty `cwd` and inherit at runtime — no update needed)

Use read-only inspection of:

- `C:\Users\Admin\AppData\Local\hermes\state.db` (open `mode=ro`) — table `sessions`, columns `id`, `title`, `cwd`, `git_repo_root`, `parent_session_id`, `source`
- `C:\Users\Admin\AppData\Local\hermes\projects.db` (open `mode=ro`) — table `projects` (`id`, `name`, `primary_path`, `archived`) and `project_folders` (`project_id`, `path`, `is_primary`) — read-only reference to confirm which explicit project the destination workspace matches

### Front-Door Output

Once discovery is complete:

1. Create the manifest by explicitly invoking the `manifest-this` skill (Markdown default; see **Manifest Storage**), saved under the active workspace's `Archive/Historical/Manifests/Hermes/` folder.
2. Produce the migration handoff summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion, pre-fill the skill's inputs, and save it under `Archive/Historical/Summaries/Migration/Hermes/`. Apply the availability guard if the skill is not loaded.
3. Group sessions by real discovered old workspace when needed. If there are mixed-source sessions, represent them as separate source groups rather than flattening them into one assumed old workspace.

### Front-Door Stop Boundary

The Front-Door Workflow stops after Hermes has:

- gathered the user inputs
- discovered the real session metadata
- built (or updated) the manifest
- built the handoff summary by explicitly invoking the `session-summary` skill (helper-scoped; see **Session Summary Integration**)
- identified the destination workspace and any source groups

At that point, if the migration must touch live Hermes state, Hermes should stop and hand execution to a non-Hermes helper agent that can run while Hermes Desktop is fully closed.

## Read-Only Mapping Workflow

When preparing a batch or front-door package for another agent:

1. Open `C:\Users\Admin\AppData\Local\hermes\state.db` read-only (`mode=ro`) and query the `sessions` table.
2. For each desired chat, select `id`, `title`, `cwd`, `git_repo_root`, `parent_session_id`, `source`.
3. Confirm `cwd` is under the old workspace. Exclude subagent sessions (`source = 'subagent'`) from migration targets unless the user explicitly asks — they inherit `cwd` at runtime from the parent.
4. Determine the destination `git_repo_root`:
   - Query for any existing session whose `cwd` matches the destination workspace and read its `git_repo_root`. If found, use that value.
   - If no reference session exists, probe whether the destination workspace (or its nearest parent) contains a `.git` folder. If yes, use that path. If no `.git` is found, default to the destination workspace path itself (same as `cwd`).
5. Compare each requested title against the screenshot/user list. Exclude chats the user explicitly excludes.
6. Optionally check `projects.db` (read-only) to confirm the destination workspace has a matching explicit project folder — if it does not, warn the user that the session will group under Tier 2 (auto-project) until they create one.
7. Produce a manifest with one entry per session:
   - `title`
   - `id`
   - `old_cwd`, `old_git_repo_root`
   - `new_cwd`, `new_git_repo_root`
   - whether the `sessions` row was found
   - any subagent children (noted for completeness, not migrated)

## Execution Workflow

Use this workflow only when a non-Hermes helper agent is running and Hermes Desktop is fully closed.

The Execution Workflow consumes the manifest and handoff package prepared by the Front-Door Workflow. It performs the real migration writes, verification, and feedback summary generation.

### Pre-flight

Before any write:

1. Confirm Hermes is closed: the **process guard** checks for a running `hermes.exe`. If one is detected, abort — the migration cannot proceed. The guard is fail-closed: if the probe raises or returns unusable output, abort as well; an unknown probe result is never read as "not running".
2. **WAL guard:** the helper refuses **every** non-empty `state.db-wal`, not only a growing one. An empty or absent WAL is safe (Hermes checkpoints on shutdown).
3. **Read-only preflight:** `--dry-run` and the preflight verification always open `state.db` with `mode=ro`; the state DB is never opened for write unless `--apply` is explicitly passed.
4. **Exact manifest before-state:** for every target session, if the manifest declares `old_cwd` or `old_git_repo_root`, the helper reads the live row and hard-fails if the actual values differ — the manifest must match reality before the migration proceeds.
5. **Exact destination state:** after the write, every target row's `cwd` must equal the destination workspace exactly, and `git_repo_root` must equal the per-session `new_git_repo_root` (or the destination workspace if unset). A wrong repo root that happens to match an old path is not accepted as "already_destination".

### Single-Layer Apply Workflow

Only apply after the user or handoff explicitly greenlights execution and Hermes Desktop is closed.

For each target session:

1. Back up `state.db`, `state.db-wal`, and `state.db-shm` (if present) to the unified backup folder before opening for write.
2. Open `state.db` for write. Confirm exactly one `sessions` row exists for the session ID.
3. Rewrite that row's two columns:
   - `cwd` = destination workspace path (raw Windows form, exactly as supplied by the manifest — do not impose a format)
   - `git_repo_root` = destination `git_repo_root` from the manifest (usually same as `cwd`)
4. Use a SQLite transaction; commit; `PRAGMA wal_checkpoint(truncate)`.
5. Run `PRAGMA integrity_check` (must be `ok`).
6. Verify: the target row's `cwd` and `git_repo_root` now equal the destination values, and no target row still holds the old workspace. Non-target rows unchanged (verify with a SHA-256 digest of non-target rows before and after).

### Helper Script

Use `scripts/migrate_hermes_workspace_chat.py` for deterministic migration when available. Prefer `--dry-run` first. The helper consumes the native JSON recovered from the durable manifest into an approved temporary `.json` (see **Durable Artifact Format Handling**); keep the durable Markdown manifest in `Archive/Historical/Manifests/Hermes/` (see **Manifest Storage**).

The helper script belongs to the **Execution Workflow** side. It is not the front door. Hermes may help discover inputs and generate the manifest, but a non-Hermes helper agent should run the script while Hermes Desktop is fully closed.

Expected manifest shape:

```json
{
  "old_workspace": "C:\\Users\\Admin\\Uzzys Universe\\Galaxies\\Trading\\Uzzy Ecosystem",
  "new_workspace": "C:\\Users\\Admin\\Uzzys Universe\\MilkyWay\\Trading\\Uzzy Ecosystem",
  "sessions": [
    {
      "id": "20260707_112356_a9e41b",
      "title": "0.) First of many",
      "new_git_repo_root": "C:\\Users\\Admin\\Uzzys Universe\\MilkyWay\\Trading\\Uzzy Ecosystem"
    }
  ]
}
```

Run modes:

- `--dry-run`: inspect and report intended changes without writing.
- `--apply`: write changes after backups and verification.

### Verification Checklist

After migration and before telling the user it is done:

- **`state.db`:** target `sessions` row has `cwd` and `git_repo_root` equal to the destination values; no target row still holds the old workspace path; `integrity_check` = `ok`; non-target rows unchanged (row count + SHA-256 digest before/after).
- WAL was empty/stale at apply time (WAL guard held).
- **HARD PASS/FAIL GATE — sidebar visibility:** after the user reopens Hermes, the migrated chat MUST appear under the destination project group in the sidebar and stay there after startup settles. If it is still under the old group or missing, the migration is **not done** — see **Failure And Rollback**.
- Confirm the chat opens/resumes normally in the destination working directory.
- User reopens Hermes Desktop and confirms:
  - chat appears under the destination project,
  - chat stays there after startup settles,
  - chat opens/resumes normally and can send/receive a message.

### Execution Feedback

After verification passes and before considering the migration closed, produce an execution feedback summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion: the Hermes handoff it received plus every change it applied, verified, or rolled back. Pre-fill the skill's inputs and save under `Archive/Historical/Summaries/Migration/Hermes/` so Hermes (and the front-door agent) can review it. Apply the availability guard if the skill is not loaded. If the helper updates the manifest (for example marking sessions applied or recording a rollback), do so through the `manifest-this` skill (update mode) so the artifact, its number, and its change log stay consistent.

### Failure And Rollback

If anything fails before a session is fully written, stop and report the failing session ID. **Coordinated backup restoration:** if a post-write verification fails (exact cwd/git_repo_root mismatch, integrity check, or non-target digest drift), the helper automatically restores `state.db` (and its `-wal`/`-shm` sidecars) from the run's backup — the DB returns to pre-migration state in one pass. Only after restoration is confirmed may the operator try a different approach.

**If the migrated chat is absent from the sidebar (or still under the old group) after the writes:** the cause is almost always that the `sessions` row was not fully updated or Hermes was still running at apply time. Diagnose in order:

1. **Re-read the `sessions` row** for the session: are both `cwd` AND `git_repo_root` the destination path? If either still holds the old path, fix and re-verify.
2. **Confirm the write actually committed** — if Hermes was open at apply time, the write may have gone to a WAL that Hermes overwrote, or been blocked. Close Hermes fully and re-apply.
3. **Cross-check against a known-good control** — find a session that IS visible under the destination workspace and confirm its `cwd` matches yours exactly (byte-for-byte, including casing/trailing separators).
4. **Check the explicit project match** — if the destination workspace does not have a matching `project_folders` entry, the session will group under Tier 2 (auto-project by `git_repo_root`). Confirm `git_repo_root` is correct, or ask the user to create an explicit project for the destination workspace.

Do not declare the migration done until the chat is visibly grouped under the destination after a restart.

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
