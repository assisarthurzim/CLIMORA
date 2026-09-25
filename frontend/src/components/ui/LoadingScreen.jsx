export function LoadingScreen({ label = 'Carregando…' }) {
  return (
    <div
      className="d-flex flex-column align-items-center justify-content-center gap-3"
      style={{ minHeight: '60vh' }}
    >
      <span className="spinner-border" style={{ color: 'var(--accent)' }} aria-hidden="true" />
      <span className="small" style={{ color: 'var(--content-secondary)' }}>
        {label}
      </span>
    </div>
  );
}
