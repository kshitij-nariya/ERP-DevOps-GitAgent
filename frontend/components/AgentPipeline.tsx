import { Bot, CheckCircle2 } from "lucide-react";

const AGENTS = [
  ["orm-performance", "ORM"],
  ["xml-validator", "XML"],
  ["security-reviewer", "Security"],
  ["documentation", "Docs"]
] as const;

export function AgentPipeline({ trail }: { trail: string[] }) {
  return (
    <section className="pipeline" aria-label="Agent pipeline">
      {AGENTS.map(([id, label], index) => {
        const done = trail.includes(id);
        return (
          <div className="pipelineItem" key={id}>
            <div className={done ? "agentBox done" : "agentBox"}>
              {done ? <CheckCircle2 size={20} aria-hidden /> : <Bot size={20} aria-hidden />}
              <span>{label}</span>
            </div>
            {index < AGENTS.length - 1 ? <span className="connector" aria-hidden /> : null}
          </div>
        );
      })}
    </section>
  );
}
