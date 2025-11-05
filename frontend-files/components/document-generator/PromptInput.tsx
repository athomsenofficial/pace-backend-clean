import React from 'react';
import type { DocumentType } from '../../types/document.types';

interface Props {
  documentType: DocumentType;
  prompt: string;
  onChange: (prompt: string) => void;
  onGenerate: () => void;
  onBack: () => void;
  isGenerating: boolean;
}

const EXAMPLE_PROMPTS: Record<DocumentType, string[]> = {
  mfr: [
    'MFR for meeting with TSgt Johnson on 15 March 2024 regarding EPR feedback. Discussed performance strengths and areas for improvement. Meeting held in building 123, conference room A.',
    'Document conversation with SSgt Smith about deployment timeline. Meeting occurred 1 Apr 2024. Covered pre-deployment requirements, family care plan, and expected departure date of 15 May 2024.',
  ],
  memo: [
    'Memorandum to 51 FSS/All from 51 FSS/CC regarding new uniform policy effective 1 June 2024. All personnel must comply with AFI 36-2903 updates. Includes guidance on OCPs and name tapes.',
    'Memo for record updating duty hours policy. From Commander to all staff. Effective immediately, duty hours are 0730-1630. Exception requests must go through flight chiefs.',
  ],
  appointment: [
    'Appoint SSgt Jane Doe as Unit Fitness Program Manager effective 1 April 2024. Duties include scheduling PT tests, maintaining fitness records, and coordinating with base FAC. Authority: AFI 36-2905.',
    'Appointment letter for TSgt John Smith as Additional Duty First Sergeant starting 15 March 2024 through 15 March 2025. Responsibilities include enlisted welfare, morale programs, and commander support per AFI 36-2113.',
  ],
  loc: [
    'LOC for A1C Brown for being late to work on 10 March 2024. Arrived at 0815 instead of 0730. First incident, counseled on importance of punctuality and military discipline.',
    'Letter of counseling for SrA Johnson regarding substandard PT performance. Failed mock PT test on 5 April 2024 with score of 65. Discussed importance of fitness and provided resources.',
  ],
  loa: [
    'LOA for SSgt Martinez for failure to follow Tech Order procedures on 12 March 2024. Violated TO 00-20-1 step 4.3. Counseled on safety implications and proper procedures. Second offense.',
    'Letter of admonishment for TSgt Williams regarding unprofessional conduct during staff meeting on 20 March 2024. Used inappropriate language. Discussed professional military bearing per AFI 36-2618.',
  ],
  lor: [
    'LOR for SSgt Adams for dereliction of duty on 8 March 2024. Failed to perform assigned guard duty shift, leaving post unmanned for 2 hours. Violated Article 92 UCMJ. Third incident this year.',
    'Letter of reprimand for TSgt Lee for DUI arrest on 15 March 2024. Arrested by base police with BAC of 0.15. Violated AFI 36-2110 and reflects poorly on Air Force standards. Commander directed.',
  ],
};

const TIPS: Record<DocumentType, string[]> = {
  mfr: [
    'Include the date of the event or meeting',
    'List participants if applicable',
    'Specify location if relevant',
    'Describe what was discussed or what happened',
  ],
  memo: [
    'Specify who the memo is to (recipient office)',
    'Include the subject line',
    'State the purpose and any action required',
    'Mention effective dates if applicable',
  ],
  appointment: [
    'Name and rank of the person being appointed',
    'Position or duty title',
    'Effective date and termination date',
    'List key duties and responsibilities',
    'Cite the governing AFI or directive',
  ],
  loc: [
    'Name and rank of the member',
    'Specific date and nature of the incident',
    'What standard or rule was violated',
    'Previous counseling (if applicable)',
  ],
  loa: [
    'Name and rank of the member',
    'Date and details of the violation',
    'Which regulation or instruction was violated',
    'Impact of the behavior',
  ],
  lor: [
    'Name and rank of the member',
    'Serious nature of the offense',
    'Date and specific details',
    'UCMJ article or AFI violated',
    'Previous disciplinary actions',
  ],
};

export const PromptInput: React.FC<Props> = ({
  documentType,
  prompt,
  onChange,
  onGenerate,
  onBack,
  isGenerating,
}) => {
  const examples = EXAMPLE_PROMPTS[documentType] || [];
  const tips = TIPS[documentType] || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Describe Your Document</h2>
        <p className="mt-1 text-sm text-gray-600">
          Write a natural language description of what you want in the document
        </p>
      </div>

      {/* Tips Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 Tips for better results:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          {tips.map((tip, index) => (
            <li key={index} className="flex items-start">
              <span className="mr-2">•</span>
              <span>{tip}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Prompt Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Document Description
        </label>
        <textarea
          value={prompt}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Describe what you want in the document..."
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
        />
        <p className="mt-1 text-xs text-gray-500">
          {prompt.length} characters
        </p>
      </div>

      {/* Example Prompts */}
      {examples.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Example prompts:</h3>
          <div className="space-y-2">
            {examples.map((example, index) => (
              <button
                key={index}
                onClick={() => onChange(example)}
                className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md text-sm text-gray-700 transition-colors"
              >
                <span className="font-medium text-indigo-600">Example {index + 1}:</span> {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={onBack}
          disabled={isGenerating}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Back
        </button>
        <button
          onClick={onGenerate}
          disabled={!prompt.trim() || isGenerating}
          className={`
            px-6 py-2 rounded-md font-medium flex items-center space-x-2
            ${
              !prompt.trim() || isGenerating
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }
          `}
        >
          {isGenerating && (
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
          <span>{isGenerating ? 'Generating...' : 'Generate Document'}</span>
        </button>
      </div>
    </div>
  );
};
