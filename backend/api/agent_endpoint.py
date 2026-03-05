"""
Agent API Endpoint
POST /agent — accepts user queries and returns structured navigation responses.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.navigation_agent import run_agent

router = APIRouter()


class AgentRequest(BaseModel):
    query: str


class PlaceResult(BaseModel):
    name: str
    lat: float
    lng: float
    rating: float | None = None
    detour_minutes: float | None = None
    place_id: str | None = None
    address: str | None = None


class RouteResult(BaseModel):
    path: list[dict] | None = None
    distance: str | None = None
    duration: str | None = None


class Suggestion(BaseModel):
    type: str
    name: str
    lat: float
    lng: float
    detour_minutes: float | None = None


class AgentResponse(BaseModel):
    summary: str
    places: list[PlaceResult] = []
    route: RouteResult | None = None
    suggestions: list[Suggestion] = []


@router.post("/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    """
    Receives a natural-language navigation query and returns
    structured route + place results from the AI agent.
    """
    try:
        result = await run_agent(request.query)
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
