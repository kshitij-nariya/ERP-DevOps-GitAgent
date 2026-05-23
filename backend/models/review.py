from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["CRITICAL", "WARNING", "SUGGESTION"]


class Finding(BaseModel):
    file: str
    line: int
    severity: Severity
    code_snippet: str = ""
    fix: str = ""
    agent: str
    pattern: str | None = None
    vulnerability_type: str | None = None
    issue_type: str | None = None
    explanation: str | None = None
    risk_description: str | None = None
    element: str | None = None


class DocumentationSummary(BaseModel):
    pr_summary: str = ""
    files_changed: list[dict[str, str]] = Field(default_factory=list)
    models_affected: list[str] = Field(default_factory=list)
    views_affected: list[str] = Field(default_factory=list)
    new_dependencies: list[str] = Field(default_factory=list)
    migration_required: bool = False
    migration_notes: str | None = None
    readme_draft: str | None = None


class ReviewReport(BaseModel):
    id: int | None = None
    repo: str
    pr_number: int
    commit_sha: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: float = 0
    files_reviewed: int = 0
    critical_count: int = 0
    warning_count: int = 0
    suggestion_count: int = 0
    critical: list[Finding] = Field(default_factory=list)
    warnings: list[Finding] = Field(default_factory=list)
    suggestions: list[Finding] = Field(default_factory=list)
    documentation: DocumentationSummary | dict[str, Any] = Field(default_factory=DocumentationSummary)
    agent_trail: list[str] = Field(default_factory=list)
    comment_markdown: str = ""
