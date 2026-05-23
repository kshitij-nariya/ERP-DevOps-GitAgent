from __future__ import annotations

import asyncio
import hashlib
import hmac
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from models.webhook import ManualReviewRequest
from services.review_pipeline import run_review_pipeline

router = APIRouter()


async def queue_review(
    repo_url: str,
    pr_number: int,
    head_sha: str,
    base_sha: str,
    repo_full_name: str,
) -> None:
    try:
        await run_review_pipeline(repo_url, pr_number, head_sha, base_sha, repo_full_name)
    except Exception as exc:
        print(
            f"Review pipeline failed for {repo_full_name} PR #{pr_number} "
            f"({head_sha[:7]}): {exc}"
        )


def verify_github_signature(payload: bytes, signature: str) -> bool:
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode()
    expected = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def github_webhook(request: Request) -> dict:
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if os.environ.get("GITHUB_WEBHOOK_SECRET") and not verify_github_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    data = await request.json()
    action = data.get("action")

    if event_type == "pull_request" and action in {"opened", "synchronize", "reopened"}:
        pr = data["pull_request"]
        asyncio.create_task(
            queue_review(
                data["repository"]["clone_url"],
                pr["number"],
                pr["head"]["sha"],
                pr["base"]["sha"],
                data["repository"]["full_name"],
            )
        )
        return {
            "status": "review_queued",
            "event": event_type,
            "action": action,
            "repo": data["repository"]["full_name"],
            "pr": pr["number"],
        }

    return {"status": "ignored", "event": event_type, "action": action}


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
