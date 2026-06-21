# Xalmg Til Roadmap

## Purpose

Build a mobile app for people who almost do not know Kalmyk and need a calm first path into the language.

The app has two jobs:

1. Teach a small, useful beginner core through short lessons.
2. Keep the full Kalmyk-Russian dictionary available as a serious reference.

The app should not pretend that 23k dictionary entries are a course. The course is curated. The dictionary is a searchable source.

## Current Reality

- Full dictionary exists in SQLite: 23,216 entries after Wiktionary merge.
- Dictionary entries now have generated tags in `entry_tags`.
- Starter lessons are still tiny and hardcoded.
- Figma direction exists, but it is not yet tied to a real learning system.
- Audio is not solved. TTS is not acceptable as a primary path because it will not reliably produce Kalmyk sounds.

## MVP User

Primary user:

- speaks Russian;
- knows little or no Kalmyk;
- may feel shame or pressure around not knowing the language;
- needs small, low-pressure wins;
- benefits from culture and identity, but cannot start with complex texts.

MVP tone:

- simple;
- respectful;
- not exam-like;
- not childish;
- culturally grounded without overloading the learner.

## Product Principles

- Course and dictionary are separate surfaces.
- Every lesson teaches a small amount.
- Every learned item should reappear later.
- Errors should create review, not punishment.
- Cultural material is a separate layer, not beginner vocabulary noise.
- Audio must be real recorded audio or absent. No fake confidence.

## MVP Scope

### In MVP

- Home screen with today's learning task.
- Learning path with first beginner units.
- Short lesson flow.
- Dictionary search over the full database.
- Word detail page with meanings and examples.
- Basic progress: completed lessons, streak or activity count.
- Cultural discovery cards from tagged content.
- Audio status support in the data model, even if most words have no audio.

### Not In MVP

- Full 23k-word learning course.
- AI/TTS-generated pronunciation as a source of truth.
- Speech recognition or pronunciation scoring.
- Todo Bichig.
- Grammar textbook mode.
- Social features.
- Push notifications.
- Heavy gamification economy.

## Data Roadmap

### Layer 1: Raw Dictionary

Source files:

- `assets/data/dictionary.json`
- `assets/data/dictionary.compact.json`
- `assets/db/dictionary.db`

Use for:

- search;
- word detail;
- examples;
- future thematic extraction.

Do not use raw dictionary entries directly as lesson content.

### Layer 2: Generated Tags

Current output:

- `assets/data/dictionary.tags.json`
- SQLite table: `entry_tags`

Existing important tags:

- `beginner_candidate`
- `cultural_candidate`
- `proverb`
- `dzhangar`
- `riddle`
- `folklore`
- `grammar_form`
- `multiword_lemma`
- `has_examples`
- `has_phonetic`

Rule: generated tags are a rough filter, not final truth.

### Layer 3: Human-Reviewed Learning Core

Needed next:

- `assets/data/learning_core.json`

This should contain the first 300-500 approved words and phrases:

- id;
- lemma;
- Russian meaning;
- category;
- difficulty;
- example entry id;
- audio status;
- lesson eligibility.

This is the real source for beginner lessons.

### Layer 4: Audio Backlog

Needed next:

- `assets/data/audio_backlog.json`

Each item:

- lemma;
- Russian meaning;
- example phrase if useful;
- target filename;
- speaker;
- status: `needed`, `recorded`, `approved`, `rejected`;
- notes.

Audio is recorded by a speaker. TTS is not the source of truth.

## Learning Roadmap

### Learning Loop V1

One lesson should take 3-7 minutes.

Lesson structure:

1. Introduce 3-6 words or phrases.
2. Ask recognition questions.
3. Ask reverse recognition questions.
4. Use one example sentence when available.
5. Repeat mistakes before finish.
6. Mark items as seen/review-needed.

Exercise types:

- choose Kalmyk from Russian;
- choose Russian from Kalmyk;
- match pairs;
- complete a short phrase;
- recognize a word inside an example;
- review previous mistakes.

Do not start with typing exercises. They are too high-friction for MVP.

### First Course Shape

Unit 0: Sounds and Letters

- special letters;
- pronunciation notes;
- examples without requiring full memorization.

Unit 1: Greeting and Politeness

- hello;
- goodbye;
- thank you;
- good day;
- how are you;
- simple respectful phrases.

Unit 2: Family

- father;
- mother;
- child;
- son;
- daughter;
- elder/younger family words if beginner-safe.

Unit 3: Home and Daily Life

- home;
- food;
- tea;
- water;
- sleep;
- go/come.

Unit 4: Steppe and Animals

- sun;
- horse;
- saiga;
- wind;
- water;
- earth/steppe.

Unit 5: Numbers and Time

- 1-10;
- day;
- today;
- tomorrow;
- week.

This first course should be small enough to complete and test.

## Cultural Roadmap

Cultural material is discovery, not mandatory beginner memorization.

Use tags:

- `proverb`
- `dzhangar`
- `riddle`
- `folklore`

MVP cultural formats:

- Proverb of the day.
- Riddle card.
- Word from Dzhangar.
- Cultural note attached to a word.

Each cultural item needs human review before it appears in the polished app.

## Audio Strategy

No full-dictionary audio in MVP.

Order:

1. Build audio backlog for first 300-500 learning items.
2. Record one stable speaker.
3. Store files with predictable names.
4. Add `audio_status` and `audio_file` to learning data.
5. Show play button only when audio is approved.

Do not show fake audio icons for words without real recordings.

## Design Roadmap

Existing Figma direction is useful, but it must now follow the learning system.

Required screen set:

- Home / today;
- Learning path;
- Lesson intro;
- Lesson question;
- Lesson result;
- Dictionary search;
- Word detail;
- Culture card;
- Profile/progress.

Design work should wait until the first course and data model are clear enough.

## Implementation Roadmap

### Phase 1: Planning And Data

Active now.

- Keep this roadmap updated.
- Validate dictionary classification with samples.
- Create first `learning_core.json`.
- Create `audio_backlog.json`.
- Define lesson data schema.

### Phase 2: Learning MVP

- Replace hardcoded starter lessons with generated/curated lesson data.
- Implement lesson item progress.
- Add review of mistakes.
- Use `entry_tags` for discovery pools.

### Phase 3: UX/Figma Alignment

- Update Figma to match real screens.
- Remove placeholder learning content.
- Make cultural cards and audio states visible in design.

### Phase 4: Audio Recording Pipeline

- Export recording sheets.
- Import approved recordings.
- Wire playback in word detail and lessons.

### Phase 5: Real Device QA

- Test on Android device.
- Check Kalmyk letters.
- Check SQLite copy/open.
- Check search performance.
- Check lesson completion and progress persistence.

## Active Focus

Current focus:

1. Product and learning plan.
2. Data structure for beginner course.
3. First human-reviewable learning core.

Do not start these until the current focus is done:

- new mascot generation;
- new Figma redesign;
- audio UI implementation;
- speech scoring;
- new game mechanics;
- full lesson catalogue generation.

## Parking Lot

Ideas parked for later:

- AI pronunciation scoring;
- Todo Bichig;
- generated illustrations for every lesson;
- phrasebook mode;
- school/teacher dashboard;
- spaced repetition beyond simple review;
- offline audio pack download;
- community contribution workflow;
- cultural map of Kalmykia;
- web version.

## Next Concrete Step

Create the first `learning_core.json` candidate list:

- 300-500 items maximum;
- selected from `beginner_candidate`;
- grouped by beginner themes;
- excluding obvious grammar forms, rare terms, and confusing entries;
- with a review report showing what was included and why.

This becomes the base for the first real course.
