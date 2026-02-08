# タスク001：プロジェクト基盤セットアップ

**ステータス:** 未着手
**優先度:** 高
**ブランチ:** TBD
**壁打ち日:** 2026-01-05

---

## 概要

Expo (Managed Workflow) への移行に向けて、app_expo プロジェクトの基盤を構築する。bulletproof-react のディレクトリ構造、デザイントークン、共通UIコンポーネント、必要なライブラリの導入を行う。

---

## 背景

### 現状の問題

- app_expo は Expo テンプレートの初期状態のまま
- 既存プロジェクトは native-base v2 に深く依存（339ファイル）
- react-navigation v1 の古いパターンを使用
- 設計思想が統一されていない

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **設計思想** | bulletproof-react に準拠 |
| **UIスタイリング** | 素のReact Native（StyleSheet）+ 必要最小限のライブラリ |
| **コンポーネント設計** | 最小限のベースライブラリ + 自作コンポーネント |
| **テーマシステム** | デザイントークン（定数ファイル） |
| **TypeScript** | strict: true（最も厳格） |

---

## ディレクトリ構造

```
app_expo/
├── app/                          # Expo Router（ルーティング）
│   ├── (tabs)/                   # タブナビゲーション
│   ├── (auth)/                   # 認証フロー
│   ├── (modals)/                 # モーダル画面
│   └── _layout.tsx               # ルートレイアウト
├── src/
│   ├── components/               # 共通UIコンポーネント
│   │   ├── ui/                   # 基本UIコンポーネント
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.styles.ts
│   │   │   │   └── index.ts
│   │   │   ├── Text/
│   │   │   ├── Input/
│   │   │   ├── Card/
│   │   │   ├── Badge/
│   │   │   ├── Spinner/
│   │   │   ├── Modal/
│   │   │   ├── ListItem/
│   │   │   └── index.ts          # バレルエクスポート
│   │   ├── feedback/             # フィードバック系
│   │   │   ├── Toast/
│   │   │   └── index.ts
│   │   ├── layouts/              # レイアウトコンポーネント
│   │   │   ├── Screen/
│   │   │   ├── Container/
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── features/                 # 機能単位のモジュール
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   ├── timeline/
│   │   ├── areas/
│   │   ├── results/
│   │   ├── mypage/
│   │   └── ...
│   ├── hooks/                    # 共通カスタムフック
│   │   ├── useAppState.ts
│   │   ├── useKeyboard.ts
│   │   └── index.ts
│   ├── stores/                   # Redux Toolkit (グローバル)
│   │   ├── index.ts              # Store設定
│   │   ├── rootReducer.ts
│   │   └── middleware.ts
│   ├── services/                 # API通信
│   │   ├── api/
│   │   │   ├── client.ts         # Axios設定
│   │   │   ├── endpoints.ts
│   │   │   └── types.ts
│   │   └── index.ts
│   ├── utils/                    # ユーティリティ
│   │   ├── date.ts
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   └── index.ts
│   ├── config/                   # 設定・定数
│   │   ├── theme/
│   │   │   ├── colors.ts
│   │   │   ├── spacing.ts
│   │   │   ├── typography.ts
│   │   │   ├── shadows.ts
│   │   │   └── index.ts
│   │   ├── constants.ts
│   │   └── env.ts
│   └── types/                    # グローバル型定義
│       ├── navigation.ts
│       ├── api.ts
│       └── index.ts
├── assets/                       # 静的アセット
│   ├── images/
│   ├── fonts/
│   └── icons/
├── app.json                      # Expo設定
├── app.config.ts                 # Expo設定（動的）
├── tsconfig.json
├── babel.config.js
└── package.json
```

---

## 導入ライブラリ一覧

### 必須ライブラリ

| ライブラリ | バージョン | 用途 |
|-----------|----------|------|
| `expo` | ~54.x | Expoフレームワーク |
| `expo-router` | ~6.x | ファイルベースルーティング |
| `react-native-reanimated` | ~4.x | アニメーション |
| `react-native-gesture-handler` | ~2.x | ジェスチャー |
| `react-native-screens` | ~4.x | ネイティブスクリーン |
| `react-native-safe-area-context` | ~5.x | セーフエリア |

### UIコンポーネント系

