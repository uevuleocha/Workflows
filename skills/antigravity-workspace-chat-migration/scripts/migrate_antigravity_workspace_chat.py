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
import uuid as _uuid
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


# The only field paths in the trajectory metadata blob where the workspace
# URI is known (schema-evidenced) to live: field 1's subfield 1, and top-level
# field 7. Field numbers come from the decoded blackboxprotobuf dict keys;
# repeated-field list indices are ignored when matching a permitted path.
PERMITTED_URI_FIELD_PATHS = ("1.1", "7")


def replace_uri_in_enumerated_fields(
    msg: Any,
    old_uri: bytes,
    new_uri: bytes,
    permitted_paths: tuple[str, ...] = PERMITTED_URI_FIELD_PATHS,
) -> tuple[Any, int, list[str]]:
    """Replace the source URI ONLY at enumerated, permitted field paths.

    This is deliberately NOT a recursive replace-any-matching-bytes walk:
    - an exact match at a permitted path is replaced;
    - an exact match at any OTHER path is a hard stop (the blob holds the URI
      somewhere the schema does not enumerate — inspect before migrating);
    - a substring match anywhere (a field that merely *contains* the URI) is a
      hard stop as ambiguous — partial rewrites of unidentified structures are
      never safe.
    Returns (modified_msg, replacement_count, replaced_paths)."""
    replaced = 0
    replaced_paths: list[str] = []
    out_of_scope: list[str] = []
    ambiguous: list[str] = []

    def _walk(obj: Any, field_path: str, display_path: str) -> Any:
        nonlocal replaced
        if isinstance(obj, (bytes, bytearray)):
            b = bytes(obj)
            if b == old_uri:
                if field_path in permitted_paths:
                    replaced += 1
                    replaced_paths.append(display_path)
                    return new_uri
                out_of_scope.append(display_path)
                return b
            if old_uri in b:
                ambiguous.append(display_path)
            return b
        if isinstance(obj, dict):
            return {
                k: _walk(
                    v,
                    f"{field_path}.{k}" if field_path else str(k),
                    f"{display_path}.{k}" if display_path else str(k),
                )
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            # Repeated field: list indices do not change the field path.
            return [
                _walk(v, field_path, f"{display_path}[{i}]")
                for i, v in enumerate(obj)
            ]
        return obj

    new_msg = _walk(msg, "", "")
    if ambiguous:
        raise SystemExit(
            "AMBIGUOUS URI matches (fields that contain but do not equal the "
            f"source URI) at: {ambiguous}. Refusing to rewrite — inspect the "
            "blob manually."
        )
    if out_of_scope:
        raise SystemExit(
            "source URI found at NON-enumerated field path(s): "
            f"{out_of_scope} (permitted: {list(permitted_paths)}). Refusing to "
            "rewrite outside the schema-evidenced locations — inspect the blob "
            "manually."
        )
    return new_msg, replaced, replaced_paths


def _field18_hard_fail(cur18: Any, cid: str) -> tuple[str, bytes]:
    """Hard-fail if Field 18 is missing, invalid, or unmodifiable.
    Returns (old_uuid_str, new_validated_bytes) for a valid src UUID."""
    if cur18 is None:
        raise SystemExit(
            f"Field 18 is MISSING for conversation {cid}. "
            "Cannot migrate a conversation without a source Project UUID."
        )
    if not isinstance(cur18, (bytes, bytearray)):
        raise SystemExit(
            f"Field 18 is not bytes for {cid}: {type(cur18).__name__}. "
            "Unexpected protobuf type — inspect manually."
        )
    if len(cur18) != 36:
        raise SystemExit(
            f"Field 18 length is {len(cur18)}, not 36, for {cid}. "
            "Cannot reassign a non-UUID field."
        )
    try:
        old = cur18.decode("ascii")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Field 18 is not ASCII-decodable for {cid}: {exc}")
    # Real UUID parsing, not a length/dash heuristic.
    try:
        parsed = _uuid.UUID(old)
    except ValueError:
        raise SystemExit(
            f"Field 18 decoded value does not parse as a UUID for {cid}: {old!r}"
        )
    if str(parsed) != old.lower():
        raise SystemExit(
            f"Field 18 value is not in canonical UUID form for {cid}: {old!r}"
        )
    return old, old.encode("utf-8")


def verify_destination_project(dest_uuid: str, dest_workspace: str) -> dict[str, Any]:
    """Read-only: confirm the destination Project exists and verify ALL resources,
    not only the first match."""
    f = REG_DIR / f"{dest_uuid}.json"
    if not f.exists():
        return {"exists": False, "reason": f"no registry json for {dest_uuid} — open the destination folder in Antigravity once"}
    d = json.loads(f.read_text(encoding="utf-8"))
    resources = (d.get("projectResources", {}) or {}).get("resources", []) or []
    expected = to_vscdb_uri(dest_workspace)
    # Check every resource, not just the first
    matches: list[dict[str, Any]] = []
    verified_all = True
    for r in resources:
        gf = r.get("gitFolder") or {}
        uri = gf.get("folderUri")
        if uri:
            match = uri == expected
            matches.append({"folderUri": uri, "matches": match})
            if not match:
                verified_all = False
    if not matches:
        return {"exists": True, "name": d.get("name"), "resources_found": 0,
                "expected": expected, "verified_all": False,
                "reason": "no gitFolder resources found"}
    return {"exists": True, "name": d.get("name"), "resources": matches,
            "expected": expected, "verified_all": verified_all,
            "match_count": sum(1 for m in matches if m["matches"]),
            "total_resources": len(matches)}


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
        try:
            row = conn.execute("SELECT id, data FROM trajectory_metadata_blob LIMIT 1").fetchone()
        except sqlite3.Error as exc:
            raise SystemExit(
                f"cannot read trajectory_metadata_blob for {cid}: {exc}"
            )
        if row is None:
            # Graceful stop, not an unpacking TypeError: an expected row that
            # is absent means this conversation DB is not migratable as-is.
            raise SystemExit(
                f"trajectory_metadata_blob has no row for conversation {cid} "
                f"({db}). Cannot migrate — inspect the conversation DB manually."
            )
        blob_id, blob = row
        msg, td = blackboxprotobuf.decode_message(blob)

        src_uri = discover_source_uri(msg)
        changed: list[str] = []
        new_msg = msg

        # URI rewrite (resume correctness) — targeted replacement in identified
        # scalar fields only, not recursively everywhere.
        dest_uri_b = dest_blob_uri.encode("utf-8")
        if src_uri and src_uri != dest_uri_b:
            new_msg, uri_replaced, uri_paths = replace_uri_in_enumerated_fields(new_msg, src_uri, dest_uri_b)
            changed.append(
                f"URI {src_uri.decode('latin1')} -> {dest_blob_uri} "
                f"({uri_replaced} enumerated field(s): {uri_paths})"
            )

        # Field 18 reassignment (THE grouping fix) — hard-fail on missing/invalid
        cur18 = new_msg.get("18")
        old18, old18_bytes = _field18_hard_fail(cur18, cid)
        if old18_bytes == dest_uuid.encode("utf-8"):
            # Already at destination — idempotent
            status_18 = "already_destination"
        else:
            new_msg["18"] = dest_uuid.encode("utf-8")
            changed.append(f"Field18 {old18} -> {dest_uuid}")
            status_18 = "migrated"

        new_blob = blackboxprotobuf.encode_message(new_msg, td)
        blackboxprotobuf.decode_message(new_blob)  # parse-verify

        result = {
            "conversation": cid, "db": str(db),
            "original_size": len(blob), "new_size": len(new_blob),
            "source_uri": src_uri.decode("latin1") if src_uri else None,
            "old_field18": old18, "new_field18": status_18,
            "changes": changed,
        }

        if apply:
            conn.execute("UPDATE trajectory_metadata_blob SET data=? WHERE id=?", (new_blob, blob_id))
            conn.commit()
            # Verify the persisted Field 18 value
            re_read = conn.execute("SELECT data FROM trajectory_metadata_blob WHERE id=?", (blob_id,)).fetchone()[0]
            re_msg, _ = blackboxprotobuf.decode_message(re_read)
            persisted_18 = re_msg.get("18")
            persisted_val = persisted_18.decode("ascii") if isinstance(persisted_18, (bytes, bytearray)) else None
            if persisted_val != dest_uuid:
                raise RuntimeError(
                    f"persisted Field 18 mismatch for {cid}: {persisted_val!r} (expected {dest_uuid})"
                )
            result["persisted_field18_verified"] = True
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
    # Real UUID validation of the destination Project UUID before anything else.
    try:
        parsed_dest = _uuid.UUID(str(dest_uuid))
    except ValueError:
        raise SystemExit(
            f"destination_project_uuid does not parse as a UUID: {dest_uuid!r}"
        )
    if str(parsed_dest) != str(dest_uuid).lower():
        raise SystemExit(
            f"destination_project_uuid is not in canonical UUID form: {dest_uuid!r}"
        )
    dest_blob_uri = to_blob_uri(dest_ws)
    apply = args.apply
    suffix = "antigravity-workspace-chat-migration-" + _dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    proj = verify_destination_project(dest_uuid, dest_ws)
    if not proj.get("exists"):
        raise SystemExit(f"destination project check FAILED: {proj.get('reason')}")
    if not proj.get("verified_all"):
        # Incomplete or false destination-resource verification is a hard stop
        # before any change is applied — never a warning that scrolls past.
        detail = (
            f"expected {proj.get('expected')}, found "
            f"{proj.get('match_count', 0)}/{proj.get('total_resources', 0)} matching "
            f"resource(s); reason: {proj.get('reason', 'resource mismatch')}"
        )
        if apply:
            raise SystemExit(
                f"destination-resource verification incomplete/false — refusing to apply: {detail}"
            )
        print(f"  DRY-RUN NOTE: destination-resource verification incomplete/false ({detail}). "
              "--apply will refuse until this is resolved.")

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
