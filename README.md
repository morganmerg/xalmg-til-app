# Хальмг Тиль — Mobile Learning App

Offline mobile app for learning Kalmyk (калмыцкий язык), built on Expo + React
Native. Companion to the grant-funded web app of the same name. Ships with the
full Kalmyk-Russian dictionary (22,846 source entries; 23,216 after Wiktionary
merge) and 5 starter lessons.

## What's here

| Part                  | Status | Notes                                          |
|-----------------------|--------|------------------------------------------------|
| Dictionary parsing    | ✅     | `scripts/parse_dsl.py` → 22,846 source entries |
| Dictionary tagging    | ✅     | `scripts/classify_dictionary.py` → entry tags  |
| Learning targets      | ✅     | `scripts/build_learning_targets.py` → 300 fixed category slots |
| Learning core         | ✅     | `scripts/build_learning_core.py` → 300 review candidates |
| SQLite + FTS5 build   | ✅     | `scripts/build_sqlite.py` → 11.8 MB bundled DB |
| Design system         | ✅     | Tokens, Ornament, GlassPill, BilingualText     |
| Home screen           | ✅     | Word of day + lesson tiles + streak            |
| Dictionary screen     | ✅     | Debounced search (Kalmyk prefix + Russian FTS) |
| Entry detail screen   | ✅     | Senses + examples                              |
| Lesson screen         | ✅     | Multiple-choice quiz w/ haptics                |
| Profile screen        | ✅     | Streak + stats + credits                       |
| Navigation            | ✅     | Tabs + modal stack                             |
| Offline DB            | ✅     | SQLite copied from asset on first run          |
| Android bundle        | ✅     | 2.42 MB Hermes bytecode                        |
| Audio playback        | ⏳     | 198 files partially decoded (Kalmyk chars miss)|
| TTS + AI pronunciation| ⏳     | needs GPU backend (grant funded)               |
| Todo Бичиг            | ⏳     | v2                                             |

## Run on device

**Prerequisite:** Expo Go app installed on your phone + phone on same network.

```bash
cd D:/morgan/10_Projects/xalmg-til-app
npx expo start
```

Press `a` (Android) or `i` (iOS) or scan the QR code with Expo Go. First load
copies the bundled `dictionary.db` from assets into app storage (one-time).

If Metro complains about worklets, blow away the cache:

```bash
npx expo start -c
```

## Rebuild data

```bash
# 1. extract DSL from the Lingvo .dz pack
gunzip -c "xal-rus.dsl.dz" > /tmp/xal-rus.dsl
iconv -f UTF-16LE -t UTF-8 /tmp/xal-rus.dsl > /tmp/xal-rus.utf8.dsl

# 2. parse to JSON
PYTHONIOENCODING=utf-8 python scripts/parse_dsl.py

# 3. (optional) decode audio filenames
PYTHONIOENCODING=utf-8 python scripts/decode_audio.py

# 4. merge Russian Wiktionary Kalmyk entries, if the local source is present
PYTHONIOENCODING=utf-8 python scripts/merge_ruwikt.py

# 5. classify entries for beginner/cultural/grammar filtering
PYTHONIOENCODING=utf-8 python scripts/classify_dictionary.py

# 6. map the fixed 300 beginner targets to dictionary entries
PYTHONIOENCODING=utf-8 python scripts/build_learning_targets.py

# 7. build the first human-reviewable learning core
PYTHONIOENCODING=utf-8 python scripts/build_learning_core.py

# 8. build SQLite with FTS and entry_tags
PYTHONIOENCODING=utf-8 python scripts/build_sqlite.py
```

## Project layout

```
src/
├── theme/         design tokens + primitives (Ornament, GlassPill, etc.)
├── data/          SQLite wrapper, lessons, word-of-day, progress/streak
├── navigation/    root stack + tabs
└── screens/       Home, Dictionary, EntryDetail, Lesson, Profile
assets/
├── data/          source JSON, tag JSON, audio manifest
└── db/            built SQLite bundled into the app
scripts/          data pipeline (Python)
docs/superpowers/ design specs
```

## Known limitations

- **Audio filenames are mojibake.** The Lingvo pack appears to use a custom
  8-bit codepage that predates proper Kalmyk Unicode support. About 20 of 198
  unique prefixes round-trip cleanly through cp437 → cp866; the rest lose
  Kalmyk-specific letters (ә, ө, ү, җ, ң, һ). Audio is therefore not linked
  in MVP. Fix requires either the original full Lingvo sources or manual
  re-labelling.
- **No web build.** expo-sqlite doesn't support the web platform. Remove
  `expo-sqlite` or swap for an in-memory JSON loader if web support becomes
  a goal.
- **Fonts bundle is heavy.** We ship all weights of Inter + JetBrains Mono
  (~4 MB). Trim to only the weights actually used (400/500/700 + 400/500)
  before release.

## Next steps

1. Review `assets/data/learning_targets.json`, resolve manual matches, and use
   it as the first-course target map.
2. Review `assets/data/learning_core.json` and promote approved items into the
   first lesson schema.
3. Create an audio backlog for the reviewed learning core.
4. Run on a real device; confirm Cyrillic + Kalmyk-specific letters render.
5. Expand lesson catalogue past the initial 5 sets using the reviewed thematic
   layer.
6. Fix audio filename decoding by comparing byte-level positions against the
   DSL file's lemma order.
