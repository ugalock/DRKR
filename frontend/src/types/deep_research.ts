export interface DeepResearch {
    id: number;
    user_id: number;
    owner_user_id: number | null;
    owner_org_id: number | null;
    visibility: string;
    title: string;
    prompt_text: string;
    final_report: string;
    model_name: string | null;
    model_params: string | null;
    source_count: number;
    created_at: string;
    updated_at: string;
}

export interface CreateDeepResearchRequest {
    title: string;
    prompt_text: string;
    final_report: string;
}

export interface UpdateDeepResearchRequest {
    title?: string;
    prompt_text?: string;
    final_report?: string;
}
