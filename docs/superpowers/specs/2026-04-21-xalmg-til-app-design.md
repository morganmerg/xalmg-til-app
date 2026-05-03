---
created: 2026-04-21
type: project
status: active
tags: [dev, grant, mobile, kalmyk]
---

# Хальмг Тиль — Mobile App Design

## Context

The grant application "Хальмг Тиль" (filed 2026-04-16, approved for execution
2026-07 through 2027-06) calls for an **interactive web application** that
teaches Kalmyk to school-age youth in Elista — 500+ students across three
partner schools. The user decided to extend scope: the learner-facing surface
should be a **cross-platform mobile app** (iOS + Android), shipped offline,
with the same brand and educational content. The grant-funded web app remains
the canonical product; the mobile app is a companion learning surface.

This spec covers the **MVP mobile app** built in a single autonomous overnight
session on 2026-04-21, using:

- the full Kalmyk-Russian Lingvo dictionary (~22,800 entries, 6.6 MB source);
- 366 WAV pronunciation files (49 MB, partial name-decoding issues — not
  bundled in MVP);
- an already-designed brand and motion sketch authored by the user
  (`scenes.jsx`, `animations.jsx`, `ios-frame.jsx`) using a warm steppe palette
  and iOS 26 liquid-glass aesthetic.

## Goals / non-goals

**Goals (MVP):**
- Ship a working offline app for both iOS and Android.
- Full Kalmyk-Russian dictionary with prefix search on lemma and Russian FTS.
- 5 starter lessons (Приветствия, Семья, Степь, Еда, Числа), each 6-10 items.
- Multiple-choice quiz flow mirroring the pitch-video lesson scene.
- Streak tracking, daily word-of-day, per-lesson completion.
- Fidelity to the pitch-video design: steppe palette, Inter + JetBrainsMono,
  Kalmyk geometric ornament, bilingual labels (Kal · Rus).
- Zero network dependency — bundled SQLite + lesson data.

**Non-goals (MVP):**
- **TTS synthesis and AI pronunciation assessment** — these require a GPU
  backend (grant budgets an RTX 5060 Ti specifically for this). Will be added
  in v2 as REST calls to a self-hosted service.
- **Audio playback of Lingvo recordings** — 198 file names fail to decode
  through cp866 because Kalmyk-specific letters (ә, ө, ү, җ, ң, һ) are outside
  that codepage. A small subset (~20 entries) matches exactly; deferred until
  the encoding is fully reverse-engineered.
- **Тодо Бичиг** (old Kalmyk vertical script) — grant marks as v2 scope.
- **SRS** (spaced repetition) — MVP tracks streak and lesson-done only; SRS
  queue comes after grant start.
- **Teacher dashboard / analytics** — grant's B2G component, not learner MVP.
- **Publication to App Store / Play Store** — delivered as Expo dev build only.

## Stack

| Concern                   | Choice                                          |
|---------------------------|-------------------------------------------------|
| Framework                 | Expo SDK 54 + React Native 0.81 (TypeScript)    |
| Navigation                | @react-navigation/native + native-stack + tabs  |
| Offline store             | expo-sqlite (bundled .db asset, 7.4 MB)         |
| Animation                 | react-native-reanimated 4 (+ worklets plugin)   |
| Haptics                   | expo-haptics                                    |
| Fonts                     | @expo-google-fonts/{inter, jetbrains-mono}      |
| Blur / glass effects      | expo-blur                                       |
| Gradient                  | expo-linear-gradient                            |
| Vector graphics           | react-native-svg                                |
| Progress persistence      | @react-native-async-storage/async-storage       |
| Audio (v2)                | expo-audio                                      |

### Why Expo over bare RN

- Same codebase for iOS + Android
- Prebuilt config plugins for sqlite/asset/audio/fonts
- `expo export` Metro bundle is Hermes-compiled (2.42 MB JS), small
- OTA updates later via EAS

### Why bundled SQLite over in-memory JSON

- 7.4 MB bundled DB vs 7.2 MB JSON — same on disk, but JSON must load + parse
  into RAM on start (~150 ms + heap cost); SQLite queries lazy.
- FTS5 virtual table supports fuzzy Russian-side search for free.

## Design language

All tokens are ports of the user's motion sketch (`scenes.jsx`):

- **Steppe palette** — clay terracotta (`#C86B3E`), ochre, cream (`#FAF5E9`),
  warm ink. oklch values preserved in comments in `src/theme/tokens.ts`.
- **Typography** — Inter (400/500/700) for UI; JetBrains Mono (400/500) for
  eyebrow kickers and meta strings.
- **Ornament** — rhombic meander pattern from `OrnamentTile`, reused on the
  word-of-day card and profile header.
- **Bilingual pattern** — every surface label is Kalmyk + Russian (Өдрин үг
  · Слово дня, Зөв! · Правильно, Эклий · Начать урок).

## Architecture

