# AgroFarm AI

Precision-agriculture dashboard with FastAPI + SQLite/PostgreSQL, React + Tailwind, trained ML artifacts, weather alerts, AI reports, and a farm-grounded chatbot.

## Requirements

Install these before setting up the project:

- Python 3.11 or newer
- Node.js 18 or newer (npm is included with Node.js)
- Git, if the project is being shared through a Git repository

The backend dependencies are listed in [requirements.txt](requirements.txt). The frontend dependencies are listed in [web/package.json](web/package.json) and locked in [web/package-lock.json](web/package-lock.json).

Do not copy the existing `venv` or `web/node_modules` folders to another laptop. They are machine-specific and can be recreated from these dependency files.

## Configuration and API keys

Copy [backend/.env.example](backend/.env.example) to `backend/.env` and set:

- `OPENWEATHER_API_KEY` - OpenWeatherMap (the backend falls back to Open-Meteo if this is empty)
- `GROQ_API_KEY` - Groq chat completions for `/chatbot/ask` (a local grounded fallback is used if this is empty)
- `GROQ_MODEL` - Groq model name, default `openai/gpt-oss-20b`
- `GROQ_BASE_URL` - default `https://api.groq.com/openai/v1`
- `DATABASE_URL` - `sqlite:///./agrofarm.db` by default, or a PostgreSQL URL such as `postgresql+psycopg2://user:password@localhost:5432/agrofarm`

The SQLite database is stored in `backend/agrofarm.db`. If it is not shared, the backend creates a new empty database automatically on startup. Never share `backend/.env`; share only `backend/.env.example` and provide API keys through a secure channel.

## Setup on Windows

Open PowerShell in the project root (`Agri`) and create the Python environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item backend\.env.example backend\.env
```

If PowerShell blocks activation, run this once in the same PowerShell window and then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

The `backend\requirements.txt` file also points to the root requirements file, so this is equivalent when run from the `backend` folder:

```powershell
pip install -r requirements.txt
```

## Run the backend

From the project root, with the virtual environment activated:

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`, and interactive API documentation is at `http://127.0.0.1:8000/docs`. Keep this terminal running.

## Install and run the frontend

Open a second PowerShell window in the project root:

```powershell
cd web
npm ci
npm run dev
```

Open `http://localhost:5173` in a browser. The Vite configuration proxies frontend API requests to `http://127.0.0.1:8000`, so both servers must be running.

For a production build preview:

```powershell
npm run build
npm run preview
```

## Backend API behavior

Tables are created on startup. Auth: `POST /auth/register`, `POST /auth/login`. Farm: `POST /farm/create`, `GET /farm/{id}`, `POST /farm/{id}/soil-data`, `POST /farm/{id}/upload-image`. Saving soil data also runs crop, fertilizer, yield, and market-price models so the dashboard cards fill from live API data.

## Model training

Trained pickles live in `saved_models/`. Publication figures and `metrics.json` live in `ml/saved_models/` and `plots/`.

```powershell
python train_models.py
python train_publication.py
python train_publication.py --vision
```

`GET /models/metrics` serves the real `metrics.json`. Fertilizer is rule-based and has no ML accuracy metric. The chatbot uses Groq's OpenAI-compatible Chat Completions API; without a `GROQ_API_KEY`, `/chatbot/ask` remains usable with a local farm-grounded fallback.

## Verify

1. Register a farmer; a farm is created with the account.
2. Save soil data on Soil Analysis; crop, yield, fertilizer, and price cards should populate.
3. Upload a leaf image on Disease Detection; the original image and Grad-CAM-style overlay should appear.
4. Open Weather & Risk, Reports, AI Assistant, and Model Evaluation and confirm live API data.
