import { useState } from "react";
import CalendarPage from "./pages/Calendar";
import TasksPage from "./pages/Tasks";
import SettingsPage from "./pages/Settings";
import PlannerPanel from "./components/PlannerPanel";

const tabs = [
  { id: "calendar", label: "Календарь", component: CalendarPage },
  { id: "tasks", label: "Задачи", component: TasksPage },
  { id: "settings", label: "Настройки", component: SettingsPage },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("calendar");
  const ActiveComponent = tabs.find((tab) => tab.id === activeTab)?.component ?? CalendarPage;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex">
      <aside className="w-72 border-r border-slate-800 p-6 space-y-6">
        <h1 className="text-2xl font-semibold text-primary">Calendar Secretary</h1>
        <nav className="space-y-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id ? "bg-primary/20 text-primary" : "hover:bg-slate-800"
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <PlannerPanel />
      </aside>
      <main className="flex-1 p-6 overflow-y-auto">
        <ActiveComponent />
      </main>
    </div>
  );
}
