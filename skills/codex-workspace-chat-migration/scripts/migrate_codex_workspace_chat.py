#!/usr/bin/env python3
"""Migrate explicit Codex Desktop chat sessions between workspaces.

This helper is intentionally manifest-driven. It will not discover or guess sessions.
Use --dry-run first; use --apply only while Codex Desktop is fully closed.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Any

CODEX_HOME = Path.home() / ".codex"
GLOBAL_STATE = CODEX_HOME / ".codex-global-state.json"
STATE_DB_CANDIDATES = [
    CODEX_HOME / "state_5.sqlite",
    CODEX_HOME / "sqlite" / "state_5.sqlite",
]
# All backups land in one unified place under the Codex dir, grouped per run.
BACKUP_ROOT = CODEX_HOME / "user-backups"


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("old_workspace") or not data.get("new_workspace"):
        raise SystemExit("manifest requires old_workspace and new_workspace")
    if not isinstance(data.get("sessions"), list) or not data["sessions"]:
        raise SystemExit("manifest requires a non-empty sessions list")
    for item in data["sessions"]:
        if not item.get("id") or not transcript_paths_for_session(item):
            raise SystemExit("each session requires id and at least one transcript path")
    return data


def backup(path: Path, suffix: str, apply: bool) -> Path | None:
    if not path.exists():
        return None
    # Unified, per-run backup folder: ~/.codex/user-backups/<suffix>/<original name>.
    # Original filenames are preserved so a whole run can be deleted as one unit.
    target_dir = BACKUP_ROOT / suffix
    target = target_dir / path.name
    if apply:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return target


def replace_path(value: Any, old: str, new: str) -> Any:
    """Replace old workspace path in structured values, case-insensitively."""
    if isinstance(value, str):
        return re.sub(re.escape(old), lambda _m: new, value, flags=re.IGNORECASE)
    if isinstance(value, list):
        return [replace_path(v, old, new) for v in value]
    if isinstance(value, dict):
        return {k: replace_path(v, old, new) for k, v in value.items()}
    return value


def transcript_paths_for_session(item: dict[str, Any]) -> list[Path]:
    raw: list[str] = []
    values = item.get("transcript_paths_to_migrate")
    if isinstance(values, list) and values:
        raw.extend(str(v) for v in values if v)
    elif item.get("transcript_path"):
        raw.append(str(item["transcript_path"]))
    else:
        for key in ("ui_rollout_path", "rollout_path_from_sqlite"):
            value = item.get(key)
            if value:
                raw.append(str(value))
        for key in ("all_transcript_paths", "additional_transcript_paths"):
            values = item.get(key)
            if isinstance(values, list):
                raw.extend(str(v) for v in values if v)
    seen: set[str] = set()
    paths: list[Path] = []
    for value in raw:
        resolved = str(Path(value))
        if resolved not in seen:
            seen.add(resolved)
            paths.append(Path(value))
    return paths


def discovered_transcript_paths_for_session(item: dict[str, Any]) -> list[Path]:
    raw: list[str] = []
    for key in ("transcript_path", "ui_rollout_path", "rollout_path_from_sqlite"):
        value = item.get(key)
        if value:
            raw.append(str(value))
    for key in ("all_transcript_paths", "additional_transcript_paths"):
        values = item.get(key)
        if isinstance(values, list):
            raw.extend(str(v) for v in values if v)
    seen: set[str] = set()
    paths: list[Path] = []
    for value in raw:
        resolved = str(Path(value))
        if resolved not in seen:
            seen.add(resolved)
            paths.append(Path(value))
    return paths


def candidate_state_dbs(manifest: dict[str, Any]) -> list[Path]:
    raw: list[str] = []
    for key in ("selected_state_db", "state_db_path"):
        value = manifest.get(key)
        if value:
            raw.append(str(value))
    values = manifest.get("candidate_state_dbs")
    if isinstance(values, list):
        raw.extend(str(v) for v in values if v)
    values = manifest.get("state_files", {}).get("candidate_state_dbs") if isinstance(manifest.get("state_files"), dict) else None
    if isinstance(values, list):
        raw.extend(str(v) for v in values if v)
    for item in manifest.get("sessions", []):
        value = item.get("state_db_path")
        if value:
            raw.append(str(value))
    raw.extend(str(p) for p in STATE_DB_CANDIDATES)

    seen: set[str] = set()
    paths: list[Path] = []
    for value in raw:
        path = Path(value)
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            paths.append(path)
    return paths


def inspect_state_db(path: Path, target_ids: set[str]) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "thread_count": None,
        "target_row_counts": {},
        "target_rows_found": 0,
    }
    if not path.exists():
        return info
    uri = path.resolve().as_uri() + "?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        info["error"] = f"open failed: {exc}"
        return info
    try:
        cur = con.cursor()
        table = cur.execute(
            "select name from sqlite_master where type='table' and name='threads'"
        ).fetchone()
        if not table:
            info["error"] = "threads table not found"
            return info
        info["thread_count"] = cur.execute("select count(*) from threads").fetchone()[0]
        for sid in sorted(target_ids):
            count = cur.execute("select count(*) from threads where id=?", (sid,)).fetchone()[0]
            info["target_row_counts"][sid] = count
            if count:
                info["target_rows_found"] += count
        return info
    except sqlite3.Error as exc:
        info["error"] = str(exc)
        return info
    finally:
        con.close()


def select_state_db(manifest: dict[str, Any], sessions: list[dict[str, Any]]) -> tuple[Path, list[dict[str, Any]]]:
    target_ids = {s["id"] for s in sessions}
    inspections = [inspect_state_db(path, target_ids) for path in candidate_state_dbs(manifest)]
    exact_matches = [
        item for item in inspections
        if item.get("exists")
        and item.get("target_row_counts")
        and all(count == 1 for count in item["target_row_counts"].values())
    ]
    if len(exact_matches) == 1:
        return Path(exact_matches[0]["path"]), inspections
    if len(exact_matches) > 1:
        exact_matches.sort(key=lambda item: Path(item["path"]).stat().st_mtime, reverse=True)
        return Path(exact_matches[0]["path"]), inspections

    details = json.dumps(inspections, indent=2)
    raise RuntimeError(f"could not identify exactly one state DB containing all target rows:\n{details}")


def migrate_transcript(path: Path, sid: str, old: str, new: str, apply: bool) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    parts = raw.splitlines(keepends=True)
    seen_session = False
    changed_records = 0
    changed_occurrences = 0
    output: list[str] = []

    for line in parts:
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        if not body.strip():
            output.append(line)
            continue
        obj = json.loads(body)
        typ = obj.get("type")
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
        before = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
        escaped_old = old.replace("\\", "\\\\")
        should_edit = False
        if typ == "session_meta" and payload.get("id") == sid:
            seen_session = True
            should_edit = True
        elif typ == "turn_context":
            should_edit = True
        if should_edit:
            obj = replace_path(obj, old, new)
            after = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
            if after != before:
                changed_records += 1
                changed_occurrences += len(re.findall(re.escape(old), before, flags=re.IGNORECASE))
                output.append(after + newline)
            else:
                output.append(line)
        else:
            output.append(line)

    if not seen_session:
        raise RuntimeError(f"{path}: session_meta id {sid} not found")
    if apply:
        path.write_text("".join(output), encoding="utf-8", newline="")
    return {"transcript": str(path), "changed_records": changed_records, "old_occurrences_in_changed_records": changed_occurrences}


def migrate_global_state(sessions: list[dict[str, Any]], old: str, new: str, manifest: dict[str, Any], apply: bool) -> dict[str, Any]:
    data = json.loads(GLOBAL_STATE.read_text(encoding="utf-8"))
    hints = data.setdefault("thread-workspace-root-hints", {})
    atom = data.setdefault("electron-persisted-atom-state", {})
    perms = atom.get("heartbeat-thread-permissions-by-id", {})
    thread_roots = data.get("thread-writable-roots", {})
    changed = []
    writable_roots_changed = []
    for item in sessions:
        sid = item["id"]
        if hints.get(sid) != new:
            hints[sid] = new
            changed.append(sid)
        if sid in perms:
            policy = perms[sid].get("sandboxPolicy", {})
            if "writableRoots" in policy:
                updated = replace_path(policy["writableRoots"], old, new)
                if updated != policy["writableRoots"]:
                    writable_roots_changed.append(sid)
                policy["writableRoots"] = updated
        if sid in thread_roots:
            updated = replace_path(thread_roots[sid], old, new)
            if updated != thread_roots[sid]:
                writable_roots_changed.append(sid)
            thread_roots[sid] = updated
    cleaned_project_roots: dict[str, list[str]] = {}
    if manifest.get("cleanup_old_project_root") or manifest.get("cleanup_old_workspace_root"):
        for key in ("electron-saved-workspace-roots", "project-order"):
            values = data.get(key)
            if isinstance(values, list):
                new_values = [v for v in values if not (isinstance(v, str) and v.lower() == old.lower())]
                if new_values != values:
                    cleaned_project_roots[key] = [v for v in values if isinstance(v, str) and v.lower() == old.lower()]
                    data[key] = new_values
    if apply:
        GLOBAL_STATE.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    return {
        "global_state": str(GLOBAL_STATE),
        "hint_sessions_changed_or_confirmed": [s["id"] for s in sessions],
        "new_hints_added": changed,
        "writable_roots_changed": sorted(set(writable_roots_changed)),
        "cleaned_project_roots": cleaned_project_roots,
    }


def digest_non_target_rows(cur: sqlite3.Cursor, target_ids: set[str]) -> str:
    h = hashlib.sha256()
    for row in cur.execute("select id,cwd,sandbox_policy from threads order by id"):
        if row[0] in target_ids:
            continue
        h.update(("|".join("" if v is None else str(v) for v in row)).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def migrate_sqlite(state_db: Path, db_inspections: list[dict[str, Any]], sessions: list[dict[str, Any]], old: str, new: str, apply: bool) -> dict[str, Any]:
    target_ids = {s["id"] for s in sessions}
    con = sqlite3.connect(state_db)
    try:
        cur = con.cursor()
        before_count = cur.execute("select count(*) from threads").fetchone()[0]
        before_digest = digest_non_target_rows(cur, target_ids)
        changed = []
        for item in sessions:
            sid = item["id"]
            row = cur.execute("select cwd,sandbox_policy from threads where id=?", (sid,)).fetchone()
            if row is None:
                raise RuntimeError(f"state_5.sqlite threads row not found for {sid}")
            cwd, sandbox_policy = row
            new_cwd = replace_path(cwd, old, new) if cwd else cwd
            if cwd == new_cwd and old not in (sandbox_policy or ""):
                changed.append({"id": sid, "status": "already_destination_or_no_old_path"})
                continue
            policy_obj = json.loads(sandbox_policy) if sandbox_policy else None
            new_policy = json.dumps(replace_path(policy_obj, old, new), separators=(",", ":")) if policy_obj is not None else sandbox_policy
            if apply:
                cur.execute("update threads set cwd=?, sandbox_policy=? where id=?", (new_cwd, new_policy, sid))
                if cur.rowcount != 1:
                    raise RuntimeError(f"unexpected rowcount for {sid}: {cur.rowcount}")
            changed.append({"id": sid, "old_cwd": cwd, "new_cwd": new_cwd})
        if apply:
            con.commit()
            cur.execute("pragma wal_checkpoint(truncate)")
        after_count = cur.execute("select count(*) from threads").fetchone()[0]
        after_digest = digest_non_target_rows(cur, target_ids)
        integrity = cur.execute("pragma integrity_check").fetchone()[0]
        if before_count != after_count:
            raise RuntimeError("threads row count changed unexpectedly")
        if before_digest != after_digest:
            raise RuntimeError("non-target thread rows changed unexpectedly")
        if integrity != "ok":
            raise RuntimeError(f"sqlite integrity_check failed: {integrity}")
        return {
            "state_db": str(state_db),
            "candidate_state_dbs": db_inspections,
            "changed": changed,
            "integrity_check": integrity,
            "thread_count": after_count,
        }
    finally:
        con.close()


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
    state_db, db_inspections = select_state_db(manifest, sessions)
    apply = args.apply
    suffix = "codex-workspace-chat-migration-" + _dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    backups = []
    if apply:
        backups.append(str(backup(GLOBAL_STATE, suffix, True)))
        backups.append(str(backup(state_db, suffix, True)))
        for sidecar in (state_db.with_name(state_db.name + "-wal"), state_db.with_name(state_db.name + "-shm")):
            b = backup(sidecar, suffix, True)
            if b:
                backups.append(str(b))
        transcript_backup_paths: list[Path] = []
        for item in sessions:
            transcript_backup_paths.extend(transcript_paths_for_session(item))
        for path in sorted(set(transcript_backup_paths)):
            backups.append(str(backup(path, suffix, True)))

    results = {
        "mode": "apply" if apply else "dry-run",
        "backups": backups,
        "selected_state_db": str(state_db),
        "candidate_state_dbs": db_inspections,
        "transcripts": [],
    }
    for item in sessions:
        for path in transcript_paths_for_session(item):
            results["transcripts"].append(migrate_transcript(path, item["id"], old, new, apply))
    results["global_state"] = migrate_global_state(sessions, old, new, manifest, apply)
    results["sqlite"] = migrate_sqlite(state_db, db_inspections, sessions, old, new, apply)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