| ライブラリ | バージョン | 用途 |
|-----------|----------|------|
| `@expo/vector-icons` | ~15.x | アイコン |
| `expo-image` | ~2.x | 高性能画像表示 |
| `react-native-toast-message` | ^2.x | Toast通知 |
| `@gorhom/bottom-sheet` | ^4.x | BottomSheet / ActionSheet |

### フォーム・バリデーション

| ライブラリ | バージョン | 用途 |
|-----------|----------|------|
| `react-hook-form` | ^7.x | フォーム管理 |
| `zod` | ^3.x | バリデーション |
| `@hookform/resolvers` | ^3.x | zodとの統合 |

### 画像・メディア

| ライブラリ | バージョン | 用途 |
|-----------|----------|------|
| `react-native-awesome-gallery` | ^0.4.x | 画像ズームビューア |

### 状態管理（タスク2で詳細）

| ライブラリ | バージョン | 用途 |
|-----------|----------|------|
| `@reduxjs/toolkit` | ^2.x | Redux Toolkit |
| `react-redux` | ^9.x | React Redux |

---

## デザイントークン設計

### colors.ts

```typescript
// src/config/theme/colors.ts

export const colors = {
  // Primary
  primary: {
    50: '#E3F2FD',
    100: '#BBDEFB',
    200: '#90CAF9',
    300: '#64B5F6',
    400: '#42A5F5',
    500: '#2196F3',  // メインカラー
    600: '#1E88E5',
    700: '#1976D2',
    800: '#1565C0',
    900: '#0D47A1',
  },

  // Neutral (Gray)
  neutral: {
    0: '#FFFFFF',
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
    1000: '#000000',
  },

  // Semantic
  success: {
    light: '#81C784',
    main: '#4CAF50',
    dark: '#388E3C',
  },
  warning: {
    light: '#FFB74D',
    main: '#FF9800',
    dark: '#F57C00',
  },
  error: {
    light: '#E57373',
    main: '#F44336',
    dark: '#D32F2F',
  },
  info: {
    light: '#64B5F6',
    main: '#2196F3',
    dark: '#1976D2',
  },

  // Background
  background: {
    primary: '#FFFFFF',
    secondary: '#F5F5F5',
    tertiary: '#EEEEEE',
  },

  // Text
  text: {
    primary: '#212121',
    secondary: '#757575',
    disabled: '#BDBDBD',
    inverse: '#FFFFFF',
  },

  // Border
  border: {
    light: '#E0E0E0',
    main: '#BDBDBD',
    dark: '#9E9E9E',
  },
} as const;

export type Colors = typeof colors;
```

### spacing.ts

```typescript
// src/config/theme/spacing.ts

export const spacing = {
  none: 0,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
} as const;

export type Spacing = typeof spacing;
```

### typography.ts

```typescript
// src/config/theme/typography.ts

import { Platform } from 'react-native';

const fontFamily = Platform.select({
  ios: 'System',
  android: 'Roboto',
  default: 'System',
});

export const typography = {
  fontFamily: {
    regular: fontFamily,
    medium: fontFamily,
    bold: fontFamily,
  },

  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
  },

  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },

  fontWeight: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },
} as const;

export type Typography = typeof typography;
```

### shadows.ts

```typescript
// src/config/theme/shadows.ts

import { Platform } from 'react-native';

export const shadows = {
  none: {},
  sm: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.18,
      shadowRadius: 1.0,
    },
    android: {
      elevation: 1,
    },
    default: {},
  }),
  md: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.22,
      shadowRadius: 2.22,
    },
    android: {
      elevation: 3,
    },
    default: {},
  }),
  lg: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.30,
      shadowRadius: 4.65,
    },
    android: {
      elevation: 8,
    },
    default: {},
  }),
  xl: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.44,
      shadowRadius: 10.32,
    },
    android: {
      elevation: 16,
    },
    default: {},
  }),
} as const;

export type Shadows = typeof shadows;
```

---

## 共通UIコンポーネント仕様

### 1. Button

