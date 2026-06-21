# Dictionary Classification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reproducible classification layer over the bundled Kalmyk dictionary so the app can distinguish ordinary words, grammar forms, cultural examples, proverbs, riddles, folklore, and beginner-safe candidates.

**Architecture:** Keep the raw dictionary JSON untouched. Add a deterministic Python classifier that reads `assets/data/dictionary.compact.json`, writes compact tag data plus an audit report, and extend SQLite build to persist tags in a separate `entry_tags` table. UI changes are out of scope for this pass.

**Tech Stack:** Python 3.11 standard library, SQLite, existing Expo asset pipeline.

---

### Task 1: Classifier Tests

**Files:**
- Create: `scripts/test_classify_dictionary.py`
- Later create: `scripts/classify_dictionary.py`

- [x] **Step 1: Write failing tests**

Create tests for `classify_entry`, `classify_entries`, and cultural marker behavior. The tests should prove:

- grammar references get `grammar_form` and are not beginner candidates;
- proverb/riddle/folklore/Djangar markers become cultural tags;
- simple one-word entries with examples become `beginner_candidate`;
- multi-word lemmas become `multiword_lemma`;
- Wiktionary entries get `source_ruwikt`.

- [x] **Step 2: Run tests and verify RED**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m unittest scripts.test_classify_dictionary -v
```

Expected: fail because `scripts.classify_dictionary` does not exist yet.

### Task 2: Classifier Implementation

**Files:**
- Create: `scripts/classify_dictionary.py`
- Output when run: `assets/data/dictionary.tags.json`
- Output when run: `docs/data/2026-06-21-dictionary-classification-report.md`

- [x] **Step 1: Implement the classifier**

Add pure functions:

- `classify_entry(entry) -> list[str]`
- `classify_entries(entries) -> tuple[list[dict], dict]`
- `write_outputs(root, tags, stats) -> None`

Use deterministic string markers only; do not use an LLM or network calls.

- [x] **Step 2: Run tests and verify GREEN**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m unittest scripts.test_classify_dictionary -v
```

Expected: all tests pass.

- [x] **Step 3: Generate real outputs**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/classify_dictionary.py
```

Expected: tag JSON and report are written.

### Task 3: SQLite Tag Table

**Files:**
- Modify: `scripts/build_sqlite.py`
- Output when run: `assets/db/dictionary.db`

- [x] **Step 1: Extend SQLite schema**

Add:

```sql
CREATE TABLE entry_tags (
  entry_id INTEGER NOT NULL,
  tag TEXT NOT NULL,
  PRIMARY KEY (entry_id, tag)
);
CREATE INDEX idx_entry_tags_tag ON entry_tags(tag);
```

- [x] **Step 2: Load generated tags during DB build**

Read `assets/data/dictionary.tags.json` if present. Map by original JSON entry `id`, then insert tags for the numeric SQLite `entry_id`.

- [x] **Step 3: Rebuild and inspect DB**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/build_sqlite.py
python - <<'PY'
import sqlite3
con = sqlite3.connect('assets/db/dictionary.db')
print(con.execute('select count(*) from entry_tags').fetchone()[0])
print(con.execute("select count(*) from entry_tags where tag='proverb'").fetchone()[0])
PY
```

Expected: `entry_tags` has rows, and cultural tags are queryable.

### Task 4: Docs And Verification

**Files:**
- Modify: `README.md`
- Verify: `docs/data/2026-06-21-dictionary-classification-report.md`

- [x] **Step 1: Document the data rebuild order**

Document:

```powershell
python scripts/parse_dsl.py
python scripts/merge_ruwikt.py
python scripts/classify_dictionary.py
python scripts/build_sqlite.py
```

- [x] **Step 2: Run full verification**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m unittest scripts.test_classify_dictionary -v
python scripts/classify_dictionary.py
python scripts/build_sqlite.py
npx tsc --noEmit
git status --short
```

Expected: tests pass, scripts complete, TypeScript still typechecks, and changed files are intentional.
