"""FastAPI health check route.

GET /health — returns system status including Qdrant, Ollama, and
graph health.
"""

import logging

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(request: Request) -> dict:
    """Check system health: Qdrant connection, graph loaded, model status.

    Args:
        request: FastAPI request object.

    Returns:
        Dict with status for each component.
    """
    result = {
        "status": "ok",
        "qdrant_ok": False,
        "graph_ok": False,
        "ollama_ok": False,
    }

    # Check Qdrant
    try:
        qdrant = request.app.state.qdrant
        qdrant.client.get_collections()
        result["qdrant_ok"] = True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        result["status"] = "degraded"

    # Check graph
    try:
        graph = request.app.state.graph
        if graph.get_all_nodes():
            result["graph_ok"] = True
    except Exception as e:
        logger.error(f"Graph health check failed: {e}")
        result["status"] = "degraded"

    # Check Ollama
    try:
        ollama = request.app.state.ollama
        if ollama and ollama.check_health():
            result["ollama_ok"] = True
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
        # Ollama is optional (fallback directions work without it)

    if not result["qdrant_ok"] or not result["graph_ok"]:
        result["status"] = "unhealthy"

    return result