```typescript
// src/components/ui/Button/Button.tsx

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { colors, spacing, typography } from '@/config/theme';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  onPress?: () => void;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
  onPress,
  style,
  textStyle,
}) => {
  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      style={[
        styles.base,
        styles[variant],
        styles[`size_${size}`],
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        style,
      ]}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === 'primary' ? colors.text.inverse : colors.primary[500]}
          size="small"
        />
      ) : (
        <Text
          style={[
            styles.text,
            styles[`text_${variant}`],
            styles[`text_${size}`],
            textStyle,
          ]}
        >
          {children}
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },

  // Variants
  primary: {
    backgroundColor: colors.primary[500],
  },
  secondary: {
    backgroundColor: colors.neutral[200],
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.primary[500],
  },
  ghost: {
    backgroundColor: 'transparent',
  },

  // Sizes
  size_sm: {
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.sm,
    minHeight: 32,
  },
  size_md: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    minHeight: 44,
  },
  size_lg: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    minHeight: 56,
  },

  // States
  disabled: {
    opacity: 0.5,
  },
  fullWidth: {
    width: '100%',
  },

  // Text
  text: {
    fontWeight: typography.fontWeight.semibold,
  },
  text_primary: {
    color: colors.text.inverse,
  },
  text_secondary: {
    color: colors.text.primary,
  },
  text_outline: {
    color: colors.primary[500],
  },
  text_ghost: {
    color: colors.primary[500],
  },
  text_sm: {
    fontSize: typography.fontSize.sm,
  },
  text_md: {
    fontSize: typography.fontSize.md,
  },
  text_lg: {
    fontSize: typography.fontSize.lg,
  },
});
```

### 2. Text

```typescript
// src/components/ui/Text/Text.tsx

import React from 'react';
import { Text as RNText, TextStyle, StyleSheet } from 'react-native';
import { colors, typography } from '@/config/theme';

type TextVariant = 'h1' | 'h2' | 'h3' | 'body' | 'bodySmall' | 'caption' | 'label';
type TextColor = 'primary' | 'secondary' | 'disabled' | 'inverse' | 'error' | 'success';

interface TextProps {
  children: React.ReactNode;
  variant?: TextVariant;
  color?: TextColor;
  weight?: keyof typeof typography.fontWeight;
  align?: 'left' | 'center' | 'right';
  numberOfLines?: number;
  style?: TextStyle;
}

export const Text: React.FC<TextProps> = ({
  children,
  variant = 'body',
  color = 'primary',
  weight,
  align = 'left',
  numberOfLines,
  style,
}) => {
  return (
    <RNText
      style={[
        styles.base,
        styles[variant],
        { color: colorMap[color] },
        weight && { fontWeight: typography.fontWeight[weight] },
        { textAlign: align },
        style,
      ]}
      numberOfLines={numberOfLines}
    >
      {children}
    </RNText>
  );
};

const colorMap: Record<TextColor, string> = {
  primary: colors.text.primary,
  secondary: colors.text.secondary,
  disabled: colors.text.disabled,
  inverse: colors.text.inverse,
  error: colors.error.main,
  success: colors.success.main,
};

const styles = StyleSheet.create({
  base: {
    fontFamily: typography.fontFamily.regular,
  },
  h1: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold,
    lineHeight: typography.fontSize['4xl'] * typography.lineHeight.tight,
  },
  h2: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
    lineHeight: typography.fontSize['3xl'] * typography.lineHeight.tight,
  },
  h3: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.semibold,
    lineHeight: typography.fontSize['2xl'] * typography.lineHeight.tight,
  },
  body: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.regular,
    lineHeight: typography.fontSize.md * typography.lineHeight.normal,
  },
  bodySmall: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.regular,
    lineHeight: typography.fontSize.sm * typography.lineHeight.normal,
  },
  caption: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.regular,
    lineHeight: typography.fontSize.xs * typography.lineHeight.normal,
  },
  label: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    lineHeight: typography.fontSize.sm * typography.lineHeight.normal,
  },
});
```

### 3. Input

