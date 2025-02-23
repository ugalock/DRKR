import { User, UpdateUserRequest } from '../../types/user';
import api from './axiosConfig';

export const userApi = {
  getCurrentUser: async () => {
    const response = await api.get<User>('/api/users/me');
    return response.data;
  },

  updateUser: async (data: UpdateUserRequest) => {
    const response = await api.patch<User>('/api/users/me', data);
    return response.data;
  },

  // Add other user-related API calls as needed
};
