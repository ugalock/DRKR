export interface ResearchSource {
    id: number;
    deep_research_id: number;
    source_url: string;
    source_title: string | null;
    source_excerpt: string | null;
    domain: string | null;
    source_type: string | null;
    created_at: string;
} 