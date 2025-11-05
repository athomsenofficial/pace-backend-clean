"""
Base generator class for Air Force administrative documents
Provides common functionality shared across all document types
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors

from .templates import (
    STYLE_AF_HEADING, STYLE_AF_SUBHEADING, STYLE_AF_FROM_TO,
    STYLE_AF_SUBJECT, STYLE_AF_BODY, STYLE_AF_SIGNATURE,
    STYLE_AF_DISTRIBUTION, STYLE_AF_DATE, STYLE_AF_BODY_INDENT,
    AF_MARGIN_TOP, AF_MARGIN_BOTTOM, AF_MARGIN_LEFT, AF_MARGIN_RIGHT,
    SIGNATURE_LINE_HEIGHT, format_af_date, format_signature_name, format_subject_line
)
from .models import DocumentMetadata, SignatureBlock


class AFDocumentGenerator:
    """
    Base class for all Air Force document generators.
    Provides common functionality for letterhead, signature blocks, etc.
    """

    def __init__(self):
        self.page_width, self.page_height = letter
        self.margin_top = AF_MARGIN_TOP
        self.margin_bottom = AF_MARGIN_BOTTOM
        self.margin_left = AF_MARGIN_LEFT
        self.margin_right = AF_MARGIN_RIGHT

        # Styles
        self.style_heading = STYLE_AF_HEADING
        self.style_subheading = STYLE_AF_SUBHEADING
        self.style_from_to = STYLE_AF_FROM_TO
        self.style_subject = STYLE_AF_SUBJECT
        self.style_body = STYLE_AF_BODY
        self.style_body_indent = STYLE_AF_BODY_INDENT
        self.style_signature = STYLE_AF_SIGNATURE
        self.style_distribution = STYLE_AF_DISTRIBUTION
        self.style_date = STYLE_AF_DATE

    def create_letterhead(self, metadata: DocumentMetadata) -> list:
        """
        Create standard AF letterhead
        Returns list of Platypus flowables
        """
        story = []

        # Organization name (centered at top)
        if metadata.organization:
            story.append(Paragraph(
                f"DEPARTMENT OF THE AIR FORCE<br/>{metadata.organization.upper()}",
                self.style_heading
            ))
        else:
            story.append(Paragraph("DEPARTMENT OF THE AIR FORCE", self.style_heading))

        story.append(Spacer(1, 0.1 * inch))

        # Office symbol (left) and Date (right) on same line
        office_date_table = Table(
            [[
                Paragraph(metadata.office_symbol, self.style_from_to),
                Paragraph(format_af_date(metadata.date), self.style_date)
            ]],
            colWidths=[4 * inch, 2.5 * inch]
        )
        office_date_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(office_date_table)
        story.append(Spacer(1, 0.2 * inch))

        return story

    def create_signature_block(self, metadata: DocumentMetadata,
                               num_signature_lines: int = 4) -> list:
        """
        Create standard AF signature block with space for handwritten signature

        Args:
            metadata: Document metadata containing author info
            num_signature_lines: Number of blank lines for handwritten signature (default 4)

        Returns:
            List of Platypus flowables
        """
        story = []

        # Blank lines for handwritten signature
        for _ in range(num_signature_lines):
            story.append(Spacer(1, SIGNATURE_LINE_HEIGHT))

        # Name in all caps with rank
        signature_name = format_signature_name(metadata.author_name, metadata.author_rank)
        story.append(Paragraph(signature_name, self.style_signature))

        # Title
        story.append(Paragraph(metadata.author_title, self.style_signature))

        return story

    def create_from_line(self, office_symbol: str) -> Paragraph:
        """Create FROM: line"""
        return Paragraph(f"FROM: {office_symbol}", self.style_from_to)

    def create_to_line(self, recipient: str) -> Paragraph:
        """Create TO: line"""
        return Paragraph(f"TO: {recipient}", self.style_from_to)

    def create_thru_line(self, routing: str) -> Paragraph:
        """Create THRU: line (optional routing)"""
        return Paragraph(f"THRU: {routing}", self.style_from_to)

    def create_subject_line(self, subject: str) -> Paragraph:
        """Create SUBJECT: line (automatically capitalizes)"""
        formatted_subject = format_subject_line(subject)
        return Paragraph(f"SUBJECT: {formatted_subject}", self.style_subject)

    def create_body_paragraphs(self, paragraphs: list, numbered: bool = False) -> list:
        """
        Create body paragraphs with optional numbering

        Args:
            paragraphs: List of paragraph text strings
            numbered: If True, add sequential numbering (1., 2., etc.)

        Returns:
            List of Paragraph flowables
        """
        story = []

        for i, para_text in enumerate(paragraphs, 1):
            if numbered and len(paragraphs) > 1:
                text = f"{i}. {para_text}"
            else:
                text = para_text

            story.append(Paragraph(text, self.style_body))
            story.append(Spacer(1, 0.12 * inch))  # Space between paragraphs

        return story

    def create_distribution_list(self, recipients: list) -> list:
        """Create distribution list section"""
        if not recipients:
            return []

        story = []
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("<b>Distribution:</b>", self.style_distribution))

        for recipient in recipients:
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{recipient}", self.style_distribution))

        return story

    def create_attachments_list(self, attachments: list) -> list:
        """Create attachments list section"""
        if not attachments:
            return []

        story = []
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("<b>Attachments:</b>", self.style_distribution))

        for i, attachment in enumerate(attachments, 1):
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. {attachment}", self.style_distribution))

        return story

    def build_pdf(self, story: list) -> BytesIO:
        """
        Build the PDF document from story elements

        Args:
            story: List of Platypus flowables

        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=self.margin_top,
            bottomMargin=self.margin_bottom,
            leftMargin=self.margin_left,
            rightMargin=self.margin_right
        )

        doc.build(story)
        buffer.seek(0)

        return buffer

    def generate(self, *args, **kwargs) -> BytesIO:
        """
        Generate the document (to be implemented by subclasses)

        Returns:
            BytesIO buffer containing the PDF
        """
        raise NotImplementedError("Subclasses must implement generate() method")
