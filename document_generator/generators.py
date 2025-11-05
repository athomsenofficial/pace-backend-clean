"""
Document-specific generators for AF administrative documents.
All generators in one file to avoid repetition and share common patterns.
"""

from io import BytesIO
from reportlab.platypus import Paragraph, Spacer, KeepTogether
from reportlab.lib.units import inch
from datetime import date as date_type

from .base_generator import AFDocumentGenerator
from .models import (
    DocumentMetadata, MFRContent, MemoContent,
    AppointmentContent, AdministrativeActionContent
)
from .templates import format_af_date
from constants import AF_APPEAL_TIMELINE_DAYS


class MFRGenerator(AFDocumentGenerator):
    """Generator for Memorandum For Record"""

    def generate(self, content: MFRContent, metadata: DocumentMetadata) -> BytesIO:
        """Generate MFR PDF"""
        story = []

        # 1. Letterhead
        story.extend(self.create_letterhead(metadata))

        # 2. "MEMORANDUM FOR RECORD" centered
        story.append(Paragraph("MEMORANDUM FOR RECORD", self.style_heading))
        story.append(Spacer(1, 0.15 * inch))

        # 3. FROM: line
        story.append(self.create_from_line(metadata.office_symbol))
        story.append(Spacer(1, 0.1 * inch))

        # 4. SUBJECT: line
        story.append(self.create_subject_line(content.subject))
        story.append(Spacer(1, 0.15 * inch))

        # 5. Body paragraphs (numbered if multiple)
        numbered = len(content.body_paragraphs) > 1
        story.extend(self.create_body_paragraphs(content.body_paragraphs, numbered=numbered))

        # 6. Signature block
        story.append(Spacer(1, 0.3 * inch))
        story.extend(self.create_signature_block(metadata))

        # 7. Distribution list (optional)
        if content.distribution_list:
            story.extend(self.create_distribution_list(content.distribution_list))

        # 8. Attachments (optional)
        if content.attachments:
            story.extend(self.create_attachments_list(content.attachments))

        # Build and return PDF
        return self.build_pdf(story)


class MemoGenerator(AFDocumentGenerator):
    """Generator for Official Memorandum"""

    def generate(self, content: MemoContent, metadata: DocumentMetadata) -> BytesIO:
        """Generate Official Memo PDF"""
        story = []

        # 1. Letterhead
        story.extend(self.create_letterhead(metadata))

        # 2. "MEMORANDUM FOR" or "MEMORANDUM THRU" heading
        if content.thru_line:
            story.append(Paragraph("MEMORANDUM THRU", self.style_heading))
        else:
            story.append(Paragraph("MEMORANDUM FOR", self.style_heading))
        story.append(Spacer(1, 0.15 * inch))

        # 3. FROM: line
        story.append(self.create_from_line(metadata.office_symbol))
        story.append(Spacer(1, 0.05 * inch))

        # 4. THRU: line (if applicable)
        if content.thru_line:
            story.append(self.create_thru_line(content.thru_line))
            story.append(Spacer(1, 0.05 * inch))

        # 5. TO: line
        story.append(self.create_to_line(content.to_line))
        story.append(Spacer(1, 0.1 * inch))

        # 6. SUBJECT: line
        story.append(self.create_subject_line(content.subject))
        story.append(Spacer(1, 0.15 * inch))

        # 7. Body paragraphs (always numbered for official memos)
        story.extend(self.create_body_paragraphs(content.body_paragraphs, numbered=True))

        # 8. Signature block
        story.append(Spacer(1, 0.3 * inch))
        story.extend(self.create_signature_block(metadata))

        # 9. Distribution list (optional)
        if content.distribution_list:
            story.extend(self.create_distribution_list(content.distribution_list))

        # 10. Attachments (optional)
        if content.attachments:
            story.extend(self.create_attachments_list(content.attachments))

        return self.build_pdf(story)


