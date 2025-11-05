# Air Force Document Generator - Frontend

React components and TypeScript implementation for the Air Force Document Generator feature.

## Overview

This frontend implementation provides a user-friendly interface for generating professional Air Force documents using natural language prompts. It supports 6 document types:

1. **MFR (Memorandum For Record)** - Document meetings, conversations, or events
2. **Memorandum** - Formal communication for policy or directives
3. **Appointment Letter** - Official appointment to positions or duties
4. **LOC (Letter of Counseling)** - Document minor performance/conduct issues
5. **LOA (Letter of Admonishment)** - Document moderate violations
6. **LOR (Letter of Reprimand)** - Document serious violations

## Features

- **4-Step Workflow**:
  1. Select document type
  2. Enter author information
  3. Describe content in natural language
  4. Review, edit, and generate PDF

- **Smart Parsing**: AI-powered extraction of dates, ranks, citations, and details from prompts
- **Live Editing**: Edit generated content before PDF creation
- **Validation**: Real-time validation with warnings and errors
- **Professional Formatting**: AF Tongue & Quill (AFH 33-337) compliant PDFs
- **CUI Marking**: Automatic Controlled Unclassified Information headers/footers

## Quick Start

### Copy Files to Your Project

```bash
# From pace-backend-clean directory:
cp -r frontend-files/types ../pace-frontend-modern/src/
cp -r frontend-files/api ../pace-frontend-modern/src/
cp -r frontend-files/components/document-generator ../pace-frontend-modern/src/components/
cp -r frontend-files/pages/DocumentGenerator.tsx ../pace-frontend-modern/src/pages/
```

### Configure Environment

```bash
# .env
VITE_API_URL=http://localhost:8000
```

### Add Route

```typescript
// App.tsx
import { DocumentGenerator } from './pages/DocumentGenerator';

<Route path="/document-generator" element={<DocumentGenerator />} />
```

See **INTEGRATION_GUIDE.md** for detailed setup instructions.

## File Structure

```
frontend-files/
├── api/
│   └── documentApi.ts              # API client with axios
├── components/
│   └── document-generator/
│       ├── DocumentTypeSelector.tsx   # Document type selection
│       ├── MetadataForm.tsx          # Author information form
│       ├── PromptInput.tsx           # Natural language input
│       └── DocumentPreview.tsx       # Review and edit interface
├── pages/
│   └── DocumentGenerator.tsx       # Main page orchestrator
├── types/
│   └── document.types.ts           # TypeScript definitions
├── INTEGRATION_GUIDE.md            # Detailed integration steps
└── README.md                       # This file
```

## Component Details

### DocumentGenerator (Main Page)

The main orchestrator component that manages state and workflow.

**State**:
- `currentStep` - Current workflow step
- `documentType` - Selected document type
- `metadata` - Author information
- `prompt` - User's natural language description
- `generatedDocument` - Backend response with parsed content

**Key Methods**:
- `handleGenerateDocument()` - Calls API to parse prompt and generate content
- `handleGeneratePDF()` - Generates and downloads PDF
- `handleReset()` - Resets workflow to start

### DocumentTypeSelector

Visual grid of 6 document types with icons and descriptions.

**Props**:
- `onSelect(type)` - Callback when user selects a type
- `selectedType` - Currently selected type (optional)

### MetadataForm

Form for collecting author information.

**Fields**:
- Office Symbol (required)
- Organization (required)
- Author Name (required)
- Author Rank (required, dropdown)
- Author Title (required)
- Phone (optional)
- Email (optional)

**Props**:
- `metadata` - Current metadata object
- `onChange(metadata)` - Callback on field changes
- `onNext()` - Proceed to next step
- `onBack()` - Return to previous step

### PromptInput

Natural language textarea with example prompts and tips.

**Features**:
- Document-specific tips for each type
- Clickable example prompts
- Character counter
- Loading state during generation

**Props**:
- `documentType` - Type of document being created
- `prompt` - Current prompt text
- `onChange(prompt)` - Callback on text change
- `onGenerate()` - Generate document from prompt
- `onBack()` - Return to previous step
- `isGenerating` - Loading state

### DocumentPreview

Editable preview of generated document with validation.

