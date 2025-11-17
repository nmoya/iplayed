from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> int:
    """Run a shell command, returning its exit code, and print helpful errors."""
    executable = command[0]
    if shutil.which(executable) is None:
        print(f"Error: '{executable}' is not available on PATH, cannot {description}.", file=sys.stderr)
        return 1

    try:
        completed = subprocess.run(command, check=False)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Failed to {description}: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


def serve_zola(_: argparse.Namespace) -> int:
    """Start the Zola dev server."""
    return run_command(["zola", "serve"], "serve the Zola site")


def run_cli(_: argparse.Namespace) -> int:
    """Launch the uv-based CLI tool."""
    app_path = Path("iplayed_cli") / "app.py"
    return run_command(["uv", "run", str(app_path)], "start the CLI tool")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Developer helpers for the iplayed project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="Serve the Zola blog locally.")
    serve_parser.set_defaults(func=serve_zola)

    cli_parser = subparsers.add_parser("cli", help="Launch the iplayed CLI tool via uv.")
    cli_parser.set_defaults(func=run_cli)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = args.func
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
