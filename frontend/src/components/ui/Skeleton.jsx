export function Skeleton({ height = 20, width = '100%', radius = 'var(--radius-sm)' }) {
  return (
    <span
      className="climora-skeleton d-block"
      style={{ height, width, borderRadius: radius }}
      aria-hidden="true"
    />
  );
}
