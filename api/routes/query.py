"""FastAPI routes for navigation queries.

v2 adds:
- Fix 1: Voice failure UX — 422 with multilingual error on empty transcription
- Fix 6: QR URL parameter — GET /locations/{node_id}/display
- Updated response shape with all v2 fields
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Request, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from core.config import Config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


class TextQueryRequest(BaseModel):
    """Request body for text navigation queries."""
    query: str
    current_node: Optional[str] = None
    language_override: Optional[str] = None


class QRQueryRequest(BaseModel):
    """Request body for QR code location queries."""
    qr_data: str


def _build_response(result: dict, start_time: float, current_location: str) -> dict:
    """Build the standard v2 API response from workflow output.

    Args:
        result: Output from the LangGraph workflow.
        start_time: time.time() at request start.
        current_location: The starting node used for this query.

    Returns:
        Dict matching the v2 API response shape.
    """
    latency_ms = (time.time() - start_time) * 1000
    return {
        "directions":              result.get("directions_text", ""),
        "destination":             result.get("destination_display_name", ""),
        "destination_node_id":     result.get("resolved_node_id", ""),
        "detected_language":       result.get("detected_language", "en"),
        "path_nodes":              result.get("path_nodes", []),
        "warnings":                result.get("warnings", []),
        "latency_ms":              round(latency_ms, 2),
        "low_confidence":          result.get("low_confidence", False),
        "rephrase_message":        result.get("rephrase_message"),
        "is_multi_destination":    result.get("is_multi_destination", False),
        "requires_disambiguation": result.get("requires_disambiguation", False),
        "disambiguation_question": result.get("disambiguation_question"),
        "disambiguation_options":  result.get("disambiguation_options"),
        "current_location_used":   current_location,
        "path_error":              result.get("path_error"),
    }


@router.post("/text")
async def query_text(
    request: Request,
    body: TextQueryRequest,
    navcore_location: Optional[str] = Cookie(default=None),
) -> JSONResponse:
    """Process a text navigation query through the full workflow.

    Location priority: body.current_node > cookie > Config.DEFAULT_START_NODE

    Args:
        request: FastAPI request object.
        body: TextQueryRequest with query, optional node, optional language.
        navcore_location: Cookie tracking patient's last known location.

    Returns:
        JSON response with all v2 fields.
    """
    start_time = time.time()
    workflow = request.app.state.workflow

    current_location = (
        body.current_node
        or navcore_location
        or Config.DEFAULT_START_NODE
    )

    initial_state = {
        "query_text": body.query,
        "input_modality": "text",
        "current_location": current_location,
    }

    if body.language_override:
        initial_state["detected_language"] = body.language_override

    # Keep CPU-heavy embedding inference off the event loop so health checks
    # and other requests remain responsive while a route is being resolved.
    result = await run_in_threadpool(workflow.invoke, initial_state)
    latency_ms = (time.time() - start_time) * 1000
    logger.info(
        f"Text query processed in {latency_ms:.0f}ms | "
        f"from={current_location} | dest={result.get('resolved_node_id')}"
    )

    # Fix 9: Log query
    from api.main import log_query
    log_query(
        request,
        query_text=body.query,
        language=result.get("detected_language", "en"),
        destination=result.get("resolved_node_id", ""),
        success=bool(result.get("path_nodes")),
        latency_ms=latency_ms,
    )

    response_data = _build_response(result, start_time, current_location)
    response = JSONResponse(content=response_data)

    # Update location cookie — patient is now at destination
    if result.get("path_nodes"):
        response.set_cookie(
            key="navcore_location",
            value=result["path_nodes"][-1],
            max_age=3600,
            httponly=True,
        )
    return response


@router.post("/audio")
async def query_audio(
    request: Request,
    file: UploadFile = File(...),
    current_node: Optional[str] = Form(default=None),
    navcore_location: Optional[str] = Cookie(default=None),
) -> JSONResponse:
    """Process an audio navigation query using Whisper transcription.

    Fix 1: Returns 422 with multilingual error on empty or invalid transcription.

    Args:
        request: FastAPI request object.
        file: Uploaded audio file (webm/WAV/MP3).
        navcore_location: Cookie tracking patient's last known location.

    Returns:
        JSON response with transcribed text and directions.
    """
    start_time = time.time()

    max_audio_bytes = 16 * 1024 * 1024
    content = await file.read(max_audio_bytes + 1)
    if not content:
        return JSONResponse(status_code=422, content={
            "error": "empty_audio",
            "message": "No audio was received. Please record your query again.",
        })
    if len(content) > max_audio_bytes:
        return JSONResponse(status_code=413, content={
            "error": "audio_too_large",
            "message": "That recording is too large. Please keep it under 12 seconds and try again.",
        })

    suffix = Path(file.filename or "audio.webm").suffix.lower()
    if suffix not in {".webm", ".wav", ".mp3", ".m4a", ".mp4", ".ogg"}:
        suffix = ".webm"
    tmp_path = None
    transcribed_text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        from agents.input_processor import transcribe_audio, is_valid_transcription
        t0 = time.time()
        raw_text = await run_in_threadpool(transcribe_audio, tmp_path)
        t_transcribe = (time.time() - t0) * 1000
        logger.info(f"Transcription took {t_transcribe:.0f}ms: '{raw_text[:60]}'")

        # Fix 1: Validate transcription before proceeding
        if not is_valid_transcription(raw_text):
            logger.warning(f"Invalid transcription: '{raw_text}'")
            return JSONResponse(
                status_code=422,
                content={
                    "error": "audio_unclear",
                    "message": "Could not understand the audio. Please type your query.",
                    "message_hi": "Aawaz samajh nahi aayi. Kripya type karein.",
                    "message_mr": "आवाज कळली नाही. कृपया टाइप करा.",
                    "message_hi_mix": "Audio clear nahi tha. Please type karein.",
                },
            )

        transcribed_text = raw_text

    except Exception:
        logger.exception("Audio transcription failed")
        return JSONResponse(
            status_code=503,
            content={
                "error": "transcription_unavailable",
                "message": "NavCore could not transcribe this recording. Please try again or type your query.",
                "message_hi": "Aawaz samajh nahi aayi. Kripya type karein.",
                "message_mr": "आवाज कळली नाही. कृपया टाइप करा.",
                "message_hi_mix": "Audio process nahi ho saka. Please type karein.",
            },
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Run navigation workflow on transcribed text
    workflow = request.app.state.workflow
    current_location = current_node or navcore_location or Config.DEFAULT_START_NODE

    initial_state = {
        "query_text": transcribed_text,
        "input_modality": "text",
        "current_location": current_location,
    }
    try:
        result = await run_in_threadpool(workflow.invoke, initial_state)
    except Exception:
        logger.exception("Navigation workflow failed for transcribed audio")
        return JSONResponse(
            status_code=500,
            content={
                "error": "navigation_failed",
                "message": "Your voice was transcribed, but NavCore could not finish the route. Showing the recognized words for another try.",
                "transcribed_text": transcribed_text,
            },
        )

    latency_ms = (time.time() - start_time) * 1000
    logger.info(f"Audio query total: {latency_ms:.0f}ms")

    response_data = _build_response(result, start_time, current_location)
    response_data["transcribed_text"] = transcribed_text

    response = JSONResponse(content=response_data)
    if result.get("path_nodes"):
        response.set_cookie(
            key="navcore_location",
            value=result["path_nodes"][-1],
            max_age=3600,
            httponly=True,
        )
    return response


@router.post("/qr")
async def query_qr(request: Request, body: QRQueryRequest) -> JSONResponse:
    """Parse QR scan and update the patient's location cookie.

    Args:
        request: FastAPI request object.
        body: QRQueryRequest with raw QR string.

    Returns:
        JSON with confirmed location. Sets navcore_location cookie.
    """
    from agents.input_processor import parse_qr_code

    qr_result = parse_qr_code(body.qr_data)
    location = qr_result.get("current_location")

    display_name = ""
    graph = request.app.state.graph
    if location and location in graph.graph:
        display_name = graph.get_node_data(location).get("display_name", location)

    logger.info(f"QR scan: location={location}, name={display_name}")

    response_data = {
        "current_location": location,
        "display_name": display_name,
        "confirmed": location is not None,
        "message": (
            f"Location set to {display_name}. "
            "You can now ask for directions from here."
        ) if location else "QR code not recognized",
    }

    response = JSONResponse(content=response_data)
    if location:
        response.set_cookie(
            key="navcore_location",
            value=location,
            max_age=3600,
            httponly=True,
        )
    return response
