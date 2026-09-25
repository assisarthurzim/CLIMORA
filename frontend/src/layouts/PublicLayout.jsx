import { Link, Outlet } from 'react-router-dom';
import { BrandMark } from '@/components/ui/BrandMark';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { useAuth } from '@/hooks/useAuth';
import { APP_NAME, ROUTES } from '@/utils/constants';

export function PublicLayout() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="app-shell">
      <header className="glass-surface mx-2 mx-md-3 mt-2 mt-md-3" style={{ borderRadius: 'var(--radius-lg)' }}>
        <nav className="container-fluid d-flex align-items-center justify-content-between gap-2 py-2 px-2 px-md-3">
          <BrandMark />
          <div className="d-flex align-items-center gap-2">
            <ThemeToggle />
            {isAuthenticated ? (
              <Link
                to={ROUTES.DASHBOARD}
                className="btn-climora btn-climora--primary btn-climora--pill text-decoration-none"
              >
                Ir para o painel
              </Link>
            ) : (
              <>
                <Link to={ROUTES.LOGIN} className="btn-climora btn-climora--ghost btn-climora--pill text-decoration-none">
                  Entrar
                </Link>
                <Link
                  to={ROUTES.REGISTER}
                  className="btn-climora btn-climora--primary btn-climora--pill text-decoration-none"
                >
                  Criar conta
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      <main className="app-shell__content">
        <Outlet />
      </main>

      <footer className="container py-4">
        <p className="mb-0 text-center small" style={{ color: 'var(--content-muted)' }}>
          {APP_NAME} · Dados meteorológicos de Open-Meteo e OpenStreetMap
        </p>
      </footer>
    </div>
  );
}
