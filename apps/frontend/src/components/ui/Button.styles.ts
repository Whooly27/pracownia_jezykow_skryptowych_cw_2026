import { ButtonSize, ButtonVariant } from './Button.types';

export const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 select-none cursor-pointer active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed';

export const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-xs gap-1.5',
  md: 'px-4 py-2.5 text-sm gap-2',
  lg: 'px-6 py-3 text-base gap-2.5',
};

export const variantStyles: Record<ButtonVariant, string> = {
  primary: 'bg-[#0061FE] text-white hover:bg-[#0052D4]',
  secondary: 'bg-[#141827] text-white hover:bg-[#2D3247]',
  outline: 'bg-transparent border border-[#E2E8F0] text-[#1E1E1E] hover:bg-[#F7F9FA]',
  ghost: 'bg-transparent text-[#1E1E1E] hover:bg-[#F7F9FA]',
};
