import { Icon } from '@/components/ui/Icon';

const VARIANTS = {
  primary: 'btn-climora--primary',
  secondary: 'btn-climora--secondary',
  ghost: 'btn-climora--ghost',
  danger: 'btn-climora--danger',
};

/**
 * Every button in the product. Variants describe intent, not appearance, so a
 * change of visual direction lands in one stylesheet.
 */
export function Button({
  children,
  variant = 'secondary',
  size,
  pill = false,
  icon,
  iconEnd,
  isLoading = false,
  loadingLabel,
  className = '',
  disabled,
  ...rest
}) {
  const classes = [
    'btn-climora',
    VARIANTS[variant] ?? VARIANTS.secondary,
    pill ? 'btn-climora--pill' : '',
    size === 'lg' ? 'btn-climora--lg' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} disabled={disabled || isLoading} {...rest}>
      {isLoading ? (
        <>
          <span className="spinner-border spinner-border-sm" aria-hidden="true" />
          {loadingLabel ?? children}
        </>
      ) : (
        <>
          {icon ? <Icon name={icon} size={15} /> : null}
          {children}
          {iconEnd ? <Icon name={iconEnd} size={15} /> : null}
        </>
      )}
    </button>
  );
}

export function IconButton({ name, label, variant = 'ghost', size = 16, className = '', ...rest }) {
  const classes = [
    'btn-climora',
    'btn-climora--icon',
    VARIANTS[variant] ?? VARIANTS.ghost,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} aria-label={label} title={label} {...rest}>
      <Icon name={name} size={size} />
    </button>
  );
}
