# VoiceOrch — Multi-Tenant Agentic Voice Orchestrator

A cloud-native SaaS platform where multiple real estate companies run automated AI voice campaigns to qualify leads. Built with **FastAPI**, **LangGraph**, **Vapi.ai**, **MongoDB Atlas**, **React + Tailwind**, and deployed on **GCP Cloud Run**.

---

## Architecture

```
Admin Dashboard (React)
        │  REST + WebSocket
        ▼
FastAPI Backend (GCP Cloud Run)
   ├── /api/campaigns/trigger  →  LangGraph Dispatch Graph
   │        └── Vapi.ai Outbound Call
   ├── /api/webhooks/vapi      →  LangGraph Evaluation Graph
   │        └── OpenAI GPT-4o-mini (transcript analysis)
   └── /ws/updates             →  WebSocket (live status push)
        │
        ▼
  MongoDB Atlas
  ├── companies
  ├── customers
  └── call_logs
```

### LangGraph Architecture

**Dispatch Graph** (triggered by admin "Launch Campaign"):
```
START → fetch_leads_node → build_prompt_node → dispatch_calls_node → END
```
- `fetch_leads_node`: Queries MongoDB for all `PENDING` leads
- `build_prompt_node`: Dynamically loads company's `system_prompt` from DB
- `dispatch_calls_node`: Calls Vapi API, updates DB to `CALL_INITIATED`, broadcasts WebSocket event

**Evaluation Graph** (triggered by Vapi webhook):
```
START → load_call_context_node → evaluate_transcript_node → human_loop_check_node → state_update_node → END
```
- `load_call_context_node`: Finds lead by `call_id`
- `evaluate_transcript_node`: Sends transcript to GPT-4o-mini with structured output
- `human_loop_check_node`: If confidence < 60% → `NEEDS_REVIEW`, else pass through
- `state_update_node`: Updates DB, saves call log, broadcasts WebSocket event

---

## Environment Variables

Create a `.env` file in the project root (never commit this):

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `VAPI_API_KEY` | Vapi.ai private API key |
| `VAPI_PHONE_NUMBER_ID` | Vapi.ai phone number ID for outbound calls |
| `OPENAI_API_KEY` | OpenAI API key (GPT-4o-mini) |
| `ENVIRONMENT` | `development` or `production` |

```bash
cp .env.example .env
# Then fill in your values
```

---

## Local Setup (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB Atlas account (free M0 tier)
- Vapi.ai account (free)
- OpenAI API key

### 1. Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Seed the database (run once)
python -m backend.seed

# Start the backend
uvicorn backend.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at: http://localhost:5173

> The Vite dev server proxies `/api` and `/ws` to `localhost:8000` automatically.

---

## Local Setup (With Docker)

```bash
# Build and run everything
docker compose up --build

# App runs at http://localhost:8080
```

---

## Vapi.ai Setup

1. Sign up at [https://vapi.ai](https://vapi.ai)
2. Go to **Phone Numbers** → buy or import a phone number → copy the **Phone Number ID**
3. Go to **Assistants** → create a new assistant
   - Set the first message and system prompt (the system will override these dynamically via `assistantOverrides`)
   - Copy the **Assistant ID**
4. Go to **Settings** → copy your **Private API Key**
5. Configure webhook URL in your assistant settings:
   - URL: `https://your-cloud-run-url/api/webhooks/vapi`
   - Events: `end-of-call-report`
6. Add all values to your `.env` file
7. Update `vapi_assistant_id` in the seed data or directly in MongoDB

---

## Testing with ngrok (Local Webhook Testing)

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Copy the https URL, e.g., https://abc123.ngrok.io
# Set this as your Vapi webhook: https://abc123.ngrok.io/api/webhooks/vapi
```

---

## GCP Cloud Run Deployment

### Prerequisites
- GCP project with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed

### 1. Store secrets in GCP Secret Manager

```bash
# Create each secret
echo -n "your-mongodb-uri" | gcloud secrets create MONGODB_URI --data-file=-
echo -n "your-vapi-key"    | gcloud secrets create VAPI_API_KEY --data-file=-
echo -n "your-openai-key"  | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "your-phone-id"    | gcloud secrets create VAPI_PHONE_NUMBER_ID --data-file=-
```

### 2. Deploy

```bash
# Edit PROJECT_ID in deploy/deploy.sh first
bash deploy/deploy.sh
```

### 3. After deployment

- Copy the Cloud Run URL
- Update your Vapi webhook URL to: `https://your-url.run.app/api/webhooks/vapi`
- Run the database seeder against your Atlas instance:
  ```bash
  MONGODB_URI=your-atlas-uri python -m backend.seed
  ```

---

## Lead Status Flow

```
PENDING → CALL_INITIATED → QUALIFIED
                        → NOT_INTERESTED
                        → NEEDS_REVIEW  (LLM confidence < 60%)
                        → FAILED        (Vapi call error)
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/companies/` | List all companies |
| GET | `/api/leads/?company_id=X` | List leads for a company |
| PATCH | `/api/leads/{id}` | Update lead status manually |
| POST | `/api/campaigns/trigger` | Launch campaign for a company |
| POST | `/api/webhooks/vapi` | Vapi webhook receiver |
| GET | `/api/call-logs/{lead_id}` | Call history for a lead |
| WS | `/ws/updates?company_id=X` | Live status updates |
| GET | `/health` | Health check |

---

## Repository Structure

```
voice-orchestrator/
├── backend/
│   ├── main.py              FastAPI app
│   ├── agents/              LangGraph dispatch + evaluation graphs
│   ├── routers/             API route handlers
│   ├── services/            DB, Vapi, LLM, WebSocket services
│   ├── models/              Pydantic schemas
│   └── seed.py              Database seeder
├── frontend/
│   └── src/
│       ├── components/      React UI components
│       ├── hooks/           useLeads, useWebSocket
│       └── api/             Axios client
├── deploy/
│   ├── nginx.conf           Nginx configuration
│   ├── supervisord.conf     Process supervisor
│   ├── deploy.sh            GCP deploy script
│   └── cloudbuild.yaml      Cloud Build CI/CD
├── Dockerfile               Multi-stage build
├── docker-compose.yml       Local development
└── .env.example             Environment template
```
