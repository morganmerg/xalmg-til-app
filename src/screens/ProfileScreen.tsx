// Profile — simple stats + credits screen.

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, Linking, Pressable } from 'react-native';
import { colors, typography, spacing, radius } from '../theme/tokens';
import { getStreak } from '../data/progress';
import { stats } from '../data/db';
import { OrnamentTile } from '../theme/Ornament';
import { BilingualText, Eyebrow } from '../theme/BilingualText';

export default function ProfileScreen() {
  const [streak, setStreak] = useState(0);
  const [entries, setEntries] = useState(0);
  const [audio, setAudio] = useState(0);

  useEffect(() => {
    (async () => {
      setStreak(await getStreak());
      const s = await stats();
      setEntries(s.entries);
      setAudio(s.audio);
    })();
  }, []);

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <BilingualText kal="Минь" rus="Мой профиль" size={34} />

        <View style={[styles.card, { marginTop: spacing.lg, overflow: 'hidden' }]}>
          <View style={{ position: 'absolute', right: -20, top: -20, opacity: 0.35 }}>
            <OrnamentTile size={140} color={colors.clay} opacity={0.4} />
          </View>
          <Eyebrow>streak · подряд</Eyebrow>
          <Text style={styles.streakBig}>🔥 {streak}</Text>
          <Text style={styles.streakSub}>
            {streak === 0 ? 'Начни сегодня' : streak === 1 ? 'день' : 'дней'}
          </Text>
        </View>

        <View style={styles.statsRow}>
          <View style={[styles.statCell]}>
            <Text style={styles.statNum}>{entries.toLocaleString('ru-RU')}</Text>
            <Text style={styles.statLabel}>слов в словаре</Text>
          </View>
          <View style={styles.statCell}>
            <Text style={styles.statNum}>{audio}</Text>
            <Text style={styles.statLabel}>озвученных</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Eyebrow>о проекте</Eyebrow>
          <Text style={styles.body}>
            Хальмг Тиль — приложение для изучения калмыцкого языка. Словарь основан на
            калмыцко-русском словаре (Lingvo).
          </Text>
        </View>

        <View style={styles.section}>
          <Eyebrow>благодарности</Eyebrow>
          <Text style={styles.body}>
            Институт калмыцкой филологии и востоковедения КалмГУ. Министерство образования и
            науки Республики Калмыкия.
          </Text>
        </View>

        <Pressable
          onPress={() => Linking.openURL('mailto:zzqq2840@gmail.com?subject=Хальмг Тиль')}
          style={({ pressed }) => [styles.link, pressed && { opacity: 0.7 }]}
        >
          <Text style={styles.linkText}>Написать автору →</Text>
        </Pressable>

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.cream },
  scroll: { paddingHorizontal: spacing.lg, paddingTop: spacing.lg },
  card: {
    backgroundColor: colors.white,
    borderRadius: radius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.hairline,
  },
  streakBig: {
    fontFamily: typography.sansBold,
    fontSize: 72,
    color: colors.ink,
    letterSpacing: -2,
    marginTop: 8,
  },
  streakSub: {
    fontFamily: typography.sansMed,
    fontSize: 16,
    color: colors.inkSoft,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: spacing.md,
  },
  statCell: {
    flex: 1,
    padding: spacing.md,
    borderRadius: radius.lg,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.hairline,
  },
  statNum: {
    fontFamily: typography.sansBold,
    fontSize: 28,
    color: colors.clay,
    letterSpacing: -0.8,
  },
  statLabel: {
    fontFamily: typography.mono,
    fontSize: 11,
    color: colors.inkSoft,
    letterSpacing: 0.6,
    marginTop: 2,
  },
  section: { marginTop: spacing.xl },
  body: {
    fontFamily: typography.sans,
    fontSize: 15,
    color: colors.ink,
    lineHeight: 22,
    marginTop: 8,
  },
  link: { marginTop: spacing.lg, alignSelf: 'flex-start' },
  linkText: {
    fontFamily: typography.sansMed,
    fontSize: 16,
    color: colors.clay,
  },
});
