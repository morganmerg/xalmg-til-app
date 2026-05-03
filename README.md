# Хальмг Тиль — Mobile Learning App

Offline mobile app for learning Kalmyk (калмыцкий язык), built on Expo + React
Native. Companion to the grant-funded web app of the same name. Ships with the
full Kalmyk-Russian dictionary (22,846 entries) and 5 starter lessons.

## What's here

| Part                  | Status | Notes                                          |
|-----------------------|--------|------------------------------------------------|
| Dictionary parsing    | ✅     | `scripts/parse_dsl.py` → 22,846 entries JSON   |
| SQLite + FTS5 build   | ✅     | `scripts/build_sqlite.py` → 7.4 MB bundled .db |
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

# 4. build SQLite
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
├── data/          source JSON (dictionary.json, audio_manifest.json)
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

1. Run on a real device; confirm Cyrillic + Kalmyk-specific letters render.
2. Expand lesson catalogue past the initial 5 sets (generate from dictionary
   categories by thematic tags in `senses.def`).
3. Stand up the TTS / pronunciation-scoring backend and wire `expo-audio`.
4. Fix audio filename decoding by comparing byte-level positions against the
   DSL file's lemma order.
