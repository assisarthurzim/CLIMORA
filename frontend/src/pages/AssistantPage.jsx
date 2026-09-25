import { ChatWindow } from '@/components/ai/ChatWindow';
import { useActiveLocation } from '@/context/LocationContext';

export function AssistantPage() {
  const { coordinates, resolvedLocation } = useActiveLocation();

  return (
    <div className="container py-4">
      <div className="mb-4">
        <h1 className="h4 fw-semibold mb-1">Assistente</h1>
        <p className="mb-0" style={{ color: 'var(--content-secondary)' }}>
          Perguntas sobre clima, respondidas com os dados reais da previsão.
        </p>
      </div>

      <ChatWindow coordinates={coordinates} locationName={resolvedLocation?.name} />
    </div>
  );
}
