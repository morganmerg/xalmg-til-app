// Home — the heart of the app. Port of UIScene from scenes.jsx:
//   header (logo + streak) → Слово дня card → Уроки list → CTA

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Pressable,
  SafeAreaView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, typography, spacing, radius, shadow } from '../theme/tokens';
import { OrnamentTile } from '../theme/Ornament';
import { BilingualText, Eyebrow } from '../theme/BilingualText';
import { LESSONS } from '../data/lessons';
import { wordOfDay } from '../data/wordOfDay';
import { getStreak, getAllLessonStatus, bumpStreak } from '../data/progress';
import type { RootStackParamList } from '../navigation/types';

type Nav = NativeStackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen() {
  const nav = useNavigation<Nav>();
  const [streak, setStreak] = useState(0);
  const [done, setDone] = useState<Record<string, boolean>>({});
  const wod = wordOfDay();

  useEffect(() => {
    (async () => {
      setStreak(await getStreak());
      setDone(await getAllLessonStatus(LESSONS.map((l) => l.id)));
    })();
  }, []);

  // Refetch progress when navigation focuses this screen (e.g. after lesson done)
  useEffect(() => {
    const unsub = nav.addListener('focus', async () => {
      setStreak(await getStreak());
      setDone(await getAllLessonStatus(LESSONS.map((l) => l.id)));
    });
    return unsub;
  }, [nav]);

  const activeIdx = LESSONS.findIndex((l) => !done[l.id]);
  const activeLesson = activeIdx >= 0 ? LESSONS[activeIdx] : LESSONS[0];

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.brandRow}>
            <View style={styles.logoBox}>
              <Text style={styles.logoLetter}>Х</Text>
            </View>
            <View>
              <Text style={styles.brandKal}>Хальмг Тиль</Text>
              <Text style={styles.brandRus}>калмыцкий язык</Text>
            </View>
          </View>
          <View style={styles.streakChip}>
            <Text style={styles.streakEmoji}>🔥</Text>
            <Text style={styles.streakNum}>{streak}</Text>
          </View>
        </View>

        {/* Слово дня */}
        <Pressable onPress={() => nav.navigate('EntryByLemma', { lemma: wod.kal })}>
          <LinearGradient
            colors={[colors.clay, colors.clayDk]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={[styles.wodCard, shadow.card2]}
          >
            <View style={styles.wodOrn}>
              <OrnamentTile color={colors.white} opacity={0.35} size={180} />
            </View>
            <Eyebrow color="rgba(255,255,255,0.75)" style={{ marginBottom: 10 }}>
              Өдрин үг · Слово дня
            </Eyebrow>
            <Text style={styles.wodKal}>{wod.kal}</Text>
            <Text style={styles.wodRus}>{wod.rus}</Text>
          </LinearGradient>
        </Pressable>

        {/* Уроки */}
        <Text style={styles.sectionTitle}>Уроки</Text>
        <View style={{ gap: 12 }}>
          {LESSONS.map((lesson, i) => {
            const isDone = !!done[lesson.id];
            const isActive = i === activeIdx;
            return (
              <Pressable
                key={lesson.id}
                onPress={() => nav.navigate('Lesson', { lessonId: lesson.id })}
                style={({ pressed }) => [
                  styles.lessonTile,
                  isActive && styles.lessonTileActive,
                  pressed && { opacity: 0.85, transform: [{ scale: 0.99 }] },
                ]}
              >
                <View style={styles.lessonEmojiBox}>
                  <Text style={styles.lessonEmoji}>{lesson.emoji}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <BilingualText kal={lesson.kal} rus={lesson.rus} size={18} />
                  <Text style={styles.lessonMeta}>
                    {lesson.minutes} мин · урок {lesson.order}
                  </Text>
                </View>
                {isDone ? (
                  <View style={styles.doneBadge}>
                    <Text style={styles.doneBadgeText}>✓</Text>
                  </View>
                ) : (
                  <Text style={[styles.chev, isActive && { color: colors.clay }]}>→</Text>
                )}
              </Pressable>
            );
          })}
        </View>

        {/* CTA */}
        <Pressable
          onPress={() => {
            bumpStreak().then(setStreak);
            nav.navigate('Lesson', { lessonId: activeLesson.id });
          }}
          style={({ pressed }) => [styles.cta, pressed && { opacity: 0.9 }]}
        >
          <Text style={styles.ctaText}>Эклий</Text>
          <Text style={styles.ctaSub}>· Начать урок</Text>
        </Pressable>

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.cream },
  scroll: { paddingHorizontal: spacing.lg, paddingTop: spacing.md },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
  },
  brandRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  logoBox: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: colors.clay,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoLetter: {
    color: colors.white,
    fontFamily: typography.sansBold,
    fontSize: 22,
  },
  brandKal: {
    fontFamily: typography.sansBold,
    fontSize: 20,
    color: colors.ink,
    letterSpacing: -0.3,
    lineHeight: 22,
  },
  brandRus: {
    fontFamily: typography.mono,
    fontSize: 11,
    color: colors.inkSoft,
    marginTop: 3,
    letterSpacing: 0.5,
  },
  streakChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: radius.pill,
    backgroundColor: colors.clayLt,
  },
  streakEmoji: { fontSize: 14 },
  streakNum: {
    fontFamily: typography.sansBold,
    fontSize: 16,
    color: colors.clayDk,
  },

  wodCard: {
    borderRadius: radius.xl,
    paddingVertical: 28,
    paddingHorizontal: 24,
    marginTop: spacing.sm,
    overflow: 'hidden',
  },
  wodOrn: { position: 'absolute', right: -30, top: -30 },
  wodKal: {
    fontFamily: typography.sansBold,
    fontSize: 48,
    color: colors.white,
    letterSpacing: -1,
    lineHeight: 52,
    marginBottom: 8,
  },
  wodRus: {
    fontFamily: typography.sansMed,
    fontSize: 17,
    color: 'rgba(255,255,255,0.9)',
    lineHeight: 22,
  },

  sectionTitle: {
    fontFamily: typography.sansBold,
    fontSize: 20,
    color: colors.ink,
    letterSpacing: -0.2,
    marginTop: spacing.xl,
    marginBottom: spacing.md,
  },

  lessonTile: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    padding: 14,
    borderRadius: radius.lg,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.hairline,
  },
  lessonTileActive: {
    backgroundColor: colors.clayLt,
    borderColor: colors.clay,
  },
  lessonEmojiBox: {
    width: 52,
    height: 52,
    borderRadius: 14,
    backgroundColor: colors.cream,
    borderWidth: 1,
    borderColor: colors.hairline,
    alignItems: 'center',
    justifyContent: 'center',
  },
  lessonEmoji: { fontSize: 24 },
  lessonMeta: {
    fontFamily: typography.mono,
    fontSize: 11,
    color: colors.inkSoft,
    marginTop: 4,
    letterSpacing: 0.5,
  },
  chev: { fontSize: 22, color: colors.inkMute, paddingHorizontal: 6 },
  doneBadge: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.clay,
    alignItems: 'center',
    justifyContent: 'center',
  },
  doneBadgeText: {
    color: colors.white,
    fontFamily: typography.sansBold,
    fontSize: 14,
  },

  cta: {
    marginTop: spacing.lg,
    backgroundColor: colors.ink,
    borderRadius: radius.lg,
    paddingVertical: 18,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  ctaText: {
    color: colors.white,
    fontFamily: typography.sansBold,
    fontSize: 18,
    letterSpacing: -0.2,
  },
  ctaSub: {
    color: 'rgba(255,255,255,0.7)',
    fontFamily: typography.sansMed,
    fontSize: 16,
  },
});
