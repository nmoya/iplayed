import shutil
import subprocess
import tempfile
from pathlib import Path

from file_persistence import clear_pending_deploy


COMPLETIONS_FILE = Path("iplayed_cli/data/completions.json")


class DeployError(Exception):
    pass


def _run_git(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
        raise DeployError(output or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def _repo_root() -> Path:
    return Path(_run_git(["rev-parse", "--show-toplevel"], Path.cwd()))


def _current_branch(repo: Path) -> str:
    return _run_git(["branch", "--show-current"], repo)


def _commit_and_push(repo: Path, message: str) -> None:
    _run_git(["add", "--", str(COMPLETIONS_FILE)], repo)
    staged = _run_git(["diff", "--cached", "--name-only", "--", str(COMPLETIONS_FILE)], repo)
    if not staged:
        clear_pending_deploy()
        return
    _run_git(["commit", "-m", message, "--", str(COMPLETIONS_FILE)], repo)
    _run_git(["push", "origin", "main"], repo)
    clear_pending_deploy()


def deploy_completions(message: str) -> None:
    message = message.strip()
    if not message:
        raise DeployError("Deploy message is required.")

    repo = _repo_root()
    source = repo / COMPLETIONS_FILE
    if not source.exists():
        raise DeployError(f"{COMPLETIONS_FILE} does not exist.")

    if _current_branch(repo) == "main":
        _commit_and_push(repo, message)
        return

    temp_dir = Path(tempfile.mkdtemp(prefix="iplayed-deploy-"))
    worktree = temp_dir / "main"
    try:
        _run_git(["worktree", "add", str(worktree), "main"], repo)
        target = worktree / COMPLETIONS_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        _commit_and_push(worktree, message)
    finally:
        try:
            _run_git(["worktree", "remove", "--force", str(worktree)], repo)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
