"""
Map a fixed 300-slot beginner target list to dictionary entries.

This is intentionally dumber than `build_learning_core.py`: the Russian target
meanings are fixed first, then the dictionary is searched for matching entries.

Inputs:
  assets/data/dictionary.compact.json
  assets/data/dictionary.tags.json

Outputs:
  assets/data/learning_targets.json
  docs/data/2026-06-21-learning-targets-report.md
"""
from __future__ import annotations

import json
import re
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "data"
DICT = DATA / "dictionary.compact.json"
TAGS = DATA / "dictionary.tags.json"
TARGETS_OUT = DATA / "learning_targets.json"
REPORT_OUT = ROOT / "docs" / "data" / "2026-06-21-learning-targets-report.md"

RU_WORD_RE = re.compile(r"[а-яё]+", re.IGNORECASE)

TARGET_CATEGORIES: "OrderedDict[str, tuple[str, ...]]" = OrderedDict(
    [
        (
            "base",
            (
                "я",
                "ты",
                "он",
                "она",
                "мы",
                "вы",
                "они",
                "мой",
                "твой",
                "наш",
                "этот",
                "тот",
                "кто",
                "что",
                "где",
                "когда",
                "почему",
                "как",
                "да",
                "нет",
                "не",
                "и",
                "или",
                "но",
                "если",
            ),
        ),
        (
            "greetings_politeness",
            (
                "привет",
                "здравствуй",
                "спасибо",
                "пожалуйста",
                "извини",
                "прощай",
                "доброе утро",
                "добрый день",
                "добрый вечер",
                "как дела",
                "хорошо",
                "плохо",
                "давай",
                "можно",
                "нельзя",
                "нужно",
                "хочу",
                "не хочу",
                "знаю",
                "не знаю",
                "понимаю",
                "не понимаю",
                "вопрос",
                "ответ",
                "слово",
            ),
        ),
        (
            "family_people",
            (
                "человек",
                "мужчина",
                "женщина",
                "ребенок",
                "отец",
                "мать",
                "сын",
                "дочь",
                "брат",
                "сестра",
                "дед",
                "бабушка",
                "семья",
                "родственник",
                "друг",
                "подруга",
                "сосед",
                "гость",
                "учитель",
                "ученик",
                "врач",
                "старик",
                "парень",
                "девушка",
                "имя",
            ),
        ),
        (
            "body_health",
            (
                "голова",
                "лицо",
                "глаз",
                "ухо",
                "нос",
                "рот",
                "зуб",
                "язык",
                "рука",
                "нога",
                "палец",
                "спина",
                "живот",
                "сердце",
                "кровь",
                "тело",
                "волос",
                "боль",
                "болезнь",
                "здоровье",
                "сильный",
                "слабый",
                "усталый",
                "живой",
                "мертвый",
            ),
        ),
        (
            "actions",
            (
                "быть",
                "жить",
                "идти",
                "приходить",
                "уходить",
                "бежать",
                "сидеть",
                "стоять",
                "лежать",
                "спать",
                "есть",
                "пить",
                "смотреть",
                "видеть",
                "слышать",
                "говорить",
                "сказать",
                "спрашивать",
                "отвечать",
                "думать",
                "знать",
                "помнить",
                "забыть",
                "делать",
                "работать",
            ),
        ),
        (
            "food_drink",
            (
                "вода",
                "чай",
                "молоко",
                "хлеб",
                "мясо",
                "рыба",
                "суп",
                "рис",
                "картофель",
                "яйцо",
                "яблоко",
                "соль",
                "сахар",
                "масло",
                "сыр",
                "еда",
                "завтрак",
                "обед",
                "ужин",
                "голод",
                "напиток",
                "чашка",
                "тарелка",
                "ложка",
                "нож",
            ),
        ),
        (
            "home_daily",
            (
                "дом",
                "комната",
                "дверь",
                "окно",
                "стол",
                "стул",
                "кровать",
                "печь",
                "огонь",
                "свет",
                "одежда",
                "обувь",
                "шапка",
                "пояс",
                "сумка",
                "книга",
                "письмо",
                "деньги",
                "работа",
                "место",
                "дорога",
                "город",
                "село",
                "школа",
                "магазин",
            ),
        ),
        (
            "nature_weather",
            (
                "солнце",
                "луна",
                "небо",
                "земля",
                "ветер",
                "дождь",
                "снег",
                "лед",
                "жара",
                "холод",
                "тепло",
                "облако",
                "туман",
                "молния",
                "гром",
                "трава",
                "дерево",
                "цветок",
                "гора",
                "река",
                "море",
                "степь",
                "поле",
                "лес",
                "камень",
            ),
        ),
        (
            "animals",
            (
                "конь",
                "собака",
                "кошка",
                "корова",
                "бык",
                "овца",
                "баран",
                "коза",
                "верблюд",
                "сайгак",
                "волк",
                "лиса",
                "заяц",
                "мышь",
                "птица",
                "орел",
                "утка",
                "курица",
                "змея",
                "насекомое",
                "щенок",
                "теленок",
                "ягненок",
                "табун",
                "скот",
            ),
        ),
        (
            "time_numbers",
            (
                "сегодня",
                "завтра",
                "вчера",
                "сейчас",
                "потом",
                "рано",
                "поздно",
                "день",
                "ночь",
                "утро",
                "вечер",
                "время",
                "час",
                "минута",
                "неделя",
                "месяц",
                "год",
                "один",
                "два",
                "три",
                "четыре",
                "пять",
                "шесть",
                "семь",
                "десять",
            ),
        ),
        (
            "qualities",
            (
                "большой",
                "маленький",
                "хороший",
                "плохой",
                "новый",
                "старый",
                "красивый",
                "некрасивый",
                "быстрый",
                "медленный",
                "горячий",
                "холодный",
                "теплый",
                "белый",
                "черный",
                "красный",
                "синий",
                "зеленый",
                "желтый",
                "длинный",
                "короткий",
                "высокий",
                "низкий",
                "чистый",
                "грязный",
            ),
        ),
        (
            "culture_feelings_life",
            (
                "радость",
                "страх",
                "стыд",
                "любовь",
                "сила",
                "правда",
                "ложь",
                "мир",
                "война",
                "праздник",
                "песня",
                "история",
                "обычай",
                "закон",
                "вера",
                "благопожелание",
                "уважение",
                "память",
                "родина",
                "народ",
                "голос",
                "звук",
                "буква",
                "начало",
                "конец",
            ),
        ),
    ]
)

