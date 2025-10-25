# Roster Editing Feature - Technical Specification

**Document Version:** 1.0
**Date:** October 23, 2025
**Status:** Proposal
**Author:** Technical Specification

---

## Executive Summary

This document specifies the technical requirements for adding pre-PDF editing capabilities to the PACE backend system. The feature will allow users to review, edit, add, and remove members from processed rosters before generating final PDFs, as well as customize the logo displayed on generated documents.

---

## Table of Contents

1. [Current System Overview](#current-system-overview)
2. [Feature Requirements](#feature-requirements)
3. [System Architecture Changes](#system-architecture-changes)
4. [API Endpoint Specifications](#api-endpoint-specifications)
5. [Data Models](#data-models)
6. [Frontend Requirements](#frontend-requirements)
7. [Security Considerations](#security-considerations)
8. [Implementation Phases](#implementation-phases)
9. [Testing Requirements](#testing-requirements)
10. [Performance Considerations](#performance-considerations)

---

## 1. Current System Overview

### Current Workflow

```
User Upload Roster (CSV/Excel)
    ↓
Backend Processes → Eligibility Determination
    ↓
Session Stored in Redis (30 min TTL)
    ↓
User Submits PASCODE Info
    ↓
PDF Generated & Downloaded
```

### Current Limitations

- **No Preview:** Users cannot see processed results before PDF generation
- **No Editing:** Cannot modify eligibility decisions or member data
- **No Manual Additions:** Cannot add members manually
- **No Manual Removals:** Cannot remove incorrectly flagged members
- **Fixed Logo:** Logo is hardcoded, cannot be customized per session
- **No Validation UI:** Errors only visible in logs or API response

---

## 2. Feature Requirements

### 2.1 Roster Preview & Review

**Functional Requirements:**
- Display processed roster data in tabular format
- Show categorized lists:
  - Eligible members
  - Ineligible members (with reasons)
  - Discrepancy members (with flags)
  - BTZ eligible members
  - Small unit members
- Display processing statistics and summary
- Show error log (if any errors occurred)

**User Actions:**
- View all processed members
- Filter by category (eligible/ineligible/discrepancy/BTZ)
- Search members by name, SSAN, or PASCODE
- Sort by any column

### 2.2 Member Editing

**Functional Requirements:**
- **Edit Existing Members:**
  - Modify any field (name, grade, dates, AFSC, etc.)
  - Change eligibility status (eligible ↔ ineligible)
  - Move between categories (e.g., eligible → discrepancy)
  - Edit ineligibility/discrepancy reasons
- **Add New Members:**
  - Manually add member with all required fields
  - Set eligibility status manually
  - Assign to appropriate category
  - Bypass normal eligibility checks (manual override)
- **Remove Members:**
  - Remove from eligible list
  - Remove from ineligible list
  - Remove from any category
  - Option to soft-delete (mark as removed) or hard-delete

**Validation:**
- Required fields validation before saving edits
- Date format validation
- Grade validation (must be valid enlisted rank)
- AFSC format validation
- PASCODE validation

### 2.3 Logo Customization

**Functional Requirements:**
- Upload custom logo per session
- Replace default logo for PDF generation
- Preview logo before PDF generation
- Revert to default logo option

**Technical Requirements:**
- Support image formats: PNG, JPG, JPEG
- Maximum file size: 5MB
- Recommended dimensions: 100x100 to 300x300 pixels
- Auto-resize/crop to fit PDF template (1 inch square)
- Store in session for duration of session TTL

---

## 3. System Architecture Changes

### 3.1 New Components

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (React)                    │
├─────────────────────────────────────────────────────┤
│  • Roster Review Table Component                    │
│  • Member Edit Modal/Form                            │
│  • Add Member Modal                                  │
│  • Logo Upload Component                             │
│  • Confirmation Dialogs                              │
└─────────────────────────────────────────────────────┘
                        │ HTTP/REST API
                        ↓
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend (New Endpoints)         │
├─────────────────────────────────────────────────────┤
│  • GET  /api/roster/preview/{session_id}             │
│  • PUT  /api/roster/member/{session_id}/{member_id}  │
│  • POST /api/roster/member/{session_id}              │
│  • DELETE /api/roster/member/{session_id}/{member_id}│
│  • POST /api/roster/logo/{session_id}                │
│  • GET  /api/roster/logo/{session_id}                │
│  • DELETE /api/roster/logo/{session_id}              │
│  • POST /api/roster/reprocess/{session_id}           │
└─────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────┐
│           Redis Session Store (Enhanced)             │
├─────────────────────────────────────────────────────┤
│  • Original roster data                              │
│  • Processed roster data                             │
│  • Edit history/audit trail                          │
│  • Custom logo (base64 encoded)                      │
│  • User modifications flag                           │
└─────────────────────────────────────────────────────┘
```

### 3.2 Session Data Structure Enhancement

**Current Session:**
```json
{
  "dataframe": [...],
  "pdf_dataframe": [...],
  "eligible_df": [...],
  "ineligible_df": [...],
  "discrepancy_df": [...],
  "btz_df": [...],
  "small_unit_df": [...],
  "pascodes": [...],
  "pascode_map": {...},
  "cycle": "SSG",
  "year": 2025,
  "error_log": [...]
}
```

**Enhanced Session:**
```json
{
  // Existing fields...
  "dataframe": [...],
  "eligible_df": [...],

  // NEW: Original unmodified data (for reference/revert)
  "original_eligible_df": [...],
  "original_ineligible_df": [...],
  "original_discrepancy_df": [...],
  "original_btz_df": [...],

  // NEW: Edit tracking
  "edited": true,
  "edit_history": [
    {
      "timestamp": "2025-10-23T19:30:00Z",
      "action": "edit_member",
      "member_id": "row_index_42",
      "field": "eligibility_status",
      "old_value": "ineligible",
      "new_value": "eligible",
      "reason": "Manual override by user"
    },
    {
      "timestamp": "2025-10-23T19:31:00Z",
      "action": "add_member",
      "member_data": {...},
      "reason": "Missing from original roster"
    }
  ],

  // NEW: Custom logo
  "custom_logo": {
    "filename": "squadron_logo.png",
    "data": "base64_encoded_image_data...",
    "content_type": "image/png",
    "uploaded_at": "2025-10-23T19:25:00Z"
  },

  // NEW: Processing metadata
  "processing_metadata": {
    "total_uploaded": 150,
    "total_processed": 148,
    "eligible_count": 120,
    "ineligible_count": 25,
    "discrepancy_count": 3,
    "btz_count": 2,
    "errors_count": 2,
    "last_modified": "2025-10-23T19:31:00Z"
  }
}
```

---

## 4. API Endpoint Specifications

### 4.1 Roster Preview Endpoint

**Endpoint:** `GET /api/roster/preview/{session_id}`

**Description:** Retrieve processed roster data for review and editing

**Path Parameters:**
- `session_id` (string, required) - Session UUID

**Query Parameters:**
- `category` (string, optional) - Filter by category: `eligible`, `ineligible`, `discrepancy`, `btz`, `small_unit`, `all`
- `page` (integer, optional, default: 1) - Page number for pagination
- `page_size` (integer, optional, default: 50) - Items per page

**Response (200 OK):**
```json
{
  "session_id": "abc123...",
  "cycle": "SSG",
  "year": 2025,
  "edited": false,
  "statistics": {
    "total_uploaded": 150,
    "total_processed": 148,
    "eligible": 120,
    "ineligible": 25,
    "discrepancy": 3,
    "btz": 2,
    "errors": 2
  },
  "categories": {
    "eligible": [
      {
        "member_id": "row_42",
        "FULL_NAME": "SMITH, JOHN A",
        "GRADE": "SSG",
        "SSAN": "1234",
        "DOR": "01-JAN-2022",
        "ASSIGNED_PAS": "FFABC",
        "ASSIGNED_PAS_CLEARTEXT": "51st Fighter Squadron",
        "DAFSC": "3D1X7",
        "TAFMSD": "01-JAN-2019",
        "DATE_ARRIVED_STATION": "15-MAR-2023",
        "editable": true
      }
    ],
    "ineligible": [
      {
        "member_id": "row_43",
        "FULL_NAME": "DOE, JANE B",
        "GRADE": "SSG",
        "REASON": "Insufficient TIG",
        "editable": true
      }
    ],
    "discrepancy": [
      {
        "member_id": "row_44",
        "FULL_NAME": "BROWN, ROBERT C",
        "GRADE": "SSG",
        "REASON": "UIF code: 2",
        "editable": true
      }
    ],
    "btz": [...],
    "small_unit": [...]
  },
  "errors": [
    "Missing required data at row 5, column TAFMSD",
    "Officer WILLIAMS, MARY (2LT) excluded from enlisted promotion processing"
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_pages": 3,
    "total_items": 148
  },
  "custom_logo": {
    "uploaded": true,
    "filename": "squadron_logo.png"
  }
}
```

**Error Responses:**
- `404 Not Found` - Session not found or expired
- `500 Internal Server Error` - Server error

---

### 4.2 Edit Member Endpoint

**Endpoint:** `PUT /api/roster/member/{session_id}/{member_id}`

**Description:** Edit an existing member's data or eligibility status

**Path Parameters:**
- `session_id` (string, required) - Session UUID
- `member_id` (string, required) - Member identifier (e.g., "row_42")

**Request Body:**
```json
{
  "action": "update_eligibility",  // or "update_data"
  "category": "eligible",  // Target category: eligible, ineligible, discrepancy, btz
  "data": {
    "FULL_NAME": "SMITH, JOHN A",
    "GRADE": "SSG",
    "DOR": "01-JAN-2022",
    "TAFMSD": "01-JAN-2019",
    "DATE_ARRIVED_STATION": "15-MAR-2023",
    "PAFSC": "3D1X7",
    "ASSIGNED_PAS": "FFABC",
    "ASSIGNED_PAS_CLEARTEXT": "51st Fighter Squadron"
    // ... other fields
  },
  "reason": "Manual override - corrected date",  // Optional reason for audit
  "override_validation": false  // Skip eligibility re-check if true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "member_id": "row_42",
  "message": "Member updated successfully",
  "updated_category": "eligible",
  "previous_category": "ineligible",
  "recalculated": false,
  "timestamp": "2025-10-23T19:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Validation failed
- `404 Not Found` - Session or member not found
- `422 Unprocessable Entity` - Invalid data format

---

### 4.3 Add Member Endpoint

**Endpoint:** `POST /api/roster/member/{session_id}`

**Description:** Manually add a new member to the roster

**Path Parameters:**
- `session_id` (string, required) - Session UUID

**Request Body:**
```json
{
  "category": "eligible",  // Target category
  "data": {
    "FULL_NAME": "NEW, MEMBER A",
    "GRADE": "SSG",
    "SSAN": "5678",
    "DOR": "01-JAN-2022",
    "TAFMSD": "01-JAN-2019",
    "DATE_ARRIVED_STATION": "15-MAR-2023",
    "PAFSC": "3D1X7",
    "ASSIGNED_PAS": "FFABC",
    "ASSIGNED_PAS_CLEARTEXT": "51st Fighter Squadron",
    "DAFSC": "3D1X7",
    "REENL_ELIG_STATUS": "1A",
    "UIF_CODE": 0
    // ... all required fields
  },
  "reason": "Member missing from original roster upload",
  "run_eligibility_check": false  // If true, runs through board_filter
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "member_id": "manual_add_1",
  "message": "Member added successfully",
  "category": "eligible",
  "timestamp": "2025-10-23T19:35:00Z",
  "eligibility_check_result": null  // Or eligibility check results if run
}
```

**Error Responses:**
- `400 Bad Request` - Missing required fields or validation failed
- `404 Not Found` - Session not found
- `422 Unprocessable Entity` - Invalid data

---

### 4.4 Delete Member Endpoint

**Endpoint:** `DELETE /api/roster/member/{session_id}/{member_id}`

**Description:** Remove a member from the roster

**Path Parameters:**
- `session_id` (string, required) - Session UUID
- `member_id` (string, required) - Member identifier

**Query Parameters:**
- `hard_delete` (boolean, optional, default: false) - If true, permanently deletes. If false, marks as removed.

**Request Body:**
```json
{
  "reason": "Duplicate entry - member already processed elsewhere"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "member_id": "row_42",
  "message": "Member removed successfully",
  "deleted_from_category": "eligible",
  "hard_delete": false,
  "timestamp": "2025-10-23T19:40:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Session or member not found
- `400 Bad Request` - Invalid request

---

### 4.5 Upload Custom Logo Endpoint

**Endpoint:** `POST /api/roster/logo/{session_id}`

**Description:** Upload a custom logo for PDF generation

**Path Parameters:**
- `session_id` (string, required) - Session UUID

**Request:**
- **Content-Type:** `multipart/form-data`
- **Fields:**
  - `logo` (file, required) - Image file (PNG, JPG, JPEG)
  - `replace_existing` (boolean, optional, default: true)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logo uploaded successfully",
  "filename": "squadron_logo.png",
  "content_type": "image/png",
  "size_bytes": 45678,
  "preview_url": "/api/roster/logo/{session_id}",
  "timestamp": "2025-10-23T19:45:00Z"
}
```

**Validation:**
- Max file size: 5MB
- Allowed types: `image/png`, `image/jpeg`, `image/jpg`
- Image will be resized to fit 1 inch square in PDF

**Error Responses:**
- `400 Bad Request` - Invalid file type or size too large
- `404 Not Found` - Session not found
- `413 Payload Too Large` - File exceeds 5MB limit

---

### 4.6 Get Custom Logo Endpoint

**Endpoint:** `GET /api/roster/logo/{session_id}`

**Description:** Retrieve the custom logo for preview

**Path Parameters:**
- `session_id` (string, required) - Session UUID

**Response (200 OK):**
- **Content-Type:** `image/png` or `image/jpeg`
- **Body:** Binary image data

**Error Responses:**
- `404 Not Found` - Session not found or no custom logo uploaded

---

### 4.7 Delete Custom Logo Endpoint

**Endpoint:** `DELETE /api/roster/logo/{session_id}`

**Description:** Remove custom logo and revert to default

**Path Parameters:**
- `session_id` (string, required) - Session UUID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Custom logo removed, reverted to default",
  "timestamp": "2025-10-23T19:50:00Z"
}
```

---

### 4.8 Reprocess Roster Endpoint

**Endpoint:** `POST /api/roster/reprocess/{session_id}`

**Description:** Re-run eligibility checks on all members (useful after bulk edits)

**Path Parameters:**
- `session_id` (string, required) - Session UUID

**Request Body:**
```json
{
  "preserve_manual_edits": true,  // Keep manual overrides
  "categories": ["eligible", "ineligible"]  // Only reprocess specific categories
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Roster reprocessed successfully",
  "changes": {
    "eligible_to_ineligible": 2,
    "ineligible_to_eligible": 1,
    "no_change": 145
  },
  "preserved_edits": 3,
  "timestamp": "2025-10-23T19:55:00Z"
}
```

---

## 5. Data Models

### 5.1 Member Data Model (Pydantic)

```python
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class MemberBase(BaseModel):
    FULL_NAME: str
    GRADE: str
    SSAN: Optional[str] = None
    DOR: str  # Date string
    TAFMSD: str  # Date string
    DATE_ARRIVED_STATION: str  # Date string
    PAFSC: str
    ASSIGNED_PAS: str
    ASSIGNED_PAS_CLEARTEXT: str
    DAFSC: str
    REENL_ELIG_STATUS: Optional[str] = None
    UIF_CODE: Optional[int] = 0
    UIF_DISPOSITION_DATE: Optional[str] = None
    GRADE_PERM_PROJ: Optional[str] = None
    AFSC_2: Optional[str] = None
    AFSC_3: Optional[str] = None
    AFSC_4: Optional[str] = None

    @validator('GRADE')
    def validate_grade(cls, v):
        valid_grades = ['AB', 'AMN', 'A1C', 'SRA', 'SSG', 'TSG', 'MSG', 'SMS']
        if v not in valid_grades:
            raise ValueError(f'Invalid grade: {v}')
        return v

    @validator('DOR', 'TAFMSD', 'DATE_ARRIVED_STATION')
    def validate_date_format(cls, v):
        # Validate date format
        try:
            datetime.strptime(v, '%d-%b-%Y')
        except:
            raise ValueError(f'Invalid date format: {v}. Expected DD-MMM-YYYY')
        return v

class MemberEdit(BaseModel):
    action: str  # "update_eligibility" or "update_data"
    category: str  # "eligible", "ineligible", "discrepancy", "btz"
    data: MemberBase
    reason: Optional[str] = None
    override_validation: bool = False

class MemberAdd(BaseModel):
    category: str
    data: MemberBase
    reason: str
    run_eligibility_check: bool = False

class MemberDelete(BaseModel):
    reason: str
```

### 5.2 Edit History Model

```python
class EditHistoryEntry(BaseModel):
    timestamp: str
    action: str  # "edit_member", "add_member", "delete_member", "reprocess"
    member_id: Optional[str] = None
    field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None
    user_ip: Optional[str] = None  # For audit trail
```

---

## 6. Frontend Requirements

### 6.1 New UI Components

**1. Roster Review Page**
```
┌─────────────────────────────────────────────────────┐
│  Roster Review - SSG 2025                     [Logo]│
├─────────────────────────────────────────────────────┤
│  Statistics:                                         │
│  ✓ 120 Eligible  ✗ 25 Ineligible  ⚠ 3 Discrepancy  │
│  ⭐ 2 BTZ  🏢 5 Small Unit  ⚠️ 2 Errors             │
├─────────────────────────────────────────────────────┤
│  [Filter: All ▼] [Search: ___________] [+ Add]      │
├─────────────────────────────────────────────────────┤
│  Name          Grade  PASCODE  Status    Actions    │
│  SMITH, JOHN   SSG    FFABC    Eligible  [Edit][Del]│
│  DOE, JANE     SSG    FFABC    Ineligib  [Edit][Del]│
│  BROWN, BOB    SSG    FFDEF    Discrep   [Edit][Del]│
│  ...                                                 │
├─────────────────────────────────────────────────────┤
│  [< Prev] Page 1 of 3 [Next >]                      │
├─────────────────────────────────────────────────────┤
│  [Upload Logo] [Reprocess All] [Generate PDF]       │
└─────────────────────────────────────────────────────┘
```

**2. Edit Member Modal**
```
┌─────────────────────────────────────────────────────┐
│  Edit Member: SMITH, JOHN A                    [X]  │
├─────────────────────────────────────────────────────┤
│  Category: [Eligible ▼]                             │
│                                                      │
│  Full Name:    [SMITH, JOHN A____________]          │
│  Grade:        [SSG ▼]                              │
│  SSAN:         [1234__________________]             │
│  DOR:          [01-JAN-2022] [📅]                   │
│  TAFMSD:       [01-JAN-2019] [📅]                   │
│  DAS:          [15-MAR-2023] [📅]                   │
│  PAFSC:        [3D1X7__________________]            │
│  PASCODE:      [FFABC__________________]            │
│  Unit:         [51st Fighter Squadron____]          │
│                                                      │
│  Reason for Edit (optional):                        │
│  [_________________________________________]         │
│                                                      │
│  ☐ Override validation (skip eligibility check)    │
│                                                      │
│  [Cancel]                          [Save Changes]   │
└─────────────────────────────────────────────────────┘
```

**3. Add Member Modal**
```
┌─────────────────────────────────────────────────────┐
│  Add New Member                                [X]  │
├─────────────────────────────────────────────────────┤
│  Add to Category: [Eligible ▼]                      │
│                                                      │
│  Full Name:    [___________________________]        │
│  Grade:        [SSG ▼]                              │
│  SSAN:         [___________________________]        │
│  DOR:          [___________] [📅]                   │
│  TAFMSD:       [___________] [📅]                   │
│  DAS:          [___________] [📅]                   │
│  PAFSC:        [___________________________]        │
│  PASCODE:      [___________________________]        │
│  Unit:         [___________________________]        │
│                                                      │
│  Reason for Addition (required):                    │
│  [Missing from original upload_______________]      │
│                                                      │
│  ☐ Run eligibility check (recommended)             │
│                                                      │
│  [Cancel]                            [Add Member]   │
└─────────────────────────────────────────────────────┘
```

**4. Logo Upload Component**
```
┌─────────────────────────────────────────────────────┐
│  Custom Logo                                   [X]  │
├─────────────────────────────────────────────────────┤
│  Current Logo:                                       │
│  ┌──────────┐                                       │
│  │          │  Default Logo                         │
│  │  [LOGO]  │  (fiftyonefss.jpeg)                   │
│  │          │                                        │
│  └──────────┘                                       │
│                                                      │
│  Upload Custom Logo:                                │
│  [Choose File] squadron_logo.png                    │
│                                                      │
│  Supported: PNG, JPG, JPEG                          │
│  Max size: 5MB                                      │
│  Recommended: 100x100 to 300x300 pixels             │
│                                                      │
│  [Remove Custom Logo] [Upload]                      │
└─────────────────────────────────────────────────────┘
```

### 6.2 User Workflows

**Workflow 1: Edit Member Eligibility**
```
1. User uploads roster
2. System processes → Review page shows results
3. User clicks "Edit" on ineligible member
4. Edit modal opens with member data
5. User changes category to "Eligible"
6. User enters reason: "Corrected DOR - was entered wrong"
7. User saves
8. System updates session data
9. Review page refreshes with updated counts
10. User continues to PDF generation
```

**Workflow 2: Add Missing Member**
```
1. User on review page
2. User clicks "+ Add Member"
3. Add modal opens
4. User fills in all required fields
5. User selects category "Eligible"
6. User enters reason: "Member missing from MILPDS export"
7. User optionally runs eligibility check
8. User saves
9. Member appears in eligible list
10. Unit totals recalculated
```

**Workflow 3: Upload Custom Logo**
```
1. User on review page
2. User clicks "Upload Logo"
3. Logo modal opens
4. User selects image file
5. System validates (size, type)
6. Preview shows uploaded logo
7. User confirms
8. Logo stored in session
9. Future PDFs use custom logo
```

---

## 7. Security Considerations

### 7.1 Authentication & Authorization

**Current State:**
- No authentication implemented
- Sessions identified by UUID only

**Recommendations:**
- Add session-level password/PIN (optional feature)
- Track session creator IP address
- Limit edits to session creator IP (configurable)
- Add read-only session sharing link

### 7.2 Input Validation

**Required Validations:**
- Sanitize all user inputs to prevent injection
- Validate file uploads (magic bytes, not just extension)
- Limit upload sizes (5MB for logos)
- Validate date formats before storing
- Validate grade values against whitelist
- Limit edit history size (prevent DoS via excessive edits)

### 7.3 Data Integrity

**Measures:**
- Store original data separately (immutable)
- Audit trail for all edits
- Checksum verification for uploaded files
- Session data validation before PDF generation
- Revert capability (restore original)

### 7.4 Rate Limiting

**Implement Rate Limits:**
- Edit operations: 100 per session
- Add operations: 50 per session
- Logo uploads: 5 per session
- API calls: 100 per minute per IP

---

## 8. Implementation Phases

### Phase 1: Backend API Foundation (Week 1)

**Tasks:**
1. ✅ Enhance session data model
2. ✅ Implement roster preview endpoint
3. ✅ Add edit member endpoint
4. ✅ Add delete member endpoint
5. ✅ Implement edit history tracking
6. ✅ Add unit tests for new endpoints

**Deliverables:**
- Working API endpoints
- Updated session_manager.py
- API documentation
- Unit tests (80%+ coverage)

### Phase 2: Member Management (Week 2)

**Tasks:**
1. ✅ Implement add member endpoint
2. ✅ Add validation logic
3. ✅ Implement reprocess endpoint
4. ✅ Update PDF generators to use edited data
5. ✅ Add integration tests

**Deliverables:**
- Complete CRUD operations for members
- Validation framework
- Updated PDF generators
- Integration tests

### Phase 3: Logo Management (Week 3)

**Tasks:**
1. ✅ Implement logo upload endpoint
2. ✅ Add image processing (resize, validation)
3. ✅ Update PDF templates to use custom logo
4. ✅ Implement logo preview endpoint
5. ✅ Add logo delete endpoint

**Deliverables:**
- Logo upload/delete functionality
- Image processing pipeline
- Updated PDF templates
- Logo tests

### Phase 4: Frontend Development (Week 4-5)

**Tasks:**
1. ✅ Create roster review page
2. ✅ Implement edit member modal
3. ✅ Implement add member modal
4. ✅ Create logo upload component
5. ✅ Add search/filter functionality
6. ✅ Implement pagination
7. ✅ Add confirmation dialogs

**Deliverables:**
- Complete UI components
- User workflows implemented
- Frontend-backend integration
- UI/UX tests

### Phase 5: Testing & Refinement (Week 6)

**Tasks:**
1. ✅ End-to-end testing
2. ✅ Performance testing
3. ✅ Security testing
4. ✅ User acceptance testing
5. ✅ Bug fixes and refinements
6. ✅ Documentation updates

**Deliverables:**
- Test reports
- Bug fixes
- Updated documentation
- Deployment readiness

---

## 9. Testing Requirements

### 9.1 Unit Tests

**Backend:**
```python
# test_roster_editing.py

def test_preview_endpoint_returns_all_categories():
    """Test preview endpoint returns all member categories"""
    pass

def test_edit_member_updates_session():
    """Test editing member updates Redis session"""
    pass

def test_edit_member_creates_audit_trail():
    """Test edit creates entry in edit_history"""
    pass

def test_add_member_validates_required_fields():
    """Test adding member validates all required fields"""
    pass

def test_delete_member_soft_delete():
    """Test soft delete marks member as removed"""
    pass

def test_delete_member_hard_delete():
    """Test hard delete removes member completely"""
    pass

def test_logo_upload_validates_file_type():
    """Test logo upload rejects invalid file types"""
    pass

def test_logo_upload_validates_file_size():
    """Test logo upload rejects files >5MB"""
    pass

def test_reprocess_preserves_manual_edits():
    """Test reprocessing preserves manual overrides"""
    pass
```

### 9.2 Integration Tests

**Scenarios:**
1. Upload roster → Edit member → Generate PDF → Verify edited data in PDF
2. Upload roster → Add member → Verify unit totals updated
3. Upload roster → Delete member → Verify not in PDF
4. Upload custom logo → Generate PDF → Verify logo appears
5. Edit multiple members → Reprocess → Verify preserved

### 9.3 Performance Tests

**Metrics to Test:**
- Preview endpoint response time (target: <500ms for 200 members)
- Edit operation latency (target: <200ms)
- Logo upload processing time (target: <2s for 5MB)
- Session data size after 100 edits (target: <10MB)
- PDF generation time with edited data (target: <5s)

---

## 10. Performance Considerations

### 10.1 Session Storage Optimization

**Current Challenge:**
- Redis session can grow large with edit history

**Solutions:**
1. **Limit edit history to last 50 entries**
2. **Compress large dataframes** before storing
3. **Store logos in separate Redis key** with independent TTL
4. **Pagination for large rosters** (only load visible page)

### 10.2 API Response Optimization

**Strategies:**
1. **Lazy loading:** Only load requested categories
2. **Pagination:** Default 50 items per page
3. **Caching:** Cache processed preview data for 5 minutes
4. **Compression:** Use gzip for large responses

### 10.3 Frontend Performance

**Optimizations:**
1. **Virtual scrolling** for large tables (>100 rows)
2. **Debounced search** (300ms delay)
3. **Lazy image loading** for logo preview
4. **Optimistic UI updates** (update UI before API response)

---

## 11. Database Schema (Optional Enhancement)

**If Moving from Redis to PostgreSQL:**

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    cycle VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    edited BOOLEAN DEFAULT FALSE,
    custom_logo_id INTEGER REFERENCES logos(id)
);

-- Members table
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    member_id VARCHAR(50) NOT NULL,
    category VARCHAR(20) NOT NULL,  -- eligible, ineligible, etc.
    full_name VARCHAR(255) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    ssan VARCHAR(20),
    dor DATE NOT NULL,
    tafmsd DATE NOT NULL,
    date_arrived_station DATE,
    pafsc VARCHAR(20),
    assigned_pas VARCHAR(20),
    assigned_pas_cleartext VARCHAR(255),
    dafsc VARCHAR(20),
    reenl_elig_status VARCHAR(10),
    uif_code INTEGER DEFAULT 0,
    is_manual_add BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    data JSONB,  -- Store all other fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Edit history table
CREATE TABLE edit_history (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    member_id INTEGER REFERENCES members(id),
    action VARCHAR(50) NOT NULL,
    field VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    user_ip VARCHAR(45),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Logos table
CREATE TABLE logos (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    data BYTEA NOT NULL,
    size_bytes INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_members_session ON members(session_id);
CREATE INDEX idx_members_category ON members(category);
CREATE INDEX idx_edit_history_session ON edit_history(session_id);
```

---

## 12. API Documentation Template

**Generate OpenAPI/Swagger Documentation:**

```yaml
openapi: 3.0.0
info:
  title: PACE Roster Editing API
  version: 1.0.0
  description: API for editing Air Force promotion rosters

paths:
  /api/roster/preview/{session_id}:
    get:
      summary: Get roster preview
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Roster preview data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RosterPreview'

  # ... (other endpoints)

components:
  schemas:
    RosterPreview:
      type: object
      properties:
        session_id:
          type: string
        cycle:
          type: string
        year:
          type: integer
        # ... (other properties)
```

---

## 13. Migration Plan

### 13.1 Backward Compatibility

**Ensure Old Workflow Still Works:**
- Existing `/api/upload/initial-mel` endpoint unchanged
- Editing is **optional** - can skip directly to PDF generation
- Default behavior: process roster → generate PDF (no changes)
- New workflow: process roster → review/edit → generate PDF

### 13.2 Gradual Rollout

**Phase 1: Backend Only (Week 1-3)**
- Deploy new API endpoints
- Old frontend continues to work
- New endpoints available but unused

**Phase 2: Optional Preview (Week 4-5)**
- Add "Review Before PDF" button in frontend
- Users can opt-in to new workflow
- Default: old workflow (direct to PDF)

**Phase 3: Default Preview (Week 6+)**
- New workflow becomes default
- "Skip Review" option for power users
- Monitor usage metrics

---

## 14. Success Metrics

### 14.1 Adoption Metrics

- % of users who use preview/edit feature
- Average number of edits per session
- % of rosters with manual additions
- % of sessions with custom logos

### 14.2 Quality Metrics

- Reduction in PDF regeneration requests
- User-reported errors before/after editing
- Average time spent on review page
- User satisfaction score

### 14.3 Performance Metrics

- API response time (p95, p99)
- PDF generation time with edits vs without
- Session storage size growth
- Error rate on edit operations

---

## 15. Open Questions & Decisions Needed

### 15.1 Questions

1. **Session Expiration:** Should editing extend the 30-min TTL?
2. **Bulk Edits:** Should we support CSV import for bulk edits?
3. **Undo/Redo:** Should we implement undo/redo functionality?
4. **Collaboration:** Should multiple users be able to edit the same session?
5. **Audit Export:** Should edit history be exportable?

### 15.2 Design Decisions

1. **Storage:** Redis vs PostgreSQL for edited data?
2. **Validation:** Client-side only vs server-side vs both?
3. **Real-time:** WebSocket updates for collaborative editing?
4. **Versioning:** Should we version roster snapshots?
5. **Rollback:** Full roster rollback vs individual member revert?

---

## 16. Risk Assessment

### 16.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Session data corruption | Medium | High | Validate on every update, keep original |
| Large session size (>10MB) | High | Medium | Implement pagination, compression |
| Redis memory exhaustion | Low | High | Set memory limits, monitor usage |
| Image processing DoS | Medium | Medium | Rate limiting, file size limits |
| Edit conflicts (future collab) | Low | Medium | Implement optimistic locking |

### 16.2 User Experience Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Confusion with new workflow | High | Low | Clear UI, optional feature initially |
| Accidental deletions | Medium | High | Confirmation dialogs, soft delete default |
| Lost edits (session expiry) | Medium | High | Auto-save, warning before expiry |
| Over-editing (incorrect changes) | Medium | Medium | Audit trail, revert capability |

---

## 17. Glossary

- **BTZ:** Below The Zone - Early promotion eligibility
- **PASCODE:** Personnel Accounting Symbol Code - Unit identifier
- **SRID:** Senior Rater Identification - Commander identifier
- **DOR:** Date of Rank
- **TAFMSD:** Total Active Federal Military Service Date
- **DAS:** Date Arrived Station
- **PAFSC:** Primary Air Force Specialty Code
- **MEL:** Master Eligibility List
- **UIF:** Unfavorable Information File
- **SCOD:** Selection Cutoff Date

---

## Appendix A: Example API Calls

### Preview Roster
```bash
curl -X GET "http://localhost:8000/api/roster/preview/abc-123-def" \
  -H "Accept: application/json"
```

### Edit Member
```bash
curl -X PUT "http://localhost:8000/api/roster/member/abc-123-def/row_42" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "update_eligibility",
    "category": "eligible",
    "data": {
      "FULL_NAME": "SMITH, JOHN A",
      "GRADE": "SSG",
      ...
    },
    "reason": "Corrected DOR"
  }'
```

### Add Member
```bash
curl -X POST "http://localhost:8000/api/roster/member/abc-123-def" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "eligible",
    "data": {
      "FULL_NAME": "NEW, MEMBER A",
      ...
    },
    "reason": "Missing from original upload"
  }'
```

### Upload Logo
```bash
curl -X POST "http://localhost:8000/api/roster/logo/abc-123-def" \
  -F "logo=@squadron_logo.png"
```

---

**END OF SPECIFICATION**

---

**Document Control:**
- **Version:** 1.0
- **Last Updated:** October 23, 2025
- **Next Review:** November 1, 2025
- **Approval Required From:** Technical Lead, Product Owner
- **Implementation Start:** TBD
