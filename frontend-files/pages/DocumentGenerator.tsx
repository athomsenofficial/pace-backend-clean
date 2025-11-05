import React, { useState } from 'react';
import { DocumentTypeSelector } from '../components/document-generator/DocumentTypeSelector';
import { MetadataForm } from '../components/document-generator/MetadataForm';
import { PromptInput } from '../components/document-generator/PromptInput';
import { DocumentPreview } from '../components/document-generator/DocumentPreview';
import { documentApi } from '../api/documentApi';
import type {
  DocumentType,
  DocumentMetadata,
  DocumentResponse,
} from '../types/document.types';

type Step = 'select-type' | 'metadata' | 'prompt' | 'preview';

export const DocumentGenerator: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<Step>('select-type');
  const [documentType, setDocumentType] = useState<DocumentType | null>(null);
  const [metadata, setMetadata] = useState<DocumentMetadata>({
    office_symbol: '',
    author_name: '',
    author_rank: '',
    author_title: '',
    organization: '',
    phone: '',
    email: '',
  });
  const [prompt, setPrompt] = useState<string>('');
  const [generatedDocument, setGeneratedDocument] = useState<DocumentResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectType = (type: DocumentType) => {
    setDocumentType(type);
    setCurrentStep('metadata');
  };

  const handleMetadataNext = () => {
    setCurrentStep('prompt');
  };

  const handleGenerateDocument = async () => {
    if (!documentType) return;

    setIsGenerating(true);
    setError(null);

    try {
      const response = await documentApi.generateFromPrompt({
        document_type: documentType,
        metadata,
        use_prompt: true,
        prompt,
      });

      setGeneratedDocument(response);
      setCurrentStep('preview');
    } catch (err: any) {
      console.error('Error generating document:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to generate document. Please check your input and try again.'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUpdateDocument = (updated: DocumentResponse) => {
    setGeneratedDocument(updated);
  };

  const handleGeneratePDF = async () => {
    if (!generatedDocument) return;

    setIsGeneratingPDF(true);
    setError(null);

    try {
      const filename = `${documentType}_${generatedDocument.document_id}.pdf`;
      await documentApi.downloadPDF(
        generatedDocument.document_id,
        {
          include_cui_marking: true,
        },
        filename
      );
    } catch (err: any) {
      console.error('Error generating PDF:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to generate PDF. Please try again.'
      );
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const handleReset = () => {
    setCurrentStep('select-type');
    setDocumentType(null);
    setMetadata({
      office_symbol: '',
      author_name: '',
      author_rank: '',
      author_title: '',
      organization: '',
      phone: '',
      email: '',
    });
    setPrompt('');
    setGeneratedDocument(null);
    setError(null);
  };

  const renderProgressBar = () => {
    const steps = [
      { key: 'select-type', label: 'Type' },
      { key: 'metadata', label: 'Author' },
      { key: 'prompt', label: 'Content' },
      { key: 'preview', label: 'Preview' },
    ];

    const currentIndex = steps.findIndex((s) => s.key === currentStep);

    return (
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <React.Fragment key={step.key}>
              <div className="flex flex-col items-center">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center font-semibold
                    ${
                      index <= currentIndex
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }
                  `}
                >
                  {index + 1}
                </div>
                <span
                  className={`
                    mt-2 text-sm font-medium
                    ${index <= currentIndex ? 'text-indigo-600' : 'text-gray-500'}
                  `}
                >
                  {step.label}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`
                    flex-1 h-1 mx-4
                    ${index < currentIndex ? 'bg-indigo-600' : 'bg-gray-200'}
                  `}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            Air Force Document Generator
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Generate professional Air Force documents using natural language
          </p>
        </div>

        {/* Progress Bar */}
        {renderProgressBar()}

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="ml-auto flex-shrink-0 text-red-500 hover:text-red-700"
              >
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {currentStep === 'select-type' && (
            <DocumentTypeSelector
              onSelect={handleSelectType}
              selectedType={documentType || undefined}
            />
          )}

          {currentStep === 'metadata' && (
            <MetadataForm
              metadata={metadata}
              onChange={setMetadata}
              onNext={handleMetadataNext}
              onBack={() => setCurrentStep('select-type')}
            />
          )}

          {currentStep === 'prompt' && documentType && (
            <PromptInput
              documentType={documentType}
              prompt={prompt}
              onChange={setPrompt}
              onGenerate={handleGenerateDocument}
              onBack={() => setCurrentStep('metadata')}
              isGenerating={isGenerating}
            />
          )}

          {currentStep === 'preview' && generatedDocument && (
            <DocumentPreview
              document={generatedDocument}
              onUpdate={handleUpdateDocument}
              onGeneratePDF={handleGeneratePDF}
              onBack={() => setCurrentStep('prompt')}
              isGeneratingPDF={isGeneratingPDF}
            />
          )}
        </div>

        {/* Reset Button */}
        {currentStep !== 'select-type' && (
          <div className="mt-6 text-center">
            <button
              onClick={handleReset}
              className="text-sm text-gray-600 hover:text-gray-900 underline"
            >
              Start Over
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
