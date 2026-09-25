import { useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { AlertMessage } from '@/components/ui/AlertMessage';
import { AuthCard } from '@/components/ui/AuthCard';
import { FormField } from '@/components/ui/FormField';
import { SubmitButton } from '@/components/ui/SubmitButton';
import { useAuth } from '@/hooks/useAuth';
import { useForm } from '@/hooks/useForm';
import { ROUTES } from '@/utils/constants';

const INITIAL_VALUES = { email: '', password: '', rememberMe: false };

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const destination = location.state?.from ?? ROUTES.DASHBOARD;

  const submit = useCallback(
    async (values) => {
      await login(values);
      navigate(destination, { replace: true });
    },
    [login, navigate, destination],
  );

  const { values, fieldErrors, formError, isSubmitting, handleChange, handleSubmit } = useForm(
    INITIAL_VALUES,
    submit,
  );

  return (
    <AuthCard
      title="Entrar"
      subtitle="Acesse seu painel e acompanhe o clima das suas cidades."
      footer={
        <span style={{ color: 'var(--content-secondary)' }}>
          Ainda não tem conta? <Link to={ROUTES.REGISTER}>Criar conta</Link>
        </span>
      }
    >
      <AlertMessage message={formError} />

      <form onSubmit={handleSubmit} noValidate>
        <FormField
          label="E-mail"
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          error={fieldErrors.email}
          autoComplete="email"
          placeholder="voce@exemplo.com"
        />
        <FormField
          label="Senha"
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          error={fieldErrors.password}
          autoComplete="current-password"
        />

        <div className="d-flex align-items-center justify-content-between mb-4">
          <div className="form-check mb-0">
            <input
              id="remember-me"
              name="rememberMe"
              type="checkbox"
              className="form-check-input"
              checked={values.rememberMe}
              onChange={handleChange}
            />
            <label htmlFor="remember-me" className="form-check-label small">
              Lembrar-me
            </label>
          </div>
          <Link to={ROUTES.FORGOT_PASSWORD} className="small">
            Esqueci minha senha
          </Link>
        </div>

        <SubmitButton isSubmitting={isSubmitting} loadingLabel="Entrando…">
          Entrar
        </SubmitButton>
      </form>
    </AuthCard>
  );
}
