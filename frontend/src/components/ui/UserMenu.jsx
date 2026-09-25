import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { Avatar } from '@/components/ui/Avatar';
import { Icon } from '@/components/ui/Icon';
import { useAuth } from '@/hooks/useAuth';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { useTheme } from '@/hooks/useTheme';
import { ROUTES } from '@/utils/constants';

function firstName(fullName) {
  return (fullName ?? '').trim().split(/\s+/)[0] ?? '';
}

export function UserMenu() {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const isMobile = useIsMobile();
  const navigate = useNavigate();

  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef(null);
  const panelRef = useRef(null);

  function close() {
    setIsOpen(false);
  }

  // A menu that survives a click elsewhere or an Escape feels broken.
  // The panel may live in a portal, so both roots are checked.
  useEffect(() => {
    if (!isOpen) return undefined;

    function handlePointerDown(event) {
      const insidePanel = panelRef.current?.contains(event.target);
      const onTrigger = triggerRef.current?.contains(event.target);
      if (!insidePanel && !onTrigger) close();
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        close();
        triggerRef.current?.focus();
      }
    }

    document.addEventListener('mousedown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  // As a sheet, the menu would otherwise let the page scroll behind it.
  useEffect(() => {
    if (!isOpen || !isMobile) return undefined;

    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previous;
    };
  }, [isOpen, isMobile]);

  function go(route) {
    close();
    navigate(route);
  }

  async function handleLogout() {
    close();
    await logout();
    navigate(ROUTES.LANDING, { replace: true });
  }

  const panel = (
    <div
      ref={panelRef}
      role="menu"
      className={isMobile ? 'climora-sheet' : 'climora-menu'}
      aria-label="Menu da conta"
    >
      {isMobile ? <span className="climora-sheet__handle" aria-hidden="true" /> : null}

      <div className="climora-menu__header">
        <Avatar name={user?.name} imageUrl={user?.avatar_url} size={44} />
        <div className="overflow-hidden">
          <span className="d-block text-truncate" style={{ fontWeight: 'var(--weight-medium)' }}>
            {user?.name}
          </span>
          <span
            className="d-block text-truncate"
            style={{ fontSize: 'var(--text-sm)', color: 'var(--content-muted)' }}
            title={user?.email}
          >
            {user?.email}
          </span>
        </div>
      </div>

      <MenuItem icon="account" label="Minha conta" onClick={() => go(ROUTES.PROFILE)} />
      <MenuItem
        icon={isDark ? 'sun' : 'moon'}
        label={isDark ? 'Tema claro' : 'Tema escuro'}
        onClick={toggleTheme}
      />

      <hr className="climora-menu__separator" />

      <MenuItem icon="logout" label="Sair" onClick={handleLogout} isDanger />
    </div>
  );

  return (
    <div className="position-relative">
      <button
        ref={triggerRef}
        type="button"
        className="btn-climora btn-climora--ghost btn-climora--pill ps-1 pe-2 pe-sm-3"
        style={{ background: isOpen ? 'var(--surface-sunken)' : 'transparent' }}
        onClick={() => setIsOpen((current) => !current)}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        aria-label="Menu da conta"
      >
        <Avatar name={user?.name} imageUrl={user?.avatar_url} size={32} />
        <span
          className="d-none d-sm-inline"
          style={{ fontWeight: 'var(--weight-medium)', color: 'var(--content-primary)' }}
        >
          {firstName(user?.name)}
        </span>
        <span className="d-none d-sm-flex" style={{ color: 'var(--content-muted)' }}>
          <Icon name={isOpen ? 'chevron-up' : 'chevron-down'} size={14} />
        </span>
      </button>

      {isOpen && !isMobile ? panel : null}

      {/* The navbar's backdrop-filter makes it a containing block, so a
          fixed-position sheet nested inside it anchors to the navbar rather
          than to the viewport. A portal escapes that entirely. */}
      {isOpen && isMobile
        ? createPortal(
            <>
              <div className="climora-scrim climora-scrim--sheet" onClick={close} aria-hidden="true" />
              {panel}
            </>,
            document.body,
          )
        : null}
    </div>
  );
}

function MenuItem({ icon, label, onClick, isDanger = false }) {
  return (
    <button
      type="button"
      role="menuitem"
      className={`climora-menu__item${isDanger ? ' climora-menu__item--danger' : ''}`}
      onClick={onClick}
    >
      <Icon name={icon} size={17} />
      {label}
    </button>
  );
}
