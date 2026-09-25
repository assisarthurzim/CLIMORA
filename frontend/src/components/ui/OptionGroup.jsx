export function OptionGroup({ label, value, options, onChange }) {
  return (
    <div className="mb-4">
      <span className="type-label d-block mb-2">{label}</span>
      <div className="segmented" role="group">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            className="segmented__option"
            aria-pressed={option.value === value}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
