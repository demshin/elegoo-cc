#!/usr/bin/env python3
"""Find topic and outcome candidates; keep all derived chat data under data/.work/."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re


TOPICS = {
    "drying": ("Влага, сушка и хранение", r"суш|влаг|мокр|пузыр"),
    "flow_speed": ("Поток, скорость и недоэкструзия", r"об[ъь]?[её]мн|поток|недоэкстру|рассло|макс.{0,12}расход"),
    "retraction": ("Ретракт и паутина", r"ретракт|откат.{0,35}(мм|mm|филам|пластик|нит|скорост)|(?:мм|mm).{0,35}откат|волос|сопли|паутин|\bstringing\b"),
    "pressure_advance": ("Pressure Advance и углы", r"pressure|пр[еэ]ш|\bп[аэ]\b|\bpa\b|наплыв"),
    "supports": ("Поддержки, мосты и нависания", r"поддерж|support|нависан|мост"),
    "warping": ("Усадка, отрыв и кайма", r"усадк|отрыв|отрыва|откле|загиб|кайм|\bbrim\b"),
    "filament_path": ("Подача, катушки и трубки", r"перехл[её]ст|катушк|трубк|подач|переж[её]в|заж[её]в"),
    "clogs": ("Засоры и тепловые пробки", r"пробк|засор|забив|забит|heat.?creep"),
    "canvas": ("CANVAS и многоцветная печать", r"канвас|canvas|1243|1242|\brfid\b|многоцвет"),
    "error_codes": ("Коды ошибок", r"\b803\b|\b702\b|\b701\b|\b502\b|\b103\b|\b104\b|\b124\d\b"),
    "bed_level": ("Стол, карта высот и Z-offset", r"карт[ауые].{0,12}(стол|высот)|z.?offs?et|о[ф]?ф?сет|выравнив|крив.{0,12}стол"),
    "adhesion": ("Пластина и адгезия", r"пластин|адгези|не лип|не прилип|перв.{0,10}сло"),
    "hotend": ("Хотэнд и температура", r"термопаст|термист|термопар|нагревател|недогрев|хот[эе]нд"),
    "noise": ("Шум и механика", r"дребез|резонанс|трещит|треск|гудит|подшипник|вибрац"),
    "layer_shift": ("Сдвиги слоёв", r"сдвиг|сместил|смещен|смещён|потер[яй].{0,10}шаг"),
    "network": ("Сеть, камера и веб-интерфейс", r"wi.?fi|вай.?фай|камер|веб|вэб|сет[ьи]|подключен"),
    "firmware": ("Прошивки", r"прошив|cosmos|космос|opencentauri|опен|open.?centauri"),
    "slicer_profiles": ("Слайсеры и профили", r"профил|слайсер|orca|орка|elegoo.?slicer"),
    "usb_files": ("USB и файлы", r"фл[еэ]ш|fat32|файл.{0,20}не вид|не вид.{0,20}файл"),
    "seams": ("Швы", r"\bшов\b|\bшва\b|seam|scarf"),
    "model_export": ("Модели и экспорт", r"\bstl\b|\bstep\b|\b3mf\b|многоугол|фасет|триангул|модел.{0,15}ошиб"),
    "pla": ("PLA", r"\bpla\b|\bпла\b"),
    "petg": ("PETG", r"\bpetg\b|п[еэ]т[гжд]|пед[гж]"),
    "abs_asa": ("ABS и ASA", r"\babs\b|\basa\b|\bабс\b|\bаса\b"),
    "tpu": ("TPU и другие эластомеры", r"\btpu\b|\bтпу\b|флекс|экзофлекс"),
    "nylon": ("Нейлон и композиты", r"нейлон|полиамид|\bpa[ -]?[612]|\bpa\d|[ -]cf\b|углеволок"),
    "nozzles": ("Сопла и их совместимость", r"сопл|nozzle"),
    "dimensions": ("Размеры, отверстия и посадки", r"допуск|размер|посадк|резьб|отверст|геометр"),
    "infill": ("Заполнение", r"заполнен|гироид|gyroid|infill"),
    "cooling": ("Охлаждение", r"обдув|вентилят|кулер|охлажден"),
    "multicolor": ("Смена цвета и очистка", r"смешиван.{0,10}цвет|продув|башн.{0,15}очист|очист.{0,15}башн|смен.{0,15}цвет"),
    "storage": ("Хранение катушек", r"силик[ао]гел|вакуум|хранен|гермобокс"),
    "maintenance": ("Обслуживание механики", r"смаз|направляющ|ремн[яией]|натяжен"),
    "environment": ("Условия печати и вытяжка", r"вытяж|запах|вентиляц|сквозняк|температур.{0,15}камер"),
}

OUTCOME = re.compile(
    r"помог(?:ло|ла|ли)\b|заработал|разобрал(?:ся|ась)|получилось|исправил|устранил|"
    r"избавил|победил|пропал|вылечил|вс[её].{0,15}(отлич|норм|ок\b)|"
    r"после.{0,70}(печатает|работает)|пузыри пропали",
    re.I,
)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--index", type=Path, default=Path("data/.work/messages.jsonl"))
    cli.add_argument("--output", type=Path, default=Path("data/.work/topics"))
    args = cli.parse_args()
    private = Path("data/.work").resolve()
    if not args.index.resolve().is_relative_to(private) or not args.output.resolve().is_relative_to(private):
        cli.error("Index and output must stay inside data/.work/")
    messages = [json.loads(line) for line in args.index.open(encoding="utf-8")]
    by_id = {m["id"]: m for m in messages}
    patterns = {key: re.compile(pattern, re.I) for key, (_, pattern) in TOPICS.items()}
    hits = {key: [] for key in TOPICS}
    candidates = {key: [] for key in TOPICS}
    pages = Counter()
    unclassified = []
    outcomes = []
    for message in messages:
        pages[message["file"]] += 1
        matched = [key for key, pattern in patterns.items() if pattern.search(message["text"])]
        for key in matched:
            hits[key].append(message["id"])
        if not matched:
            unclassified.append(message["id"])
        if not OUTCOME.search(message["text"]):
            continue
        # A lexical outcome signal is a candidate, never proof of resolution.
        outcomes.append(message["id"])
        chain = [message]
        seen = {message["id"]}
        current = message
        for _ in range(5):
            current = by_id.get(current["reply"])
            if current is None or current["id"] in seen:
                break
            chain.append(current)
            seen.add(current["id"])
        context = "\n".join(m["text"] for m in chain)
        for key, pattern in patterns.items():
            if pattern.search(context):
                candidates[key].append({"id": message["id"], "chain": [m["id"] for m in chain]})
    args.output.mkdir(parents=True, exist_ok=True)
    summary = {
        "messages": len(messages),
        "pages": dict(pages),
        "unclassified_ids": unclassified,
        "outcome_signal_ids": outcomes,
        "topics": {},
    }
    for key, (label, _) in TOPICS.items():
        summary["topics"][key] = {"label": label, "hit_ids": hits[key], "candidates": candidates[key]}
        with (args.output / f"{key}.md").open("w", encoding="utf-8") as handle:
            handle.write(f"# {label}\n\nPrivate machine candidates, not verified cases.\n")
            for candidate in candidates[key]:
                handle.write(f"\n## Candidate {candidate['id']}\n")
                for mid in candidate["chain"]:
                    m = by_id[mid]
                    handle.write(f"\n### {mid} | {m['file']} | {m['date']} | {m['author']} | reply={m['reply']}\n\n{m['text']}\n")
        print(f"{key}: {len(hits[key])} matching messages, {len(candidates[key])} outcome candidates")
    (args.output / "catalog.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scanned {len(messages)} messages in {len(pages)} pages; {len(unclassified)} have no topic keyword")


if __name__ == "__main__":
    main()