**Features**:
- Type-specific layouts (MFR, Memo, Appointment, Administrative Actions)
- Add/remove array items (paragraphs, duties, violations, etc.)
- Edit all fields inline
- Validation warnings and errors display
- PDF generation button

**Props**:
- `document` - DocumentResponse from backend
- `onUpdate(document)` - Callback when content is edited
- `onGeneratePDF()` - Generate PDF
- `onBack()` - Return to previous step
- `isGeneratingPDF` - Loading state

## API Client

### documentApi.ts

Axios-based API client with these methods:

```typescript
// Get document templates and metadata
getTemplates(): Promise<DocumentTemplatesResponse>

// Generate document from natural language prompt
generateFromPrompt(request: DocumentGenerationRequest): Promise<DocumentResponse>

// Generate PDF from document
generatePDF(documentId: string, request: GeneratePDFRequest): Promise<Blob>

// Generate and trigger browser download
downloadPDF(documentId: string, request: GeneratePDFRequest, filename: string): Promise<void>
```

## Type Definitions

All types are defined in `types/document.types.ts` and mirror the backend Pydantic models:

- `DocumentType` - Union type of 6 document types
- `DocumentMetadata` - Author information
- `SignatureBlock` - Signature block data
- `MFRContent`, `MemoContent`, `AppointmentContent`, `AdministrativeActionContent` - Content models
- `DocumentGenerationRequest` - Request payload for generation
- `DocumentResponse` - Response from backend with parsed content
- `ValidationResult` - Validation errors and warnings
- `GeneratePDFRequest` - PDF generation options
- `DocumentTemplatesResponse` - Template metadata

## Example Usage

### Basic Flow

```typescript
// 1. User selects "MFR"
setDocumentType('mfr');

// 2. User fills metadata
setMetadata({
  office_symbol: '51 FSS/CC',
  author_name: 'JOHN DOE',
  author_rank: 'Capt',
  author_title: 'Commander',
  organization: '51st Force Support Squadron',
});

// 3. User enters prompt
setPrompt('MFR for meeting with TSgt Johnson on 15 March 2024...');

// 4. Generate document
const response = await documentApi.generateFromPrompt({
  document_type: 'mfr',
  metadata,
  use_prompt: true,
  prompt,
});

// 5. User reviews/edits, then generates PDF
await documentApi.downloadPDF(response.document_id, {
  include_cui_marking: true,
});
```

## Styling

Uses Tailwind CSS with these color schemes:

- **Primary (Indigo)**: Interactive elements, selected states
- **Success (Green)**: PDF generation, completion
- **Warning (Yellow)**: Validation warnings
- **Error (Red)**: Validation errors
- **Neutral (Gray)**: Backgrounds, borders, text

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Requires support for:
  - ES6+ features
  - Fetch API / Axios
  - Blob API (for PDF download)

## Performance

- Lazy loading not implemented (can be added)
- API calls use axios (no caching implemented)
- PDF downloads handled via Blob URLs
- No pagination (all content loads at once)

## Accessibility

Basic accessibility features:
- Semantic HTML
- Form labels
- Button states
- Keyboard navigation (inherited from browser/React)

**Future improvements**:
- ARIA labels
- Screen reader announcements
- Focus management
- Keyboard shortcuts

## Testing Checklist

- [ ] All 6 document types can be selected
- [ ] Metadata form validates required fields
- [ ] Example prompts populate textarea
- [ ] Document generation shows loading state
- [ ] Generated content displays correctly
- [ ] Editing fields updates state
- [ ] Adding/removing array items works
- [ ] Validation errors prevent PDF generation
- [ ] PDF downloads successfully
- [ ] "Start Over" resets workflow
- [ ] Error messages display properly
- [ ] Backend connectivity works

## Future Enhancements

- [ ] Save drafts to browser localStorage
- [ ] History of generated documents
- [ ] Template favorites
- [ ] Batch document generation
- [ ] Export to Word format
- [ ] Email integration
- [ ] Collaboration features
- [ ] Unit tests with React Testing Library
- [ ] E2E tests with Playwright/Cypress

## Troubleshooting

See **INTEGRATION_GUIDE.md** for detailed troubleshooting steps.

## License

Part of the PACE (Promotion and Career Eligibility) System.
