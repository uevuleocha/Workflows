---
name: zcode-workspace-chat-migration
description: "Safely migrate zCode (Z.ai) chat sessions between workspaces. Use when the user asks to move/reassign zCode chats, sessions, sidebar project grouping, working directory, or recent-projects entries from one local workspace/project to another. THE sidebar grouping key is v2/tasks-index.sqlite table tasks fields workspace_key, workspace_path, and meta_json.workspacePath (zCode's equivalent of Codex's state_5.sqlite threads). It is NOT db.sqlite. SECONDARY: cli/db/db.sqlite session.{directory,path,project_id} (resume working dir + persistent identity). CLEANUP/PARITY: v2/setting.json picker, db.sqlite message.data per-turn context, Local Storage cache. With zCode fully closed, back up each DB (+ -wal/-shm), rewrite the tasks-index row (moves the sidebar) and the session row (resume dir), integrity_check, reopen to confirm. NO message-send and NO source-folder deletion are required (those were disproven). Includes backups, one-session testing, manifests, and verification."
---

# zCode Workspace Chat Migration

Migrate zCode (Z.ai) chat sessions from one workspace to another by rewriting the workspace-binding fields in two SQLite databases. **The sidebar grouping key lives in `tasks-index.sqlite`, not `db.sqlite`** — this was proven the hard way (see the note at the end of this section).

