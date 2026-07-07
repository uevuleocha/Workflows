---
name: claude-workspace-chat-migration
description: "Safely migrate Claude Desktop chat sessions between workspaces. Use when the user asks to move/reassign Claude Code chats, sessions, transcript JSONL, sidebar project grouping, working directory, workspace memory, or session sidecar data from one local workspace/project to another. Covers the required state surfaces: the CLI transcript JSONL, adjacent Claude project data such as memory, session subagents, and session tool-results, and the Claude Desktop chat store with backups, one-session testing, manifests, and verification."
---

# Claude Workspace Chat Migration

Migrate Claude Desktop chat sessions from one workspace to another by making the local Claude state surfaces agree:

1. Layer A — CLI transcript JSONL under `C:\Users\Admin\.claude\projects\<encoded-path>\<cliSessionId>.jsonl`. The encoded folder name is the workspace path with every `:`, `\`, and space replaced by `-` (e.g. `C:\Users\Admin\Uzzys Universe` becomes `C--Users-Admin-Uzzys-Universe`). The sidebar/CLI grouping for a chat is the encoded folder its transcript lives in; each record also carries a top-level `cwd` used to resume in the right directory.
2. Adjacent Claude project data under the same encoded folder: workspace `memory/`, plus per-session `<cliSessionId>\subagents\` and `<cliSessionId>\tool-results\` folders. These are path-keyed state and must move with the workspace/session they belong to; they are not disposable cache.
3. Layer B — Desktop chat store under `C:\Users\Admin\AppData\Roaming\Claude\claude-code-sessions\<account>\<group>\local_*.json`. Each chat has one record (linked to Layer A by `cliSessionId`) carrying `cwd`, `originCwd`, and `title` — the fields that drive the Desktop sidebar group and title.

Use this skill only for Claude Desktop local session/workspace migration. Do not use it to edit project source code.

Claude has these local state surfaces for workspace migration. There is no SQLite thread index and no global-state hints file (those are Codex concerns). Do not invent additional layers.

## Required Inputs

Require explicit values before applying changes:

- Source workspace path, for example `C:\Users\Admin\Uzzys World`.
- Destination workspace path, for example `C:\Users\Admin\Uzzys Universe`.
- CLI session ID(s) to migrate (the `cliSessionId`, which is also the transcript filename stem).
- The Layer B Desktop record path for each session (`...\claude-code-sessions\...\local_*.json`).
- Confirmation that Claude Desktop and every Claude Code session are fully closed before applying writes.

If the user only provides chat titles, first map titles to session IDs, transcript paths, and Desktop records using read-only inspection of the projects folder and the Desktop chat store. Do not guess when duplicate titles exist.

## Runtime Selection

This skill has two sides. Which side runs depends on the runtime context, not on the model vendor or model family.

- If the skill is being run inside Claude Desktop / Claude local runtime, run the **Front-Door Workflow**.
- If the skill is being run by a non-Claude helper agent while Claude Desktop is fully closed, run the **Execution Workflow**.

Examples:

- Codex or another non-Claude agent may run the **Execution Workflow** if Claude is fully closed, even when that helper agent uses a non-Anthropic model.
- Claude itself should not run the **Execution Workflow** against live Claude state. Claude should run the **Front-Door Workflow**, prepare the artifacts, and stop before the closed-Claude execution handoff.

## Safety Rules

- Start with one session when testing a new migration pattern.
- Do not modify any Claude state while Claude Desktop or any Claude Code session is running.
- Back up every touched file before mutation.
- Back up every touched adjacent data folder before moving it.
- Do not globally replace paths across `C:\Users\Admin\.claude` or the Desktop chat store.
- Edit only structured workspace metadata: the transcript's top-level `cwd`, and the Desktop record's `cwd` and `originCwd`. Do not rewrite user/assistant prose just because it mentions the old path.
- Move adjacent `memory/`, `<cliSessionId>\subagents\`, and `<cliSessionId>\tool-results\` directories byte-for-byte. Do not rewrite their contents during relocation.
- Preserve JSONL format: one JSON object per line.
- Preserve the Layer B file's existing byte/encoding state. Detect whether the record already has a UTF-8 BOM and keep that state; never add or strip a BOM.
- Keep a rollback path by preserving backups.
- Save every backup to the unified backup folder, never scattered next to originals (see **Backup Location**).

## Backup Location

All backups this skill makes — whether written by the helper script's `backup()` or made manually by an agent during a one-session fix — go to a single unified folder under the Claude directory, grouped per run:

```
C:\Users\Admin\.claude\user-backups\<run-timestamp>\<original filename>
```

- Equivalent notation: `~/.claude/user-backups/<run-timestamp>/`.
- `<run-timestamp>` is one subfolder per migration run, e.g. `claude-workspace-chat-migration-20260621-142709`.
- Keep the original filename inside that subfolder so a whole run can be deleted as a single unit.
- Rationale: one safe, unified place. When the migration is confirmed, the user can ask an agent to delete a run's subfolder (or the whole `user-backups` folder) — nothing else needs hunting down.
- The helper script does this automatically. When backing up manually, copy into the same `~/.claude/user-backups/<run-timestamp>/` folder.

## Manifest Storage

Building a manifest when running this skill is encouraged — it keeps a migration explicit and auditable. It is a shared concern: the **Front-Door Workflow** creates the manifest and the **Execution Workflow** consumes it. Save the manifest into the active workspace's `Archive/Manifests/Claude/` folder (create it if missing), written workspace-relative so it works for whichever project/working directory the migration targets:

```
$WORKSPACE/Archive/Manifests/Claude/
<workspace_root>/Archive/Manifests/Claude/
./Archive/Manifests/Claude/
```

All three notations mean the same thing: the `Archive/Manifests/Claude/` folder of the workspace currently being worked in. The platform folder is determined by the chat platform being migrated, not by the agent performing the work: a Codex or Antigravity helper executing a Claude migration still uses the `Claude` folder. Once a migration is confirmed, the manifest is no longer needed — the user can ask an agent to delete it from there.

Every manifest saved in `Archive/Manifests/Claude/` must start with the next sequential `N.) ` prefix based only on the highest existing numbered file in that platform folder. Use `N.) <descriptive-manifest-name>.json`; for example, `1.) claude_migration_manifest_chats0-4_full_batch.json`. When updating or renaming a staged manifest, preserve its existing sequence number while changing the descriptive portion to match its current scope and state. Do not leave migration manifests unnumbered.

When a migration is staged (e.g. one-session test first, then the rest), prefer updating the existing manifest in place to reflect what is done and what remains, rather than creating a second file, unless the sessions come from more than one source workspace. One source workspace means one manifest.

## Front-Door Workflow

Use this workflow when the skill is started from Claude Desktop / Claude local runtime.

This is the native front door of the skill. Claude uses it to gather user inputs, discover the real session metadata from source-of-truth files, build the manifest and handoff artifacts, and then stop before execution.

### Front-Door Inputs

Collect or confirm these user inputs up front:

- the chat titles, screenshots, or explicit session list the user wants migrated
- the destination workspace path
- any explicit exclusions

Do not ask the user to supply source workspace roots when those can be discovered from Claude state. The user may know the destination workspace, but Claude should discover the actual per-session source paths from the stored metadata.

### Front-Door Discovery

For the requested sessions, discover the real values from Claude's source-of-truth files. Do not infer or guess them. See the **Read-Only Mapping Workflow** below for the step-by-step discovery procedure.

- discover CLI session IDs
- discover transcript JSONL paths (encoded projects folder + `<cliSessionId>.jsonl`)
- discover adjacent workspace/session data in the source encoded folder: `memory/`, `<cliSessionId>\subagents\`, and `<cliSessionId>\tool-results\`
- discover the Layer B Desktop record path per session
- discover old workspace roots per session (from the transcript `cwd` and the Desktop record `cwd`)
- discover whether the requested sessions come from one source workspace or multiple source groups

Use read-only inspection of:

- `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\` for transcript filenames (= session IDs)
- `C:\Users\Admin\AppData\Roaming\Claude\claude-code-sessions\<account>\<group>\local_*.json` for `cliSessionId`, `cwd`, `originCwd`, `title`

### Front-Door Output

Once discovery is complete:

1. Save (or update in place) a sequentially numbered `N.) ` manifest under the active workspace's `Archive/Manifests/Claude/` folder.
2. Produce the migration handoff summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion, pre-fill the skill's inputs, and save it under `Archive/Summaries/Migration/Claude/`. Apply the availability guard if the skill is not loaded.
3. Group sessions by real discovered old workspace when needed. If there are mixed-source sessions, represent them as separate source groups rather than flattening them into one assumed old workspace.

### Front-Door Stop Boundary

The Front-Door Workflow stops after Claude has:

- gathered the user inputs
- discovered the real session metadata
- built (or updated) the manifest
- built the handoff summary by explicitly invoking the `session-summary` skill (helper-scoped; see **Session Summary Integration**)
- identified the destination workspace and any source groups

At that point, if the migration must touch live Claude state, Claude should stop and hand execution to a non-Claude helper agent that can run while Claude Desktop is fully closed.

## Read-Only Mapping Workflow

When preparing a batch or front-door package for another agent:

1. List `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\*.jsonl` — each filename stem is a `cliSessionId`.
2. List `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\memory\`, if present.
3. For every target session ID, list adjacent `C:\Users\Admin\.claude\projects\<encoded-old-workspace>\<cliSessionId>\subagents\` and `...\<cliSessionId>\tool-results\`, if present.
4. For each desired chat, find its Layer B record by scanning `...\claude-code-sessions\<account>\<group>\local_*.json` for the one whose `cliSessionId` matches; read its `title`, `cwd`, `originCwd`.
5. Confirm the transcript's top-level `cwd` matches the old workspace.
6. Compare each requested title against the screenshot/user list. Exclude chats the user explicitly excludes.
7. Produce a manifest with one entry per session:
   - `title`
   - `cli_session_id`
   - `desktop_record` (full path to the `local_*.json`)
   - optional `transcript_path` (else the helper computes it from the workspace + id)
   - whether the transcript and Desktop record were found.
   - optional `sessions[].sidecars` discovery metadata when present:
     - workspace-level `memory/` source and destination
     - per-session `subagents/` and `tool-results/` source and destination
8. If adjacent data must be moved by the helper script, also produce a top-level `adjacent_data_relocation` execution plan:
   - `memory_move` for workspace-level `memory/`
   - `sidecar_relocations` for per-session `subagents/` and `tool-results/`
   - `then_delete` for deleting the old encoded folder only after true-empty verification

Important: `sessions[].sidecars` is human-readable discovery/audit metadata. It is not, by itself, a helper-script execution instruction. If a manifest only records sidecars under `sessions[].sidecars`, the helper can migrate transcripts and Desktop records but will not know which adjacent folders to move.

## Execution Workflow

Use this workflow only when a non-Claude helper agent is running and Claude Desktop is fully closed.

The Execution Workflow consumes the manifest and handoff package prepared by the Front-Door Workflow. It performs the real migration writes, verification, and reporting.

### Two-Layer Apply Workflow

Only apply after the user or handoff explicitly greenlights execution and Claude Desktop is closed.

#### Layer A: CLI Transcript

For each target session:

1. Confirm the old transcript exists at `<encoded-old-workspace>\<cliSessionId>.jsonl`.
2. Back up the transcript file before writing.
3. Create the new projects dir `C:\Users\Admin\.claude\projects\<encoded-new-workspace>\` if missing.
4. For every JSONL record with a top-level `cwd` equal to the old workspace (or under it), rewrite that `cwd` to the destination workspace. Do not touch `content` or other prose.
5. Write the transformed transcript to `<encoded-new-workspace>\<cliSessionId>.jsonl` and verify every non-empty line still parses as JSON, with the expected count of destination `cwd` values and zero old-workspace `cwd` values.
6. Remove the old transcript from the old projects dir only after the destination is verified (the chat must live in exactly one projects folder).

#### Layer B: Desktop Chat Store

For each target session's `local_*.json`:

1. Back up the record before writing.
2. Detect the file's current encoding state (UTF-8, with or without a BOM).
3. Rewrite only `cwd` and `originCwd` from the old workspace to the destination workspace.
4. Preserve all other keys (including `cliSessionId`, `title`, `model`, permissions) and preserve the detected BOM/no-BOM state on write.
5. Verify the file still parses as JSON and that `cliSessionId` and `title` are unchanged.

#### Adjacent Project Data: Memory and Sidecars

For each source encoded workspace:

1. Discover whether `memory/` exists. If present, back it up and move it to the destination encoded workspace's `memory/` folder, creating the destination parent if missing. Do not overwrite an existing destination `memory/` unless the manifest explicitly says how to merge or replace it.
2. For each target `cliSessionId`, discover sibling `<cliSessionId>\subagents\` and `<cliSessionId>\tool-results\` folders. Back up each present folder before moving.
3. Move each sidecar folder to the encoded workspace where that session's `<cliSessionId>.jsonl` now lives. In mixed-destination batches, do not assume one destination for every sidecar; route by the manifest's `adjacent_data_relocation.sidecar_relocations` destination.
4. Preserve sidecar contents byte-for-byte. Do not parse, rewrite, or normalize files inside these folders.
5. After relocation, verify every moved destination folder exists, every source folder is gone, and the source encoded workspace is truly empty before it is eligible for deletion.

True-empty means `0` files and `0` subdirectories remain, not merely `0` `.jsonl` transcripts.

### Helper Script

Use `scripts/migrate_claude_workspace_chat.py` for deterministic migration when available. Prefer `--dry-run` first. Save the manifest you pass to it under the workspace's `Archive/Manifests/Claude/` folder (see **Manifest Storage**).

The helper script belongs to the **Execution Workflow** side. It is not the front door. Claude may help discover inputs and generate the manifest, but a non-Claude helper agent should run the script while Claude Desktop is fully closed.

Expected manifest shape:

```json
{
  "old_workspace": "C:\\Users\\Admin\\Uzzys World",
  "new_workspace": "C:\\Users\\Admin\\Uzzys Universe",
  "sessions": [
    {
      "title": "0.) First of Many --> Setup",
      "cli_session_id": "5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19",
      "desktop_record": "C:\\Users\\Admin\\AppData\\Roaming\\Claude\\claude-code-sessions\\<account>\\<group>\\local_33716310-....json"
    }
  ]
}
```

When adjacent Claude project data must move, include a top-level `adjacent_data_relocation` block:

- `memory_move`: `source`, `destination`, and expected `files`
- `sidecar_relocations`: entries with `session_id`, `sidecar_kind`, `source`, `destination`, and `dest_encoded_folder`
- `then_delete`: source encoded folder to delete only after true-empty verification

Example:

```json
{
  "adjacent_data_relocation": {
    "sidecar_relocations": [
      {
        "session_id": "5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19",
        "sidecar_kind": "tool-results",
        "source": "C:\\Users\\Admin\\.claude\\projects\\<old-encoded>\\5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19\\tool-results",
        "destination": "C:\\Users\\Admin\\.claude\\projects\\<new-encoded>\\5ac10e6f-5aca-4f2c-8b6e-a6c50c7a7a19\\tool-results",
        "dest_encoded_folder": "<new-encoded>"
      }
    ],
    "then_delete": "C:\\Users\\Admin\\.claude\\projects\\<old-encoded>"
  }
}
```

The old `third_pass_leftover_relocation.aux_relocations` name came from an earlier staged cleanup pass. The helper may keep a small fallback for archived manifests, but new manifests must use `adjacent_data_relocation.sidecar_relocations`.

The helper must dry-run this block before apply, back up every source folder under `~/.claude/user-backups/<run-timestamp>/`, move the folders byte-for-byte, verify destinations and source absence, verify true-empty, and only then delete `then_delete`.

Run modes:

- `--dry-run`: inspect and report intended changes without writing.
- `--apply`: write changes after backups and verification.

### Verification Checklist

After migration and before telling the user it is done:

- The new projects dir `<encoded-new-workspace>` exists and contains `<cliSessionId>.jsonl` for each migrated session.
- The migrated transcript parses line by line, with the expected count of destination `cwd` values and zero old-workspace `cwd` values.
- The old transcript no longer exists in the old projects dir for each migrated session.
- Each migrated Desktop record has `cwd` and `originCwd` equal to the destination workspace, with `cliSessionId` and `title` unchanged and the original BOM/no-BOM state preserved.
- Workspace `memory/`, if present and in scope, exists in the destination encoded workspace and no longer exists in the source encoded workspace.
- Each target session's `subagents/` and `tool-results/` sidecar folders, if present and in scope, exist beside the destination transcript folder and no longer exist under the source encoded workspace.
- Before deleting any source encoded workspace folder, recursively verify it contains `0` files and `0` subdirectories.
- Non-target sessions (transcripts and Desktop records) are unchanged.
- User reopens Claude Desktop and confirms:
  - chat appears under the destination project,
  - chat stays there after startup settles,
  - chat opens/resumes normally and can send/receive a message.

### Execution Summary

After verification passes and before considering the migration closed, produce an execution report by explicitly invoking the `session-summary` skill (see **Session Summary Integration**). Scope it to the helper agent's portion: the handoff it received plus every change it applied, verified, or rolled back. Pre-fill the skill's inputs and save under `Archive/Summaries/Migration/Claude/` so the user (and the front-door agent) can review it. Apply the availability guard if the skill is not loaded.

### Failure And Rollback

If anything fails before a session is fully written, stop and report the failing session ID and file. If a post-write verification fails, restore from backups before attempting another approach. If the UI still shows a chat under the old group after both layers agree, re-confirm the encoded folder name and the Desktop record `cliSessionId` link, and inspect for any additional Desktop-side cache before retrying.

## Session Summary Integration

Both workflows close by producing an explicit session summary through the `session-summary` skill — not hand-written prose. This skill and `session-summary` are meant to travel together; if you ever share this skill, ship that one with it.

**Availability guard (both workflows).** Before the summary step, confirm the `session-summary` skill is present in the agent's loaded skills.

- If it is NOT available, pause and tell the user:
  > The `session-summary` skill is not loaded. It is required to produce the migration handoff/report summary. Please make it available, or tell me to continue without it.
- If the user insists on continuing without it, proceed and write a plain markdown summary into the same folder with the same naming, then note in your final report that the dedicated skill was unavailable.
- Never silently skip the summary.

**Save location and naming (both workflows).** Invoke `session-summary` pre-filled so the user does not have to complete its input template:

- Directory: `<workspace_root>/Archive/Summaries/Migration/Claude/`
- Create the `Claude` platform folder if it does not exist.
- Sequence number: the next integer after the highest existing `N.)` file in the `Claude` platform folder only.
- Filename: the `session-summary` convention `x.) [Project] [Topic] Summary [N].md`.
