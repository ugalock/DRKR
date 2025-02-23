export interface User {
    id: string
    username: string
    email: string
    display_name: string | null
    default_role: 'user' | 'admin' | 'owner'
    created_at: string
    updated_at: string
    auth_id?: string
    auth_provider?: 'google' | 'github',
    picture_url?: string
}

export interface OrganizationMember {
    id: string
    organization_id: string
    user_id: string
    role: 'member' | 'admin' | 'owner'
}
export interface UserProfile extends User {
    org_memberships: OrganizationMember[]
}

export interface UpdateUserRequest {
    email?: string
    display_name?: string
}