# Quick Start - Document Generator Frontend

## For the Impatient

```bash
# 1. Copy files (from pace-backend-clean directory)
./frontend-files/COPY_COMMANDS.sh

# 2. Navigate to frontend
cd ../pace-frontend-modern

# 3. Add to src/App.tsx (after imports):
import { DocumentGenerator } from './pages/DocumentGenerator';

# 4. Add route (in your Routes component):
<Route path="/document-generator" element={<DocumentGenerator />} />

# 5. Add nav link (optional, in your nav component):
<Link to="/document-generator">Document Generator</Link>

# 6. Ensure .env has backend URL:
echo "VITE_API_URL=http://localhost:8000" >> .env

# 7. Start backend (in new terminal)
cd ../pace-backend-clean
docker-compose up -d

# 8. Start frontend
cd ../pace-frontend-modern
npm run dev

# 9. Visit http://localhost:5173/document-generator
```

## What You Get

A complete document generator interface with:

- ✅ 6 Air Force document types (MFR, Memo, Appointment, LOC, LOA, LOR)
- ✅ Natural language input ("MFR for meeting with TSgt Johnson on 15 March...")
- ✅ Smart parsing of dates, ranks, citations, duties
- ✅ Editable preview before PDF generation
- ✅ AF Tongue & Quill compliant PDFs with CUI marking
- ✅ Validation warnings and error handling
- ✅ Professional UI with Tailwind CSS

## Example Prompt

```
MFR for meeting with TSgt Johnson on 15 March 2024 regarding EPR feedback.
Discussed performance strengths in customer service and leadership.
Identified areas for improvement in technical knowledge.
Meeting held in building 123, conference room A.
```

## File Structure After Copy

```
pace-frontend-modern/src/
├── api/
│   └── documentApi.ts
├── components/
│   └── document-generator/
│       ├── DocumentTypeSelector.tsx
│       ├── MetadataForm.tsx
│       ├── PromptInput.tsx
│       ├── DocumentPreview.tsx
│       └── index.ts
├── pages/
│   └── DocumentGenerator.tsx
└── types/
    └── document.types.ts
```

## Troubleshooting

**Problem**: "Failed to generate document"
- Check backend is running: `curl http://localhost:8000/api/health`
- Verify VITE_API_URL in .env matches backend URL
- Check browser console for CORS errors

**Problem**: TypeScript errors
- Restart TypeScript server in VS Code
- Ensure files are in correct locations
- Run `npm run build` to check compilation

**Problem**: Styles broken
- Verify Tailwind CSS is configured
- Check tailwind.config.js includes component paths
- Ensure @tailwind directives are in main CSS

## Next Steps

- Read **INTEGRATION_GUIDE.md** for detailed setup
- Read **README.md** for component documentation
- Test all 6 document types
- Customize styles to match your design
- Add to your main navigation

## Need Help?

- Check logs: `docker-compose logs backend`
- Review API docs: `pace-backend-clean/API_REFERENCE.md`
- See architecture: `pace-backend-clean/CLAUDE.md`
