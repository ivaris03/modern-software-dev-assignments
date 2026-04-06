# Week 5

Minimal full‑stack starter for experimenting with autonomous coding agents.

- FastAPI backend with SQLite (SQLAlchemy)
- Static frontend (no Node toolchain needed)
- Minimal tests (pytest)
- Pre-commit (black + ruff)
- Tasks to practice agent-driven workflows

## Quickstart

1) Create and activate a virtualenv, then install dependencies

```bash
cd /Users/mihaileric/Documents/code/modern-software-dev-assignments
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

2) (Optional) Install pre-commit hooks

```bash
pre-commit install
```

3) Run the app (from `week5/`)

```bash
cd week5 && make run
```

Open `http://localhost:8000` for the frontend and `http://localhost:8000/docs` for the API docs.

## Structure

```
backend/                # FastAPI app
frontend/               # Static UI served by FastAPI
data/                   # SQLite DB + seed
docs/                   # TASKS for agent-driven workflows
```

## Tests

```bash
cd week5 && make test
```

## Formatting/Linting

```bash
cd week5 && make format
cd week5 && make lint
```

## Configuration

Copy `.env.example` to `.env` (in `week5/`) to override defaults like the database path.

## Deploy Guide

This application can be deployed on Vercel with a FastAPI backend and React frontend.

### Architecture

- **Frontend**: React app built with Vite, served as static files
- **Backend**: FastAPI Python serverless function on Vercel
- **Database**: SQLite (ephemeral on Vercel - data does not persist between requests)

### Limitations

Vercel's Python runtime is **stateless**. SQLite databases do not persist between requests because Vercel uses ephemeral filesystem mounts. For production deployments requiring persistent data, consider:

- Deploying the backend to **Fly.io** or **Render** (which support persistent SQLite)
- Using a managed database service like **Supabase**, **PlanetScale**, or **Neon**

### Environment Variables

Required for deployment:

| Variable | Description | Example |
|----------|-------------|---------|
| `FRONTEND_ORIGIN` | The origin URL of your Vercel frontend deployment | `https://your-project.vercel.app` |
| `VITE_API_BASE_URL` | API base URL for the frontend (can be empty if using same-origin rewrites) | `/api` or empty |

### Deploy Commands

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Build the frontend**:
   ```bash
   cd week5/frontend/ui && npm install && npm run build
   ```

3. **Deploy to Vercel**:
   ```bash
   vercel deploy --prod
   ```

   Or connect your GitHub repository to Vercel for automatic deployments.

4. **Set environment variables** in Vercel dashboard:
   - `FRONTEND_ORIGIN`: Your Vercel frontend URL (e.g., `https://week5-abc123.vercel.app`)

### Rollback

To rollback to a previous deployment:

1. Go to the Vercel dashboard
2. Select your project
3. Click on the "Deployments" tab
4. Find the previous working deployment
5. Click "..." menu and select "Promote to Production"

Alternatively, use the CLI:
```bash
vercel rollback [deployment-url]
```

### Local Development with Vercel

To test the serverless configuration locally:

```bash
# Install Vercel CLI
npm install -g vercel

# Run local serverless emulation
vercel dev
```

### Project Structure for Vercel

```
week5/
├── api/
│   └── index.py          # Serverless Python function
├── backend/
│   └── app/              # FastAPI application
├── frontend/
│   ├── dist/             # Built React app
│   └── ui/               # React source code
├── vercel.json           # Vercel routing configuration
└── requirements.txt      # Python dependencies
```
