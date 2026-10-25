
"""FastAPI routes for the deterministic grounded data assistant."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from assistant.core.assistant_service import answer_question


router = APIRouter(prefix="/api/assistant", tags=["Grounded Data Assistant"])


class AssistantQuestion(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="A question supported by the approved intelligence outputs.",
    )


class AssistantResponse(BaseModel):
    status: str
    answer: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    validation: dict[str, Any] = Field(default_factory=dict)
    details: dict[str, Any] | None = None
    evidence_package: dict[str, Any] | None = None
    grounding: dict[str, Any] | None = None
    explanation: dict[str, Any] | None = None


@router.post("/ask", response_model=AssistantResponse)
def ask_grounded_assistant(request: AssistantQuestion) -> dict[str, Any]:
    """Answer one supported question using approved output files only."""
    try:
        return answer_question(request.question)
    except Exception as exc:
        # Keep internals and configuration out of the public error response.
        # The application logging layer can record the exception separately.
        raise HTTPException(
            status_code=500,
            detail="The grounded assistant could not process this request safely.",
        ) from exc



@router.get("/health")
def assistant_health() -> dict[str, str | bool]:
    """Report assistant mode and Gemini configuration status."""
    import os

    return {
        "status": "available",
        "mode": "deterministic_plus_llm_explanation",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
    }
