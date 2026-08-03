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


def _cf(value: str) -> str:
    """Casefold a string for case-insensitive Windows-path comparison. Windows
    paths are case-insensitive, so identity/prefix tests must not depend on the
    stored casing — only the *comparison* is normalized; the original string is
    preserved whenever a value is left unchanged."""
    return value.casefold()


def _under(value: str, base: str) -> bool:
    """Case-insensitive: value equals base or sits under base\\."""
    vf, bf = _cf(value), _cf(base)
    return vf == bf or vf.startswith(bf + "\\")


def _is_nested(old: str, new: str) -> bool:
    """True when old and new are in a parent/child relationship (either
    direction) rather than side by side. In a nested move a subtree of the old
    workspace must be preserved as an honest record, not stamped with new.
    Case-insensitive, since Windows paths are."""
    of, nf = _cf(old), _cf(new)
    return nf.startswith(of + "\\") or of.startswith(nf + "\\")


def remap_cwd(value: str, old: str, new: str) -> str:
    """Nesting-aware, idempotent workspace-path remap.

    Classification precedence — the ORDER is load-bearing:
      1. Exact old root -> rewrite to ``new``. Checked FIRST so that when
         ``old`` is itself nested under ``new`` (source-under-destination), the
         exact old root is still rewritten instead of being swallowed by the
         already-destination guard in step 2.
      2. Already at/under ``new`` -> leave unchanged. This is the guard the
         original code lacked: when ``new`` is nested under ``old``, a value
         already correctly at/under ``new`` also matches ``old\\`` and would
         otherwise get ``new`` appended a second time (the doubled-path bug).
         It also makes the transform idempotent.
      3. A different subtree of ``old`` -> a side-by-side move swaps the ``old``
         prefix for ``new`` (subfolders travel with the workspace); a nested
         move (either direction) LEAVES the value unchanged rather than
         fabricating a ``new``-relative path that never existed.
      4. Unrelated -> unchanged.
    """
    # All comparisons are case-insensitive (Windows paths). When rewriting, the
    # manifest-provided ``new`` spelling is used; when leaving a value alone, the
    # original string (its own casing) is returned untouched. ``len(old)`` is a
    # safe slice index because ``old`` is a case-insensitive prefix here, so the
    # character count matches regardless of casing.
    # 1. exact old root
    if _cf(value) == _cf(old):
        return new
    # 2. already at/under destination (idempotent; nesting-safe)
    if _under(value, new):
        return value
    # 3. a different subtree of old
    if _cf(value).startswith(_cf(old) + "\\"):
        if _is_nested(old, new):
            return value
        return new + value[len(old):]
    # 4. unrelated
    return value


def is_doubled_new(value: Any, old: str, new: str) -> bool:
    """True if ``value`` is a doubled-destination corruption: ``new`` with its
    own old-relative tail re-applied on top. This is the exact shape the
    prefix-only remap produced when ``new`` was nested under ``old`` (e.g.
    ``…\\Workflows\\MilkyWay\\Tools\\Workflows\\skills``).

    Such a value starts with ``new\\`` and therefore looks clean to
    ``is_residual_old`` (which treats anything under ``new`` as non-residual).
    Verification checks this separately so a doubled path can never pass merely
    because it begins with ``new``. Only meaningful when ``new`` is nested under
    ``old`` — that is the only configuration in which the doubling can arise."""
    if not isinstance(value, str):
        return False
    if not _cf(new).startswith(_cf(old) + "\\"):
        return False
    rel = new[len(old) + 1:]           # new's path relative to old
    doubled = _cf(new + "\\" + rel)
    vf = _cf(value)
    return vf == doubled or vf.startswith(doubled + "\\")


