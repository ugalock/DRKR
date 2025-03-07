export type ResearchJobStatus = 'pending_answers' | 'running' | 'completed' | 'failed' | 'cancelled';
export type Visibility = 'private' | 'public' | 'org';

export interface ResearchJob {
    id: number;
    job_id: string;
    user_id: number;
    owner_user_id?: number;
    owner_org_id?: number;
    visibility: Visibility;
    status: ResearchJobStatus;
    service: string;
    prompt: string;
    model_name: string;
    model_params?: Record<string, any>;
    deep_research_id?: number;
    created_at?: string;
    updated_at?: string;
}

export interface ResearchJobCreateRequest {
    service: string;
    prompt: string;
    model?: string;
    model_params?: Record<string, any>;
    visibility?: Visibility;
    org_id?: number;
}

export interface ResearchJobCreateResponse {
    job: ResearchJob;
    questions?: string[];
}

export interface ResearchJobUpdateRequest {
    visibility?: Visibility;
    status?: ResearchJobStatus;
}

export interface ResearchJobGetRequest {
    id?: number;
    job_id?: string;
    service?: string;
}

export interface ResearchJobAnswerRequest {
    service: string;
    job_id: string;
    answers: string[];
} 