/**
 * Prompt Input Component
 * Copy this file to: src/components/PromptInput.tsx
 */

import React from 'react';
import type { DocumentTemplate } from '../types/document.types';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  template?: DocumentTemplate;
  disabled?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  value,
  onChange,
  template,
  disabled = false,
}) => {
  const handleExampleClick = (example: string) => {
    onChange(example);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Describe what you need in plain English
        </label>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          rows={6}
          placeholder="Example: Create an MFR documenting a phone call with MSgt Smith on 15 Jan 2025 about TDY voucher processing delays. We discussed the need to submit vouchers within 5 days of return from TDY per AFI 65-103."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <p className="mt-1 text-xs text-gray-500">
          The AI will extract key information from your prompt. Be as specific as possible.
        </p>
      </div>

      {/* Example Prompts */}
      {template && template.example_prompts.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">
            Quick Examples (click to use):
          </p>
          <div className="space-y-2">
            {template.example_prompts.map((example, idx) => (
              <button
                key={idx}
                onClick={() => handleExampleClick(example)}
                disabled={disabled}
                className="w-full text-left px-3 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md text-sm text-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
        <p className="text-sm font-medium text-blue-900 mb-1">💡 Tips for better results:</p>
        <ul className="text-xs text-blue-800 space-y-1 list-disc list-inside">
          <li>Include specific dates (e.g., "15 Jan 2025")</li>
          <li>Mention ranks and names when relevant</li>
          <li>Reference AFI citations if applicable</li>
          <li>Describe the situation clearly and concisely</li>
        </ul>
      </div>
    </div>
  );
};
