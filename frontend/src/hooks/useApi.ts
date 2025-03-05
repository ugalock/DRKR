// frontend/src/hooks/useApi.ts
import axios from 'axios';
import { useMemo } from 'react';

import { DeepResearch, CreateDeepResearchRequest, UpdateDeepResearchRequest } from '../types/deep_research';
import { Tag, CreateTagRequest } from '../types/tag';
import { User, UpdateUserRequest } from '../types/user';
import { ResearchService } from '../types/research_service';
import { Organization, OrgMembershipRequest, OrganizationCreateRequest } from '../types/organization';
import { ApiKey, ApiKeyCreate } from '../types/api_key';
import { 
    ResearchJob, 
    ResearchJobCreateRequest, 
    ResearchJobCreateResponse, 
    ResearchJobUpdateRequest, 
    ResearchJobGetRequest, 
    ResearchJobAnswerRequest
} from '../types/research_job';

import { useAuth } from './useAuth';

export const useApi = () => {
    const { getAccessTokenSilently } = useAuth();

    const api = useMemo(() => {
        const instance = axios.create({
            baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        instance.interceptors.request.use(
            async (config) => {
                const token = await getAccessTokenSilently();
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // instance.interceptors.response.use(
        //     (response) => response,
        //     async (error) => {
        //         if (error.response?.status === 401) {
        //             localStorage.removeItem('token');
        //             window.location.href = '/';
        //         }
        //         return Promise.reject(error);
        //     }
        // );

        return instance;
    }, [getAccessTokenSilently]);

    const deepResearchApi = {
        getResearchItems: async (params?: { page?: number; limit?: number }) => {
            const response = await api.get<DeepResearch[]>('/api/deep-research', { params });
            console.log(response.data);
            return response.data;
        },

        getResearchById: async (id: string) => {
            const response = await api.get<DeepResearch>(`/api/deep-research/${id}`);
            return response.data;
        },

        getResearchTags: async (id: string) => {
            const response = await api.get<Tag[]>(`/api/deep-research/${id}/tags`);
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
    }

    const tagsApi = {
        getTags: async () => {
            const response = await api.get<Tag[]>('/api/tags');
            return response.data;
        },

        createTag: async (data: CreateTagRequest) => {
            const response = await api.post<Tag>('/api/tags', data);
            return response.data;
        },

        // Add other tag-related API calls
    }

    const userApi = {
        updateUser: async (data: UpdateUserRequest) => {
            const response = await api.patch<User>('/api/users/me', data);
            return response.data;
        },

        // Add other user-related API calls as needed
    }

    const researchJobsApi = {
        getResearchJobs: async (params?: { 
            page?: number; 
            limit?: number;
            service?: string;
            status?: string;
            visibility?: string;
        }) => {
            const response = await api.get<ResearchJob[]>('/api/research-jobs', { params });
            return response.data;
        },

        getResearchJob: async (request: ResearchJobGetRequest) => {
            const response = await api.post<ResearchJob>('/api/research-jobs/get', request);
            return response.data;
        },

        createResearchJob: async (data: ResearchJobCreateRequest) => {
            const response = await api.post<ResearchJobCreateResponse>('/api/research-jobs', data);
            return response.data;
        },

        updateResearchJob: async (id: string, data: ResearchJobUpdateRequest) => {
            const response = await api.patch<ResearchJob>(`/api/research-jobs/${id}`, data);
            return response.data;
        },

        answerResearchJob: async (data: ResearchJobAnswerRequest) => {
            const response = await api.post<ResearchJob>('/api/research-jobs/answer', data);
            return response.data;
        },
    }

    const researchServicesApi = {
        getResearchServices: async (params?: { service?: string }) => {
            const response = await api.get<ResearchService[]>('/api/research-services', { params });
            return response.data;
        },
    }

    const apiKeysApi = {
        getApiKeys: async () => {
            const response = await api.get<ApiKey[]>('/api/api-keys');
            return response.data;
        },

        createApiKey: async (data: ApiKeyCreate, orgId?: number) => {
            const response = await api.post<ApiKey>('/api/api-keys', data, {
                params: orgId ? { org_id: orgId } : undefined
            });
            return response.data;
        },

        revokeApiKey: async (keyId: number) => {
            const response = await api.delete<{ message: string }>(`/api/api-keys/${keyId}`);
            return response.data;
        },
    }

    const organizationsApi = {
        getOrganizations: async () => {
            const response = await api.get<Organization[]>('/api/orgs');
            return response.data;
        },

        getOrganization: async (id: number) => {
            const response = await api.get<Organization>(`/api/orgs/${id}`);
            return response.data;
        },

        createOrganization: async (data: OrganizationCreateRequest) => {
            const response = await api.post<Organization>('/api/orgs', data);
            return response.data;
        },

        addMember: async (orgId: number, data: OrgMembershipRequest) => {
            const response = await api.post<void>(`/api/orgs/${orgId}/members`, data);
            return response.data;
        },

        removeMember: async (orgId: number, userId: number) => {
            const response = await api.delete<void>(`/api/orgs/${orgId}/members`, {
                params: { user_id: userId }
            });
            return response.data;
        },
    }

    return {
        api,
        deepResearchApi,
        tagsApi,
        userApi,
        researchJobsApi,
        researchServicesApi,
        apiKeysApi,
        organizationsApi,
    };
};