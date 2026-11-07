import { COLORS } from '@/values/colors';
import {TypographyColor, TypographyVariant} from "@/components/ui/typography/Typography.types";

export const typographyStyles = {
  variant: {
    h1: `text-3xl md:text-4xl font-extrabold tracking-tight text-[${COLORS.surface.onSurface}]`,
    h2: `text-xl md:text-2xl font-bold tracking-tight text-[${COLORS.surface.onSurface}]`,
    body: `text-sm md:text-base text-[${COLORS.surface.onVariant}] leading-relaxed`,
    caption: `text-xs font-medium text-[${COLORS.surface.onVariant}]`,
    link: `text-xs font-semibold text-[${COLORS.primary.main}] hover:underline cursor-pointer transition-colors`,
  },
  color: {
    default: `text-[${COLORS.surface.onSurface}]`,
    variant: `text-[${COLORS.surface.onVariant}]`,
    primary: `text-[${COLORS.primary.main}]`,
    error: `text-[${COLORS.error.main}]`,
  },
} as const;

export const getTypographyClasses = (
  variant: TypographyVariant = 'body',
  color?: TypographyColor,
  className: string = ''
): string => {
  return [
    typographyStyles.variant[variant],
    color ? typographyStyles.color[color] : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');
};
