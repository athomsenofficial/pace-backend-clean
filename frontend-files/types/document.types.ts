// TypeScript types for Air Force Document Generator
// Mirrors backend Pydantic models in document_generator/models.py

export type DocumentType = 'mfr' | 'memo' | 'appointment' | 'loc' | 'loa' | 'lor';

export interface DocumentMetadata {
  office_symbol: string;
  author_name: string;
  author_rank: string;
  author_title: string;
  organization: string;
  phone?: string;
  email?: string;
  date?: string; // ISO date string
}

export interface SignatureBlock {
  name: string;
  rank: string;
  title: string;
  organization?: string;
  date_signed?: string; // ISO date string
}

export interface MFRContent {
  subject: string;
  body_paragraphs: string[];
  participants?: string[];
  location?: string;
}

export interface MemoContent {
  recipient_name: string;
  recipient_office: string;
  subject: string;
  body_paragraphs: string[];
  coordination_required?: boolean;
  coordinating_officials?: SignatureBlock[];
}

export interface AppointmentContent {
  appointee_name: string;
  appointee_rank: string;
  position_title: string;
  duties: string[];
  effective_date: string; // ISO date string
  termination_date?: string; // ISO date string
  authority_citation: string;
}

export interface AdministrativeActionContent {
  member_name: string;
  member_rank: string;
  member_unit: string;
  incident_date: string; // ISO date string
  incident_description: string;
  violations: string[];
  corrective_actions: string[];
  authority_citation: string;
  counseling_points?: string[];
}

export interface DocumentGenerationRequest {
  document_type: DocumentType;
  metadata: DocumentMetadata;
  use_prompt?: boolean;
  prompt?: string;
  content?: MFRContent | MemoContent | AppointmentContent | AdministrativeActionContent;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface DocumentResponse {
  document_id: string;
  document_type: DocumentType;
  metadata: DocumentMetadata;
  content: MFRContent | MemoContent | AppointmentContent | AdministrativeActionContent;
  validation: ValidationResult;
  created_at: string;
}

export interface GeneratePDFRequest {
  include_cui_marking?: boolean;
  logo_filename?: string;
}

export interface DocumentTemplatesResponse {
  templates: {
    [key in DocumentType]: {
      name: string;
      description: string;
      required_fields: string[];
      example_prompt: string;
    };
  };
}
