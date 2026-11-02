#!/usr/bin/env python3
"""Index a Telegram HTML export locally, preserving message and reply IDs."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re


class ChatParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.divs = []
        self.message = None
        self.start_depth = None
        self.messages = []
        self.last_author = "unknown"
        self.last_sender = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        if tag == "div":
            self.divs.append(classes)
            if "message" in classes and "default" in classes:
                self.start_depth = len(self.divs)
                self.message = {
                    "id": int(attrs["id"].removeprefix("message")),
                    "file": self.source,
                    "date": "",
                    "reply": None,
                    "author": self.last_author if "joined" in classes else "unknown",
                    "sender": self.last_sender if "joined" in classes else None,
                    "forwarded_author": None,
                    "text": "",
                    "links": [],
                    "media": [],
                    "_name": "",
                    "_forwarded": "",
                }
        if self.message is None:
            return
        if tag == "div" and "date" in classes and not self.message["date"]:
            self.message["date"] = attrs.get("title", "")
        if tag == "img" and "userpic" in classes:
            src = attrs.get("src", "")
            if "author_" in src:
                self.message["author"] = hashlib.sha256(src.encode()).hexdigest()[:16]
        in_text = any("text" in frame for frame in self.divs)
        if tag == "br" and in_text:
            self.message["text"] += "\n"
        if tag == "a":
            href = attrs.get("href", "")
            if any("reply_to" in frame for frame in self.divs):
                match = re.search(r'(?:go_to_message|#message)(\d+)', href)
                if match:
                    self.message["reply"] = int(match[1])
            elif in_text and href.startswith(("http://", "https://")):
                self.message["links"].append(href)
            elif href.startswith(("photos/", "video_files/", "files/", "voice_messages/")):
                self.message["media"].append(href)

    def handle_data(self, data):
        if self.message is None:
            return
        if any("text" in frame for frame in self.divs):
            self.message["text"] += data
        if any("from_name" in frame for frame in self.divs):
            self.message["_name"] += data
        if any("forwarded_from" in frame for frame in self.divs):
            self.message["_forwarded"] += data

    def handle_endtag(self, tag):
        if tag != "div" or not self.divs:
            return
        if self.message is not None and len(self.divs) == self.start_depth:
            name = self.message.pop("_name").strip()
            forwarded = self.message.pop("_forwarded").strip()
            if forwarded.startswith("Forwarded from "):
                origin = forwarded.removeprefix("Forwarded from ").strip()
                if origin:
                    self.message["forwarded_author"] = hashlib.sha256(origin.encode()).hexdigest()[:16]
            if self.message["author"] == "unknown" and name:
                self.message["author"] = hashlib.sha256(name.encode()).hexdigest()[:16]
            if name:
                self.message["sender"] = hashlib.sha256(name.encode()).hexdigest()[:16]
            self.last_author = self.message["author"]
            self.last_sender = self.message["sender"]
            self.message["text"] = self.message["text"].strip()
            self.message["links"] = list(dict.fromkeys(self.message["links"]))
            self.message["media"] = list(dict.fromkeys(self.message["media"]))
            self.messages.append(self.message)
            self.message = None
            self.start_depth = None
        self.divs.pop()


def page_number(path):
    return int(path.stem.removeprefix("messages") or "1")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("export", type=Path)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    data_root = Path("data").resolve()
    export = args.export.resolve()
    output = args.output.resolve()
    if not export.is_relative_to(data_root) or not output.is_relative_to(data_root):
        cli.error("Both export and output must be inside the local data/ directory")
    pages = sorted(export.glob("messages*.html"), key=page_number)
    if not pages:
        cli.error("No messages*.html files found")
    output.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    with output.open("w", encoding="utf-8") as handle:
        for page in pages:
            parser = ChatParser(page.name)
            source = page.read_text(encoding="utf-8")
            parser.feed(source)
            parser.close()
            expected = len(re.findall(r'<div class="message default[^\"]*"', source))
            if len(parser.messages) != expected:
                raise ValueError(f"Message count mismatch in {page.name}")
            for message in parser.messages:
                if message["id"] in seen:
                    raise ValueError(f"Duplicate message ID: {message['id']}")
                seen.add(message["id"])
                handle.write(json.dumps(message, ensure_ascii=False) + "\n")
            print(f"{page.name}: {len(parser.messages)} messages")
    print(f"Indexed {len(seen)} messages into {output.relative_to(data_root)}")


if __name__ == "__main__":
    main()
