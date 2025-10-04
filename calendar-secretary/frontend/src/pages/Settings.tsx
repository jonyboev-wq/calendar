export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-3xl font-semibold text-slate-100">Настройки</h2>
        <p className="text-slate-400">Тихие часы, синхронизация и Помодоро.</p>
      </header>
      <section className="grid grid-cols-2 gap-6">
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3">
          <h3 className="text-xl font-semibold text-slate-200">Синхронизация</h3>
          <p className="text-sm text-slate-400">Подключите iCloud CalDAV или импортируйте ICS.</p>
          <button className="px-4 py-2 rounded-lg bg-primary/80 hover:bg-primary">Подключить CalDAV</button>
          <button className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700">Импорт ICS</button>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3">
          <h3 className="text-xl font-semibold text-slate-200">Помодоро</h3>
          <p className="text-sm text-slate-400">Управление длительностью сессий и перерывов.</p>
          <dl className="grid grid-cols-2 gap-2 text-sm text-slate-300">
            <div>
              <dt>Работа</dt>
              <dd>25 минут</dd>
            </div>
            <div>
              <dt>Перерыв</dt>
              <dd>5 минут</dd>
            </div>
            <div>
              <dt>Длинный перерыв</dt>
              <dd>15 минут</dd>
            </div>
            <div>
              <dt>Каждые</dt>
              <dd>4 цикла</dd>
            </div>
          </dl>
        </div>
      </section>
    </div>
  );
}
