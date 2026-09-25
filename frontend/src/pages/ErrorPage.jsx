import { Link, useRouteError } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';

const MESSAGES = {
  404: 'O endereço acessado não existe no Climora.',
  401: 'Você precisa entrar para ver esta página.',
  403: 'Você não tem permissão para acessar esta página.',
};

const FALLBACK_MESSAGE = 'Ocorreu um erro inesperado ao carregar esta página.';

export function ErrorPage() {
  const error = useRouteError();
  const status = error?.status;

  return (
    <div className="app-shell">
      <div className="container py-5 text-center my-auto">
        <p
          className="fw-semibold mb-2"
          style={{ fontSize: 'var(--text-3xl)', color: 'var(--content-muted)' }}
        >
          {status ?? 'Erro'}
        </p>
        <h1 className="h4 fw-semibold mb-2">Não conseguimos abrir esta página</h1>
        <p className="mb-4 mx-auto" style={{ maxWidth: 440, color: 'var(--content-secondary)' }}>
          {MESSAGES[status] ?? FALLBACK_MESSAGE}
        </p>
        <Link
          to={ROUTES.LANDING}
          className="btn-climora btn-climora--primary btn-climora--pill text-decoration-none"
        >
          Voltar ao início
        </Link>
      </div>
    </div>
  );
}
