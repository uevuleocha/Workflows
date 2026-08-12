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
import os
import re
import shutil
import sqlite3
import subprocess
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


def backup(path: Path, suffix: str, apply: bool, backup_manifest: list[dict[str, str]] | None = None) -> Path | None:
    """Back up one file into the unified per-run folder and record an explicit
    original-path -> backup-path entry in ``backup_manifest``.

    Backups are NEVER flattened by basename: each backup lives under a
    collision-free numbered slot (``NNN-<original name>``) so two originals
    that share a filename (e.g. state DBs in different directories) can never
    overwrite each other's backup. Restoration uses only the recorded
    original path, never a guessed location."""
    if not path.exists():
        return None
    target_dir = BACKUP_ROOT / suffix
    slot = len(backup_manifest) if backup_manifest is not None else 0
    target = target_dir / f"{slot:03d}-{path.name}"
    if apply:
        target_dir.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError(f"backup slot collision (should be impossible): {target}")
        shutil.copy2(path, target)
    if backup_manifest is not None:
        backup_manifest.append({"original": str(path.resolve()), "backup": str(target)})
    return target


def _is_nested(old: str, new: str) -> bool:
    """True when old and new are in a parent/child relationship (either
    direction) rather than side by side."""
    lo, ln = old.lower(), new.lower()
    return ln.startswith(lo + "\\") or lo.startswith(ln + "\\")


def remap_path_str(value: str, old: str, new: str) -> str:
    """Nesting-aware, idempotent, boundary-safe remap of a single string.

    Precedence (case-insensitive, matching Codex's original IGNORECASE intent):
      1. Exact old root -> ``new`` (checked first so a source-under-destination
         exact root is rewritten rather than caught by the guard in step 2).
      2. Already at/under ``new`` -> unchanged. Kills the doubling that the old
         global ``re.sub`` produced when ``new`` was nested under ``old`` (an
         already-destination value contains ``old`` as a prefix and had ``new``
         re-applied on top). Also makes the transform idempotent.
      3. A subtree of ``old`` (separator-anchored, so a sibling like
         ``…Universe2`` never matches ``…Universe``) -> side-by-side move swaps
         the prefix; a nested move leaves it unchanged (never fabricates a
         ``new``-relative path).
      4. Otherwise -> unchanged.

    This is intentionally prefix-anchored on whole path *values* rather than the
    original global ``re.sub`` substring rewrite. The substring form both doubled
    already-destination values under nesting and corrupted sibling prefixes
    (``…Universe`` inside ``…Universe2``). The trade-off is that a workspace path
    embedded mid-string (e.g. inside a command-line breadcrumb) is no longer
    rewritten — which is the safe behavior: stamping such a breadcrumb is the
    same fabrication class as the doubling this fix removes.
    """
    prefix = ""
    v = value
    if v.startswith("\\\\?\\"):
        prefix = "\\\\?\\"
        v = v[4:]
    clean_old = old[4:] if old.startswith("\\\\?\\") else old
    clean_new = new[4:] if new.startswith("\\\\?\\") else new

    lv, lo, ln = v.lower(), clean_old.lower(), clean_new.lower()
    if lv == lo:
        return prefix + clean_new
    if lv == ln or lv.startswith(ln + "\\"):
        return value
    if lv.startswith(lo + "\\"):
        if _is_nested(clean_old, clean_new):
            return value
        return prefix + clean_new + v[len(clean_old):]
    return value


def replace_path(value: Any, old: str, new: str) -> Any:
    """Replace old workspace path in structured values, nesting-aware and
    boundary-safe (see ``remap_path_str``)."""
    if isinstance(value, str):
        return remap_path_str(value, old, new)
    if isinstance(value, list):
        return [replace_path(v, old, new) for v in value]
    if isinstance(value, dict):
        return {k: replace_path(v, old, new) for k, v in value.items()}
    return value


def is_doubled_new(value: Any, old: str, new: str) -> bool:
    """True if ``value`` is a doubled-destination corruption: ``new`` with its
    own old-relative tail re-applied on top (the exact shape the old global
    ``re.sub`` produced when ``new`` was nested under ``old``). Such a value
    begins with ``new`` and so must be checked explicitly — a doubled path can
    never pass verification merely because it starts with the destination."""
    if not isinstance(value, str):
        return False
    lv, lo, ln = value.lower(), old.lower(), new.lower()
    if not ln.startswith(lo + "\\"):
        return False
    rel = new[len(old) + 1:]
    doubled = (new + "\\" + rel).lower()
    return lv == doubled or lv.startswith(doubled + "\\")


