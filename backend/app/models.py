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
    api_keys = relationship("ApiKey", back_populates="organization")
    research_jobs = relationship("ResearchJob", back_populates="organization", foreign_keys="ResearchJob.owner_org_id")

# 2) users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(255), unique=True, nullable=False)
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
    
    # Relationships - added explicit back_populates
    organization_memberships = relationship("OrganizationMember", back_populates="user", lazy="selectin")
    api_keys = relationship("ApiKey", back_populates="user", foreign_keys="ApiKey.user_id")
    research_ratings = relationship("ResearchRating", back_populates="user")
    comments = relationship("ResearchComment", back_populates="user")
    research_jobs = relationship("ResearchJob", back_populates="user", foreign_keys="ResearchJob.user_id")

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
    user = relationship("User", back_populates="organization_memberships")

# 4) api_keys
class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    expires_at = Column(DateTime(timezone=False))

    # Enforce exactly one of user_id or organization_id is non-NULL:
    __table_args__ = (
        CheckConstraint("""
            (user_id IS NOT NULL AND organization_id IS NULL)
            OR (user_id IS NULL AND organization_id IS NOT NULL)
        """, name="chk_api_key_owner"),
    )

    # Changed backref to back_populates
    user = relationship("User", back_populates="api_keys")
    organization = relationship("Organization", back_populates="api_keys")

# We'll define a Python Enum for 'visibility' to match your Postgres enum.
VisibilityEnum = PGEnum("private", "public", "org", name="visibility", create_type=False)

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

    # Added explicit relationships with back_populates
    chunks = relationship("ResearchChunk", back_populates="deep_research", cascade="all, delete-orphan")
    summaries = relationship("ResearchSummary", back_populates="deep_research", cascade="all, delete-orphan")
    sources = relationship("ResearchSource", back_populates="deep_research", cascade="all, delete-orphan")
    ratings = relationship("ResearchRating", back_populates="deep_research")
    comments = relationship("ResearchComment", back_populates="deep_research")
    auto_metadata = relationship("ResearchAutoMetadata", back_populates="deep_research")
    research_job = relationship("ResearchJob", back_populates="deep_research", foreign_keys="ResearchJob.deep_research_id")

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

    deep_research = relationship("DeepResearch", back_populates="chunks")

# 7) research_summaries
class ResearchSummary(Base):
    __tablename__ = "research_summaries"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    summary_scope = Column(String(50), nullable=False)
    summary_length = Column(String(50), nullable=False)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    deep_research = relationship("DeepResearch", back_populates="summaries")

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

    deep_research = relationship("DeepResearch", back_populates="sources")

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

    deep_research = relationship("DeepResearch", back_populates="ratings")
    user = relationship("User", back_populates="research_ratings")

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

    deep_research = relationship("DeepResearch", back_populates="comments")
    user = relationship("User", back_populates="comments")

# 14) research_auto_metadata
class ResearchAutoMetadata(Base):
    __tablename__ = "research_auto_metadata"

    id = Column(Integer, primary_key=True)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="CASCADE"), nullable=False)
    meta_key = Column(String(100), nullable=False)
    meta_value = Column(Text, nullable=False)
    confidence_score = Column(Integer)  # or Float
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())

    deep_research = relationship("DeepResearch", back_populates="auto_metadata")

# 15) research_jobs
class ResearchJob(Base):
    __tablename__ = "research_jobs"

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    owner_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    visibility = Column(VisibilityEnum, nullable=False, server_default="private")
    status = Column(String(50), nullable=False)
    service = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_params = Column(JSONB)
    deep_research_id = Column(Integer, ForeignKey("deep_research.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=False), server_default=sql_func.now())
    updated_at = Column(DateTime(timezone=False), server_default=sql_func.now(), onupdate=sql_func.now())

    __table_args__ = (
        CheckConstraint("""
            status IN ('pending_answers', 'running', 'completed', 'failed', 'cancelled')
        """, name="chk_research_job_status"),
        UniqueConstraint("job_id", "service", name="uq_research_job_job_id_service"),
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="research_jobs")
    deep_research = relationship("DeepResearch", foreign_keys=[deep_research_id], back_populates="research_job")
    organization = relationship("Organization", foreign_keys=[owner_org_id], back_populates="research_jobs")

# 16) research_services
class ResearchService(Base):
    """
    Model for research services like "open-dr"
    Stores the main service information
    """
    __tablename__ = "research_services"
    
    id = Column(Integer, primary_key=True)
    service_key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(255))
    default_model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=True)
    created_at = Column(String, server_default=func.now())
    updated_at = Column(String, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    default_model = relationship("AiModel", foreign_keys=[default_model_id], lazy="joined")
    models = relationship("AiModel", secondary="research_service_models", back_populates="services")
    service_models = relationship("ResearchServiceModel", back_populates="service", lazy='joined', 
                             innerjoin=False, join_depth=1, overlaps="models")

# 17) ai_models
class AiModel(Base):
    """
    Model for AI models with their specifications
    Can be used by multiple research services
    """
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True)
    model_key = Column(String(255), unique=True, nullable=False, index=True)
    default_params = Column(JSONB, nullable=False)
    max_tokens = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String, server_default=func.now())
    updated_at = Column(String, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    services = relationship("ResearchService", secondary="research_service_models", 
                            back_populates="models", 
                            overlaps="service_models")
    service_models = relationship("ResearchServiceModel", back_populates="model",
                                 overlaps="models,services")


# 18) research_service_models
class ResearchServiceModel(Base):
    """
    Linking table between Research Services and AI Models
    Allows for many-to-many relationship
    """
    __tablename__ = "research_service_models"
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("research_services.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(Integer, ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(String, server_default=func.now())
    updated_at = Column(String, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    service = relationship("ResearchService", back_populates="service_models",
                          overlaps="models,services")
    model = relationship("AiModel", back_populates="service_models",
                        overlaps="models,services")
    
    # Make sure each model is linked to a service only once
    __table_args__ = (
        UniqueConstraint("service_id", "model_id", name="uq_service_model"),
    )
    