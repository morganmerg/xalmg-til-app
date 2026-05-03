// Bilingual text — Kalmyk on top, Russian below. Core pattern of the app UI
// (Өдрин үг · Слово дня, Зөв! · Правильно, Эклий · Начать урок).

import React from 'react';
import { View, Text, StyleSheet, TextStyle, ViewStyle } from 'react-native';
import { colors, typography } from './tokens';

type Props = {
  kal: string;
  rus?: string;
  size?: number;
  align?: 'left' | 'center' | 'right';
  kalStyle?: TextStyle;
  rusStyle?: TextStyle;
  inline?: boolean;          // "Kal · Rus" on a single line
  mutedRus?: boolean;        // dim Russian (secondary)
  style?: ViewStyle;
};

export function BilingualText({
  kal,
  rus,
  size = 20,
  align = 'left',
  kalStyle,
  rusStyle,
  inline = false,
  mutedRus = true,
  style,
}: Props) {
  if (inline && rus) {
    return (
      <Text
        style={[
          {
            fontFamily: typography.sansBold,
            fontSize: size,
            color: colors.ink,
            textAlign: align,
            letterSpacing: -0.4,
          },
          kalStyle,
        ]}
      >
        {kal}
        <Text style={{ color: colors.inkSoft, fontFamily: typography.sansMed }}> · {rus}</Text>
      </Text>
    );
  }
  return (
    <View style={[{ alignItems: align === 'center' ? 'center' : align === 'right' ? 'flex-end' : 'flex-start' }, style]}>
      <Text
        style={[
          {
            fontFamily: typography.sansBold,
            fontSize: size,
            color: colors.ink,
            letterSpacing: -0.4,
            lineHeight: size * 1.1,
          },
          kalStyle,
        ]}
      >
        {kal}
      </Text>
      {rus ? (
        <Text
          style={[
            {
              fontFamily: typography.sansMed,
              fontSize: Math.max(12, size * 0.58),
              color: mutedRus ? colors.inkSoft : colors.ink,
              marginTop: 2,
              letterSpacing: 0,
            },
            rusStyle,
          ]}
        >
          {rus}
        </Text>
      ) : null}
    </View>
  );
}

// Eyebrow kicker: JetBrains Mono, uppercase, spaced
export function Eyebrow({
  children,
  color,
  style,
}: {
  children: React.ReactNode;
  color?: string;
  style?: TextStyle;
}) {
  return (
    <Text
      style={[
        {
          fontFamily: typography.mono,
          fontSize: 11,
          letterSpacing: 2,
          textTransform: 'uppercase',
          color: color ?? colors.inkSoft,
        },
        style,
      ]}
    >
      {children}
    </Text>
  );
}

const _unused = StyleSheet.create({}); // keeps RN import side-effect parity
