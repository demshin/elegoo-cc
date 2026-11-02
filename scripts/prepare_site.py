#!/usr/bin/env python3
"""Prepare only explicitly allowed public content; never open archive targets."""

import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
TARGET = SITE / "src/content/docs"
SOURCE_DOCS = {
    "docs/evidence.md", "docs/evidence-more.md", "docs/evidence-expanded.md",
    "docs/evidence-qa.md", "docs/evidence-history.md", "docs/sources.md",
}
SITE_PAGES = {
    "site/home.mdx", "site/beginners.md", "site/advanced.md",
    "site/models.md", "site/method.md",
}


def article_count_label(count):
    if 11 <= count % 100 <= 14:
        noun = "статей"
    elif count % 10 == 1:
        noun = "статья"
    elif 2 <= count % 10 <= 4:
        noun = "статьи"
    else:
        noun = "статей"
    return f"{count} {noun}"


def main():
    manifest = json.loads((SITE / "content-manifest.json").read_text())
    pages = manifest["pages"]
    routes = {page["source"]: page["route"] for page in pages}
    assert len(routes) == len(pages), "Duplicate source in publication manifest"
    assert len(set(routes.values())) == len(routes), "Duplicate public route"
    article_count = sum(page["source"].startswith("faq/") for page in pages)
    assets = manifest.get("assets", [])
    assert len(set(assets)) == len(assets), "Duplicate public asset"
    assert all(re.fullmatch(r"(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_.-]+", asset) for asset in assets), "Invalid public asset path"
    actual_assets = set()
    for path in (SITE / "public").rglob("*"):
        assert not path.is_symlink(), f"Symlink in public assets: {path.name}"
        if path.is_file():
            actual_assets.add(path.relative_to(SITE / "public").as_posix())
    assert actual_assets == set(assets), "Public assets must match the publication manifest"
    aliases = manifest["aliases"]
    assert set(aliases) == {"README.md", "docs/topic-map.md", "docs/history-audit.md"}
    assert set(aliases.values()) <= set(routes.values())
    routes.update(aliases)
    base = "/" + os.environ.get("SITE_BASE", "").strip("/")
    base = base.rstrip("/")
    assert re.fullmatch(r"(?:/[A-Za-z0-9_-]+)*", base), "Invalid project base"

    def public_url(route, fragment=""):
        return base + "/" + (route + "/" if route else "") + ("#" + fragment if fragment else "")

    def rewrite(source, destination, label):
        if destination.startswith(("https://", "http://", "mailto:", "#")):
            return f"[{label}]({destination})"
        parsed = urlsplit(destination)
        assert not parsed.scheme and not parsed.netloc and not parsed.query, destination
        path = (ROOT / source).parent / unquote(parsed.path)
        path = path.resolve()
        assert path.is_relative_to(ROOT), f"Link leaves project: {source}: {destination}"
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("data/"):
            assert re.fullmatch(r"data/[^/]+/messages\d*\.html", relative), destination
            assert re.fullmatch(r"message\d+", parsed.fragment), destination
            return f"архив чата · {parsed.fragment.replace('message', 'сообщение ')}"
        assert relative in routes, f"Unlisted link: {source}: {destination}"
        return f"[{label}]({public_url(routes[relative], parsed.fragment)})"

    prepared = []
    for page in pages:
        source = page["source"]
        path = ROOT / source
        assert source in SOURCE_DOCS | SITE_PAGES or re.fullmatch(r"faq/(?:[a-z0-9-]+/)*[a-z0-9-]+\.md", source), source
        assert path.resolve() == path.absolute() and path.is_file(), source
        route = page["route"]
        assert not route or re.fullmatch(r"(?:[a-z0-9-]+/)*[a-z0-9-]+", route), route
        text = path.read_text()
        assert not re.search(r"!\[[^\]]*\]\([^)]*data/", text), source
        text = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", lambda m: rewrite(source, m[2], m[1]), text)
        text = text.replace("`data/.work/`", "локальном кеше")
        text = text.replace("Локальные ссылки требуют исходной выгрузки в `data/`.", "Исходная переписка закрыта; вместо ссылок на неё приведены архивные номера сообщений.")
        text = text.replace("в `data/`", "в закрытой локальной выгрузке")
        text = text.replace("в data/", "в закрытой локальной выгрузке")
        text = text.replace("{{BASE}}", base)
        text = text.replace("{{ARTICLE_COUNT_LABEL}}", article_count_label(article_count))
        assert not re.search(r"(?:\.\./)*data/|/Users/|file://|plugin://", text), source
        if not text.startswith("---\n"):
            title = re.search(r"^# (.+)$", text, re.M)
            assert title, f"Missing H1: {source}"
            text = text[:title.start()] + text[title.end():].lstrip("\n")
            metadata = "---\ntitle: " + json.dumps(title[1], ensure_ascii=False) + "\n"
            if page["group"] == "sources":
                metadata += "pagefind: false\n"
            text = metadata + "---\n\n" + text
        edit_url = "https://github.com/demshin/elegoo-cc/edit/main/" + source
        text = text.replace("---\n", "---\neditUrl: " + json.dumps(edit_url) + "\n", 1)
        suffix = ".mdx" if path.suffix == ".mdx" else ".md"
        prepared.append((TARGET / ((route or "index") + suffix), text))

    # Validate everything before replacing this tool's generated directory.
    assert TARGET == SITE / "src/content/docs" and not TARGET.is_symlink()
    if TARGET.exists():
        shutil.rmtree(TARGET)
    for path, text in prepared:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    print(f"Prepared {len(prepared)} public pages from allowlist; archive files were not read.")


if __name__ == "__main__":
    main()
