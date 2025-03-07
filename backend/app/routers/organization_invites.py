import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import StrictInt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.authentication import get_current_user
from app.models import Organization, OrganizationMember, OrganizationInvite, User
from app.schemas.organization_invite_request import OrganizationInviteRequest
from app.schemas.organization_invite_response import OrganizationInviteResponse
from app.services.email import send_invite_email
from app.config import settings

router = APIRouter(prefix="/orgs/{id}")
invites_router = APIRouter()

async def _is_org_admin(db: AsyncSession, user_id: int, org_id: int) -> bool:
    """Check if the user is an admin or owner of the organization."""
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.role.in_(["admin", "owner"])
        )
    )
    member = result.scalar_one_or_none()
    return member is not None

@router.post(
    "/invites",
    responses={
        201: {"model": OrganizationInviteResponse, "description": "Invite created"},
        403: {"description": "Forbidden - user is not an admin or owner"},
        404: {"description": "Organization or user not found"}
    },
    tags=["organization_invites"],
    summary="Create an invitation to an organization",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationInviteResponse,
    response_model_by_alias=True,
)
async def create_invite(
    id: StrictInt = Path(..., description="Organization ID"),
    invite_request: OrganizationInviteRequest = Body(..., description="Invite details"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> OrganizationInviteResponse:
    # Check if organization exists
    org_result = await db.execute(select(Organization).where(Organization.id == id))
    organization = org_result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is admin/owner
    is_admin = await _is_org_admin(db, current_user.id, id)
    if not is_admin:
        raise HTTPException(status_code=403, detail="You don't have permission to invite users")
    
    # Check if invited user exists
    user_result = await db.execute(select(User).where(User.id == invite_request.invited_user_id))
    invited_user = user_result.scalar_one_or_none()
    if not invited_user:
        raise HTTPException(status_code=404, detail="Invited user not found")
    
    # Check if user is already a member
    member_result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == id,
            OrganizationMember.user_id == invite_request.invited_user_id
        )
    )
    existing_member = member_result.scalar_one_or_none()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this organization")
    
    # Check if there's already a pending invite
    invite_result = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.organization_id == id,
            OrganizationInvite.invited_user_id == invite_request.invited_user_id,
            OrganizationInvite.is_used == False,
            OrganizationInvite.expires_at > datetime.utcnow()
        )
    )
    existing_invite = invite_result.scalar_one_or_none()
    if existing_invite:
        raise HTTPException(status_code=400, detail="There's already a pending invite for this user")
    
    # Create a new invite
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    new_invite = OrganizationInvite(
        organization_id=id,
        invited_user_id=invite_request.invited_user_id,
        token=token,
        role=invite_request.role,
        created_by=current_user.id,
        expires_at=expires_at
    )
    
    db.add(new_invite)
    await db.commit()
    await db.refresh(new_invite)
    
    # Generate invite link
    invite_link = f"{settings.CLIENT_URL}/invites/{token}"
    
    # Send email
    send_invite_email(
        from_user=current_user.display_name or current_user.username, 
        recipient_email=invited_user.email,
        invite_link=invite_link,
        organization_name=organization.name
    )
    
    # Create a dictionary with all the required fields, including invited_user_name
    invite_dict = {
        "id": new_invite.id,
        "organization_id": new_invite.organization_id,
        "invited_user_id": new_invite.invited_user_id,
        "invited_user_name": invited_user.display_name or invited_user.username,
        "role": new_invite.role,
        "is_used": new_invite.is_used,
        "expires_at": new_invite.expires_at.isoformat(),
        "created_at": new_invite.created_at.isoformat() if new_invite.created_at else datetime.utcnow().isoformat()
    }
    
    # Validate with all fields present
    return OrganizationInviteResponse.model_validate(invite_dict)

