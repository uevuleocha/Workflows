---
name: antigravity-workspace-chat-migration
description: "Safely migrate Antigravity (Gemini) Desktop chat conversations between workspaces/projects. Use when the user asks to move/reassign Antigravity chats, conversations, sidebar Project grouping, or working directory from one local workspace/project to another. The grouping key is the conversation blob's Project UUID (protobuf Field 18) resolved via the Project Registry — NOT the workspace URI. Covers protobuf decode/re-encode of the per-conversation SQLite blob (Field 18 + workspace URI), the Project Registry, the derived agyhub index, and the Electron state.vscdb, with backups, one-session testing, manifests, and verification."
---

# Antigravity Workspace Chat Migration

Migrate Antigravity Desktop chat conversations from one workspace/project to another by reassigning each conversation's **Project UUID**.

**The hard-won lesson (see the Antigravity Migration summaries):** Antigravity's sidebar groups a conversation by the **Project UUID stored in protobuf Field 18** of its per-conversation blob — **not** by the workspace URI. Rewriting the URI alone does NOT move a chat. You MUST reassign Field 18 to the destination's **pre-existing** Project UUID.

## The Layers (in priority order)

1. **Layer 1 — Per-conversation SQLite blob (PRIMARY).** `C:\Users\Admin\.gemini\antigravity\conversations\<conversation-id>.db`, table `trajectory_metadata_blob`, single row, a **protobuf blob**. Inside:
   - **Field 18 = Project UUID** — the grouping key. Reassign this.
   - **Workspace URI** (fields like `1.1` and `7`, `file:///c:/...%20...`) — keep consistent for resume correctness, but it does not drive grouping.
   Edit the blob via **protobuf decode → modify → re-encode** (`blackboxprotobuf`), never raw byte-patching (length-prefixes).
2. **Layer 0 — Project Registry.** `C:\Users\Admin\.gemini\config\projects\<uuid>.json` defines each project: `id`, `name` (the sidebar label), and `projectResources.resources[].gitFolder.folderUri` (the workspace path, colon-encoded `file:///c%3A/...`). Used **read-only** to resolve a destination workspace → its Project UUID. The destination project must already exist here.
3. **Derived — `agyhub_summaries_proto.pb`.** `C:\Users\Admin\.gemini\antigravity\agyhub_summaries_proto.pb` is a **derived index** that Antigravity **regenerates from the conversation blobs on launch**. Do NOT hand-edit it.
4. **Secondary — Electron `state.vscdb`.** `C:\Users\Admin\AppData\Roaming\Antigravity\User\globalStorage\state.vscdb`, `ItemTable` key `google.antigravity` → `antigravity.workspaceCascadeMap`. Optional touch; was a no-op in the proven migration.

Use this skill only for Antigravity Desktop local conversation/workspace migration. Do not use it to edit project source code.

## Required Inputs

Require these before applying changes:

- Destination workspace path, e.g. `C:\Users\Admin\Uzzys Universe` (its Antigravity **Project must already exist** — open the folder in Antigravity once if not).
- The conversation ID(s) to migrate (the `<conversation-id>` = the `.db` filename stem).
- Confirmation that Antigravity Desktop is fully closed before applying writes.

The **source** workspace/project does NOT need to exist. Each conversation's current workspace URI and Project UUID are discovered from its own blob; a deleted/renamed source folder or a deleted source project does not block migration.

## Runtime Selection

This skill has two sides; which runs depends on runtime context, not model vendor.

- Run the **Front-Door Workflow** from inside any agent (it is read-only discovery + manifest + handoff).
- Run the **Execution Workflow** from a **non-Antigravity helper agent while Antigravity Desktop is fully closed** (Claude or Codex are fine).

Antigravity itself should not run the Execution Workflow against its own live state.

## Safety Rules

- Do not modify any Antigravity state while Antigravity Desktop is running. Abort if the target conversation has a non-empty `.db-wal` (the WAL guard).
- Back up every touched file before mutation, to the unified backup folder.
- Edit the blob via protobuf **decode → modify → re-encode** only. Never raw byte-replace a protobuf (length-prefixes).
- **Field 18 hard-fail:** if Field 18 is missing, is not bytes, is not 36 bytes long, or does not **parse as a canonical UUID** (real `uuid.UUID` parsing, not a length/dash heuristic), the helper hard-fails rather than silently skipping the conversation or reporting false success. A missing `trajectory_metadata_blob` row is a graceful hard stop, never an unpacking crash. The manifest's `destination_project_uuid` is UUID-parsed the same way before anything runs. After write, the persisted blob is re-read and Field 18 is verified byte-for-byte.
- Edit only the structured fields: **Field 18 (Project UUID)** and the **workspace URI**, which is replaced **only at the enumerated, schema-evidenced field paths** (`1.1` and `7`). An exact URI match at any non-enumerated path, or any field that merely *contains* the URI (an ambiguous partial match), is a hard stop — never rewritten. Do not rewrite user/assistant prose, summaries, or unrelated `file:///` paths. **Arbitrary whole-app-data replacement is explicitly prohibited** — a recursive walk replacing arbitrary matching byte values is not acceptable.
- Do NOT edit `agyhub_summaries_proto.pb` — it regenerates from the blobs.
- The destination **Project UUID must already exist** in the Project Registry. All destination resources (not just the first `gitFolder.folderUri`) are verified against the expected workspace URI. Incomplete or false destination-resource verification is a **hard stop before any change is applied** (`--apply` refuses; `--dry-run` reports the failure prominently), not a warning.
- Use SQLite transactions; run `PRAGMA integrity_check` after writing a conversation DB.
- Keep a rollback path by preserving backups.

