#!/bin/bash

# Script to copy frontend files to pace-frontend-modern
# Run this from the pace-backend-clean directory

echo "🚀 Copying Document Generator files to pace-frontend-modern..."

# Check if pace-frontend-modern exists
if [ ! -d "../pace-frontend-modern" ]; then
    echo "❌ Error: pace-frontend-modern directory not found at ../pace-frontend-modern"
    echo "Please run this script from the pace-backend-clean directory"
    exit 1
fi

# Create directories if they don't exist
mkdir -p ../pace-frontend-modern/src/types
mkdir -p ../pace-frontend-modern/src/api
mkdir -p ../pace-frontend-modern/src/components/document-generator
mkdir -p ../pace-frontend-modern/src/pages

# Copy files
echo "📁 Copying types..."
cp frontend-files/types/document.types.ts ../pace-frontend-modern/src/types/

echo "📁 Copying API client..."
cp frontend-files/api/documentApi.ts ../pace-frontend-modern/src/api/

echo "📁 Copying components..."
cp frontend-files/components/document-generator/DocumentTypeSelector.tsx ../pace-frontend-modern/src/components/document-generator/
cp frontend-files/components/document-generator/MetadataForm.tsx ../pace-frontend-modern/src/components/document-generator/
cp frontend-files/components/document-generator/PromptInput.tsx ../pace-frontend-modern/src/components/document-generator/
cp frontend-files/components/document-generator/DocumentPreview.tsx ../pace-frontend-modern/src/components/document-generator/
cp frontend-files/components/document-generator/index.ts ../pace-frontend-modern/src/components/document-generator/

echo "📁 Copying main page..."
cp frontend-files/pages/DocumentGenerator.tsx ../pace-frontend-modern/src/pages/

echo "✅ All files copied successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Add route to src/App.tsx:"
echo "   import { DocumentGenerator } from './pages/DocumentGenerator';"
echo "   <Route path=\"/document-generator\" element={<DocumentGenerator />} />"
echo ""
echo "2. Add navigation link to your nav component:"
echo "   <Link to=\"/document-generator\">Document Generator</Link>"
echo ""
echo "3. Ensure .env has VITE_API_URL set:"
echo "   VITE_API_URL=http://localhost:8000"
echo ""
echo "4. Test the feature:"
echo "   cd ../pace-frontend-modern && npm run dev"
echo ""
echo "📚 See INTEGRATION_GUIDE.md for detailed instructions"