1. **PRIMARY — `C:\Users\Admin\.zcode\v2\tasks-index.sqlite`, table `tasks` (THE sidebar grouping key).** Each chat is one row, keyed by `task_id` = the `sess_<uuid>` id. The sidebar groups the chat under **`workspace_path`** and labels it with `title`. Three fields carry the workspace and must all be rewritten together:
   - `workspace_path` — raw destination workspace path. **This is what the sidebar groups by.**
   - `workspace_key` — same raw path (zCode's key form; equals `workspace_path` on this install).
   - `meta_json` — a JSON string; rewrite its embedded `"workspacePath"` value.
   - This DB is zCode's equivalent of **Codex's `state_5.sqlite threads`** table. It has a live ~1.7 MB WAL while zCode runs (WAL guard applies). Leaving these on the old path is what keeps a chat hidden/misgrouped even after every `db.sqlite` edit.
2. **SECONDARY — `C:\Users\Admin\.zcode\cli\db\db.sqlite`, table `session` (resume working dir + persistent identity).** Each chat is one row. Rewrite all three, derived from the same source path:
   - `directory` — raw workspace path (the working directory the chat resumes in).
   - `path` — duplicate of `directory`.
   - `project_id` — deterministic transform: `"proj_" + path.lower()`, then **drop `:`** (not dash — so `C:\Users` → `c-users`, single dash), and replace every `\` and space with `-`.
   - ⚠️ This row is necessary for the chat to *open* in the correct folder, but it does **NOT** drive sidebar grouping. Rewriting it alone leaves the chat hidden — that is the trap that cost a multi-round investigation.
3. **CLEANUP / PARITY — `C:\Users\Admin\.zcode\v2\setting.json`.** `recentProjects[]` and `lastWorkspaceSession[].workspacePath` — the start-screen "Recent Projects" picker. Rewrite stale strings for cleanliness.
4. **CLEANUP / PARITY — `db.sqlite` `message` table `data` JSON.** Per-turn workspace context: `data.path.cwd`/`data.path.root` (assistant turns) and `data.contextSnapshot.envInfo.cwd` (user turns). Rewriting these makes the migrated session byte-identical to a native destination session, but they are not the grouping key. Edit only these structured fields, never message prose (prose lives in the `part` table — do not touch).
5. **CLEANUP / PARITY — Electron `Local Storage` leveldb.** A UI cache that regenerates from the DBs; the helper soft-resets it on `--apply` by moving the whole folder into the run backup so stale per-path drafts/history do not linger.

Use this skill only for zCode local session/workspace migration. Do not use it to edit project source code.

> **Hard-won correction (2026-07-07).** Earlier versions of this skill claimed the grouping key was `session.project_id` (Layer 1), then a "Local Storage cache" (Layer 3), then a "runtime binding fixed by opening the workspace and sending a message" (Layer 4). **All three were wrong.** A control-group differential (two sessions with identical `db.sqlite` rows, one visible and one hidden) proved the only difference was `tasks-index.sqlite`. There is **no** required "send a message" step and **no** need to delete the source folder first — keep the source until after migration, as with every other platform. Rewrite the `tasks-index.sqlite` row (and the `db.sqlite session` row for the resume dir) with zCode closed, and the chat moves.

## Required Inputs

Require explicit values before applying changes:

- Source workspace path, for example `C:\Users\Admin\Uzzys Universe\Galaxies\Trading\Uzzy Ecosystem`.
- Destination workspace path, for example `C:\Users\Admin\Uzzys Universe\MilkyWay\Trading\Uzzy Ecosystem`.
- Session ID(s) to migrate (the `sess_<uuid>` id, which is also the rollout filename stem).
- Confirmation that zCode is fully closed before applying writes (the WAL guard covers **both** `tasks-index.sqlite` and `db.sqlite`).

> **Retired requirements (do NOT ask for these — they were based on disproven theories):** ~~deletion of the old workspace folder before reopening~~ and ~~a "send one message to re-bind" step~~. Neither is needed. The source folder should be kept until after the migration is confirmed, exactly as with the other platforms. Local Storage is not the grouping key, but the helper soft-resets it during `--apply` as cleanup/parity hygiene.

## Runtime Selection

This skill has two sides. Which side runs depends on the runtime context, not on the model vendor or model family.

- If the skill is being run inside zCode / Z.ai local runtime, run the **Front-Door Workflow**.
- If the skill is being run by a non-zCode helper agent while zCode is fully closed, run the **Execution Workflow**.

Examples:

- Codex, Claude, Antigravity, or Hermes may run the **Execution Workflow** if zCode is fully closed, even when that helper agent uses a non-Z.ai model.
- zCode itself should not run the **Execution Workflow** against live zCode state. zCode should run the **Front-Door Workflow**, prepare the artifacts, and stop before the closed-zCode execution handoff.

## Safety Rules

- Start with one session when testing a new migration pattern.
- Do not modify any zCode state while zCode is running. Abort if `db.sqlite-wal` or `tasks-index.sqlite-wal` is being actively written at apply time (the WAL guard).
- Back up every touched file before mutation.
- Do not globally replace paths across `C:\Users\Admin\.zcode`.
- Edit only structured workspace metadata fields: the `tasks` row's `workspace_key`, `workspace_path`, and `meta_json.workspacePath`; the `session` row's `directory`, `path`, and `project_id`; `setting.json` path strings; and structured `message.data` cwd/root fields. Do not rewrite user/assistant prose, message content, `part` rows, or rollout transcript records just because they mention the old path.
- Preserve on-disk format: SQLite transactions with `PRAGMA integrity_check`; JSON validity; UTF-8 encoding; preserve BOM/no-BOM state where relevant.
- Keep a rollback path by preserving backups.
- Save every backup to the unified backup folder, never scattered next to originals (see **Backup Location**).

## Backup Location

All backups this skill makes — whether written by the helper script's `backup()` or made manually by an agent during a one-session fix — go to a single unified folder under the zCode directory, grouped per run:

```
C:\Users\Admin\.zcode\user-backups\<run-timestamp>\<original filename>
```

- Equivalent notation: `~/.zcode/user-backups/<run-timestamp>/`.
- `<run-timestamp>` is one subfolder per migration run, e.g. `zcode-workspace-chat-migration-20260706-233000`.
- Keep the original filename inside that subfolder so a whole run can be deleted as a single unit.
- Rationale: one safe, unified place. When the migration is confirmed, the user can ask an agent to delete a run's subfolder (or the whole `user-backups` folder) — nothing else needs hunting down.
- The helper script does this automatically. When backing up manually, copy into the same `~/.zcode/user-backups/<run-timestamp>/` folder.

## Manifest Storage

Building a manifest when running this skill is encouraged — it keeps a migration explicit and auditable. It is a shared concern: the **Front-Door Workflow** creates the manifest and the **Execution Workflow** consumes it. Save the manifest into the active workspace's `Archive/Manifests/zCode/` folder (create it if missing), written workspace-relative so it works for whichever project/working directory the migration targets:

```
$WORKSPACE/Archive/Manifests/zCode/
<workspace_root>/Archive/Manifests/zCode/
./Archive/Manifests/zCode/
```

All three notations mean the same thing: the `Archive/Manifests/zCode/` folder of the workspace currently being worked in. The platform folder is determined by the chat platform being migrated, not by the agent performing the work: a Codex or Claude helper executing a zCode migration still uses the `zCode` folder. Once a migration is confirmed, the manifest is no longer needed — the user can ask an agent to delete it from there.

Every manifest saved in `Archive/Manifests/zCode/` must start with the next sequential `N.) ` prefix based only on the highest existing numbered file in that platform folder. Use `N.) <descriptive-manifest-name>.json`; for example, `1.) zcode_galaxies_to_milkyway_manifest.json`. When updating or renaming a staged manifest, preserve its existing sequence number while changing the descriptive portion to match its current scope and state. Do not leave migration manifests unnumbered.

When a migration is staged (e.g. one-session test first, then the rest), prefer updating the existing manifest in place to reflect what is done and what remains, rather than creating a second file, unless the sessions come from more than one source workspace. One source workspace means one manifest.

## Session Summary Integration

Both workflows close by producing an explicit session summary through the `session-summary` skill — not hand-written prose. This skill and `session-summary` are meant to travel together; if you ever share this skill, ship that one with it.

**Availability guard (both workflows).** Before the summary step, confirm the `session-summary` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `session-summary` skill is not loaded. It is required to produce the migration handoff/report summary. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, proceed and write a plain markdown summary into the same folder with the same naming, then note in your final report that the dedicated skill was unavailable.
- Never silently skip the summary.

**Save location and naming (both workflows).** Invoke `session-summary` pre-filled so the user does not have to complete its input template:

- Directory: `<workspace_root>/Archive/Summaries/Migration/zCode/`
- Create the `zCode` platform folder if it does not exist.
- Sequence number: the next integer after the highest existing `N.)` file in the `zCode` platform folder only.
- Filename: the `session-summary` convention `x.) [Project] [Topic] Summary [N].md`.

## Front-Door Workflow

Use this workflow when the skill is started from zCode / Z.ai local runtime.

This is the native front door of the skill. zCode uses it to gather user inputs, discover the real session metadata from source-of-truth files, build the manifest and handoff artifacts, and then stop before execution.

### Front-Door Inputs

Collect or confirm these user inputs up front:

- the chat titles, screenshots, or explicit session list the user wants migrated
- the destination workspace path
- any explicit exclusions

Do not ask the user to supply source workspace roots when those can be discovered from zCode state. The user may know the destination workspace, but zCode should discover the actual per-session source paths from the stored metadata.

### Front-Door Discovery

For the requested sessions, discover the real values from zCode's source-of-truth files. Do not infer or guess them. See the **Read-Only Mapping Workflow** below for the step-by-step discovery procedure.

- discover session IDs
- discover the current `directory`, `path`, and `project_id` per session
- discover old workspace roots per session (from `directory`)
- discover whether the requested sessions come from one source workspace or multiple source groups
- discover whether the destination path exists on disk (it should — the rename must have happened first)

Use read-only inspection of:

- `C:\Users\Admin\.zcode\cli\db\db.sqlite` (open `mode=ro`) — table `session`, columns `id`, `title`, `directory`, `path`, `project_id`
- `C:\Users\Admin\.zcode\v2\setting.json` — `recentProjects` and `lastWorkspaceSession`

### Front-Door Output

Once discovery is complete:

1. Save (or update in place) a sequentially numbered `N.) ` manifest under the active workspace's `Archive/Manifests/zCode/` folder.
2. Produce the migration handoff summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion, pre-fill the skill's inputs, and save it under `Archive/Summaries/Migration/zCode/`. Apply the availability guard if the skill is not loaded.
3. Group sessions by real discovered old workspace when needed. If there are mixed-source sessions, represent them as separate source groups rather than flattening them into one assumed old workspace.

### Front-Door Stop Boundary

The Front-Door Workflow stops after zCode has:

- gathered the user inputs
- discovered the real session metadata
- built (or updated) the manifest
- built the handoff summary by explicitly invoking the `session-summary` skill (helper-scoped; see **Session Summary Integration**)
- identified the destination workspace and any source groups

At that point, if the migration must touch live zCode state, zCode should stop and hand execution to a non-zCode helper agent that can run while zCode is fully closed.

## Read-Only Mapping Workflow

When preparing a batch or front-door package for another agent:

1. Open `C:\Users\Admin\.zcode\cli\db\db.sqlite` read-only (`mode=ro`) and query the `session` table.
2. For each desired chat, select `id`, `title`, `directory`, `path`, `project_id`.
3. Confirm `directory`/`path` are under the old workspace.
4. Compute the destination `project_id` from the destination path: `"proj_" + path.lower()`, then drop `:` (not dash), and replace every `\` and space with `-` (e.g. `C:\Users\Admin\Uzzys Universe` → `proj_c-users-admin-uzzys-universe`). The helper script's `compute_project_id()` encodes this exactly.
5. Compare each requested title against the screenshot/user list. Exclude chats the user explicitly excludes.
6. Read `setting.json` and note which `recentProjects` and `lastWorkspaceSession` entries are stale (under the old path).
7. Produce a manifest with one entry per session:
   - `title`
   - `id`
   - `old_directory`, `old_project_id`
   - `new_directory`, `new_project_id`
   - whether the `session` row was found
   - the list of stale `setting.json` entries to rewrite.

## Execution Workflow

Use this workflow only when a non-zCode helper agent is running and zCode is fully closed.

The Execution Workflow consumes the manifest and handoff package prepared by the Front-Door Workflow. It performs the real migration writes, verification, and reporting.

### Pre-flight

Before any write:

1. Confirm zCode is closed: check that `C:\Users\Admin\AppData\Roaming\zcode\lockfile` is stale or absent, and that no zCode process is running.
2. **WAL guard:** open the DBs read-only and confirm the target rows exist. If `db.sqlite-wal` **or** `tasks-index.sqlite-wal` is being actively written (modification time advancing), abort — zCode is still running. Both DBs carry a live WAL while zCode is open.

### Step 1 (PRIMARY): `v2/tasks-index.sqlite`, table `tasks` — THE grouping key

This is the edit that actually moves the chat in the sidebar. For each target session (`task_id` = the `sess_<uuid>` id):

1. Back up `tasks-index.sqlite`, `tasks-index.sqlite-wal`, and `tasks-index.sqlite-shm` (if present) to the unified backup folder before opening for write.
2. Open `tasks-index.sqlite` for write. Confirm exactly one `tasks` row exists for `task_id`.
3. Rewrite that row's workspace fields:
   - `workspace_path` = destination workspace path (raw Windows form) — **the field the sidebar groups by**
   - `workspace_key` = destination workspace path (identical on this install)
   - `meta_json` = the row's JSON with its `"workspacePath"` value rewritten to the destination (parse → set → re-serialize; leave all other keys, e.g. `taskId`/`traceId`/`title`, untouched)
4. Use a SQLite transaction; commit; `PRAGMA wal_checkpoint(truncate)`.
5. Run `PRAGMA integrity_check` (must be `ok`).
6. Verify: the row's three workspace fields now equal the destination, `meta_json` has no old-path reference, and no `tasks` row still points at the old workspace. Non-target `tasks` rows unchanged.

### Step 2 (SECONDARY): `db.sqlite`, table `session` — resume working directory

Needed so the migrated chat *opens* in the correct folder (grouping already handled by Step 1). For each target session:

1. Back up `db.sqlite`, `db.sqlite-wal`, and `db.sqlite-shm` (if present) to the unified backup folder before opening for write.
2. Open `db.sqlite` for write. Confirm exactly one `session` row exists for the session ID.
3. Rewrite that row's three columns:
   - `directory` = destination workspace path (raw Windows form)
   - `path` = destination workspace path (identical)
   - `project_id` = `compute_project_id(dest_path)` — `"proj_" + path.lower()`, drop `:`, replace `\` and space with `-` (see the helper script)
4. Defensive check: if `workflow_run` has any rows whose `cwd` is under the old workspace, rewrite those too (0 rows expected on most installs).
5. Transaction; commit; `PRAGMA integrity_check` = `ok`; verify target row = destination, non-target rows unchanged.

### Step 3 (cleanup / parity): `v2/setting.json` picker

1. Back up `setting.json` before writing.
2. Detect the file's current encoding state (UTF-8, with or without a BOM).
3. Load as JSON. Rewrite every stale path string in `recentProjects[]` and `lastWorkspaceSession[].workspacePath` from old to new. Preserve array shape, element order, and all other keys/values.
4. Write back as UTF-8 JSON, preserving the detected BOM/no-BOM state.
5. Verify the file still parses as JSON and that non-stale entries are unchanged.

### Step 4 (cleanup / parity): `db.sqlite` `message` table per-turn context

Rewriting these makes the migrated session byte-identical to a native destination session, but they are **not** the grouping key. The helper runs this step for parity. For each `message` row of the target session, parse `data` JSON and rewrite only these structured fields where they start with the old workspace path:
- assistant turns: `data.path.cwd`, `data.path.root`
- user turns: `data.contextSnapshot.envInfo.cwd`

**Never** rewrite message prose — prose lives in the `part` table; do not touch it. Re-serialize each edited `data` blob; `integrity_check` after.

### Step 5 (cleanup / parity): Electron Local Storage cache reset

`AppData\Roaming\zcode\session\Local Storage` is a rebuildable UI cache (composer drafts, prompt-history, expansion state). It is **not** the grouping key and does not need to be reset for a migration to succeed, but the helper soft-resets it for cleanup/parity: with zCode closed, move the `Local Storage` folder to the unified backup folder and let zCode rebuild it on next launch. Warn the user that unsent drafts + prompt-history autocomplete are cleared for all workspaces until retyped (chats are untouched).

### ❌ Retired steps (do NOT perform — disproven 2026-07-07)

- **"Send one message in the destination workspace to re-bind"** — NOT needed. The chat moves from the `tasks-index.sqlite` edit alone; no runtime re-bind exists.
- **"Delete the old workspace folder before reopening"** — NOT needed and harmful. Keep the source until the migration is confirmed, then remove it, exactly as with the other platforms.
- **"Local Storage reset is required for the sidebar to move"** — FALSE; the helper still performs it as cleanup/parity hygiene.

### Optional Cleanup (harmless if skipped)

After Layer 1 is verified, optionally delete orphaned rows keyed by the dead `project_id`:

- `local_setting` rows where `scope = 'project'` and `scope_id` = old `project_id`
- `input_history` rows where `project_id` = old `project_id`

These do not affect sidebar grouping. Skip unless the user asks for a tidy DB.

### Do NOT touch

- **Rollout transcripts** (`cli/rollout/model-io-sess_<id>.jsonl`) — no workspace field; the old path appears only inside `request`/`response` prose, which is off-limits.
- **Electron IndexedDB** (`AppData\Roaming\zcode\session\IndexedDB\file__0.indexeddb.leveldb\`) and **Session Storage** — inspected 2026-07-07, no workspace binding. Leave them alone.
- **Message prose** — the `part` table and message content. Only the structured `message.data` path fields in Step 4 may be edited, never prose.

> ⚠️ `v2/tasks-index.sqlite` was previously (wrongly) listed here as "not a chat store, out of scope." It is in fact the **PRIMARY grouping store** — see **Step 1**. Never skip it.

### Helper Script

Use `scripts/migrate_zcode_workspace_chat.py` for deterministic migration when available. Prefer `--dry-run` first. Save the manifest you pass to it under the workspace's `Archive/Manifests/zCode/` folder (see **Manifest Storage**).

The helper script belongs to the **Execution Workflow** side. It is not the front door. zCode may help discover inputs and generate the manifest, but a non-zCode helper agent should run the script while zCode is fully closed.

Expected manifest shape:

```json
{
  "old_workspace": "C:\\Users\\Admin\\Uzzys Universe\\Galaxies\\Trading\\Uzzy Ecosystem",
  "new_workspace": "C:\\Users\\Admin\\Uzzys Universe\\MilkyWay\\Trading\\Uzzy Ecosystem",
  "sessions": [
    {
      "id": "sess_bb6d3e64-f056-4b98-9e0e-311a91f0b073",
      "title": "Running Git Diff Skill"
    }
  ]
}
```

Run modes:

- `--dry-run`: inspect and report intended changes without writing.
- `--apply`: write changes after backups and verification.

### Verification Checklist

After migration and before telling the user it is done:

- **`tasks-index.sqlite` (PRIMARY):** target `tasks` row has `workspace_key`, `workspace_path`, and `meta_json.workspacePath` all equal to the destination; no `tasks` row still points at the old workspace; `integrity_check` = `ok`; non-target rows unchanged.
- **`db.sqlite` (SECONDARY):** migrated `session` row has `directory`/`path`/`project_id` = destination; non-target rows unchanged (row count + digest before/after); `integrity_check` = `ok`.
- Cleanup/parity: `setting.json` parses, stale entries rewritten, shape + BOM preserved; target `message.data` path fields all destination; Local Storage was moved to the run backup if present.
- Both WALs were empty/stale at apply time (WAL guard held for `tasks-index.sqlite` **and** `db.sqlite`).
- **HARD PASS/FAIL GATE — sidebar visibility:** after the user reopens zCode, the migrated chat MUST appear under the destination project group in the sidebar and stay there after a restart. **No message-send is required.** If it is still absent, the migration is **not done** — see Failure And Rollback.
- Confirm the chat opens/resumes normally in the destination working directory.

### Execution Summary

After verification passes and before considering the migration closed, produce an execution report by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion: the handoff it received plus every change it applied, verified, or rolled back. Pre-fill the skill's inputs and save under `Archive/Summaries/Migration/zCode/` so the user (and the front-door agent) can review it. Apply the availability guard if the skill is not loaded.

### Failure And Rollback

If anything fails before a session is fully written, stop and report the failing session ID and file. If a post-write verification fails, restore from backups before attempting another approach.

**If the migrated chat is absent from the sidebar (or still under the old group) after the writes:** the cause is almost always that **`tasks-index.sqlite` was not fully updated** — that DB, not `db.sqlite`, is what the sidebar reads. Diagnose in order:
1. **Re-read the `tasks` row** for the session: are `workspace_key`, `workspace_path`, AND `meta_json.workspacePath` all the destination path? If any still holds the old path, the sidebar groups by it. Fix and re-verify.
2. **Confirm the write actually committed** — if zCode was open at apply time, the write may have gone to a WAL that zCode overwrote, or been blocked. Close zCode fully and re-apply.
3. **Cross-check against a known-good control** — find a session that IS visible under the destination workspace and confirm its `tasks.workspace_path` matches yours exactly (byte-for-byte, including casing/trailing separators).
4. Only after `tasks-index.sqlite` is confirmed correct, check the `db.sqlite session` row (for resume dir). A stale `session` row makes the chat open in the wrong folder but does **not** hide it from the sidebar.

Do not declare the migration done until the chat is visibly grouped under the destination after a restart. **There is no "send a message" fix and no folder-deletion requirement** — those were disproven. If `tasks-index.sqlite` is confirmed correct and the chat is still hidden, escalate to investigating whether an additional store exists (none has been found beyond `tasks-index.sqlite` as of 2026-07-07).
