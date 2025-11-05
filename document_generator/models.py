"""
Pydantic models for Air Force administrative documents
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types"""
    MFR = "mfr"
    MEMO = "memo"
    APPOINTMENT = "appointment"
    LOC = "loc"
    LOA = "loa"
    LOR = "lor"


class DocumentMetadata(BaseModel):
    """Common metadata for all AF documents"""
    office_symbol: str = Field(..., example="51 FSS/CC", description="Unit office symbol")
    author_name: str = Field(..., example="John A. Doe", description="Author's full name")
    author_rank: str = Field(..., example="Capt", description="Author's rank abbreviation")
    author_title: str = Field(..., example="Commander", description="Author's duty title")
    organization: str = Field(..., example="51st Force Support Squadron", description="Organization name")
    date: Optional[date] = Field(default_factory=date.today, description="Document date")
    phone: Optional[str] = Field(None, example="DSN 315-784-1234")
    email: Optional[str] = Field(None, example="john.doe@us.af.mil")


class SignatureBlock(BaseModel):
    """Signature block information"""
    name: str
    rank: str
    title: str
    organization: Optional[str] = None
    date_signed: Optional[date] = None


class MFRContent(BaseModel):
    """Content for Memorandum For Record"""
    subject: str = Field(..., description="Subject line (will be capitalized)")
    body_paragraphs: List[str] = Field(..., min_items=1, description="Body paragraphs")
    distribution_list: Optional[List[str]] = Field(None, description="Distribution list recipients")
    attachments: Optional[List[str]] = Field(None, description="List of attachments")


class MemoContent(BaseModel):
    """Content for Official Memorandum"""
    to_line: str = Field(..., example="51 FSS/CCF", description="TO: recipient")
    thru_line: Optional[str] = Field(None, example="51 FSS/CC", description="THRU: routing (optional)")
    subject: str = Field(..., description="Subject line (will be capitalized)")
    body_paragraphs: List[str] = Field(..., min_items=1, description="Body paragraphs (numbered)")
    distribution_list: Optional[List[str]] = Field(None)
    attachments: Optional[List[str]] = Field(None)


class AppointmentContent(BaseModel):
    """Content for Appointment Letter"""
    appointee_name: str = Field(..., example="John A. Smith")
    appointee_rank: str = Field(..., example="SSgt")
    appointee_ssan: Optional[str] = Field(None, example="1234", description="Last 4 of SSN")
    position_title: str = Field(..., example="Squadron Safety Representative")
    authority_citation: str = Field(..., example="AFI 91-202, para 2.3", description="Authority for appointment")
    duties: List[str] = Field(..., min_items=1, description="List of duties and responsibilities")
    effective_date: date = Field(..., description="Appointment effective date")
    termination_date: Optional[date] = Field(None, description="Appointment end date (if applicable)")


class AdministrativeActionContent(BaseModel):
    """Base model for LOC/LOA/LOR"""
    member_name: str = Field(..., example="John A. Smith")
    member_rank: str = Field(..., example="SSgt")
    member_unit: str = Field(..., example="51st Force Support Squadron")
    member_ssan: Optional[str] = Field(None, example="1234", description="Last 4 of SSN")
    subject: str = Field(..., description="Subject line")
    incident_date: date = Field(..., description="Date of incident")
    incident_description: str = Field(..., description="Detailed description of incident")
    violations: List[str] = Field(..., min_items=1, description="Standards violated (AFI citations)")
    standards_expected: str = Field(..., description="Expected standards of behavior")
    consequences: str = Field(..., description="Consequences if behavior continues")
    previous_actions: Optional[List[str]] = Field(None, description="Previous counseling/actions")
    filing_location: Optional[Literal["PIF", "DCAF", "UPRG"]] = Field(None, description="For LOR only")
    appeal_rights: Optional[str] = Field(None, description="For LOA/LOR - appeal process")


class DocumentGenerationRequest(BaseModel):
    """Request to generate a document from a prompt"""
    document_type: DocumentType
    prompt: str = Field(..., min_length=10, max_length=5000, description="Natural language prompt")
    metadata: DocumentMetadata
    options: Optional[dict] = Field(default_factory=dict, description="Additional generation options")


class DocumentResponse(BaseModel):
    """Response after document generation"""
    document_id: str
    session_id: str
    document_type: str
    status: Literal["draft", "finalized"]
    message: str
    extracted_fields: Optional[dict] = None
    validation_warnings: List[str] = []
    pdf_url: Optional[str] = None
