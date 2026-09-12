#!/usr/bin/env python3
"""Detect drift between Skills helper imports and dependency declarations.

Compares, per skill folder:
  1. third-party imports in scripts/**.py
     vs the Import name column of the skill's SKILL.md Runtime Dependencies
     table;
  2. the Install name column of every such table
     vs the packages listed in requirements.txt at the Skills root.

Names are normalized to the top-level import segment on both sides, so a
declaration of `google.genai` matches code importing `google.genai`.

Exit codes: 0 = no drift, 1 = drift found, 2 = operational error.
Run with: python -X utf8 Skills/check_dependency_drift.py [skills-root]
"""

import ast
import re
import sys
from pathlib import Path

STDLIB = sys.stdlib_module_names


def top(name: str) -> str:
    return name.split(".")[0]


def helper_third_party_imports(skill_dir: Path, local_names: set[str]) -> set[str]:
    found: set[str] = set()
    for py in sorted(skill_dir.rglob("*.py")):
        if py.name == "check_dependency_drift.py":
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            raise RuntimeError(f"cannot parse {py}: {exc}") from exc
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = top(alias.name)
                    if root not in STDLIB and root != "__future__" and root not in local_names:
                        found.add(root)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    root = top(node.module)
                    if root not in STDLIB and root not in local_names:
                        found.add(root)
    return found


def declared_dependencies(skill_md: Path) -> list[tuple[str, str]]:
    """Return (import name, install name) rows of the Runtime Dependencies table."""
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"^## Runtime Dependencies\s*$", text, re.MULTILINE)
    if not match:
        return []
    tail = text[match.end():]
    lines = tail.splitlines()
    rows: list[tuple[str, str]] = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") and not in_table:
            if stripped.startswith("#"):
                break
            continue
        if stripped.startswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell):
                in_table = True
                continue
            if in_table and len(cells) >= 2:
                rows.append((cells[0], cells[1]))
        elif in_table:
            break
    return rows


def manifest_packages(path: Path) -> set[str]:
    names: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        token = re.split(r"[\s<>=!\[]", line, maxsplit=1)[0]
        if token:
            names.add(token)
    return names


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent
    manifest = root / "requirements.txt"
    if not manifest.is_file():
        print(f"operational_error: manifest not found: {manifest}", file=sys.stderr)
        return 2

    local_names = {p.stem for p in root.rglob("*.py")}
    local_names |= {p.parent.name for p in root.rglob("__init__.py")}

    drift: list[str] = []
    manifest_names = manifest_packages(manifest)
    all_install_names: set[str] = set()

    for skill_md in sorted(root.glob("*/SKILL.md")):
        skill_dir = skill_md.parent
        imports = helper_third_party_imports(skill_dir, local_names)
        declared = declared_dependencies(skill_md)
        declared_imports = {top(imp) for imp, _ in declared}
        for name in sorted(imports - declared_imports):
            drift.append(f"{skill_dir.name}: helper imports {name} but SKILL.md Runtime Dependencies does not declare it")
        for name in sorted(declared_imports - imports):
            drift.append(f"{skill_dir.name}: SKILL.md Runtime Dependencies declares {name} but no helper script imports it")
        for imp, install in declared:
            all_install_names.add(install)

    for name in sorted(all_install_names - manifest_names):
        drift.append(f"requirements.txt is missing declared install name: {name}")
    for name in sorted(manifest_names - all_install_names):
        drift.append(f"requirements.txt lists {name} but no SKILL.md Runtime Dependencies table declares it")

    if drift:
        for line in drift:
            print(line)
        print(f"dependency drift: {len(drift)} finding(s)", file=sys.stderr)
        return 1
    print("no dependency drift: helper imports, SKILL.md declarations, and requirements.txt agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
