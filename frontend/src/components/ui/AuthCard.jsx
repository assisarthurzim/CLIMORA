export function AuthCard({ title, subtitle, children, footer }) {
  return (
    <div className="container py-4 py-md-5">
      <div className="surface p-4 p-md-5 mx-auto" style={{ maxWidth: 440 }}>
        <h1 className="h4 fw-semibold mb-1">{title}</h1>
        <p className="small mb-4" style={{ color: 'var(--content-secondary)' }}>
          {subtitle}
        </p>
        {children}
        {footer ? <div className="text-center small mt-4">{footer}</div> : null}
      </div>
    </div>
  );
}
