from __future__ import annotations

import time
from datetime import datetime
import os
from pathlib import Path
from typing import Any

from db.database import save_review
from services.github_service import format_pr_comment, post_pr_comment
from services.local_analyzer import analyze_orm, analyze_security, analyze_xml, generate_documentation
from services.repo_service import get_repo_data


async def run_review_pipeline(
    repo_url: str,
    pr_number: int,
    head_sha: str,
    base_sha: str,
    repo_full_name: str,
) -> dict[str, Any]:
    start_time = time.time()
    repo_data = get_repo_data(repo_url, head_sha, base_sha, repo_full_name, pr_number)
    file_contents = repo_data["file_contents"]

    orm_findings = analyze_orm(file_contents)
    security_findings = analyze_security(file_contents)
    xml_findings = analyze_xml(file_contents)
    all_findings = orm_findings + security_findings + xml_findings

    critical = [item for item in all_findings if item["severity"] == "CRITICAL"]
    warnings = [item for item in all_findings if item["severity"] == "WARNING"]
    suggestions = [item for item in all_findings if item["severity"] == "SUGGESTION"]
    docs = generate_documentation(repo_full_name, pr_number, repo_data)

    report = {
        "repo": repo_full_name,
        "pr_number": pr_number,
        "commit_sha": head_sha,
        "base_sha": base_sha,
        "created_at": datetime.utcnow().isoformat(),
        "duration_seconds": round(time.time() - start_time, 2),
        "files_reviewed": len(repo_data["changed_files"]),
        "critical_count": len(critical),
        "warning_count": len(warnings),
        "suggestion_count": len(suggestions),
        "critical": critical,
        "warnings": warnings,
        "suggestions": suggestions,
        "documentation": docs,
        "agent_trail": _agent_trail(repo_data),
    }
    report["comment_markdown"] = format_pr_comment(report)
    github_comment_status = {"status": "skipped", "reason": "not_attempted"}
    if pr_number > 0 and repo_full_name:
        github_comment_status = await post_pr_comment(repo_full_name, pr_number, report)
    report["github_comment_status"] = github_comment_status

    review_id = save_review(report)
    report["id"] = review_id

    write_to_memory(report)

    return report


def write_to_memory(report: dict[str, Any]) -> None:
    default_gitagent_root = Path(__file__).resolve().parents[2] / "erp-devops-agent"
    gitagent_root = Path(os.environ.get("GITAGENT_PATH", str(default_gitagent_root)))
    memory_file = gitagent_root / "memory" / "runtime" / "reviews.md"
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    entry = (
        f"\n## Review: {report['repo']} PR #{report['pr_number']}\n"
        f"- Timestamp: {report['created_at']}\n"
        f"- Files reviewed: {report['files_reviewed']}\n"
        f"- Critical: {report['critical_count']} | Warnings: {report['warning_count']}\n"
        f"- Agents run: {', '.join(report['agent_trail'])}\n"
        f"- Duration: {report['duration_seconds']}s\n"
    )
    with memory_file.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def _agent_trail(repo_data: dict[str, Any]) -> list[str]:
    agents = []
    if repo_data["python_files"]:
        agents.extend(["orm-performance", "security-reviewer"])
    if repo_data["xml_files"]:
        agents.append("xml-validator")
    agents.append("documentation")
    return agents
