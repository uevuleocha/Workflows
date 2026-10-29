"""Integration fixtures retained under an explicitly supplied workspace tmp path."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HELPER = Path(__file__).with_name("bootstrap.py")


def snapshot(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path, required=True)
    root = parser.parse_args().scratch.absolute()
    if "tmp" not in root.parts or root.exists():
        raise ValueError("Use a nonexistent scratch directory beneath workspace tmp")
    root.mkdir(parents=True)
    env = {key: val for key, val in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_NAME="Bootstrap Test", GIT_COMMITTER_NAME="Bootstrap Test",
               GIT_AUTHOR_EMAIL="bootstrap@example.invalid", GIT_COMMITTER_EMAIL="bootstrap@example.invalid")
    results = []

    def git(folder, *args):
        run = subprocess.run(["git", "-C", str(folder), *args], env=env,
                             capture_output=True, text=True, encoding="utf-8")
        if run.returncode:
            raise AssertionError(run.stderr)
        return run.stdout.strip()

    def folder(name):
        target = root / name
        target.mkdir()
        return target

    def invoke(target, *options, apply=True, custom_env=None, success=True):
        command = [sys.executable, "-X", "utf8", str(HELPER), "--target", str(target),
                   "--name", target.name, "--tier", "World", "--solar-system", "Tools",
                   "--purpose", "A reproducible test workspace."]
        if apply:
            command += ["--apply", "--confirmed"]
        command += options
        run = subprocess.run(command, env=custom_env or env, capture_output=True, text=True, encoding="utf-8")
        assert (run.returncode == 0) == success, (command, run.stdout, run.stderr)
        result = {"case": target.name, "arguments": options, "exit": run.returncode,
                  "stdout": run.stdout, "stderr": run.stderr}
        results.append(result)
        (root / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        return run

    fresh = folder("Fresh World")
    before = snapshot(fresh)
    invoke(fresh, apply=False)
    assert snapshot(fresh) == before and not list(fresh.iterdir())
    run = invoke(fresh)
    expected = {".git", ".gitignore", "AGENTS.md", "CLAUDE.md", "README.md", "Archive", "tmp"}
    assert {p.name for p in fresh.iterdir()} == expected
    assert (fresh / "Archive/Live").is_dir() and (fresh / "Archive/Historical").is_dir()
    assert (fresh / ".gitignore").read_bytes() == b""
    assert Path(git(fresh, "rev-parse", "--show-toplevel")) == fresh
    assert git(fresh, "branch", "--show-current") == "main"
    assert git(fresh, "rev-list", "--count", "HEAD") == "1"
    assert set(git(fresh, "ls-tree", "--name-only", "HEAD").splitlines()) == expected - {".git", "Archive", "tmp"}
    assert git(fresh, "remote") == ""
    assert "This is a lightweight bootstrap." in run.stdout
    contract = (fresh / "CLAUDE.md").read_text(encoding="utf-8")
    assert "under the **** world" not in contract and "a world in the **Tools**" in contract
    for filename in ("CLAUDE.md", "AGENTS.md", "README.md"):
        assert not re.search(r"\{[^{}]*\}", (fresh / filename).read_text(encoding="utf-8"))
    before = snapshot(fresh)
    invoke(fresh, success=False)
    assert snapshot(fresh) == before

    continent = folder("Continent")
    invoke(continent, "--tier", "Continent", "--world", "Games", "--solar-system", "Mastery")
    assert "a continent under the **Games** world" in (continent / "CLAUDE.md").read_text(encoding="utf-8")

    partial = folder("Partial")
    (partial / "README.md").write_bytes(b"Existing README\r\n")
    (partial / ".gitignore").write_bytes(b"private/\r\n")
    (partial / "Archive").mkdir()
    (partial / "tmp").mkdir()
    old = snapshot(partial)
    run = invoke(partial)
    assert all((partial / name).read_bytes() == {"README.md": b"Existing README\r\n", ".gitignore": b"private/\r\n"}[name] for name in old)
    assert set(git(partial, "ls-tree", "--name-only", "HEAD").splitlines()) == {"AGENTS.md", "CLAUDE.md"}
    assert '"skipped"' in run.stdout and '"README.md"' in run.stdout
    before = snapshot(partial)
    invoke(partial, success=False)
    assert snapshot(partial) == before

    empty_stub = folder("Empty stub")
    (empty_stub / "AGENTS.md").write_bytes(b"")
    invoke(empty_stub)
    assert (empty_stub / "AGENTS.md").read_bytes() == b""

    staged = folder("Staged")
    git(staged, "init", "-b", "main", "--template=")
    (staged / "keep.txt").write_bytes(b"keep")
    git(staged, "add", "keep.txt")
    before = snapshot(staged)
    invoke(staged, success=False)
    assert snapshot(staged) == before

    existing = folder("Existing repo")
    git(existing, "init", "-b", "topic", "--template=")
    (existing / "keep.txt").write_bytes(b"keep")
    git(existing, "add", "keep.txt")
    git(existing, "-c", "commit.gpgsign=false", "commit", "-m", "Existing")
    invoke(existing)
    assert git(existing, "branch", "--show-current") == "topic"
    assert git(existing, "rev-list", "--count", "HEAD") == "2"

    no_commit = folder("No commit")
    invoke(no_commit, "--no-commit")
    assert git(no_commit, "ls-files") == ""

    missing_identity = folder("Missing identity")
    anonymous = {k: v for k, v in env.items() if k not in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL")}
    identity_config = root / "identity-required.gitconfig"
    identity_config.write_text('[user]\n    useConfigOnly = true\n', encoding='utf-8')
    anonymous['GIT_CONFIG_GLOBAL'] = str(identity_config)
    invoke(missing_identity, custom_env=anonymous, success=False)
    assert "identity unavailable" in results[-1]['stderr']
    assert not list(missing_identity.iterdir())

    for label, setup in (("Wrong type", lambda p: (p / "Archive").write_bytes(b"file")),
                         ("Git file", lambda p: (p / ".git").write_text("gitdir: ../elsewhere\n", encoding="utf-8")),
                         ("Established", lambda p: (p / "CLAUDE.md").write_bytes(b"Real instructions"))):
        target = folder(label)
        setup(target)
        before = snapshot(target)
        invoke(target, success=False)
        assert snapshot(target) == before

    invalid = folder("Invalid placeholder")
    invoke(invalid, "--purpose", "{unresolved}", success=False)
    assert not list(invalid.iterdir())
    redirected = folder("Environment redirect")
    invoke(redirected, custom_env=dict(env, GIT_DIR=str(fresh / ".git")), success=False)
    assert not list(redirected.iterdir())
    custom_ignore = folder("Custom ignore")
    invoke(custom_ignore, "--gitignore-content", "private/\n")
    assert (custom_ignore / ".gitignore").read_bytes() == b"private/\n"

    detached = folder("Detached")
    git(detached, "init", "-b", "main", "--template=")
    git(detached, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "Existing")
    git(detached, "checkout", "--detach")
    before = snapshot(detached)
    invoke(detached, success=False)
    assert snapshot(detached) == before

    filtered = folder("Filtered")
    git(filtered, "init", "-b", "main", "--template=")
    (filtered / ".gitattributes").write_text('*.md filter=custom\n', encoding='utf-8')
    before = snapshot(filtered)
    invoke(filtered, success=False)
    assert snapshot(filtered) == before

    unconfirmed = folder("Unconfirmed")
    command = [sys.executable, "-X", "utf8", str(HELPER), "--target", str(unconfirmed),
               "--name", "Unconfirmed", "--tier", "World", "--solar-system", "Tools",
               "--purpose", "Test approval", "--apply"]
    run = subprocess.run(command, env=env, capture_output=True, text=True, encoding='utf-8')
    assert run.returncode != 0 and '--confirmed' in run.stderr and not list(unconfirmed.iterdir())
    results.append({'case':'Unconfirmed', 'exit':run.returncode, 'stderr':run.stderr})
    (root / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"PASS: {len(results)} integration invocations; retained fixtures: {root}")


if __name__ == "__main__":
    main()
