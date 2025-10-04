import EventForm from "../components/EventForm";

export default function CalendarPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-slate-100">Расписание</h2>
          <p className="text-slate-400">Просмотр дневного и недельного календаря.</p>
        </div>
        <div className="flex space-x-2">
          <button className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700">День</button>
          <button className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700">Неделя</button>
        </div>
      </header>
      <section className="grid grid-cols-3 gap-6">
        <div className="col-span-2 min-h-[400px] rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="text-sm text-slate-400">
            Здесь будет календарный вид с поддержкой drag-and-drop и подсветкой помодоро-перерывов.
          </p>
        </div>
        <div>
          <EventForm onSubmit={(payload) => console.log("save", payload)} />
        </div>
      </section>
    </div>
  );
}