class AppointmentGenerator(AFDocumentGenerator):
    """Generator for Appointment Letters"""

    def generate(self, content: AppointmentContent, metadata: DocumentMetadata) -> BytesIO:
        """Generate Appointment Letter PDF"""
        story = []

        # 1. Letterhead
        story.extend(self.create_letterhead(metadata))

        # 2. "MEMORANDUM FOR RECORD" centered
        story.append(Paragraph("MEMORANDUM FOR RECORD", self.style_heading))
        story.append(Spacer(1, 0.15 * inch))

        # 3. FROM: line
        story.append(self.create_from_line(metadata.office_symbol))
        story.append(Spacer(1, 0.1 * inch))

        # 4. SUBJECT: Appointment Letter
        story.append(self.create_subject_line(f"APPOINTMENT OF {content.position_title}"))
        story.append(Spacer(1, 0.15 * inch))

        # 5. Body - Appointment details
        # Para 1: Authority and appointee
        para1 = (
            f"1. By the authority vested in me by {content.authority_citation}, "
            f"{content.appointee_rank} {content.appointee_name}"
        )
        if content.appointee_ssan:
            para1 += f", SSAN {content.appointee_ssan},"
        para1 += f" is hereby appointed as {content.position_title}, effective {format_af_date(content.effective_date)}."

        if content.termination_date:
            para1 += f" This appointment will terminate on {format_af_date(content.termination_date)}."

        story.append(Paragraph(para1, self.style_body))
        story.append(Spacer(1, 0.12 * inch))

        # Para 2: Duties and responsibilities
        para2 = "2. Duties and responsibilities include:"
        story.append(Paragraph(para2, self.style_body))
        story.append(Spacer(1, 0.08 * inch))

        # List duties with sub-numbering
        for i, duty in enumerate(content.duties):
            duty_text = f"&nbsp;&nbsp;&nbsp;&nbsp;{chr(97 + i)}. {duty}"  # a, b, c...
            story.append(Paragraph(duty_text, self.style_body_indent))
            story.append(Spacer(1, 0.05 * inch))

        story.append(Spacer(1, 0.05 * inch))

        # Para 3: Acknowledgment
        para3 = (
            "3. This letter does not constitute authority to perform duties "
            "outside the scope of this appointment. The appointee will ensure "
            "all actions taken under this appointment comply with applicable "
            "Air Force instructions and directives."
        )
        story.append(Paragraph(para3, self.style_body))
        story.append(Spacer(1, 0.12 * inch))

        # 6. Signature block
        story.append(Spacer(1, 0.3 * inch))
        story.extend(self.create_signature_block(metadata))

        return self.build_pdf(story)


class LOCGenerator(AFDocumentGenerator):
    """Generator for Letter of Counseling"""

    def generate(self, content: AdministrativeActionContent, metadata: DocumentMetadata) -> BytesIO:
        """Generate LOC PDF"""
        story = []

        # 1. Letterhead
        story.extend(self.create_letterhead(metadata))

        # 2. "LETTER OF COUNSELING" centered
        story.append(Paragraph("LETTER OF COUNSELING", self.style_heading))
        story.append(Spacer(1, 0.15 * inch))

        # 3. FROM: and TO: lines
        story.append(self.create_from_line(metadata.office_symbol))
        story.append(Spacer(1, 0.05 * inch))

        to_line_text = f"{content.member_rank} {content.member_name}"
        if content.member_ssan:
            to_line_text += f", SSAN {content.member_ssan}"
        story.append(self.create_to_line(to_line_text))
        story.append(Spacer(1, 0.1 * inch))

        # 4. SUBJECT: line
        story.append(self.create_subject_line(content.subject))
        story.append(Spacer(1, 0.15 * inch))

        # 5. Body paragraphs
        # Para 1: Purpose and incident description
        para1 = (
            f"1. On {format_af_date(content.incident_date)}, {content.incident_description} "
            "This letter is to counsel you on your failure to meet Air Force standards."
        )
        story.append(Paragraph(para1, self.style_body))
        story.append(Spacer(1, 0.12 * inch))

        # Para 2: Standards violated
        para2 = "2. Your actions violated the following standards:"
        story.append(Paragraph(para2, self.style_body))
        story.append(Spacer(1, 0.08 * inch))

        for violation in content.violations:
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;• {violation}", self.style_body_indent))
            story.append(Spacer(1, 0.05 * inch))

        story.append(Spacer(1, 0.05 * inch))

        # Para 3: Expected standards
        para3 = f"3. {content.standards_expected}"
        story.append(Paragraph(para3, self.style_body))
        story.append(Spacer(1, 0.12 * inch))

        # Para 4: Consequences
        para4 = f"4. {content.consequences}"
        story.append(Paragraph(para4, self.style_body))
        story.append(Spacer(1, 0.12 * inch))

        # Para 5: Acknowledgment
        para5 = (
            f"5. You have {AF_APPEAL_TIMELINE_DAYS['LOC']} duty days from receipt of this letter "
            "to acknowledge receipt by signing below. Your signature does not indicate agreement, "
            "only that you have received and read this letter. You may submit written matters "
            "in your own behalf."
        )
        story.append(Paragraph(para5, self.style_body))
        story.append(Spacer(1, 0.2 * inch))

        # 6. Signature block
        story.extend(self.create_signature_block(metadata, num_signature_lines=3))

        # 7. Acknowledgment section
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("ACKNOWLEDGMENT", self.style_subheading))
        story.append(Spacer(1, 0.2 * inch))

        ack_text = (
            f"I acknowledge receipt of this Letter of Counseling on ________________.<br/><br/><br/>"
            f"_______________________________________&nbsp;&nbsp;&nbsp;&nbsp;Date: ________________<br/>"
            f"{content.member_rank} {content.member_name.upper()}, USAF"
        )
        story.append(Paragraph(ack_text, self.style_body))

        return self.build_pdf(story)