def is_residual_old(value: Any, old: str, new: str) -> bool:
    """True if a cwd value still points at or under the old workspace after the
    transform. Catches stale descendant paths (``old\\\\subdir``), not only the
    exact old root, so a leftover descendant cannot pass verification silently.
    A value at or under the destination is never residual, which keeps nested
    old-under-new configs honest."""
    if not isinstance(value, str):
        return False
    under_old = _under(value, old)
    under_new = _under(value, new)
    return under_old and not under_new


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
    # Read BOM-safely: a pre-existing UTF-8 BOM must not break JSON parsing.
    # Detect it, then decode with utf-8-sig so the BOM (if any) is consumed
    # without ever forcing one onto the (plain UTF-8) JSONL output.
    raw_bytes = old_path.read_bytes()
    had_bom = raw_bytes.startswith(BOM)
    raw = raw_bytes.decode("utf-8-sig")
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
    # Verify in-memory before writing: every line parses, and no residual
    # old-workspace cwd remains. Residual detection is descendant-aware, so a
    # stale ``old\subdir`` value cannot pass verification by differing from the
    # exact old root.
    cwd_new = cwd_residual = cwd_doubled = 0
    residual_examples: list[str] = []
    doubled_examples: list[str] = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        c = json.loads(ln).get("cwd")
        # Doubled paths are checked FIRST: they start with ``new`` and would
        # otherwise be miscounted as clean by the ``c == new`` / residual tests.
        if is_doubled_new(c, old, new):
            cwd_doubled += 1
            if len(doubled_examples) < 3:
                doubled_examples.append(str(c))
        elif c == new:
            cwd_new += 1
        elif is_residual_old(c, old, new):
            cwd_residual += 1
            if len(residual_examples) < 3:
                residual_examples.append(str(c))
    if cwd_residual or cwd_doubled:
        raise RuntimeError(
            f"{old_path}: transform verification failed — "
            f"{cwd_residual} residual old-workspace cwd value(s) "
            f"(examples: {residual_examples}); "
            f"{cwd_doubled} doubled-destination cwd value(s) "
            f"(examples: {doubled_examples})"
        )

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
        "cwd_residual_after_transform": cwd_residual,
        "cwd_doubled_after_transform": cwd_doubled,
        "had_bom": had_bom,
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


def _require_expected_counts_declared(label: str, expected: Any) -> None:
    """Hard-stop BEFORE any move when the manifest omits the mandatory
    ``expected_files`` block. Requiring the declaration up front means an
    invalid manifest never gets as far as moving files."""
    if not isinstance(expected, dict):
        raise SystemExit(
            f"{label}: manifest is missing the required expected_files block "
            "(expected-file/count verification is mandatory for every relocation)"
        )
    if expected.get("files") is None and expected.get("directories") is None:
        raise SystemExit(
            f"{label}: expected_files must declare 'files' and/or 'directories' counts; "
            "an empty block is not verification evidence"
        )


def _check_missing_source(label: str, source: Path, expected: Any, allow_missing: Any) -> bool:
    """Gate a declared relocation whose source does not exist.

    A missing declared source is a hard stop — a relocation must never
    silently succeed as a no-op — unless the manifest explicitly sets
    ``allow_missing_source: true`` for that entry AND declares expected
    counts of exactly 0 files and 0 directories (i.e. the manifest itself
    asserts there is nothing to move). Returns True when the relocation may
    proceed as an intentional, explicitly-declared no-op."""
    if source.exists():
        return False
    if allow_missing is not True:
        raise SystemExit(
            f"{label}: declared source does not exist: {source}. A missing "
            "declared source is a hard stop; set allow_missing_source: true "
            "(with expected_files files=0 and directories=0) only when the "
            "no-op is intentional."
        )
    files = expected.get("files") if isinstance(expected, dict) else None
    dirs = expected.get("directories") if isinstance(expected, dict) else None
    if files != 0 or dirs != 0:
        raise SystemExit(
            f"{label}: allow_missing_source is set but expected_files is not "
            f"files=0/directories=0 (got files={files!r}, directories={dirs!r}). "
            "The allowance is only valid when the manifest declares both "
            "expected counts as zero."
        )
    return True


