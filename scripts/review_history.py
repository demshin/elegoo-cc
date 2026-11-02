#!/usr/bin/env python3
"""Prepare and track an explicit sequential review of the private chat index."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


INDEX = Path("data/.work/messages.jsonl")
WORK = Path("data/.work/history-audit")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def messages():
    return [json.loads(line) for line in INDEX.read_text(encoding="utf-8").splitlines()]


def fingerprint():
    return hashlib.sha256(INDEX.read_bytes()).hexdigest()


def manifest():
    result = read_json(WORK / "manifest.json")
    if result["index_sha256"] != fingerprint():
        raise SystemExit("The index changed; do not reuse review coverage for a different export.")
    return result


def prepare(max_chars):
    WORK.mkdir(parents=True, exist_ok=True)
    if (WORK / "manifest.json").exists():
        existing = manifest()
        print(f"Existing queue: {len(existing['units'])} units; progress preserved")
        return
    units = []
    current = []
    size = 0
    source = None
    all_messages = messages()
    for message in all_messages:
        cost = len(message["text"]) + 85
        if current and (size + cost > max_chars or message["file"] != source):
            units.append({"id": f"H{len(units) + 1:04d}", "file": source, "message_ids": current})
            current = []
            size = 0
        current.append(message["id"])
        source = message["file"]
        size += cost
    if current:
        units.append({"id": f"H{len(units) + 1:04d}", "file": source, "message_ids": current})
    flattened = [mid for unit in units for mid in unit["message_ids"]]
    assert flattened == [message["id"] for message in all_messages]
    assert len(set(flattened)) == len(flattened)
    write_json(WORK / "manifest.json", {"index_sha256": fingerprint(), "message_count": len(flattened), "max_chars": max_chars, "units": units})
    write_json(WORK / "progress.json", {"reviewed": {}})
    print(f"Prepared {len(units)} units covering {len(flattened)} messages exactly once")


def get_unit(unit_id):
    return next(unit for unit in manifest()["units"] if unit["id"] == unit_id)


def show(unit_id):
    unit = get_unit(unit_id)
    by_id = {message["id"]: message for message in messages()}
    print(f"BEGIN {unit_id} | {unit['file']} | {len(unit['message_ids'])} messages")
    date = None
    for mid in unit["message_ids"]:
        message = by_id[mid]
        day = message["date"].split(",")[0]
        if day != date:
            print(f"DATE {day}")
            date = day
        name = message.get("sender") or "unknown"
        origin = f" forwarded={message['forwarded_author'][:8]}" if message.get("forwarded_author") else ""
        print(f"#{mid} a={message['author'][:8]} n={name[:8]}{origin} reply={message['reply']} media={len(message['media'])}")
        print(message["text"] or "[no text; assess attachments using the conversation context]")
    print(f"END {unit_id}")


def mark(unit_id, note_path):
    unit = get_unit(unit_id)
    if not note_path.resolve().is_relative_to(Path("data").resolve()):
        raise SystemExit("Private review notes must stay under data/.")
    note = read_json(note_path)
    if note.get("unit") != unit_id or note.get("full_text_reviewed") is not True:
        raise SystemExit("An explicit completed text review is required.")
    if not note.get("summary") or "candidates" not in note or "media_policy" not in note:
        raise SystemExit("Record the review summary, candidates and attachment handling.")
    selected = set(unit["message_ids"])
    for candidate in note["candidates"]:
        if not candidate.get("ids") or not set(candidate["ids"]) <= selected:
            raise SystemExit("Candidate source IDs must belong to this review unit.")
        if not candidate.get("decision") or not candidate.get("reason"):
            raise SystemExit("Candidates need a disposition and reason.")
    progress = read_json(WORK / "progress.json")
    if unit_id in progress["reviewed"]:
        raise SystemExit("Unit already reviewed; preserve its existing review record.")
    progress["reviewed"][unit_id] = note
    write_json(WORK / "progress.json", progress)
    print(f"Recorded completed text review: {unit_id}; attachments retain their stated status")


def status():
    queue = manifest()
    reviewed = read_json(WORK / "progress.json")["reviewed"]
    totals = Counter()
    done = Counter()
    for unit in queue["units"]:
        totals[unit["file"]] += len(unit["message_ids"])
        if unit["id"] in reviewed:
            done[unit["file"]] += len(unit["message_ids"])
    next_unit = next((unit["id"] for unit in queue["units"] if unit["id"] not in reviewed), None)
    print(f"Text reviewed: {sum(done.values())}/{queue['message_count']}; units {len(reviewed)}/{len(queue['units'])}; next {next_unit}")
    for source, count in totals.items():
        print(f"{source}: {done[source]}/{count}")


def report():
    queue = manifest()
    reviewed = read_json(WORK / "progress.json")["reviewed"]
    totals = Counter()
    done = Counter()
    for unit in queue["units"]:
        totals[unit["file"]] += len(unit["message_ids"])
        if unit["id"] in reviewed:
            done[unit["file"]] += len(unit["message_ids"])
    count = sum(done.values())
    next_unit = next((unit["id"] for unit in queue["units"] if unit["id"] not in reviewed), "нет")
    corpus = messages()
    forwarded = sum(bool(message.get("forwarded_author")) for message in corpus)
    lines = [
        "# Последовательный разбор всей истории", "",
        "Этот учёт дополняет [выборочный тематический разбор](topic-map.md). "
        "Полнота текстового чтения учитывается отдельно от поиска, проверки вложений и готовности статей.", "",
        f"В индексе **{queue['message_count']:,} обычных сообщений**; в последовательном проходе полностью прочитан текст "
        f"**{count:,} ({count / queue['message_count']:.1%})**. Завершено **{len(reviewed)} из {len(queue['units'])} блоков**. "
        f"Следующий блок: `{next_unit}`.", "",
        "Ранее выбранные основания статей не прибавляются к этому счётчику: они проверялись выборочно, "
        "без полного последовательного просмотра окружающих участков.", "",
        "| Файл выгрузки | Прочитано полностью | Всего сообщений |", "| --- | ---: | ---: |",
    ]
    lines.extend(f"| {source} | {done[source]} | {total} |" for source, total in totals.items())
    lines.extend([
        "", "## Как сохраняется проверка", "",
        "Блоки следуют порядку выгрузки, содержат полный текст без обрезки и вместе включают каждое индексированное сообщение ровно один раз. "
        "Для завершённого блока локально записываются выводы, кандидаты, причины отбора или отклонения и статус вложений. "
        "Хеш индекса защищает от переноса отметок на другую выгрузку.", "",
        "Кандидат ещё не статья: его нужно сопоставить с продолжением переписки, независимыми повторениями, "
        "явным результатом и документацией. Благодарность, обещание попробовать, фотография полученной запчасти "
        "и повторная пересылка не доказывают успешного устранения.", "",
        f"В архиве {forwarded} сообщений с указанием исходного автора пересылки. "
        "В локальном индексе подпись и аватар отправителя, а также подпись исходного автора пересылки учитываются отдельно. "
        "Одинаковые имена встречаются у разных профилей. Имя или аватар — только признак для сопоставления, "
        "а не доказательство личности или независимости случая; нужны также связи и продолжение переписки.", "",
        "Вложения не считаются просмотренными по факту чтения текста. Технические фотографии, видео и файлы "
        "при необходимости проверяются отдельно; непросмотренные материалы не используются как визуальное подтверждение.", "",
        "## Воспроизведение", "", "Требуется локальная выгрузка и её индекс в `data/`:", "", "```sh",
        "python3 scripts/review_history.py status",
        *(["python3 scripts/review_history.py show " + next_unit] if next_unit != "нет" else []),
        "python3 scripts/review_history.py report", "```", "",
        "Очередь, заметки, промежуточные файлы и исходные сообщения остаются в игнорируемой директории `data/`. "
        "Этот отчёт содержит только методику и сводные числа. Подготовка и публикация сайта описаны отдельно "
        "в [плане сайта](site-plan.md).", "",
    ])
    target = Path("docs/history-audit.md")
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated {target}: {count}/{queue['message_count']} messages reviewed")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("prepare")
    setup.add_argument("--max-chars", type=int, default=16000)
    display = commands.add_parser("show")
    display.add_argument("unit")
    complete = commands.add_parser("mark")
    complete.add_argument("unit")
    complete.add_argument("--note", type=Path, required=True)
    commands.add_parser("status")
    commands.add_parser("report")
    args = cli.parse_args()
    if args.command == "prepare":
        if args.max_chars < 1000:
            cli.error("Use a review unit size of at least 1000 characters.")
        prepare(args.max_chars)
    elif args.command == "show":
        show(args.unit)
    elif args.command == "mark":
        mark(args.unit, args.note)
    elif args.command == "report":
        report()
    else:
        status()


if __name__ == "__main__":
    main()
