#!/usr/bin/env python3
"""Migrate explicit Hermes Desktop chat sessions between workspaces.

This helper is intentionally manifest-driven. It will not discover or guess
sessions. Use --dry-run first; use --apply only while Hermes Desktop is fully
closed.

Layer 1 (PRIMARY, the only layer) - ~/AppData/Local/hermes/state.db, table `sessions`:
    rewrite `cwd` (grouping signal + resume working directory) and
    `git_repo_root` (auto-project fallback grouping).

Never rewrite messages.content, system_prompt, or any prose. Never touch
projects.db. The migration is a pure two-column UPDATE on sessions.
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

HERMES_HOME = Path.home() / "AppData" / "Local" / "hermes"
STATE_DB_PATH = HERMES_HOME / "state.db"

# All backups land in one unified place under the Hermes dir, grouped per run.
BACKUP_ROOT = HERMES_HOME / "user-backups"


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


def backup(path: Path, suffix: str, apply: bool) -> Path | None:
    if not path.exists():
        return None
    target_dir = BACKUP_ROOT / suffix
    target = target_dir / path.name
    if apply:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return target


def backup_sqlite_family(db_path: Path, suffix: str, apply: bool) -> list[str]:
    """Back up the DB plus its -wal and -shm sidecars if they exist."""
    paths = [
        db_path,
        db_path.with_name(db_path.name + "-wal"),
        db_path.with_name(db_path.name + "-shm"),
    ]
    backups: list[str] = []
    for path in paths:
        target = backup(path, suffix, apply)
        if target:
            backups.append(str(target))
    return backups


def row_digest(rows: list[tuple[Any, ...]]) -> str:
    """SHA-256 digest of a list of rows for non-target verification."""
    h = hashlib.sha256()
    for row in rows:
        h.update(
            json.dumps(row, ensure_ascii=False, sort_keys=True, default=str).encode(
                "utf-8"
            )
        )
        h.update(b"\n")
    return h.hexdigest()


def digest_sessions_non_target(cur: sqlite3.Cursor, target_ids: set[str]) -> str:
    """Hash all session rows that are NOT migration targets, to prove they
    didn't change."""
    rows = []
    for row in cur.execute(
        "select id, cwd, git_repo_root from sessions order by id"
    ):
        if row[0] not in target_ids:
            rows.append(row)
    return row_digest(rows)


