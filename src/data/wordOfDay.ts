// Deterministic "word of the day" selection — picks a lemma from a curated
// list so users see the same word on the same day. Index = day-of-year mod N.

import { LESSONS } from './lessons';

// Flatten all lesson items and dedupe
const POOL = Array.from(
  new Map(
    LESSONS.flatMap((l) => l.items).map((it) => [it.kal.toLowerCase(), it])
  ).values()
);

export type WordOfDay = {
  kal: string;
  rus: string;
  index: number;
  total: number;
};

export function wordOfDay(date = new Date()): WordOfDay {
  const start = new Date(date.getFullYear(), 0, 0);
  const diff = date.getTime() - start.getTime();
  const day = Math.floor(diff / (1000 * 60 * 60 * 24));
  const idx = ((day % POOL.length) + POOL.length) % POOL.length;
  const item = POOL[idx];
  return {
    kal: item.kal,
    rus: item.rus,
    index: idx,
    total: POOL.length,
  };
}
