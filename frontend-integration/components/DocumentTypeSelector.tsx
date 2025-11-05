/**
 * Document Type Selector Component
 * Copy this file to: src/components/DocumentTypeSelector.tsx
 */

import React from 'react';
import type { DocumentType, DocumentTemplate } from '../types/document.types';

interface DocumentTypeSelectorProps {
  templates: DocumentTemplate[];
  selectedType: DocumentType;
  onSelect: (type: DocumentType) => void;
}

const documentIcons: Record<DocumentType, string> = {
  mfr: '📝',
  memo: '📄',
  appointment: '📋',
  loc: '⚠️',
  loa: '🔶',
  lor: '🔴',
};

export const DocumentTypeSelector: React.FC<DocumentTypeSelectorProps> = ({
  templates,
  selectedType,
  onSelect,
}) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {templates.map((template) => (
        <button
          key={template.type}
          onClick={() => onSelect(template.type)}
          className={`
            p-4 rounded-lg border-2 transition-all text-left
            ${
              selectedType === template.type
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 bg-white hover:border-indigo-300'
            }
          `}
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{documentIcons[template.type]}</span>
            <h3 className="font-semibold text-gray-900">{template.name}</h3>
          </div>
          <p className="text-sm text-gray-600">{template.description}</p>
        </button>
      ))}
    </div>
  );
};
