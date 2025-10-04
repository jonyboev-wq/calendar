import { useState } from "react";

interface EventFormProps {
  onSubmit: (payload: unknown) => void;
}

const defaultState = {
  title: "",
  type: "flexible",
  duration_min: 60,
  priority: 5,
  family_key: "",
  pomodoro_opt_in: false,
};

export default function EventForm({ onSubmit }: EventFormProps) {
  const [state, setState] = useState(defaultState);

  return (
    <form
      className="space-y-4 bg-slate-800/80 p-4 rounded-xl"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit(state);
      }}
    >
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
            onChange={(event) => setState({ ...state, type: event.target.value })}
          >
            <option value="fixed">Фиксированное</option>
            <option value="flexible">Гибкое</option>
          </select>
        </div>
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
      </div>
      <div className="space-y-1">
        <label className="text-sm text-slate-400">Семейство</label>
        <input
          className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
          value={state.family_key}
          onChange={(event) => setState({ ...state, family_key: event.target.value })}
          placeholder="Например, health"
        />
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
        className="w-full bg-primary/80 hover:bg-primary text-white py-2 rounded-lg transition-colors"
      >
        Сохранить
      </button>
    </form>
  );
}
