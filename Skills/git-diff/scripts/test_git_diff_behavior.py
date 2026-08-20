from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile


WORKSPACE = Path(__file__).resolve().parents[3]
TMP_ROOT = WORKSPACE / "tmp"


def git(repo: Path, *args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remove_tree(path: Path) -> None:
    def make_writable(function, target, _error) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    shutil.rmtree(path, onerror=make_writable)


def main() -> None:
    TMP_ROOT.mkdir(exist_ok=True)
    fixture = Path(tempfile.mkdtemp(prefix="git-diff-autonomy-", dir=TMP_ROOT))
    repo = fixture / "repo"
    repo.mkdir()
    try:
        git(repo, "init", "-b", "main")
        git(repo, "config", "user.name", "Autonomy Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
        write(repo / "same" / "old.txt", "one\ntwo\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-m", "Seed fixture")

        (repo / "same" / "old.txt").rename(repo / "same" / "new.txt")
        write(repo / "untracked.txt", "new\n")

        status_before = git(repo, "status", "--porcelain=v1", "-z").stdout
        index_path = Path(git(repo, "rev-parse", "--git-path", "index").stdout.decode().strip())
        if not index_path.is_absolute():
            index_path = repo / index_path
        index_before = digest(index_path)

        temp_index = index_path.with_name(index_path.name + ".git-diff-fixture")
        child_env = os.environ.copy()
        child_env["GIT_INDEX_FILE"] = str(temp_index)
        try:
            git(repo, "read-tree", "HEAD", env=child_env)
            git(repo, "add", "-A", env=child_env)
            off = git(repo, "-c", "diff.renames=false", "diff", "--cached", "--shortstat", env=child_env).stdout
            on = git(repo, "-c", "diff.renames=true", "diff", "--cached", "--shortstat", env=child_env).stdout
            assert b"files changed" in off or b"file changed" in off
            assert b"files changed" in on or b"file changed" in on
        finally:
            temp_index.unlink(missing_ok=True)

        assert digest(index_path) == index_before
        assert git(repo, "status", "--porcelain=v1", "-z").stdout == status_before

        before = {"same/old.txt"}
        after = {"same/new.txt", "untracked.txt"}
        before_folders = {str(Path(p).parent) for p in before}
        after_folders = {str(Path(p).parent) for p in after if Path(p).parent != Path(".")}
        assert "same" in before_folders and "same" in after_folders
        assert not (before_folders - after_folders)

        outside = fixture / "not-a-repo"
        outside.mkdir()
        isolated_env = os.environ.copy()
        isolated_env["GIT_CEILING_DIRECTORIES"] = str(fixture.resolve())
        missing = git(outside, "rev-parse", "--show-toplevel", check=False, env=isolated_env)
        assert missing.returncode != 0
        print("git-diff disposable behavior scenarios passed")
    finally:
        remove_tree(fixture)


if __name__ == "__main__":
    main()
