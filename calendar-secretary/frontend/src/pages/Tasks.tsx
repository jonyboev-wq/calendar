import { useMemo, useState } from "react";
import { useQuery } from "react-query";
import { EventItem, fetchEvents } from "../api";

const filters = [
  { id: "all", label: "Все" },
  { id: "fixed", label: "Фиксированные" },
  { id: "flexible", label: "Гибкие" },
  { id: "meals", label: "Питание" },
  { id: "study", label: "Учёба" },
];

function matchFilter(event: EventItem, activeFilter: string): boolean {
  switch (activeFilter) {
    case "fixed":
      return event.type === "fixed";
    case "flexible":
      return event.type === "flexible";
    case "meals":
      return event.family_key === "meals";
    case "study":
      return event.family_key === "study";
    default:
      return true;
  }
}

export default function TasksPage() {
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const { data, isLoading, error } = useQuery<EventItem[]>("events", fetchEvents);

  const tasks = useMemo(() => {
    if (!data) {
      return [];
    }
    return data.filter((event) => event.type !== "fixed" || event.family_key !== null);
  }, [data]);

  const visibleTasks = useMemo(() => {
    return tasks.filter((task) => matchFilter(task, activeFilter));
  }, [tasks, activeFilter]);

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-slate-100">Задачи</h2>
          <p className="text-slate-400">
            Управление гибкими задачами, зависимостями и помодоро-настройками. Все события подгружаются из базы.
          </p>
        </div>
        <div className="flex space-x-2">
          {filters.map((filter) => (
            <button
              key={filter.id}
              onClick={() => setActiveFilter(filter.id)}
              className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                activeFilter === filter.id ? "bg-primary/20 text-primary" : "bg-slate-800 hover:bg-slate-700"
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </header>
      <section className="space-y-3">
        {isLoading && <p className="text-sm text-slate-400">Загрузка задач…</p>}
        {error && <p className="text-sm text-red-400">Не удалось загрузить список задач</p>}
        {!isLoading && !error && visibleTasks.length === 0 && (
          <p className="text-sm text-slate-400">Нет задач в выбранной категории.</p>
        )}
        {visibleTasks.map((task) => (
          <article key={task.id} className="p-4 rounded-xl border border-slate-800 bg-slate-900/60">
            <h3 className="font-semibold text-slate-200">{task.title}</h3>
            <p className="text-sm text-slate-400">
              {task.duration_min} мин · Семейство: {task.family_key ?? "не задано"} · Помодоро: {task.pomodoro_opt_in ? "да" : "нет"}
            </p>
            <p className="mt-2 text-xs text-slate-500">
              Приоритет {task.priority} {task.deadline ? `· Дедлайн ${new Date(task.deadline).toLocaleString()}` : ""}
            </p>
          </article>
        ))}
      </section>
    </div>
  );
}
