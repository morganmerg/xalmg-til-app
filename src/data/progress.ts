// Progress + streak persistence via AsyncStorage.

import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY_STREAK = 'xt:streak';
const KEY_LAST_DAY = 'xt:lastDay';
const KEY_LESSON = (id: string) => `xt:lesson:${id}`;

function toDayStr(d = new Date()): string {
  return d.toISOString().slice(0, 10); // YYYY-MM-DD
}

export async function getStreak(): Promise<number> {
  const s = await AsyncStorage.getItem(KEY_STREAK);
  return s ? parseInt(s, 10) || 0 : 0;
}

export async function bumpStreak(): Promise<number> {
  const today = toDayStr();
  const last = await AsyncStorage.getItem(KEY_LAST_DAY);
  let streak = parseInt((await AsyncStorage.getItem(KEY_STREAK)) || '0', 10) || 0;
  if (last === today) {
    return streak;
  }
  const yest = new Date();
  yest.setDate(yest.getDate() - 1);
  if (last === toDayStr(yest)) {
    streak += 1;
  } else {
    streak = 1;
  }
  await AsyncStorage.multiSet([
    [KEY_STREAK, String(streak)],
    [KEY_LAST_DAY, today],
  ]);
  return streak;
}

export async function isLessonDone(id: string): Promise<boolean> {
  return (await AsyncStorage.getItem(KEY_LESSON(id))) === 'done';
}

export async function markLessonDone(id: string): Promise<void> {
  await AsyncStorage.setItem(KEY_LESSON(id), 'done');
}

export async function getAllLessonStatus(
  ids: string[]
): Promise<Record<string, boolean>> {
  const out: Record<string, boolean> = {};
  const pairs = await AsyncStorage.multiGet(ids.map(KEY_LESSON));
  for (const [k, v] of pairs) {
    const id = k.slice('xt:lesson:'.length);
    out[id] = v === 'done';
  }
  return out;
}
