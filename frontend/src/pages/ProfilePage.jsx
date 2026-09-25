import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertMessage } from '@/components/ui/AlertMessage';
import { Avatar } from '@/components/ui/Avatar';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { FormField } from '@/components/ui/FormField';
import { OptionGroup } from '@/components/ui/OptionGroup';
import { SectionCard } from '@/components/ui/SectionCard';
import { SubmitButton } from '@/components/ui/SubmitButton';
import { useSettings } from '@/context/SettingsContext';
import { useToast } from '@/context/ToastContext';
import { useAuth } from '@/hooks/useAuth';
import { useForm } from '@/hooks/useForm';
import { profileService } from '@/services/profileService';
import { ROUTES } from '@/utils/constants';

const CONFIRM_WORD = 'EXCLUIR';

export function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const { notify } = useToast();
  const { settings, update: updateSettings } = useSettings();
  const [isDeleting, setIsDeleting] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState(null);

  const submitProfile = useCallback(
    async (values) => {
      await profileService.update({ name: values.name });
      notify({ message: 'Nome atualizado.', tone: 'success' });
    },
    [notify],
  );

  const submitPassword = useCallback(
    async (values) => {
      await profileService.changePassword(values);
      notify({ message: 'Senha alterada com sucesso.', tone: 'success' });
    },
    [notify],
  );

  const profileForm = useForm({ name: user?.name ?? '' }, submitProfile);
  const passwordForm = useForm(
    { currentPassword: '', newPassword: '', newPasswordConfirmation: '' },
    submitPassword,
    { resetOnSuccess: true },
  );

  async function handlePreference(changes) {
    try {
      await updateSettings(changes);
      notify({ message: 'Preferência atualizada.', tone: 'success' });
    } catch (error) {
      notify({ message: error.message, tone: 'error' });
    }
  }

  async function handleDelete() {
    setDeleteError(null);
    try {
      await profileService.deleteAccount(deletePassword);
      await logout();
      navigate(ROUTES.LANDING, { replace: true });
    } catch (error) {
      setDeleteError(error.message);
      setIsDeleting(false);
    }
  }

  return (
    <div className="container py-3 py-md-4" style={{ maxWidth: 640 }}>
      <div className="d-flex align-items-center gap-3 mb-4 flex-wrap">
        <Avatar name={user?.name} imageUrl={user?.avatar_url} size={64} />
        <div>
          <h1 className="h4 fw-semibold mb-1">{user?.name}</h1>
          <p className="mb-0" style={{ color: 'var(--content-secondary)' }}>
            {user?.email}
          </p>
        </div>
      </div>

      <SectionCard title="Dados da conta" description="Seu nome aparece na barra superior e nas saudações.">
        <AlertMessage message={profileForm.formError} />
        <form onSubmit={profileForm.handleSubmit} noValidate>
          <FormField
            label="Nome"
            name="name"
            value={profileForm.values.name}
            onChange={profileForm.handleChange}
            error={profileForm.fieldErrors.name}
            autoComplete="name"
          />
          <SubmitButton isSubmitting={profileForm.isSubmitting} loadingLabel="Salvando…">
            Salvar nome
          </SubmitButton>
        </form>
      </SectionCard>

      <SectionCard
        title="Preferências"
        description="Aplicadas imediatamente em todo o painel."
      >
        <OptionGroup
          label="Temperatura"
          value={settings.temperature_unit}
          options={[
            { value: 'celsius', label: 'Celsius (°C)' },
            { value: 'fahrenheit', label: 'Fahrenheit (°F)' },
          ]}
          onChange={(value) => handlePreference({ temperature_unit: value })}
        />
        <OptionGroup
          label="Velocidade do vento"
          value={settings.wind_speed_unit}
          options={[
            { value: 'kmh', label: 'km/h' },
            { value: 'ms', label: 'm/s' },
            { value: 'mph', label: 'mph' },
          ]}
          onChange={(value) => handlePreference({ wind_speed_unit: value })}
        />
      </SectionCard>

      <SectionCard
        title="Alterar senha"
        description="Sua sessão continua ativa depois da troca."
      >
        <AlertMessage message={passwordForm.formError} />
        <form onSubmit={passwordForm.handleSubmit} noValidate>
          <FormField
            label="Senha atual"
            name="currentPassword"
            type="password"
            value={passwordForm.values.currentPassword}
            onChange={passwordForm.handleChange}
            error={passwordForm.fieldErrors.current_password}
            autoComplete="current-password"
          />
          <FormField
            label="Nova senha"
            name="newPassword"
            type="password"
            value={passwordForm.values.newPassword}
            onChange={passwordForm.handleChange}
            error={passwordForm.fieldErrors.new_password}
            autoComplete="new-password"
            placeholder="Ao menos 8 caracteres, com letra e número"
          />
          <FormField
            label="Confirmar nova senha"
            name="newPasswordConfirmation"
            type="password"
            value={passwordForm.values.newPasswordConfirmation}
            onChange={passwordForm.handleChange}
            error={passwordForm.fieldErrors.new_password_confirmation}
            autoComplete="new-password"
          />
          <SubmitButton isSubmitting={passwordForm.isSubmitting} loadingLabel="Alterando…">
            Alterar senha
          </SubmitButton>
        </form>
      </SectionCard>

      <SectionCard
        title="Excluir conta"
        description="Remove permanentemente seus favoritos, histórico e conversas. Não há como desfazer."
      >
        <AlertMessage message={deleteError} />
        <div className="mb-3">
          <label htmlFor="delete-password" className="form-label small fw-medium">
            Confirme sua senha
          </label>
          <input
            id="delete-password"
            type="password"
            className="form-control"
            value={deletePassword}
            onChange={(event) => setDeletePassword(event.target.value)}
            autoComplete="current-password"
          />
        </div>
        <button
          type="button"
          className="btn-climora btn-climora--danger btn-climora--pill"
          onClick={() => setIsDeleting(true)}
          disabled={!deletePassword}
        >
          Excluir minha conta
        </button>
      </SectionCard>

      {isDeleting ? (
        <ConfirmDialog
          title="Excluir sua conta?"
          description="Todos os seus dados serão apagados imediatamente e de forma permanente."
          confirmLabel="Excluir definitivamente"
          isDestructive
          requiresText={CONFIRM_WORD}
          onConfirm={handleDelete}
          onCancel={() => setIsDeleting(false)}
        />
      ) : null}
    </div>
  );
}