BLOCKED_AUTO_TAGS = {
    "archaic",
    "domain_term",
    "grammar_form",
    "source_ruwikt",
}

CONFUSING_MARKERS = (
    "см.",
    "то же",
    "вариант",
    "уменьш",
    "ласк",
    "бран",
    "перен.",
    "обл.",
    "диал.",
    "уст.",
    "редко",
    "род. п. от",
    "парн.",
    "совм.",
    "взаимн.",
    "прич. от",
    "деепр.",
)


def normalize_russian(value: str) -> str:
    normalized = value.lower().replace("ё", "е")
    normalized = re.sub(r"[^а-я0-9]+", " ", normalized)
    return " ".join(normalized.split())


def russian_tokens(value: str) -> list[str]:
    return RU_WORD_RE.findall(normalize_russian(value))


def flatten_targets(categories: "OrderedDict[str, tuple[str, ...]]") -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    number = 1
    for category, words in categories.items():
        for word in words:
            targets.append(
                {
                    "id": f"lt_{number:04d}",
                    "category": category,
                    "target_ru": word,
                }
            )
            number += 1
    return targets


def clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def first_translation(entry: dict[str, Any]) -> str:
    for sense in entry.get("senses") or []:
        text = clean_text(sense.get("def"))
        if text:
            return text
    return ""


def first_example(entry: dict[str, Any]) -> dict[str, str] | None:
    for sense in entry.get("senses") or []:
        for example in sense.get("examples") or []:
            kal = clean_text(example.get("kal"))
            rus = clean_text(example.get("rus"))
            if kal or rus:
                return {"kal": kal, "rus": rus}
    return None