class LOAGenerator(AFDocumentGenerator):
    """Generator for Letter of Admonishment"""

    def generate(self, content: AdministrativeActionContent, metadata: DocumentMetadata) -> BytesIO:
        """Generate LOA PDF"""
        story = []

        # Similar to LOC but with more formal tone and mention of previous counseling
        story.extend(self.create_letterhead(metadata))

        story.append(Paragraph("LETTER OF ADMONISHMENT", self.style_heading))
        story.append(Spacer(1, 0.15 * inch))

        story.append(self.create_from_line(metadata.office_symbol))
        story.append(Spacer(1, 0.05 * inch))

        to_line_text = f"{content.member_rank} {content.member_name}"
        if content.member_ssan:
            to_line_text += f", SSAN {content.member_ssan}"
        story.append(self.create_to_line(to_line_text))
        story.append(Spacer(1, 0.1 * inch))

        story.append(self.create_subject_line(content.subject))
        story.append(Spacer(1, 0.15 * inch))

        # Para 1: Incident and formal admonishment
        para1 = (
            f"1. On {format_af_date(content.incident_date)}, {content.incident_description} "
            "I am formally admonishing you for this conduct, which fails to meet the standards "
            "expected of Air Force members."
        )
        story.append(Paragraph(para1, self.style_body))
        story.append(Spacer(1, 0.12 * inch))

        # Para 2: Previous actions (if any)
        if content.previous_actions:
            para2 = "2. You have previously been counseled for similar conduct:"
            story.append(Paragraph(para2, self.style_body))
            story.append(Spacer(1, 0.08 * inch))

            for action in content.previous_actions:
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;• {action}", self.style_body_indent))
                story.append(Spacer(1, 0.05 * inch))

            story.append(Spacer(1, 0.05 * inch))
            para_num = 3
        else:
            para_num = 2

        # Standards violated
        para_std = f"{para_num}. Your actions violated:"
        story.append(Paragraph(para_std, self.style_body))
        story.append(Spacer(1, 0.08 * inch))

        for violation in content.violations:
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;• {violation}", self.style_body_indent))
            story.append(Spacer(1, 0.05 * inch))

        story.append(Spacer(1, 0.05 * inch))
        para_num += 1

        # Expected standards
        para_exp = f"{para_num}. {content.standards_expected}"
        story.append(Paragraph(para_exp, self.style_body))
        story.append(Spacer(1, 0.12 * inch))
        para_num += 1

        # Consequences
        para_con = f"{para_num}. {content.consequences}"
        story.append(Paragraph(para_con, self.style_body))
        story.append(Spacer(1, 0.12 * inch))
        para_num += 1

        # Appeal rights
        if content.appeal_rights:
            para_appeal = f"{para_num}. {content.appeal_rights}"
        else:
            para_appeal = (
                f"{para_num}. You have {AF_APPEAL_TIMELINE_DAYS['LOA']} duty days from receipt "
                "to acknowledge this letter and may submit written matters in your own behalf."
            )
        story.append(Paragraph(para_appeal, self.style_body))
        story.append(Spacer(1, 0.2 * inch))

        # Signature block
        story.extend(self.create_signature_block(metadata, num_signature_lines=3))

        # Acknowledgment section
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("ACKNOWLEDGMENT", self.style_subheading))
        story.append(Spacer(1, 0.2 * inch))

        ack_text = (
            f"I acknowledge receipt of this Letter of Admonishment on ________________.<br/><br/><br/>"
            f"_______________________________________&nbsp;&nbsp;&nbsp;&nbsp;Date: ________________<br/>"
            f"{content.member_rank} {content.member_name.upper()}, USAF"
        )
        story.append(Paragraph(ack_text, self.style_body))

        return self.build_pdf(story)


