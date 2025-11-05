/**
 * API integration for Air Force Document Generator
 * Copy this file to: src/api/documentApi.ts
 */

import axios from 'axios';
import type {
  DocumentGenerationRequest,
  DocumentResponse,
  DocumentTemplatesResponse,
  GeneratePDFRequest,
} from '../types/document.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const documentApi = {
  /**
   * Get list of available document templates
   */
  getTemplates: async (): Promise<DocumentTemplatesResponse> => {
    const response = await axios.get(`${API_BASE_URL}/api/documents/templates`);
    return response.data;
  },

  /**
   * Generate document from prompt
   */
  generateFromPrompt: async (
    request: DocumentGenerationRequest
  ): Promise<DocumentResponse> => {
    const response = await axios.post(
      `${API_BASE_URL}/api/documents/generate`,
      request
    );
    return response.data;
  },

  /**
   * Generate PDF from document content
   */
  generatePDF: async (
    documentId: string,
    request: GeneratePDFRequest
  ): Promise<Blob> => {
    const response = await axios.post(
      `${API_BASE_URL}/api/documents/${documentId}/generate-pdf`,
      request,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },

  /**
   * Download PDF (convenience method)
   */
  downloadPDF: async (
    documentId: string,
    request: GeneratePDFRequest,
    filename: string
  ): Promise<void> => {
    const blob = await documentApi.generatePDF(documentId, request);

    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};
