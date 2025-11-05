/**
 * Document Preview Component
 * Copy this file to: src/components/DocumentPreview.tsx
 */

import React, { useState, useEffect } from 'react';
import type {
  DocumentType,
  DocumentMetadata,
  DocumentContent,
  MFRContent,
  MemoContent,
  AppointmentContent,
  AdministrativeActionContent,
} from '../types/document.types';

interface DocumentPreviewProps {
  documentType: DocumentType;
  extractedFields: any;
  metadata: DocumentMetadata;
  onGeneratePDF: (content: DocumentContent) => void;
  isGenerating: boolean;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  documentType,
  extractedFields,
  metadata,
  onGeneratePDF,
  isGenerating,
}) => {
  const [editableContent, setEditableContent] = useState<any>(extractedFields);

  useEffect(() => {
    setEditableContent(extractedFields);
  }, [extractedFields]);

  const handleFieldChange = (field: string, value: any) => {
    setEditableContent({ ...editableContent, [field]: value });
  };

  const handleArrayFieldChange = (field: string, index: number, value: string) => {
    const newArray = [...(editableContent[field] || [])];
    newArray[index] = value;
    setEditableContent({ ...editableContent, [field]: newArray });
  };

  const handleAddArrayItem = (field: string) => {
    const newArray = [...(editableContent[field] || []), ''];
    setEditableContent({ ...editableContent, [field]: newArray });
  };

  const handleRemoveArrayItem = (field: string, index: number) => {
    const newArray = [...(editableContent[field] || [])];
    newArray.splice(index, 1);
    setEditableContent({ ...editableContent, [field]: newArray });
  };

  const handleGeneratePDF = () => {
    let content: DocumentContent;

    switch (documentType) {
      case 'mfr':
        content = {
          subject: editableContent.subject || '',
          body_paragraphs: editableContent.body_hints || editableContent.body_paragraphs || [''],
          distribution_list: editableContent.distribution_list,
          attachments: editableContent.attachments,
        } as MFRContent;
        break;

      case 'memo':
        content = {
          to_line: editableContent.to_line || '',
          thru_line: editableContent.thru_line,
          subject: editableContent.subject || '',
          body_paragraphs: editableContent.body_hints || editableContent.body_paragraphs || [''],
          distribution_list: editableContent.distribution_list,
          attachments: editableContent.attachments,
        } as MemoContent;
        break;

      case 'appointment':
        content = {
          appointee_name: editableContent.appointee_name || '',
          appointee_rank: editableContent.appointee_rank || '',
          appointee_ssan: editableContent.appointee_ssan,
          position_title: editableContent.position_title || '',
          authority_citation: editableContent.authority_citation || '',
          duties: editableContent.duties || [''],
          effective_date: editableContent.effective_date || new Date().toISOString().split('T')[0],
          termination_date: editableContent.termination_date,
        } as AppointmentContent;
        break;

      case 'loc':
      case 'loa':
      case 'lor':
        content = {
          member_name: editableContent.member_name || '',
          member_rank: editableContent.member_rank || '',
          member_unit: editableContent.member_unit || metadata.organization,
          member_ssan: editableContent.member_ssan,
          subject: editableContent.subject || '',
          incident_date: editableContent.incident_date || new Date().toISOString().split('T')[0],
          incident_description: editableContent.incident_description || '',
          violations: editableContent.violations || [''],
          standards_expected: editableContent.standards_expected || '',
          consequences: editableContent.consequences || '',
          previous_actions: editableContent.previous_actions,
          filing_location: editableContent.filing_location,
          appeal_rights: editableContent.appeal_rights,
        } as AdministrativeActionContent;
        break;

      default:
        content = editableContent;
    }

    onGeneratePDF(content);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Review & Edit</h3>

      <div className="space-y-4">
        {/* Subject Field (for MFR, Memo, LOC/LOA/LOR) */}
        {['mfr', 'memo', 'loc', 'loa', 'lor'].includes(documentType) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject
            </label>
            <input
              type="text"
              value={editableContent.subject || ''}
              onChange={(e) => handleFieldChange('subject', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Subject line"
            />
          </div>
        )}

        {/* MFR/Memo specific fields */}
        {['mfr', 'memo'].includes(documentType) && (
          <>
            {documentType === 'memo' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    To
                  </label>
                  <input
                    type="text"
                    value={editableContent.to_line || ''}
                    onChange={(e) => handleFieldChange('to_line', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Recipient office symbol"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Thru (optional)
                  </label>
                  <input
                    type="text"
                    value={editableContent.thru_line || ''}
                    onChange={(e) => handleFieldChange('thru_line', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Routing office symbol"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Body Paragraphs
              </label>
              {(editableContent.body_hints || editableContent.body_paragraphs || ['']).map((para: string, idx: number) => (
                <div key={idx} className="flex gap-2 mb-2">
                  <textarea
                    value={para}
                    onChange={(e) => handleArrayFieldChange('body_hints', idx, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                    rows={2}
                    placeholder={`Paragraph ${idx + 1}`}
                  />
                  <button
                    onClick={() => handleRemoveArrayItem('body_hints', idx)}
                    className="px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                onClick={() => handleAddArrayItem('body_hints')}
                className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 text-sm"
              >
                + Add Paragraph
              </button>
            </div>
          </>
        )}

        {/* Appointment specific fields */}
        {documentType === 'appointment' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Appointee Name
              </label>
              <input
                type="text"
                value={editableContent.appointee_name || ''}
                onChange={(e) => handleFieldChange('appointee_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Position Title
              </label>
              <input
                type="text"
                value={editableContent.position_title || ''}
                onChange={(e) => handleFieldChange('position_title', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Authority Citation (AFI)
              </label>
              <input
                type="text"
                value={editableContent.authority_citation || ''}
                onChange={(e) => handleFieldChange('authority_citation', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="e.g., AFI 91-202, para 2.3"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duties
              </label>
              {(editableContent.duties || ['']).map((duty: string, idx: number) => (
                <div key={idx} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={duty}
                    onChange={(e) => handleArrayFieldChange('duties', idx, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                    placeholder={`Duty ${idx + 1}`}
                  />
                  <button
                    onClick={() => handleRemoveArrayItem('duties', idx)}
                    className="px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                onClick={() => handleAddArrayItem('duties')}
                className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 text-sm"
              >
                + Add Duty
              </button>
            </div>
          </>
        )}

        {/* Administrative Action specific fields */}
        {['loc', 'loa', 'lor'].includes(documentType) && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Member Name
              </label>
              <input
                type="text"
                value={editableContent.member_name || ''}
                onChange={(e) => handleFieldChange('member_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Incident Description
              </label>
              <textarea
                value={editableContent.incident_description || ''}
                onChange={(e) => handleFieldChange('incident_description', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={3}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Violations (AFI Citations)
              </label>
              {(editableContent.violations || ['']).map((violation: string, idx: number) => (
                <div key={idx} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={violation}
                    onChange={(e) => handleArrayFieldChange('violations', idx, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., AFI 36-2618, para 3.1"
                  />
                  <button
                    onClick={() => handleRemoveArrayItem('violations', idx)}
                    className="px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                onClick={() => handleAddArrayItem('violations')}
                className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 text-sm"
              >
                + Add Violation
              </button>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Standards Expected
              </label>
              <textarea
                value={editableContent.standards_expected || ''}
                onChange={(e) => handleFieldChange('standards_expected', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={2}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Consequences
              </label>
              <textarea
                value={editableContent.consequences || ''}
                onChange={(e) => handleFieldChange('consequences', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={2}
              />
            </div>
            {documentType === 'lor' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filing Location
                </label>
                <select
                  value={editableContent.filing_location || 'PIF'}
                  onChange={(e) => handleFieldChange('filing_location', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="PIF">PIF (Personnel Information File)</option>
                  <option value="DCAF">DCAF (Disciplinary Control and Actions File)</option>
                  <option value="UPRG">UPRG (Unit Personnel Record Group)</option>
                </select>
              </div>
            )}
          </>
        )}
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <button
          onClick={handleGeneratePDF}
          disabled={isGenerating}
          className="w-full px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {isGenerating ? 'Generating PDF...' : '📄 Generate PDF'}
        </button>
      </div>
    </div>
  );
};
