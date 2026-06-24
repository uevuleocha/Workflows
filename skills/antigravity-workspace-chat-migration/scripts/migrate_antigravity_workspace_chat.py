#!/usr/bin/env python3
"""Migrate explicit Antigravity Desktop conversations between workspaces/projects.

Manifest-driven. It will not discover or guess conversations.
Use --dry-run first; use --apply only while Antigravity Desktop is fully closed.

The grouping key is the per-conversation protobuf blob's **Project UUID (Field 18)**,
resolved via the Project Registry — NOT the workspace URI. This helper:
  - reassigns Field 18 -> the destination Project UUID (the move), and
  - rewrites the workspace URI -> the destination URI (resume correctness),
via protobuf decode -> modify -> re-encode (blackboxprotobuf). It does NOT touch
agyhub_summaries_proto.pb (a derived index Antigravity regenerates on launch).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import sqlite3
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Any

import blackboxprotobuf

GEMINI_HOME = Path.home() / ".gemini"
CONV_DIR = GEMINI_HOME / "antigravity" / "conversations"
REG_DIR = GEMINI_HOME / "config" / "projects"
STATE_VSCDB = Path.home() / "AppData" / "Roaming" / "Antigravity" / "User" / "globalStorage" / "state.vscdb"
BACKUP_ROOT = GEMINI_HOME / "user-backups"


# ---- URI helpers ----
def _enc(rest: str) -> str:
    return urllib.parse.quote(rest.replace("\\", "/"), safe="/")


def to_blob_uri(path: str) -> str:
    """C:\\Users\\Admin\\Uzzys Universe -> file:///c:/Users/Admin/Uzzys%20Universe"""
    return "file:///" + path[0].lower() + ":" + _enc(path[2:])


def to_vscdb_uri(path: str) -> str:
    """C:\\Users\\Admin\\Uzzys Universe -> file:///c%3A/Users/Admin/Uzzys%20Universe"""
    return "file:///" + path[0].lower() + "%3A" + _enc(path[2:])


# ---- manifest ----
def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("destination_workspace") or not data.get("destination_project_uuid"):
        raise SystemExit("manifest requires destination_workspace and destination_project_uuid")
    if not isinstance(data.get("conversations"), list) or not data["conversations"]:
        raise SystemExit("manifest requires a non-empty conversations list")
    for c in data["conversations"]:
        if not c.get("id"):
            raise SystemExit("each conversation requires an id")
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


def verify_destination_project(dest_uuid: str, dest_workspace: str) -> dict[str, Any]:
    """Read-only: confirm the destination Project exists and its folderUri matches."""
    f = REG_DIR / f"{dest_uuid}.json"
    if not f.exists():
        return {"exists": False, "reason": f"no registry json for {dest_uuid} — open the destination folder in Antigravity once"}
    d = json.loads(f.read_text(encoding="utf-8"))
    uri = None
    for r in (d.get("projectResources", {}) or {}).get("resources", []) or []:
        gf = r.get("gitFolder") or {}
        if gf.get("folderUri"):
            uri = gf["folderUri"]
            break
    expected = to_vscdb_uri(dest_workspace)
    return {"exists": True, "name": d.get("name"), "folderUri": uri,
            "folderUri_matches": (uri == expected), "expected": expected}


# ---- protobuf message walking ----
def _collect_uris(msg: Any, acc: list[bytes]) -> None:
    if isinstance(msg, (bytes, bytearray)):
        if bytes(msg).startswith(b"file:///"):
            acc.append(bytes(msg))
    elif isinstance(msg, dict):
        for v in msg.values():
            _collect_uris(v, acc)
    elif isinstance(msg, list):
        for v in msg:
            _collect_uris(v, acc)


def discover_source_uri(msg: Any) -> bytes | None:
    acc: list[bytes] = []
    _collect_uris(msg, acc)
    if not acc:
        return None
    # the workspace root URI is the most frequent file:/// value in the blob
    return Counter(acc).most_common(1)[0][0]


def replace_bytes(msg: Any, old: bytes, new: bytes) -> Any:
    if isinstance(msg, (bytes, bytearray)):
        b = bytes(msg)
        return b.replace(old, new) if old in b else b
    if isinstance(msg, dict):
        return {k: replace_bytes(v, old, new) for k, v in msg.items()}
    if isinstance(msg, list):
        return [replace_bytes(v, old, new) for v in msg]
    return msg


