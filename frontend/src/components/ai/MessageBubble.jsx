import { formatTime } from '@/utils/formatters';

export function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`d-flex mb-3 ${isUser ? 'justify-content-end' : 'justify-content-start'}`}>
      <div
        className="px-3 py-2"
        style={{
          maxWidth: 'min(88%, 620px)',
          borderRadius: 'var(--radius-lg)',
          background: isUser ? 'var(--accent)' : 'var(--surface-sunken)',
          color: isUser ? 'var(--accent-content)' : 'var(--content-primary)',
          borderBottomRightRadius: isUser ? 'var(--radius-sm)' : undefined,
          borderBottomLeftRadius: isUser ? undefined : 'var(--radius-sm)',
        }}
      >
        <p className="mb-1" style={{ whiteSpace: 'pre-wrap' }}>
          {message.content}
        </p>
        <span
          className="d-block small"
          style={{ opacity: 0.7, fontSize: 'var(--text-xs)', textAlign: 'right' }}
        >
          {formatTime(message.created_at)}
        </span>
      </div>
    </div>
  );
}
