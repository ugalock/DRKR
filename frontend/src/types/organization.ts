export interface OrganizationMember {
  id?: number;
  organization_id?: number;
  user_id?: number;
  role?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Organization {
  id?: number;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  members?: OrganizationMember[];
}

export interface OrgMembershipRequest {
  user_id: number;
  role?: string;
}

export interface OrganizationCreateRequest {
  name: string;
  description?: string;
} 