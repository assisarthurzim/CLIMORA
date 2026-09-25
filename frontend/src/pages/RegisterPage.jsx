import { useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertMessage } from '@/components/ui/AlertMessage';
import { AuthCard } from '@/components/ui/AuthCard';
import { FormField } from '@/components/ui/FormField';
import { SubmitButton } from '@/components/ui/SubmitButton';
import { useAuth } from '@/hooks/useAuth';
import { useForm } from '@/hooks/useForm';
import { ROUTES } from '@/utils/constants';

const INITIAL_VALUES = { name: '', email: '', password: '', passwordConfirmation: '' };

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const submit = useCallback(
    async (values) => {
      await register(values);
      navigate(ROUTES.DASHBOARD, { replace: true });
    },
    [register, navigate],
  );

  const { values, fieldErrors, formError, isSubmitting, handleChange, handleSubmit } = useForm(
    INITIAL_VALUES,
    submit,
  );

  return (
    <AuthCard
      title="Criar conta"
      subtitle="Leva menos de um minuto. Nenhum cartão necessário."
      footer={
        <span style={{ color: 'var(--content-secondary)' }}>
          Já tem conta? <Link to={ROUTES.LOGIN}>Entrar</Link>
        </span>
      }
    >
      <AlertMessage message={formError} />

      <form onSubmit={handleSubmit} noValidate>
        <FormField
          label="Nome"
          name="name"
          value={values.name}
          onChange={handleChange}
          error={fieldErrors.name}
          autoComplete="name"
          placeholder="Como devemos te chamar"
        />
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
          autoComplete="new-password"
          placeholder="Ao menos 8 caracteres, com letra e número"
        />
        <FormField
          label="Confirmar senha"
          name="passwordConfirmation"
          type="password"
          value={values.passwordConfirmation}
          onChange={handleChange}
          error={fieldErrors.passwordConfirmation}
          autoComplete="new-password"
        />

        <div className="mt-4">
          <SubmitButton isSubmitting={isSubmitting} loadingLabel="Criando conta…">
            Criar conta
          </SubmitButton>
        </div>
      </form>
    </AuthCard>
  );
}
