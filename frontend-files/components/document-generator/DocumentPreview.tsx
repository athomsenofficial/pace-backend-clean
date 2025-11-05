import React, { useState } from 'react';
import type {
  DocumentResponse,
  MFRContent,
  MemoContent,
  AppointmentContent,
  AdministrativeActionContent,
} from '../../types/document.types';

interface Props {
  document: DocumentResponse;
  onUpdate: (document: DocumentResponse) => void;
  onGeneratePDF: () => void;
  onBack: () => void;
  isGeneratingPDF: boolean;
}

export const DocumentPreview: React.FC<Props> = ({
  document,
  onUpdate,
  onGeneratePDF,
  onBack,
  isGeneratingPDF,
}) => {
  const [editMode, setEditMode] = useState<string | null>(null);

  const updateContent = (updates: Partial<typeof document.content>) => {
    onUpdate({
      ...document,
      content: { ...document.content, ...updates },
    });
  };

  const addArrayItem = (field: string) => {
    const currentArray = (document.content as any)[field] || [];
    updateContent({ [field]: [...currentArray, ''] });
  };

  const updateArrayItem = (field: string, index: number, value: string) => {
    const currentArray = [...((document.content as any)[field] || [])];
    currentArray[index] = value;
    updateContent({ [field]: currentArray });
  };

  const removeArrayItem = (field: string, index: number) => {
    const currentArray = [...((document.content as any)[field] || [])];
    currentArray.splice(index, 1);
    updateContent({ [field]: currentArray });
  };

  const renderMFRContent = (content: MFRContent) => (
    <div className="space-y-4">
      {/* Subject */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
        <input
          type="text"
          value={content.subject}
          onChange={(e) => updateContent({ subject: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Location (Optional)</label>
        <input
          type="text"
          value={content.location || ''}
          onChange={(e) => updateContent({ location: e.target.value })}
          placeholder="e.g., Building 123, Conference Room A"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Participants */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Participants (Optional)</label>
        {(content.participants || []).map((participant, index) => (
          <div key={index} className="flex items-center space-x-2 mb-2">
            <input
              type="text"
              value={participant}
              onChange={(e) => updateArrayItem('participants', index, e.target.value)}
              placeholder="Name and rank"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={() => removeArrayItem('participants', index)}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          onClick={() => addArrayItem('participants')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Add Participant
        </button>
      </div>

      {/* Body Paragraphs */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Body Paragraphs</label>
        {content.body_paragraphs.map((paragraph, index) => (
          <div key={index} className="mb-3">
            <div className="flex items-start space-x-2">
              <div className="flex-1">
                <textarea
                  value={paragraph}
                  onChange={(e) => updateArrayItem('body_paragraphs', index, e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <button
                onClick={() => removeArrayItem('body_paragraphs', index)}
                className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
        <button
          onClick={() => addArrayItem('body_paragraphs')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Add Paragraph
        </button>
      </div>
    </div>
  );

  const renderMemoContent = (content: MemoContent) => (
    <div className="space-y-4">
      {/* Recipient */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Recipient Name</label>
          <input
            type="text"
            value={content.recipient_name}
            onChange={(e) => updateContent({ recipient_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Recipient Office</label>
          <input
            type="text"
            value={content.recipient_office}
            onChange={(e) => updateContent({ recipient_office: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Subject */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
        <input
          type="text"
          value={content.subject}
          onChange={(e) => updateContent({ subject: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Body Paragraphs */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Body Paragraphs</label>
        {content.body_paragraphs.map((paragraph, index) => (
          <div key={index} className="mb-3">
            <div className="flex items-start space-x-2">
              <textarea
                value={paragraph}
                onChange={(e) => updateArrayItem('body_paragraphs', index, e.target.value)}
                rows={3}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={() => removeArrayItem('body_paragraphs', index)}
                className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
        <button
          onClick={() => addArrayItem('body_paragraphs')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Add Paragraph
        </button>
      </div>
    </div>
  );

  const renderAppointmentContent = (content: AppointmentContent) => (
    <div className="space-y-4">
      {/* Appointee Info */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Appointee Name</label>
          <input
            type="text"
            value={content.appointee_name}
            onChange={(e) => updateContent({ appointee_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Appointee Rank</label>
          <input
            type="text"
            value={content.appointee_rank}
            onChange={(e) => updateContent({ appointee_rank: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Position */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Position Title</label>
        <input
          type="text"
          value={content.position_title}
          onChange={(e) => updateContent({ position_title: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Dates */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Effective Date</label>
          <input
            type="date"
            value={content.effective_date}
            onChange={(e) => updateContent({ effective_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Termination Date (Optional)</label>
          <input
            type="date"
            value={content.termination_date || ''}
            onChange={(e) => updateContent({ termination_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Authority */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Authority Citation</label>
        <input
          type="text"
          value={content.authority_citation}
          onChange={(e) => updateContent({ authority_citation: e.target.value })}
          placeholder="e.g., AFI 36-2905"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Duties */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Duties</label>
        {content.duties.map((duty, index) => (
          <div key={index} className="flex items-start space-x-2 mb-2">
            <input
              type="text"
              value={duty}
              onChange={(e) => updateArrayItem('duties', index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={() => removeArrayItem('duties', index)}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          onClick={() => addArrayItem('duties')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Add Duty
        </button>
      </div>
    </div>
  );

  const renderAdministrativeActionContent = (content: AdministrativeActionContent) => (
    <div className="space-y-4">
      {/* Member Info */}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Member Name</label>
          <input
            type="text"
            value={content.member_name}
            onChange={(e) => updateContent({ member_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Rank</label>
          <input
            type="text"
            value={content.member_rank}
            onChange={(e) => updateContent({ member_rank: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
          <input
            type="text"
            value={content.member_unit}
            onChange={(e) => updateContent({ member_unit: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Incident Date */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Incident Date</label>
        <input
          type="date"
          value={content.incident_date}
          onChange={(e) => updateContent({ incident_date: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Incident Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Incident Description</label>
        <textarea
          value={content.incident_description}
          onChange={(e) => updateContent({ incident_description: e.target.value })}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Violations */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Violations</label>
        {content.violations.map((violation, index) => (
          <div key={index} className="flex items-start space-x-2 mb-2">
            <input
              type="text"
              value={violation}
              onChange={(e) => updateArrayItem('violations', index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={() => removeArrayItem('violations', index)}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          onClick={() => addArrayItem('violations')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Add Violation
        </button>
      </div>

      {/* Corrective Actions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Corrective Actions</label>
        {content.corrective_actions.map((action, index) => (
          <div key={index} className="flex items-start space-x-2 mb-2">
            <input
              type="text"
              value={action}
              onChange={(e) => updateArrayItem('corrective_actions', index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={() => removeArrayItem('corrective_actions', index)}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          onClick={() => addArrayItem('corrective_actions')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Add Action
        </button>
      </div>

      {/* Authority */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Authority Citation</label>
        <input
          type="text"
          value={content.authority_citation}
          onChange={(e) => updateContent({ authority_citation: e.target.value })}
          placeholder="e.g., AFI 36-2907, Article 92 UCMJ"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>
  );

  const renderContent = () => {
    switch (document.document_type) {
      case 'mfr':
        return renderMFRContent(document.content as MFRContent);
      case 'memo':
        return renderMemoContent(document.content as MemoContent);
      case 'appointment':
        return renderAppointmentContent(document.content as AppointmentContent);
      case 'loc':
      case 'loa':
      case 'lor':
        return renderAdministrativeActionContent(document.content as AdministrativeActionContent);
      default:
        return <div>Unknown document type</div>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Review & Edit Document</h2>
        <p className="mt-1 text-sm text-gray-600">
          Review the generated content and make any necessary edits before generating the PDF
        </p>
      </div>

      {/* Validation Warnings */}
      {document.validation.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-yellow-900 mb-2">⚠️ Warnings:</h3>
          <ul className="text-sm text-yellow-800 space-y-1">
            {document.validation.warnings.map((warning, index) => (
              <li key={index}>• {warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Validation Errors */}
      {document.validation.errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-red-900 mb-2">❌ Errors:</h3>
          <ul className="text-sm text-red-800 space-y-1">
            {document.validation.errors.map((error, index) => (
              <li key={index}>• {error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Content Editor */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {renderContent()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={onBack}
          disabled={isGeneratingPDF}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Back
        </button>
        <button
          onClick={onGeneratePDF}
          disabled={isGeneratingPDF || document.validation.errors.length > 0}
          className={`
            px-6 py-2 rounded-md font-medium flex items-center space-x-2
            ${
              isGeneratingPDF || document.validation.errors.length > 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }
          `}
        >
          {isGeneratingPDF && (
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          )}
          <span>📄</span>
          <span>{isGeneratingPDF ? 'Generating PDF...' : 'Generate PDF'}</span>
        </button>
      </div>
    </div>
  );
};
