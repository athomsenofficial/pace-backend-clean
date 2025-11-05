/**
 * Metadata Form Component
 * Copy this file to: src/components/MetadataForm.tsx
 */

import React from 'react';
import type { DocumentMetadata } from '../types/document.types';

interface MetadataFormProps {
  metadata: DocumentMetadata;
  onChange: (metadata: DocumentMetadata) => void;
}

const rankOptions = [
  // Enlisted
  'AB', 'Amn', 'A1C', 'SrA', 'SSgt', 'TSgt', 'MSgt', 'SMSgt', 'CMSgt',
  // Officer
  '2d Lt', '1st Lt', 'Capt', 'Maj', 'Lt Col', 'Col', 'Brig Gen', 'Maj Gen', 'Lt Gen', 'Gen'
];

export const MetadataForm: React.FC<MetadataFormProps> = ({ metadata, onChange }) => {
  const handleChange = (field: keyof DocumentMetadata, value: string) => {
    onChange({ ...metadata, [field]: value });
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Office Symbol */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Office Symbol <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={metadata.office_symbol}
          onChange={(e) => handleChange('office_symbol', e.target.value)}
          placeholder="e.g., 51 FSS/CC"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Author Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Your Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={metadata.author_name}
          onChange={(e) => handleChange('author_name', e.target.value)}
          placeholder="e.g., John A. Doe"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Author Rank */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Your Rank <span className="text-red-500">*</span>
        </label>
        <select
          value={metadata.author_rank}
          onChange={(e) => handleChange('author_rank', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Select Rank</option>
          <optgroup label="Enlisted">
            {rankOptions.slice(0, 9).map(rank => (
              <option key={rank} value={rank}>{rank}</option>
            ))}
          </optgroup>
          <optgroup label="Officer">
            {rankOptions.slice(9).map(rank => (
              <option key={rank} value={rank}>{rank}</option>
            ))}
          </optgroup>
        </select>
      </div>

      {/* Author Title */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Your Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={metadata.author_title}
          onChange={(e) => handleChange('author_title', e.target.value)}
          placeholder="e.g., Commander"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Organization */}
      <div className="md:col-span-2">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Organization <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={metadata.organization}
          onChange={(e) => handleChange('organization', e.target.value)}
          placeholder="e.g., 51st Force Support Squadron"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Phone (Optional) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Phone (Optional)
        </label>
        <input
          type="text"
          value={metadata.phone || ''}
          onChange={(e) => handleChange('phone', e.target.value)}
          placeholder="e.g., DSN 315-784-1234"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Email (Optional) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Email (Optional)
        </label>
        <input
          type="email"
          value={metadata.email || ''}
          onChange={(e) => handleChange('email', e.target.value)}
          placeholder="e.g., john.doe@us.af.mil"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>
  );
};