def transcript_paths_for_session(item: dict[str, Any]) -> list[Path]:
    """Return every authoritative transcript path for a session, unioned and
    deduplicated. The explicit ``transcript_paths_to_migrate`` list is the
    override: when present it alone is authoritative (use it to exclude later
    handoff/review transcripts that merely mention the session ID). Otherwise
    every path source is collected so a single ``transcript_path`` can never
    shadow the UI-facing SQLite ``rollout_path`` or any archived/fork
    transcripts — the original Prompt 6 failure class."""
    raw: list[str] = []
    # Override: explicit migration list
    values = item.get("transcript_paths_to_migrate")
    if isinstance(values, list) and values:
        raw.extend(str(v) for v in values if v)
    else:
        # Union every authoritative source — no elif chain that shadows the
        # UI rollout path.
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
        for v in values:
            if isinstance(v, dict) and "path" in v:
                raw.append(str(v["path"]))
            elif v:
                raw.append(str(v))
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
        # Multiple exact-match state DBs is genuinely ambiguous — a newer
        # mtime is not a safe tiebreaker. Hard-stop rather than guessing.
        exact_matches.sort(key=lambda item: Path(item["path"]).stat().st_mtime, reverse=True)
        details = json.dumps([item for item in exact_matches], indent=2)
        raise RuntimeError(
            f"MULTIPLE exact-match state DB candidates found — cannot disambiguate.\n"
            f"Candidates (sorted by mtime, newest first):\n{details}\n"
            f"Please explicitly select one by setting selected_state_db in the manifest."
        )

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
    # Use .get() instead of .setdefault(): never silently insert an empty key
    # into the persisted global state just because we touched the field.
    hints = data.get("thread-workspace-root-hints")
    if not isinstance(hints, dict):
        hints = {}
    atom = data.get("electron-persisted-atom-state")
    perms = atom.get("heartbeat-thread-permissions-by-id", {}) if isinstance(atom, dict) else {}
    thread_roots = data.get("thread-writable-roots", {})
    if not isinstance(thread_roots, dict):
        thread_roots = {}
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
    # Only persist the keys we actually modified — never insert an empty root.
    if changed:
        data["thread-workspace-root-hints"] = hints
    if writable_roots_changed:
        if "electron-persisted-atom-state" not in data:
            data["electron-persisted-atom-state"] = {}
        data["electron-persisted-atom-state"]["heartbeat-thread-permissions-by-id"] = perms
        data["thread-writable-roots"] = thread_roots
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
        # Post-write doubling guard: re-read every target cwd and refuse to
        # accept a doubled-destination path that begins with ``new`` but carries
        # a re-applied old-relative tail.
        if apply:
            for sid in sorted(target_ids):
                row = cur.execute("select cwd from threads where id=?", (sid,)).fetchone()
                cwd_after = row[0] if row else None
                if is_doubled_new(cwd_after, old, new):
                    raise RuntimeError(
                        f"post-write doubled-destination cwd for {sid}: {cwd_after!r}"
                    )
        return {
            "state_db": str(state_db),
            "candidate_state_dbs": db_inspections,
            "changed": changed,
            "integrity_check": integrity,
            "thread_count": after_count,
        }
    finally:
        con.close()


def _codex_process_running() -> bool:
    """True if a Codex Desktop process appears to be running.

    Fail-closed: if the probe raises or returns something unusable, we cannot
    prove Codex is closed, so the guard treats that as unsafe and stops the
    migration rather than interpreting an unknown result as "not running"."""
    probes = ("codex.exe", "codex")
    try:
        out = subprocess.check_output(["tasklist", "/FI", "STATUS eq RUNNING"],
                                        text=True, timeout=5)
    except Exception as exc:
        raise SystemExit(
            f"process probe failed ({exc!r}); cannot prove Codex Desktop is "
            "closed. Refusing to proceed — verify manually and retry."
        )
    if not isinstance(out, str) or not out.strip():
        raise SystemExit(
            "process probe returned no output; cannot prove Codex Desktop is "
            "closed. Refusing to proceed — verify manually and retry."
        )
    return any(p in out.lower() for p in probes)


def _non_empty_wal(db_path: Path) -> bool:
    """True if the DB's WAL file exists and is non-empty."""
    wal = db_path.with_name(db_path.name + "-wal")
    return wal.exists() and wal.stat().st_size > 0


