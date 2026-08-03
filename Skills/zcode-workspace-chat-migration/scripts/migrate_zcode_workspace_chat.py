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
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

ZCODE_HOME = Path.home() / ".zcode"
TASKS_INDEX_PATH = ZCODE_HOME / "v2" / "tasks-index.sqlite"
DB_PATH = ZCODE_HOME / "cli" / "db" / "db.sqlite"
SETTING_PATH = ZCODE_HOME / "v2" / "setting.json"
LOCAL_STORAGE_PATH = Path.home() / "AppData" / "Roaming" / "zcode" / "session" / "Local Storage"

# All backups land in one unified place under the zCode dir, grouped per run.
BACKUP_ROOT = ZCODE_HOME / "user-backups"


# Exact approved before-state keys the manifest MUST declare per session.
# tasks-index.sqlite (primary) and db.sqlite (secondary) rows are compared
# against these values before anything is overwritten.
BEFORE_STATE_TASKS_KEYS = ("old_workspace_key", "old_workspace_path", "old_meta_workspacePath")
BEFORE_STATE_SESSION_KEYS = ("old_directory", "old_path", "old_project_id")


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("old_workspace") or not data.get("new_workspace"):
        raise SystemExit("manifest requires old_workspace and new_workspace")
    if not isinstance(data.get("sessions"), list) or not data["sessions"]:
        raise SystemExit("manifest requires a non-empty sessions list")
    for item in data["sessions"]:
        if not item.get("id"):
            raise SystemExit("each session requires id")
        missing = [
            key for key in BEFORE_STATE_TASKS_KEYS + BEFORE_STATE_SESSION_KEYS
            if key not in item
        ]
        if missing:
            raise SystemExit(
                f"session {item['id']}: manifest must record the exact approved "
                f"before-state; missing keys: {missing}. Capture them during "
                "front-door intake from the populated tasks-index.sqlite row and "
                "the db.sqlite session row."
            )
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


def backup_sqlite_family(
    db_path: Path, suffix: str, apply: bool,
    backup_manifest: list[dict[str, str]] | None = None,
) -> list[str]:
    paths = [db_path, db_path.with_name(db_path.name + "-wal"), db_path.with_name(db_path.name + "-shm")]
    backups: list[str] = []
    for path in paths:
        target = backup(path, suffix, apply)
        if target:
            backups.append(str(target))
            if backup_manifest is not None:
                backup_manifest.append({"original": str(path), "backup": str(target)})
    return backups


def restore_backups(backup_manifest: list[dict[str, str]]) -> list[str]:
    """Restore every backed-up file to its recorded original path and verify
    each restoration byte-for-byte. Coordinated: called when updating or
    verifying EITHER database fails, so BOTH databases return to their
    pre-migration state. Raises if any restoration cannot be verified."""
    restored: list[str] = []
    errors: list[str] = []
    # Remove stray -wal/-shm sidecars created after backup time: restoring a
    # main DB file next to a leftover post-failure WAL would corrupt it.
    originals = {entry["original"] for entry in backup_manifest}
    for entry in backup_manifest:
        original = Path(entry["original"])
        if original.suffix == ".sqlite":
            for sidecar in (original.with_name(original.name + "-wal"),
                            original.with_name(original.name + "-shm")):
                if str(sidecar) not in originals and sidecar.exists():
                    try:
                        sidecar.unlink()
                        restored.append(f"removed stray sidecar {sidecar}")
                    except OSError as exc:
                        errors.append(f"could not remove stray sidecar {sidecar}: {exc}")
    for entry in backup_manifest:
        bp = Path(entry["backup"])
        original = Path(entry["original"])
        if not bp.exists():
            errors.append(f"backup file missing, cannot restore {original}: {bp}")
            continue
        try:
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bp, original)
            if original.read_bytes() != bp.read_bytes():
                errors.append(f"restoration verification failed for {original}")
                continue
            restored.append(str(original))
        except OSError as exc:
            errors.append(f"restore failed for {original}: {exc}")
    if errors:
        raise RuntimeError(
            "coordinated backup restoration incomplete:\n" + "\n".join(errors)
            + f"\nRestored so far: {restored}"
        )
    return restored


