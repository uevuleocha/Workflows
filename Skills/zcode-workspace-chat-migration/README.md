# zCode Workspace Chat Migration - Adoption Guide

Migrates zCode (Z.ai) local chat sessions between workspaces across the stores that matter for a native-looking migration:

1. `v2/tasks-index.sqlite` `tasks` row: `workspace_key`, `workspace_path`, and `meta_json.workspacePath`. This is the real sidebar grouping key.
2. `cli/db/db.sqlite` `session` row: `directory`, `path`, and path-derived `project_id`. This is the resume working directory / persistent identity.
3. Cleanup/parity stores: `v2/setting.json`, structured `db.sqlite` `message.data` cwd/root fields, and the rebuildable Electron Local Storage cache.

**Critical:** zCode does not group the sidebar from `session.project_id`. A `db.sqlite` rewrite alone can leave the chat hidden. The migration must rewrite `tasks-index.sqlite` first, with zCode fully closed, then verify the chat appears under the destination group after reopen.

There is no required "send one message to re-bind" step and no need to delete the old workspace folder before reopening. Those theories were disproven during the Galaxies-to-MilkyWay migration test. Keep the source folder until the migration is confirmed, then clean it up separately if desired.

The bundled helper script runs the primary, secondary, and cleanup/parity steps: `tasks-index.sqlite`, `db.sqlite` session/workflow/message data, `setting.json`, and a Local Storage soft reset into the run backup folder on `--apply`.

## Dependency

`zcode-workspace-chat-migration` depends on the `session-summary` skill. Both the Front-Door and Execution workflows close by producing an explicit handoff/feedback summary through `session-summary` - not hand-written prose (see the `## Session Summary Integration` section in `SKILL.md`). It runs with an availability guard and falls back to a plain markdown summary if `session-summary` is not loaded.

**If you adopted `zcode-workspace-chat-migration` from Uzo (U-Z-O), also adopt `session-summary`.** This skill also ships its own bundled `scripts/` - keep those with it when you copy the skill.

For the general mechanism, see the workspace's `Documentation/` folder, `3.) Skill-to-Skill Calls - Pattern and Registry.md`.

## Adoption Prompt

```text
Read this README and SKILL.md. This skill depends on `session-summary` and ships
its own scripts/ folder; make sure `session-summary` is installed in the same
agent installs (Codex / Claude / Antigravity / Hermes / zCode) and that the
scripts travel with the skill. Use my OS path conventions and ask before creating
missing folders.
```

## Optional artifact formats

Pair with `html-this` or `pdf-this` for HTML-only or PDF-only manifests, handoffs, and feedback summaries while this skill retains migration ownership.
