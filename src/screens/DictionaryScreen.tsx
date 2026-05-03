// Dictionary — search input over lemma prefix; list of entries with preview.
// Tapping an entry opens EntryDetail.

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Pressable,
  FlatList,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, typography, spacing, radius } from '../theme/tokens';
import type { RootStackParamList } from '../navigation/types';
import { searchLemma, searchRussian, stats, type Entry } from '../data/db';

type Nav = NativeStackNavigationProp<RootStackParamList, 'Dictionary'>;

export default function DictionaryScreen() {
  const nav = useNavigation<Nav>();
  const [q, setQ] = useState('');
  const [results, setResults] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const debounce = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    stats().then((s) => setTotal(s.entries));
  }, []);

  const runSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    setLoading(true);
    try {
      const lemmaHits = await searchLemma(query);
      const hits = lemmaHits.length ? lemmaHits : await searchRussian(query);
      setResults(hits);
    } finally {
      setLoading(false);
    }
  }, []);

  const onChange = (text: string) => {
    setQ(text);
    if (debounce.current) clearTimeout(debounce.current);
    debounce.current = setTimeout(() => runSearch(text), 180);
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.searchWrap}>
        <Text style={styles.searchIcon}>🔍</Text>
        <TextInput
          value={q}
          onChangeText={onChange}
          placeholder="Толь · Поиск в словаре"
          placeholderTextColor={colors.inkMute}
          style={styles.input}
          autoCapitalize="none"
          autoCorrect={false}
          returnKeyType="search"
        />
        {q.length > 0 && (
          <Pressable onPress={() => { setQ(''); setResults([]); }} hitSlop={10}>
            <Text style={styles.clear}>✕</Text>
          </Pressable>
        )}
      </View>

      {q.length === 0 ? (
        <View style={styles.emptyWrap}>
          <Text style={styles.emptyKal}>Толь</Text>
          <Text style={styles.emptyRus}>{total.toLocaleString('ru-RU')} слов</Text>
          <Text style={styles.emptyHint}>
            Введите калмыцкое или русское слово
          </Text>
        </View>
      ) : loading && results.length === 0 ? (
        <ActivityIndicator style={{ marginTop: 40 }} color={colors.clay} />
      ) : results.length === 0 ? (
        <Text style={styles.noRes}>Ничего не найдено</Text>
      ) : (
        <FlatList
          data={results}
          keyExtractor={(e) => String(e.id)}
          contentContainerStyle={{ paddingBottom: 40 }}
          renderItem={({ item }) => (
            <Pressable
              style={({ pressed }) => [styles.row, pressed && { backgroundColor: colors.creamDk }]}
              onPress={() => nav.navigate('EntryDetail', { id: item.id })}
            >
              <View style={{ flex: 1 }}>
                <Text style={styles.rowLemma}>{item.lemma}</Text>
                {item.phonetic ? (
                  <Text style={styles.rowPhon}>[{item.phonetic}]</Text>
                ) : null}
                <Text style={styles.rowDef} numberOfLines={1}>
                  {item.senses[0]?.def || '—'}
                </Text>
              </View>
              {item.audioFile ? <Text style={styles.audioDot}>♪</Text> : null}
              <Text style={styles.chev}>›</Text>
            </Pressable>
          )}
          ItemSeparatorComponent={() => <View style={styles.sep} />}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.cream },
  searchWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: spacing.lg,
    marginTop: spacing.sm,
    marginBottom: spacing.sm,
    backgroundColor: colors.white,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.hairline,
    paddingHorizontal: 12,
    height: 48,
    gap: 10,
  },
  searchIcon: { fontSize: 15 },
  input: {
    flex: 1,
    fontFamily: typography.sans,
    fontSize: 16,
    color: colors.ink,
    paddingVertical: 0,
  },
  clear: { color: colors.inkMute, fontSize: 18, paddingHorizontal: 4 },

  emptyWrap: { alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 8 },
  emptyKal: {
    fontFamily: typography.sansBold,
    fontSize: 40,
    color: colors.ink,
    letterSpacing: -1,
  },
  emptyRus: {
    fontFamily: typography.mono,
    fontSize: 13,
    color: colors.inkSoft,
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
  emptyHint: { fontFamily: typography.sans, color: colors.inkSoft, marginTop: 24, fontSize: 14 },
  noRes: { textAlign: 'center', marginTop: 40, color: colors.inkSoft, fontFamily: typography.sans },

  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: 12,
    gap: 10,
  },
  sep: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.hairline,
    marginLeft: spacing.lg,
  },
  rowLemma: { fontFamily: typography.sansBold, fontSize: 18, color: colors.ink, letterSpacing: -0.3 },
  rowPhon: { fontFamily: typography.mono, fontSize: 12, color: colors.inkSoft, marginTop: 1 },
  rowDef: { fontFamily: typography.sans, fontSize: 14, color: colors.inkSoft, marginTop: 2 },
  audioDot: { color: colors.clay, fontSize: 18, marginRight: 4 },
  chev: { color: colors.inkMute, fontSize: 22 },
});
