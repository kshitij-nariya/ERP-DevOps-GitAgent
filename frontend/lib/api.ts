export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Finding {
  file: string;
  line: number;
  severity: "CRITICAL" | "WARNING" | "SUGGESTION";
  pattern?: string;
  vulnerability_type?: string;
  issue_type?: string;
  code_snippet?: string;
  explanation?: string;
  risk_description?: string;
  fix?: string;
  agent: string;
}

export interface ReviewReport {
  id?: number;
  repo: string;
  pr_number: number;
  duration_seconds: number;
  files_reviewed: number;
  critical_count: number;
  warning_count: number;
  suggestion_count: number;
  critical: Finding[];
  warnings: Finding[];
  suggestions: Finding[];
  documentation: { pr_summary?: string };
  agent_trail: string[];
  comment_markdown: string;
}

export async function fetchReviews(): Promise<ReviewReport[]> {
  const response = await fetch(`${API_URL}/api/reviews`, { cache: "no-store" });
  if (!response.ok) return [];
  return response.json();
}

export async function runManualReview(repoUrl: string): Promise<ReviewReport> {
  const response = await fetch(`${API_URL}/webhook/manual-sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl, pr_number: 0 })
  });
  if (!response.ok) throw new Error("Review failed");
  return response.json();
}