```
App.tsx
  └── RootNavigator (NavigationContainer)
        ├── Tabs: Home / Dictionary / Profile
        └── Stack modals: Lesson / EntryDetail / EntryByLemma

src/
├── theme/         tokens, Ornament, GlassPill, BilingualText
├── data/
│   ├── db.ts          SQLite wrapper — getDb, searchLemma, searchRussian
│   ├── lessons.ts     5 hardcoded starter lessons
│   ├── wordOfDay.ts   deterministic daily word
│   └── progress.ts    AsyncStorage streak + lesson-done
├── navigation/    Root + types
└── screens/       Home, Dictionary, EntryDetail, Lesson, Profile

assets/
├── data/          dictionary.json, audio_manifest.json
└── db/dictionary.db   (built from JSON via scripts/build_sqlite.py)

scripts/
├── parse_dsl.py   Lingvo DSL → structured JSON
├── decode_audio.py  WAV filename mojibake → best-guess Kalmyk lemma
└── build_sqlite.py  JSON → SQLite (with FTS5)
```

### Data pipeline

```
xal-rus.dsl.dz  ── gunzip ─► xal-rus.dsl (UTF-16 LE)
                             │
                             ▼   iconv → UTF-8
               parse_dsl.py  │
                             ▼
               dictionary.json (22,846 entries)
                             │
            build_sqlite.py  │ + audio_manifest.json
                             ▼
                    dictionary.db (FTS5, 7.4 MB)  ← bundled as asset
```

## Screens

### Home
- Brand header + streak chip (🔥 count pulled from AsyncStorage).
- **Слово дня** — gradient card with the ornament stamp, renders a
  deterministic daily Kalmyk word from the lesson pool; taps open Entry.
- **Уроки** — vertical list of 5 lesson tiles. The first incomplete one is
  highlighted (clay fill). Taps push Lesson modal.
- CTA at bottom: "Эклий · Начать урок".

### Dictionary
- Debounced text input. If query contains Kalmyk-only characters →
  `searchLemma` (prefix on lemma_lc). Otherwise → `searchRussian` (FTS5 match
  on `def` tokens). Falls back to lemma search when FTS returns empty.
- Empty state shows total entry count and input hint.
- Rows show lemma + phonetic + first definition + audio dot (if available).

### Entry detail
- Large lemma + phonetic + POS.
- Sense list: numbered, with indented example block (Kalmyk on top line,
  Russian translation below prefixed by an em-dash).

### Lesson
- Top bar: back + reanimated progress track + "n/N" counter.
- Question: Russian prompt in quotes; 4 Kalmyk options in a 2×2 grid.
- On pick: haptic + reveal correct (clay fill + shadow) or mark wrong
  (danger border). 950 ms beat, then advance.
- On finish: celebration screen with score, `markLessonDone`, `bumpStreak`.

### Profile
- Streak card with ornament overlay.
- Stats row: total dictionary entries, audio-enabled count.
- About + credits text; mailto link.

## Data model (SQLite)

```sql
entries(id PK, lemma, lemma_lc, phonetic, pos)
senses(id PK, entry_id FK, num, def, examples_json)
aliases(alias, entry_id)     -- alt forms
audio(lemma_lc PK, file)      -- 198 rows (best-effort mapping)
entries_fts (lemma, def)      -- FTS5, external content
```

Indexes on `entries.lemma_lc` and `senses.entry_id`.

## MVP acceptance

- [x] `npx tsc --noEmit` passes with `"strict": true`.
- [x] `npx expo export --platform android` produces a bundle (2.42 MB Hermes)
      that includes `dictionary.db` as an asset.
- [ ] `expo start` launches Metro and the app renders Home with lesson tiles
      on a physical device (Expo Go). **→ needs user to run on device.**
- [ ] Dictionary search returns results for both Kalmyk (e.g. `аав`) and
      Russian (e.g. `отец`) queries. **→ needs on-device run.**
- [ ] Finishing a lesson bumps streak and marks the tile ✓. **→ on-device.**

Device-verification steps are listed in `README.md`.

## Future work

1. **Audio restoration** — fully decode the Lingvo WAV filenames. Likely the
   original pack used a Mongolian/Kalmyk custom codepage; requires either the
   original DSL file side-by-side (which already points to files by index),
   or manual labelling of the 197 unique prefixes.
2. **TTS + pronunciation scoring** — implement as a FastAPI service on the
   grant-funded GPU rig, accessed via `https://mcp.morganmerg.tech/xalmg/...`
   or a dedicated subdomain. Client just records a short clip, posts it, and
   displays a feedback score + waveform.
3. **Proper SRS** — when lesson catalogue grows past the curated 5,
   introduce a Leitner or SM-2 queue with review reminders.
4. **Expo Router migration** — once > 10 screens, move from native-stack +
   Tabs to file-based routing.
5. **Shared design with the grant web app** — extract tokens + ornament to a
   `@xalmg/ui` package; the web app imports the same Tailwind config + SVG.
6. **Todo Bichig (vertical script)** — dedicated module with custom font and
   vertical text rendering.
