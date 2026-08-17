from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.business.mcp_runtime import create_business_mcp_client
from backend.data_access.config import SQLAnywhereSettings
from backend.llm.session_chat import create_session_manager
from backend.llm.visualizations import build_visualization


class SessionResponse(BaseModel):
    session_id: str
    created_at: str


class MessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    session_id: str
    response: str
    visualization: Dict[str, Any] | None = None


class ToolResponse(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]


app = FastAPI(title="Executive MCP Chatbot API", version="0.1.0")
logger = logging.getLogger("executive_chatbot.api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
session_manager = create_session_manager()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat/sessions", response_model=SessionResponse, status_code=201)
def create_session() -> SessionResponse:
    session = session_manager.create()
    return SessionResponse(session_id=session.session_id, created_at=session.created_at.isoformat())


@app.get("/api/chat/sessions/{session_id}")
def get_session(session_id: str) -> Dict[str, Any]:
    try:
        session = session_manager.get(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"session_id": session.session_id, "created_at": session.created_at.isoformat(), "messages": session.messages}


@app.post("/api/chat/sessions/{session_id}/messages", response_model=MessageResponse)
def send_message(session_id: str, request: MessageRequest) -> MessageResponse:
    try:
        response = session_manager.get(session_id).send(request.content)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=502, detail="Chat provider or tool error") from exc
    visualization = None
    for tool_result in session_manager.get(session_id).last_tool_results:
        visualization = build_visualization(tool_result["name"], tool_result["result"])
        if visualization:
            break
    return MessageResponse(session_id=session_id, response=response, visualization=visualization)


@app.delete("/api/chat/sessions/{session_id}", status_code=204, response_class=Response)
def delete_session(session_id: str) -> Response:
    session_manager.delete(session_id)
    return Response(status_code=204)


@app.get("/api/mcp/tools", response_model=List[ToolResponse])
def list_tools() -> List[ToolResponse]:
    try:
        settings = SQLAnywhereSettings.from_env()
        _, definitions = create_business_mcp_client(settings)
        return [ToolResponse(**definition) for definition in definitions]
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail="Business tools are unavailable") from exc