## Nested Workspaces

Workspaces are sometimes **nested inside another workspace** — e.g. a hub with sub-workspaces under it. This shape is common in some setups but is **not assumed universal** (this skill may be used anywhere).

Antigravity is **structurally immune** to the nested-workspace over-rewrite class: it moves a conversation by reassigning its Project UUID (Field 18) to the **exact** destination UUID (with an already-destination idempotency guard), and it rewrites the workspace URI only on an **exact** match at schema-enumerated field paths — hard-stopping on any substring/ambiguous match rather than rewriting. The driver re-discovers the source URI each run and skips when it already equals the destination. Because nothing is prefix-spliced, no doubled or fabricated path can arise even when the destination URI *contains* the source URI (as it does when the destination nests under the source).

## Backup Location

All backups go to a single unified folder under the Gemini directory, grouped per run:

```
C:\Users\Admin\.gemini\user-backups\<run-timestamp>\<original filename>
```

- Equivalent notation: `~/.gemini/user-backups/<run-timestamp>/`.
- `<run-timestamp>` is one subfolder per run, e.g. `antigravity-workspace-chat-migration-20260623-101500`.
- Keep original filenames so a whole run deletes as a single unit. The helper does this automatically.

## Manifest Storage

The **Front-Door Workflow** creates the manifest; the **Execution Workflow** consumes it. Save it under the active workspace's `Archive/Historical/Manifests/Antigravity/` folder:

```
$WORKSPACE/Archive/Historical/Manifests/Antigravity/
<workspace_root>/Archive/Historical/Manifests/Antigravity/
./Archive/Historical/Manifests/Antigravity/
```

The platform folder is the chat platform being migrated (`Antigravity`), regardless of which agent performs the work. Every manifest must start with the next sequential `N.) ` prefix based only on the highest existing numbered file in that platform folder, e.g. `1.) antigravity_migration_manifest.json`. When updating or renaming a staged manifest, preserve its sequence number. Do not leave migration manifests unnumbered. One destination project means one manifest.

## Front-Door Workflow

Use from inside any agent. Gather inputs, discover the real metadata, build the manifest and handoff, then stop before execution.

### Front-Door Inputs

- the chat titles, screenshots, or explicit conversation list to migrate
- the destination workspace path

### Front-Door Discovery (read-only)

- **Resolve the destination Project UUID:** scan `C:\Users\Admin\.gemini\config\projects\*.json` for the project whose `projectResources.resources[].gitFolder.folderUri` matches the destination workspace (colon-encoded `file:///c%3A/...` form); fall back to matching `name`. If none matches, **stop** and tell the user to open the destination folder in Antigravity once, then re-run.
- **Per conversation:** open `…\conversations\<id>.db`, read `trajectory_metadata_blob`, decode with `blackboxprotobuf`, and discover the conversation's current **Field 18** (source Project UUID) and **workspace URI** (the most-frequent `file:///` value in the blob). These are the auto-discovered "source" values.
- Map chat titles to conversation IDs using read-only inspection; do not guess on duplicate titles.

### Front-Door Output

1. Save (or update in place) a sequentially numbered manifest under `Archive/Historical/Manifests/Antigravity/`.
2. Produce the migration handoff summary by explicitly invoking the `session-summary` skill (see **Session Summary Integration**), saved under `Archive/Historical/Summaries/Migration/Antigravity/`. Apply the availability guard if it is not loaded.

### Front-Door Stop Boundary

Stop after inputs are gathered, the destination Project UUID is resolved, per-conversation source values are discovered, the manifest is built, and the handoff summary is produced. Hand execution to a non-Antigravity helper that can run while Antigravity is fully closed.

## Read-Only Mapping Workflow

