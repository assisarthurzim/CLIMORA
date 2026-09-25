import { Button } from '@/components/ui/Button';

export function SubmitButton({ children, isSubmitting, loadingLabel = 'Enviando…' }) {
  return (
    <Button
      type="submit"
      variant="primary"
      size="lg"
      pill
      className="w-100"
      isLoading={isSubmitting}
      loadingLabel={loadingLabel}
    >
      {children}
    </Button>
  );
}
