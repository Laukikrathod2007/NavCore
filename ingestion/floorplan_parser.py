"""Floor plan parser using GPT-4o Vision (one-time, online).

This module runs ONCE during hospital setup to convert a floor plan
image into a spatial graph JSON. It is NOT used at runtime — the system
is offline-first.

Based on Floorplan2Guide (arxiv 2512.12177): graph-based spatial
structure achieves 15.4% higher success rate than direct visual
reasoning.
"""

import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# System prompt for GPT-4o Vision to extract spatial graph from floorplan
_FLOORPLAN_SYSTEM_PROMPT = """You are a multimodal reasoning system that specializes in floorplan parsing.
Your task is to analyze the provided floorplan image and extract spatial
information to build a navigable knowledge graph.

Extract:
1. All rooms, corridors, entrances, lifts, and infrastructure nodes
2. Their display names, floor numbers, and descriptions
3. Connectivity (which rooms connect to which)
4. Nearby landmarks (water coolers, nurse stations, etc.)

Output as JSON with this structure:
{
  "hospital_name": "string",
  "nodes": {
    "node_id": {
      "display_name": "string",
      "floor": int,
      "wing": "string or null",
      "room_number": "string or null",
      "node_type": "department|corridor|entrance|infrastructure|amenity|landmark",
      "connects_to": ["node_id", ...],
      "landmarks_nearby": ["string", ...],
      "timing": "string",
      "is_accessible": true,
      "is_available": true,
      "description": "string"
    }
  }
}
"""


def parse_floorplan_with_llm(
    floorplan_image_path: str,
    api_key: str,
    model: str = "gpt-4o",
) -> Dict:
    """Parse a floor plan image into a spatial graph JSON using GPT-4o Vision.

    This is a one-time online operation. The resulting graph.json is
    used offline at runtime.

    Args:
        floorplan_image_path: Path to the floor plan image file.
        api_key: OpenAI API key (used once during setup).
        model: Vision model to use (default: gpt-4o).

    Returns:
        Dict containing the parsed spatial graph in graph.json format.

    Raises:
        ImportError: If openai package is not installed.
        RuntimeError: If API call fails.
    """
    logger.info(f"Parsing floorplan: {floorplan_image_path}")

    try:
        import openai
    except ImportError as e:
        raise ImportError(
            "openai package required for floorplan parsing: pip install openai"
        ) from e

    try:
        import base64

        with open(floorplan_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _FLOORPLAN_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                        {
                            "type": "text",
                            "text": "Extract the spatial knowledge graph from this floor plan.",
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        logger.info(
            f"Floorplan parsed: {len(result.get('nodes', {}))} nodes extracted"
        )
        return result

    except Exception as e:
        logger.error(f"Floorplan parsing failed: {e}")
        raise RuntimeError(f"Floorplan parsing failed: {e}") from e


def save_graph_json(graph_data: Dict, output_path: str) -> None:
    """Save parsed graph data to a JSON file.

    Args:
        graph_data: Parsed graph dict from parse_floorplan_with_llm.
        output_path: Path to save graph.json.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Graph saved to {output_path}")
