import { Link } from 'react-router-dom';
import { PageSection } from '@/components/ui/PageSection';
import { ROUTES } from '@/utils/constants';

export function NotFoundPage() {
  return (
    <PageSection className="text-center">
      <h1 className="display-6 fw-semibold mb-2">Página não encontrada</h1>
      <p className="mb-4" style={{ color: 'var(--content-secondary)' }}>
        O endereço acessado não existe no Climora.
      </p>
      <Link to={ROUTES.LANDING} className="btn-climora btn-climora--secondary btn-climora--pill text-decoration-none">
        Voltar ao início
      </Link>
    </PageSection>
  );
}
