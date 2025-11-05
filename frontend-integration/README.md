# Frontend Integration Files
## Air Force Document Generator

**Branch:** `claude/document-generator-frontend-011CUp15ejs3GMBfxgJBuovn`

---

## 📦 What's Included

This directory contains **production-ready** React/TypeScript components for the Air Force Document Generator feature.

### Files (8 total, ~1,356 lines)

```
frontend-integration/
├── INTEGRATION_GUIDE.md          # Step-by-step integration instructions
├── README.md                      # This file
├── api/
│   └── documentApi.ts            # API client for backend endpoints
├── components/
│   ├── DocumentTypeSelector.tsx  # Document type picker
│   ├── MetadataForm.tsx          # Author information form
│   ├── PromptInput.tsx           # Natural language prompt input
│   └── DocumentPreview.tsx       # Review & edit extracted fields
├── pages/
│   └── DocumentGenerator.tsx     # Main page component
└── types/
    └── document.types.ts         # TypeScript type definitions
```

---

## 🚀 Quick Start

### Option 1: Copy to Your Frontend Repo

```bash
# From your pace-frontend-modern directory:
cp -r ../pace-backend-clean/frontend-integration/types src/
cp -r ../pace-backend-clean/frontend-integration/api src/
cp -r ../pace-backend-clean/frontend-integration/components src/
cp -r ../pace-backend-clean/frontend-integration/pages src/
```

### Option 2: Follow the Integration Guide

Read `INTEGRATION_GUIDE.md` for detailed step-by-step instructions.

---

## ✨ Features

- ✅ **6 Document Types:** MFR, Official Memo, Appointment Letters, LOC, LOA, LOR
- ✅ **Natural Language Input:** Describe documents in plain English
- ✅ **AI-Powered Parsing:** Extracts key information from prompts
- ✅ **Interactive Editing:** Review and edit all extracted fields
- ✅ **Real-Time Validation:** Shows warnings for missing information
- ✅ **PDF Generation:** One-click PDF download
- ✅ **Responsive Design:** Works on desktop, tablet, and mobile
- ✅ **Type-Safe:** Full TypeScript coverage
- ✅ **Example Prompts:** Built-in examples for each document type

---

## 🛠️ Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Router** - Routing

**No additional dependencies required!** Uses your existing stack.

---

## 📖 Usage Example

After integration, users can:

1. Navigate to `/documents`
2. Select document type (e.g., "Memorandum For Record")
3. Fill in their information (name, rank, office symbol)
4. Enter a natural language prompt:
   ```
   Create an MFR documenting a phone call with MSgt Smith on
   15 Jan 2025 about TDY voucher processing delays. We discussed
   the need to submit vouchers within 5 days per AFI 65-103.
   ```
5. Review extracted fields (subject, body, participants)
6. Edit any fields if needed
7. Click "Generate PDF" to download

---

## 🔌 Backend Integration

These components connect to the backend endpoints:

- `GET /api/documents/templates` - List document types
- `POST /api/documents/generate` - Parse prompt
- `POST /api/documents/{id}/generate-pdf` - Generate PDF

**Backend must be running** for full functionality.

---

## 🎨 Customization

### Colors

Default theme uses **Indigo** primary colors. To customize:

```tsx
// Change from:
className="bg-indigo-600 hover:bg-indigo-700"

// To your brand color:
className="bg-blue-600 hover:bg-blue-700"
```

### Styling

All components use Tailwind utility classes. Modify classes directly in components or extend `tailwind.config.js`.

---

## 📝 Component Details

### DocumentGenerator.tsx
Main page orchestrating the entire flow. Manages state for:
- Selected document type
- User metadata (author info)
- Prompt input
- Extracted fields
- PDF generation

### DocumentTypeSelector.tsx
Grid of buttons showing available document types with icons and descriptions.

### MetadataForm.tsx
Form for author information:
- Office symbol
- Name, rank, title
- Organization
- Phone, email (optional)

### PromptInput.tsx
Textarea for natural language input with:
- Example prompts (clickable)
- Tips for better results
- Character/word count (future)

### DocumentPreview.tsx
The most complex component. Shows extracted fields in editable form:
- Different layouts per document type
- Array field management (add/remove items)
- Inline editing
- Generate PDF button

### documentApi.ts
Axios-based API client with methods:
- `getTemplates()` - Fetch available document types
- `generateFromPrompt()` - Send prompt for parsing
- `generatePDF()` - Create final PDF
- `downloadPDF()` - Download with proper filename

### document.types.ts
Complete TypeScript definitions for all document types, requests, and responses.

---

## 🧪 Testing Checklist

After integration, test:

- [ ] Can navigate to `/documents` page
- [ ] All 6 document types display
- [ ] Can select a document type
- [ ] Metadata form accepts input
- [ ] Prompt textarea accepts text
- [ ] Example prompts are clickable
- [ ] Generate Document button works
- [ ] Extracted fields display correctly
- [ ] Can edit extracted fields
- [ ] Array fields can add/remove items
- [ ] Generate PDF downloads file
- [ ] PDF opens correctly
- [ ] Responsive on mobile/tablet
- [ ] No console errors

---

## 📚 Additional Resources

- **Backend Docs:** See `../DOCUMENT_GENERATOR_PLAN.md`
- **API Reference:** See `../API_REFERENCE.md` (if exists)
- **Tongue & Quill:** AFH 33-337 (official AF writing guide)

---

## 🤝 Contributing

To modify or extend:

1. Add new document types in backend first
2. Update `document.types.ts` with new types
3. Add rendering logic in `DocumentPreview.tsx`
4. Update `DocumentTypeSelector.tsx` with icon/description
5. Test end-to-end

---

## 🐛 Known Issues / Future Work

- [ ] Add draft saving to localStorage
- [ ] Add document history
- [ ] Support multiple file formats (Word export)
- [ ] Enhanced LLM integration for better parsing
- [ ] Batch document generation
- [ ] Document templates library

---

## 📞 Support

Questions or issues? Check:

1. **Integration Guide** - `INTEGRATION_GUIDE.md`
2. **Backend Logs** - `docker-compose logs backend`
3. **Browser Console** - F12 to check for errors
4. **Network Tab** - Verify API calls are successful

---

## ✅ Summary

**8 files, ~1,356 lines of production-ready code** that integrates seamlessly with your existing PACE frontend.

**Time to integrate:** ~15 minutes (copy files + add route)

**Complexity:** Low - no new dependencies, uses existing patterns

**Maintenance:** Minimal - self-contained feature

**Value:** High - automates AF document creation with AI

---

**Ready to integrate?** Start with `INTEGRATION_GUIDE.md`! 🚀