def migrate_state_db(
    sessions: list[dict[str, Any]],
    old: str,
    new: str,
    apply: bool,
) -> dict[str, Any]:
    """The core migration: UPDATE sessions SET cwd=?, git_repo_root=? WHERE id=?.

    This is the single layer Hermes needs. No transcript files, no global state,
    no protobuf, no sidecar folders — just two columns in one table.
    """
    target_ids = {s["id"] for s in sessions}
    # Preflight / dry-run ALWAYS opens read-only.  Apply opens read-write.
    uri = STATE_DB_PATH.resolve().as_uri()
    if apply:
        con = sqlite3.connect(STATE_DB_PATH)
    else:
        con = sqlite3.connect(uri + "?mode=ro", uri=True)
    try:
        cur = con.cursor()

        # Capture before-state for non-target verification
        before_count = cur.execute("select count(*) from sessions").fetchone()[0]
        before_digest = digest_sessions_non_target(cur, target_ids)

        # Enforce exact manifest before-state for every target row.
        manifest_by_id = {s["id"]: s for s in sessions}
        preflight_verification: list[dict[str, Any]] = []
        for sid in sorted(target_ids):
            row = cur.execute(
                "select cwd, git_repo_root from sessions where id=?", (sid,)
            ).fetchone()
            if row is None:
                raise RuntimeError(
                    f"state.db sessions row not found for {sid}"
                )
            actual_cwd, actual_git_repo_root = row
            manifest_entry = manifest_by_id[sid]
            # Exact before-state from manifest (if declared)
            declared_old_cwd = manifest_entry.get("old_cwd")
            declared_old_git = manifest_entry.get("old_git_repo_root")
            if declared_old_cwd is not None and actual_cwd != declared_old_cwd:
                raise RuntimeError(
                    f"before-state mismatch for {sid}: "
                    f"manifest says old_cwd={declared_old_cwd!r}, actual cwd={actual_cwd!r}"
                )
            if declared_old_git is not None and actual_git_repo_root != declared_old_git:
                raise RuntimeError(
                    f"before-state mismatch for {sid}: "
                    f"manifest says old_git_repo_root={declared_old_git!r}, actual git_repo_root={actual_git_repo_root!r}"
                )
            preflight_verification.append({
                "id": sid,
                "old_cwd": actual_cwd,
                "old_git_repo_root": actual_git_repo_root,
                "manifest_matches": True,
            })

        if not apply:
            return {
                "preflight_only": True,
                "db": str(STATE_DB_PATH),
                "sessions_count": before_count,
                "preflight_verification": preflight_verification,
            }

        # -- Apply phase: explicit write transaction --
        new_git_repo_root_global = new
        changed = []
        cur.execute("BEGIN IMMEDIATE")
        for item in sessions:
            sid = item["id"]
            row = cur.execute(
                "select cwd, git_repo_root from sessions where id=?", (sid,)
            ).fetchone()
            # Re-read within transaction to confirm nothing shifted
            old_cwd, old_git_repo_root = row

            new_git_repo_root = item.get("new_git_repo_root", new_git_repo_root_global)
            entry = {
                "id": sid,
                "old_cwd": old_cwd,
                "old_git_repo_root": old_git_repo_root,
                "new_cwd": new,
                "new_git_repo_root": new_git_repo_root,
            }

            # Exact idempotency: both cwd AND git_repo_root must match destination
            if old_cwd == new and old_git_repo_root == new_git_repo_root:
                entry["status"] = "already_destination"
                changed.append(entry)
                continue

            cur.execute(
                "update sessions set cwd=?, git_repo_root=? where id=?",
                (new, new_git_repo_root, sid),
            )
            if cur.rowcount != 1:
                raise RuntimeError(
                    f"unexpected sessions rowcount for {sid}: {cur.rowcount}"
                )
            entry["status"] = "migrated"
            changed.append(entry)

        cur.execute("COMMIT")
        cur.execute("pragma wal_checkpoint(truncate)")

        # Post-write verification
        after_count = cur.execute("select count(*) from sessions").fetchone()[0]
        after_digest = digest_sessions_non_target(cur, target_ids)
        integrity = cur.execute("pragma integrity_check").fetchone()[0]

        if before_count != after_count:
            raise RuntimeError("sessions row count changed unexpectedly")
        if before_digest != after_digest:
            raise RuntimeError("non-target session rows changed unexpectedly")
        if integrity != "ok":
            raise RuntimeError(f"state.db integrity_check failed: {integrity}")

        # Per-session verification
        verification = []
        for sid in target_ids:
            row = cur.execute(
                "select cwd, git_repo_root from sessions where id=?", (sid,)
            ).fetchone()
            if row is None:
                raise RuntimeError(f"sessions row disappeared for {sid}")
            v_cwd, v_git_repo_root = row
            expected_git = sessions_by_id(sid, sessions).get("new_git_repo_root", new)
            verification.append(
                {
                    "id": sid,
                    "cwd": v_cwd,
                    "git_repo_root": v_git_repo_root,
                    "cwd_is_destination": v_cwd == new,
                    "git_repo_root_is_destination": v_git_repo_root == expected_git,
                }
            )
            if not (v_cwd == new):
                raise RuntimeError(f"post-write cwd mismatch for {sid}: {v_cwd!r}")
            if not (v_git_repo_root == expected_git):
                raise RuntimeError(f"post-write git_repo_root mismatch for {sid}: {v_git_repo_root!r}")

        # Target-scoped stale check: only the target sessions are verified,
        # not a global cwd sweep that can miss descendants.
        old_workspace_rows = cur.execute(
            "select count(*) from sessions where id in (%s) and cwd=?"
            % ",".join("?" for _ in target_ids),
            tuple(target_ids) + (old,),
        ).fetchone()[0]

        return {
            "db": str(STATE_DB_PATH),
            "changed": changed,
            "verification": verification,
            "old_workspace_rows_remaining": old_workspace_rows,
            "integrity_check": integrity,
            "sessions_count": after_count,
            "transaction": {"begin": "IMMEDIATE", "commit": True},
        }
    finally:
        con.close()


