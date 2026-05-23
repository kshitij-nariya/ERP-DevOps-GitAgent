# ERP DevOps GitAgent

Automated code review for Odoo/ERP repositories using GitAgent-defined agents.
It detects ORM performance issues, XML validation risks, security
vulnerabilities, and generates developer documentation.

## What Was Built

- `erp-devops-agent/`: GitAgent repository with orchestrator and specialist agents.
- `backend/`: FastAPI service for webhooks, manual review, GitHub comments, SQLite history, and agent metadata.
- `frontend/`: Next.js dashboard with manual trigger, agent pipeline, findings tabs, and PR comment preview.
- `demo/erp-devops-test-repo/`: Odoo demo module containing intentional bad patterns.
- `docker-compose.yml`: Runs backend and frontend together.

## Agents

| Agent | Detects |
|---|---|
| ORM Performance | `search()` in loops, `write()` in loops, browse prefetch issues |
| XML Validator | malformed XML, fragile XPath, duplicate XML IDs, unsafe `t-raw` |
| Security Reviewer | unrestricted `sudo()`, SQL injection, public route risks |
| Documentation | PR summary, changed file overview, migration notes |

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- Agent definitions: http://localhost:8000/api/agents

## Local Demo Without Docker

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then run:

```bash
curl -X POST http://localhost:8000/webhook/manual-sync \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"../demo/erp-devops-test-repo","pr_number":0}'
```

## GitAgent CLI

If the GitAgent CLI is installed:

```bash
cd erp-devops-agent
gitagent validate
gitagent info
gitagent export --format system-prompt
```

## Notes

The backend includes deterministic local analyzers so the demo works without an
LLM key. The GitAgent files are still loaded by `/api/agents` and can be used as
system prompts when `ANTHROPIC_API_KEY` is configured.
