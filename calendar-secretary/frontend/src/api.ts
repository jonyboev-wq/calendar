export interface EventItem {
  id: string;
  title: string;
  type: "fixed" | "flexible";
  duration_min: number;
  priority: number;
  deadline?: string | null;
  time_windows?: Array<{ start: string; end: string }>;
  flex?: Record<string, unknown> | null;
  location?: string | null;
  travel_time_min: number;
  calendar_id?: string | null;
  external_ids?: Record<string, string | null> | null;
  constraints?: Record<string, unknown> | null;
  metadata?: Record<string, unknown> | null;
  family_key?: string | null;
  pomodoro_opt_in: boolean;
  depends_on?: Array<{ task_id: string; type: string; lag_min: number }>;
}

export interface EventCreatePayload {
  title: string;
  type: "fixed" | "flexible";
  duration_min: number;
  priority: number;
  family_key?: string | null;
  pomodoro_opt_in: boolean;
}

async function handleJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || response.statusText);
  }
  return response.json() as Promise<T>;
}

export async function fetchEvents(): Promise<EventItem[]> {
  const response = await fetch("/api/events");
  return handleJsonResponse<EventItem[]>(response);
}

export async function createEvent(payload: EventCreatePayload): Promise<EventItem> {
  const response = await fetch("/api/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      depends_on: [],
      time_windows: [],
      constraints: null,
      metadata: null,
    }),
  });
  return handleJsonResponse<EventItem>(response);
}

export interface TaskFamily {
  key: string;
  name: string;
  weight: number;
  min_daily_minutes?: number | null;
  weekly_target_minutes?: number | null;
  max_daily_minutes?: number | null;
}

export async function fetchFamilies(): Promise<TaskFamily[]> {
  const response = await fetch("/api/families");
  return handleJsonResponse<TaskFamily[]>(response);
}

export interface PomodoroSettings {
  enabled: boolean;
  pomodoro_len_min: number;
  short_break_min: number;
  long_break_min: number;
  long_break_every: number;
}

export async function fetchPomodoroSettings(): Promise<PomodoroSettings> {
  const response = await fetch("/api/users/me");
  return handleJsonResponse<PomodoroSettings>(response);
}

export async function updatePomodoroSettings(
  payload: Partial<PomodoroSettings>
): Promise<PomodoroSettings> {
  const response = await fetch("/api/users/me", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleJsonResponse<PomodoroSettings>(response);
}

export interface CalDavCredentials {
  url: string;
  username: string;
  password: string;
}

export async function connectCalDav(credentials: CalDavCredentials): Promise<{ status: string }> {
  const response = await fetch("/api/sync/caldav/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  return handleJsonResponse<{ status: string }>(response);
}

export async function importIcs(file: File): Promise<{ created: number }> {
  const text = await file.text();
  const response = await fetch("/api/sync/import/ics", {
    method: "POST",
    headers: { "Content-Type": "text/calendar" },
    body: text,
  });
  return handleJsonResponse<{ created: number }>(response);
}

export interface PlannerProposal {
  event_id: string;
  suggested_start: string;
  suggested_end: string;
  score: number;
  reasoning: string;
}

export async function fetchPlannerProposals(): Promise<PlannerProposal[]> {
  const response = await fetch("/api/plan/proposals");
  const data = await handleJsonResponse<{ proposals?: PlannerProposal[] }>(response);
  return data.proposals ?? [];
}
