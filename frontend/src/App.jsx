import { RouterProvider } from 'react-router-dom';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { GlobalFeedback } from '@/components/ui/GlobalFeedback';
import { AuthProvider } from '@/context/AuthContext';
import { LocationProvider } from '@/context/LocationContext';
import { SettingsProvider } from '@/context/SettingsContext';
import { ThemeProvider } from '@/context/ThemeContext';
import { ToastProvider } from '@/context/ToastContext';
import { router } from '@/router';

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <SettingsProvider>
              <LocationProvider>
                <GlobalFeedback />
                <RouterProvider router={router} />
              </LocationProvider>
            </SettingsProvider>
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
