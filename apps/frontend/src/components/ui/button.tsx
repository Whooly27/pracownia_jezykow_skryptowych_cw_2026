import React from 'react';
import { ButtonProps } from './Button.types';
import { baseStyles, sizeStyles, variantStyles } from './Button.styles';

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  className = '',
  ...props
}) => {
  const classes = [
    baseStyles,
    sizeStyles[size],
    variantStyles[variant],
    isLoading ? 'relative !text-transparent pointer-events-none' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button className={classes} disabled={disabled || isLoading} {...props}>
      {isLoading && (
        <span className="absolute inset-0 flex items-center justify-center">
          <span className="w-4 h-4 border-2 border-current border-r-transparent rounded-full animate-spin" />
        </span>
      )}
      {!isLoading && leftIcon}
      <span>{children}</span>
      {!isLoading && rightIcon}
    </button>
  );
};
