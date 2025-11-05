import React from 'react';
import type { DocumentMetadata } from '../../types/document.types';

interface Props {
  metadata: DocumentMetadata;
  onChange: (metadata: DocumentMetadata) => void;
  onNext: () => void;
  onBack: () => void;
}

const ENLISTED_RANKS = [
  'AB', 'Amn', 'A1C', 'SrA', 'SSgt', 'TSgt', 'MSgt', 'SMSgt', 'CMSgt',
];

const OFFICER_RANKS = [
  '2d Lt', '1st Lt', 'Capt', 'Maj', 'Lt Col', 'Col', 'Brig Gen', 'Maj Gen', 'Lt Gen', 'Gen',
];

export const MetadataForm: React.FC<Props> = ({ metadata, onChange, onNext, onBack }) => {
  const handleChange = (field: keyof DocumentMetadata, value: string) => {
    onChange({ ...metadata, [field]: value });
  };

  const isValid = () => {
    return (
      metadata.office_symbol?.trim() &&
      metadata.author_name?.trim() &&
      metadata.author_rank?.trim() &&
      metadata.author_title?.trim() &&
      metadata.organization?.trim()
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Author Information</h2>
        <p className="mt-1 text-sm text-gray-600">
          Enter the details of the person creating this document
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
        {/* Office Symbol */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Office Symbol <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={metadata.office_symbol || ''}
            onChange={(e) => handleChange('office_symbol', e.target.value)}
            placeholder="e.g., 51 FSS/CC"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        {/* Organization */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Organization <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={metadata.organization || ''}
            onChange={(e) => handleChange('organization', e.target.value)}
            placeholder="e.g., 51st Force Support Squadron"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        {/* Author Name and Rank */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Author Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={metadata.author_name || ''}
              onChange={(e) => handleChange('author_name', e.target.value)}
              placeholder="e.g., JOHN A. DOE"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rank <span className="text-red-500">*</span>
            </label>
            <select
              value={metadata.author_rank || ''}
              onChange={(e) => handleChange('author_rank', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Select Rank</option>
              <optgroup label="Enlisted">
                {ENLISTED_RANKS.map((rank) => (
                  <option key={rank} value={rank}>
                    {rank}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Officer">
                {OFFICER_RANKS.map((rank) => (
                  <option key={rank} value={rank}>
                    {rank}
                  </option>
                ))}
              </optgroup>
            </select>
          </div>
        </div>

        {/* Author Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={metadata.author_title || ''}
            onChange={(e) => handleChange('author_title', e.target.value)}
            placeholder="e.g., Commander"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        {/* Phone and Email */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone (Optional)
            </label>
            <input
              type="tel"
              value={metadata.phone || ''}
              onChange={(e) => handleChange('phone', e.target.value)}
              placeholder="e.g., 123-456-7890"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email (Optional)
            </label>
            <input
              type="email"
              value={metadata.email || ''}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="e.g., john.doe@us.af.mil"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={onNext}
          disabled={!isValid()}
          className={`
            px-6 py-2 rounded-md font-medium
            ${
              isValid()
                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          Continue to Content
        </button>
      </div>
    </div>
  );
};
