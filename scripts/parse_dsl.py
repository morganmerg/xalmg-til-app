"""
Parse ABBYY Lingvo DSL (Kalmyk-Russian) into structured JSON.

Input:  /tmp/xal-rus.utf8.dsl (already converted from UTF-16 to UTF-8)
Output: data/dictionary.json  — list of entries
        data/categories.json  — simple thematic buckets

Entry schema:
{
  "id": "abbreviated stable id",
  "lemma": "калмыцкое слово",
  "phonetic": "транскрипция" | null,
  "pos": "часть речи" | null,
  "senses": [
    {
      "num": 1,
      "def": "русский перевод / толкование",
      "examples": [{"kal": "...", "rus": "..."}, ...]
    }
  ],
  "aliases": ["=forms pointing to this lemma"]
}
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DSL = Path(os.environ.get("XALMG_DSL_PATH", PROJECT_ROOT / "data" / "xal-rus.utf8.dsl"))
OUT_DICT = PROJECT_ROOT / "assets" / "data" / "dictionary.json"
OUT_COMPACT = PROJECT_ROOT / "assets" / "data" / "dictionary.compact.json"


TAG = re.compile(r"\[/?[^\]]+\]")
EX_BLOCK = re.compile(r"\[ex\](.*?)\[/ex\]", re.DOTALL)
C_BLOCK = re.compile(r"\[c\](.*?)\[/c\]", re.DOTALL)
PHON_BLOCK = re.compile(r"^\s*\\\[(.+?)\\\]\s*$")
SENSE_NUM = re.compile(r"^\s*(\d+)\)\s*(.*)")


def strip_tags(s: str) -> str:
    # Drop curly-brace tags like {лингв.}
    s = re.sub(r"\{[^}]+\}", "", s)
    s = TAG.sub("", s)
    return re.sub(r"\s+", " ", s).strip()


def split_example(ex: str) -> dict[str, str]:
    """Split 'калмыцкий — русский' on em/en dash."""
    for dash in (" — ", " – ", " - "):
        if dash in ex:
            k, r = ex.split(dash, 1)
            return {"kal": strip_tags(k), "rus": strip_tags(r)}
    return {"kal": strip_tags(ex), "rus": ""}


def parse_entry_body(lines: list[str]) -> tuple[str | None, str | None, list[dict]]:
    """Return (pos, phonetic, senses)."""
    pos: str | None = None
    phonetic: str | None = None
    senses: list[dict] = []
    current: dict | None = None

    for raw in lines:
        line = raw.rstrip("\n\r")

        # phonetic on its own line:   \[word\]
        m = PHON_BLOCK.match(line.strip())
        if m:
            phonetic = m.group(1).strip()
            continue

        # extract [c]..[/c] — grammar/category
        for cm in C_BLOCK.finditer(line):
            c_text = strip_tags(cm.group(1))
            if c_text and (pos is None or len(c_text) < len(pos) + 20):
                pos = c_text if pos is None else f"{pos}; {c_text}" if c_text not in pos else pos

        # examples
        examples = [split_example(m.group(1)) for m in EX_BLOCK.finditer(line)]

        # strip all tags for the definition text
        plain = strip_tags(line)

        # skip if line is pure category (already captured)
        if not plain and not examples:
            continue

        # numbered sense start?
        num_match = SENSE_NUM.match(plain)
        if num_match:
            if current:
                senses.append(current)
            current = {
                "num": int(num_match.group(1)),
                "def": num_match.group(2).strip(),
                "examples": examples,
            }
            continue

        # [m1] — primary def line, usually starts a new sense if no numbers seen
        if line.lstrip().startswith("[m1]"):
            if current is None:
                current = {"num": 1, "def": plain, "examples": examples}
            else:
                # Continuation / additional meaning
                if plain:
                    current["def"] = (current["def"] + "; " + plain).strip("; ")
                current["examples"].extend(examples)
            continue

        # [m2] / [*] — example/sub-content
        if line.lstrip().startswith("[m2]") or line.lstrip().startswith("[*]"):
            if current is None:
                current = {"num": 1, "def": "", "examples": []}
            current["examples"].extend(examples)
            if plain and not examples:
                # Something that wasn't wrapped in [ex] — treat as additional def
                if not current["def"]:
                    current["def"] = plain
            continue

        # Fallback — just collect plain text
        if current is None:
            current = {"num": 1, "def": plain, "examples": examples}
        else:
            if plain and not current["def"]:
                current["def"] = plain
            current["examples"].extend(examples)

    if current:
        senses.append(current)

    # Dedupe examples per sense
    for s in senses:
        seen = set()
        uniq = []
        for e in s["examples"]:
            key = (e["kal"], e["rus"])
            if key in seen or not e["kal"]:
                continue
            seen.add(key)
            uniq.append(e)
        s["examples"] = uniq

    return pos, phonetic, senses


def make_id(lemma: str, idx: int) -> str:
    slug = re.sub(r"\s+", "_", lemma.strip())
    return f"{idx:06d}_{slug}"


def parse(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    # Drop BOM + header lines starting with '#' at the very top
    raw_lines = text.splitlines()
    # Skip DSL header
    body_start = 0
    for i, ln in enumerate(raw_lines):
        if ln.strip().startswith("#"):
            body_start = i + 1
        elif ln.strip() == "":
            continue
        else:
            break
    raw_lines = raw_lines[body_start:]

    entries: list[dict[str, Any]] = []
    current_headwords: list[str] = []  # stacked `=w1`/`=w2`/lemma all sharing one body
    current_body: list[str] = []

    def flush():
        nonlocal current_headwords, current_body
        if not current_headwords:
            current_body = []
            return
        pos, phonetic, senses = parse_entry_body(current_body)
        senses = [s for s in senses if s["def"] or s["examples"]]
        if senses:
            primary = current_headwords[0]
            aliases = current_headwords[1:]
            entries.append({
                "id": make_id(primary, len(entries)),
                "lemma": primary.strip(),
                "phonetic": phonetic,
                "pos": pos,
                "senses": senses,
                "aliases": aliases,
            })
        current_headwords = []
        current_body = []

    for raw in raw_lines:
        if not raw.strip():
            continue
        # Skip DSL directive lines (BOM-prefixed #NAME etc.)
        stripped = raw.lstrip("\ufeff").strip()
        if stripped.startswith("#"):
            continue

        if raw.startswith("\t") or raw.startswith(" "):
            # indented continuation line belongs to previous/open entry body
            if current_headwords:
                current_body.append(raw)
            continue

        # Non-indented line. If we already have a body, this starts a new entry.
        # Stacking: `=word` lines or bare headwords at column 0 before body = headword group.
        if current_body:
            flush()

        if raw.startswith("="):
            current_headwords.append(raw[1:].strip())
        else:
            current_headwords.append(raw.strip())

    flush()
    return entries


def main() -> int:
    if not DSL.exists():
        print(f"DSL not found: {DSL}", file=sys.stderr)
        return 1
    OUT_DICT.parent.mkdir(parents=True, exist_ok=True)

    entries = parse(DSL)
    print(f"parsed {len(entries)} entries")

    OUT_DICT.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # compact for bundling
    OUT_COMPACT.write_text(
        json.dumps(entries, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"wrote {OUT_DICT} ({OUT_DICT.stat().st_size:,} bytes)")
    print(f"wrote {OUT_COMPACT} ({OUT_COMPACT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
