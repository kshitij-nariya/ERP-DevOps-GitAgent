"use client";

import { AlertTriangle, ShieldAlert, Sparkles } from "lucide-react";
import { useState } from "react";
import type { Finding } from "@/lib/api";

export function FindingsList({
  critical,
  warnings,
  suggestions
}: {
  critical: Finding[];
  warnings: Finding[];
  suggestions: Finding[];
}) {
  const [tab, setTab] = useState<"critical" | "warnings" | "suggestions">("critical");
  const groups = {
    critical: { label: "Critical", items: critical, icon: ShieldAlert },
    warnings: { label: "Warnings", items: warnings, icon: AlertTriangle },
    suggestions: { label: "Suggestions", items: suggestions, icon: Sparkles }
  };
  const selected = groups[tab];
  const Icon = selected.icon;

  return (
    <section className="findings">
      <div className="tabs">
        {Object.entries(groups).map(([key, group]) => (
          <button className={tab === key ? "active" : ""} key={key} onClick={() => setTab(key as typeof tab)}>
            {group.label} <span>{group.items.length}</span>
          </button>
        ))}
      </div>
      <div className="findingList">
        {selected.items.length === 0 ? (
          <div className="empty">
            <Icon size={22} aria-hidden />
            <span>No {selected.label.toLowerCase()} found.</span>
          </div>
        ) : (
          selected.items.map((finding, index) => <FindingCard key={`${finding.file}-${finding.line}-${index}`} finding={finding} />)
        )}
      </div>
    </section>
  );
}

function FindingCard({ finding }: { finding: Finding }) {
  const title = finding.pattern || finding.vulnerability_type || finding.issue_type || "Issue";
  const body = finding.explanation || finding.risk_description || "";
  return (
    <article className={`findingCard ${finding.severity.toLowerCase()}`}>
      <div className="findingHeader">
        <strong>{title}</strong>
        <span>{finding.agent}</span>
      </div>
      <p className="fileLine">{finding.file}:{finding.line}</p>
      {body ? <p>{body}</p> : null}
      {finding.code_snippet ? <pre>{finding.code_snippet}</pre> : null}
      {finding.fix ? <p className="fix">Fix: {finding.fix}</p> : null}
    </article>
  );
}
