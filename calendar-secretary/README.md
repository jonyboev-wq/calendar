# Calendar Secretary

"Calendar Secretary" is a full-stack productivity assistant that blends an
intelligent calendar with a personal secretary. It automatically selects the
best slots for meals, study sessions, workouts, and work tasks while respecting
hard constraints (classes, meetings) and softer preferences (quiet hours,
family targets, Pomodoro cadence).

## Features

- **Smart planning** powered by OR-Tools CP-SAT with a heuristic fallback.
- **Flexible events** supporting priorities, deadlines, shift windows, split
  rules, and travel buffers.
- **Task families** with weights, daily quotas, and weekly targets that shape
  the objective function.
- **Task dependencies** with FS/SS/FF/SF relationships and lag minutes.
- **Pomodoro expansion** that automatically slices large flexible tasks into
  work/break chunks using personal settings.
- **Two synchronization strategies**:
  - CalDAV two-way sync with iCloud (app-specific password).
  - ICS import/export with hashtag-based metadata mapping.
- **Live updates** via WebSockets (placeholder in this scaffolding).
- **Timezone aware** (default: `Europe/Helsinki`, stored internally as UTC).

## Getting Started

### Prerequisites

- Docker / Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11 with Poetry (for backend development)

### Environment configuration

Create a `.env` at the repository root:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/calendar
ENCRYPTION_KEY=<generate Fernet key>
OBJ_WEIGHT_FAMILY_DEFICIT=3.0
OBJ_WEIGHT_OVERUSE=2.0
OBJ_WEIGHT_FAMILY_TARGET=1.0
OBJ_BONUS_POMODORO=0.5
```

Generate a Fernet key via `python -c "from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())"`.

### Running with Docker

```bash
docker compose up --build
```

The backend is available on http://localhost:8000 and the frontend on
http://localhost:5173.

#### Проверка успешного запуска

- Убедитесь, что контейнеры находятся в состоянии `running` с помощью
  `docker compose ps`.
- Для бэкенда выполните `curl http://localhost:8000/health` и убедитесь, что в
  ответ приходит `{"status": "ok"}`. Этот эндпоинт объявлен в
  `app/main.py` и служит простым индикатором готовности сервера.
- Для фронтенда откройте в браузере http://localhost:5173 — должна загрузиться
  стартовая страница приложения.

### Running locally (backend)

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Running locally (frontend)

```bash
cd frontend
npm install
npm run dev
```

### Database migrations

Alembic scripts live under `backend/alembic`. To generate new migrations:

```bash
poetry run alembic revision --autogenerate -m "describe change"
poetry run alembic upgrade head
```

### CalDAV with iCloud

1. Visit Apple ID → Security → Generate an app-specific password.
2. In the frontend settings, enable CalDAV sync and enter your Apple ID email
   plus the generated password.
3. The backend encrypts credentials with Fernet before storing them. Use the
   `ENCRYPTION_KEY` from `.env`.

### ICS import/export

- Import: upload an ICS file via `POST /api/sync/import/ics`. Hashtags like
  `#family:health` or `#dep:FS(<UUID>,30)` are parsed into structured data.
- Export: the service can emit an ICS snapshot of the current schedule with the
  same metadata encoding.

### Objective weights & quiet hours

Objective weights are configurable via `.env` variables prefixed with
`OBJ_WEIGHT_` and `OBJ_BONUS_`. Quiet hours and meal windows are stored per user
in the database (see `user` table fields and planner services).

### Testing

```bash
cd backend
poetry run pytest
```

### Additional concepts

- **Dependencies**: Supported types are Finish-to-Start (FS), Start-to-Start
  (SS), Finish-to-Finish (FF), and Start-to-Finish (SF) with lag minutes. Cycles
  are rejected on ingestion.
- **Families**: Each task can belong to a family (`family_key`). The family
  defines weighting and optional daily/weekly targets. Planner penalties push
  the schedule towards satisfying these targets.
- **Pomodoro**: When enabled in personal settings (`/api/users/me/pomodoro`),
  flexible tasks opted into Pomodoro automatically expand into alternating work
  and break chunks. Breaks are modeled as fixed events.

### Sample data

```json
{
  "families": [
    {"key": "study", "name": "Учёба", "weight": 1.0, "weekly_target_minutes": 600},
    {"key": "health", "name": "Здоровье", "weight": 1.4, "min_daily_minutes": 45, "weekly_target_minutes": 210}
  ],
  "user_pomodoro": {"enabled": true, "pomodoro_len_min": 25, "short_break_min": 5, "long_break_min": 15, "long_break_every": 4},
  "events": [
    {"id":"A", "title":"Собрать материалы", "type":"flexible", "duration_min":60, "priority":7, "family_key":"study", "pomodoro_opt_in": true},
    {"id":"B", "title":"Слайды", "type":"flexible", "duration_min":120, "priority":8, "family_key":"study", "pomodoro_opt_in": true, "depends_on":[{"task_id":"A","type":"FS","lag_min":30}]},
    {"id":"C", "title":"Тренировка", "type":"flexible", "duration_min":90, "priority":6, "family_key":"health"}
  ]
}
```

## Frontend overview

- **Calendar view**: day/week toggle with drag-and-drop for flexible tasks and
  Pomodoro break markers.
- **Tasks page**: filters (Fixed/Flexible/Meals/Study) and dependency badges.
- **Settings**: quiet hours, meal windows, Pomodoro preferences, feature flags.
- **Planner panel**: live plan preview, family progress bars, "best slots"
  suggestions sorted by effective priority.

## CI & Quality

- Pre-commit hooks configured for Black, Ruff, and Mypy (see `pyproject.toml`).
- GitHub Actions workflows run tests and linting (not included in this stub but
  described for future expansion).
