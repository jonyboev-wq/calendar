import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import EventForm from "../components/EventForm";
import { createEvent, EventCreatePayload, EventItem, fetchEvents, fetchFamilies, TaskFamily } from "../api";

export default function CalendarPage() {
  const [view, setView] = useState<"day" | "week">("day");
  const queryClient = useQueryClient();
  const { data: events, isLoading: isEventsLoading, error: eventsError } = useQuery<EventItem[]>("events", fetchEvents);
  const { data: families } = useQuery<TaskFamily[]>("families", fetchFamilies);

  const createMutation = useMutation((payload: EventCreatePayload) => createEvent(payload), {
    onSuccess: () => {
      queryClient.invalidateQueries("events");
    },
  });

  const sortedEvents = useMemo(() => {
    if (!events) {
      return [];
    }
    return [...events].sort((left, right) => right.priority - left.priority);
  }, [events]);

  const visibleEvents = useMemo(() => {
    if (view === "day") {
      return sortedEvents.slice(0, 5);
    }
    return sortedEvents;
  }, [sortedEvents, view]);

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-slate-100">Расписание</h2>
          <p className="text-slate-400">Просмотр дневного и недельного календаря. Добавляйте задачи, чтобы планировщик мог работать.</p>
        </div>
        <div className="flex space-x-2">
          <button
            className={`px-4 py-2 rounded-lg transition-colors ${
              view === "day" ? "bg-primary/20 text-primary" : "bg-slate-800 hover:bg-slate-700"
            }`}
            onClick={() => setView("day")}
          >
            День
          </button>
          <button
            className={`px-4 py-2 rounded-lg transition-colors ${
              view === "week" ? "bg-primary/20 text-primary" : "bg-slate-800 hover:bg-slate-700"
            }`}
            onClick={() => setView("week")}
          >
            Неделя
          </button>
        </div>
      </header>
      <section className="grid grid-cols-3 gap-6">
        <div className="col-span-2 min-h-[400px] rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          {isEventsLoading && <p className="text-sm text-slate-400">Загружаем события…</p>}
          {eventsError && <p className="text-sm text-red-400">Не удалось загрузить события</p>}
          {!isEventsLoading && !eventsError && visibleEvents.length === 0 && (
            <p className="text-sm text-slate-400">Пока нет задач. Создайте первую через форму справа.</p>
          )}
          <ul className="space-y-3">
            {visibleEvents.map((event) => (
              <li key={event.id} className="p-4 rounded-lg bg-slate-800/70 border border-slate-700">
                <div className="flex items-center justify-between">
                  <p className="text-lg font-medium text-slate-100">{event.title}</p>
                  <span className="text-xs uppercase tracking-wide text-accent">Приоритет {event.priority}</span>
                </div>
                <p className="text-sm text-slate-400 mt-1">
                  Тип: {event.type === "fixed" ? "фиксированное" : "гибкое"} · Длительность: {event.duration_min} минут
                  {event.family_key ? ` · Семейство: ${event.family_key}` : ""}
                </p>
                {event.deadline && (
                  <p className="text-xs text-slate-500 mt-2">Дедлайн: {new Date(event.deadline).toLocaleString()}</p>
                )}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <EventForm
            families={families ?? []}
            onSubmit={(payload) => createMutation.mutateAsync(payload)}
            isSubmitting={createMutation.isLoading}
          />
        </div>
      </section>
    </div>
  );
}
