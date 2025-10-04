const filters = [
  { id: "all", label: "Все" },
  { id: "fixed", label: "Фиксированные" },
  { id: "flexible", label: "Гибкие" },
  { id: "meals", label: "Питание" },
  { id: "study", label: "Учёба" }
];

export default function TasksPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-slate-100">Задачи</h2>
          <p className="text-slate-400">Управление гибкими задачами, зависимостями и помодоро-настройками.</p>
        </div>
        <div className="flex space-x-2">
          {filters.map((filter) => (
            <button key={filter.id} className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm">
              {filter.label}
            </button>
          ))}
        </div>
      </header>
      <section className="space-y-3">
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60">
          <h3 className="font-semibold text-slate-200">Курсовая работа</h3>
          <p className="text-sm text-slate-400">10 ч • Семейство: study • Помодоро: да</p>
          <div className="mt-2 flex space-x-2 text-xs text-slate-400">
            <span className="bg-slate-800 px-2 py-1 rounded">FS → Сбор материалов</span>
            <span className="bg-slate-800 px-2 py-1 rounded">Дедлайн: завтра</span>
          </div>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60">
          <h3 className="font-semibold text-slate-200">Тренировка</h3>
          <p className="text-sm text-slate-400">90 мин • Семейство: health • Перенос в течение недели</p>
        </div>
      </section>
    </div>
  );
}
