#!/usr/bin/env python3
"""Prepare only explicitly allowed public content; never open archive targets."""

from datetime import date
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlencode, urlsplit


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
REVIEW_LABELS = {
    "supported": "Сверено с источниками",
    "partial": "Подтверждено частично",
    "contradicted": "Найдены противоречия",
    "insufficient": "Недостаточно подтверждений",
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


def article_info(text):
    title = re.search(r"^# (.+)$", text, re.M)
    assert title, "Article needs an H1"
    scope = re.search(r"\*\*Область:\*\*\s*(.+?)(?=\s*\*\*(?:Обновлено|Сверка):\*\*|\n|$)", text)
    return title[1].strip(), scope[1].strip() if scope else "Применимость уточняйте в статье."


def review_status(text, record):
    if record is None:
        return "Сверка этой редакции отдельно не зафиксирована. Основания приведены ниже."
    reviewed_on = date.fromisoformat(record["reviewed_on"]).strftime("%d.%m.%Y")
    if sha256(text.encode()).hexdigest() != record["content_sha256"]:
        return f"Текст изменён после сверки {reviewed_on}; нужна повторная сверка."
    return f"{REVIEW_LABELS[record['status']]} {reviewed_on}. {record['summary']}"


def feedback_links(route, title, scope):
    origin = os.environ.get("SITE_URL", "https://demshin.github.io").rstrip("/")
    prefix = os.environ.get("SITE_BASE", "/elegoo-cc").strip("/")
    canonical = origin + "/" + (prefix + "/" if prefix else "") + route + "/"
    endpoint = "https://github.com/demshin/elegoo-cc/issues/new?"
    common = {"page": canonical}
    return {
        "case": endpoint + urlencode({**common, "template": "case.yml", "title": "Случай: " + title, "conditions": scope}),
        "correction": endpoint + urlencode({**common, "template": "correction.yml", "title": "Исправление: " + title}),
    }


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
    sources = {}
    for page in pages:
        source = page["source"]
        path = ROOT / source
        assert source in SOURCE_DOCS | SITE_PAGES or re.fullmatch(r"(?:faq/(?:[a-z0-9-]+/)*|site/topics/)[a-z0-9-]+\.md", source), source
        assert path.resolve() == path.absolute() and path.is_file(), source
        assert not page["route"] or re.fullmatch(r"(?:[a-z0-9-]+/)*[a-z0-9-]+", page["route"]), page["route"]
        sources[source] = path.read_bytes().decode("utf-8")
    review_file = SITE / "article-reviews.json"
    assert not review_file.is_symlink(), "Symlink in article review registry"
    reviews = json.loads(review_file.read_text())["reviews"] if review_file.is_file() else {}
    for source, record in reviews.items():
        assert source in sources and source.startswith("faq/"), f"Review for unlisted article: {source}"
        assert re.fullmatch(r"[a-f0-9]{64}", record["content_sha256"]), source
        date.fromisoformat(record["reviewed_on"])
        assert record["status"] in REVIEW_LABELS and isinstance(record["summary"], str) and record["summary"].strip(), source
        assert not re.search(r"data/|/Users/|file://|plugin://|[<>\r\n]", record["summary"]), f"Invalid public review summary: {source}"
        assert isinstance(record["evidence"], list) and record["evidence"], source
        assert all(isinstance(url, str) and not re.search(r"data/|/Users/|file://|plugin://", url) for url in record["evidence"]), source
    groups = {group["id"]: group for group in manifest.get("groups", [])}
    assert len(groups) == len(manifest.get("groups", [])), "Duplicate topic group"
    for group in groups.values():
        assert group["route"] in routes.values(), f"Topic overview missing: {group['id']}"
    if groups:
        for page in pages:
            if page["source"].startswith("faq/"):
                assert page["group"] in groups, f"Article has no topic: {page['source']}"

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
        route = page["route"]
        original = sources[source]
        text = original.replace("\r\n", "\n")
        assert not re.search(r"!\[[^\]]*\]\([^)]*data/", text), source
        text = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", lambda m: rewrite(source, m[2], m[1]), text)
        text = text.replace("`data/.work/`", "локальном кеше")
        text = text.replace("Локальные ссылки требуют исходной выгрузки в `data/`.", "Исходная переписка закрыта; вместо ссылок на неё приведены архивные номера сообщений.")
        text = text.replace("в `data/`", "в закрытой локальной выгрузке")
        text = text.replace("в data/", "в закрытой локальной выгрузке")
        text = text.replace("{{BASE}}", base)
        text = text.replace("{{ARTICLE_COUNT_LABEL}}", article_count_label(article_count))
        if "{{TOPIC_CARDS}}" in text:
            cards = []
            for group in groups.values():
                title = json.dumps(group["label"], ensure_ascii=False)
                description = json.dumps(group["description"], ensure_ascii=False)
                href = json.dumps(public_url(group["route"]))
                cards.append(f"  <LinkCard title={{{title}}} description={{{description}}} href={{{href}}} />")
            text = text.replace("{{TOPIC_CARDS}}", "\n".join(cards))
        if "topic" in page:
            topic = page["topic"]
            assert topic in groups, f"Unknown topic: {topic}"
            assert route == groups[topic]["route"], f"Wrong topic overview route: {topic}"
            items = [item for item in pages if item["source"].startswith("faq/") and item["group"] == topic]
            rows = [f"{article_count_label(len(items))} в этом разделе.", "", "| Симптом или вопрос | Применимость |", "| --- | --- |"]
            for item in items:
                title, scope = article_info(sources[item["source"]])
                scope = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", lambda m: rewrite(item["source"], m[2], m[1]), scope)
                title, scope = title.replace("|", "\\|"), scope.replace("|", "\\|")
                rows.append(f"| [{title}]({public_url(item['route'])}) | {scope} |")
            assert "{{TOPIC_ARTICLES}}" in text, source
            text = text.replace("{{TOPIC_ARTICLES}}", "\n".join(rows))
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
        if source.startswith("faq/"):
            title, scope = article_info(original)
            record = reviews.get(source)
            grounds = {}
            def add_ground(link):
                destination = re.search(r"\]\((.*)\)$", link)[1]
                grounds.setdefault(destination, link)
            for match in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", original):
                if re.search(r"(?:^|/)docs/evidence[^/]*\.md(?:#|$)", match[2]):
                    add_ground(rewrite(source, match[2], match[1]))
            if record:
                for index, destination in enumerate(record["evidence"], 1):
                    add_ground(rewrite("README.md", destination, f"Источник сверки {index}"))
            status = review_status(original, record)
            panel = "> **Сверка с источниками:** " + status + "\n>\n> **Основания:** " + (" · ".join(grounds.values()) or "См. источники в тексте статьи.")
            metadata_end = text.index("\n---\n", 4) + len("\n---\n")
            text = text[:metadata_end] + "\n" + panel + "\n" + text[metadata_end:]
            links = feedback_links(route, title, scope)
            text += ('\n\n<section class="article-feedback" aria-label="Обратная связь по статье" data-pagefind-ignore>\n'
                     '<p><strong>Есть опыт по этой теме?</strong> Добавьте свой случай или сообщите о неточности.</p>\n'
                     '<div class="feedback-actions">'
                     f'<a href="{escape(links["case"], quote=True)}">Добавить свой случай</a>'
                     f'<a href="{escape(links["correction"], quote=True)}">Сообщить об ошибке</a>'
                     '</div>\n<p>Обсуждение откроется в GitHub Issues. Для отправки нужен аккаунт GitHub.</p>\n</section>\n')
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
