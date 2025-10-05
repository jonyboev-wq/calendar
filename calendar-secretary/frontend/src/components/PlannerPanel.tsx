import { useQuery } from "react-query";
import { useMemo } from "react";

interface Proposal {
  event_id: string;
  suggested_start: string;
  suggested_end: string;
  score: number;
  reasoning: string;
}

async function fetchProposals(): Promise<Proposal[]> {
  const response = await fetch("/api/plan/proposals");
  if (!response.ok) {
    throw new Error("Failed to load proposals");
  }
  const data = await response.json();
  return data.proposals ?? [];
}

export default function PlannerPanel() {
  const { data, isLoading, error } = useQuery("proposals", fetchProposals);
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
    </section>
  );
}
