import { Comment } from './comment';
import { ResearchChunk } from './research_chunk';
import { ResearchSummary } from './research_summary';
import { ResearchSource } from './research_source';
import { ResearchAutoMetadata } from './research_auto_metadata';
import { ResearchRating } from './research_rating';
import { ResearchJob, Visibility } from './research_job';

export interface DeepResearch {
    id: number;
    user_id: number;
    owner_user_id: number | null;
    owner_org_id: number | null;
    visibility: Visibility;
    title: string;
    prompt_text: string;
    questions_and_answers?: string | null;
    final_report: string;
    model_name: string | null;
    model_params: Record<string, any> | null;
    source_count: number;
    created_at: string;
    updated_at: string;
    chunks?: ResearchChunk[];
    summaries?: ResearchSummary[];
    sources?: ResearchSource[];
    auto_metadata?: ResearchAutoMetadata[];
    comments?: Comment[];
    ratings?: ResearchRating[];
    research_job?: ResearchJob;
    avg_rating?: number | null;
    creator_username?: string | null;
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
    owner_org_id?: number;
    visibility?: Visibility;
}
