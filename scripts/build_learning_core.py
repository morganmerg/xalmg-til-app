"""
Build a human-reviewable beginner learning core from generated dictionary tags.

Inputs:
  assets/data/dictionary.compact.json
  assets/data/dictionary.tags.json

Outputs:
  assets/data/learning_core.json
  docs/data/2026-06-21-learning-core-report.md
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "data"
DICT = DATA / "dictionary.compact.json"
TAGS = DATA / "dictionary.tags.json"
CORE_OUT = DATA / "learning_core.json"
REPORT_OUT = ROOT / "docs" / "data" / "2026-06-21-learning-core-report.md"

TARGET_MAX = 300

CATEGORY_ORDER = (
    "greetings_politeness",
    "family_people",
    "home_daily",
    "food_drink",
    "steppe_nature",
    "animals",
    "numbers_time",
    "body_health",
    "common_actions",
    "qualities",
    "objects_places",
)

BLOCKING_TAGS = {
    "archaic",
    "domain_term",
    "function_word",
    "grammar_form",
    "multiword_lemma",
    "source_ruwikt",
}

WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


def mojibake_form(value: str) -> str:
    """Return the common UTF-8-as-cp1251 mojibake form used by old exports."""
    return value.encode("utf-8").decode("cp1251", errors="ignore")


def keyword_forms(*keywords: str) -> tuple[str, ...]:
    forms: set[str] = set()
    for keyword in keywords:
        normalized = keyword.lower()
        forms.add(normalized)
        forms.add(mojibake_form(normalized).lower())
    return tuple(sorted(forms))


CATEGORY_EXACT: dict[str, tuple[str, ...]] = {
    "greetings_politeness": keyword_forms(
        "привет",
        "спасибо",
        "здравствуйте",
        "здравствуй",
        "прощай",
        "извините",
        "благодарность",
    ),
    "family_people": keyword_forms(
        "отец",
        "папа",
        "мать",
        "мама",
        "сын",
        "дочь",
        "брат",
        "сестра",
        "семья",
        "родня",
        "человек",
        "люди",
        "мужчина",
        "женщина",
        "ребен",
        "ребён",
        "мальчик",
        "девочка",
        "старик",
        "старуха",
    ),
    "home_daily": keyword_forms(
        "дом",
        "жить",
        "спать",
        "идти",
        "ходить",
        "работа",
        "играть",
        "учить",
        "сидеть",
        "стоять",
        "юрта",
    ),
    "food_drink": keyword_forms(
        "чай",
        "молоко",
        "вода",
        "хлеб",
        "мясо",
        "сахар",
        "соль",
        "суп",
        "еда",
        "пить",
        "масло",
        "сыр",
        "рыба",
        "яблоко",
        "чайник",
    ),
    "steppe_nature": keyword_forms(
        "солнце",
        "луна",
        "ветер",
        "степь",
        "земля",
        "огонь",
        "небо",
        "трава",
        "дерево",
        "гора",
        "река",
        "дождь",
        "снег",
        "природа",
    ),
    "animals": keyword_forms(
        "конь",
        "лошадь",
        "верблюд",
        "сайг",
        "корова",
        "бык",
        "овца",
        "баран",
        "собака",
        "волк",
        "птица",
        "заяц",
        "животное",
    ),
    "numbers_time": keyword_forms(
        "один",
        "два",
        "три",
        "четыр",
        "пять",
        "шесть",
        "семь",
        "восем",
        "девять",
        "десять",
        "день",
        "ночь",
        "утро",
        "вечер",
        "сегодня",
        "завтра",
        "время",
        "год",
        "месяц",
        "неделя",
    ),
    "body_health": keyword_forms(
        "голова",
        "рука",
        "нога",
        "глаз",
        "ухо",
        "сердце",
        "кровь",
        "болезнь",
        "болеть",
        "зуб",
        "лицо",
        "нос",
        "тело",
    ),
    "common_actions": keyword_forms(
        "делать",
        "идти",
        "дать",
        "брать",
        "видеть",
        "смотреть",
        "сказать",
        "говорить",
        "есть",
        "пить",
        "спать",
        "жить",
        "любить",
        "знать",
    ),
    "qualities": keyword_forms(
        "хорош",
        "плох",
        "больш",
        "малый",
        "маленький",
        "красн",
        "син",
        "белый",
        "черный",
        "чёрный",
        "новый",
        "старый",
        "быстрый",
        "медленный",
        "тяжелый",
        "тяжёлый",
        "легкий",
        "лёгкий",
    ),
    "objects_places": keyword_forms(
        "книга",
        "письмо",
        "дорога",
        "город",
        "село",
        "школа",
        "стол",
        "нож",
        "одежда",
        "место",
        "комната",
        "двор",
    ),
}

CATEGORY_STEMS: dict[str, tuple[str, ...]] = {
    "greetings_politeness": keyword_forms(
        "приветств",
        "поздрав",
        "прощен",
        "прощён",
        "извин",
        "благопожел",
    ),
    "family_people": keyword_forms(
        "родствен",
        "сестр",
        "девоч",
        "сынов",
        "дочер",
        "усынов",
    ),
    "home_daily": keyword_forms(
        "домаш",
        "приход",
        "учеб",
    ),
    "food_drink": keyword_forms(
        "питьев",
        "молоч",
        "хлебн",
    ),
    "steppe_nature": keyword_forms(
        "степн",
        "солнеч",
        "лунн",
        "ветрен",
        "земн",
        "огнен",
        "небес",
        "травн",
        "травя",
        "дожд",
        "снеж",
        "природ",
    ),
    "animals": keyword_forms(
        "лошад",
        "верблю",
        "сайг",
        "собач",
        "птич",
        "животн",
    ),
    "numbers_time": keyword_forms(
        "вечерн",
        "утрен",
        "дневн",
        "ночн",
        "сегодняш",
        "завтраш",
        "недель",
        "месяч",
    ),
    "body_health": keyword_forms(
        "сердеч",
        "кровян",
        "болезн",
        "зубн",
        "телес",
    ),
    "common_actions": keyword_forms(
    ),
    "qualities": keyword_forms(
        "хорош",
        "плох",
        "больш",
        "красн",
        "красноват",
        "синеват",
        "беловат",
        "черноват",
        "быстр",
        "медлен",
        "тяжел",
        "тяжёл",
        "легк",
    ),
    "objects_places": keyword_forms(
        "городск",
        "сельск",
        "школьн",
        "одежд",
        "дорож",
    ),
}

CONFUSING_MARKERS = keyword_forms(
    "см.",
    "см ",
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
    "мн. ч.",
    "род. п. от",
    "звукоподр",
    "парн.",
    "нареч.",
    "совм.",
    "взаимн.",
    "прич. от",
    "деепр.",
    "вводн.",
    "частица",
    "высок.",
    "вет.",
    "геол.",
    "юр.",
    "спец.",
)


def clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def definition_blob(entry: dict[str, Any]) -> str:
    chunks = [
        clean_text(entry.get("lemma")),
        clean_text(entry.get("phonetic")),
        clean_text(entry.get("pos")),
    ]
    for alias in entry.get("aliases") or []:
        chunks.append(clean_text(alias))
    for sense in entry.get("senses") or []:
        chunks.append(clean_text(sense.get("def")))
    return "\n".join(chunk for chunk in chunks if chunk).lower()


def category_blob(entry: dict[str, Any]) -> str:
    chunks = [
        clean_text(entry.get("lemma")),
        clean_text(entry.get("phonetic")),
        first_translation(entry),
    ]
    return "\n".join(chunk for chunk in chunks if chunk).lower()


def tokens_for_text(text: str) -> set[str]:
    return set(WORD_RE.findall(text))


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


def load_tag_index(records: list[dict[str, Any]]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for record in records:
        source_id = record.get("source_id")
        if not source_id:
            continue
        index[str(source_id)] = {str(tag) for tag in record.get("tags") or []}
    return index


def category_for_entry(entry: dict[str, Any]) -> str | None:
    blob = category_blob(entry)
    tokens = tokens_for_text(blob)
    for category in CATEGORY_ORDER:
        if tokens.intersection(CATEGORY_EXACT[category]):
            return category
        if any(keyword in blob for keyword in CATEGORY_STEMS[category]):
            return category
    return None


def has_confusing_shape(entry: dict[str, Any]) -> bool:
    translation = first_translation(entry)
    translation_lc = translation.lower().strip()
    blob = definition_blob(entry)
    if any(marker in blob for marker in CONFUSING_MARKERS):
        return True
    if translation_lc in {"i", "ii", "iii", "iv", "v", "1.", "2.", "3."}:
        return True
    if translation_lc.startswith(("i;", "ii;", "iii;", "iv;", "v;", "1.;", "2.;", "3.;")):
        return True
    if "||" in translation:
        return True
    if len(translation) > 180:
        return True
    if len(translation.split()) > 16:
        return True
    return False


def is_learning_candidate(entry: dict[str, Any], tags: set[str]) -> bool:
    if "beginner_candidate" not in tags:
        return False
    if tags.intersection(BLOCKING_TAGS):
        return False
    if not first_translation(entry):
        return False
    if has_confusing_shape(entry):
        return False
    return category_for_entry(entry) is not None


def candidate_score(entry: dict[str, Any], tags: set[str]) -> int:
    score = 100
    translation = first_translation(entry)
    example = first_example(entry)
    if "has_examples" in tags or example:
        score += 35
    if "has_phonetic" in tags or entry.get("phonetic"):
        score += 20
    if "has_aliases" in tags or entry.get("aliases"):
        score += 5
    if "cultural_candidate" in tags:
        score -= 30
    score -= len(translation) // 12
    score -= len(clean_text(entry.get("lemma"))) // 8
    return score


def build_core_item(
    number: int,
    entry: dict[str, Any],
    tags: set[str],
    category: str,
) -> dict[str, Any]:
    notes: list[str] = []
    if "cultural_candidate" in tags:
        notes.append("has_cultural_markers")
    if "has_examples" not in tags and first_example(entry) is None:
        notes.append("needs_example")
    if "has_phonetic" not in tags and not entry.get("phonetic"):
        notes.append("needs_pronunciation_review")

    return {
        "id": f"lc_{number:04d}",
        "source_id": entry.get("id"),
        "lemma": clean_text(entry.get("lemma")),
        "translation": first_translation(entry),
        "category": category,
        "difficulty": 1,
        "review_status": "candidate",
        "lesson_eligible": False,
        "audio_status": "needed",
        "audio_file": None,
        "example": first_example(entry),
        "notes": notes,
        "source_tags": sorted(tags),
    }


def build_learning_core(
    entries: list[dict[str, Any]],
    tag_index: dict[str, set[str]],
    target_max: int = TARGET_MAX,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[str, list[tuple[int, str, dict[str, Any], set[str]]]] = {
        category: [] for category in CATEGORY_ORDER
    }
    skipped: Counter[str] = Counter()

    for entry in entries:
        source_id = str(entry.get("id") or "")
        tags = tag_index.get(source_id, set())

        if "beginner_candidate" not in tags:
            skipped["not_beginner_candidate"] += 1
            continue
        if tags.intersection(BLOCKING_TAGS):
            skipped["blocked_tags"] += 1
            continue
        if not first_translation(entry):
            skipped["missing_translation"] += 1
            continue
        if has_confusing_shape(entry):
            skipped["confusing_shape"] += 1
            continue

        category = category_for_entry(entry)
        if category is None:
            skipped["no_beginner_theme"] += 1
            continue

        grouped[category].append((candidate_score(entry, tags), source_id, entry, tags))

    for candidates in grouped.values():
        candidates.sort(key=lambda item: (-item[0], clean_text(item[2].get("lemma")), item[1]))

    selected: list[tuple[int, str, dict[str, Any], set[str], str]] = []
    selected_ids: set[str] = set()
    per_category = max(1, target_max // len(CATEGORY_ORDER))

    for category in CATEGORY_ORDER:
        for score, source_id, entry, tags in grouped[category][:per_category]:
            if len(selected) >= target_max:
                break
            selected.append((score, source_id, entry, tags, category))
            selected_ids.add(source_id)

    if len(selected) < target_max:
        remaining_by_category: dict[str, list[tuple[int, str, dict[str, Any], set[str], str]]] = {
            category: [] for category in CATEGORY_ORDER
        }
        for category in CATEGORY_ORDER:
            for score, source_id, entry, tags in grouped[category]:
                if source_id not in selected_ids:
                    remaining_by_category[category].append((score, source_id, entry, tags, category))

        while len(selected) < target_max:
            progressed = False
            for category in CATEGORY_ORDER:
                if len(selected) >= target_max:
                    break
                if not remaining_by_category[category]:
                    continue
                candidate = remaining_by_category[category].pop(0)
                selected.append(candidate)
                selected_ids.add(candidate[1])
                progressed = True
            if not progressed:
                break

    selected.sort(
        key=lambda item: (
            CATEGORY_ORDER.index(item[4]),
            -item[0],
            clean_text(item[2].get("lemma")),
            item[1],
        )
    )

    core = [
        build_core_item(index, entry, tags, category)
        for index, (_score, _source_id, entry, tags, category) in enumerate(selected, start=1)
    ]
    by_category = Counter(item["category"] for item in core)
    eligible_by_category = {category: len(grouped[category]) for category in CATEGORY_ORDER}

    stats = {
        "target_max": target_max,
        "selected": len(core),
        "eligible": sum(eligible_by_category.values()),
        "by_category": dict(by_category),
        "eligible_by_category": eligible_by_category,
        "skipped": dict(skipped),
    }
    return core, stats


def render_report(core: list[dict[str, Any]], stats: dict[str, Any]) -> str:
    lines = [
        "# Learning Core Candidate Report",
        "",
        "Generated by `scripts/build_learning_core.py`.",
        "",
        "## Summary",
        "",
        f"- target max: `{stats['target_max']}`",
        f"- selected candidates: `{stats['selected']}`",
        f"- eligible themed candidates before cap: `{stats['eligible']}`",
        "- review status: all exported items are `candidate`, not final approved lesson content",
        "- lesson eligibility: exported as `false` until human review",
        "",
        "## Selected By Category",
        "",
    ]
    for category in CATEGORY_ORDER:
        lines.append(f"- `{category}`: `{stats['by_category'].get(category, 0)}`")

    lines.extend(["", "## Eligible Pool By Category", ""])
    for category in CATEGORY_ORDER:
        lines.append(f"- `{category}`: `{stats['eligible_by_category'].get(category, 0)}`")

    lines.extend(["", "## Skipped", ""])
    for reason, count in sorted(stats["skipped"].items()):
        lines.append(f"- `{reason}`: `{count}`")

    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- Selection is deterministic and heuristic.",
            "- Inputs are `beginner_candidate` entries from the generated tag layer.",
            "- Blocking tags remove grammar forms, Wiktionary-only imports, multiword lemmas, function words, archaic entries, and domain terms.",
            "- Cultural candidates are allowed, but marked with `has_cultural_markers` for human review.",
            "- Items without examples or phonetics are kept when otherwise useful, but marked in `notes`.",
            "",
            "## First 30 Candidates",
            "",
        ]
    )
    for item in core[:30]:
        lines.append(
            f"- `{item['id']}` `{item['category']}`: {item['lemma']} — {item['translation']}"
        )
    lines.append("")
    return "\n".join(lines)


def write_outputs(root: Path, core: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    core_out = root / "assets" / "data" / "learning_core.json"
    report_out = root / "docs" / "data" / "2026-06-21-learning-core-report.md"
    core_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    core_out.write_text(json.dumps(core, ensure_ascii=False, indent=2), encoding="utf-8")
    report_out.write_text(render_report(core, stats), encoding="utf-8")


def main() -> int:
    entries = json.loads(DICT.read_text(encoding="utf-8"))
    tag_records = json.loads(TAGS.read_text(encoding="utf-8"))
    core, stats = build_learning_core(entries, load_tag_index(tag_records), target_max=TARGET_MAX)
    write_outputs(ROOT, core, stats)
    print(f"wrote {CORE_OUT} ({len(core)} candidates)")
    print(f"wrote {REPORT_OUT}")
    for category in CATEGORY_ORDER:
        print(f"{category}: {stats['by_category'].get(category, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
