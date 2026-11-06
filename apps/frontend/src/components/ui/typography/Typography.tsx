import React from 'react';
import { TypographyProps } from './Typography.types';
import { getTypographyClasses } from './Typography.styles';

export const Typography: React.FC<TypographyProps> = ({
  variant = 'body',
  color,
  as: Component = 'div',
  children,
  className = '',
  ...props
}) => {
  const computedClasses = getTypographyClasses(variant, color, className);

  return (
    <Component className={computedClasses} {...props}>
      {children}
    </Component>
  );
};

export default Typography;
