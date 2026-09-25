export function SectionCard({ title, description, children }) {
  return (
    <section className="surface p-3 p-md-4 mb-3 mb-md-4">
      <h2 className="h6 fw-medium mb-1">{title}</h2>
      {description ? (
        <p className="small mb-4" style={{ color: 'var(--content-secondary)' }}>
          {description}
        </p>
      ) : null}
      {children}
    </section>
  );
}
