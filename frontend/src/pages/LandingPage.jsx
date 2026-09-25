import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PageSection } from '@/components/ui/PageSection';
import { systemService } from '@/services/systemService';
import { APP_NAME, APP_TAGLINE, ROUTES } from '@/utils/constants';

const STATUS_LABEL = {
  checking: 'Verificando conexão com a API…',
  online: 'API conectada',
  offline: 'API indisponível',
};

export function LandingPage() {
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    let active = true;
    systemService
      .getHealth()
      .then(() => active && setStatus('online'))
      .catch(() => active && setStatus('offline'));
    return () => {
      active = false;
    };
  }, []);

  return (
    <PageSection className="text-center">
      <p
        className="text-uppercase small fw-semibold mb-3"
        style={{ color: 'var(--accent)', letterSpacing: '0.08em' }}
      >
        Previsão, análise e recomendação
      </p>
      <h1 className="type-hero mb-3">
        {APP_NAME}
      </h1>
      <p className="fs-5 mb-4 mx-auto" style={{ maxWidth: 560, color: 'var(--content-secondary)' }}>
        {APP_TAGLINE}
      </p>

      <div className="d-flex flex-column flex-sm-row gap-2 justify-content-center mb-5">
        <Link
          to={ROUTES.REGISTER}
          className="btn-climora btn-climora--primary btn-climora--pill btn-climora--lg text-decoration-none"
        >
          Criar conta
        </Link>
        <Link
          to={ROUTES.LOGIN}
          className="btn-climora btn-climora--secondary btn-climora--pill btn-climora--lg text-decoration-none"
        >
          Entrar
        </Link>
      </div>

      <div
        className="glass-surface d-inline-flex align-items-center gap-2 px-3 py-2"
        style={{ borderRadius: 'var(--radius-pill)' }}
      >
        <span
          className="rounded-circle"
          style={{
            width: 8,
            height: 8,
            background:
              status === 'online'
                ? 'var(--positive)'
                : status === 'offline'
                  ? 'var(--danger)'
                  : 'var(--content-muted)',
          }}
        />
        <span className="small" style={{ color: 'var(--content-secondary)' }}>
          {STATUS_LABEL[status]}
        </span>
      </div>
    </PageSection>
  );
}
