const GRADIENTS = [
  'linear-gradient(135deg, #2f6fed, #7ea6f7)',
  'linear-gradient(135deg, #1f57cc, #4fb3d9)',
  'linear-gradient(135deg, #17429c, #6d8ff0)',
  'linear-gradient(135deg, #2f6fed, #f5b32e)',
  'linear-gradient(135deg, #3a5fd0, #9b7ef0)',
];

export function initialsOf(fullName) {
  const parts = (fullName ?? '').trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/** Stable per-name colour, so the same person always gets the same avatar. */
function gradientFor(name) {
  const seed = [...(name ?? '')].reduce((total, char) => total + char.charCodeAt(0), 0);
  return GRADIENTS[seed % GRADIENTS.length];
}

export function Avatar({ name, imageUrl, size = 34 }) {
  const style = {
    width: size,
    height: size,
    fontSize: size * 0.38,
    borderRadius: '50%',
    background: imageUrl ? `center / cover url(${imageUrl})` : gradientFor(name),
    color: '#ffffff',
    fontWeight: 600,
    letterSpacing: '0.02em',
    boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.18)',
  };

  return (
    <span
      className="d-inline-flex align-items-center justify-content-center flex-shrink-0"
      style={style}
      aria-hidden="true"
    >
      {imageUrl ? null : initialsOf(name)}
    </span>
  );
}
