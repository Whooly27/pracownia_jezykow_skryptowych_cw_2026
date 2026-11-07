import React from 'react';
import { ButtonProps } from './Button.types';
import { getButtonClasses, ButtonVariant, ButtonSize } from './Button.styles';

export const Button: React.FC<ButtonProps & {
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
}> = ({
  variant,
  size,
  className,
  children,
  ...props
}) => {
  const computedClasses = getButtonClasses(variant, size, className);

  return (
    <button className={computedClasses} {...props}>
      {children}
    </button>
  );
};

export default Button;
