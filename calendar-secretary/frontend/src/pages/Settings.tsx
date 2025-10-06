import { useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  CalDavCredentials,
  connectCalDav,
  fetchFamilies,
  fetchPomodoroSettings,
  importIcs,
  PomodoroSettings,
  TaskFamily,
  updatePomodoroSettings,
} from "../api";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { data: families } = useQuery<TaskFamily[]>("families", fetchFamilies);
  const { data: pomodoroSettings, isLoading: isPomodoroLoading } = useQuery<PomodoroSettings>(
    "pomodoro",
    fetchPomodoroSettings
  );

  const caldavMutation = useMutation((credentials: CalDavCredentials) => connectCalDav(credentials));
  const icsMutation = useMutation((file: File) => importIcs(file), {
    onSuccess: () => {
      queryClient.invalidateQueries("events");
    },
  });
  const pomodoroMutation = useMutation((payload: Partial<PomodoroSettings>) => updatePomodoroSettings(payload), {
    onSuccess: (data) => {
      queryClient.setQueryData("pomodoro", data);
      setPomodoroForm(data);
    },
  });

  const [caldavForm, setCalDavForm] = useState<CalDavCredentials>({ url: "", username: "", password: "" });
  const [pomodoroForm, setPomodoroForm] = useState<PomodoroSettings | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const familiesSummary = useMemo(() => {
    if (!families || families.length === 0) {
      return "Пока нет семейств. Добавьте их через API или импорт";
    }
    return families
      .map((family) => `${family.name} (${family.key}) — вес ${family.weight}`)
      .join("\n");
  }, [families]);

  const showPomodoroForm = pomodoroForm ?? pomodoroSettings ?? null;

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-3xl font-semibold text-slate-100">Настройки</h2>
        <p className="text-slate-400">Тихие часы, синхронизация и Помодоро.</p>
      </header>
      <section className="grid grid-cols-2 gap-6">
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-4">
          <h3 className="text-xl font-semibold text-slate-200">Синхронизация</h3>
          <p className="text-sm text-slate-400">Подключите iCloud CalDAV или импортируйте ICS.</p>
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              caldavMutation.mutate(caldavForm);
            }}
          >
            <div className="space-y-1">
              <label className="text-sm text-slate-400">CalDAV URL</label>
              <input
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
                value={caldavForm.url}
                onChange={(event) => setCalDavForm({ ...caldavForm, url: event.target.value })}
                placeholder="https://caldav.icloud.com"
                required
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm text-slate-400">Apple ID</label>
              <input
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
                value={caldavForm.username}
                onChange={(event) => setCalDavForm({ ...caldavForm, username: event.target.value })}
                placeholder="user@icloud.com"
                required
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm text-slate-400">Пароль приложения</label>
              <input
                type="password"
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
                value={caldavForm.password}
                onChange={(event) => setCalDavForm({ ...caldavForm, password: event.target.value })}
                required
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-primary/80 hover:bg-primary disabled:opacity-60"
              disabled={caldavMutation.isLoading}
            >
              {caldavMutation.isLoading ? "Подключаем..." : "Подключить CalDAV"}
            </button>
            {caldavMutation.isError && (
              <p className="text-sm text-red-400">Не удалось подключить CalDAV: {(caldavMutation.error as Error).message}</p>
            )}
            {caldavMutation.isSuccess && <p className="text-sm text-emerald-400">Подключение успешно сохранено.</p>}
          </form>
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".ics,text/calendar"
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) {
                  icsMutation.mutate(file);
                  event.target.value = "";
                }
              }}
            />
            <button
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700"
              onClick={() => fileInputRef.current?.click()}
              disabled={icsMutation.isLoading}
            >
              {icsMutation.isLoading ? "Импортируем..." : "Импорт ICS"}
            </button>
            {icsMutation.isError && (
              <p className="text-sm text-red-400">Не удалось импортировать файл: {(icsMutation.error as Error).message}</p>
            )}
            {icsMutation.isSuccess && (
              <p className="text-sm text-emerald-400">Импортировано событий: {icsMutation.data?.created ?? 0}</p>
            )}
          </div>
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-slate-300">Семейства задач</h4>
            <pre className="text-xs text-slate-400 whitespace-pre-wrap bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              {familiesSummary}
            </pre>
          </div>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3">
          <h3 className="text-xl font-semibold text-slate-200">Помодоро</h3>
          <p className="text-sm text-slate-400">Управление длительностью сессий и перерывов.</p>
          {isPomodoroLoading && <p className="text-sm text-slate-400">Загружаем настройки...</p>}
          {showPomodoroForm && (
            <form
              className="space-y-3"
              onSubmit={(event) => {
                event.preventDefault();
                pomodoroMutation.mutate(showPomodoroForm);
              }}
            >
              <label className="flex items-center space-x-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={showPomodoroForm.enabled}
                  onChange={(event) =>
                    setPomodoroForm({ ...showPomodoroForm, enabled: event.target.checked })
                  }
                />
                <span>Включить Помодоро</span>
              </label>
              <div className="grid grid-cols-2 gap-3 text-sm text-slate-300">
                <label className="space-y-1">
                  <span>Работа (мин)</span>
                  <input
                    type="number"
                    min={15}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
                    value={showPomodoroForm.pomodoro_len_min}
                    onChange={(event) =>
                      setPomodoroForm({ ...showPomodoroForm, pomodoro_len_min: Number(event.target.value) })
                    }
                  />
                </label>
                <label className="space-y-1">
                  <span>Перерыв (мин)</span>
                  <input
                    type="number"
                    min={3}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
                    value={showPomodoroForm.short_break_min}
                    onChange={(event) =>
                      setPomodoroForm({ ...showPomodoroForm, short_break_min: Number(event.target.value) })
                    }
                  />
                </label>
                <label className="space-y-1">
                  <span>Длинный перерыв (мин)</span>
                  <input
                    type="number"
                    min={5}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
                    value={showPomodoroForm.long_break_min}
                    onChange={(event) =>
                      setPomodoroForm({ ...showPomodoroForm, long_break_min: Number(event.target.value) })
                    }
                  />
                </label>
                <label className="space-y-1">
                  <span>Каждые N циклов</span>
                  <input
                    type="number"
                    min={1}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700"
                    value={showPomodoroForm.long_break_every}
                    onChange={(event) =>
                      setPomodoroForm({ ...showPomodoroForm, long_break_every: Number(event.target.value) })
                    }
                  />
                </label>
              </div>
              <button
                type="submit"
                disabled={pomodoroMutation.isLoading}
                className="px-4 py-2 rounded-lg bg-primary/80 hover:bg-primary disabled:opacity-60"
              >
                {pomodoroMutation.isLoading ? "Сохраняем..." : "Сохранить"}
              </button>
            </form>
          )}
          {pomodoroMutation.isError && (
            <p className="text-sm text-red-400">
              Не удалось обновить настройки: {(pomodoroMutation.error as Error).message}
            </p>
          )}
          {pomodoroMutation.isSuccess && (
            <p className="text-sm text-emerald-400">Настройки обновлены. Планировщик учтёт их при расчёте.</p>
          )}
          {!isPomodoroLoading && !showPomodoroForm && (
            <p className="text-sm text-red-400">Не удалось загрузить настройки Помодоро — проверьте бэкенд.</p>
          )}
        </div>
      </section>
    </div>
  );
}
