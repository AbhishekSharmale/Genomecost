from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: str
    name: str
    organization: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Job schemas
class CreateJobRequest(BaseModel):
    job_id: str
    workflow_name: str
    sample_id: str
    project_name: str
    pipeline_type: str  # WGS, RNA-seq, ChIP-seq, etc.
    azure_resource_group: str
    azure_batch_pool_id: Optional[str] = None
    estimated_runtime_hours: Optional[float] = None
    nextflow_config: Optional[Dict[str, Any]] = None

class GenomicsJobResponse(BaseModel):
    id: int
    job_id: str
    workflow_name: str
    sample_id: str
    project_name: str
    user_email: str
    pipeline_type: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    estimated_cost: float
    actual_cost: float
    estimated_runtime_hours: Optional[float] = None
    actual_runtime_hours: Optional[float] = None
    progress_percentage: int

# Dashboard schemas
class ProjectSummary(BaseModel):
    name: str
    cost: float
    samples: int

class AlertSummary(BaseModel):
    id: int
    type: str
    message: str
    timestamp: str
    severity: str

class DashboardOverview(BaseModel):
    total_cost_this_month: float
    total_jobs_running: int
    total_jobs_completed: int
    average_cost_per_sample: float
    cost_trend_percentage: float
    top_projects: List[ProjectSummary]
    recent_alerts: List[AlertSummary]

class CostTrendData(BaseModel):
    date: str
    total_cost: float
    compute_cost: float
    storage_cost: float
    network_cost: float
    job_count: int

# Cost breakdown schemas
class CostBreakdownItem(BaseModel):
    resource_type: str
    cost: float
    percentage: float

class DailyCost(BaseModel):
    date: str
    cost: float

class JobCostBreakdown(BaseModel):
    job_id: str
    total_cost: float
    breakdown: List[CostBreakdownItem]
    daily_costs: List[DailyCost]

# Budget alert schemas
class CreateAlertRequest(BaseModel):
    name: str
    alert_type: str  # project, sample, user, total
    threshold_amount: float
    threshold_percentage: Optional[float] = None
    time_period: str = "monthly"  # daily, weekly, monthly
    project_name: Optional[str] = None
    user_email: Optional[str] = None

class BudgetAlertResponse(BaseModel):
    id: int
    name: str
    alert_type: str
    threshold_amount: float
    current_amount: float
    threshold_percentage: Optional[float] = None
    project_name: Optional[str] = None
    user_email: Optional[str] = None
    is_active: bool
    last_triggered: Optional[str] = None

# Optimization recommendation schemas
class OptimizationRecommendationResponse(BaseModel):
    id: int
    title: str
    description: str
    recommendation_type: str  # storage, compute, network
    potential_savings: float
    confidence_score: float
    project_name: Optional[str] = None
    status: str  # pending, implemented, dismissed

# Azure connection schemas
class CreateAzureConnectionRequest(BaseModel):
    name: str
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_id: str

class AzureConnectionResponse(BaseModel):
    id: int
    name: str
    tenant_id: str
    client_id: str
    subscription_id: str
    is_active: bool
    created_at: str

# Nextflow integration schemas
class NextflowConfig(BaseModel):
    workflow_name: str
    revision: str
    params: Dict[str, Any]
    azure_config: Dict[str, Any]

class NextflowJobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    started_at: str
    estimated_completion: Optional[str] = None
    resource_usage: Dict[str, Any]

# Real-time update schemas
class CostUpdateMessage(BaseModel):
    type: str
    job_id: Optional[str] = None
    cost_change: Optional[float] = None
    timestamp: str
    data: Dict[str, Any]

# Analytics schemas
class CostAnalytics(BaseModel):
    period: str  # daily, weekly, monthly
    total_cost: float
    cost_by_project: Dict[str, float]
    cost_by_pipeline: Dict[str, float]
    cost_by_user: Dict[str, float]
    efficiency_metrics: Dict[str, float]

class SampleCostAnalysis(BaseModel):
    sample_id: str
    project_name: str
    pipeline_type: str
    total_cost: float
    cost_per_gb: float
    runtime_hours: float
    cost_efficiency_score: float
    comparison_to_average: float