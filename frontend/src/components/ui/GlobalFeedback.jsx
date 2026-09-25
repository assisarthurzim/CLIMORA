import { useEffect, useRef } from 'react';
import { OfflineBanner } from '@/components/ui/OfflineBanner';
import { ToastStack } from '@/components/ui/ToastStack';
import { useToast } from '@/context/ToastContext';
import { onNetworkError, onSessionExpired } from '@/services/httpClient';

const NETWORK_COOLDOWN = 15000;

/**
 * Bridges failures raised outside React — inside the HTTP interceptors — into
 * the interface, which otherwise has no way to hear about them.
 */
export function GlobalFeedback() {
  const { notify } = useToast();
  const lastNetworkWarning = useRef(0);

  useEffect(() => {
    onSessionExpired(() => {
      notify({ message: 'Sua sessão expirou. Entre novamente para continuar.', tone: 'warning' });
    });

    onNetworkError(() => {
      // A dashboard loading several widgets would otherwise stack identical
      // warnings for one outage.
      const now = Date.now();
      if (now - lastNetworkWarning.current < NETWORK_COOLDOWN) return;
      lastNetworkWarning.current = now;

      notify({
        message: 'Não foi possível falar com o Climora. Verifique se o servidor está no ar.',
        tone: 'error',
      });
    });
  }, [notify]);

  return (
    <>
      <OfflineBanner />
      <ToastStack />
    </>
  );
}