def sense_example(sense: dict[str, Any]) -> dict[str, str] | None:
    for example in sense.get("examples") or []:
        kal = clean_text(example.get("kal"))
        rus = clean_text(example.get("rus"))
        if kal or rus:
            return {"kal": kal, "rus": rus}
    return None


def matching_sense(entry: dict[str, Any], target_ru: str) -> dict[str, Any] | None:
    target_norm = normalize_russian(target_ru)
    best: tuple[int, int, dict[str, Any]] | None = None
    for index, sense in enumerate(entry.get("senses") or []):
        definition = clean_text(sense.get("def"))
        if not definition_matches_target(definition, target_ru):
            continue
        definition_norm = normalize_russian(definition)
        priority = 0
        if definition_norm == target_norm:
            priority = 3
        elif definition_norm.startswith(f"{target_norm} "):
            priority = 2
        else:
            priority = 1
        candidate = (priority, -index, sense)
        if best is None or candidate > best:
            best = candidate
    return best[2] if best else None


def matched_translation(entry: dict[str, Any], target_ru: str) -> str:
    sense = matching_sense(entry, target_ru)
    if sense:
        return clean_text(sense.get("def"))
    return first_translation(entry)


def matched_example(entry: dict[str, Any], target_ru: str) -> dict[str, str] | None:
    sense = matching_sense(entry, target_ru)
    if sense:
        return sense_example(sense) or first_example(entry)
    return first_example(entry)


