import { COLORS } from '@/values/colors';

export const inputStyles = {
  base: `w-full bg-[${COLORS.surface.default}] text-[${COLORS.surface.onSurface}] placeholder-[${COLORS.outline.variant}] text-sm rounded-lg px-4 py-3 transition-all duration-200 outline-none border border-[${COLORS.outline.default}] focus:border-[${COLORS.primary.main}] focus:ring-2 focus:ring-[${COLORS.primary.container}] disabled:bg-[${COLORS.surface.variant}] disabled:cursor-not-allowed`,
  error: `border-[${COLORS.error.main}] text-[${COLORS.error.main}] focus:border-[${COLORS.error.main}] focus:ring-[${COLORS.error.container}]`,
  label: `block text-xs font-semibold text-[${COLORS.surface.onSurface}] mb-1.5`,
  helper: `mt-1.5 text-xs text-[${COLORS.surface.onVariant}]`,
  errorText: `mt-1.5 text-xs text-[${COLORS.error.main}]`,
} as const;

export const getInputClasses = (hasError: boolean = false, className: string = ''): string => {
  return [
    inputStyles.base,
    hasError ? inputStyles.error : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');
};
