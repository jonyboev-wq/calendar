import { useMemo } from "react";
import { useQuery } from "react-query";
import { fetchPlannerProposals, PlannerProposal } from "../api";

export default function PlannerPanel() {
  const { data, isLoading, error } = useQuery<PlannerProposal[]>("proposals", fetchPlannerProposals);
  const items = useMemo(() => data ?? [], [data]);

  return (
    <section className="space-y-3">
      <header>
        <h2 className="text-lg font-semibold text-slate-200">Лучшие слоты</h2>
        <p className="text-sm text-slate-400">
          Предложения формируются на основе приоритета и недобора по семействам.
        </p>
      </header>
      {isLoading && <p className="text-sm text-slate-400">Загрузка...</p>}
      {error && <p className="text-sm text-red-400">Не удалось загрузить предложения</p>}
      <ul className="space-y-2">
        {items.map((proposal) => (
          <li key={proposal.event_id} className="p-3 rounded-lg bg-slate-800/80">
            <p className="font-medium">{proposal.reasoning}</p>
            <p className="text-sm text-slate-400">
              {new Date(proposal.suggested_start).toLocaleString()} → {" "}
              {new Date(proposal.suggested_end).toLocaleTimeString()}
            </p>
            <span className="text-xs uppercase tracking-wide text-accent">
              Score: {proposal.score.toFixed(1)}
            </span>
          </li>
        ))}
      </ul>
      {!isLoading && !error && items.length === 0 && (
        <p className="text-sm text-slate-400">Нет предложений — добавьте задачи, чтобы планировщик что-то подсказал.</p>
      )}
    </section>
  );
}
