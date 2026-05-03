// Design tokens for Хальмг Тиль — ported from pitch scenes.jsx
// Steppe palette: terracotta + ochre + cream + deep ink.
// oklch() originals preserved in comments; hex approximations used for RN.

export const colors = {
  // Accent
  clay:    '#C86B3E', // oklch(58% 0.14 40)  — terracotta
  clayDk:  '#A64B28', // oklch(48% 0.15 35)
  clayLt:  '#F4E1D2', // oklch(95% 0.04 70)  — active tile bg / chip
  ochre:   '#D4A04D', // oklch(72% 0.13 75)
  sky:     '#4A7FAE', // oklch(55% 0.09 235)

  // Neutrals
  cream:   '#FAF5E9', // oklch(97% 0.015 80) — page bg
  creamDk: '#F0EBDF', // ribbons, cards on cream
  ink:     '#2D2821', // oklch(22% 0.02 50)  — primary text
  inkSoft: '#6F6254', // oklch(45% 0.02 50)  — secondary text
  inkMute: '#AEA499', // oklch(70% 0.02 80)  — tertiary / icons
  hairline:'#E5E1D8', // oklch(90% 0.005 80) — borders
  track:   '#EAE5DD', // oklch(92% 0.01 80)  — progress bg

  // States
  white:   '#FFFFFF',
  black:   '#000000',
  danger:  '#B33A3A',
} as const;

export const typography = {
  // Loaded via @expo-google-fonts/inter and @expo-google-fonts/jetbrains-mono
  sans:    'Inter_400Regular',
  sansMed: 'Inter_500Medium',
  sansBold:'Inter_700Bold',
  mono:    'JetBrainsMono_400Regular',
  monoMed: 'JetBrainsMono_500Medium',
  // System fallbacks for iOS-native feel in nav
  systemBold: 'System', // maps to -apple-system/San Francisco
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 44,
} as const;

export const radius = {
  sm: 8,
  md: 16,
  lg: 20,
  xl: 28,
  pill: 999,
} as const;

// Shadow recipes mirroring scenes.jsx card depths.
export const shadow = {
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 4,
  },
  card2: {
    shadowColor: colors.clay,
    shadowOffset: { width: 0, height: 20 },
    shadowOpacity: 0.22,
    shadowRadius: 40,
    elevation: 10,
  },
  floating: {
    shadowColor: colors.clay,
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.35,
    shadowRadius: 30,
    elevation: 12,
  },
} as const;

// Grammar/POS tag → emoji hint used on lesson tiles
export const themeEmoji: Record<string, string> = {
  greetings: '👋',
  steppe:    '🐎',
  food:      '🍵',
  family:    '👨‍👩‍👧',
  numbers:   '🔢',
  nature:    '🌿',
  colors:    '🎨',
  body:      '🖐️',
};
