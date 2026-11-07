import { COLORS } from '@/values/colors';

export const buttonVariants = {
  variant: {
    primary: `bg-[${COLORS.primary.main}] text-[${COLORS.primary.onPrimary}] hover:opacity-90 active:opacity-100 shadow-sm`,
    outline: `bg-transparent text-[${COLORS.surface.onSurface}] border border-[${COLORS.outline.default}] hover:bg-[${COLORS.surface.variant}] active:bg-[${COLORS.outline.default}]`,
    secondary: `bg-[${COLORS.secondary.container}] text-[${COLORS.secondary.onContainer}] hover:bg-[${COLORS.outline.default}] active:opacity-90`,
    ghost: `bg-transparent text-[${COLORS.surface.onSurface}] hover:bg-[${COLORS.surface.variant}] active:bg-[${COLORS.outline.default}]`,
    gradient: `bg-gradient-to-r from-[#0061FE] to-[#0044B3] text-white hover:opacity-95 active:opacity-90 shadow-md hover:shadow-lg transition-all`,
  },
  size: {
    sm: 'px-3 py-1.5 text-xs font-medium rounded-md',
    md: 'px-4 py-2 text-sm font-semibold rounded-lg',
    lg: 'px-6 py-3 text-base font-semibold rounded-xl',
  },
} as const;

export type ButtonVariant = keyof typeof buttonVariants.variant;
export type ButtonSize = keyof typeof buttonVariants.size;

export const getButtonClasses = (
  variant: ButtonVariant = 'primary',
  size: ButtonSize = 'md',
  extraClasses: string = ''
): string => {
  return [
    'inline-flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none cursor-pointer',
    buttonVariants.variant[variant],
    buttonVariants.size[size],
    extraClasses,
  ]
    .filter(Boolean)
    .join(' ');
};
