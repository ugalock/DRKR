export interface OrganizationMember {
    id: string
    organization_id: string
    user_id: string
    role: 'member' | 'admin' | 'owner'
}

export interface User {
    id: string
    external_id: string
    username: string
    email: string
    display_name: string | null
    default_role: 'user' | 'admin' | 'owner'
    auth_provider?: 'google' | 'github'
    picture_url?: string
    organization_memberships: OrganizationMember[]
    created_at: string
    updated_at: string
}

export interface UpdateUserRequest {
    email?: string
    display_name?: string
}