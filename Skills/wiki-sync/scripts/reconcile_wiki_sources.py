#!/usr/bin/env python3
"""Read-only coverage reconciliation for schema-driven workspace wikis."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


VALID_STATUSES = {
    "represented-unchanged",
    "new",
    "changed",
    "uncertain",
    "skipped",
}
VALID_SCOPES = {"workspace-full", "root-full", "named-source"}
VALID_CLAIMS = {"none", "workspace-synced", "root-synced", "scoped-synced"}
VALID_PHASES = {"before", "after"}


class ContractError(ValueError):
    """Raised when reconciliation inputs are invalid or unsafe."""


@dataclass(frozen=True)
class SourceIdentity:
    identity: str
    root_id: str
    path: str
    mode: str


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read {label} JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"{label} must be a JSON object")
    return data


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ContractError(f"{label} must be a list of strings")
    return value


def _glob_list(value: Any, label: str) -> list[str]:
    patterns = _string_list(value, label)
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        pure = PurePosixPath(normalized)
        if pure.is_absolute() or pure.drive or ".." in pure.parts:
            raise ContractError(f"{label} contains an unsafe pattern: {pattern}")
    return patterns


def _normalize_relative(raw: str, label: str) -> str:
    value = raw.strip().replace("\\", "/")
    if not value:
        raise ContractError(f"{label} contains an empty path")
    if "://" in value:
        raise ContractError(f"{label} must be a workspace-relative path, not a URL: {raw}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or pure.drive or ".." in pure.parts:
        raise ContractError(f"{label} escapes the workspace: {raw}")
    normalized = pure.as_posix()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized or normalized == ".":
        raise ContractError(f"{label} resolves to an empty path")
    return normalized


def _path_key(path: str, case_sensitive: bool) -> str:
    return path if case_sensitive else path.casefold()


def _matches(path: str, patterns: Iterable[str], case_sensitive: bool) -> bool:
    candidate = path if case_sensitive else path.casefold()
    for raw_pattern in patterns:
        pattern = raw_pattern.replace("\\", "/")
        if not case_sensitive:
            pattern = pattern.casefold()
        if fnmatch.fnmatchcase(candidate, pattern) or PurePosixPath(candidate).match(pattern):
            return True
        prefix = pattern.removesuffix("/**").rstrip("/")
        if prefix != pattern and (candidate == prefix or candidate.startswith(prefix + "/")):
            return True
    return False


def _has_nested_marker(directory: Path, markers: set[str]) -> bool:
    try:
        return any(entry.name in markers for entry in directory.iterdir())
    except OSError as exc:
        raise ContractError(f"cannot inspect nested-workspace markers in {directory}: {exc}") from exc


def _iter_files(
    workspace: Path,
    root: Path,
    markers: set[str],
    excludes: list[str],
    case_sensitive: bool,
) -> Iterable[Path]:
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name.casefold())
        except OSError as exc:
            raise ContractError(f"cannot enumerate source directory {current}: {exc}") from exc
        for entry in entries:
            relative = entry.relative_to(workspace).as_posix()
            if _matches(relative, excludes, case_sensitive):
                continue
            if entry.is_symlink():
                raise ContractError(f"source enumeration refuses symbolic link: {relative}")
            if entry.is_dir():
                if entry != root and _has_nested_marker(entry, markers):
                    continue
                pending.append(entry)
            elif entry.is_file():
                yield entry


def _load_contract(workspace: Path, contract_path: Path) -> dict[str, Any]:
    contract = _load_json(contract_path, "coverage contract")
    if contract.get("version") != 1:
        raise ContractError("coverage contract version must be 1")
    roots = contract.get("source_roots")
    if not isinstance(roots, list) or not roots:
        raise ContractError("coverage contract source_roots must be a non-empty list")
    seen: set[str] = set()
    for index, root in enumerate(roots):
        if not isinstance(root, dict):
            raise ContractError(f"source_roots[{index}] must be an object")
        root_id = _require_string(root.get("id"), f"source_roots[{index}].id")
        if root_id in seen:
            raise ContractError(f"duplicate source root id: {root_id}")
        seen.add(root_id)
        relative = _normalize_relative(
            _require_string(root.get("path"), f"source_roots[{index}].path"),
            f"source_roots[{index}].path",
        )
        resolved = (workspace / relative).resolve()
        if workspace not in resolved.parents and resolved != workspace:
            raise ContractError(f"source root escapes workspace: {relative}")
        if not resolved.is_dir():
            raise ContractError(f"source root is missing or not a directory: {relative}")
        mode = root.get("identity_mode")
        if mode not in {"file", "immediate-directory"}:
            raise ContractError(
                f"source_roots[{index}].identity_mode must be file or immediate-directory"
            )
        _glob_list(root.get("include", ["**/*"]), f"source_roots[{index}].include")
        _glob_list(root.get("exclude", []), f"source_roots[{index}].exclude")
    wiki = contract.get("wiki")
    if not isinstance(wiki, dict):
        raise ContractError("coverage contract wiki must be an object")
    wiki_relative = _normalize_relative(_require_string(wiki.get("path"), "wiki.path"), "wiki.path")
    wiki_path = (workspace / wiki_relative).resolve()
    if workspace not in wiki_path.parents or not wiki_path.is_dir():
        raise ContractError(f"wiki path is missing or escapes workspace: {wiki_relative}")
    _require_string(wiki.get("provenance_field"), "wiki.provenance_field")
    _glob_list(wiki.get("page_globs", ["**/*.md"]), "wiki.page_globs")
    _glob_list(wiki.get("exclude", []), "wiki.exclude")
    _string_list(contract.get("nested_workspace_markers", []), "nested_workspace_markers")
    _string_list(contract.get("allowed_skip_reasons", []), "allowed_skip_reasons")
    if not isinstance(contract.get("case_sensitive_paths", True), bool):
        raise ContractError("case_sensitive_paths must be a boolean")
    return contract


def enumerate_identities(workspace: Path, contract: dict[str, Any]) -> list[SourceIdentity]:
    markers = set(contract.get("nested_workspace_markers", []))
    case_sensitive = contract.get("case_sensitive_paths", True)
    identities: list[SourceIdentity] = []
    for root in contract["source_roots"]:
        root_id = root["id"]
        root_relative = _normalize_relative(root["path"], f"source root {root_id}")
        root_path = (workspace / root_relative).resolve()
        includes = _glob_list(root.get("include", ["**/*"]), f"source root {root_id} include")
        excludes = _glob_list(root.get("exclude", []), f"source root {root_id} exclude")
        mode = root["identity_mode"]
        if mode == "file":
            for source in _iter_files(workspace, root_path, markers, excludes, case_sensitive):
                relative = source.relative_to(workspace).as_posix()
                root_local = source.relative_to(root_path).as_posix()
                if not _matches(root_local, includes, case_sensitive):
                    continue
                identities.append(SourceIdentity(f"{root_id}:{relative}", root_id, relative, mode))
        else:
            try:
                children = sorted(root_path.iterdir(), key=lambda item: item.name.casefold())
            except OSError as exc:
                raise ContractError(f"cannot enumerate source root {root_relative}: {exc}") from exc
            for child in children:
                if child.is_symlink():
                    raise ContractError(
                        f"source enumeration refuses symbolic link: "
                        f"{child.relative_to(workspace).as_posix()}"
                    )
                if not child.is_dir() or _has_nested_marker(child, markers):
                    continue
                relative = child.relative_to(workspace).as_posix()
                if _matches(relative, excludes, case_sensitive):
                    continue
                if not _matches(child.name, includes, case_sensitive):
                    continue
                identities.append(SourceIdentity(f"{root_id}:{relative}", root_id, relative, mode))
    identities.sort(key=lambda item: item.identity.casefold())
    keys: set[str] = set()
    for item in identities:
        key = _path_key(item.identity, case_sensitive)
        if key in keys:
            raise ContractError(f"duplicate normalized source identity: {item.identity}")
        keys.add(key)
    return identities


def _parse_inline_value(raw: str, page: Path, field: str) -> list[str]:
    value = raw.strip()
    if not value:
        return []
    parsed: Any
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError) as exc:
            if value.startswith(("'", '"')):
                raise ContractError(f"cannot parse {field} in {page}: {exc}") from exc
            parsed = value
    if isinstance(parsed, str):
        return [parsed]
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise ContractError(f"{field} in {page} must be a string or list of strings")
    return parsed


def _frontmatter_values(page: Path, field: str) -> list[str]:
    try:
        lines = page.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ContractError(f"cannot read wiki page {page}: {exc}") from exc
    if not lines or lines[0].strip() != "---":
        return []
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ContractError(f"unterminated frontmatter in {page}") from exc
    prefix = field + ":"
    for index in range(1, end):
        line = lines[index]
        if not line.startswith(prefix):
            continue
        remainder = line[len(prefix) :].strip()
        if remainder:
            return _parse_inline_value(remainder, page, field)
        values: list[str] = []
        for child in lines[index + 1 : end]:
            stripped = child.strip()
            if not stripped:
                continue
            if not child.startswith((" ", "\t")) or not stripped.startswith("-"):
                break
            values.extend(_parse_inline_value(stripped[1:].strip(), page, field))
        return values
    return []


def collect_provenance(workspace: Path, contract: dict[str, Any]) -> list[str]:
    wiki = contract["wiki"]
    wiki_path = (workspace / _normalize_relative(wiki["path"], "wiki.path")).resolve()
    globs = _glob_list(wiki.get("page_globs", ["**/*.md"]), "wiki.page_globs")
    excludes = _glob_list(wiki.get("exclude", []), "wiki.exclude")
    case_sensitive = contract.get("case_sensitive_paths", True)
    pages: dict[str, Path] = {}
    for pattern in globs:
        for page in wiki_path.glob(pattern):
            if not page.is_file():
                continue
            if page.is_symlink():
                raise ContractError(f"provenance extraction refuses symbolic link: {page}")
            relative = page.relative_to(wiki_path).as_posix()
            if _matches(relative, excludes, case_sensitive):
                continue
            pages[relative] = page
    values: set[str] = set()
    field = wiki["provenance_field"]
    for page in sorted(pages.values(), key=lambda item: item.as_posix().casefold()):
        for raw in _frontmatter_values(page, field):
            try:
                values.add(_normalize_relative(raw, f"{field} in {page}"))
            except ContractError:
                if "://" in raw:
                    continue
                raise
    return sorted(values, key=str.casefold)


def _identity_for_path(
    path: str,
    identities: list[SourceIdentity],
    case_sensitive: bool,
) -> str | None:
    path_key = _path_key(path, case_sensitive)
    for item in identities:
        item_key = _path_key(item.path, case_sensitive)
        if item.mode == "file" and path_key == item_key:
            return item.identity
        if item.mode == "immediate-directory" and (
            path_key == item_key or path_key.startswith(item_key + "/")
        ):
            return item.identity
    return None


def _declared_root_for_path(path: str, contract: dict[str, Any]) -> str | None:
    case_sensitive = contract.get("case_sensitive_paths", True)
    key = _path_key(path, case_sensitive)
    for root in contract["source_roots"]:
        root_path = _normalize_relative(root["path"], f"source root {root['id']}")
        root_key = _path_key(root_path, case_sensitive)
        if key == root_key or key.startswith(root_key + "/"):
            return root["id"]
    return None


def build_inventory(workspace: Path, contract: dict[str, Any]) -> dict[str, Any]:
    identities = enumerate_identities(workspace, contract)
    provenance = collect_provenance(workspace, contract)
    case_sensitive = contract.get("case_sensitive_paths", True)
    represented: dict[str, list[str]] = {item.identity: [] for item in identities}
    stale: list[str] = []
    ignored: list[str] = []
    for path in provenance:
        identity = _identity_for_path(path, identities, case_sensitive)
        if identity:
            represented[identity].append(path)
        elif _declared_root_for_path(path, contract):
            stale.append(path)
        else:
            ignored.append(path)
    return {
        "version": 1,
        "eligible": [item.__dict__ for item in identities],
        "represented": {key: value for key, value in represented.items() if value},
        "stale_provenance": sorted(stale, key=str.casefold),
        "out_of_contract_provenance": sorted(ignored, key=str.casefold),
    }


def _scope_identities(
    inventory: dict[str, Any],
    scope: str,
    root_id: str | None,
    source_ids: list[str],
) -> list[str]:
    all_items = inventory["eligible"]
    all_ids = {item["identity"] for item in all_items}
    if scope == "workspace-full":
        if root_id or source_ids:
            raise ContractError("workspace-full does not accept --root-id or --source-id")
        return sorted(all_ids, key=str.casefold)
    if scope == "root-full":
        if not root_id or source_ids:
            raise ContractError("root-full requires exactly one --root-id and no --source-id")
        selected = [item["identity"] for item in all_items if item["root_id"] == root_id]
        if not selected:
            raise ContractError(f"root-full selected no eligible identities for root: {root_id}")
        return sorted(selected, key=str.casefold)
    if root_id or not source_ids:
        raise ContractError("named-source requires one or more --source-id and no --root-id")
    unknown = sorted(set(source_ids) - all_ids, key=str.casefold)
    if unknown:
        raise ContractError(f"named-source contains unknown identities: {', '.join(unknown)}")
    return sorted(set(source_ids), key=str.casefold)


def reconcile(
    workspace: Path,
    contract: dict[str, Any],
    manifest: dict[str, Any],
    scope: str,
    root_id: str | None,
    source_ids: list[str],
    claim: str,
    phase: str = "before",
) -> tuple[dict[str, Any], bool]:
    if scope not in VALID_SCOPES:
        raise ContractError(f"invalid scope: {scope}")
    if claim not in VALID_CLAIMS:
        raise ContractError(f"invalid claim: {claim}")
    if phase not in VALID_PHASES:
        raise ContractError(f"invalid phase: {phase}")
    if manifest.get("version") != 1 or not isinstance(manifest.get("entries"), list):
        raise ContractError("manifest must have version 1 and an entries list")
    inventory = build_inventory(workspace, contract)
    required = _scope_identities(inventory, scope, root_id, source_ids)
    represented = inventory["represented"]
    allowed_skips = set(contract.get("allowed_skip_reasons", []))
    entries: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, entry in enumerate(manifest["entries"]):
        if not isinstance(entry, dict):
            raise ContractError(f"manifest entries[{index}] must be an object")
        identity = _require_string(entry.get("identity"), f"manifest entries[{index}].identity")
        if identity in entries:
            errors.append(f"duplicate manifest identity: {identity}")
            continue
        status = entry.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"invalid status for {identity}: {status}")
        previous_paths = _string_list(entry.get("previous_paths", []), f"{identity}.previous_paths")
        normalized_previous = [
            _normalize_relative(path, f"{identity}.previous_paths") for path in previous_paths
        ]
        normalized = dict(entry)
        normalized["previous_paths"] = normalized_previous
        entries[identity] = normalized
        if status == "skipped":
            reason = entry.get("skip_reason")
            if reason not in allowed_skips:
                errors.append(f"invalid or missing skip_reason for {identity}: {reason}")
        elif entry.get("skip_reason") is not None:
            errors.append(f"skip_reason is only valid for skipped identity: {identity}")
    omissions = sorted(set(required) - set(entries), key=str.casefold)
    extras = sorted(set(entries) - set(required), key=str.casefold)
    if extras:
        errors.append("manifest contains identities outside the selected scope: " + ", ".join(extras))
    explained_previous: dict[str, str] = {}
    for identity, entry in entries.items():
        for previous in entry.get("previous_paths", []):
            if previous in explained_previous:
                errors.append(
                    f"previous provenance path {previous} is claimed by both "
                    f"{explained_previous[previous]} and {identity}"
                )
            explained_previous[previous] = identity
        status = entry.get("status")
        is_represented = identity in represented
        has_previous = bool(entry.get("previous_paths"))
        if status == "represented-unchanged" and not is_represented:
            errors.append(f"represented-unchanged identity lacks current provenance: {identity}")
        if status == "new":
            if has_previous:
                errors.append(f"new identity cannot declare previous provenance: {identity}")
            if phase == "before" and is_represented:
                errors.append(f"new identity already has current provenance: {identity}")
            if phase == "after" and not is_represented:
                errors.append(f"new identity lacks synthesized current provenance: {identity}")
        if status == "changed":
            if phase == "before" and not (is_represented or has_previous):
                errors.append(f"changed identity has neither current nor previous provenance: {identity}")
            if phase == "after" and not is_represented:
                errors.append(f"changed identity lacks repaired current provenance: {identity}")
    all_stale = set(inventory["stale_provenance"])
    if scope == "workspace-full":
        stale = all_stale
    elif scope == "root-full":
        stale = {
            path for path in all_stale if _declared_root_for_path(path, contract) == root_id
        }
    else:
        stale = all_stale & set(explained_previous)
    out_of_scope_stale = sorted(all_stale - stale, key=str.casefold)
    explained_stale = sorted(stale & set(explained_previous), key=str.casefold)
    unexplained_stale = sorted(stale - set(explained_previous), key=str.casefold)
    unused_previous = sorted(set(explained_previous) - stale, key=str.casefold)
    if phase == "before" and unused_previous:
        errors.append("previous_paths are not stale provenance: " + ", ".join(unused_previous))
    unrepaired_stale = sorted(stale, key=str.casefold) if phase == "after" else []
    statuses = {identity: entries[identity].get("status") for identity in required if identity in entries}
    uncertain = sorted(
        [identity for identity, status in statuses.items() if status == "uncertain"],
        key=str.casefold,
    )
    skipped = sorted(
        [identity for identity, status in statuses.items() if status == "skipped"],
        key=str.casefold,
    )
    coverage_complete = not omissions and not unexplained_stale and not unrepaired_stale and not errors
    claim_errors: list[str] = []
    if claim != "none" and phase != "after":
        claim_errors.append("a synchronized status claim is valid only in the after phase")
    if claim == "workspace-synced" and scope != "workspace-full":
        claim_errors.append("workspace-synced claim requires workspace-full scope")
    if claim == "root-synced" and scope != "root-full":
        claim_errors.append("root-synced claim requires root-full scope")
    if claim == "scoped-synced" and scope != "named-source":
        claim_errors.append("scoped-synced claim requires named-source scope")
    if claim != "none" and (uncertain or skipped):
        claim_errors.append("a synchronized status claim requires zero uncertain and zero skipped identities")
    if claim != "none" and not coverage_complete:
        claim_errors.append("a synchronized status claim requires complete reconciliation")
    failed = not coverage_complete or bool(claim_errors)
    result = {
        "version": 1,
        "phase": phase,
        "scope": scope,
        "claim": claim,
        "eligible_count": len(required),
        "classified_count": len(set(required) & set(entries)),
        "status_counts": {
            status: sum(1 for value in statuses.values() if value == status)
            for status in sorted(VALID_STATUSES)
        },
        "omissions": omissions,
        "unexplained_stale_provenance": unexplained_stale,
        "explained_stale_provenance": explained_stale if phase == "before" else [],
        "unrepaired_stale_provenance": unrepaired_stale,
        "out_of_scope_stale_provenance": out_of_scope_stale,
        "uncertain": uncertain,
        "skipped": skipped,
        "errors": errors,
        "claim_errors": claim_errors,
        "coverage_complete": coverage_complete,
        "claim_allowed": claim != "none" and not failed,
    }
    return result, failed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory", help="enumerate identities and provenance")
    inventory.add_argument("--workspace", required=True)
    inventory.add_argument("--contract", required=True)
    check = subparsers.add_parser("check", help="validate a classification manifest")
    check.add_argument("--workspace", required=True)
    check.add_argument("--contract", required=True)
    check.add_argument("--manifest", required=True)
    check.add_argument("--scope", choices=sorted(VALID_SCOPES), required=True)
    check.add_argument("--root-id")
    check.add_argument("--source-id", action="append", default=[])
    check.add_argument("--claim", choices=sorted(VALID_CLAIMS), default="none")
    check.add_argument("--phase", choices=sorted(VALID_PHASES), default="before")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        workspace = Path(args.workspace).resolve()
        if not workspace.is_dir():
            raise ContractError(f"workspace is missing or not a directory: {workspace}")
        contract_path = Path(args.contract)
        if not contract_path.is_absolute():
            contract_path = workspace / contract_path
        contract_path = contract_path.resolve()
        if workspace not in contract_path.parents:
            raise ContractError(f"coverage contract escapes workspace: {contract_path}")
        contract = _load_contract(workspace, contract_path)
        if args.command == "inventory":
            result = build_inventory(workspace, contract)
            print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
            return 0
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            manifest_path = workspace / manifest_path
        manifest_path = manifest_path.resolve()
        if workspace not in manifest_path.parents:
            raise ContractError(f"manifest escapes workspace: {manifest_path}")
        manifest = _load_json(manifest_path, "manifest")
        result, failed = reconcile(
            workspace,
            contract,
            manifest,
            args.scope,
            args.root_id,
            args.source_id,
            args.claim,
            args.phase,
        )
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 1 if failed else 0
    except ContractError as exc:
        print(json.dumps({"operational_error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