```typescript
// src/components/ui/Input/Input.tsx

import React, { forwardRef } from 'react';
import {
  View,
  TextInput,
  StyleSheet,
  TextInputProps,
  ViewStyle,
} from 'react-native';
import { Text } from '../Text';
import { colors, spacing, typography } from '@/config/theme';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  hint?: string;
  disabled?: boolean;
  containerStyle?: ViewStyle;
}

export const Input = forwardRef<TextInput, InputProps>(
  ({ label, error, hint, disabled, containerStyle, style, ...props }, ref) => {
    const hasError = !!error;

    return (
      <View style={[styles.container, containerStyle]}>
        {label && (
          <Text variant="label" style={styles.label}>
            {label}
          </Text>
        )}
        <TextInput
          ref={ref}
          style={[
            styles.input,
            hasError && styles.inputError,
            disabled && styles.inputDisabled,
            style,
          ]}
          placeholderTextColor={colors.text.disabled}
          editable={!disabled}
          {...props}
        />
        {error && (
          <Text variant="caption" color="error" style={styles.message}>
            {error}
          </Text>
        )}
        {hint && !error && (
          <Text variant="caption" color="secondary" style={styles.message}>
            {hint}
          </Text>
        )}
      </View>
    );
  }
);

Input.displayName = 'Input';

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  label: {
    marginBottom: spacing.xs,
  },
  input: {
    height: 48,
    borderWidth: 1,
    borderColor: colors.border.main,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    fontSize: typography.fontSize.md,
    color: colors.text.primary,
    backgroundColor: colors.background.primary,
  },
  inputError: {
    borderColor: colors.error.main,
  },
  inputDisabled: {
    backgroundColor: colors.background.secondary,
    color: colors.text.disabled,
  },
  message: {
    marginTop: spacing.xs,
  },
});
```

### 4. Card

```typescript
// src/components/ui/Card/Card.tsx

import React from 'react';
import { View, StyleSheet, ViewStyle, Pressable } from 'react-native';
import { colors, spacing, shadows } from '@/config/theme';

interface CardProps {
  children: React.ReactNode;
  variant?: 'elevated' | 'outlined' | 'filled';
  padding?: keyof typeof spacing;
  onPress?: () => void;
  style?: ViewStyle;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'elevated',
  padding = 'md',
  onPress,
  style,
}) => {
  const content = (
    <View
      style={[
        styles.base,
        styles[variant],
        { padding: spacing[padding] },
        style,
      ]}
    >
      {children}
    </View>
  );

  if (onPress) {
    return (
      <Pressable onPress={onPress} style={({ pressed }) => [pressed && styles.pressed]}>
        {content}
      </Pressable>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  base: {
    borderRadius: 12,
    backgroundColor: colors.background.primary,
  },
  elevated: {
    ...shadows.md,
  },
  outlined: {
    borderWidth: 1,
    borderColor: colors.border.light,
  },
  filled: {
    backgroundColor: colors.background.secondary,
  },
  pressed: {
    opacity: 0.9,
  },
});
```

### 5. Toast設定

```typescript
// src/components/feedback/Toast/toastConfig.tsx

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from '../../ui/Text';
import { colors, spacing, shadows } from '@/config/theme';
import { BaseToastProps } from 'react-native-toast-message';

export const toastConfig = {
  success: ({ text1, text2 }: BaseToastProps) => (
    <View style={[styles.container, styles.success]}>
      <Text variant="label" color="inverse">{text1}</Text>
      {text2 && <Text variant="caption" color="inverse">{text2}</Text>}
    </View>
  ),
  error: ({ text1, text2 }: BaseToastProps) => (
    <View style={[styles.container, styles.error]}>
      <Text variant="label" color="inverse">{text1}</Text>
      {text2 && <Text variant="caption" color="inverse">{text2}</Text>}
    </View>
  ),
  info: ({ text1, text2 }: BaseToastProps) => (
    <View style={[styles.container, styles.info]}>
      <Text variant="label" color="inverse">{text1}</Text>
      {text2 && <Text variant="caption" color="inverse">{text2}</Text>}
    </View>
  ),
  warning: ({ text1, text2 }: BaseToastProps) => (
    <View style={[styles.container, styles.warning]}>
      <Text variant="label" style={{ color: colors.text.primary }}>{text1}</Text>
      {text2 && <Text variant="caption" style={{ color: colors.text.secondary }}>{text2}</Text>}
    </View>
  ),
};

const styles = StyleSheet.create({
  container: {
    width: '90%',
    padding: spacing.md,
    borderRadius: 8,
    ...shadows.lg,
  },
  success: {
    backgroundColor: colors.success.main,
  },
  error: {
    backgroundColor: colors.error.main,
  },
  info: {
    backgroundColor: colors.info.main,
  },
  warning: {
    backgroundColor: colors.warning.light,
  },
});
```

---

## 実装手順

### Phase 1: プロジェクト設定

- [ ] app_expo のディレクトリ構造を bulletproof-react に沿って作成
- [ ] tsconfig.json を strict: true に設定
- [ ] パスエイリアス（@/）を設定
- [ ] ESLint / Prettier 設定