def migrate_conversation(cid: str, dest_uuid: str, dest_blob_uri: str, apply: bool, suffix: str) -> dict[str, Any]:
    db = CONV_DIR / f"{cid}.db"
    if not db.exists():
        raise SystemExit(f"conversation DB not found: {db}")
    wal = db.with_suffix(".db-wal")
    if apply and wal.exists() and wal.stat().st_size > 0:
        raise SystemExit(f"{db.name} has a non-empty WAL ({wal.stat().st_size} B) — Antigravity still running? Close it first.")

    backup(db, suffix, apply)
    for sc in (db.with_suffix(".db-wal"), db.with_suffix(".db-shm")):
        backup(sc, suffix, apply)

    conn = sqlite3.connect(str(db))
    try:
        row = conn.execute("SELECT id, data FROM trajectory_metadata_blob LIMIT 1").fetchone()
        blob_id, blob = row
        msg, td = blackboxprotobuf.decode_message(blob)

        src_uri = discover_source_uri(msg)
        changed: list[str] = []
        new_msg = msg

        # URI rewrite (resume correctness)
        dest_uri_b = dest_blob_uri.encode("utf-8")
        if src_uri and src_uri != dest_uri_b:
            new_msg = replace_bytes(new_msg, src_uri, dest_uri_b)
            changed.append(f"URI {src_uri.decode('latin1')} -> {dest_blob_uri}")

        # Field 18 reassignment (THE grouping fix)
        cur18 = new_msg.get("18")
        old18 = cur18.decode() if isinstance(cur18, (bytes, bytearray)) else None
        if isinstance(cur18, (bytes, bytearray)) and len(cur18) == 36 and cur18 != dest_uuid.encode():
            new_msg["18"] = dest_uuid.encode("utf-8")
            changed.append(f"Field18 {old18} -> {dest_uuid}")

        new_blob = blackboxprotobuf.encode_message(new_msg, td)
        blackboxprotobuf.decode_message(new_blob)  # parse-verify

        result = {
            "conversation": cid, "db": str(db),
            "original_size": len(blob), "new_size": len(new_blob),
            "source_uri": src_uri.decode("latin1") if src_uri else None,
            "old_field18": old18, "new_field18": dest_uuid,
            "changes": changed,
        }

        if apply:
            conn.execute("UPDATE trajectory_metadata_blob SET data=? WHERE id=?", (new_blob, blob_id))
            conn.commit()
            result["integrity_check"] = conn.execute("PRAGMA integrity_check").fetchone()[0]
        else:
            result["integrity_check"] = "dry-run"
        return result
    finally:
        conn.close()


def migrate_cascademap(conv_ids: list[str], dest_workspace: str, apply: bool, suffix: str) -> dict[str, Any]:
    """Optional Layer 2: ensure the destination workspace URI is present in the cascade map."""
    if not STATE_VSCDB.exists():
        return {"skipped": "state.vscdb not found"}
    backup(STATE_VSCDB, suffix, apply)
    dest_uri = to_vscdb_uri(dest_workspace)
    conn = sqlite3.connect(str(STATE_VSCDB))
    try:
        row = conn.execute("SELECT value FROM ItemTable WHERE key='google.antigravity'").fetchone()
        if not row:
            return {"skipped": "google.antigravity key absent"}
        data = json.loads(row[0])
        cm = data.get("antigravity.workspaceCascadeMap", {})
        change = "no change (already present)"
        if dest_uri not in cm:
            cm[dest_uri] = conv_ids[0]
            data["antigravity.workspaceCascadeMap"] = cm
            change = f"added {dest_uri} -> {conv_ids[0]}"
            if apply:
                conn.execute("UPDATE ItemTable SET value=? WHERE key='google.antigravity'",
                             (json.dumps(data, separators=(",", ":"), ensure_ascii=False),))
                conn.commit()
        return {"cascademap": change}
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Antigravity workspace chat migration")
    parser.add_argument("manifest", type=Path)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    m = load_manifest(args.manifest)
    dest_ws = m["destination_workspace"]
    dest_uuid = m["destination_project_uuid"]
    dest_blob_uri = to_blob_uri(dest_ws)
    apply = args.apply
    suffix = "antigravity-workspace-chat-migration-" + _dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    proj = verify_destination_project(dest_uuid, dest_ws)
    if not proj.get("exists"):
        raise SystemExit(f"destination project check FAILED: {proj.get('reason')}")
    if not proj.get("folderUri_matches"):
        print(f"  WARNING: destination project folderUri {proj.get('folderUri')} != expected {proj.get('expected')}")

    results: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "destination_workspace": dest_ws,
        "destination_project_uuid": dest_uuid,
        "destination_blob_uri": dest_blob_uri,
        "destination_project": proj,
        "conversations": [],
    }
    ids = [c["id"] for c in m["conversations"]]
    for c in m["conversations"]:
        results["conversations"].append(migrate_conversation(c["id"], dest_uuid, dest_blob_uri, apply, suffix))
    results["layer2"] = migrate_cascademap(ids, dest_ws, apply, suffix)

    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
