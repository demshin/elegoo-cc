#!/usr/bin/env python3
"""Read selected messages from the private chat index without exposing author names."""

import argparse
import json
from pathlib import Path
import re


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--ids", type=int, nargs="+")
    cli.add_argument("--pattern")
    cli.add_argument("--limit", type=int, default=20)
    cli.add_argument("--offset", type=int, default=0)
    cli.add_argument("--chars", type=int, default=800)
    cli.add_argument("--chain", type=int, default=0)
    cli.add_argument("--near", type=int, default=0)
    args = cli.parse_args()
    messages = [json.loads(line) for line in Path("data/.work/messages.jsonl").open(encoding="utf-8")]
    by_id = {m["id"]: m for m in messages}
    if args.ids:
        selected = [by_id[mid] for mid in args.ids if mid in by_id]
    elif args.pattern:
        pattern = re.compile(args.pattern, re.I | re.S)
        found = [m for m in messages if pattern.search(m["text"])]
        print(f"Matches: {len(found)}; offset: {args.offset}")
        selected = found[args.offset:args.offset + args.limit]
    else:
        cli.error("Specify --ids or --pattern")
    printed = set()

    def show(message):
        if message["id"] in printed:
            return
        printed.add(message["id"])
        print(f"\n{message['id']} | {message['file']} | {message['date']} | a={message['author'][:8]} | reply={message['reply']}")
        text = message["text"]
        print(text if args.chars == 0 else text[:args.chars])
        if message["media"]:
            print("MEDIA:", message["media"])

    for message in selected:
        show(message)
        current = message
        seen = {message["id"]}
        for _ in range(args.chain):
            current = by_id.get(current["reply"])
            if current is None or current["id"] in seen:
                break
            seen.add(current["id"])
            show(current)
        if args.near:
            for neighbor in messages:
                if abs(neighbor["id"] - message["id"]) <= args.near:
                    show(neighbor)


if __name__ == "__main__":
    main()
