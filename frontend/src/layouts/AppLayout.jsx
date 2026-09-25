import { NavLink, Outlet } from 'react-router-dom';
import { BrandMark } from '@/components/ui/BrandMark';
import { Icon } from '@/components/ui/Icon';
import { UserMenu } from '@/components/ui/UserMenu';
import { ROUTES } from '@/utils/constants';

function NavItem({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className="btn-climora btn-climora--ghost btn-climora--pill text-decoration-none"
      style={({ isActive }) => ({
        background: isActive ? 'var(--surface-sunken)' : 'transparent',
        color: isActive ? 'var(--content-primary)' : 'var(--content-secondary)',
      })}
    >
      <Icon name={icon} size={16} />
      <span className="d-none d-sm-inline">{label}</span>
    </NavLink>
  );
}

export function AppLayout() {
  return (
    <div className="app-shell">
      <header className="glass-surface mx-2 mx-md-3 mt-2 mt-md-3" style={{ borderRadius: 'var(--radius-lg)' }}>
        <nav className="container-fluid d-flex align-items-center justify-content-between gap-2 py-2 px-2 px-md-3">
          <div className="d-flex align-items-center gap-2 gap-md-4 min-width-0">
            <BrandMark to={ROUTES.DASHBOARD} />
            <nav className="d-flex gap-1" aria-label="Seções">
              <NavItem to={ROUTES.DASHBOARD} icon="dashboard" label="Painel" />
              <NavItem to={ROUTES.ASSISTANT} icon="assistant" label="Assistente" />
            </nav>
          </div>
          <UserMenu />
        </nav>
      </header>

      <main className="app-shell__content">
        <Outlet />
      </main>
    </div>
  );
}
