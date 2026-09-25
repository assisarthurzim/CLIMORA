import { Link } from 'react-router-dom';
import { AuthCard } from '@/components/ui/AuthCard';
import { ROUTES } from '@/utils/constants';

export function ForgotPasswordPage() {
  return (
    <AuthCard
      title="Esqueci minha senha"
      subtitle="A recuperação por e-mail depende da configuração de envio, ainda pendente."
      footer={<Link to={ROUTES.LOGIN}>Voltar para o login</Link>}
    >
      <p className="small mb-0" style={{ color: 'var(--content-secondary)' }}>
        Enquanto isso, entre em contato com o suporte para redefinir seu acesso.
      </p>
    </AuthCard>
  );
}