def sessions_by_id(
    sid: str, sessions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Helper: find a session entry by id from the manifest."""
    for s in sessions:
        if s["id"] == sid:
            return s
    return {}


def _hermes_process_running() -> bool:
    """True if a Hermes process appears to be running.

    Fail-closed: if the probe raises or returns unusable output, we cannot
    prove Hermes is closed, so the guard stops the migration rather than
    interpreting an unknown result as "not running"."""
    try:
        out = subprocess.check_output(["tasklist", "/FI", "STATUS eq RUNNING"],
                                        text=True, timeout=5)
    except Exception as exc:
        raise SystemExit(
            f"process probe failed ({exc!r}); cannot prove Hermes is closed. "
            "Refusing to proceed — verify manually and retry."
        )
    if not isinstance(out, str) or not out.strip():
        raise SystemExit(
            "process probe returned no output; cannot prove Hermes is closed. "
            "Refusing to proceed — verify manually and retry."
        )
    return "hermes.exe" in out.lower()


def restore_backups(backup_records: list[str]) -> list[str]:
    """Copy backed-up files back to their original locations under HERMES_HOME."""
    restored = []
    for bp in backup_records:
        bp_path = Path(bp)
        if not bp_path.exists():
            continue
        name = bp_path.name
        # Restore to the expected platform location
        dest = HERMES_HOME / name if "user-backups" not in str(bp_path.parent) else None
        if dest is None:
            dest = HERMES_HOME / name
        shutil.copy2(bp_path, dest)
        restored.append(str(dest))
    return restored


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hermes workspace chat migration"
    )
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
        "hermes-workspace-chat-migration-"
        + _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    )

    # -- Process guard (apply only) --
    if apply and _hermes_process_running():
        raise SystemExit(
            "Hermes Desktop appears to be running (hermes.exe detected). "
            "Close it fully before --apply."
        )

    # -- WAL guard: refuse ANY non-empty WAL, not merely a changing WAL.
    #    A fixed-size non-empty WAL that isn't growing is still a live
    #    application's pending work. --
    wal_path = STATE_DB_PATH.with_name(STATE_DB_PATH.name + "-wal")
    if apply and wal_path.exists() and wal_path.stat().st_size > 0:
        raise SystemExit(
            f"Non-empty WAL at {wal_path} ({wal_path.stat().st_size} bytes). "
            "Hermes may still be running; close it fully before --apply. "
            "A non-empty WAL that is not actively growing is still unsafe."
        )

    # Backups
    backups: list[str] = []
    if apply:
        backups.extend(backup_sqlite_family(STATE_DB_PATH, suffix, True))

    results: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "backup_run": suffix,
        "backups": backups,
        "old_workspace": old,
        "new_workspace": new,
    }

    # -- Coordinated backup restoration on failure --
    try:
        results["state_db"] = migrate_state_db(sessions, old, new, apply)
        results["post_write_verified"] = True
    except (RuntimeError, SystemExit):
        if apply and backups:
            restored = restore_backups(backups)
            results["restored_from_backups"] = restored
            results["rollback_performed"] = True
            print(json.dumps(results, indent=2, ensure_ascii=False))
        raise

    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
