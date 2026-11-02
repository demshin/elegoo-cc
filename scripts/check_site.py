#!/usr/bin/env python3
"""Verify static page coverage, links and exclusion of private archive files."""

from html.parser import HTMLParser
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.id_counts = Counter()
        self.tags = Counter()
        self.lang = None
        self.viewport = False
        self.images_have_alt = True
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.tags[tag] += 1
        if "id" in attrs:
            self.ids.add(attrs["id"])
            self.id_counts[attrs["id"]] += 1
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = "width=device-width" in attrs.get("content", "")
        if tag == "img" and "alt" not in attrs:
            self.images_have_alt = False
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def main():
    root = Path(__file__).resolve().parent.parent / "site"
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--dist", type=Path, default=root / "dist")
    dist = cli.parse_args().dist.resolve()
    base = "/" + os.environ.get("SITE_BASE", "").strip("/")
    base = base.rstrip("/")
    manifest = json.loads((root / "content-manifest.json").read_text())
    pages = {}
    for item in manifest["pages"]:
        path = dist / item["route"] / "index.html"
        assert path.is_file(), f"Missing page: {path}"
    for path in dist.rglob("*"):
        assert not path.is_symlink(), f"Symlink in output: {path}"
        if not path.is_file():
            continue
        relative = path.relative_to(dist).as_posix()
        assert not re.search(r"(?:^|/)(?:data|photos|video_files|\.work|node_modules|\.agents)(?:/|$)|messages\d*\.html|\.jsonl$", relative), relative
        if path.suffix in {".html", ".json", ".js", ".css", ".xml", ".svg"}:
            text = path.read_text()
            assert not re.search(r"ChatExport|chatExport|data/\.work|\.\./data/|/Users/|<div class=[\"']message", text), f"Private material in {relative}"
            if path.suffix == ".html":
                pages[path] = Page(text)
    checked = 0
    for path, page in pages.items():
        assert page.lang == "ru", f"Wrong page language: {path}"
        assert page.viewport, f"Missing mobile viewport: {path}"
        assert page.tags["h1"] == 1 and page.tags["main"] == 1, f"Invalid page landmarks: {path}"
        assert all(count == 1 for count in page.id_counts.values()), f"Duplicate element IDs: {path}"
        assert page.images_have_alt, f"Image without alt attribute: {path}"
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith("/"):
                assert url.path.startswith(base + "/"), f"Base missing: {path}: {link}"
                target = dist / unquote(url.path[len(base):]).lstrip("/")
            else:
                target = path.parent / unquote(url.path) if url.path else path
            target = target.resolve()
            assert target.is_relative_to(dist.resolve()), f"Link outside output: {link}"
            if target.is_dir():
                target /= "index.html"
            assert target.is_file(), f"Broken link: {path.relative_to(dist)}: {link}"
            if url.fragment and target in pages:
                assert unquote(url.fragment) in pages[target].ids, f"Broken anchor: {path.relative_to(dist)}: {link}"
            checked += 1
    metadata = json.loads((dist / "pagefind/pagefind-entry.json").read_text())
    assert "ru" in metadata["languages"], "Russian search index missing"
    print(f"OK: {len(manifest['pages'])} allowlisted pages, {len(pages)} HTML files, {checked} local URLs/anchors; Russian search index; semantic HTML/mobile viewport; no archive assets.")


if __name__ == "__main__":
    main()
