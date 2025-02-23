# app/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
    Index,
    Enum,
    func,
)
from pgvector.sqlalchemy import Vector as VECTOR
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func as sql_func
import datetime

from app.db.database import Base
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

# 1) organizations
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    # e.g. api_keys = relationship("ApiKey", back_populates="organization", ...)

# 2) users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(255), unique=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(100))
    default_role = Column(String(50), default="user")
    auth_provider = Column(String(50), default="google-oauth2")
    picture_url = Column(String(255))
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    __table_args__ = (
        CheckConstraint("""
            auth_provider IN ('google-oauth2', 'github', 'facebook', 'linkedin', 'twitter')
        """, name="chk_user_auth_provider"),
    )
    # Relationship examples
    # deep_research_created = relationship("DeepResearch", back_populates="owner_user") # etc.

# 3) organization_members
class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False, default="member")
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_user"),
    )

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", backref="organization_memberships")

# 4) api_keys
class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    expires_at = Column(DateTime(timezone=False))

    # Enforce exactly one of user_id or organization_id is non-NULL:
    __table_args__ = (
        CheckConstraint("""
            (user_id IS NOT NULL AND organization_id IS NULL)
            OR (user_id IS NULL AND organization_id IS NOT NULL)
        """, name="chk_api_key_owner"),
    )

    # You could define relationships if you want:
    user = relationship("User", backref="api_keys")
    organization = relationship("Organization", backref="api_keys")

# We'll define a Python Enum for 'visibility' to match your Postgres enum.
VisibilityEnum = PGEnum("private", "public", "org", name="visibility", create_type=True)

# 5) deep_research
class DeepResearch(Base):
    __tablename__ = "deep_research"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    owner_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    visibility = Column(VisibilityEnum, nullable=False, server_default="public")

    title = Column(String(255), nullable=False)
    prompt_text = Column(Text, nullable=False)
    final_report = Column(Text, nullable=False)
    model_name = Column(String(100))
    model_params = Column(JSONB)
    source_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    # Postgres full-text columns
    prompt_tsv = Column(TSVECTOR)
    report_tsv = Column(TSVECTOR)

    # Vector embeddings
    prompt_embedding = Column(VECTOR(3072))
    report_embedding = Column(VECTOR(3072))

    # Relationships (optional)
    # e.g. user = relationship("User", foreign_keys=[user_id])
    # If you want to track the "owner" user as well:
    # owner_user = relationship("User", foreign_keys=[owner_user_id])
    # owner_org = relationship("Organization", foreign_keys=[owner_org_id])

# 6) research_chunks
class ResearchChunk(Base):
    __tablename__ = "research_chunks"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_type = Column(String(50))
    chunk_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    deep_research = relationship("DeepResearch", backref=backref("chunks", cascade="all, delete-orphan"))

# 7) research_summaries
class ResearchSummary(Base):
    __tablename__ = "research_summaries"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    summary_scope = Column(String(50), nullable=False)
    summary_length = Column(String(50), nullable=False)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    deep_research = relationship("DeepResearch", backref=backref("summaries", cascade="all, delete-orphan"))

# 8) research_sources
class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    source_url = Column(Text, nullable=False)
    source_title = Column(Text)
    source_excerpt = Column(Text)
    domain = Column(String(255))  # e.g. "nytimes.com"
    source_type = Column(String(50))  # e.g. "website", "paper", "book"
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    deep_research = relationship("DeepResearch", backref=backref("sources", cascade="all, delete-orphan"))

# 9) domain_co_occurrences
class DomainCoOccurrence(Base):
    __tablename__ = "domain_co_occurrences"

    id = Column(Integer, primary_key=True)
    domain_a = Column(String(255), nullable=False)
    domain_b = Column(String(255), nullable=False)
    co_occurrence_count = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime(timezone=False), server_default=sql_func.now())

    __table_args__ = (
        UniqueConstraint("domain_a", "domain_b", name="uq_domain_a_b"),
    )

# 10) tags
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_global = Column(Boolean, nullable=False, default=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    # The check constraint:
    __table_args__ = (
        CheckConstraint("""
            (
              is_global = TRUE AND organization_id IS NULL AND user_id IS NULL
            )
            OR
            (
              is_global = FALSE
              AND organization_id IS NOT NULL
              AND user_id IS NULL
            )
            OR
            (
              is_global = FALSE
              AND user_id IS NOT NULL
              AND organization_id IS NULL
            )
        """, name="chk_tags_scope"),
    )

    # Partial indexes for uniqueness across different scopes typically need to be done
    # in migrations manually. You can define them here, but Alembic might not autogenerate them:
    # from sqlalchemy import Index, text
    Index("unique_global_tag_name", func.lower(name),
          unique=True,
          postgresql_where="is_global = TRUE")

    Index("unique_org_tag_name", "organization_id", func.lower(name),
          unique=True,
          postgresql_where="organization_id IS NOT NULL")

    Index("unique_user_tag_name", "user_id", func.lower(name),
          unique=True,
          postgresql_where="user_id IS NOT NULL")

# 11) deep_research_tags (join table)
from sqlalchemy import Table, ForeignKeyConstraint

class DeepResearchTag(Base):
    __tablename__ = "deep_research_tags"

    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

# 12) research_ratings
class ResearchRating(Base):
    __tablename__ = "research_ratings"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating_value = Column(Integer, nullable=False)  # e.g. 1-5 or -1/1
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    __table_args__ = (
        UniqueConstraint("deep_research_id", "user_id", name="uq_research_user_rating"),
    )

    deep_research = relationship("DeepResearch", backref="ratings")
    user = relationship("User", backref="research_ratings")

# 13) research_comments
class ResearchComment(Base):
    __tablename__ = "research_comments"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_comment_id = Column(Integer)  # For nested threads (self-referential if needed)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    deep_research = relationship("DeepResearch", backref="comments")
    user = relationship("User", backref="comments")

# 14) research_auto_metadata
class ResearchAutoMetadata(Base):
    __tablename__ = "research_auto_metadata"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    meta_key = Column(String(100), nullable=False)
    meta_value = Column(Text, nullable=False)
    confidence_score = Column(Integer)  # or Float
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    deep_research = relationship("DeepResearch", backref="auto_metadata")
