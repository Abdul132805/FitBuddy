# FitBuddy — AI Fitness Plan Generator

FitBuddy is a locally runnable FastAPI website that creates personalized seven-day workout plans, offers a nutrition and recovery tip, and refines a saved plan from user feedback. User profiles and plans are stored in SQLite.

## Features

- Responsive fitness themed interface with Jinja2 templates.
- Validated profile inputs for age, weight, fitness goal, and training intensity.
- Structured workout generation through Groq's GPT-OSS 120B model.
- Short nutrition guidance through Groq's GPT-OSS 20B model.
- Feedback driven plan refinement, with original and latest plans retained.
- SQLite/SQLAlchemy persistence and a saved plans page at `/users`.
- Automatic interactive API docs at `/docs` and `/redoc`.

## Technology

Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy, SQLite, Jinja2, Groq Python SDK, HTML, CSS, and JavaScript.

## Project structure

```text
app/                 FastAPI routes, settings, schemas, persistence, and Groq AI services
templates/           Home, workout result, and saved users pages
static/css/           Responsive FitBuddy styles
static/js/            Small form interaction
static/images/        Reserved for local image assets
database/             Automatically created SQLite database
.env.example          Groq configuration template
requirements.txt      Python dependencies
README.md             Setup and usage guide
```

## Installation

From the project directory:

```powershell
python -m venv fitbuddy-env
fitbuddy-env\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your Groq API key:

```env
GROQ_API_KEY=your_real_key
AI_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-120b
GROQ_NUTRITION_MODEL=openai/gpt-oss-20b
```

The project reads the key only on the server. Never put it into a template or commit `.env`. The `.env.example` contains a placeholder only. Groq's model catalog can change; set `GROQ_MODEL` and `GROQ_NUTRITION_MODEL` to models available to your Groq account if needed. The legacy `GROQ_WORKOUT_MODEL` remains accepted when `GROQ_MODEL` is not set.

## Database

On application startup, SQLAlchemy creates `database/fitbuddy.db` and its table automatically. No SQL commands are needed. To use another database URL, set `DATABASE_URL` in `.env`.

## Run

```powershell
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. Other useful URLs:

- `/users` — saved profiles and plan links
- `/docs` — generated OpenAPI/Swagger documentation
- `/redoc` — ReDoc documentation

## How generation works

The form is validated by Pydantic, then the workout service requests JSON from Groq and validates that it contains exactly seven days with warm-up, main workout, and cool-down entries. A fast Groq model generates a concise nutrition tip. The complete record is saved to SQLite. Feedback is validated and included alongside the profile and prior plan in a second generation request; the refined result is stored while preserving the original.

If the Groq API key is missing or the AI service is unavailable, FitBuddy shows a friendly message instead of a traceback. Nutrition guidance has a conservative general-purpose fallback. A working Groq key is needed to generate and refine workout plans. Backend logs record sanitized exception type, HTTP status, and request ID without logging prompts or credentials.

## Try it

1. Start the server and open the home page.
2. Enter a name, age from 13–100, weight from 25–350 kg, goal, and intensity.
3. Generate the seven day plan and review its profile, training sections, and nutrition tip.
4. Enter a request such as “I prefer home workouts and shorter sessions” and choose **Update My Plan**.
5. Visit `/users` to see saved entries and reopen their plans.

## Troubleshooting

- **Groq is not configured:** add a valid `GROQ_API_KEY` to `.env` and restart Uvicorn.
- **Model not found or unavailable:** set the model environment variable to an ID supported by the API key's account.
- **Import error:** activate the virtual environment and run `pip install -r requirements.txt`.
- **Port in use:** run `uvicorn app.main:app --reload --port 8001` and open port 8001.
- **Database issue:** stop the server and check write access to `database/`; the DB is created automatically on next startup.

## Deploy to Railway

The repository includes `railway.toml`, which installs the Python requirements, starts Uvicorn on Railway's injected `PORT`, and checks `/health` before routing traffic. Push this repository to GitHub, create a Railway project from that repository, and deploy from the project root.

In the Railway service Variables page, set `GROQ_API_KEY` to a valid key and set `AI_PROVIDER=groq`. The model variables in `.env.example` have defaults and can be overridden if your account uses different Groq models. Do not upload or commit `.env`.

Saved plans need persistent storage. Choose one of these options before relying on the deployment:

- **PostgreSQL (recommended):** add a Railway PostgreSQL service and set the web service's `DATABASE_URL` to the PostgreSQL service's connection URL (usually `${{Postgres.DATABASE_URL}}`). The app accepts Railway's `postgres://` URL format. The `psycopg` driver is installed from `requirements.txt`.
- **SQLite:** attach a Railway Volume to the web service at `/data` and set `DATABASE_URL=sqlite:////data/fitbuddy.db`. Without a volume, SQLite data is lost when Railway replaces the container.

After deployment, Railway assigns a public domain in the service's Networking settings. Check `/health` for the deployment health response and `/` for the FitBuddy page.

## Safety note

FitBuddy provides general fitness and nutrition information, not medical advice. Start at a comfortable level and stop if exercise causes pain or unusual symptoms.
