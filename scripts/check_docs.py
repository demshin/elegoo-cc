#!/usr/bin/env python3
"""Check public Markdown links, local message anchors and data exclusion rules."""

import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import unquote


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--public", action="store_true", help="Validate archive pointer syntax without reading the private archive")
    public = cli.parse_args().public
    root = Path.cwd().resolve()
    documents = [*Path(".").glob("*.md"), *Path("faq").rglob("*.md"), *Path("docs").rglob("*.md"), *Path("site").glob("*.md"), *Path("site").glob("*.mdx")]
    if public:
        documents = [path for path in documents if not path.is_relative_to("docs/prompts")]
    cache = {}
    links = 0
    source_links = 0
    external = set()
    for document in documents:
        content = document.read_text(encoding="utf-8")
        assert len(re.findall(r"^```", content, re.M)) % 2 == 0, f"Unclosed code block: {document}"
        assert '<div class="message' not in content, f"Raw export markup: {document}"
        assert not re.search(r'!\[[^\]]*\]\([^)]*data/', content), f"Raw media embed: {document}"
        for destination in re.findall(r"\]\(([^)]+)\)", content):
            if destination.startswith(("https://", "http://")):
                external.add(destination)
                continue
            filename, _, fragment = destination.partition("#")
            archive = os.path.normpath(document.parent / unquote(filename)) if filename else ""
            if public and archive.startswith("data/"):
                assert re.fullmatch(r"data/[^/]+/messages\d*\.html", archive), f"Invalid archive pointer: {document}"
                assert re.fullmatch(r"message\d+", fragment), f"Invalid message ID: {document}"
                source_links += 1
                links += 1
                continue
            target = (document.parent / unquote(filename)).resolve() if filename else document.resolve()
            assert target.is_relative_to(root), f"Link outside project: {document} -> {destination}"
            assert target.is_file(), f"Missing link: {document} -> {destination}"
            if target not in cache:
                cache[target] = target.read_text(encoding="utf-8")
            if fragment:
                if target.suffix == ".html" and fragment.startswith("message"):
                    assert f'id="{fragment}"' in cache[target], f"Missing message: {destination}"
                    source_links += 1
                else:
                    headings = re.findall(r"^#+ (.+)$", cache[target], re.M)
                    anchors = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
                    assert unquote(fragment) in anchors, f"Missing heading: {document} -> {destination}"
            links += 1
    for script in Path("scripts").glob("*.py"):
        compile(script.read_text(encoding="utf-8"), str(script), "exec")
    with tempfile.TemporaryDirectory(prefix="elegoo-ignore-") as folder:
        subprocess.run(["git", "init", "--quiet", folder], check=True, capture_output=True)
        Path(folder, ".gitignore").write_text(Path(".gitignore").read_text())
        protected = ["data/export/messages.html", "data/.local/beget-api.json", "data/.work/messages.jsonl", "data/.work/topics/catalog.json", ".agents/skills/example/SKILL.md", ".codex/config.toml", ".env", ".env.local", "docs/prompts/humanize-faq.md", ".DS_Store", "scripts/__pycache__/index_chat.pyc", "site/node_modules/example/index.js", "site/dist/index.html", "site/src/content/docs/index.md", "site/.astro/content-assets.mjs"]
        result = subprocess.run(["git", "-C", folder, "check-ignore", "--no-index", *protected], capture_output=True, text=True)
        assert result.returncode == 0 and set(result.stdout.splitlines()) == set(protected), result.stderr or result.stdout
    source_check = "archive pointers (syntax only; archive not read)" if public else "message anchors (archive checked)"
    print(f"OK: {len(documents)} Markdown documents, {links} local links, {source_links} {source_check}")
    print(f"OK: Python syntax and data exclusion; {len(external)} distinct external URLs listed (not HTTP-tested)")


if __name__ == "__main__":
    main()
