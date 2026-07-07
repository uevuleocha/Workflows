#!/usr/bin/env python3
"""Migrate explicit zCode (Z.ai) chat sessions between workspaces.

This helper is intentionally manifest-driven. It will not discover or guess
sessions. Use --dry-run first; use --apply only while zCode is fully closed.

Layer 1 (PRIMARY) - ~/.zcode/v2/tasks-index.sqlite, table `tasks`:
    rewrite `workspace_key`, `workspace_path`, and `meta_json.workspacePath`.
    This is the sidebar grouping store.

Layer 2 (SECONDARY) - ~/.zcode/cli/db/db.sqlite, table `session`:
    rewrite `directory`, `path`, and the path-derived `project_id`.
    This is the resume working directory / persistent identity store.

Cleanup layers:
    - ~/.zcode/v2/setting.json recent-project picker strings.
    - db.sqlite message.data structured cwd/root fields.
    - Electron Local Storage cache soft reset on --apply.

Never rewrite rollout transcripts, message prose, or the `part` table.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any

ZCODE_HOME = Path.home() / ".zcode"
TASKS_INDEX_PATH = ZCODE_HOME / "v2" / "tasks-index.sqlite"
DB_PATH = ZCODE_HOME / "cli" / "db" / "db.sqlite"
SETTING_PATH = ZCODE_HOME / "v2" / "setting.json"
LOCAL_STORAGE_PATH = Path.home() / "AppData" / "Roaming" / "zcode" / "session" / "Local Storage"

# All backups land in one unified place under the zCode dir, grouped per run.
BACKUP_ROOT = ZCODE_HOME / "user-backups"


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("old_workspace") or not data.get("new_workspace"):
        raise SystemExit("manifest requires old_workspace and new_workspace")
    if not isinstance(data.get("sessions"), list) or not data["sessions"]:
        raise SystemExit("manifest requires a non-empty sessions list")
    for item in data["sessions"]:
        if not item.get("id"):
            raise SystemExit("each session requires id")
    return data


def compute_project_id(workspace_path: str) -> str:
    """Reproduce zCode's path-derived project id.

    Transform: "proj_" + lowercase, then DROP ":" (not dash), and replace each
    "\\" and " " with "-". The colon is dropped, not dashed, so "C:\\Users" ->
    "c-users" (single dash), not "c--users".
    """
    return (
        "proj_"
        + workspace_path.lower().replace(":", "").replace("\\", "-").replace(" ", "-")
    )


def backup(path: Path, suffix: str, apply: bool) -> Path | None:
    if not path.exists():
        return None
    target_dir = BACKUP_ROOT / suffix
    target = target_dir / path.name
    if apply:
        target_dir.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            if target.exists():
                raise RuntimeError(f"backup target already exists: {target}")
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)
    return target


def backup_sqlite_family(db_path: Path, suffix: str, apply: bool) -> list[str]:
    paths = [db_path, db_path.with_name(db_path.name + "-wal"), db_path.with_name(db_path.name + "-shm")]
    backups: list[str] = []
    for path in paths:
        target = backup(path, suffix, apply)
        if target:
            backups.append(str(target))
    return backups


def detect_bom(raw: bytes) -> bool:
    return raw.startswith(b"\xef\xbb\xbf")


def replace_prefix(value: Any, old: str, new: str) -> tuple[Any, bool]:
    if isinstance(value, str) and value.startswith(old):
        return new + value[len(old) :], True
    return value, False


def row_digest(rows: list[tuple[Any, ...]]) -> str:
    h = hashlib.sha256()
    for row in rows:
        h.update(
            json.dumps(row, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
        )
        h.update(b"\n")
    return h.hexdigest()


def digest_tasks_non_target(cur: sqlite3.Cursor, target_ids: set[str]) -> str:
    rows = []
    for row in cur.execute(
        "select task_id, workspace_key, workspace_path, meta_json from tasks order by task_id"
    ):
        if row[0] not in target_ids:
            rows.append(row)
    return row_digest(rows)


def digest_sessions_non_target(cur: sqlite3.Cursor, target_ids: set[str]) -> str:
    rows = []
    for row in cur.execute(
        "select id, directory, path, project_id from session order by id"
    ):
        if row[0] not in target_ids:
            rows.append(row)
    return row_digest(rows)


def parse_meta_json(raw: str | None, sid: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"tasks.meta_json is invalid for {sid}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"tasks.meta_json is not an object for {sid}")
    return parsed


def migrate_tasks_index(
    sessions: list[dict[str, Any]], old: str, new: str, apply: bool
) -> dict[str, Any]:
    target_ids = {s["id"] for s in sessions}
    con = sqlite3.connect(TASKS_INDEX_PATH)
    try:
        cur = con.cursor()
        before_count = cur.execute("select count(*) from tasks").fetchone()[0]
        before_digest = digest_tasks_non_target(cur, target_ids)
        changed = []

        for item in sessions:
            sid = item["id"]
            row = cur.execute(
                "select workspace_key, workspace_path, meta_json from tasks where task_id=?",
                (sid,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"tasks-index.sqlite tasks row not found for {sid}")

            workspace_key, workspace_path, meta_json_raw = row
            meta_json = parse_meta_json(meta_json_raw, sid)
            before_meta_workspace = meta_json.get("workspacePath")
            meta_json["workspacePath"] = new
            new_meta_json = json.dumps(meta_json, ensure_ascii=False, separators=(",", ":"))

            entry = {
                "id": sid,
                "old_workspace_key": workspace_key,
                "old_workspace_path": workspace_path,
                "old_meta_workspacePath": before_meta_workspace,
                "new_workspace_key": new,
                "new_workspace_path": new,
                "new_meta_workspacePath": new,
            }

            if (
                workspace_key == new
                and workspace_path == new
                and before_meta_workspace == new
                and old not in (meta_json_raw or "")
            ):
                entry["status"] = "already_destination"
                changed.append(entry)
                continue

            if apply:
                cur.execute(
                    """
                    update tasks
                       set workspace_key=?,
                           workspace_path=?,
                           meta_json=?
                     where task_id=?
                    """,
                    (new, new, new_meta_json, sid),
                )
                if cur.rowcount != 1:
                    raise RuntimeError(f"unexpected tasks rowcount for {sid}: {cur.rowcount}")
            entry["status"] = "migrated"
            changed.append(entry)

        if apply:
            con.commit()
            cur.execute("pragma wal_checkpoint(truncate)")

        after_count = cur.execute("select count(*) from tasks").fetchone()[0]
        after_digest = digest_tasks_non_target(cur, target_ids)
        integrity = cur.execute("pragma integrity_check").fetchone()[0]
        if before_count != after_count:
            raise RuntimeError("tasks row count changed unexpectedly")
        if before_digest != after_digest:
            raise RuntimeError("non-target tasks rows changed unexpectedly")
        if integrity != "ok":
            raise RuntimeError(f"tasks-index.sqlite integrity_check failed: {integrity}")

        verification = []
        for sid in target_ids:
            row = cur.execute(
                "select workspace_key, workspace_path, meta_json from tasks where task_id=?",
                (sid,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"tasks row disappeared for {sid}")
            workspace_key, workspace_path, meta_json_raw = row
            meta_json = parse_meta_json(meta_json_raw, sid)
            meta_workspace = meta_json.get("workspacePath")
            if apply and (workspace_key != new or workspace_path != new or meta_workspace != new):
                raise RuntimeError(f"tasks row verification failed for {sid}")
            verification.append(
                {
                    "id": sid,
                    "workspace_key": workspace_key,
                    "workspace_path": workspace_path,
                    "meta_workspacePath": meta_workspace,
                    "contains_old_workspace": old in (meta_json_raw or ""),
                }
            )

        old_workspace_rows = cur.execute(
            "select count(*) from tasks where workspace_key=? or workspace_path=?",
            (old, old),
        ).fetchone()[0]

        return {
            "db": str(TASKS_INDEX_PATH),
            "changed": changed,
            "verification": verification,
            "old_workspace_rows_remaining": old_workspace_rows,
            "integrity_check": integrity,
            "tasks_count": after_count,
        }
    finally:
        con.close()


def migrate_setting_json(old: str, new: str, apply: bool) -> dict[str, Any]:
    raw = SETTING_PATH.read_bytes()
    has_bom = detect_bom(raw)
    text = raw.decode("utf-8-sig")
    data = json.loads(text)

    changed_recent: list[dict[str, str]] = []
    changed_last: list[dict[str, str]] = []

    recent = data.get("recentProjects")
    if isinstance(recent, list):
        for i, entry in enumerate(recent):
            replaced, changed = replace_prefix(entry, old, new)
            if changed:
                recent[i] = replaced
                changed_recent.append({"old": entry, "new": replaced})

    last = data.get("lastWorkspaceSession")
    if isinstance(last, list):
        for entry in last:
            if isinstance(entry, dict):
                old_value = entry.get("workspacePath")
                replaced, changed = replace_prefix(old_value, old, new)
                if changed:
                    entry["workspacePath"] = replaced
                    changed_last.append({"old": old_value, "new": replaced})

    if apply and (changed_recent or changed_last):
        out = json.dumps(data, indent=2, ensure_ascii=False)
        prefix = b"\xef\xbb\xbf" if has_bom else b""
        SETTING_PATH.write_bytes(prefix + out.encode("utf-8"))

    return {
        "setting_json": str(SETTING_PATH),
        "recent_projects_changed": changed_recent,
        "last_workspace_session_changed": changed_last,
        "bom_preserved": has_bom,
    }


def migrate_sqlite(
    sessions: list[dict[str, Any]], old: str, new: str, apply: bool
) -> dict[str, Any]:
    target_ids = {s["id"] for s in sessions}
    new_project_id = compute_project_id(new)
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        before_count = cur.execute("select count(*) from session").fetchone()[0]
        before_digest = digest_sessions_non_target(cur, target_ids)
        changed = []

        for item in sessions:
            sid = item["id"]
            row = cur.execute(
                "select directory, path, project_id from session where id=?", (sid,)
            ).fetchone()
            if row is None:
                raise RuntimeError(f"db.sqlite session row not found for {sid}")
            directory, path, project_id = row
            entry = {
                "id": sid,
                "old_directory": directory,
                "old_path": path,
                "old_project_id": project_id,
                "new_directory": new,
                "new_path": new,
                "new_project_id": new_project_id,
            }
            if directory == new and path == new and project_id == new_project_id:
                entry["status"] = "already_destination"
                changed.append(entry)
                continue
            if apply:
                cur.execute(
                    "update session set directory=?, path=?, project_id=? where id=?",
                    (new, new, new_project_id, sid),
                )
                if cur.rowcount != 1:
                    raise RuntimeError(f"unexpected session rowcount for {sid}: {cur.rowcount}")
            entry["status"] = "migrated"
            changed.append(entry)

        wf_changed = 0
        for wf_id, wf_cwd in cur.execute(
            "select id, cwd from workflow_run where cwd like ?", (old + "%",)
        ).fetchall():
            new_cwd, changed_cwd = replace_prefix(wf_cwd, old, new)
            if changed_cwd:
                if apply:
                    cur.execute("update workflow_run set cwd=? where id=?", (new_cwd, wf_id))
                wf_changed += 1

        message_changed = migrate_message_data(cur, target_ids, old, new, apply)

        if apply:
            con.commit()
            cur.execute("pragma wal_checkpoint(truncate)")

        after_count = cur.execute("select count(*) from session").fetchone()[0]
        after_digest = digest_sessions_non_target(cur, target_ids)
        integrity = cur.execute("pragma integrity_check").fetchone()[0]
        if before_count != after_count:
            raise RuntimeError("session row count changed unexpectedly")
        if before_digest != after_digest:
            raise RuntimeError("non-target session rows changed unexpectedly")
        if integrity != "ok":
            raise RuntimeError(f"db.sqlite integrity_check failed: {integrity}")

        return {
            "db": str(DB_PATH),
            "changed": changed,
            "workflow_run_cwd_changed": wf_changed,
            "message_data_changed": message_changed,
            "integrity_check": integrity,
            "session_count": after_count,
        }
    finally:
        con.close()


def migrate_message_data(
    cur: sqlite3.Cursor, target_ids: set[str], old: str, new: str, apply: bool
) -> dict[str, Any]:
    table_names = {
        row[0] for row in cur.execute("select name from sqlite_master where type='table'")
    }
    if "message" not in table_names:
        return {"rows_changed": 0, "fields_changed": 0, "status": "message_table_missing"}

    columns = {row[1] for row in cur.execute("pragma table_info(message)")}
    if not {"id", "session_id", "data"}.issubset(columns):
        return {"rows_changed": 0, "fields_changed": 0, "status": "message_columns_missing"}

    rows_changed = 0
    fields_changed = 0
    changed_messages: list[str] = []

    for message_id, data_raw in cur.execute(
        "select id, data from message where session_id in (%s)"
        % ",".join("?" for _ in target_ids),
        tuple(target_ids),
    ).fetchall():
        if not data_raw:
            continue
        try:
            data = json.loads(data_raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue

        changed = False

        path_obj = data.get("path")
        if isinstance(path_obj, dict):
            for key in ("cwd", "root"):
                replaced, did_change = replace_prefix(path_obj.get(key), old, new)
                if did_change:
                    path_obj[key] = replaced
                    fields_changed += 1
                    changed = True

        context_snapshot = data.get("contextSnapshot")
        if isinstance(context_snapshot, dict):
            env_info = context_snapshot.get("envInfo")
            if isinstance(env_info, dict):
                replaced, did_change = replace_prefix(env_info.get("cwd"), old, new)
                if did_change:
                    env_info["cwd"] = replaced
                    fields_changed += 1
                    changed = True

        if changed:
            rows_changed += 1
            changed_messages.append(str(message_id))
            if apply:
                cur.execute(
                    "update message set data=? where id=?",
                    (json.dumps(data, ensure_ascii=False, separators=(",", ":")), message_id),
                )

    return {
        "rows_changed": rows_changed,
        "fields_changed": fields_changed,
        "message_ids_changed": changed_messages,
        "status": "ok",
    }


def reset_local_storage(suffix: str, apply: bool) -> dict[str, Any]:
    if not LOCAL_STORAGE_PATH.exists():
        return {
            "local_storage": str(LOCAL_STORAGE_PATH),
            "status": "missing",
            "backup": None,
        }

    backup_target = BACKUP_ROOT / suffix / LOCAL_STORAGE_PATH.name
    if apply:
        backup_target.parent.mkdir(parents=True, exist_ok=True)
        if backup_target.exists():
            raise RuntimeError(f"Local Storage backup already exists: {backup_target}")
        shutil.move(str(LOCAL_STORAGE_PATH), str(backup_target))
        status = "moved_to_backup"
    else:
        status = "would_move_to_backup"

    return {
        "local_storage": str(LOCAL_STORAGE_PATH),
        "status": status,
        "backup": str(backup_target),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    old = manifest["old_workspace"]
    new = manifest["new_workspace"]
    sessions = manifest["sessions"]
    apply = args.apply
    suffix = (
        "zcode-workspace-chat-migration-"
        + _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    )

    backups: list[str] = []
    if apply:
        backups.extend(backup_sqlite_family(TASKS_INDEX_PATH, suffix, True))
        backups.extend(backup_sqlite_family(DB_PATH, suffix, True))
        setting_backup = backup(SETTING_PATH, suffix, True)
        if setting_backup:
            backups.append(str(setting_backup))

    results: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "backup_run": suffix,
        "backups": backups,
    }
    results["tasks_index"] = migrate_tasks_index(sessions, old, new, apply)
    results["sqlite"] = migrate_sqlite(sessions, old, new, apply)
    results["setting_json"] = migrate_setting_json(old, new, apply)
    results["local_storage"] = reset_local_storage(suffix, apply)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
