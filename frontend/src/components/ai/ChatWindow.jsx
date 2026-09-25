import { useEffect, useRef, useState } from 'react';
import { MessageBubble } from '@/components/ai/MessageBubble';
import { SuggestedQuestions } from '@/components/ai/SuggestedQuestions';
import { Icon } from '@/components/ui/Icon';
import { StateMessage } from '@/components/ui/StateMessage';
import { aiService } from '@/services/aiService';

export function ChatWindow({ coordinates, locationName }) {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [draft, setDraft] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  async function send(text) {
    const question = text.trim();
    if (!question || isSending || !coordinates) return;

    setDraft('');
    setError(null);
    setIsSending(true);

    // The question appears immediately; only the answer waits on the network.
    const optimistic = {
      id: `pending-${Date.now()}`,
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    };
    setMessages((current) => [...current, optimistic]);

    try {
      const result = await aiService.ask({ message: question, conversationId, coordinates });
      setConversationId(result.conversation.id);
      setMessages((current) => [
        ...current.filter((message) => message.id !== optimistic.id),
        result.question,
        result.answer,
      ]);
    } catch (requestError) {
      setMessages((current) => current.filter((message) => message.id !== optimistic.id));
      setDraft(question);
      setError(requestError.message);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div
      className="surface d-flex flex-column p-3 p-md-4"
      // dvh follows the browser chrome as it hides on scroll; vh does not,
      // which is what pushes the input field under the address bar.
      style={{ height: 'min(72dvh, 720px)' }}
    >
      <div className="flex-grow-1 overflow-auto pe-1">
        {messages.length === 0 ? (
          <StateMessage
            icon="assistant"
            title="Pergunte sobre o tempo"
            description={
              locationName
                ? `Respondo com base nos dados atuais de ${locationName}.`
                : 'Respondo apenas sobre clima, usando dados reais da previsão.'
            }
            action={<SuggestedQuestions onSelect={send} />}
          />
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}

        {isSending ? (
          <div className="d-flex align-items-center gap-2 small" style={{ color: 'var(--content-muted)' }}>
            <span className="spinner-border spinner-border-sm" aria-hidden="true" />
            Consultando a previsão…
          </div>
        ) : null}

        <div ref={endRef} />
      </div>

      {error ? (
        <p className="small mb-2" style={{ color: 'var(--danger)' }}>
          {error}
        </p>
      ) : null}

      <form
        className="d-flex gap-2 mt-3"
        onSubmit={(event) => {
          event.preventDefault();
          send(draft);
        }}
      >
        <input
          type="text"
          className="form-control"
          placeholder="Vai chover hoje?"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          disabled={isSending || !coordinates}
          aria-label="Mensagem para o assistente"
          maxLength={1000}
        />
        <button
          type="submit"
          className="btn-climora btn-climora--primary btn-climora--icon"
          style={{ borderRadius: 'var(--radius-pill)', width: 42, height: 42 }}
          disabled={isSending || !draft.trim() || !coordinates}
          aria-label="Enviar pergunta"
        >
          <Icon name="send" size={16} />
        </button>
      </form>
    </div>
  );
}
