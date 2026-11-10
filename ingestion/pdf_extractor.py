"""PDF extractor using pdfplumber for hospital directory parsing.

Extracts alias data (doctor names, procedures, department names) from
a hospital directory PDF. This is a one-time ingestion step.
"""

import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """Extract all text pages from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of text strings, one per page.

    Raises:
        ImportError: If pdfplumber is not installed.
        FileNotFoundError: If PDF file does not exist.
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")

    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError(
            "pdfplumber required for PDF extraction: pip install pdfplumber"
        ) from e

    pages_text: List[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
                logger.info(f"Extracted {len(text)} chars from page {len(pages_text)}")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}") from e

    logger.info(f"Extracted {len(pages_text)} pages from PDF")
    return pages_text


def parse_directory_to_aliases(
    pages_text: List[str],
    known_node_ids: List[str],
) -> List[Dict]:
    """Parse PDF text into alias entries.

    This is a simplified parser that looks for doctor names, department
    names, and room numbers in the extracted text. A production system
    would use more sophisticated NLP or LLM-based extraction.

    Args:
        pages_text: List of text strings from PDF pages.
        known_node_ids: List of canonical node IDs to match against.

    Returns:
        List of alias entries in aliases.json format.
    """
    logger.info("Parsing PDF text into alias entries")

    aliases: List[Dict] = []
    full_text = "\n".join(pages_text)

    # Simple heuristic extraction: look for patterns like
    # "Dr. <Name>" and "<Department> - Room <number>"
    import re

    doctor_pattern = re.compile(r"Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)")
    room_pattern = re.compile(r"Room\s+(\d+[A-Za-z]?)")

    doctors = set(doctor_pattern.findall(full_text))
    rooms = set(room_pattern.findall(full_text))

    logger.info(
        f"Extracted {len(doctors)} doctor names, {len(rooms)} room numbers"
    )

    # Build alias entries — this is a stub for the real parser
    # In production, this would use NLP to map doctors to departments
    for node_id in known_node_ids:
        entry: Dict = {
            "canonical_node_id": node_id,
            "aliases": [],
            "procedures": [],
            "doctors": [],
        }
        aliases.append(entry)

    logger.info(f"Parsed {len(aliases)} alias entries")
    return aliases


def extract_aliases_from_pdf(
    pdf_path: str,
    known_node_ids: List[str],
    output_path: Optional[str] = None,
) -> List[Dict]:
    """Full pipeline: PDF → text → aliases → optional JSON save.

    Args:
        pdf_path: Path to the hospital directory PDF.
        known_node_ids: List of canonical node IDs from graph.json.
        output_path: Optional path to save aliases.json.

    Returns:
        List of alias entries.
    """
    pages_text = extract_text_from_pdf(pdf_path)
    aliases = parse_directory_to_aliases(pages_text, known_node_ids)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(aliases, f, indent=2, ensure_ascii=False)
        logger.info(f"Aliases saved to {output_path}")

    return aliases
