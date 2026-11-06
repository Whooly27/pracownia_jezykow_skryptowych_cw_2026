import React from 'react';

export type TypographyVariant = 'h1' | 'h2' | 'body' | 'caption' | 'link';
export type TypographyColor = 'default' | 'variant' | 'primary' | 'error';

export interface TypographyProps {
  variant?: TypographyVariant;
  color?: TypographyColor;
  as?: React.ElementType;
  children: React.ReactNode;
  className?: string;
  id?: string;
  style?: React.CSSProperties;
  onClick?: (event: React.MouseEvent<HTMLElement>) => void;
}
