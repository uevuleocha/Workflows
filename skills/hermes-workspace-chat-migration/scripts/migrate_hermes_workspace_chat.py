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
import shutil
import sqlite3
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
    con = sqlite3.connect(STATE_DB_PATH)
    try:
        cur = con.cursor()

        # Capture before-state for non-target verification
        before_count = cur.execute("select count(*) from sessions").fetchone()[0]
        before_digest = digest_sessions_non_target(cur, target_ids)

        changed = []
        for item in sessions:
            sid = item["id"]
            row = cur.execute(
                "select cwd, git_repo_root from sessions where id=?", (sid,)
            ).fetchone()
            if row is None:
                raise RuntimeError(
                    f"state.db sessions row not found for {sid}"
                )

            old_cwd, old_git_repo_root = row

            # Determine the new git_repo_root:
            # - Use manifest's new_git_repo_root if provided
            # - Otherwise default to the new workspace (same as cwd)
            new_git_repo_root = item.get("new_git_repo_root", new)

            entry = {
                "id": sid,
                "old_cwd": old_cwd,
                "old_git_repo_root": old_git_repo_root,
                "new_cwd": new,
                "new_git_repo_root": new_git_repo_root,
            }

            # Idempotency check: skip if already at destination
            if old_cwd == new and (old_git_repo_root == new_git_repo_root or old_git_repo_root == new):
                entry["status"] = "already_destination"
                changed.append(entry)
                continue

            if apply:
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

        if apply:
            con.commit()
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
            verification.append(
                {
                    "id": sid,
                    "cwd": v_cwd,
                    "git_repo_root": v_git_repo_root,
                    "cwd_is_destination": v_cwd == new,
                    "git_repo_root_is_destination": (
                        v_git_repo_root == new
                        or v_git_repo_root == sessions_by_id(sid, sessions).get(
                            "new_git_repo_root", new
                        )
                    ),
                }
            )

        # Check no target row still holds the old workspace
        old_workspace_rows = cur.execute(
            "select count(*) from sessions where cwd=?", (old,)
        ).fetchone()[0]

        return {
            "db": str(STATE_DB_PATH),
            "changed": changed,
            "verification": verification,
            "old_workspace_rows_remaining": old_workspace_rows,
            "integrity_check": integrity,
            "sessions_count": after_count,
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

    # WAL guard: check if state.db-wal is being actively written
    wal_path = STATE_DB_PATH.with_name(STATE_DB_PATH.name + "-wal")
    if wal_path.exists() and apply:
        import time

        size1 = wal_path.stat().st_size
        time.sleep(0.3)
        size2 = wal_path.stat().st_size
        if size1 > 0 and size2 != size1:
            raise SystemExit(
                f"WAL guard: {wal_path} is being actively written "
                f"(size changed {size1} -> {size2} in 0.3s). "
                "Hermes appears to be running. Close it fully before applying."
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
    results["state_db"] = migrate_state_db(sessions, old, new, apply)

    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
