# Frontend Integration Guide
## Air Force Document Generator

This guide explains how to integrate the Document Generator feature into your `pace-frontend-modern` React application.

---

## 📋 Prerequisites

- React 19 + TypeScript + Vite (already set up)
- Tailwind CSS (already configured)
- Axios for API calls (already installed)
- React Router (already configured)

---

## 🚀 Step-by-Step Integration

### Step 1: Copy Files to Frontend

Copy all files from `frontend-integration/` to your `pace-frontend-modern/` directory:

```bash
# From your pace-frontend-modern directory:

# Copy types
cp ../pace-backend-clean/frontend-integration/types/document.types.ts src/types/

# Copy API
cp ../pace-backend-clean/frontend-integration/api/documentApi.ts src/api/

# Copy components
cp ../pace-backend-clean/frontend-integration/components/*.tsx src/components/

# Copy page
cp ../pace-backend-clean/frontend-integration/pages/DocumentGenerator.tsx src/pages/
```

### Step 2: Update App.tsx (Add Route)

Add the Document Generator route to your `src/App.tsx`:

```tsx
import DocumentGenerator from './pages/DocumentGenerator';

// Inside your Routes:
<Route path="/documents" element={<DocumentGenerator />} />
```

**Full example:**
```tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DocumentGenerator from './pages/DocumentGenerator';
// ... other imports

function App() {
  return (
    <Router>
      <Routes>
        {/* Existing routes */}
        <Route path="/" element={<Dashboard />} />
        <Route path="/initial-mel" element={<InitialMEL />} />
        <Route path="/final-mel" element={<FinalMEL />} />

        {/* NEW: Document Generator route */}
        <Route path="/documents" element={<DocumentGenerator />} />

        {/* Other routes... */}
      </Routes>
    </Router>
  );
}
```

### Step 3: Add Navigation Link

Update your navigation menu (likely in `src/components/Navigation.tsx` or similar):

```tsx
<nav>
  {/* Existing links */}
  <Link to="/">Dashboard</Link>
  <Link to="/initial-mel">Initial MEL</Link>
  <Link to="/final-mel">Final MEL</Link>

  {/* NEW: Document Generator link */}
  <Link to="/documents">Document Generator</Link>
</nav>
```

**Or if using a more complex navigation structure:**

```tsx
const navItems = [
  { path: '/', label: 'Dashboard', icon: '🏠' },
  { path: '/initial-mel', label: 'Initial MEL', icon: '📊' },
  { path: '/final-mel', label: 'Final MEL', icon: '📋' },
  { path: '/documents', label: 'Documents', icon: '📝' }, // NEW
];
```

### Step 4: Verify Environment Variables

Ensure your `.env` file has the correct API URL:

```env
# .env (development)
VITE_API_URL=http://localhost:8000

# .env.production
VITE_API_URL=https://api.businessbydrew.cloud
```

### Step 5: Create Type Definitions Directory (if needed)

If `src/types/` doesn't exist, create it:

```bash
mkdir -p src/types
```

### Step 6: Create API Directory (if needed)

If `src/api/` doesn't exist, create it:

```bash
mkdir -p src/api
```

---

## 📁 File Structure

After integration, your frontend should have:

```
pace-frontend-modern/
├── src/
│   ├── api/
│   │   └── documentApi.ts          # NEW
│   ├── components/
│   │   ├── DocumentTypeSelector.tsx  # NEW
│   │   ├── MetadataForm.tsx         # NEW
│   │   ├── PromptInput.tsx          # NEW
│   │   └── DocumentPreview.tsx      # NEW
│   ├── pages/
│   │   ├── Dashboard.tsx            # Existing
│   │   ├── InitialMEL.tsx           # Existing
│   │   ├── FinalMEL.tsx             # Existing
│   │   └── DocumentGenerator.tsx    # NEW
│   ├── types/
│   │   └── document.types.ts        # NEW
│   └── App.tsx                      # MODIFIED (add route)
```

---

## 🎨 Styling Notes

All components use Tailwind CSS classes compatible with your existing setup. The color scheme uses:

- **Primary**: Indigo (matching your existing PACE theme)
- **Success**: Green
- **Warning**: Yellow
- **Error**: Red

If you need to customize colors, update the Tailwind classes in each component.

---

## 🔌 API Integration

The `documentApi.ts` file handles all backend communication:

- `getTemplates()` - Fetch available document types
- `generateFromPrompt()` - Parse natural language prompt
- `generatePDF()` - Create final PDF
- `downloadPDF()` - Convenience method to download PDF

All API calls use Axios and the `VITE_API_URL` environment variable.

---

## 🧪 Testing

### 1. Start the Backend

```bash
cd pace-backend-clean
docker-compose up -d
# OR
uvicorn main:app --reload
```

### 2. Start the Frontend

```bash
cd pace-frontend-modern
npm run dev
```

### 3. Test Document Generation

1. Navigate to `http://localhost:5173/documents`
2. Select a document type (e.g., MFR)
3. Fill in your information
4. Enter a prompt or click an example
5. Review extracted fields
6. Generate PDF

---

## 🐛 Troubleshooting

### Issue: "Network Error" when generating documents

**Solution:** Check that backend is running and CORS is configured:
```bash
# In backend constants.py, ensure:
cors_origins = [
    "http://localhost:5173",  # Add your frontend URL
    # ...
]
```

### Issue: "Module not found" errors

**Solution:** Ensure all files are copied to correct directories and imports match your structure.

### Issue: Types not recognized

**Solution:** Restart TypeScript server in VSCode:
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
- Type "TypeScript: Restart TS Server"

### Issue: Styling looks broken

**Solution:** Ensure Tailwind CSS is configured and running:
```bash
# Verify tailwind.config.js includes new paths:
content: [
  "./src/**/*.{js,jsx,ts,tsx}",
],
```

---

## ✨ Features Implemented

- ✅ 6 document types (MFR, Memo, Appointment, LOC, LOA, LOR)
- ✅ Natural language prompt parsing
- ✅ Interactive document preview with editing
- ✅ Real-time validation warnings
- ✅ PDF generation and download
- ✅ Responsive design (mobile-friendly)
- ✅ Example prompts for each document type
- ✅ Array field management (add/remove paragraphs, duties, violations)

---

## 🔮 Future Enhancements

- [ ] Save draft documents to localStorage
- [ ] Document history/templates
- [ ] Bulk document generation
- [ ] Export to Word (.docx)
- [ ] Enhanced AI prompt assistance
- [ ] Document sharing/collaboration

---

## 📞 Support

If you encounter issues:

1. Check backend logs: `docker-compose logs backend`
2. Check browser console for frontend errors
3. Verify API connectivity: `curl http://localhost:8000/api/documents/templates`
4. Review CORS configuration in backend `constants.py`

---

## 🎉 You're Done!

Navigate to `/documents` in your frontend and start generating Air Force administrative documents!
