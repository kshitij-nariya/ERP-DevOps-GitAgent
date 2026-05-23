from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_GITAGENT_ROOT = Path(__file__).resolve().parents[2] / "erp-devops-agent"
GITAGENT_ROOT = Path(os.environ.get("GITAGENT_PATH", str(DEFAULT_GITAGENT_ROOT))).resolve()


def _agent_path(agent_name: str) -> Path:
    return GITAGENT_ROOT if agent_name == "orchestrator" else GITAGENT_ROOT / "agents" / agent_name


def load_agent_system_prompt(agent_name: str) -> str:
    agent_path = _agent_path(agent_name)
    parts = []
    for filename in ("SOUL.md", "RULES.md"):
        path = agent_path / filename
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))

    knowledge_map = {
        "orm-performance": ["odoo-antipatterns.md"],
        "xml-validator": ["xml-best-practices.md", "odoo-antipatterns.md"],
        "security-reviewer": ["security-checklist.md", "odoo-antipatterns.md"],
        "documentation": [],
        "orchestrator": ["odoo-antipatterns.md", "security-checklist.md"],
    }
    for filename in knowledge_map.get(agent_name, []):
        path = GITAGENT_ROOT / "knowledge" / filename
        if path.exists():
            parts.append("## Reference Knowledge\n" + path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def load_agent_manifest(agent_name: str) -> dict[str, Any]:
    path = _agent_path(agent_name) / "agent.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def list_all_agents() -> list[dict[str, Any]]:
    agents_root = GITAGENT_ROOT / "agents"
    if not agents_root.exists():
        return []
    agents = []
    for child in sorted(agents_root.iterdir()):
        if not child.is_dir():
            continue
        manifest = load_agent_manifest(child.name)
        manifest["name"] = manifest.get("name", child.name)
        manifest["path"] = str(child.relative_to(GITAGENT_ROOT))
        manifest["system_prompt_preview"] = load_agent_system_prompt(child.name)[:600]
        agents.append(manifest)
    return agents
