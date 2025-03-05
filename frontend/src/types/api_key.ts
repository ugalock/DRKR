// frontend/src/types/api_key.ts

export interface ApiService {
    id: number;
    name: string;
    created_at: string;
    updated_at: string;
}

export interface ApiKey {
    id: number;
    name: string;
    user_id?: number;
    organization_id?: number;
    token: string;
    is_active: boolean;
    expires_at: string;
    api_service?: ApiService;
    created_at: string;
    updated_at: string;
}

export interface ApiKeyCreate {
    name: string;
    api_service_name?: string;
    token?: string;
    expires_in_days?: number;
}