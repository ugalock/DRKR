// Organization invite types
export interface OrganizationInvite {
    id: number;
    organization_id: number;
    invited_user_id: number;
    invited_user_name: string;
    role: string;
    is_used: boolean;
    expires_at: string;
    created_at: string;
}

export interface OrganizationInviteRequest {
    invited_user_id: number;
    role: string;
}

export interface AcceptInviteResponse {
    message: string;
    organization_id: number;
    organization_name: string;
}

export interface InviteError {
    detail: string;
}