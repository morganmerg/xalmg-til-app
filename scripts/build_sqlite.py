"""
Convert dictionary.json -> dictionary.db (SQLite, bundled as app asset).

Tables:
  entries(id, lemma, lemma_lc, phonetic, pos)
  senses(id, entry_id, num, def, examples_json)
  aliases(alias, entry_id)  -- lookup by alternate form
  audio(lemma_lc, file)     -- populated from audio_manifest.json

FTS5 virtual table for full-text search over lemma + def.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "data"
DB_OUT = ROOT / "assets" / "db" / "dictionary.db"

DB_OUT.parent.mkdir(parents=True, exist_ok=True)
if DB_OUT.exists():
    DB_OUT.unlink()


def lc(s: str) -> str:
    return s.lower().strip() if s else ""


def main() -> int:
    dict_path = DATA / "dictionary.compact.json"
    audio_path = DATA / "audio_manifest.json"
    entries = json.loads(dict_path.read_text(encoding="utf-8"))

    audio_map: dict[str, str] = {}
    if audio_path.exists():
        audio = json.loads(audio_path.read_text(encoding="utf-8"))
        for lemma, items in audio["manifest"].items():
            # Prefer the base variant (no _I_1) suffix) if available
            items.sort(key=lambda x: len(x.get("variant", "")))
            if items:
                audio_map[lemma] = items[0]["file"]

    conn = sqlite3.connect(DB_OUT)
    c = conn.cursor()
    c.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=OFF;

        CREATE TABLE entries (
            id INTEGER PRIMARY KEY,
            lemma TEXT NOT NULL,
            lemma_lc TEXT NOT NULL,
            phonetic TEXT,
            pos TEXT
        );
        CREATE INDEX idx_entries_lemma_lc ON entries(lemma_lc);

        CREATE TABLE senses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            num INTEGER,
            def TEXT,
            examples_json TEXT
        );
        CREATE INDEX idx_senses_entry ON senses(entry_id);

        CREATE TABLE aliases (
            alias TEXT NOT NULL,
            entry_id INTEGER NOT NULL
        );
        CREATE INDEX idx_aliases_alias ON aliases(alias);

        CREATE TABLE audio (
            lemma_lc TEXT PRIMARY KEY,
            file TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE entries_fts USING fts5(
            lemma, def,
            content=''
        );
        """
    )

    eid = 0
    for e in entries:
        eid += 1
        c.execute(
            "INSERT INTO entries(id, lemma, lemma_lc, phonetic, pos) VALUES (?,?,?,?,?)",
            (eid, e["lemma"], lc(e["lemma"]), e.get("phonetic"), e.get("pos")),
        )
        # senses
        all_defs: list[str] = []
        for s in e["senses"]:
            c.execute(
                "INSERT INTO senses(entry_id, num, def, examples_json) VALUES (?,?,?,?)",
                (eid, s.get("num"), s.get("def"), json.dumps(s.get("examples", []), ensure_ascii=False)),
            )
            if s.get("def"):
                all_defs.append(s["def"])
        # aliases
        for al in e.get("aliases") or []:
            c.execute("INSERT INTO aliases(alias, entry_id) VALUES (?,?)", (lc(al), eid))
        # fts
        c.execute(
            "INSERT INTO entries_fts(rowid, lemma, def) VALUES (?,?,?)",
            (eid, e["lemma"], " ".join(all_defs)),
        )

    # audio
    for lemma_lc, file in audio_map.items():
        c.execute("INSERT OR REPLACE INTO audio(lemma_lc, file) VALUES (?,?)", (lemma_lc, file))

    conn.commit()
    conn.execute("VACUUM")
    conn.close()

    size = DB_OUT.stat().st_size
    print(f"built {DB_OUT} ({size:,} bytes, {size/1024/1024:.1f} MB)")
    print(f"entries: {eid}")
    print(f"audio rows: {len(audio_map)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