def preflight_before_state(
    sessions: list[dict[str, Any]], old: str, new: str
) -> dict[str, Any]:
    """Read-only preflight across BOTH databases before either is written.

    Validates all six exact before-state values per session (tasks-index:
    workspace_key/workspace_path/meta_json.workspacePath; db.sqlite session:
    directory/path/project_id) against the manifest. A row already fully at
    the destination is accepted as already_destination. Any other mismatch or
    missing row raises with ZERO writes performed."""
    new_project_id = compute_project_id(new)
    report: dict[str, Any] = {"tasks_index": [], "session": []}

    def _ro(path: Path) -> sqlite3.Connection:
        return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)

    con = _ro(TASKS_INDEX_PATH)
    try:
        cur = con.cursor()
        for item in sessions:
            sid = item["id"]
            row = cur.execute(
                "select workspace_key, workspace_path, meta_json from tasks where task_id=?",
                (sid,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"preflight: tasks-index.sqlite tasks row not found for {sid}")
            workspace_key, workspace_path, meta_json_raw = row
            meta_workspace = parse_meta_json(meta_json_raw, sid).get("workspacePath")
            at_dest = (
                workspace_key == new and workspace_path == new
                and meta_workspace == new and old not in (meta_json_raw or "")
            )
            if not at_dest:
                mismatches = [
                    f"{key}: manifest={item[key]!r}, actual={actual!r}"
                    for key, actual in (
                        ("old_workspace_key", workspace_key),
                        ("old_workspace_path", workspace_path),
                        ("old_meta_workspacePath", meta_workspace),
                    )
                    if item[key] != actual
                ]
                if mismatches:
                    raise RuntimeError(
                        f"preflight: tasks-index before-state mismatch for {sid}: "
                        + "; ".join(mismatches)
                    )
            report["tasks_index"].append({"id": sid, "already_destination": at_dest})
    finally:
        con.close()

    con = _ro(DB_PATH)
    try:
        cur = con.cursor()
        for item in sessions:
            sid = item["id"]
            row = cur.execute(
                "select directory, path, project_id from session where id=?", (sid,)
            ).fetchone()
            if row is None:
                raise RuntimeError(f"preflight: db.sqlite session row not found for {sid}")
            directory, path, project_id = row
            at_dest = directory == new and path == new and project_id == new_project_id
            if not at_dest:
                mismatches = [
                    f"{key}: manifest={item[key]!r}, actual={actual!r}"
                    for key, actual in (
                        ("old_directory", directory),
                        ("old_path", path),
                        ("old_project_id", project_id),
                    )
                    if item[key] != actual
                ]
                if mismatches:
                    raise RuntimeError(
                        f"preflight: db.sqlite before-state mismatch for {sid}: "
                        + "; ".join(mismatches)
                    )
            report["session"].append({"id": sid, "already_destination": at_dest})
    finally:
        con.close()

    report["all_before_state_verified"] = True
    return report


def detect_bom(raw: bytes) -> bool:
    return raw.startswith(b"\xef\xbb\xbf")


def _cf(value: str) -> str:
    """Casefold for case-insensitive Windows-path comparison. Only comparisons
    are normalized; a value left unchanged keeps its original casing."""
    return value.casefold()


def _is_nested(old: str, new: str) -> bool:
    """True when old and new are in a parent/child relationship (either
    direction) rather than side by side. Case-insensitive (Windows paths)."""
    of, nf = _cf(old), _cf(new)
    return nf.startswith(of + "\\") or of.startswith(nf + "\\")


def replace_prefix(value: Any, old: str, new: str) -> tuple[Any, bool]:
    """Nesting-aware, idempotent, boundary-safe workspace-path prefix remap.

    Used by the cleanup surfaces (workflow_run.cwd, setting.json recent/last
    projects, message.data path fields). The primary/secondary grouping stores
    do exact manifest-directed replacement and never call this.

    Precedence:
      1. Exact old root -> ``new`` (checked before the destination guard so a
         source-under-destination exact root is still rewritten).
      2. Already at/under ``new`` -> unchanged. The original ``value.startswith
         (old)`` had neither this guard nor a separator boundary, so when
         ``new`` was nested under ``old`` an already-destination value got
         ``new`` re-applied (doubling), and a sibling like ``…Universe2``
         matched ``…Universe``. Both are fixed here.
      3. A subtree of ``old`` (separator-anchored) -> side-by-side move swaps
         the prefix; a nested move leaves it unchanged (no fabricated path).
      4. Otherwise -> unchanged.
    """
    if not isinstance(value, str):
        return value, False
    vf, of, nf = _cf(value), _cf(old), _cf(new)
    # Case-insensitive comparisons; rewrites use the manifest ``new`` spelling,
    # preserved values keep their original casing. ``len(old)`` is safe because
    # ``old`` is a case-insensitive prefix at that branch.
    if vf == of:
        return new, True
    if vf == nf or vf.startswith(nf + "\\"):
        return value, False
    if vf.startswith(of + "\\"):
        if _is_nested(old, new):
            return value, False
        return new + value[len(old):], True
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

            # Exact approved before-state: the live row must match the
            # manifest's recorded values exactly before it is overwritten.
            mismatches = [
                f"{key}: manifest={item[key]!r}, actual={actual!r}"
                for key, actual in (
                    ("old_workspace_key", workspace_key),
                    ("old_workspace_path", workspace_path),
                    ("old_meta_workspacePath", before_meta_workspace),
                )
                if item[key] != actual
            ]
            if mismatches:
                raise RuntimeError(
                    f"tasks-index before-state mismatch for {sid}: "
                    + "; ".join(mismatches)
                )
            entry["before_state_verified"] = True

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
            # Exact approved before-state for the secondary db.sqlite row.
            mismatches = [
                f"{key}: manifest={item[key]!r}, actual={actual!r}"
                for key, actual in (
                    ("old_directory", directory),
                    ("old_path", path),
                    ("old_project_id", project_id),
                )
                if item[key] != actual
            ]
            if mismatches:
                raise RuntimeError(
                    f"db.sqlite before-state mismatch for {sid}: "
                    + "; ".join(mismatches)
                )
            entry["before_state_verified"] = True
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
        # Escape %, _, and the escape character itself in SQL LIKE patterns.
        # Old workspace paths are user-provided and can contain these chars.
        like_old = old.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        for wf_id, wf_cwd in cur.execute(
            "select id, cwd from workflow_run where cwd like ? escape '\\'",
            (like_old + "%",),
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


def _zcode_process_running() -> bool:
    """True if a zCode process appears to be running.

    Fail-closed: if the probe raises or returns unusable output, we cannot
    prove zCode is closed, so the guard stops the migration rather than
    interpreting an unknown result as "not running"."""
    try:
        out = subprocess.check_output(["tasklist", "/FI", "STATUS eq RUNNING"],
                                        text=True, timeout=5)
    except Exception as exc:
        raise SystemExit(
            f"process probe failed ({exc!r}); cannot prove zCode is closed. "
            "Refusing to proceed — verify manually and retry."
        )
    if not isinstance(out, str) or not out.strip():
        raise SystemExit(
            "process probe returned no output; cannot prove zCode is closed. "
            "Refusing to proceed — verify manually and retry."
        )
    return "zcode.exe" in out.lower() or "z code.exe" in out.lower()


def _non_empty_wal(db_path: Path) -> bool:
    wal = db_path.with_name(db_path.name + "-wal")
    return wal.exists() and wal.stat().st_size > 0


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

    # -- Process + dual-WAL guards (apply only) --
    if apply:
        if _zcode_process_running():
            raise SystemExit("zCode appears to be running. Close it fully before --apply.")
        for db_path, label in ((TASKS_INDEX_PATH, "tasks-index.sqlite"), (DB_PATH, "db.sqlite")):
            if _non_empty_wal(db_path):
                raise SystemExit(
                    f"Non-empty WAL at {db_path.with_name(db_path.name + '-wal')} "
                    f"({label}). zCode may still be running; close it fully before --apply."
                )

    # -- Cross-database preflight: all six exact before-state values across
    #    BOTH databases are validated read-only before either DB is written.
    #    Any mismatch stops here with zero writes. --
    preflight = preflight_before_state(sessions, old, new)

    # -- Backups: BOTH database families (plus setting.json) are backed up
    #    with an explicit original->backup manifest before the first write. --
    backup_manifest: list[dict[str, str]] = []
    backups: list[str] = []
    if apply:
        backups.extend(backup_sqlite_family(TASKS_INDEX_PATH, suffix, True, backup_manifest))
        backups.extend(backup_sqlite_family(DB_PATH, suffix, True, backup_manifest))
        setting_backup = backup(SETTING_PATH, suffix, True)
        if setting_backup:
            backups.append(str(setting_backup))
            backup_manifest.append({"original": str(SETTING_PATH), "backup": str(setting_backup)})

    results: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "backup_run": suffix,
        "backups": backups,
        "preflight": preflight,
    }
    # -- Coordinated operation: both database updates and their post-write
    #    assertions run inside one guarded block. A failure updating or
    #    verifying EITHER database restores BOTH from the verified backups
    #    before the failure is returned. --
    try:
        results["tasks_index"] = migrate_tasks_index(sessions, old, new, apply)
        results["sqlite"] = migrate_sqlite(sessions, old, new, apply)
        results["setting_json"] = migrate_setting_json(old, new, apply)
        results["local_storage"] = reset_local_storage(suffix, apply)
    except BaseException as exc:
        # EVERY failure raised while updating or verifying either database —
        # RuntimeError/SystemExit, sqlite3.Error subclasses, OSError, JSON or
        # Unicode decode errors, unexpected helper exceptions, and even a
        # KeyboardInterrupt — triggers coordinated verified restoration of
        # both database families (plus recorded settings) from the exact
        # backup manifest, then re-raises the ORIGINAL failure. Nothing is
        # swallowed, and an interrupt is never converted into success.
        if apply and backup_manifest:
            try:
                restored = restore_backups(backup_manifest)
            except RuntimeError as restore_exc:
                # Restoration itself failed: surface BOTH failures — the
                # restore error chained onto the original exception.
                results["rollback_performed"] = False
                results["rollback_error"] = str(restore_exc)
                print(json.dumps(results, indent=2, ensure_ascii=False))
                raise restore_exc from exc
            results["restored_from_backups"] = restored
            results["rollback_performed"] = True
            print(json.dumps(results, indent=2, ensure_ascii=False))
        raise
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
