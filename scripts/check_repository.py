#!/usr/bin/env python3
"""Reject private files in the Git publication set without opening them."""

from pathlib import Path
import re
import subprocess


def main():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True, text=True,
    )
    files = result.stdout.strip("\0").split("\0") if result.stdout else []
    assert files, "No tracked public files"
    forbidden = (
        "data/", ".agents/", ".codex/", "docs/prompts/", "site/node_modules/",
        "site/dist/", "site/.astro/", "site/src/content/docs/",
    )
    for relative in files:
        path = root / relative
        assert not relative.startswith(forbidden), f"Private/generated file tracked: {relative}"
        assert not any(part.startswith(".env") or part in {".DS_Store", "__pycache__"} for part in path.relative_to(root).parts), f"Local file tracked: {relative}"
        assert not re.search(r"(?:^|/)messages\d*\.html$|\.(?:jsonl|log|pyc)$", relative), f"Archive/log file tracked: {relative}"
        assert not path.is_symlink(), f"Symlink tracked: {relative}"
    print(f"OK: {len(files)} tracked source files; no private archive, local skills or generated output.")


if __name__ == "__main__":
    main()
