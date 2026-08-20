from __future__ import annotations

from pathlib import Path
import os
import shutil
import stat
import subprocess
import tempfile


WORKSPACE = Path(__file__).resolve().parents[3]
TMP_ROOT = WORKSPACE / "tmp"


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def configure(repo: Path) -> None:
    git(repo, "config", "user.name", "Autonomy Fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")


def remove_tree(path: Path) -> None:
    def make_writable(function, target, _error) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    shutil.rmtree(path, onerror=make_writable)


def commit_and_push_nested(nested: Path, scope: list[str], subject: str) -> str:
    git(nested, "add", "-A", "--", *scope)
    staged = git(nested, "diff", "--cached", "--name-only").stdout.decode().splitlines()
    assert staged == scope
    git(nested, "commit", "-m", subject, "-m", "Agent: Codex")
    git(nested, "push")
    git(nested, "fetch", "origin")
    git(nested, "merge-base", "--is-ancestor", "HEAD", "@{upstream}")
    return git(nested, "rev-parse", "HEAD").stdout.decode().strip()


def sync_pointer(hub: Path, nested_rel: str, nested_head: str, subject: str) -> None:
    git(hub, "add", "--", nested_rel)
    staged = git(hub, "diff", "--cached", "--name-only").stdout.decode().splitlines()
    assert staged == [nested_rel]
    raw = git(hub, "diff", "--cached", "--raw").stdout.decode()
    assert "160000 160000" in raw
    staged_sha = git(hub, "rev-parse", f":{nested_rel}").stdout.decode().strip()
    assert staged_sha == nested_head
    git(hub, "commit", "-m", subject, "-m", "Agent: Codex")
    git(hub, "push")
    git(hub, "fetch", "origin")
    remote_sha = git(hub, "ls-tree", "@{upstream}", "--", nested_rel).stdout.decode().split()[2]
    assert remote_sha == nested_head


def main() -> None:
    TMP_ROOT.mkdir(exist_ok=True)
    fixture = Path(tempfile.mkdtemp(prefix="stage-commit-push-autonomy-", dir=TMP_ROOT))
    try:
        nested_remote = fixture / "nested-remote.git"
        hub_remote = fixture / "hub-remote.git"
        nested_seed = fixture / "nested-seed"
        hub = fixture / "hub"
        for bare in (nested_remote, hub_remote):
            bare.mkdir()
            git(bare, "init", "--bare")

        nested_seed.mkdir()
        git(nested_seed, "init", "-b", "main")
        configure(nested_seed)
        write(nested_seed / "tracked.txt", "seed\n")
        git(nested_seed, "add", "-A")
        git(nested_seed, "commit", "-m", "Seed nested repository")
        git(nested_seed, "remote", "add", "origin", str(nested_remote))
        git(nested_seed, "push", "-u", "origin", "main")
        git(nested_remote, "symbolic-ref", "HEAD", "refs/heads/main")

        hub.mkdir()
        git(hub, "init", "-b", "main")
        configure(hub)
        git(hub, "remote", "add", "origin", str(hub_remote))
        write(hub / "README.md", "fixture\n")
        git(hub, "add", "README.md")
        git(hub, "commit", "-m", "Seed hub repository")
        git(hub, "clone", str(nested_remote), "deps/nested")
        write(
            hub / ".gitmodules",
            f'[submodule "nested"]\n\tpath = deps/nested\n\turl = {nested_remote.as_posix()}\n',
        )
        git(hub, "add", ".gitmodules", "deps/nested")
        git(hub, "commit", "-m", "Add nested repository")
        git(hub, "push", "-u", "origin", "main")
        git(hub_remote, "symbolic-ref", "HEAD", "refs/heads/main")

        nested = hub / "deps" / "nested"
        configure(nested)

        write(nested / "tracked.txt", "all scope\n")
        write(nested / "added.txt", "added\n")
        all_head = commit_and_push_nested(nested, ["added.txt", "tracked.txt"], "Exercise All scope")
        sync_pointer(hub, "deps/nested", all_head, "Bump nested pointer after All scope")

        write(nested / "tracked.txt", "particular scope\n")
        particular_head = commit_and_push_nested(nested, ["tracked.txt"], "Exercise Particular scope")
        sync_pointer(hub, "deps/nested", particular_head, "Bump nested pointer after Particular scope")

        skill_text = (WORKSPACE / "Skills" / "stage-commit-push" / "SKILL.md").read_text(encoding="utf-8")
        assert "If scope is ambiguous, ask before mutation." in skill_text
        assert "Hard-stop if the remote is ahead or the histories diverged." in skill_text
        assert "require explicit user approval before a push that would include pre-existing unpushed commits" in skill_text
        assert "Lowercase `m` is not syncable." in skill_text
        assert "does not require a second approval" in skill_text

        other = fixture / "other"
        git(fixture, "clone", str(nested_remote), str(other))
        configure(other)
        write(other / "remote-ahead.txt", "ahead\n")
        git(other, "add", "remote-ahead.txt")
        git(other, "commit", "-m", "Advance remote")
        git(other, "push")
        git(nested, "fetch", "origin")
        counts = git(nested, "rev-list", "--left-right", "--count", "HEAD...@{upstream}").stdout.decode().split()
        assert int(counts[1]) > 0

        write(nested / "local-only.txt", "local\n")
        git(nested, "add", "local-only.txt")
        git(nested, "commit", "-m", "Create pre-existing local commit")
        unpushed = git(nested, "log", "--format=%H", "@{upstream}..HEAD").stdout.decode().splitlines()
        assert unpushed

        write(nested / "dirty.txt", "dirty\n")
        assert git(nested, "status", "--porcelain").stdout
        print("stage-commit-push disposable autonomy scenarios passed")
    finally:
        remove_tree(fixture)


if __name__ == "__main__":
    main()
