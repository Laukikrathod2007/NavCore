"""FastAPI application for NavCore.

v2 adds:
- Fix 9: In-memory query log (deque, last 100 queries)
- Startup graph connectivity check
- Workflow dependency injection for secondary destination lookup
- Query log appended after every /query/text and /query/audio request
"""

import logging
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from core.config import Config, setup_logging
from api.routes import query, admin, health

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all NavCore infrastructure on startup.

    Creates and injects:
    - QdrantManager, EmbeddingManager, OllamaManager, SpatialGraph
    - All agent node dependencies
    - Compiled LangGraph workflow
    - In-memory query log
    - Startup graph connectivity check
    """
    setup_logging()
    logger.info("NavCore v2 starting up...")

    from core.qdrant_client import QdrantManager
    from core.embeddings import EmbeddingManager
    from core.ollama_client import OllamaManager
    from core.graph import SpatialGraph
    from agents import retrieval, path_planner, direction_generator, disambiguation
    from agents.workflow import build_workflow, init_workflow_dependencies
    from ingestion.ingest import run_ingestion

    # Infrastructure
    qdrant = QdrantManager()
    embedder = EmbeddingManager()
    graph = SpatialGraph()
    graph.load_from_json(f"{Config.DATA_DIR}/graph.json")

    # Optional Ollama
    ollama = None
    try:
        ollama = OllamaManager()
    except Exception as e:
        logger.warning(f"Ollama not available, using fallback: {e}")

    # Run ingestion if empty
    topo_count = qdrant.count_points(Config.TOPOLOGICAL_COLLECTION)
    if topo_count == 0:
        logger.info("Qdrant collections empty, running ingestion...")
        run_ingestion(Config.DATA_DIR, qdrant, embedder)
    else:
        logger.info(f"Qdrant already has {topo_count} topological nodes")

    # Inject dependencies into agents
    retrieval.init_retrieval(qdrant, embedder)
    path_planner.init_path_planner(graph)
    direction_generator.init_direction_generator(ollama, graph)
    disambiguation.init_disambiguation(graph)

    # Pre-warm Whisper at startup so first voice query is fast
    try:
        from agents.input_processor import _get_whisper_model
        logger.info(f"Pre-loading Whisper {Config.WHISPER_MODEL} model...")
        _get_whisper_model()
        logger.info("Whisper model pre-loaded and ready")
    except Exception as e:
        logger.warning(f"Whisper pre-load skipped: {e}")

    # Startup graph connectivity check (Fix 2)
    logger.info("Checking graph connectivity from default start node...")
    unreachable = []
    for node_id in graph.get_all_nodes():
        try:
            path = graph.find_shortest_path(Config.DEFAULT_START_NODE, node_id)
            if not path:
                unreachable.append(node_id)
        except KeyError:
            unreachable.append(node_id)

    if unreachable:
        logger.warning(
            f"UNREACHABLE NODES from {Config.DEFAULT_START_NODE}: {unreachable}. "
            "Fix graph.json to ensure all nodes are connected."
        )
    else:
        logger.info(
            f"Graph connectivity OK — all {len(graph.get_all_nodes())} nodes reachable"
        )

    # Build workflow + inject dependencies for secondary destination lookup
    init_workflow_dependencies(embedder, qdrant)
    workflow = build_workflow()

    # In-memory query log (Fix 9)
    query_log = deque(maxlen=100)

    # Store everything in app state
    app.state.workflow = workflow
    app.state.qdrant = qdrant
    app.state.graph = graph
    app.state.ollama = ollama
    app.state.query_log = query_log

    logger.info("NavCore v2 startup complete")
    yield
    logger.info("NavCore shutting down")


app = FastAPI(
    title="NavCore v2",
    description="Offline dual-memory spatial RAG for multilingual indoor navigation",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(admin.router)
app.include_router(health.router)


@app.middleware("http")
async def log_query_middleware(request: Request, call_next):
    """Middleware to log every navigation query (Fix 9).

    Only logs /query/text and /query/audio requests.
    Appends to the in-memory query_log deque.
    """
    response = await call_next(request)

    if request.url.path in ("/query/text", "/query/audio"):
        try:
            # We can only read body in middleware if we buffer it — instead
            # we log what we can from the response headers and app state.
            # The actual query text is logged by the route handler.
            # Here we log the timestamp and path for analytics.
            if hasattr(app.state, "query_log"):
                app.state.query_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "path": request.url.path,
                    "status_code": response.status_code,
                })
        except Exception:
            pass

    return response


def log_query(
    request: Request,
    query_text: str,
    language: str,
    destination: str,
    success: bool,
    latency_ms: float,
) -> None:
    """Append a completed query to the in-memory log.

    Called explicitly from route handlers after workflow completes.

    Args:
        request: FastAPI request object.
        query_text: The patient's query.
        language: Detected language code.
        destination: Resolved destination node ID.
        success: Whether a valid path was found.
        latency_ms: Total processing time.
    """
    try:
        if hasattr(request.app.state, "query_log"):
            request.app.state.query_log.append({
                "timestamp": datetime.now().isoformat(),
                "query": query_text,
                "language": language,
                "destination": destination,
                "success": success,
                "latency_ms": round(latency_ms, 2),
            })
    except Exception as e:
        logger.debug(f"Query log append failed: {e}")
