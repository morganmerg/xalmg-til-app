// iOS 26 liquid-glass pill — blur + tint + shine
// Port of IOSGlassPill from ios-frame.jsx

import React from 'react';
import { View, StyleSheet, ViewStyle, Platform } from 'react-native';
import { BlurView } from 'expo-blur';

type Props = {
  children?: React.ReactNode;
  dark?: boolean;
  style?: ViewStyle;
  height?: number;
  minWidth?: number;
};

export function GlassPill({ children, dark = false, style, height = 44, minWidth = 44 }: Props) {
  return (
    <View
      style={[
        styles.pill,
        { height, minWidth, borderRadius: height / 2 },
        dark ? styles.shadowDark : styles.shadowLight,
        style,
      ]}
    >
      <BlurView
        tint={dark ? 'dark' : 'light'}
        intensity={Platform.OS === 'ios' ? 40 : 20}
        style={[StyleSheet.absoluteFillObject, { borderRadius: height / 2 }]}
      />
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          {
            borderRadius: height / 2,
            backgroundColor: dark ? 'rgba(120,120,128,0.28)' : 'rgba(255,255,255,0.5)',
          },
        ]}
      />
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          {
            borderRadius: height / 2,
            borderWidth: 0.5,
            borderColor: dark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.06)',
          },
        ]}
      />
      <View style={styles.inner}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  inner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    zIndex: 1,
  },
  shadowLight: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.06,
    shadowRadius: 10,
    elevation: 3,
  },
  shadowDark: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 6,
  },
});
