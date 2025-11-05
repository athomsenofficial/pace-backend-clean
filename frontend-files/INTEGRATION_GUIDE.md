# Frontend Integration Guide - Document Generator

This guide will help you integrate the Air Force Document Generator into your pace-frontend-modern React application.

## Prerequisites

- React 19
- TypeScript
- Axios
- Tailwind CSS
- React Router (if using routing)

## Installation Steps

### 1. Copy Files to Your Frontend

Copy the following directories from `pace-backend-clean/frontend-files/` to your `pace-frontend-modern/src/` directory:

```bash
# From the pace-backend-clean directory:
cp -r frontend-files/types ../pace-frontend-modern/src/
cp -r frontend-files/api ../pace-frontend-modern/src/
cp -r frontend-files/components/document-generator ../pace-frontend-modern/src/components/
cp -r frontend-files/pages/DocumentGenerator.tsx ../pace-frontend-modern/src/pages/
```

### 2. Install Required Dependencies

Make sure you have the required npm packages:

```bash
cd ../pace-frontend-modern
npm install axios
```

### 3. Configure Environment Variables

Add the backend API URL to your `.env` file:

```bash
# .env
VITE_API_URL=http://localhost:8000
# Or for production:
# VITE_API_URL=https://api.businessbydrew.cloud
```

### 4. Add Route to App.tsx

Update your `src/App.tsx` to include the document generator route:

```typescript
import { DocumentGenerator } from './pages/DocumentGenerator';

// In your routes:
<Route path="/document-generator" element={<DocumentGenerator />} />
```

### 5. Add Navigation Link (Optional)

Add a navigation link to your header/sidebar:

```tsx
<Link to="/document-generator">Document Generator</Link>
```

## File Structure

After integration, your file structure should look like:

```
pace-frontend-modern/
├── src/
│   ├── api/
│   │   └── documentApi.ts          # API client for document endpoints
│   ├── components/
│   │   └── document-generator/
│   │       ├── DocumentTypeSelector.tsx
│   │       ├── MetadataForm.tsx
│   │       ├── PromptInput.tsx
│   │       └── DocumentPreview.tsx
│   ├── pages/
│   │   └── DocumentGenerator.tsx   # Main page component
│   ├── types/
│   │   └── document.types.ts       # TypeScript type definitions
│   └── App.tsx
```

## Complete App.tsx Example

```typescript
import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { DocumentGenerator } from './pages/DocumentGenerator';
import { InitialMEL } from './pages/InitialMEL';
import { FinalMEL } from './pages/FinalMEL';
import { Dashboard } from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex space-x-8">
                <Link
                  to="/"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                >
                  Dashboard
                </Link>
                <Link
                  to="/initial-mel"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                >
                  Initial MEL
                </Link>
                <Link
                  to="/final-mel"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                >
                  Final MEL
                </Link>
                <Link
                  to="/document-generator"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                >
                  Document Generator
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/initial-mel" element={<InitialMEL />} />
          <Route path="/final-mel" element={<FinalMEL />} />
          <Route path="/document-generator" element={<DocumentGenerator />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

## API Endpoints Used

The document generator uses these backend endpoints:

- `GET /api/documents/templates` - Get available document templates
- `POST /api/documents/generate` - Generate document from prompt
- `POST /api/documents/{document_id}/generate-pdf` - Generate PDF

Make sure your backend is running and accessible at the URL specified in `VITE_API_URL`.

## Testing

1. Start your backend:
   ```bash
   cd pace-backend-clean
   docker-compose up -d
   ```

2. Start your frontend:
   ```bash
   cd pace-frontend-modern
   npm run dev
   ```

3. Navigate to: `http://localhost:5173/document-generator`

## Customization

### Styling

The components use Tailwind CSS classes. You can customize the styling by:
- Modifying the Tailwind classes in each component
- Adding custom CSS classes
- Updating your `tailwind.config.js`

### Colors

The components use these primary colors:
- Primary (Indigo): `indigo-600`, `indigo-700`
- Success (Green): `green-600`, `green-700`
- Warning (Yellow): `yellow-50`, `yellow-200`
- Error (Red): `red-50`, `red-200`

Adjust these in the component files to match your design system.

## Troubleshooting

### API Connection Issues

**Problem**: "Failed to generate document" error

**Solutions**:
1. Check that `VITE_API_URL` is set correctly in `.env`
2. Verify backend is running: `curl http://localhost:8000/api/health`
3. Check browser console for CORS errors
4. Ensure backend CORS is configured to allow your frontend origin (check `pace-backend-clean/constants.py`)

### Type Errors

**Problem**: TypeScript errors about missing types

**Solutions**:
1. Ensure `document.types.ts` is in the correct location
2. Restart TypeScript server in your IDE
3. Run `npm run build` to check for type errors

### Styling Issues

**Problem**: Components look unstyled or broken

**Solutions**:
1. Ensure Tailwind CSS is configured and running
2. Check that your `tailwind.config.js` includes the component paths
3. Verify Tailwind directives are in your main CSS file:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

## Additional Features

### Logo Upload

The backend supports custom unit logos. To enable logo upload in the frontend:

1. Add a file input in the MetadataForm or DocumentPreview
2. Upload logo to `/api/documents/upload-logo` endpoint (you may need to add this)
3. Pass `logo_filename` in the `GeneratePDFRequest`

### Document Templates

To show available templates and their requirements:

```typescript
import { documentApi } from '../api/documentApi';

const [templates, setTemplates] = useState(null);

useEffect(() => {
  documentApi.getTemplates().then(setTemplates);
}, []);
```

## Support

For issues or questions:
- Check backend logs: `docker-compose logs backend`
- Review API documentation: `pace-backend-clean/API_REFERENCE.md`
- Check CLAUDE.md for system architecture details
