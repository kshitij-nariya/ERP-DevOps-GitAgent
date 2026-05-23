from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import create_db_and_tables
from routers import agents, reviews, webhook

app = FastAPI(
    title="ERP DevOps GitAgent",
    description="Multi-agent code review for Odoo/ERP repositories",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    create_db_and_tables()


app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "erp-devops-gitagent"}
