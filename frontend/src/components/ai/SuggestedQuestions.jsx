const SUGGESTIONS = [
  'Vai chover hoje?',
  'Qual o melhor horário para caminhar?',
  'Preciso levar guarda-chuva?',
  'Como fica o fim de semana?',
];

export function SuggestedQuestions({ onSelect }) {
  return (
    <div className="d-flex flex-wrap justify-content-center gap-2">
      {SUGGESTIONS.map((question) => (
        <button
          key={question}
          type="button"
          className="btn-climora btn-climora--secondary btn-climora--pill"
          onClick={() => onSelect(question)}
        >
          {question}
        </button>
      ))}
    </div>
  );
}
