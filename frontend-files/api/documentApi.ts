import axios from 'axios';
import type {
  DocumentGenerationRequest,
  DocumentResponse,
  GeneratePDFRequest,
  DocumentTemplatesResponse,
} from '../types/document.types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const documentApi = {
  /**
   * Get available document templates and their metadata
   */
  getTemplates: async (): Promise<DocumentTemplatesResponse> => {
    const response = await axios.get<DocumentTemplatesResponse>(
      `${API_URL}/api/documents/templates`
    );
    return response.data;
  },

  /**
   * Generate a document from a prompt or structured content
   */
  generateFromPrompt: async (
    request: DocumentGenerationRequest
  ): Promise<DocumentResponse> => {
    const response = await axios.post<DocumentResponse>(
      `${API_URL}/api/documents/generate`,
      request
    );
    return response.data;
  },

  /**
   * Generate PDF from a document
   */
  generatePDF: async (
    documentId: string,
    request: GeneratePDFRequest = {}
  ): Promise<Blob> => {
    const response = await axios.post(
      `${API_URL}/api/documents/${documentId}/generate-pdf`,
      request,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },

  /**
   * Generate and download PDF
   */
  downloadPDF: async (
    documentId: string,
    request: GeneratePDFRequest = {},
    filename: string = 'document.pdf'
  ): Promise<void> => {
    const blob = await documentApi.generatePDF(documentId, request);

    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};
