# PACE Backend Enhancement: Air Force Administrative Document Generator
## Planning Document

---

## 📋 Executive Summary

This enhancement adds a **prompt-driven PDF generator** for Air Force administrative documents following Air Force Tongue & Quill standards. The system will generate properly formatted memorandums, appointment letters, and administrative actions through a conversational prompt interface.

---

## 🎯 Feature Overview

### Purpose
Automate the creation of Air Force administrative documents that comply with AFI 33-321 (The Tongue and Quill) formatting standards, reducing time spent on formatting and ensuring regulatory compliance.

### Key Differentiators from Existing MEL Generator
- **Prompt-driven:** Natural language input vs. structured CSV upload
- **Template-based:** Predefined AF formats vs. roster data processing
- **Individual documents:** One-off memos vs. bulk roster processing
- **Text-heavy:** Paragraphs and signatures vs. tabular data

---

## 📝 Document Types

### Phase 1: Core Administrative Documents

#### 1. **Memorandum For Record (MFR)**
- **Purpose:** Internal documentation of events, decisions, phone calls
- **Format:** Standard AF letterhead with subject line
- **Key Elements:**
  - FROM: Office symbol
  - SUBJECT: Brief description
  - Body: Chronological narrative
  - Signature block

#### 2. **Official Memorandum**
- **Purpose:** Formal communication between organizations
- **Variants:**
  - Memorandum For (specific recipient)
  - Memorandum Thru (routing through chain of command)
- **Key Elements:**
  - TO/FROM/THRU routing
  - SUBJECT line
  - Numbered paragraphs
  - Signature block with rank/title

#### 3. **Appointment Letter**
- **Purpose:** Assign duties, responsibilities, authorities
- **Common Types:**
  - Squadron duty appointments (Safety, Security, Training, etc.)
  - Investigation appointments
  - Board member appointments
- **Key Elements:**
  - Authority citation (AFI reference)
  - Appointee information (name, rank, SSAN)
  - Duty description
  - Effective dates
  - Commander signature

### Phase 2: Administrative Actions

#### 4. **Letter of Counseling (LOC)**
- **Purpose:** Initial corrective action for minor infractions
- **Key Elements:**
  - Incident description with dates/times
  - Standards violated (AFI citations)
  - Expected behavior
  - Consequences of continued behavior
  - Member acknowledgment section
  - Supervisor signature

#### 5. **Letter of Admonishment (LOA)**
- **Purpose:** Mid-level corrective action
- **Key Elements:**
  - More formal tone than LOC
  - Detailed violation description
  - Previous counseling references
  - Impact statement
  - Acknowledgment and appeal rights
  - Commander signature

#### 6. **Letter of Reprimand (LOR)**
- **Purpose:** Serious corrective action, filed in PIF/UPRG
- **Key Elements:**
  - Formal charges/allegations
  - Evidence summary
  - AFI violations with specific paragraphs
  - Impact on mission/unit
  - Filing location (PIF, DCAF, or UPRG)
  - Appeal rights and timeline
  - Commander/higher authority signature

---

## 🏗️ Architecture Design

### Module Structure

```
document_generator/
├── __init__.py
├── models.py              # Pydantic models (all document types)
├── base_generator.py      # Base class for AF document generation
├── generators.py          # All document-specific generators in one file
├── prompt_parser.py       # Prompt parsing logic
├── validation.py          # AFI citation, rank validation
└── templates.py           # T&Q formatting styles
```

### Shared Infrastructure (Reuse from MEL)
- ✅ `session_manager.py` - Store draft documents in Redis
- ✅ `constants.py` - Add AF document constants
- ✅ `pdf_templates.py` - Reuse font/layout utilities
- ✅ Redis session storage - Cache document drafts
- ✅ FastAPI routing - Add new document endpoints
- ✅ CORS configuration - Already set up
- ✅ Logging infrastructure - Session-specific logs

---

## 🔌 API Design

### Base Path: `/api/documents`

#### 1. **Create Document from Prompt**
```http
POST /api/documents/generate
Content-Type: application/json

{
  "document_type": "mfr|memo|appointment|loc|loa|lor",
  "prompt": "Create a memorandum for record about...",
  "metadata": {
    "office_symbol": "51 FSS/CC",
    "author_name": "John A. Doe",
    "author_rank": "Capt",
    "author_title": "Commander",
    "organization": "51st Force Support Squadron",
    "date": "2025-01-15"
  }
}
```

#### 2. **Generate Final PDF**
```http
POST /api/documents/{document_id}/generate-pdf

Response: StreamingResponse (PDF file)
```

#### 3. **List Document Templates**
```http
GET /api/documents/templates

Response: List of available document types with examples
```

---

## 📊 Implementation Phases

### **Phase 1: MVP (Current)**
- ✅ Basic prompt parsing (rule-based)
- ✅ MFR generator with ReportLab
- ✅ Official Memorandum generator
- ✅ API endpoints for document generation
- ✅ Redis session storage for drafts
- ✅ PDF download endpoint

### **Phase 2: Administrative Actions**
- ✅ Appointment Letter generator
- ✅ LOC generator
- ✅ LOA generator

### **Phase 3: Advanced Features**
- ✅ LOR generator
- ✅ Multi-page document support
- ✅ Enhanced validation

---

**Planning Document Version:** 1.0
**Date:** 2025-01-05
**Status:** In Progress
