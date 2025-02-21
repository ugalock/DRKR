# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import Any, List
from app.schemas.org_membership_request import OrgMembershipRequest
from app.schemas.organization import Organization
from app.schemas.organization_create_request import OrganizationCreateRequest


class BaseOrganizations:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseOrganizations.subclasses = BaseOrganizations.subclasses + (cls,)
    async def orgs_get(
        self,
    ) -> List[Organization]:
        ...


    async def orgs_id_get(
        self,
        id: StrictInt,
    ) -> Organization:
        ...


    async def orgs_id_members_delete(
        self,
        id: StrictInt,
        user_id: StrictInt,
    ) -> None:
        ...


    async def orgs_id_members_post(
        self,
        id: StrictInt,
        org_membership_request: OrgMembershipRequest,
    ) -> None:
        ...


    async def orgs_post(
        self,
        organization_create_request: OrganizationCreateRequest,
    ) -> Organization:
        ...
