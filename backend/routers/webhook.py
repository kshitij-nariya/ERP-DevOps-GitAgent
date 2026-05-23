from __future__ import annotations

import hashlib
import hmac
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from models.webhook import ManualReviewRequest
from services.review_pipeline import run_review_pipeline

router = APIRouter()


def verify_github_signature(payload: bytes, signature: str) -> bool:
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode()
    expected = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if os.environ.get("GITHUB_WEBHOOK_SECRET") and not verify_github_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    data = await request.json()
    if event_type == "pull_request" and data.get("action") in {"opened", "synchronize", "reopened"}:
        pr = data["pull_request"]
        background_tasks.add_task(
            run_review_pipeline,
            data["repository"]["clone_url"],
            pr["number"],
            pr["head"]["sha"],
            pr["base"]["sha"],
            data["repository"]["full_name"],
        )
        return {"status": "review_queued", "pr": pr["number"]}
    return {"status": "ignored", "event": event_type}


@router.post("/manual")
async def manual_trigger(payload: ManualReviewRequest, background_tasks: BackgroundTasks) -> dict:
    repo_full_name = payload.repo_url.split("github.com/")[-1].removesuffix(".git")
    background_tasks.add_task(
        run_review_pipeline,
        payload.repo_url,
        payload.pr_number,
        payload.head_sha,
        payload.base_sha,
        repo_full_name,
    )
    return {"status": "review_queued", "repo": payload.repo_url}


@router.post("/manual-sync")
async def manual_trigger_sync(payload: ManualReviewRequest) -> dict:
    repo_full_name = payload.repo_url.split("github.com/")[-1].removesuffix(".git")
    return await run_review_pipeline(
        payload.repo_url,
        payload.pr_number,
        payload.head_sha,
        payload.base_sha,
        repo_full_name,
    )
