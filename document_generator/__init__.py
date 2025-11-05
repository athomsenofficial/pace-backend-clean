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

Usage:
    from document_generator.models import DocumentGenerationRequest
    from document_generator.generators import MFRGenerator
"""

__version__ = "1.0.0"

# Note: Import classes directly from submodules to avoid circular imports
# Example:
#   from document_generator.models import DocumentType, MFRContent
#   from document_generator.generators import MFRGenerator
