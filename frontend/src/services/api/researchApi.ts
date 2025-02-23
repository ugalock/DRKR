import { DeepResearch, CreateDeepResearchRequest, UpdateDeepResearchRequest } from '../../types/deep_research';
import api from './axiosConfig';

export const researchApi = {
  getResearchItems: async (params?: { page?: number; limit?: number }) => {
    const response = await api.get<{ items: DeepResearch[]; total: number }>('/api/deep-research', { params });
    return response.data;
  },

  getResearchById: async (id: string) => {
    const response = await api.get<DeepResearch>(`/api/deep-research/${id}`);
    return response.data;
  },

  createResearch: async (data: CreateDeepResearchRequest) => {
    const response = await api.post<DeepResearch>('/api/deep-research', data);
    return response.data;
  },

  updateResearch: async (id: string, data: UpdateDeepResearchRequest) => {
    const response = await api.patch<DeepResearch>(`/api/deep-research/${id}`, data);
    return response.data;
  },

  deleteResearch: async (id: string) => {
    const response = await api.delete<void>(`/api/deep-research/${id}`);
    return response.data;
  },

  // Add other research-related API calls
};
