"""
Air Force Administrative Document Generator

This module provides functionality to generate Air Force administrative documents
following AFH 33-337 (The Tongue and Quill) formatting standards.

Supported document types:
- Memorandum For Record (MFR)
- Official Memorandum (Memo)
- Appointment Letters
- Letter of Counseling (LOC)
- Letter of Admonishment (LOA)
- Letter of Reprimand (LOR)
"""

from .models import (
    DocumentType,
    DocumentMetadata,
    DocumentGenerationRequest,
    MFRContent,
    MemoContent,
    AppointmentContent,
    AdministrativeActionContent
)

from .generators import (
    MFRGenerator,
    MemoGenerator,
    AppointmentGenerator,
    LOCGenerator,
    LOAGenerator,
    LORGenerator
)

__version__ = "1.0.0"
__all__ = [
    "DocumentType",
    "DocumentMetadata",
    "DocumentGenerationRequest",
    "MFRContent",
    "MemoContent",
    "AppointmentContent",
    "AdministrativeActionContent",
    "MFRGenerator",
    "MemoGenerator",
    "AppointmentGenerator",
    "LOCGenerator",
    "LOAGenerator",
    "LORGenerator"
]
