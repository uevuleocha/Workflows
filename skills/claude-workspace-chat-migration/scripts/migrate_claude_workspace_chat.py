#!/usr/bin/env python3
"""Migrate explicit Claude Desktop chat sessions between workspaces.

This helper is intentionally manifest-driven. It will not discover or guess sessions.
Use --dry-run first; use --apply only while Claude Desktop is fully closed.

Claude has two state layers (no SQLite, no global-state):
  Layer A - CLI transcript JSONL: ~/.claude/projects/<encoded-workspace>/<cliSessionId>.jsonl
            (relocate to the destination encoded folder + rewrite each top-level `cwd`)
  Adjacent project data:       ~/.claude/projects/<encoded-workspace>/memory/
                               ~/.claude/projects/<encoded-workspace>/<cliSessionId>/{subagents,tool-results}/
            (relocate byte-for-byte to the destination encoded folder)
  Layer B - Desktop chat store:   .../claude-code-sessions/<account>/<group>/local_*.json
            (rewrite `cwd` and `originCwd`; preserve the file's existing BOM/no-BOM state)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
from pathlib import Path
from typing import Any

CLAUDE_HOME = Path.home() / ".claude"
# All backups land in one unified place under the Claude dir, grouped per run.
BACKUP_ROOT = CLAUDE_HOME / "user-backups"
BOM = b"\xef\xbb\xbf"


def encode_workspace(ws: str) -> str:
    """Encode a workspace path the way Claude names its projects folder:
    every ':' '\\' and space becomes '-'."""
    return "".join("-" if ch in (":", "\\", " ") else ch for ch in ws)


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("old_workspace") or not data.get("new_workspace"):
        raise SystemExit("manifest requires old_workspace and new_workspace")
    has_sessions = isinstance(data.get("sessions"), list) and bool(data["sessions"])
    has_adjacent_data = isinstance(data.get("adjacent_data_relocation"), dict)
    has_legacy_leftovers = isinstance(data.get("third_pass_leftover_relocation"), dict)
    if not has_sessions and not (has_adjacent_data or has_legacy_leftovers):
        raise SystemExit("manifest requires sessions or adjacent_data_relocation")
    for item in data.get("sessions", []):
        if not item.get("cli_session_id") or not item.get("desktop_record"):
            raise SystemExit("each session requires cli_session_id and desktop_record")
    return data


def backup(path: Path, suffix: str, apply: bool) -> Path | None:
    if not path.exists():
        return None
    # Unified, per-run backup folder: ~/.claude/user-backups/<suffix>/<original name>.
    target_dir = BACKUP_ROOT / suffix
    target = target_dir / path.name
    if apply:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return target


def backup_tree(path: Path, suffix: str, apply: bool) -> Path | None:
    if not path.exists():
        return None
    try:
        rel = path.relative_to(CLAUDE_HOME)
    except ValueError:
        rel = Path(path.drive.replace(":", "")) / Path(*path.parts[1:])
    target = BACKUP_ROOT / suffix / rel
    if apply:
        if path.is_dir():
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(path, target, copy_function=shutil.copy2)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return target


def remap_cwd(value: str, old: str, new: str) -> str:
    """Exact match or under-the-workspace prefix; otherwise unchanged."""
    if value == old:
        return new
    if value.startswith(old + "\\"):
        return new + value[len(old):]
    return value


def transcript_paths(item: dict[str, Any], old_ws: str, new_ws: str) -> tuple[Path, Path]:
    sid = item["cli_session_id"]
    new_dir = CLAUDE_HOME / "projects" / encode_workspace(new_ws)
    if item.get("transcript_path"):
        old_t = Path(item["transcript_path"])
    else:
        old_t = CLAUDE_HOME / "projects" / encode_workspace(old_ws) / f"{sid}.jsonl"
    return old_t, new_dir / f"{sid}.jsonl"


def migrate_transcript(old_path: Path, new_path: Path, old: str, new: str, apply: bool) -> dict[str, Any]:
    if not old_path.exists():
        raise SystemExit(f"transcript not found: {old_path} (already migrated? mark status: done in manifest)")
    raw = old_path.read_text(encoding="utf-8")
    out: list[str] = []
    changed = 0
    for line in raw.splitlines(keepends=True):
        nl = "\n" if line.endswith("\n") else ""
        body = line[:-1] if nl else line
        if not body.strip():
            out.append(line)
            continue
        obj = json.loads(body)
        cwd = obj.get("cwd")
        if isinstance(cwd, str):
            ncwd = remap_cwd(cwd, old, new)
            if ncwd != cwd:
                obj["cwd"] = ncwd
                out.append(json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + nl)
                changed += 1
                continue
        out.append(line)

    text = "".join(out)
    # Verify in-memory before writing: every line parses, counts add up.
    cwd_new = cwd_old = 0
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        c = json.loads(ln).get("cwd")
        if c == new:
            cwd_new += 1
        elif c == old:
            cwd_old += 1
    if cwd_old:
        raise RuntimeError(f"{old_path}: {cwd_old} old-workspace cwd values still present after transform")

    if apply:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.write_text(text, encoding="utf-8", newline="")
        if not new_path.exists():
            raise RuntimeError(f"failed to write destination transcript {new_path}")
        if old_path.resolve() != new_path.resolve():
            old_path.unlink()  # chat must live in exactly one projects folder

    return {
        "from": str(old_path),
        "to": str(new_path),
        "changed_records": changed,
        "cwd_new": cwd_new,
        "cwd_old": cwd_old,
    }


def migrate_desktop_record(path: Path, old: str, new: str, apply: bool) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"desktop record not found: {path}")
    raw = path.read_bytes()
    has_bom = raw.startswith(BOM)
    obj = json.loads(raw.decode("utf-8-sig"))
    before = {"cwd": obj.get("cwd"), "originCwd": obj.get("originCwd")}
    for k in ("cwd", "originCwd"):
        v = obj.get(k)
        if isinstance(v, str):
            obj[k] = remap_cwd(v, old, new)
    data = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if has_bom:
        data = BOM + data
    json.loads(data.decode("utf-8-sig"))  # verify still valid JSON
    if apply:
        path.write_bytes(data)
    return {
        "record": str(path),
        "before": before,
        "after": {"cwd": obj.get("cwd"), "originCwd": obj.get("originCwd")},
        "bom_preserved": has_bom,
        "cliSessionId": obj.get("cliSessionId"),
        "title": obj.get("title"),
    }


def count_tree(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"files": 0, "directories": 0}
    files = 0
    dirs = 0
    for item in path.rglob("*"):
        if item.is_dir():
            dirs += 1
        else:
            files += 1
    return {"files": files, "directories": dirs}


def prune_empty_dirs(path: Path) -> list[str]:
    removed: list[str] = []
    if not path.exists():
        return removed
    dirs = sorted((p for p in path.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True)
    for item in dirs:
        try:
            item.rmdir()
        except OSError:
            continue
        removed.append(str(item))
    return removed


def move_tree(source: Path, destination: Path, suffix: str, apply: bool) -> dict[str, Any]:
    before = count_tree(source)
    backup_path = backup_tree(source, suffix, apply)
    result: dict[str, Any] = {
        "source": str(source),
        "destination": str(destination),
        "source_exists_before": source.exists(),
        "destination_exists_before": destination.exists(),
        "source_counts_before": before,
        "backup": str(backup_path) if backup_path else None,
    }
    if not source.exists():
        result.update({
            "moved": False,
            "would_move": False,
            "source_exists_after": False,
            "destination_exists_after": destination.exists(),
            "destination_counts_after": count_tree(destination),
        })
        return result
    if destination.exists():
        raise SystemExit(f"destination already exists, refusing to overwrite: {destination}")
    if apply:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        if source.exists():
            raise RuntimeError(f"source still exists after move: {source}")
        if not destination.exists():
            raise RuntimeError(f"destination missing after move: {destination}")
    result.update({
        "moved": bool(apply),
        "would_move": True,
        "source_exists_after": source.exists() if apply else source.exists(),
        "destination_exists_after": destination.exists() if apply else destination.exists(),
        "destination_counts_after": count_tree(destination) if apply else before,
    })
    return result


def relocate_adjacent_data(plan: dict[str, Any], suffix: str, apply: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "memory_move": None,
        "sidecar_relocations": [],
        "then_delete": plan.get("then_delete"),
        "then_delete_counts_before": None,
        "then_delete_removed": False,
    }
    memory = plan.get("memory_move")
    if isinstance(memory, dict) and memory.get("source") and memory.get("destination"):
        result["memory_move"] = move_tree(Path(memory["source"]), Path(memory["destination"]), suffix, apply)

    # `aux_relocations` is the legacy manifest key. New manifests should use
    # the clearer `sidecar_relocations` key.
    sidecar_relocations = plan.get("sidecar_relocations", plan.get("aux_relocations", []))
    for item in sidecar_relocations:
        source = Path(item["source"])
        destination = Path(item["destination"])
        moved = move_tree(source, destination, suffix, apply)
        moved.update({
            "session_id": item.get("session_id"),
            "sidecar_kind": item.get("sidecar_kind", item.get("aux_kind")),
            "dest_encoded_folder": item.get("dest_encoded_folder"),
        })
        result["sidecar_relocations"].append(moved)

    if plan.get("then_delete"):
        target = Path(plan["then_delete"])
        if apply:
            result["pruned_empty_dirs_before_delete"] = prune_empty_dirs(target)
        counts = count_tree(target)
        result["then_delete_counts_before"] = counts
        if apply and (counts["files"] or counts["directories"]):
            raise SystemExit(f"refusing to delete non-empty source folder: {target} ({counts})")
        if apply and target.exists():
            target.rmdir()
            if target.exists():
                raise RuntimeError(f"failed to remove empty source folder: {target}")
            result["then_delete_removed"] = True
    return result


def adjacent_data_plan(manifest: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(manifest.get("adjacent_data_relocation"), dict):
        return manifest["adjacent_data_relocation"]
    # Legacy fallback for manifests created before the clearer field name.
    if isinstance(manifest.get("third_pass_leftover_relocation"), dict):
        return manifest["third_pass_leftover_relocation"]
    return None


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
    apply = args.apply
    suffix = "claude-workspace-chat-migration-" + _dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    def is_done(s: dict[str, Any]) -> bool:
        return str(s.get("status", "")).lower() == "done"

    results: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "old_workspace": old,
        "new_workspace": new,
        "skipped_done": [s["cli_session_id"] for s in manifest.get("sessions", []) if is_done(s)],
        "backups": [],
        "sessions": [],
    }

    for item in (s for s in manifest.get("sessions", []) if not is_done(s)):
        old_t, new_t = transcript_paths(item, old, new)
        rec = Path(item["desktop_record"])
        if apply:
            for b in (backup(old_t, suffix, True), backup(rec, suffix, True)):
                if b:
                    results["backups"].append(str(b))
        results["sessions"].append({
            "cli_session_id": item["cli_session_id"],
            "title": item.get("title"),
            "layer_A": migrate_transcript(old_t, new_t, old, new, apply),
            "layer_B": migrate_desktop_record(rec, old, new, apply),
        })

    plan = adjacent_data_plan(manifest)
    if isinstance(plan, dict):
        results["adjacent_data_relocation"] = relocate_adjacent_data(plan, suffix, apply)

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
