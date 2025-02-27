export interface AiModel {
    id: number;
    model_key: string;
    default_params: Record<string, any>;
    max_tokens: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ResearchServiceModel {
    id: number;
    service_id: number;
    model_id: number;
    is_default: boolean;
    created_at: string;
    updated_at: string;
    model: AiModel;
}

export interface ResearchService {
    id: number;
    service_key: string;
    name: string;
    description?: string | null;
    url?: string | null;
    default_model_id?: number | null;
    created_at: string;
    updated_at: string;
    default_model?: AiModel | null;
    service_models: ResearchServiceModel[];
}

export type ResearchServiceCreate = Pick<
    ResearchService,
    'service_key' | 'name' | 'description' | 'url' | 'default_model_id'
>; 