@router.get(
    "/invites",
    responses={
        200: {"model": List[OrganizationInviteResponse], "description": "List of invites"},
        403: {"description": "Forbidden - user is not an admin or owner"},
        404: {"description": "Organization not found"}
    },
    tags=["organization_invites"],
    summary="List all pending invites for an organization",
    response_model=List[OrganizationInviteResponse],
    response_model_by_alias=True,
)
async def list_invites(
    id: StrictInt = Path(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[OrganizationInviteResponse]:
    # Check if organization exists
    org_result = await db.execute(select(Organization).where(Organization.id == id))
    organization = org_result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is admin/owner
    is_admin = await _is_org_admin(db, current_user.id, id)
    if not is_admin:
        raise HTTPException(status_code=403, detail="You don't have permission to view invites")
    
    # Get all pending invites
    invites_result = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.organization_id == id,
            OrganizationInvite.is_used == False,
            OrganizationInvite.expires_at > datetime.utcnow()
        )
    )
    invites = invites_result.scalars().all()
    
    # Get all user IDs to fetch in a single query
    user_ids = [invite.invited_user_id for invite in invites]
    
    # Fetch all users at once
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {user.id: user for user in users_result.scalars().all()}
    
    # Create responses with invited_user_name
    responses = []
    for invite in invites:
        user = users.get(invite.invited_user_id)
        user_name = "Unknown User"
        if user:
            user_name = user.display_name or user.username
        
        # Create a dictionary with all required fields
        invite_dict = {
            "id": invite.id,
            "organization_id": invite.organization_id,
            "invited_user_id": invite.invited_user_id,
            "invited_user_name": user_name,
            "role": invite.role,
            "is_used": invite.is_used,
            "expires_at": invite.expires_at.isoformat(),
            "created_at": invite.created_at.isoformat() if invite.created_at else datetime.utcnow().isoformat()
        }
        
        # Validate with all fields present
        responses.append(OrganizationInviteResponse.model_validate(invite_dict))
    
    return responses

@router.delete(
    "/invites/{invite_id}",
    responses={
        204: {"description": "Invite deleted"},
        403: {"description": "Forbidden - user is not an admin or owner"},
        404: {"description": "Organization or invite not found"}
    },
    tags=["organization_invites"],
    summary="Delete an invitation",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_invite(
    id: StrictInt = Path(..., description="Organization ID"),
    invite_id: StrictInt = Path(..., description="Invite ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> None:
    # Check if organization exists
    org_result = await db.execute(select(Organization).where(Organization.id == id))
    organization = org_result.scalar_one_or_none()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if current user is admin/owner
    is_admin = await _is_org_admin(db, current_user.id, id)
    if not is_admin:
        raise HTTPException(status_code=403, detail="You don't have permission to delete invites")
    
    # Get the invite
    invite_result = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.id == invite_id,
            OrganizationInvite.organization_id == id
        )
    )
    invite = invite_result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    # Delete the invite
    await db.delete(invite)
    await db.commit()

@invites_router.post(
    "/invites/{token}/accept",
    responses={
        200: {"description": "Invite accepted"},
        400: {"description": "Invalid or expired invite"},
        404: {"description": "Invite not found"}
    },
    tags=["organization_invites"],
    summary="Accept an invitation",
)
async def accept_invite(
    token: str = Path(..., description="Invite token"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> dict:
    # Find the invite
    invite_result = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.token == token,
            OrganizationInvite.is_used == False,
            OrganizationInvite.expires_at > datetime.utcnow()
        )
    )
    invite = invite_result.scalar_one_or_none()
    
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found or expired")
    
    # Check if the invite is for the current user
    if invite.invited_user_id != current_user.id:
        raise HTTPException(status_code=400, detail="This invite is not for you")
    
    # Check if user is already a member
    member_result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == invite.organization_id,
            OrganizationMember.user_id == current_user.id
        )
    )
    existing_member = member_result.scalar_one_or_none()
    if existing_member:
        # Mark invite as used
        invite.is_used = True
        await db.commit()
        raise HTTPException(status_code=400, detail="You are already a member of this organization")
    
    # Add user to organization
    new_member = OrganizationMember(
        organization_id=invite.organization_id,
        user_id=current_user.id,
        role=invite.role
    )
    
    db.add(new_member)
    
    # Mark invite as used
    invite.is_used = True
    
    await db.commit()
    
    # Get organization details
    org_result = await db.execute(select(Organization).where(Organization.id == invite.organization_id))
    organization = org_result.scalar_one_or_none()
    
    return {
        "message": f"You have successfully joined {organization.name}",
        "organization_id": organization.id,
        "organization_name": organization.name
    } 