def _verify_expected_counts(label: str, dest: Path, expected: Any, moved: dict[str, Any]) -> None:
    """Assert that a relocated tree matches the manifest's expected file/dir
    counts. Expected counts are REQUIRED evidence for every relocation the
    manifest declares (see ``_require_expected_counts_declared``); the
    destination must match exactly."""
    _require_expected_counts_declared(label, expected)
    if moved.get("source_exists_before") is False:
        # Unreachable for declared relocations: missing sources hard-stop in
        # _check_missing_source before any move. Kept as defense in depth.
        raise SystemExit(
            f"{label}: relocation reached count verification with a missing "
            f"source ({moved.get('source')}); this should have been gated by "
            "the missing-source check."
        )
    expected_files = expected.get("files")
    expected_dirs = expected.get("directories")
    after = moved.get("destination_counts_after") or count_tree(dest)
    if expected_files is not None and after.get("files") != expected_files:
        raise RuntimeError(
            f"{label}: expected {expected_files} files at {dest}, found {after.get('files')}"
        )
    if expected_dirs is not None and after.get("directories") != expected_dirs:
        raise RuntimeError(
            f"{label}: expected {expected_dirs} directories at {dest}, found {after.get('directories')}"
        )


def relocate_adjacent_data(plan: dict[str, Any], suffix: str, apply: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "memory_move": None,
        "sidecar_relocations": [],
        "then_delete": plan.get("then_delete"),
        "then_delete_counts_before": None,
        "then_delete_removed": False,
        "memory_scope": plan.get("memory_scope"),
    }
    memory = plan.get("memory_move")
    if isinstance(memory, dict) and memory.get("source") and memory.get("destination"):
        # Workspace `memory/` is whole-workspace state shared by every chat in
        # the encoded project folder, not per-selected-chat state. Moving it as
        # part of a selected-chat migration would silently drag other chats'
        # memory along. The manifest MUST declare the scope explicitly:
        # "whole_workspace" (only valid when the whole workspace is moving) or
        # "none" (skip the move for a selected-chat migration). An absent
        # scope is a hard stop — it is never defaulted.
        if result["memory_scope"] is None:
            raise SystemExit(
                "memory_move is declared but memory_scope is absent. Declare "
                "memory_scope 'whole_workspace' or 'none' explicitly; the scope "
                "is never defaulted."
            )
        scope = str(result["memory_scope"]).strip().lower()
        if scope == "none":
            result["memory_move"] = {
                "skipped": True,
                "reason": "memory_scope=none: workspace memory is whole-workspace and was not moved",
            }
        elif scope != "whole_workspace":
            raise SystemExit(
                f"memory_move requires memory_scope 'whole_workspace' or 'none'; got {scope!r}. "
                "Workspace memory/ is whole-workspace state, not per-selected-chat."
            )
        else:
            _require_expected_counts_declared("memory_move", memory.get("expected_files"))
            source = Path(memory["source"])
            if _check_missing_source(
                "memory_move", source, memory.get("expected_files"),
                memory.get("allow_missing_source"),
            ):
                result["memory_move"] = {
                    "skipped": True,
                    "reason": "allow_missing_source: declared no-op (source absent, expected counts 0/0)",
                    "source": str(source),
                }
            else:
                moved = move_tree(source, Path(memory["destination"]), suffix, apply)
                _verify_expected_counts(
                    "memory_move", Path(memory["destination"]), memory.get("expected_files"), moved
                )
                result["memory_move"] = moved

    # `aux_relocations` is the legacy manifest key. New manifests should use
    # the clearer `sidecar_relocations` key.
    sidecar_relocations = plan.get("sidecar_relocations", plan.get("aux_relocations", []))
    for item in sidecar_relocations:
        source = Path(item["source"])
        destination = Path(item["destination"])
        label = f"sidecar[{item.get('session_id')}]"
        _require_expected_counts_declared(label, item.get("expected_files"))
        if _check_missing_source(
            label, source, item.get("expected_files"), item.get("allow_missing_source")
        ):
            result["sidecar_relocations"].append({
                "skipped": True,
                "reason": "allow_missing_source: declared no-op (source absent, expected counts 0/0)",
                "source": str(source),
                "session_id": item.get("session_id"),
                "sidecar_kind": item.get("sidecar_kind", item.get("aux_kind")),
            })
            continue
        moved = move_tree(source, destination, suffix, apply)
        _verify_expected_counts(
            f"sidecar[{item.get('session_id')}]",
            destination,
            item.get("expected_files"),
            moved,
        )
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
