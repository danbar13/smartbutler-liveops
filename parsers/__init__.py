"""
SmartButler LiveOps Digest - Parsers Package (parsers/__init__.py)
Unified entry point for parsing SmartButler documents across PDF, CSV, and JSON.
"""

import io
import os
from typing import Union
from .models import TicketItem, DepartmentSummary, ParsedLogReport, parse_duration_to_minutes, format_minutes_to_duration
from .pdf_parser import SmartButlerPDFParser
from .csv_parser import SmartButlerCSVParser
from .json_parser import SmartButlerJSONParser

def parse_smartbutler_document(
    file_source: Union[str, bytes, io.BytesIO],
    filename: str = ""
) -> ParsedLogReport:
    """
    Auto-detects format from filename or content inspection and parses
    into a standardized ParsedLogReport.
    """
    fn_lower = filename.lower()

    if fn_lower.endswith(".pdf"):
        return SmartButlerPDFParser().parse(file_source, filename=filename or "report.pdf")
    elif fn_lower.endswith(".csv"):
        return SmartButlerCSVParser().parse(file_source, filename=filename or "report.csv")
    elif fn_lower.endswith(".json"):
        return SmartButlerJSONParser().parse(file_source, filename=filename or "report.json")

    # If filename is ambiguous, inspect source
    if isinstance(file_source, (bytes, bytearray)):
        sample = file_source[:10]
        if sample.startswith(b"%PDF"):
            return SmartButlerPDFParser().parse(file_source, filename=filename or "report.pdf")
        if sample.strip().startswith(b"{") or sample.strip().startswith(b"["):
            return SmartButlerJSONParser().parse(file_source, filename=filename or "report.json")
        return SmartButlerCSVParser().parse(file_source, filename=filename or "report.csv")
    elif isinstance(file_source, str) and os.path.exists(file_source):
        ext = os.path.splitext(file_source)[1].lower()
        if ext == ".pdf":
            return SmartButlerPDFParser().parse(file_source, filename=filename or os.path.basename(file_source))
        elif ext == ".json":
            return SmartButlerJSONParser().parse(file_source, filename=filename or os.path.basename(file_source))
        else:
            return SmartButlerCSVParser().parse(file_source, filename=filename or os.path.basename(file_source))

    # Default fallback to PDF parser
    return SmartButlerPDFParser().parse(file_source, filename=filename or "report.pdf")

__all__ = [
    "parse_smartbutler_document",
    "SmartButlerPDFParser",
    "SmartButlerCSVParser",
    "SmartButlerJSONParser",
    "TicketItem",
    "DepartmentSummary",
    "ParsedLogReport",
    "parse_duration_to_minutes",
    "format_minutes_to_duration"
]
