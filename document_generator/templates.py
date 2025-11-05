"""
Air Force Tongue & Quill (AFH 33-337) formatting styles for PDF generation
"""

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.units import inch
from constants import BODY_FONT, BOLD_FONT


# ============================================================================
# AF TONGUE & QUILL PARAGRAPH STYLES
# ============================================================================

STYLE_AF_HEADING = ParagraphStyle(
    'AFHeading',
    fontName=BOLD_FONT,
    fontSize=12,
    alignment=TA_CENTER,
    spaceAfter=12,
    spaceBefore=0,
    leading=14
)

STYLE_AF_SUBHEADING = ParagraphStyle(
    'AFSubheading',
    fontName=BOLD_FONT,
    fontSize=11,
    alignment=TA_LEFT,
    spaceAfter=6,
    spaceBefore=6,
    leading=13
)

STYLE_AF_FROM_TO = ParagraphStyle(
    'AFFromTo',
    fontName=BODY_FONT,
    fontSize=12,
    alignment=TA_LEFT,
    spaceAfter=0,
    spaceBefore=0,
    leading=14
)

STYLE_AF_SUBJECT = ParagraphStyle(
    'AFSubject',
    fontName=BODY_FONT,
    fontSize=12,
    alignment=TA_LEFT,
    spaceAfter=12,
    spaceBefore=0,
    leading=14
)

STYLE_AF_BODY = ParagraphStyle(
    'AFBody',
    fontName=BODY_FONT,
    fontSize=12,
    alignment=TA_JUSTIFY,
    spaceAfter=12,
    spaceBefore=0,
    leading=14,  # Single spacing per T&Q
    firstLineIndent=0
)

STYLE_AF_BODY_INDENT = ParagraphStyle(
    'AFBodyIndent',
    fontName=BODY_FONT,
    fontSize=12,
    alignment=TA_JUSTIFY,
    spaceAfter=12,
    spaceBefore=0,
    leading=14,
    leftIndent=0.5 * inch,
    firstLineIndent=0
)

STYLE_AF_SIGNATURE = ParagraphStyle(
    'AFSignature',
    fontName=BODY_FONT,
    fontSize=12,
    alignment=TA_LEFT,
    spaceAfter=0,
    spaceBefore=0,
    leftIndent=3.5 * inch,  # Signature block indented
    leading=14
)

STYLE_AF_DISTRIBUTION = ParagraphStyle(
    'AFDistribution',
    fontName=BODY_FONT,
    fontSize=11,
    alignment=TA_LEFT,
    spaceAfter=4,
    spaceBefore=0,
    leading=13
)

STYLE_AF_FOOTER = ParagraphStyle(
    'AFFooter',
    fontName=BODY_FONT,
    fontSize=10,
    alignment=TA_LEFT,
    spaceAfter=0,
    spaceBefore=0,
    leading=12
)

STYLE_AF_DATE = ParagraphStyle(
    'AFDate',
    fontName=BODY_FONT,
    fontSize=12,
    alignment=TA_RIGHT,
    spaceAfter=0,
    spaceBefore=0,
    leading=14
)


# ============================================================================
# DOCUMENT LAYOUT CONSTANTS
# ============================================================================

# Standard AF margins (1 inch all sides per T&Q)
AF_MARGIN_TOP = 1.0 * inch
AF_MARGIN_BOTTOM = 1.0 * inch
AF_MARGIN_LEFT = 1.0 * inch
AF_MARGIN_RIGHT = 1.0 * inch

# Letterhead positioning
LETTERHEAD_ORG_Y = 10.5 * inch  # Organization name at top
LETTERHEAD_OFFICE_Y = 10.2 * inch  # Office symbol
LETTERHEAD_DATE_Y = 10.2 * inch  # Date (right-aligned)

# Signature block spacing
SIGNATURE_BLOCK_SPACING = 4  # Lines of space above signature for handwritten signature
SIGNATURE_LINE_HEIGHT = 0.18 * inch

# Paragraph spacing
PARAGRAPH_SPACING = 0.15 * inch  # Double-space between paragraphs per T&Q

# Date format per AFH 33-337
AF_DATE_FORMAT = "%d %b %Y"  # Example: 15 Jan 2025
AF_DATE_FORMAT_FULL = "%d %B %Y"  # Example: 15 January 2025


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_af_date(date_obj) -> str:
    """Format date according to AF Tongue & Quill standards"""
    if date_obj is None:
        return ""
    return date_obj.strftime(AF_DATE_FORMAT).upper()


def format_signature_name(name: str, rank: str) -> str:
    """
    Format name for signature block per T&Q standards
    Example: JOHN A. DOE, Capt, USAF
    """
    return f"{name.upper()}, {rank}, USAF"


def format_subject_line(subject: str) -> str:
    """Format subject line (all caps per T&Q)"""
    return subject.upper()


def format_office_symbol(office_symbol: str, date_str: str) -> tuple:
    """
    Return formatted office symbol and date for letterhead
    Returns: (office_line, date_line)
    """
    office_line = f"DEPARTMENT OF THE AIR FORCE<br/>{office_symbol}"
    date_line = date_str
    return office_line, date_line