def load_tag_index(records: list[dict[str, Any]]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for record in records:
        source_id = record.get("source_id")
        if not source_id:
            continue
        index[str(source_id)] = {str(tag) for tag in record.get("tags") or []}
    return index


def token_sequence_contains(tokens: list[str], target_tokens: list[str]) -> bool:
    if not target_tokens or len(target_tokens) > len(tokens):
        return False
    width = len(target_tokens)
    return any(tokens[index : index + width] == target_tokens for index in range(len(tokens) - width + 1))


def definition_matches_target(definition: str, target_ru: str) -> bool:
    target_tokens = russian_tokens(target_ru)
    definition_tokens = russian_tokens(definition)
    if len(target_tokens) == 1:
        target = target_tokens[0]
        for index, token in enumerate(definition_tokens):
            if token != target:
                continue
            if index > 0 and definition_tokens[index - 1] == "не":
                continue
            return True
        return False
    return token_sequence_contains(definition_tokens, target_tokens)


def entry_definitions(entry: dict[str, Any]) -> list[str]:
    return [clean_text(sense.get("def")) for sense in entry.get("senses") or [] if clean_text(sense.get("def"))]


def has_confusing_definition(entry: dict[str, Any]) -> bool:
    blob = "\n".join(entry_definitions(entry)).lower()
    if any(marker in blob for marker in CONFUSING_MARKERS):
        return True
    first = first_translation(entry)
    if len(first) > 170:
        return True
    if first.lower().strip() in {"i", "ii", "iii", "1.", "2.", "3."}:
        return True
    return False


def score_match(entry: dict[str, Any], tags: set[str], target_ru: str) -> int | None:
    if tags.intersection(BLOCKED_AUTO_TAGS):
        return None

    score: int | None = None
    target_norm = normalize_russian(target_ru)
    for index, definition in enumerate(entry_definitions(entry)):
        if not definition_matches_target(definition, target_ru):
            continue
        definition_norm = normalize_russian(definition)
        current = 500
        if definition_norm == target_norm:
            current += 400
        elif definition_norm.startswith(f"{target_norm} "):
            current += 250
        elif index == 0:
            current += 100
        else:
            current += 50
        current -= min(len(definition_norm), 160) // 10
        score = current if score is None else max(score, current)

    if score is None:
        return None

    if "beginner_candidate" in tags:
        score += 50
    if "has_examples" in tags or first_example(entry):
        score += 25
    if "has_phonetic" in tags or entry.get("phonetic"):
        score += 15
    if "multiword_lemma" in tags:
        score -= 25
    if has_confusing_definition(entry):
        score -= 75
    return score


def prepare_search_index(
    entries: list[dict[str, Any]],
    tag_index: dict[str, set[str]],
) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        definitions = entry_definitions(entry)
        if not definitions:
            continue
        definition_tokens = [russian_tokens(definition) for definition in definitions]
        prepared = {
            "entry": entry,
            "tags": tag_index.get(str(entry.get("id") or ""), set()),
            "definitions": definitions,
            "definition_tokens": definition_tokens,
            "definition_norms": [normalize_russian(definition) for definition in definitions],
        }
        unique_tokens = {token for tokens in definition_tokens for token in tokens}
        for token in unique_tokens:
            index[token].append(prepared)
    return dict(index)


def score_prepared_match(prepared: dict[str, Any], target_ru: str) -> int | None:
    tags = prepared["tags"]
    if tags.intersection(BLOCKED_AUTO_TAGS):
        return None

    score: int | None = None
    target_norm = normalize_russian(target_ru)
    for index, definition in enumerate(prepared["definitions"]):
        if not definition_matches_target(definition, target_ru):
            continue
        definition_norm = prepared["definition_norms"][index]
        current = 500
        if definition_norm == target_norm:
            current += 400
        elif definition_norm.startswith(f"{target_norm} "):
            current += 250
        elif index == 0:
            current += 100
        else:
            current += 50
        current -= min(len(definition_norm), 160) // 10
        score = current if score is None else max(score, current)

    if score is None:
        return None

    entry = prepared["entry"]
    if "beginner_candidate" in tags:
        score += 50
    if "has_examples" in tags or first_example(entry):
        score += 25
    if "has_phonetic" in tags or entry.get("phonetic"):
        score += 15
    if "multiword_lemma" in tags:
        score -= 25
    if has_confusing_definition(entry):
        score -= 75
    return score


def match_candidates_from_index(
    search_index: dict[str, list[dict[str, Any]]],
    target_ru: str,
) -> list[tuple[int, dict[str, Any], set[str]]]:
    target_tokens = russian_tokens(target_ru)
    if not target_tokens:
        return []
    pool = search_index.get(target_tokens[0], [])
    candidates: list[tuple[int, dict[str, Any], set[str]]] = []
    seen: set[str] = set()
    for prepared in pool:
        entry = prepared["entry"]
        source_id = str(entry.get("id") or "")
        if source_id in seen:
            continue
        seen.add(source_id)
        score = score_prepared_match(prepared, target_ru)
        if score is not None and score > 0:
            candidates.append((score, entry, prepared["tags"]))
    candidates.sort(key=lambda item: (-item[0], clean_text(item[1].get("lemma")), str(item[1].get("id"))))
    return candidates


def match_candidates(
    entries: list[dict[str, Any]],
    tag_index: dict[str, set[str]],
    target_ru: str,
) -> list[tuple[int, dict[str, Any], set[str]]]:
    return match_candidates_from_index(prepare_search_index(entries, tag_index), target_ru)


def candidate_summary(score: int, entry: dict[str, Any], target_ru: str) -> dict[str, Any]:
    return {
        "source_id": entry.get("id"),
        "lemma": clean_text(entry.get("lemma")),
        "translation": matched_translation(entry, target_ru),
        "score": score,
    }


def build_target_row(
    target: dict[str, str],
    candidates: list[tuple[int, dict[str, Any], set[str]]],
) -> dict[str, Any]:
    base = {
        "id": target["id"],
        "category": target["category"],
        "target_ru": target["target_ru"],
        "review_status": "candidate",
        "lesson_eligible": False,
        "audio_status": "needed",
        "audio_file": None,
    }

    if not candidates:
        return {
            **base,
            "match_status": "needs_manual_match",
            "source_id": None,
            "lemma": None,
            "translation": None,
            "example": None,
            "source_tags": [],
            "match_score": 0,
            "alternatives": [],
            "notes": ["no_dictionary_match"],
        }

    score, entry, tags = candidates[0]
    alternatives = [
        candidate_summary(alt_score, alt_entry, target["target_ru"])
        for alt_score, alt_entry, _tags in candidates[1:4]
    ]
    notes: list[str] = []
    if not matched_example(entry, target["target_ru"]):
        notes.append("needs_example")
    if "has_phonetic" not in tags and not entry.get("phonetic"):
        notes.append("needs_pronunciation_review")
    if "cultural_candidate" in tags:
        notes.append("has_cultural_markers")
    if score < 600:
        notes.append("low_confidence_match")

    return {
        **base,
        "match_status": "matched",
        "source_id": entry.get("id"),
        "lemma": clean_text(entry.get("lemma")),
        "translation": matched_translation(entry, target["target_ru"]),
        "example": matched_example(entry, target["target_ru"]),
        "source_tags": sorted(tags),
        "match_score": score,
        "alternatives": alternatives,
        "notes": notes,
    }


def build_learning_targets(
    entries: list[dict[str, Any]],
    tag_index: dict[str, set[str]],
    targets: list[dict[str, str]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected_targets = targets or flatten_targets(TARGET_CATEGORIES)
    search_index = prepare_search_index(entries, tag_index)
    rows = [
        build_target_row(target, match_candidates_from_index(search_index, target["target_ru"]))
        for target in selected_targets
    ]

    by_category: dict[str, dict[str, int]] = {}
    for category in TARGET_CATEGORIES:
        category_rows = [row for row in rows if row["category"] == category]
        by_category[category] = {
            "targets": len(category_rows),
            "matched": sum(1 for row in category_rows if row["match_status"] == "matched"),
            "needs_manual_match": sum(
                1 for row in category_rows if row["match_status"] == "needs_manual_match"
            ),
        }

    status_counts = Counter(row["match_status"] for row in rows)
    stats = {
        "targets": len(rows),
        "matched": status_counts.get("matched", 0),
        "needs_manual_match": status_counts.get("needs_manual_match", 0),
        "by_category": by_category,
    }
    return rows, stats


def render_report(rows: list[dict[str, Any]], stats: dict[str, Any]) -> str:
    lines = [
        "# Learning Targets Match Report",
        "",
        "Generated by `scripts/build_learning_targets.py`.",
        "",
        "## Summary",
        "",
        f"- target slots: `{stats['targets']}`",
        f"- matched automatically: `{stats['matched']}`",
        f"- needs manual match: `{stats['needs_manual_match']}`",
        "- review status: all rows are `candidate` until human review",
        "",
        "## By Category",
        "",
    ]
    for category, category_stats in stats["by_category"].items():
        lines.append(
            f"- `{category}`: `{category_stats['matched']}` matched / "
            f"`{category_stats['needs_manual_match']}` manual / `{category_stats['targets']}` total"
        )

    lines.extend(["", "## Manual Match Needed", ""])
    missing = [row for row in rows if row["match_status"] == "needs_manual_match"]
    if not missing:
        lines.append("- none")
    else:
        for row in missing:
            lines.append(f"- `{row['id']}` `{row['category']}`: {row['target_ru']}")

    lines.extend(["", "## First 40 Matches", ""])
    for row in [item for item in rows if item["match_status"] == "matched"][:40]:
        lines.append(
            f"- `{row['id']}` `{row['category']}`: {row['target_ru']} -> "
            f"{row['lemma']} ({row['translation']})"
        )
    lines.append("")
    return "\n".join(lines)


def write_outputs(root: Path, rows: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    targets_out = root / "assets" / "data" / "learning_targets.json"
    report_out = root / "docs" / "data" / "2026-06-21-learning-targets-report.md"
    targets_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    targets_out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    report_out.write_text(render_report(rows, stats), encoding="utf-8")


def main() -> int:
    entries = json.loads(DICT.read_text(encoding="utf-8"))
    tag_records = json.loads(TAGS.read_text(encoding="utf-8"))
    rows, stats = build_learning_targets(entries, load_tag_index(tag_records))
    write_outputs(ROOT, rows, stats)
    print(f"wrote {TARGETS_OUT} ({len(rows)} targets)")
    print(f"wrote {REPORT_OUT}")
    print(f"matched: {stats['matched']}")
    print(f"needs_manual_match: {stats['needs_manual_match']}")
    for category, category_stats in stats["by_category"].items():
        print(f"{category}: {category_stats['matched']}/{category_stats['targets']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
