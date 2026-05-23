from fastapi import APIRouter

from services.gitagent_loader import list_all_agents, load_agent_manifest, load_agent_system_prompt

router = APIRouter()


@router.get("")
def agents() -> list[dict]:
    return list_all_agents()


@router.get("/{agent_name}")
def agent_detail(agent_name: str) -> dict:
    return {
        "manifest": load_agent_manifest(agent_name),
        "system_prompt": load_agent_system_prompt(agent_name),
    }
