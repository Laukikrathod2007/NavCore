"""FastAPI routes for admin operations.

v2 adds:
- GET /admin/query-log — in-memory query history
- GET /locations/{node_id}/display — node display name for QR URL (Fix 6)
"""

import logging
import json
from typing import Optional

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from core.config import Config

logger = logging.getLogger(__name__)
router = APIRouter(tags=["admin"])

_connected_navcores: list[WebSocket] = []


class AvailabilityUpdate(BaseModel):
    """Request body for updating node availability."""
    is_available: bool
    reason: Optional[str] = None


@router.patch("/locations/{node_id}/availability")
async def update_availability(
    request: Request,
    node_id: str,
    body: AvailabilityUpdate,
) -> dict:
    """Update a location's availability status and broadcast to navcores.

    Args:
        request: FastAPI request object.
        node_id: The node ID to update.
        body: AvailabilityUpdate with is_available and optional reason.

    Returns:
        Dict with success status and broadcast confirmation.
    """
    qdrant = request.app.state.qdrant
    graph = request.app.state.graph

    # Update in-memory graph node
    if node_id in graph.graph:
        graph.graph.nodes[node_id]["is_available"] = body.is_available
        if body.reason:
            graph.graph.nodes[node_id]["unavailability_reason"] = body.reason

    # Update Qdrant payload
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        results = qdrant.client.query_points(
            collection_name=Config.TOPOLOGICAL_COLLECTION,
            query=None,
            query_filter=Filter(
                must=[FieldCondition(key="node_id", match=MatchValue(value=node_id))]
            ),
            limit=1,
        )
        if results.points:
            point_id = results.points[0].id
            payload_update = {"is_available": body.is_available}
            if body.reason:
                payload_update["unavailability_reason"] = body.reason
            qdrant.update_payload(Config.TOPOLOGICAL_COLLECTION, point_id, payload_update)
    except Exception as e:
        logger.error(f"Failed to update Qdrant payload: {e}")

    broadcast_msg = {
        "type": "availability_update",
        "node_id": node_id,
        "is_available": body.is_available,
        "reason": body.reason,
    }
    await _broadcast_to_navcores(broadcast_msg)

    return {"success": True, "broadcast_sent": len(_connected_navcores) > 0}


@router.get("/locations")
async def list_locations(request: Request) -> dict:
    """List all locations with current availability status.

    Returns:
        Dict with list of all nodes and their metadata.
    """
    graph = request.app.state.graph
    locations = []
    for node_id in graph.get_all_nodes():
        data = graph.get_node_data(node_id)
        locations.append({
            "node_id": node_id,
            "display_name": data.get("display_name", node_id),
            "floor": data.get("floor"),
            "wing": data.get("wing"),
            "node_type": data.get("node_type"),
            "is_available": data.get("is_available", True),
            "timing": data.get("timing", ""),
        })

    return {"locations": locations, "total": len(locations)}


@router.get("/locations/{node_id}/display")
async def get_location_display(request: Request, node_id: str) -> dict:
    """Get the display name for a node ID (Fix 6 — QR URL support).

    QR codes encode node IDs. When a patient scans a QR code, the
    frontend calls this endpoint to show the human-readable location name.

    Args:
        request: FastAPI request object.
        node_id: Node ID to look up (e.g. "floor_3_corridor_A").

    Returns:
        Dict with node_id, display_name, floor, and confirmation.
    """
    graph = request.app.state.graph

    if node_id not in graph.graph:
        return {
            "node_id": node_id,
            "display_name": node_id.replace("_", " ").title(),
            "floor": None,
            "confirmed": False,
            "message": f"Node '{node_id}' not found in hospital map",
        }

    data = graph.get_node_data(node_id)
    return {
        "node_id": node_id,
        "display_name": data.get("display_name", node_id),
        "floor": data.get("floor"),
        "wing": data.get("wing"),
        "node_type": data.get("node_type"),
        "confirmed": True,
        "message": f"Location confirmed: {data.get('display_name', node_id)}",
    }


@router.get("/admin/query-log")
async def get_query_log(request: Request) -> dict:
    """Return the last 100 queries processed (Fix 9 — Query History).

    This endpoint shows what patients are actually asking — invaluable
    for expanding aliases and fixing failures.

    Returns:
        Dict with recent queries, language breakdown, and failure rate.
    """
    log = list(request.app.state.query_log)

    # Basic analytics
    total = len(log)
    if total == 0:
        return {"queries": [], "total": 0, "analytics": {}}

    successes = sum(1 for q in log if q.get("success"))
    lang_counts: dict = {}
    dest_counts: dict = {}
    failures = []

    for q in log:
        lang = q.get("language", "unknown")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

        dest = q.get("destination")
        if dest:
            dest_counts[dest] = dest_counts.get(dest, 0) + 1

        if not q.get("success"):
            failures.append({
                "query": q.get("query"),
                "language": q.get("language"),
                "timestamp": q.get("timestamp"),
            })

    analytics = {
        "total_queries": total,
        "success_rate": round(successes / total, 3),
        "language_distribution": lang_counts,
        "top_destinations": sorted(
            dest_counts.items(), key=lambda x: x[1], reverse=True
        )[:5],
        "failure_count": total - successes,
        "recent_failures": failures[-10:],
    }

    return {
        "queries": log[-100:],
        "total": total,
        "analytics": analytics,
    }


@router.websocket("/ws/navcore")
async def navcore_websocket(websocket: WebSocket) -> None:
    """WebSocket for real-time navcore availability updates.

    Args:
        websocket: The WebSocket connection.
    """
    await websocket.accept()
    _connected_navcores.append(websocket)
    logger.info(f"NavCore connected. Total: {len(_connected_navcores)}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _connected_navcores.remove(websocket)
        logger.info(f"NavCore disconnected. Total: {len(_connected_navcores)}")


async def _broadcast_to_navcores(message: dict) -> None:
    """Broadcast a message to all connected navcores.

    Args:
        message: Dict to send as JSON.
    """
    msg_str = json.dumps(message)
    for navcore in _connected_navcores[:]:
        try:
            await navcore.send_text(msg_str)
        except Exception as e:
            logger.error(f"Failed to send to navcore: {e}")
            _connected_navcores.remove(navcore)
