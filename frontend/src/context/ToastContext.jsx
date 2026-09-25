import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react';

export const ToastContext = createContext(null);

const DEFAULT_DURATION = 5000;
const MAX_VISIBLE = 3;

/**
 * One place for transient feedback. Without it, every screen invents its own
 * banner and errors raised outside a component have nowhere to surface.
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const nextId = useRef(0);

  const dismiss = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const notify = useCallback(
    ({ message, tone = 'info', duration = DEFAULT_DURATION }) => {
      const id = (nextId.current += 1);
      setToasts((current) => [...current.slice(-(MAX_VISIBLE - 1)), { id, message, tone }]);

      if (duration > 0) {
        setTimeout(() => dismiss(id), duration);
      }
      return id;
    },
    [dismiss],
  );

  const value = useMemo(() => ({ toasts, notify, dismiss }), [toasts, notify, dismiss]);

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast deve ser usado dentro de ToastProvider.');
  }
  return context;
}
