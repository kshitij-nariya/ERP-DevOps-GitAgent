"use client";

import { Play, Server } from "lucide-react";
import { useState } from "react";
import { runManualReview, type ReviewReport } from "@/lib/api";

const DEMO_REPOS = [
  {
    label: "Local demo bad patterns",
    url: "../demo/erp-devops-test-repo"
  },
  {
    label: "OCA - account-invoicing",
    url: "https://github.com/OCA/account-invoicing"
  },
  {
    label: "OCA - sale-workflow",
    url: "https://github.com/OCA/sale-workflow"
  }
];

export function ManualTrigger({ onReview }: { onReview: (review: ReviewReport) => void }) {
  const [repoUrl, setRepoUrl] = useState(DEMO_REPOS[0].url);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    setRunning(true);
    setError("");
    try {
      onReview(await runManualReview(repoUrl));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Review failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <section className="trigger">
      <div>
        <h1>ERP DevOps GitAgent</h1>
        <p>GitHub-integrated Odoo review for ORM performance, XML validity, security, and developer documentation.</p>
      </div>
      <div className="triggerRow">
        <Server size={20} aria-hidden />
        <input value={repoUrl} onChange={(event) => setRepoUrl(event.target.value)} aria-label="Repository URL" />
        <button onClick={submit} disabled={running}>
          <Play size={18} aria-hidden />
          {running ? "Running" : "Run Review"}
        </button>
      </div>
      <div className="demoRepos">
        {DEMO_REPOS.map((repo) => (
          <button key={repo.url} type="button" onClick={() => setRepoUrl(repo.url)}>
            {repo.label}
          </button>
        ))}
      </div>
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}
