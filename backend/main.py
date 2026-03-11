"""
AI Navigation Copilot — FastAPI Entry Point
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.agent_endpoint import router as agent_router


load_dotenv()

@app.get("/")
def root():
    return {
        "title": "AI Navigation Copilot",
        "description": "Multimodal AI agent for route-aware navigation assistance",
        "version": "0.1.0",
    }

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
