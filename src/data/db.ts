// SQLite wrapper — opens the bundled dictionary.db asset once and exposes
// typed queries. expo-sqlite + expo-asset together let us ship a prebuilt DB.

import * as SQLite from 'expo-sqlite';
import { Asset } from 'expo-asset';
import * as FileSystem from 'expo-file-system/legacy';

export type Sense = {
  num: number | null;
  def: string;
  examples: Array<{ kal: string; rus: string }>;
};

export type Entry = {
  id: number;
  lemma: string;
  phonetic: string | null;
  pos: string | null;
  senses: Sense[];
  audioFile?: string | null;
};

let db: SQLite.SQLiteDatabase | null = null;
let opening: Promise<SQLite.SQLiteDatabase> | null = null;

async function copyBundledDb(): Promise<string> {
  const dbDir = `${FileSystem.documentDirectory}SQLite`;
  const dest = `${dbDir}/dictionary.db`;

  await FileSystem.makeDirectoryAsync(dbDir, { intermediates: true });
  const asset = Asset.fromModule(require('../../assets/db/dictionary.db'));
  await asset.downloadAsync();
  if (!asset.localUri) {
    throw new Error('Dictionary DB asset not available');
  }

  const info = await FileSystem.getInfoAsync(dest);
  const assetInfo = await FileSystem.getInfoAsync(asset.localUri);
  const destSize = (info.exists && (info as any).size) || 0;
  const assetSize = (assetInfo.exists && (assetInfo as any).size) || 0;
  if (destSize && assetSize && destSize === assetSize) {
    return dest;
  }

  await FileSystem.copyAsync({ from: asset.localUri, to: dest });
  return dest;
}

export async function getDb(): Promise<SQLite.SQLiteDatabase> {
  if (db) return db;
  if (!opening) {
    opening = (async () => {
      await copyBundledDb();
      const opened = await SQLite.openDatabaseAsync('dictionary.db');
      db = opened;
      return opened;
    })();
  }
  return opening;
}

export async function searchLemma(query: string, limit = 40): Promise<Entry[]> {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const d = await getDb();
  // Prefix match first, then FTS fallback
  const rows = await d.getAllAsync<{
    id: number;
    lemma: string;
    phonetic: string | null;
    pos: string | null;
  }>(
    `SELECT id, lemma, phonetic, pos FROM entries
     WHERE lemma_lc LIKE ? OR lemma_lc = ?
     ORDER BY CASE WHEN lemma_lc = ? THEN 0 WHEN lemma_lc LIKE ? THEN 1 ELSE 2 END, length(lemma), lemma
     LIMIT ?`,
    [`${q}%`, q, q, `${q}%`, limit]
  );
  return Promise.all(rows.map(hydrateEntry));
}

export async function searchRussian(query: string, limit = 30): Promise<Entry[]> {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const d = await getDb();
  const rows = await d.getAllAsync<{
    id: number;
    lemma: string;
    phonetic: string | null;
    pos: string | null;
  }>(
    `SELECT e.id, e.lemma, e.phonetic, e.pos
     FROM entries_fts fts JOIN entries e ON e.id = fts.rowid
     WHERE entries_fts MATCH ?
     ORDER BY rank
     LIMIT ?`,
    [q + '*', limit]
  );
  return Promise.all(rows.map(hydrateEntry));
}

export async function getEntry(id: number): Promise<Entry | null> {
  const d = await getDb();
  const row = await d.getFirstAsync<{
    id: number;
    lemma: string;
    phonetic: string | null;
    pos: string | null;
  }>(`SELECT id, lemma, phonetic, pos FROM entries WHERE id = ?`, [id]);
  if (!row) return null;
  return hydrateEntry(row);
}

export async function getEntryByLemma(lemma: string): Promise<Entry | null> {
  const d = await getDb();
  const row = await d.getFirstAsync<{
    id: number;
    lemma: string;
    phonetic: string | null;
    pos: string | null;
  }>(
    `SELECT id, lemma, phonetic, pos FROM entries WHERE lemma_lc = ? LIMIT 1`,
    [lemma.toLowerCase()]
  );
  if (!row) return null;
  return hydrateEntry(row);
}

async function hydrateEntry(row: {
  id: number;
  lemma: string;
  phonetic: string | null;
  pos: string | null;
}): Promise<Entry> {
  const d = await getDb();
  const senses = await d.getAllAsync<{
    num: number | null;
    def: string;
    examples_json: string;
  }>(
    `SELECT num, def, examples_json FROM senses WHERE entry_id = ? ORDER BY id`,
    [row.id]
  );
  const audio = await d.getFirstAsync<{ file: string }>(
    `SELECT file FROM audio WHERE lemma_lc = ? LIMIT 1`,
    [row.lemma.toLowerCase()]
  );
  return {
    id: row.id,
    lemma: row.lemma,
    phonetic: row.phonetic,
    pos: row.pos,
    audioFile: audio?.file ?? null,
    senses: senses.map((s) => ({
      num: s.num,
      def: s.def,
      examples: JSON.parse(s.examples_json || '[]'),
    })),
  };
}

export async function stats(): Promise<{ entries: number; audio: number }> {
  const d = await getDb();
  const e = await d.getFirstAsync<{ c: number }>(`SELECT count(*) as c FROM entries`);
  const a = await d.getFirstAsync<{ c: number }>(`SELECT count(*) as c FROM audio`);
  return { entries: e?.c ?? 0, audio: a?.c ?? 0 };
}
