from __future__ import annotations

import os
from typing import Any

import httpx

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def format_pr_comment(report: dict[str, Any]) -> str:
    lines = ["## ERP DevOps GitAgent Review", ""]
    lines.append(
        f"Files reviewed: **{report['files_reviewed']}** | Duration: **{report['duration_seconds']}s**"
    )
    if report["critical_count"]:
        status = "Action Required"
    elif report["warning_count"]:
        status = "Review Suggested"
    else:
        status = "Looks Good"
    lines.append(f"Status: **{status}**")
    lines.append(
        f"Critical: **{report['critical_count']}** | Warnings: **{report['warning_count']}** | Suggestions: **{report['suggestion_count']}**"
    )

    if report["critical"]:
        lines.extend(["", "### Critical Issues"])
        for finding in report["critical"]:
            title = finding.get("pattern") or finding.get("vulnerability_type") or finding.get("issue_type") or "Issue"
            lines.append(f"- **{finding.get('file')}:{finding.get('line')}** - {title}")
            snippet = finding.get("code_snippet") or finding.get("element") or ""
            if snippet:
                lines.append(f"```python\n{snippet}\n```")
            detail = finding.get("explanation") or finding.get("risk_description") or ""
            if detail:
                lines.append(detail)
            lines.append(f"Fix: {finding.get('fix', '')}")

    if report["warnings"]:
        lines.extend(["", "### Warnings"])
        for finding in report["warnings"][:8]:
            title = finding.get("pattern") or finding.get("vulnerability_type") or finding.get("issue_type") or "Issue"
            lines.append(f"- **{finding.get('file')}:{finding.get('line')}** - {title}")

    docs = report.get("documentation") or {}
    if docs.get("pr_summary"):
        lines.extend(["", "### PR Summary", docs["pr_summary"]])

    lines.extend(["", "---", "Powered by ERP DevOps GitAgent."])
    return "\n".join(lines)


async def post_pr_comment(repo_full_name: str, pr_number: int, report: dict[str, Any]) -> dict[str, Any]:
    if not GITHUB_TOKEN or pr_number <= 0:
        return {"status": "skipped", "reason": "missing_github_token_or_pr_number"}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments",
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json",
                },
                json={"body": format_pr_comment(report)},
            )
        if response.status_code >= 400:
            return {"status": "error", "http_status": response.status_code, "body": response.text}
        return {"status": "posted", "http_status": response.status_code}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
