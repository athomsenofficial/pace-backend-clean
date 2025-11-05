/**
 * TypeScript types for Air Force Document Generator
 * Copy this file to: src/types/document.types.ts
 */

export type DocumentType = 'mfr' | 'memo' | 'appointment' | 'loc' | 'loa' | 'lor';

export interface DocumentMetadata {
  office_symbol: string;
  author_name: string;
  author_rank: string;
  author_title: string;
  organization: string;
  date?: string;
  phone?: string;
  email?: string;
}

export interface MFRContent {
  subject: string;
  body_paragraphs: string[];
  distribution_list?: string[];
  attachments?: string[];
}

export interface MemoContent {
  to_line: string;
  thru_line?: string;
  subject: string;
  body_paragraphs: string[];
  distribution_list?: string[];
  attachments?: string[];
}

export interface AppointmentContent {
  appointee_name: string;
  appointee_rank: string;
  appointee_ssan?: string;
  position_title: string;
  authority_citation: string;
  duties: string[];
  effective_date: string;
  termination_date?: string;
}

export interface AdministrativeActionContent {
  member_name: string;
  member_rank: string;
  member_unit: string;
  member_ssan?: string;
  subject: string;
  incident_date: string;
  incident_description: string;
  violations: string[];
  standards_expected: string;
  consequences: string;
  previous_actions?: string[];
  filing_location?: 'PIF' | 'DCAF' | 'UPRG';
  appeal_rights?: string;
}

export type DocumentContent =
  | MFRContent
  | MemoContent
  | AppointmentContent
  | AdministrativeActionContent;

export interface DocumentGenerationRequest {
  document_type: DocumentType;
  prompt: string;
  metadata: DocumentMetadata;
  options?: Record<string, any>;
}

export interface DocumentResponse {
  document_id: string;
  session_id: string;
  document_type: string;
  status: 'draft' | 'finalized';
  message: string;
  extracted_fields?: Record<string, any>;
  validation_warnings: string[];
  pdf_url?: string;
}

export interface DocumentTemplate {
  type: DocumentType;
  name: string;
  description: string;
  required_fields: string[];
  optional_fields: string[];
  example_prompts: string[];
}

export interface DocumentTemplatesResponse {
  templates: DocumentTemplate[];
}

export interface GeneratePDFRequest {
  metadata: DocumentMetadata;
  content: DocumentContent;
}
