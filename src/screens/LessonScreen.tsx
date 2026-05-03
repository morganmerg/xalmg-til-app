// Lesson — multiple-choice quiz. Port of LessonScene from scenes.jsx.
// 5-item deck drawn from Lesson.items; on finish, mark lesson done.

import React, { useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  SafeAreaView,
} from 'react-native';
import { useNavigation, useRoute, type RouteProp } from '@react-navigation/native';
import * as Haptics from 'expo-haptics';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
} from 'react-native-reanimated';
import { colors, typography, spacing, radius } from '../theme/tokens';
import type { RootStackParamList } from '../navigation/types';
import { getLesson, type Lesson, type LessonItem } from '../data/lessons';
import { markLessonDone, bumpStreak } from '../data/progress';

type LessonRoute = RouteProp<RootStackParamList, 'Lesson'>;

type Card = {
  kal: string;
  rus: string;
  options: string[]; // 4 Kalmyk words, only one correct (== kal)
};

function shuffle<T>(arr: T[]): T[] {
  const out = arr.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function buildDeck(lesson: Lesson): Card[] {
  const pool = lesson.items;
  return shuffle(pool).slice(0, Math.min(5, pool.length)).map((correct) => {
    const distractors = shuffle(pool.filter((i) => i.kal !== correct.kal))
      .slice(0, 3)
      .map((d) => d.kal);
    const options = shuffle([correct.kal, ...distractors]);
    return { kal: correct.kal, rus: correct.rus, options };
  });
}

export default function LessonScreen() {
  const nav = useNavigation();
  const route = useRoute<LessonRoute>();
  const lesson = getLesson(route.params.lessonId);

  const [deck] = useState<Card[]>(() => (lesson ? buildDeck(lesson) : []));
  const [index, setIndex] = useState(0);
  const [picked, setPicked] = useState<string | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [done, setDone] = useState(false);

  const card = deck[index];
  const progress = useSharedValue(0);

  useEffect(() => {
    progress.value = withTiming(index / Math.max(1, deck.length), { duration: 300 });
  }, [index, deck.length, progress]);

  const progressStyle = useAnimatedStyle(() => ({
    width: `${progress.value * 100}%`,
  }));

  if (!lesson || !card) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text style={styles.lost}>Урок не найден</Text>
      </SafeAreaView>
    );
  }

  const pick = (opt: string) => {
    if (picked) return;
    setPicked(opt);
    const correct = opt === card.kal;
    if (correct) {
      setCorrectCount((c) => c + 1);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success).catch(() => {});
    } else {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning).catch(() => {});
    }
    setTimeout(() => {
      if (index + 1 >= deck.length) {
        finish(correct ? correctCount + 1 : correctCount);
      } else {
        setPicked(null);
        setIndex(index + 1);
      }
    }, 950);
  };

  const finish = async (finalCorrect: number) => {
    setDone(true);
    await markLessonDone(lesson.id);
    await bumpStreak();
  };

  if (done) {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.doneWrap}>
          <Text style={styles.doneKal}>Зөв!</Text>
          <Text style={styles.doneRus}>Урок пройден</Text>
          <Text style={styles.doneScore}>
            {correctCount} / {deck.length}
          </Text>
          <Pressable
            onPress={() => nav.goBack()}
            style={({ pressed }) => [styles.doneBtn, pressed && { opacity: 0.85 }]}
          >
            <Text style={styles.doneBtnText}>Эргх · Вернуться</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      {/* Top bar: back + progress + counter */}
      <View style={styles.topBar}>
        <Pressable onPress={() => nav.goBack()} style={styles.backBtn} hitSlop={10}>
          <Text style={styles.backText}>←</Text>
        </Pressable>
        <View style={styles.progressTrack}>
          <Animated.View style={[styles.progressBar, progressStyle]} />
        </View>
        <Text style={styles.counter}>
          {index + 1}/{deck.length}
        </Text>
      </View>

      {/* Question */}
      <View style={styles.qBlock}>
        <Text style={styles.qEyebrow}>выберите перевод</Text>
        <Text style={styles.qKal}>«{card.rus}»</Text>
        <Text style={styles.qHint}>Найдите калмыцкое слово</Text>
      </View>

      {/* Options grid */}
      <View style={styles.grid}>
        {card.options.map((opt) => {
          const isPicked = picked === opt;
          const isCorrect = picked && opt === card.kal;
          const isWrongPick = isPicked && opt !== card.kal;
          const showAsCorrect = picked && opt === card.kal;

          return (
            <Pressable
              key={opt}
              onPress={() => pick(opt)}
              disabled={!!picked}
              style={({ pressed }) => [
                styles.option,
                showAsCorrect && styles.optionCorrect,
                isWrongPick && styles.optionWrong,
                pressed && !picked && { transform: [{ scale: 0.98 }] },
              ]}
            >
              <Text style={[styles.optionText, showAsCorrect && { color: colors.white }]}>
                {opt}
              </Text>
            </Pressable>
          );
        })}
      </View>

      {picked && picked === card.kal && (
        <View style={styles.toast}>
          <Text style={styles.toastText}>✓ Зөв! · Правильно</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.cream },
  lost: { textAlign: 'center', marginTop: 80, color: colors.inkSoft },

  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingHorizontal: spacing.lg,
    marginTop: spacing.sm,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.hairline,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backText: { fontSize: 20, color: colors.ink },
  progressTrack: {
    flex: 1,
    height: 10,
    backgroundColor: colors.track,
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressBar: { height: '100%', backgroundColor: colors.clay, borderRadius: 5 },
  counter: {
    fontFamily: typography.mono,
    fontSize: 13,
    color: colors.inkSoft,
    letterSpacing: 0.5,
  },

  qBlock: { paddingHorizontal: spacing.lg, marginTop: spacing.xl },
  qEyebrow: {
    fontFamily: typography.mono,
    fontSize: 11,
    color: colors.inkSoft,
    letterSpacing: 2,
    textTransform: 'uppercase',
    marginBottom: 12,
  },
  qKal: {
    fontFamily: typography.sansBold,
    fontSize: 32,
    color: colors.ink,
    letterSpacing: -0.8,
    lineHeight: 36,
  },
  qHint: {
    fontFamily: typography.sans,
    fontSize: 14,
    color: colors.inkSoft,
    marginTop: 8,
  },

  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.lg,
    marginTop: spacing.xl,
    gap: 12,
  },
  option: {
    width: '48%',
    minHeight: 90,
    borderRadius: radius.lg,
    borderWidth: 2,
    borderColor: colors.hairline,
    backgroundColor: colors.white,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 12,
  },
  optionCorrect: {
    backgroundColor: colors.clay,
    borderColor: colors.clay,
  },
  optionWrong: {
    borderColor: colors.danger,
    backgroundColor: '#F9E4E4',
  },
  optionText: {
    fontFamily: typography.sansBold,
    fontSize: 20,
    color: colors.ink,
    letterSpacing: -0.4,
    textAlign: 'center',
  },

  toast: {
    position: 'absolute',
    alignSelf: 'center',
    bottom: 80,
    backgroundColor: colors.clay,
    paddingVertical: 12,
    paddingHorizontal: 22,
    borderRadius: radius.pill,
  },
  toastText: {
    color: colors.white,
    fontFamily: typography.sansBold,
    fontSize: 16,
  },

  doneWrap: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: spacing.lg, gap: 8 },
  doneKal: {
    fontFamily: typography.sansBold,
    fontSize: 72,
    color: colors.clay,
    letterSpacing: -2,
    lineHeight: 76,
  },
  doneRus: {
    fontFamily: typography.sansMed,
    fontSize: 18,
    color: colors.inkSoft,
    marginTop: 2,
  },
  doneScore: {
    marginTop: 28,
    fontFamily: typography.sansBold,
    fontSize: 54,
    color: colors.ink,
    letterSpacing: -1,
  },
  doneBtn: {
    marginTop: 36,
    paddingVertical: 16,
    paddingHorizontal: 32,
    backgroundColor: colors.ink,
    borderRadius: radius.lg,
  },
  doneBtnText: {
    color: colors.white,
    fontFamily: typography.sansBold,
    fontSize: 16,
  },
});