class LORGenerator(AFDocumentGenerator):
    """Generator for Letter of Reprimand"""

    def generate(self, content: AdministrativeActionContent, metadata: DocumentMetadata) -> BytesIO:
        """Generate LOR PDF"""
        story = []

        # Most formal administrative action
        story.extend(self.create_letterhead(metadata))

        story.append(Paragraph("LETTER OF REPRIMAND", self.style_heading))
        story.append(Spacer(1, 0.15 * inch))

        story.append(self.create_from_line(metadata.office_symbol))
        story.append(Spacer(1, 0.05 * inch))

        to_line_text = f"{content.member_rank} {content.member_name}"
        if content.member_ssan:
            to_line_text += f", SSAN {content.member_ssan}"
        story.append(self.create_to_line(to_line_text))
        story.append(Spacer(1, 0.1 * inch))

        story.append(self.create_subject_line(content.subject))
        story.append(Spacer(1, 0.15 * inch))

        # Para 1: Formal reprimand
        para1 = (
            f"1. You are hereby reprimanded for your actions on {format_af_date(content.incident_date)}. "
            f"{content.incident_description} This conduct is unacceptable and violates the standards "
            "of conduct expected of all Air Force members."
        )
        story.append(Paragraph(para1, self.style_body))
        story.append(Spacer(1, 0.12 * inch))

        # Para 2: Previous actions
        if content.previous_actions:
            para2 = "2. Despite previous corrective actions, your conduct has not improved:"
            story.append(Paragraph(para2, self.style_body))
            story.append(Spacer(1, 0.08 * inch))

            for action in content.previous_actions:
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;• {action}", self.style_body_indent))
                story.append(Spacer(1, 0.05 * inch))

            story.append(Spacer(1, 0.05 * inch))
            para_num = 3
        else:
            para_num = 2

        # Violations with impact
        para_vio = f"{para_num}. Your conduct violated the following directives and had a negative impact on the mission:"
        story.append(Paragraph(para_vio, self.style_body))
        story.append(Spacer(1, 0.08 * inch))

        for violation in content.violations:
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;• {violation}", self.style_body_indent))
            story.append(Spacer(1, 0.05 * inch))

        story.append(Spacer(1, 0.05 * inch))
        para_num += 1

        # Filing location
        if content.filing_location:
            from constants import AF_ADMIN_ACTION_FILING
            para_file = (
                f"{para_num}. This Letter of Reprimand will be filed in your {content.filing_location} "
                f"({AF_ADMIN_ACTION_FILING.get(content.filing_location, 'personnel file')})."
            )
            story.append(Paragraph(para_file, self.style_body))
            story.append(Spacer(1, 0.12 * inch))
            para_num += 1

        # Appeal rights
        if content.appeal_rights:
            para_appeal = f"{para_num}. {content.appeal_rights}"
        else:
            para_appeal = (
                f"{para_num}. You have {AF_APPEAL_TIMELINE_DAYS['LOR']} calendar days from receipt "
                "to submit matters in your own behalf and to request removal of this letter. "
                "Your submission should be forwarded through your chain of command to the issuing authority."
            )
        story.append(Paragraph(para_appeal, self.style_body))
        story.append(Spacer(1, 0.2 * inch))

        # Signature block (usually requires commander or higher)
        story.extend(self.create_signature_block(metadata, num_signature_lines=3))

        # Acknowledgment section
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("ACKNOWLEDGMENT OF RECEIPT", self.style_subheading))
        story.append(Spacer(1, 0.2 * inch))

        ack_text = (
            f"I acknowledge receipt of this Letter of Reprimand on ________________.<br/>"
            "My signature does not indicate agreement with the contents of this letter.<br/><br/><br/>"
            f"_______________________________________&nbsp;&nbsp;&nbsp;&nbsp;Date: ________________<br/>"
            f"{content.member_rank} {content.member_name.upper()}, USAF"
        )
        story.append(Paragraph(ack_text, self.style_body))

        return self.build_pdf(story)
