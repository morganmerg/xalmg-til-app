// Entry detail — full word entry view with all senses, examples, and (if
// available) audio playback.

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Pressable,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute, type RouteProp } from '@react-navigation/native';
import { colors, typography, spacing, radius } from '../theme/tokens';
import type { RootStackParamList } from '../navigation/types';
import { getEntry, getEntryByLemma, type Entry } from '../data/db';

type DetailRoute = RouteProp<RootStackParamList, 'EntryDetail' | 'EntryByLemma'>;

export default function EntryDetailScreen() {
  const route = useRoute<DetailRoute>();
  const nav = useNavigation();
  const [entry, setEntry] = useState<Entry | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      let e: Entry | null = null;
      if ('id' in route.params) {
        e = await getEntry(route.params.id);
      } else if ('lemma' in route.params) {
        e = await getEntryByLemma(route.params.lemma);
      }
      setEntry(e);
      setLoading(false);
    })();
  }, [route.params]);

  if (loading) {
    return (
      <SafeAreaView style={styles.safe}>
        <ActivityIndicator style={{ marginTop: 80 }} color={colors.clay} />
      </SafeAreaView>
    );
  }
  if (!entry) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text style={styles.notFound}>Запись не найдена</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Pressable onPress={() => nav.goBack()} style={styles.back} hitSlop={10}>
          <Text style={styles.backIcon}>←</Text>
        </Pressable>

        <Text style={styles.lemma}>{entry.lemma}</Text>
        {entry.phonetic ? <Text style={styles.phon}>[{entry.phonetic}]</Text> : null}
        {entry.pos ? <Text style={styles.pos}>{entry.pos}</Text> : null}

        {entry.senses.map((s, i) => (
          <View key={i} style={styles.senseBlock}>
            <View style={styles.senseHead}>
              {s.num != null && entry.senses.length > 1 ? (
                <Text style={styles.senseNum}>{s.num}</Text>
              ) : null}
              <Text style={styles.senseDef}>{s.def}</Text>
            </View>
            {s.examples.length > 0 && (
              <View style={styles.examplesBox}>
                {s.examples.map((ex, j) => (
                  <View key={j} style={styles.exampleRow}>
                    <Text style={styles.exKal}>{ex.kal}</Text>
                    {ex.rus ? <Text style={styles.exRus}>— {ex.rus}</Text> : null}
                  </View>
                ))}
              </View>
            )}
          </View>
        ))}

        <View style={{ height: 60 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.cream },
  scroll: { paddingHorizontal: spacing.lg, paddingTop: spacing.sm },
  back: { alignSelf: 'flex-start', padding: 8, marginBottom: spacing.sm },
  backIcon: { fontSize: 24, color: colors.ink },
  notFound: { textAlign: 'center', marginTop: 80, color: colors.inkSoft },

  lemma: {
    fontFamily: typography.sansBold,
    fontSize: 44,
    color: colors.ink,
    letterSpacing: -1.2,
    lineHeight: 50,
  },
  phon: {
    fontFamily: typography.mono,
    fontSize: 16,
    color: colors.inkSoft,
    marginTop: 4,
  },
  pos: {
    fontFamily: typography.mono,
    fontSize: 12,
    color: colors.clay,
    marginTop: 8,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },

  senseBlock: { marginTop: spacing.xl },
  senseHead: { flexDirection: 'row', gap: 10, alignItems: 'flex-start' },
  senseNum: {
    fontFamily: typography.sansBold,
    fontSize: 20,
    color: colors.clay,
    minWidth: 22,
  },
  senseDef: {
    flex: 1,
    fontFamily: typography.sansMed,
    fontSize: 20,
    color: colors.ink,
    lineHeight: 28,
    letterSpacing: -0.3,
  },

  examplesBox: {
    marginTop: 12,
    paddingLeft: spacing.md,
    borderLeftWidth: 2,
    borderLeftColor: colors.clayLt,
    gap: 10,
  },
  exampleRow: { gap: 2 },
  exKal: {
    fontFamily: typography.sansMed,
    fontSize: 16,
    color: colors.ink,
    lineHeight: 22,
  },
  exRus: {
    fontFamily: typography.sans,
    fontSize: 14,
    color: colors.inkSoft,
    lineHeight: 20,
  },
});
