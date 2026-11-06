import React, { forwardRef } from 'react';
import { InputProps } from './Input.types';
import { inputStyles, getInputClasses } from './Input.styles';

export const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  fullWidth = true,
  className = '',
  id,
  ...props
}, ref) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className={`${fullWidth ? 'w-full' : 'w-auto'} flex flex-col`}>
      {label && (
        <label htmlFor={inputId} className={inputStyles.label}>
          {label}
        </label>
      )}

      <input
        ref={ref}
        id={inputId}
        className={getInputClasses(!!error, className)}
        {...props}
      />

      {error && <span className={inputStyles.errorText}>{error}</span>}
      {!error && helperText && <span className={inputStyles.helper}>{helperText}</span>}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
