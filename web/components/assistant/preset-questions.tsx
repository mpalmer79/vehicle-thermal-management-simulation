"use client";

/**
 * Tappable starter questions.
 *
 * Selecting one submits it straight into the conversation. The same control is reused
 * for the contextual follow-ups offered under an answer, with a lighter treatment.
 */
export function PresetQuestions({
  questions,
  onSelect,
  label,
  variant = "preset",
}: {
  questions: readonly string[];
  onSelect: (question: string) => void;
  label: string;
  variant?: "preset" | "follow-up";
}) {
  if (questions.length === 0) return null;

  return (
    <div className={`assistant-prompts ${variant}`}>
      <span className="eyebrow">{label}</span>
      <ul>
        {questions.map((question, index) => (
          <li key={question} style={{ animationDelay: `${index * 45}ms` }}>
            <button onClick={() => onSelect(question)} type="button">
              <span>{question}</span>
              <i aria-hidden="true">→</i>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
