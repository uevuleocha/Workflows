"""Exclusive-create workspace bootstrap; preview is the default."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

REMINDER = "This is a lightweight bootstrap. When you want full universal-standards parity for this workspace, run `workspace-setup`."
FILES = ("AGENTS.md", "CLAUDE.md", "README.md", ".gitignore")
DIRS = ("tmp", "Archive", "Archive/Live", "Archive/Historical")
ASSETS = Path(__file__).resolve().parent.parent / "assets"


def git(target, *args, check=True):
    """Run Git only at an explicit target, with automation disabled."""
    environment = dict(os.environ, GIT_CEILING_DIRECTORIES=str(Path(target).parent))
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=" + os.devnull,
         "-c", "commit.gpgsign=false", "-c", "core.fsmonitor=false",
         "-c", "core.untrackedCache=false", "-C", str(target), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=environment,
    )
    if check and result.returncode:
        # Configuration values and commit identities must not leak in errors.
        raise ValueError("Git operation failed: " + args[0] + "; inspect locally before retrying")
    return result


def linked(path):
    """Detect symlinks and Windows reparse points without following them."""
    if not os.path.lexists(path):
        return False
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def value(text, label):
    if not text or not text.strip() or any(c in text for c in "{}\r\n\x00"):
        raise ValueError(label + " must be nonempty, single-line, and contain no braces")
    return text.strip()


def render(args, target):
    name = value(args.name, "name")
    tier = value(args.tier, "tier")
    solar = value(args.solar_system, "solar system")
    purpose = value(args.purpose, "purpose")
    world_level = tier.casefold() == "world"
    if world_level and args.world:
        raise ValueError("A World workspace has no parent World")
    world = "" if world_level else value(args.world, "parent World")
    mapping = {
        "Workspace Name": name, "tier term": tier.lower(), "Tier Term": tier,
        "World": world, "Solar System": solar, "one-line purpose": purpose,
        "workspace path": str(target),
        "layout-sync timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "parent-world clause": "" if world_level else f" under the **{world}** world",
    }
    result = {}
    for filename in FILES[:3]:
        text = (ASSETS / filename).read_text(encoding="utf-8")
        for key, replacement in mapping.items():
            text = text.replace("{" + key + "}", replacement)
        if re.search(r"\{[^{}]*\}", text):
            raise ValueError("Unresolved template placeholder in " + filename)
        result[filename] = text
    result[".gitignore"] = args.gitignore_content
    return result


def verify_repo(target):
    """Require an independent ordinary repo whose metadata stays in target."""
    if not (target / ".git").is_dir() or linked(target / ".git"):
        raise ValueError("External/file-based .git is preserved; use workspace-setup")
    for query in ("--show-toplevel", "--absolute-git-dir", "--git-common-dir"):
        found = Path(git(target, "rev-parse", query).stdout.strip())
        found = (target / found).resolve() if not found.is_absolute() else found.resolve()
        expected = target if query == "--show-toplevel" else target / ".git"
        if found != expected:
            raise ValueError("Repository ownership escapes target")
    # A metadata child junction could redirect index, objects, refs, or logs.
    for current, directories, files in os.walk(target / ".git", followlinks=False):
        if any(linked(Path(current) / entry) for entry in directories + files):
            raise ValueError("Linked Git metadata is not supported")
    for marker in ("index.lock", "HEAD.lock", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer"):
        if (target / ".git" / marker).exists():
            raise ValueError("Repository operation in progress; stop before bootstrap")
    staged = git(target, "diff", "--cached", "--name-only").stdout
    if staged.strip():
        raise ValueError("Existing staged changes must be preserved; stop before bootstrap")
    if git(target, "symbolic-ref", "--quiet", "HEAD", check=False).returncode:
        raise ValueError("Detached HEAD is not a fresh workspace; use workspace-setup")
    attributes = git(target, "check-attr", "filter", "--", *FILES).stdout.splitlines()
    if any(not line.endswith((": unspecified", ": unset")) for line in attributes):
        raise ValueError("Git clean filters could execute external writes; stop before bootstrap")


def run(args):
    raw = Path(args.target).absolute()
    if not raw.is_dir():
        raise ValueError("Target must be an existing directory")
    if any(linked(p) for p in (raw, *raw.parents)):
        raise ValueError("Target traverses a link or junction")
    target = raw.resolve()
    # Do not allow Git routing variables to redirect this run to the hub/index.
    forbidden = {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_NAMESPACE", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT"}
    if forbidden.intersection(os.environ):
        raise ValueError("Git routing/configuration environment overrides must be cleared")
    entries = sorted(p.name for p in target.iterdir())
    for relative in (*FILES, *DIRS, ".git"):
        path = target / relative
        if linked(path):
            raise ValueError("Managed path is linked: " + relative)
        if path.exists():
            if relative in FILES and not path.is_file():
                raise ValueError("Expected file: " + relative)
            if relative in DIRS and not path.is_dir():
                raise ValueError("Expected directory: " + relative)
    for filename in ("CLAUDE.md", "AGENTS.md"):
        path = target / filename
        if path.exists() and path.read_text(encoding="utf-8-sig").strip():
            raise ValueError("Established workspace: preserved unchanged; use workspace-setup")
    documents = render(args, target)
    existing_git = (target / ".git").exists()
    git(target, "--version")
    if existing_git:
        verify_repo(target)
    if not args.no_commit:
        for identity in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
            if git(target, "var", identity, check=False).returncode:
                raise ValueError("Git commit identity unavailable; configure it or explicitly choose --no-commit")
    receipt = {"target": str(target), "entries_before": entries, "created": [], "skipped": [],
               "applied": args.apply, "commit": None, "branch": None}
    if not args.apply:
        receipt["would_create"] = [p for p in (".git", *FILES[:3], *DIRS, ".gitignore") if not (target / p).exists()]
        receipt["skipped"] = [p for p in (".git", *FILES[:3], *DIRS, ".gitignore") if (target / p).exists()]
        return receipt
    if not args.confirmed:
        raise ValueError("Apply requires --confirmed after the user's identity approval")
    try:
        if existing_git:
            receipt["skipped"].append(".git")
        else:
            git(target, "init", "-b", "main", "--template=")
            receipt["created"].append(".git")
        verify_repo(target)
        for filename in FILES[:3]:
            path = target / filename
            if path.exists():
                receipt["skipped"].append(filename)
            else:
                with path.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(documents[filename])
                receipt["created"].append(filename)
        for relative in DIRS:
            path = target / relative
            if path.exists():
                receipt["skipped"].append(relative)
            else:
                path.mkdir()
                receipt["created"].append(relative)
        if (target / ".gitignore").exists():
            receipt["skipped"].append(".gitignore")
        else:
            with (target / ".gitignore").open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(documents[".gitignore"])
            receipt["created"].append(".gitignore")
        new_files = [name for name in FILES if name in receipt["created"]]
        if new_files and not args.no_commit:
            verify_repo(target)
            git(target, "add", "--", *new_files)
            # --only excludes any unrelated staging done after the pre-flight.
            git(target, "commit", "--only", "-m", "Initialize " + args.name + " workspace", "--", *new_files)
            receipt["commit"] = git(target, "rev-parse", "HEAD").stdout.strip()
        receipt["branch"] = git(target, "symbolic-ref", "--short", "HEAD").stdout.strip()
        receipt["entries_after"] = sorted(p.name for p in target.iterdir())
        receipt["no_commit_requested"] = args.no_commit
        receipt["reminder"] = REMINDER
        return receipt
    except Exception:
        print(json.dumps({"partial_run": receipt}, ensure_ascii=False), file=sys.stderr)
        raise


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--target", default=str(Path.cwd()))
    result.add_argument("--name", required=True)
    result.add_argument("--tier", required=True)
    result.add_argument("--solar-system", required=True)
    result.add_argument("--world", default="")
    result.add_argument("--purpose", required=True)
    result.add_argument("--gitignore-content", default="")
    result.add_argument("--no-commit", action="store_true")
    result.add_argument("--apply", action="store_true")
    result.add_argument("--confirmed", action="store_true")
    return result


if __name__ == "__main__":
    try:
        arguments = parser().parse_args()
        outcome = run(arguments)
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
        if arguments.apply:
            print(REMINDER)
    except (ValueError, OSError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