### Phase 2: 依存ライブラリ導入

- [ ] 必須ライブラリのインストール（expo-image, react-native-toast-message, @gorhom/bottom-sheet等）
- [ ] react-hook-form + zod のインストール
- [ ] package.json の整理

### Phase 3: デザイントークン作成

- [ ] src/config/theme/colors.ts 作成
- [ ] src/config/theme/spacing.ts 作成
- [ ] src/config/theme/typography.ts 作成
- [ ] src/config/theme/shadows.ts 作成
- [ ] src/config/theme/index.ts でバレルエクスポート

### Phase 4: 共通UIコンポーネント作成

- [ ] Button コンポーネント
- [ ] Text コンポーネント
- [ ] Input コンポーネント
- [ ] Card コンポーネント
- [ ] Badge コンポーネント
- [ ] Spinner コンポーネント
- [ ] Modal コンポーネント
- [ ] ListItem コンポーネント
- [ ] Toast 設定（react-native-toast-message）
- [ ] BottomSheet 設定（@gorhom/bottom-sheet）

### Phase 5: レイアウトコンポーネント作成

- [ ] Screen コンポーネント（SafeArea + StatusBar）
- [ ] Container コンポーネント

### Phase 6: 動作確認

- [ ] 各コンポーネントの表示テスト
- [ ] TypeScript エラー: 0件確認

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|---------|
| `app_expo/tsconfig.json` | strict: true、パスエイリアス設定 |
| `app_expo/package.json` | 依存ライブラリ追加 |
| `app_expo/babel.config.js` | モジュールリゾルバー設定 |
| `app_expo/app.json` | Expo設定（必要に応じて） |

### 新規作成

| ファイル | 説明 |
|---------|------|
| `src/config/theme/*.ts` | デザイントークン |
| `src/components/ui/**/*.tsx` | UIコンポーネント |
| `src/components/feedback/**/*.tsx` | フィードバックコンポーネント |
| `src/components/layouts/**/*.tsx` | レイアウトコンポーネント |

---

## 確認事項

- [ ] TypeScriptエラー: 0件
- [ ] 全コンポーネントの表示確認
- [ ] パスエイリアス（@/）が正常に動作すること
- [ ] expo start で正常に起動すること

---

## 注意事項

- 既存プロジェクト（/app）のテーマ変数を参考に、新しいデザイントークンを作成する
- コンポーネントはシンプルに保ち、過度な抽象化を避ける
- 各コンポーネントは単体で動作確認できるようにする
- native-base からの移行時に参照しやすいよう、Props名は一般的な命名規則に従う

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| 1-1 | タスクの進め方 | A. ボトムアップ |
| 1-2 | UIライブラリの選定 | 素のReact Native（StyleSheet） |
| 1-3 | 状態管理の方針 | A. Redux Toolkit に移行 |
| 1-4 | コンポーネント設計方針 | B. 最小限のベースライブラリ + 自作 |
| 1-5 | デザイントークン/テーマシステム | A. デザイントークン（定数ファイル） |
| 1-6 | bulletproof-react ディレクトリ構造 | A. この構造でOK |
| 2-1 | 共通UIコンポーネントの範囲 | C. フルセット |
| 2-2 | デザイントークンの初期値 | C. 既存ベース + 整理 |
| 2-3 | TypeScript の厳格度 | A. strict: true |
| 2-4 | Toast ライブラリ | A. react-native-toast-message |
| 2-5 | ActionSheet / BottomSheet | A. @gorhom/bottom-sheet |
| 2-6 | Modal | A. React Native 標準 Modal |
| 2-7 | 画像表示 | A. expo-image |
| 2-8 | 画像ズームビューア | A. react-native-awesome-gallery |
| 2-9 | フォーム管理 | A. react-hook-form 継続 |
| 2-10 | バリデーション | A. zod |

### 設計方針

| 項目 | 決定 |
|------|------|
| 設計思想 | bulletproof-react |
| 移行アプローチ | Greenfield（新規プロジェクト作成 + 段階的移植） |

### 保留事項

| 項目 | 理由 |
|------|------|
| 具体的な色の値 | 既存プロジェクトのテーマを確認して決定 |
| アイコンセット | 既存プロジェクトで使用しているアイコンを確認して決定 |
