"""
Merge Russian Wiktionary Kalmyk entries (via kaikki.org) into dictionary.compact.json.

Source: 1944 xal entries extracted from ru.wiktionary.
Format per line: {word, pos, senses: [{glosses, examples?}], ...}

Strategy:
- Normalize lemma (NFC, lowercase) for matching.
- If lemma exists in Муниев: append new Russian glosses as extra senses (tagged source).
- If lemma is new: create fresh entry.
- Dedup senses by normalized def string to avoid churn on re-run.

License: ru.wiktionary = CC BY-SA 4.0 + GFDL. Attribution in app About.
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT = ROOT / "assets" / "data" / "dictionary.compact.json"
KAIKKI = ROOT / "scripts" / "_merge_src" / "kaikki-ruwikt-Kalmyk.jsonl"
OUT = DICT  # overwrite in place (git is the backup)


def norm(s: str) -> str:
    return unicodedata.normalize("NFC", s.strip().lower())


def load_kaikki(path: Path) -> list[dict]:
    entries: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return entries


def flatten_senses(e: dict) -> list[str]:
    """Extract Russian gloss strings from a kaikki entry."""
    out: list[str] = []
    for s in e.get("senses", []) or []:
        for g in s.get("glosses", []) or []:
            g = g.strip()
            if g and len(g) < 400:
                out.append(g)
    return out


SUFFIX_POS = {"suffix", "prefix", "affix"}
# Kalmyk-specific stripper: drop leading pometa markers ("парн.;", "зоол.", "хим.", "I"+space)
import re as _re
_POMETA = _re.compile(r"^(?:[IVX]+\.?\s*|[а-яё]+\.\s*)+", _re.IGNORECASE)
_PAREN = _re.compile(r"\([^()]*\)")
_DISJ = _re.compile(r"\|\|")


def core_terms(text: str) -> set[str]:
    """Normalize a definition and split into core term set for fuzzy dedup."""
    t = _POMETA.sub("", text)
    t = _PAREN.sub("", t)
    t = _DISJ.sub(",", t)
    parts = [p.strip(" .;:—-") for p in _re.split(r"[,;]", t)]
    return {norm(p) for p in parts if p}


def main() -> int:
    existing: list[dict] = json.loads(DICT.read_text(encoding="utf-8"))
    kaikki = load_kaikki(KAIKKI)

    # Index existing by normalized lemma
    by_lemma: dict[str, dict] = {}
    for entry in existing:
        by_lemma[norm(entry["lemma"])] = entry

    new_lemmas = 0
    added_senses = 0
    next_id = max(int(e["id"].split("_")[0]) for e in existing) + 1

    for e in kaikki:
        lemma = (e.get("word") or "").strip()
        if not lemma:
            continue
        glosses = flatten_senses(e)
        if not glosses:
            continue
        pos = e.get("pos")

        key = norm(lemma)
        target = by_lemma.get(key)
        if target is None:
            # new entry
            target = {
                "id": f"{next_id:06d}_{lemma[:2]}",
                "lemma": lemma,
                "phonetic": None,
                "pos": pos,
                "senses": [],
                "aliases": [],
                "source": "ruwikt",
            }
            next_id += 1
            by_lemma[key] = target
            existing.append(target)
            new_lemmas += 1

        existing_defs = {norm(s["def"]) for s in target["senses"] if s.get("def")}
        next_num = max((s.get("num") or 0) for s in target["senses"]) + 1 if target["senses"] else 1
        for g in glosses:
            if norm(g) in existing_defs:
                continue
            target["senses"].append(
                {
                    "num": next_num,
                    "def": g,
                    "examples": [],
                    "source": "ruwikt",
                }
            )
            existing_defs.add(norm(g))
            next_num += 1
            added_senses += 1

    OUT.write_text(
        json.dumps(existing, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"total entries after merge: {len(existing)}")
    print(f"new lemmas added: {new_lemmas}")
    print(f"new senses added to existing lemmas: {added_senses}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
