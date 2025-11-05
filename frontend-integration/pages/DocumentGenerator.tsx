/**
 * Main Document Generator Page
 * Copy this file to: src/pages/DocumentGenerator.tsx
 */

import React, { useState, useEffect } from 'react';
import { documentApi } from '../api/documentApi';
import type {
  DocumentType,
  DocumentTemplate,
  DocumentMetadata,
  DocumentContent,
} from '../types/document.types';
import { DocumentTypeSelector } from '../components/DocumentTypeSelector';
import { PromptInput } from '../components/PromptInput';
import { MetadataForm } from '../components/MetadataForm';
import { DocumentPreview } from '../components/DocumentPreview';

export const DocumentGenerator: React.FC = () => {
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [selectedType, setSelectedType] = useState<DocumentType>('mfr');
  const [prompt, setPrompt] = useState('');
  const [metadata, setMetadata] = useState<DocumentMetadata>({
    office_symbol: '',
    author_name: '',
    author_rank: '',
    author_title: '',
    organization: '',
  });
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [extractedFields, setExtractedFields] = useState<any>(null);
  const [validationWarnings, setValidationWarnings] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load templates on mount
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const data = await documentApi.getTemplates();
        setTemplates(data.templates);
      } catch (err) {
        console.error('Failed to load templates:', err);
        setError('Failed to load document templates');
      }
    };
    loadTemplates();
  }, []);

  const handleGenerateFromPrompt = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    // Validate metadata
    const requiredFields = ['office_symbol', 'author_name', 'author_rank', 'author_title', 'organization'];
    const missingFields = requiredFields.filter(field => !metadata[field as keyof DocumentMetadata]);

    if (missingFields.length > 0) {
      setError(`Please fill in: ${missingFields.join(', ')}`);
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await documentApi.generateFromPrompt({
        document_type: selectedType,
        prompt,
        metadata,
      });

      setDocumentId(response.document_id);
      setExtractedFields(response.extracted_fields);
      setValidationWarnings(response.validation_warnings);
    } catch (err: any) {
      console.error('Generation failed:', err);
      setError(err.response?.data?.error || 'Failed to generate document');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGeneratePDF = async (content: DocumentContent) => {
    if (!documentId) return;

    setIsGenerating(true);
    setError(null);

    try {
      const filename = `${selectedType}_${new Date().toISOString().split('T')[0]}.pdf`;
      await documentApi.downloadPDF(
        documentId,
        { metadata, content },
        filename
      );
    } catch (err: any) {
      console.error('PDF generation failed:', err);
      setError(err.response?.data?.error || 'Failed to generate PDF');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleReset = () => {
    setPrompt('');
    setDocumentId(null);
    setExtractedFields(null);
    setValidationWarnings([]);
    setError(null);
  };

  const selectedTemplate = templates.find(t => t.type === selectedType);

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Air Force Document Generator
        </h1>
        <p className="text-gray-600">
          Generate AF administrative documents using natural language prompts
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Input */}
        <div className="lg:col-span-2 space-y-6">
          {/* Step 1: Select Document Type */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Step 1: Select Document Type
            </h2>
            <DocumentTypeSelector
              templates={templates}
              selectedType={selectedType}
              onSelect={setSelectedType}
            />
          </div>

          {/* Step 2: Author Information */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Step 2: Author Information
            </h2>
            <MetadataForm
              metadata={metadata}
              onChange={setMetadata}
            />
          </div>

          {/* Step 3: Prompt Input */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Step 3: Describe Your Document
            </h2>
            <PromptInput
              value={prompt}
              onChange={setPrompt}
              template={selectedTemplate}
              disabled={isGenerating}
            />
            <div className="mt-4 flex gap-3">
              <button
                onClick={handleGenerateFromPrompt}
                disabled={isGenerating || !prompt.trim()}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {isGenerating ? 'Processing...' : 'Generate Document'}
              </button>
              {documentId && (
                <button
                  onClick={handleReset}
                  className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Start Over
                </button>
              )}
            </div>
          </div>

          {/* Validation Warnings */}
          {validationWarnings.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-800 mb-2">
                ⚠️ Validation Warnings
              </h3>
              <ul className="list-disc list-inside text-yellow-700 space-y-1">
                {validationWarnings.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Right Column: Preview & Info */}
        <div className="space-y-6">
          {/* Template Info */}
          {selectedTemplate && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">
                {selectedTemplate.name}
              </h3>
              <p className="text-blue-800 text-sm mb-3">
                {selectedTemplate.description}
              </p>
              <div className="text-xs text-blue-700">
                <p className="font-medium mb-1">Example prompts:</p>
                <ul className="space-y-1">
                  {selectedTemplate.example_prompts.map((example, idx) => (
                    <li key={idx} className="italic">
                      "{example}"
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Document Preview */}
          {extractedFields && (
            <DocumentPreview
              documentType={selectedType}
              extractedFields={extractedFields}
              metadata={metadata}
              onGeneratePDF={handleGeneratePDF}
              isGenerating={isGenerating}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentGenerator;
