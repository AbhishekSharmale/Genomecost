from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ..config.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subscription_tier = Column(String, default="starter")  # starter, professional, enterprise
    azure_spend_limit = Column(Float, default=10000.0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    azure_connections = relationship("AzureConnection", back_populates="organization")
    genomics_jobs = relationship("GenomicsJob", back_populates="organization")

class AzureConnection(Base):
    __tablename__ = "azure_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    tenant_id = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)  # Encrypted
    subscription_id = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="azure_connections")

class GenomicsJob(Base):
    __tablename__ = "genomics_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    job_id = Column(String, unique=True, nullable=False)  # Nextflow run ID
    workflow_name = Column(String, nullable=False)
    sample_id = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    pipeline_type = Column(String, nullable=False)  # WGS, RNA-seq, etc.
    
    # Job status
    status = Column(String, default="running")  # running, completed, failed, cancelled
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Resource information
    azure_resource_group = Column(String, nullable=False)
    azure_batch_pool_id = Column(String, nullable=True)
    estimated_runtime_hours = Column(Float, nullable=True)
    actual_runtime_hours = Column(Float, nullable=True)
    
    # Cost information
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    cost_last_updated = Column(DateTime, nullable=True)
    
    # Metadata
    nextflow_config = Column(JSON, nullable=True)
    resource_tags = Column(JSON, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="genomics_jobs")
    cost_data = relationship("CostData", back_populates="genomics_job")

class CostData(Base):
    __tablename__ = "cost_data"
    
    id = Column(Integer, primary_key=True, index=True)
    genomics_job_id = Column(Integer, ForeignKey("genomics_jobs.id"))
    
    # Azure cost details
    resource_id = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)  # Batch, Storage, Network, etc.
    service_name = Column(String, nullable=False)
    cost_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    billing_period = Column(String, nullable=False)  # YYYY-MM-DD
    usage_date = Column(DateTime, nullable=False)
    
    # Attribution
    sample_id = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    
    # Metadata
    azure_tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    genomics_job = relationship("GenomicsJob", back_populates="cost_data")

class BudgetAlert(Base):
    __tablename__ = "budget_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Alert configuration
    name = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)  # project, sample, user, total
    threshold_amount = Column(Float, nullable=False)
    threshold_percentage = Column(Float, nullable=True)
    time_period = Column(String, default="monthly")  # daily, weekly, monthly
    
    # Scope
    project_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

class OptimizationRecommendation(Base):
    __tablename__ = "optimization_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Recommendation details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recommendation_type = Column(String, nullable=False)  # storage, compute, network
    potential_savings = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Scope
    resource_type = Column(String, nullable=True)
    project_name = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, implemented, dismissed
    created_at = Column(DateTime, default=func.now())
    implemented_at = Column(DateTime, nullable=True)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()