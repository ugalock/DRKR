import { Tag, CreateTagRequest } from '../../types/tags';
import api from './axiosConfig';

export const tagsApi = {
  getTags: async () => {
    const response = await api.get<Tag[]>('/api/tags');
    return response.data;
  },

  createTag: async (data: CreateTagRequest) => {
    const response = await api.post<Tag>('/api/tags', data);
    return response.data;
  },

  // Add other tag-related API calls
};
