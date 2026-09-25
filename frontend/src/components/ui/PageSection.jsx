export function PageSection({ children, className = '' }) {
  return (
    <section className={`container py-5 ${className}`.trim()}>{children}</section>
  );
}
