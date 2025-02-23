export interface Tag {
    id: number
    name: string
    description: string | null
    is_global: boolean
    organization_id: number | null
    user_id: number | null
    created_at: string
    updated_at: string
}

export interface CreateTagRequest {
    name: string
    description?: string
    is_global?: boolean
    organization_id?: number
    user_id?: number
}