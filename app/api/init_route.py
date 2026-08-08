import uuid
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.persona import PERSONA
from app.core.scheduler import start_scheduler
from app.db.models import insert_agent

router = APIRouter()


class PersonaBody(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    voice: Optional[str] = None


class InitRequest(BaseModel):
    persona: Optional[PersonaBody] = None


@router.post("/api/agent/init")
def init_agent(body: Optional[InitRequest] = None):
    persona = PERSONA.copy()

    if body and body.persona:
        if body.persona.name is not None:
            persona["name"] = body.persona.name
        if body.persona.domain is not None:
            persona["domain"] = body.persona.domain
        if body.persona.voice is not None:
            persona["voice"] = body.persona.voice

    agent_id = str(uuid.uuid4())[:8]
    insert_agent(agent_id, persona["name"], persona["domain"], persona["voice"])
    start_scheduler(agent_id)
    return {"agentId": agent_id}
