// Ornament — stylised Kalmyk geometric pattern from scenes.jsx OrnamentTile
// Repeats as a subtle background texture. Built with react-native-svg.

import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import Svg, { G, Path, Circle, Defs, Pattern, Rect } from 'react-native-svg';
import { colors } from './tokens';

type Props = {
  color?: string;
  opacity?: number;
  size?: number;
  style?: ViewStyle;
  tint?: boolean; // overlay subtle cream
};

function OrnamentGlyph({ color, opacity }: { color: string; opacity: number }) {
  return (
    <G stroke={color} strokeWidth={1.2} fill="none" opacity={opacity}>
      <Path d="M30 10 L50 30 L30 50 L10 30 Z" />
      <Path d="M30 18 L42 30 L30 42 L18 30 Z" />
      <Path d="M2 2 L12 2 L12 8 L6 8 L6 12 L2 12 Z" />
      <Path d="M58 2 L48 2 L48 8 L54 8 L54 12 L58 12 Z" />
      <Path d="M2 58 L12 58 L12 52 L6 52 L6 48 L2 48 Z" />
      <Path d="M58 58 L48 58 L48 52 L54 52 L54 48 L58 48 Z" />
      <Circle cx={30} cy={30} r={1.5} fill={color} stroke="none" />
    </G>
  );
}

export function OrnamentTile({
  color = colors.clay,
  opacity = 0.18,
  size = 80,
  style,
}: Props) {
  return (
    <View style={[{ width: size, height: size }, style]}>
      <Svg width={size} height={size} viewBox="0 0 60 60">
        <OrnamentGlyph color={color} opacity={opacity} />
      </Svg>
    </View>
  );
}

// Full-bleed repeating ornamental background
export function OrnamentBG({
  color = colors.clay,
  opacity = 0.1,
  tileSize = 80,
  style,
}: Props & { tileSize?: number }) {
  return (
    <View pointerEvents="none" style={[StyleSheet.absoluteFillObject, style]}>
      <Svg width="100%" height="100%">
        <Defs>
          <Pattern
            id="orn"
            x={0}
            y={0}
            width={tileSize}
            height={tileSize}
            patternUnits="userSpaceOnUse"
          >
            <Svg width={tileSize} height={tileSize} viewBox="0 0 60 60">
              <OrnamentGlyph color={color} opacity={opacity} />
            </Svg>
          </Pattern>
        </Defs>
        <Rect width="100%" height="100%" fill="url(#orn)" />
      </Svg>
    </View>
  );
}
