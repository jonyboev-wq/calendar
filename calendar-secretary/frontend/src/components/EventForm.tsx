import { FormEvent, useState } from "react";
import { EventCreatePayload, TaskFamily } from "../api";

interface EventFormProps {
  families: TaskFamily[];
  onSubmit: (payload: EventCreatePayload) => Promise<void>;
  isSubmitting?: boolean;
}

const defaultState: EventCreatePayload = {
  title: "",
  type: "flexible",
  duration_min: 60,
  priority: 5,
  family_key: "",
  pomodoro_opt_in: false,
};

export default function EventForm({ families, onSubmit, isSubmitting }: EventFormProps) {
  const [state, setState] = useState<EventCreatePayload>(defaultState);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);
    try {
      await onSubmit({
        ...state,
        family_key: state.family_key ? state.family_key : null,
      });
      setState({ ...defaultState });
      setSuccessMessage("Событие сохранено");
    } catch (submitError) {
      const message = submitError instanceof Error ? submitError.message : "Неизвестная ошибка";
      setError(message);
    }
  }

  return (
    <form className="space-y-4 bg-slate-800/80 p-4 rounded-xl" onSubmit={handleSubmit}>
      <header className="space-y-1">
        <h3 className="text-lg font-semibold text-slate-200">Новая задача</h3>
        <p className="text-xs text-slate-400">Минимально необходимый набор данных для планировщика.</p>
      </header>
      <div className="space-y-1">
        <label className="text-sm text-slate-400">Название</label>
        <input
          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
          value={state.title}
          onChange={(event) => setState({ ...state, title: event.target.value })}
          placeholder="Например, обед"
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm text-slate-400">Тип</label>
          <select
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
            value={state.type}
            onChange={(event) => setState({ ...state, type: event.target.value as EventCreatePayload["type"] })}
          >
            <option value="fixed">Фиксированное</option>
            <option value="flexible">Гибкое</option>
          </select>
        </div>
        <div>
          <label className="text-sm text-slate-400">Длительность (мин)</label>
          <input
            type="number"
            min={15}
            step={15}
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
            value={state.duration_min}
            onChange={(event) => setState({ ...state, duration_min: Number(event.target.value) })}
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm text-slate-400">Приоритет</label>
          <input
            type="number"
            min={1}
            max={10}
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
            value={state.priority}
            onChange={(event) => setState({ ...state, priority: Number(event.target.value) })}
          />
        </div>
        <div>
          <label className="text-sm text-slate-400">Семейство</label>
          <select
            className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
            value={state.family_key ?? ""}
            onChange={(event) => setState({ ...state, family_key: event.target.value })}
          >
            <option value="">Без семейства</option>
            {families.map((family) => (
              <option key={family.key} value={family.key}>
                {family.name} ({family.key})
              </option>
            ))}
          </select>
        </div>
      </div>
      <label className="flex items-center space-x-2 text-sm text-slate-300">
        <input
          type="checkbox"
          checked={state.pomodoro_opt_in}
          onChange={(event) => setState({ ...state, pomodoro_opt_in: event.target.checked })}
        />
        <span>Резать по Помодоро</span>
      </label>
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-primary/80 hover:bg-primary disabled:opacity-60 text-white py-2 rounded-lg transition-colors"
      >
        {isSubmitting ? "Сохраняем..." : "Сохранить"}
      </button>
      {error && <p className="text-sm text-red-400">{error}</p>}
      {successMessage && <p className="text-sm text-emerald-400">{successMessage}</p>}
    </form>
  );
}