def restore_backups(backup_manifest: list[dict[str, str]]) -> list[str]:
    """Restore every backed-up file to its RECORDED original path.

    Coordinated restoration after a verification failure: each manifest entry
    is an explicit ``{"original": ..., "backup": ...}`` pair captured when the
    backup was taken. Files are restored only to their recorded original path
    — never to a location guessed from the backup's basename — and each
    restoration is verified byte-for-byte against the backup. Any missing
    backup or failed verification raises, because a partial silent restore is
    worse than a loud one."""
    restored = []
    errors = []
    for entry in backup_manifest:
        bp_path = Path(entry["backup"])
        original = Path(entry["original"])
        if not bp_path.exists():
            errors.append(f"backup file missing, cannot restore {original}: {bp_path}")
            continue
        try:
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bp_path, original)
            if original.read_bytes() != bp_path.read_bytes():
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

    # -- Process + WAL guards (apply only; dry-run is advisory) --
    if apply:
        if _codex_process_running():
            raise SystemExit(
                "Codex Desktop appears to be running. Close it fully before --apply."
            )
        if _non_empty_wal(state_db):
            raise SystemExit(
                f"Non-empty WAL at {state_db.with_name(state_db.name + '-wal')}. "
                "Codex may still be running; close it fully before --apply."
            )

    backup_manifest: list[dict[str, str]] = []
    results: dict[str, Any] = {"mode": "apply" if apply else "dry-run", "backups": backup_manifest}
    try:
        if apply:
            backup(GLOBAL_STATE, suffix, True, backup_manifest)
            backup(state_db, suffix, True, backup_manifest)
            for sidecar in (state_db.with_name(state_db.name + "-wal"), state_db.with_name(state_db.name + "-shm")):
                backup(sidecar, suffix, True, backup_manifest)
            transcript_backup_paths: list[Path] = []
            for item in sessions:
                transcript_backup_paths.extend(transcript_paths_for_session(item))
            for path in sorted(set(transcript_backup_paths), key=str):
                backup(path, suffix, True, backup_manifest)

        results = {
            "mode": "apply" if apply else "dry-run",
            "backups": backup_manifest,
            "selected_state_db": str(state_db),
            "candidate_state_dbs": db_inspections,
            "transcripts": [],
        }
        for item in sessions:
            for path in transcript_paths_for_session(item):
                results["transcripts"].append(migrate_transcript(path, item["id"], old, new, apply))
        results["global_state"] = migrate_global_state(sessions, old, new, manifest, apply)
        results["sqlite"] = migrate_sqlite(state_db, db_inspections, sessions, old, new, apply)

        # -- Post-write re-parse verification (apply only) --
        if apply:
            for item in sessions:
                # Verify each transcript at its RECORDED authoritative path —
                # the exact path that was migrated in place. Never guess a
                # basename under CODEX_HOME: a missing recorded path is a
                # verification failure, not a prompt to search elsewhere.
                for path in transcript_paths_for_session(item):
                    if not path.exists():
                        raise RuntimeError(f"transcript missing after write at recorded path: {path}")
                    # Re-parse every line; confirm session_meta.id is present
                    raw = path.read_text(encoding="utf-8")
                    found = False
                    for line in raw.splitlines():
                        if not line.strip():
                            continue
                        obj = json.loads(line)
                        if obj.get("type") == "session_meta" and obj.get("payload", {}).get("id") == item["id"]:
                            found = True
                            break
                    if not found:
                        raise RuntimeError(f"session_meta id={item['id']} not found in {path} after write")
            # Re-parse global state. The authoritative workspace-root hint must
            # EXIST and equal the intended destination for every migrated
            # session — an absent hint is a failure, not a pass.
            gs = json.loads(GLOBAL_STATE.read_text(encoding="utf-8"))
            for item in sessions:
                hint_val = gs.get("thread-workspace-root-hints", {}).get(item["id"])
                if hint_val is None:
                    raise RuntimeError(
                        f"global-state hint missing for {item['id']} after write (expected {new})"
                    )
                if hint_val != new:
                    raise RuntimeError(f"global-state hint mismatch for {item['id']}: {hint_val} (expected {new})")

        results["post_write_verified"] = True

    except (RuntimeError, SystemExit):
        if apply and backup_manifest:
            restored = restore_backups(backup_manifest)
            results["restored_from_backups"] = restored
            results["rollback_performed"] = True
            print(json.dumps(results, indent=2))
        raise

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
