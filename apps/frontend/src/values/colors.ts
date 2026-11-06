// src/values/colors.ts

export const COLORS = {
  primary: {
    main: '#0061FE',
    onPrimary: '#FFFFFF',
    container: '#EDF4FF',
    onContainer: '#001D6C',
  },
  secondary: {
    main: '#141827',
    onSecondary: '#FFFFFF',
    container: '#F1F5F9',
    onContainer: '#141827',
  },
  surface: {
    default: '#FFFFFF',
    onSurface: '#1E1E1E',
    variant: '#F7F9FA',
    onVariant: '#5E6C84',
  },
  outline: {
    default: '#E2E8F0',
    variant: '#8C9BAB',
  },
  error: {
    main: '#E11D48',
    onError: '#FFFFFF',
    container: '#FEE2E2',
    onContainer: '#991B1B',
  },
  status: {
    success: '#00875A',
    warning: '#FFAB00',
  },
} as const;

export type Colors = typeof COLORS;