1. List `…\conversations\*.db` — each filename stem is a conversation ID.
2. For each desired chat, decode its `trajectory_metadata_blob` and read Field 18 (Project UUID) + the workspace URI.
3. Resolve project UUIDs to names via `…\config\projects\<uuid>.json` (`name`).
4. Produce a manifest with: the destination workspace, the resolved destination Project UUID, and one entry per conversation (`id`, optional `title`).

## Execution Workflow

Use only when a non-Antigravity helper is running and Antigravity Desktop is fully closed. Consumes the manifest. Only apply after the user/handoff greenlights execution.

### Per-Conversation Apply (Layer 1)

For each target conversation:

1. Confirm Antigravity is closed (WAL guard: abort if `<id>.db-wal` is non-empty).
2. Back up `<id>.db` (+ `.db-wal` / `.db-shm` if present) and `state.vscdb`.
3. Open the conversation DB; read `trajectory_metadata_blob`; decode with `blackboxprotobuf`.
4. **Reassign Field 18** to the destination Project UUID (both UUIDs are 36-byte strings → no length change).
5. **Rewrite the workspace URI:** discover the conversation's current workspace URI (most-frequent `file:///` value) and replace it with the destination workspace URI (blob `file:///c:/...` variant) **only at the enumerated permitted field paths (`1.1` and `7`)**. An exact match anywhere else, or an ambiguous partial match anywhere, hard-stops the migration. Leave unrelated `file:///` file paths and all prose untouched.
6. Re-encode the blob, `UPDATE` the row, commit, and run `PRAGMA integrity_check` (must be `ok`).

### Electron cascadeMap (Layer 2, optional)

In `state.vscdb` `ItemTable` key `google.antigravity` → `antigravity.workspaceCascadeMap`, add/update `<destination URI (vscdb c%3A variant)> → <conversation id>` if absent. This is a secondary convenience touch — it maps the destination URI to a single representative conversation ID (`conv_ids[0]`). The schema maps one URI to one conversation ID and has not been proven to support multi-ID values; do not invent a multi-ID registry shape without schema evidence.

### Do NOT touch the derived index

Leave `agyhub_summaries_proto.pb` alone — Antigravity rebuilds it from the conversation blobs on next launch, picking up the new Field 18.

### Helper Script

Use `scripts/migrate_antigravity_workspace_chat.py` for deterministic migration. Prefer `--dry-run` first. Requires `blackboxprotobuf` in the Python runtime. Save the manifest under `Archive/Historical/Manifests/Antigravity/`.

Expected manifest shape:

```json
{
  "destination_workspace": "C:\\Users\\Admin\\Uzzys Universe",
  "destination_project_uuid": "d8b0d828-1df1-4dfc-affa-6ce042da99a7",
  "conversations": [
    { "id": "1c16af14-7e29-461c-bc4a-519e63bf06f2", "title": "0.) First of Many" }
  ]
}
```

Run modes: `--dry-run` (inspect/report, no writes) and `--apply` (write after backups + verification).

### Verification Checklist

- The destination Project UUID exists in the registry and its `folderUri` matches the destination workspace.
- Each migrated conversation blob: Field 18 == destination Project UUID; workspace URI == destination URI; `PRAGMA integrity_check = ok`.
- Non-target conversations unchanged.
- User reopens Antigravity Desktop and confirms each chat appears under the destination Project, opens/resumes, and stays grouped after startup settles.
- (Optional) the old/source Project shows the conversations gone; if it is now empty the user may delete it.

### Execution Summary

After verification passes, produce an execution report by explicitly invoking the `session-summary` skill (see **Session Summary Integration**), scoped to the helper's portion, saved under `Archive/Historical/Summaries/Migration/Antigravity/`.

### Failure And Rollback

If anything fails before a conversation is fully written, stop and report the failing conversation ID. If a post-write verification fails, restore from backups before retrying. If the UI still shows a chat under the old project after Field 18 is reassigned, re-confirm the destination Project UUID actually exists in the registry, then try a full Antigravity quit (the index regenerates on launch).

## Session Summary Integration

Both workflows close by producing an explicit session summary through the `session-summary` skill — not hand-written prose. Ship `session-summary` alongside this skill.

**Availability guard (both workflows).** Before the summary step, confirm the `session-summary` skill is loaded.

- If NOT available, pause and tell the user:
  > The `session-summary` skill is not loaded. It is required to produce the migration handoff/report summary. Please make it available, or tell me to continue without it.
- If the user insists, write a plain markdown summary into the same folder with the same naming and note the dedicated skill was unavailable. Never silently skip the summary.

**Save location and naming (both workflows).** Invoke `session-summary` pre-filled:

- Directory: `<workspace_root>/Archive/Historical/Summaries/Migration/Antigravity/`
- Filename: the `session-summary` convention `x.) [Project] [Topic] Summary [N].md`.
