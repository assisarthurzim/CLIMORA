import { IconButton } from '@/components/ui/Button';
import { useTheme } from '@/hooks/useTheme';

export function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <IconButton
      name={isDark ? 'sun' : 'moon'}
      label={isDark ? 'Usar tema claro' : 'Usar tema escuro'}
      onClick={toggleTheme}
    />
  );
}
