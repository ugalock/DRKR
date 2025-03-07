import { OrganizationMember } from './organization'

export interface User {
    id: number
    external_id: string
    username: string
    email: string
    display_name: string | null
    default_role: 'user' | 'admin' | 'owner'
    auth_provider?: 'google-oauth2' | 'github'
    picture_url?: string
    organization_memberships: OrganizationMember[]
    created_at: string
    updated_at: string
}

export interface UpdateUserRequest {
    email?: string
    display_name?: string
}