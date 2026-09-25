import { useId } from 'react';

export function FormField({
  label,
  name,
  type = 'text',
  value,
  onChange,
  error,
  autoComplete,
  placeholder,
  required = true,
}) {
  const inputId = useId();
  const errorId = `${inputId}-error`;

  return (
    <div className="mb-3">
      <label htmlFor={inputId} className="form-label small fw-medium">
        {label}
      </label>
      <input
        id={inputId}
        name={name}
        type={type}
        className={`form-control${error ? ' is-invalid' : ''}`}
        value={value}
        onChange={onChange}
        autoComplete={autoComplete}
        placeholder={placeholder}
        required={required}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
      />
      {error ? (
        <div id={errorId} className="invalid-feedback d-block small">
          {error}
        </div>
      ) : null}
    </div>
  );
}
