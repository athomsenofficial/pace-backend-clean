import React from 'react';
import type { DocumentType } from '../../types/document.types';

interface DocumentTypeOption {
  type: DocumentType;
  name: string;
  description: string;
  icon: string;
}

const documentTypes: DocumentTypeOption[] = [
  {
    type: 'mfr',
    name: 'Memorandum For Record (MFR)',
    description: 'Document meetings, conversations, or events for official record',
    icon: '📝',
  },
  {
    type: 'memo',
    name: 'Memorandum',
    description: 'Formal communication for policy, directives, or information',
    icon: '📄',
  },
  {
    type: 'appointment',
    name: 'Appointment Letter',
    description: 'Officially appoint personnel to positions or duties',
    icon: '📋',
  },
  {
    type: 'loc',
    name: 'Letter of Counseling (LOC)',
    description: 'Document minor performance or conduct issues',
    icon: '⚠️',
  },
  {
    type: 'loa',
    name: 'Letter of Admonishment (LOA)',
    description: 'Document moderate performance or conduct violations',
    icon: '🔶',
  },
  {
    type: 'lor',
    name: 'Letter of Reprimand (LOR)',
    description: 'Document serious performance or conduct violations',
    icon: '🔴',
  },
];

interface Props {
  onSelect: (type: DocumentType) => void;
  selectedType?: DocumentType;
}

export const DocumentTypeSelector: React.FC<Props> = ({ onSelect, selectedType }) => {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Select Document Type</h2>
        <p className="mt-1 text-sm text-gray-600">
          Choose the type of Air Force document you want to generate
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {documentTypes.map((docType) => (
          <button
            key={docType.type}
            onClick={() => onSelect(docType.type)}
            className={`
              relative rounded-lg border-2 p-6 text-left transition-all hover:shadow-lg
              ${
                selectedType === docType.type
                  ? 'border-indigo-600 bg-indigo-50 ring-2 ring-indigo-600'
                  : 'border-gray-300 bg-white hover:border-indigo-400'
              }
            `}
          >
            <div className="flex items-start space-x-3">
              <span className="text-4xl">{docType.icon}</span>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900">
                  {docType.name}
                </h3>
                <p className="mt-1 text-sm text-gray-600">{docType.description}</p>
              </div>
            </div>
            {selectedType === docType.type && (
              <div className="absolute top-4 right-4">
                <div className="h-6 w-6 rounded-full bg-indigo-600 flex items-center justify-center">
                  <svg
                    className="h-4 w-4 text-white"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};
