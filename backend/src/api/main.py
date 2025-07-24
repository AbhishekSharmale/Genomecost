from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import asyncio

from ..config.settings import settings
from ..models.database import get_db, create_tables, GenomicsJob, CostData, BudgetAlert, OptimizationRecommendation
from ..services.azure_cost_service import AzureCostService, CostReconciliationService
from .schemas import *
from .auth import get_current_user, create_access_token

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Real-time cost monitoring for genomics workloads on Azure"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Startup event
@app.on_event("startup")
async def startup_event():
    create_tables()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication endpoints
@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Mock authentication - replace with real auth
    if credentials.email == "demo@genomecost.com" and credentials.password == "demo123":
        access_token = create_access_token(data={"sub": credentials.email})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": credentials.email,
                "name": "Demo User",
                "organization": "Demo Lab"
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Dashboard endpoints
@app.get("/api/v1/dashboard/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock data for demo - replace with real queries
    return {
        "total_cost_this_month": 2847.32,
        "total_jobs_running": 12,
        "total_jobs_completed": 156,
        "average_cost_per_sample": 18.25,
        "cost_trend_percentage": 8.5,
        "top_projects": [
            {"name": "Cancer Genomics", "cost": 1245.67, "samples": 68},
            {"name": "Rare Disease Study", "cost": 892.45, "samples": 49},
            {"name": "Population Genetics", "cost": 709.20, "samples": 39}
        ],
        "recent_alerts": [
            {
                "id": 1,
                "type": "budget_exceeded",
                "message": "Project 'Cancer Genomics' exceeded 80% of monthly budget",
                "timestamp": "2024-01-15T10:30:00Z",
                "severity": "warning"
            }
        ]
    }

@app.get("/api/v1/dashboard/cost-trends", response_model=List[CostTrendData])
async def get_cost_trends(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock data for demo
    base_date = datetime.now() - timedelta(days=days)
    trends = []
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "total_cost": 45.67 + (i * 2.3) + (i % 7 * 15.2),
            "compute_cost": 32.45 + (i * 1.8),
            "storage_cost": 8.92 + (i * 0.3),
            "network_cost": 4.30 + (i * 0.2),
            "job_count": 3 + (i % 5)
        })
    
    return trends

# Jobs endpoints
@app.get("/api/v1/jobs", response_model=List[GenomicsJobResponse])
async def get_jobs(
    status: Optional[str] = None,
    project: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock data for demo
    jobs = [
        {
            "id": 1,
            "job_id": "nf-core-rnaseq-001",
            "workflow_name": "nf-core/rnaseq",
            "sample_id": "SAMPLE_001",
            "project_name": "Cancer Genomics",
            "user_email": "researcher@lab.com",
            "pipeline_type": "RNA-seq",
            "status": "running",
            "started_at": "2024-01-15T08:30:00Z",
            "estimated_cost": 23.45,
            "actual_cost": 0.0,
            "estimated_runtime_hours": 4.5,
            "progress_percentage": 65
        },
        {
            "id": 2,
            "job_id": "nf-core-wgs-002",
            "workflow_name": "nf-core/sarek",
            "sample_id": "SAMPLE_002",
            "project_name": "Rare Disease Study",
            "user_email": "analyst@lab.com",
            "pipeline_type": "WGS",
            "status": "completed",
            "started_at": "2024-01-14T14:20:00Z",
            "completed_at": "2024-01-15T02:15:00Z",
            "estimated_cost": 89.32,
            "actual_cost": 92.18,
            "estimated_runtime_hours": 12.0,
            "actual_runtime_hours": 11.9,
            "progress_percentage": 100
        }
    ]
    
    # Filter by status if provided
    if status:
        jobs = [job for job in jobs if job["status"] == status]
    
    # Filter by project if provided
    if project:
        jobs = [job for job in jobs if job["project_name"] == project]
    
    return jobs[:limit]

@app.post("/api/v1/jobs", response_model=GenomicsJobResponse)
async def create_job(
    job_request: CreateJobRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create new genomics job
    job = GenomicsJob(
        organization_id=1,  # Mock organization
        job_id=job_request.job_id,
        workflow_name=job_request.workflow_name,
        sample_id=job_request.sample_id,
        project_name=job_request.project_name,
        user_email=current_user["email"],
        pipeline_type=job_request.pipeline_type,
        azure_resource_group=job_request.azure_resource_group,
        azure_batch_pool_id=job_request.azure_batch_pool_id,
        estimated_runtime_hours=job_request.estimated_runtime_hours,
        nextflow_config=job_request.nextflow_config
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Estimate cost
    # azure_service = AzureCostService(azure_connection)  # Would get from DB
    # estimated_cost = await azure_service.estimate_job_cost(job)
    # job.estimated_cost = estimated_cost
    job.estimated_cost = 45.67  # Mock for demo
    
    db.commit()
    
    # Broadcast job creation to WebSocket clients
    await manager.broadcast(json.dumps({
        "type": "job_created",
        "job_id": job.job_id,
        "estimated_cost": job.estimated_cost
    }))
    
    return {
        "id": job.id,
        "job_id": job.job_id,
        "workflow_name": job.workflow_name,
        "sample_id": job.sample_id,
        "project_name": job.project_name,
        "user_email": job.user_email,
        "pipeline_type": job.pipeline_type,
        "status": job.status,
        "started_at": job.started_at.isoformat() + "Z",
        "estimated_cost": job.estimated_cost,
        "actual_cost": job.actual_cost,
        "estimated_runtime_hours": job.estimated_runtime_hours,
        "progress_percentage": 0
    }

@app.get("/api/v1/jobs/{job_id}/cost-breakdown", response_model=JobCostBreakdown)
async def get_job_cost_breakdown(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock cost breakdown data
    return {
        "job_id": job_id,
        "total_cost": 92.18,
        "breakdown": [
            {"resource_type": "Compute", "cost": 67.45, "percentage": 73.2},
            {"resource_type": "Storage", "cost": 18.92, "percentage": 20.5},
            {"resource_type": "Network", "cost": 5.81, "percentage": 6.3}
        ],
        "daily_costs": [
            {"date": "2024-01-14", "cost": 45.32},
            {"date": "2024-01-15", "cost": 46.86}
        ]
    }

# Budget alerts endpoints
@app.get("/api/v1/alerts", response_model=List[BudgetAlertResponse])
async def get_alerts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock alerts data
    return [
        {
            "id": 1,
            "name": "Monthly Project Budget",
            "alert_type": "project",
            "threshold_amount": 1000.0,
            "current_amount": 847.32,
            "threshold_percentage": 80.0,
            "project_name": "Cancer Genomics",
            "is_active": True,
            "last_triggered": "2024-01-15T10:30:00Z"
        }
    ]

@app.post("/api/v1/alerts", response_model=BudgetAlertResponse)
async def create_alert(
    alert_request: CreateAlertRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = BudgetAlert(
        organization_id=1,  # Mock organization
        name=alert_request.name,
        alert_type=alert_request.alert_type,
        threshold_amount=alert_request.threshold_amount,
        threshold_percentage=alert_request.threshold_percentage,
        time_period=alert_request.time_period,
        project_name=alert_request.project_name,
        user_email=alert_request.user_email
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return {
        "id": alert.id,
        "name": alert.name,
        "alert_type": alert.alert_type,
        "threshold_amount": alert.threshold_amount,
        "current_amount": 0.0,
        "threshold_percentage": alert.threshold_percentage,
        "project_name": alert.project_name,
        "user_email": alert.user_email,
        "is_active": alert.is_active,
        "last_triggered": alert.last_triggered.isoformat() + "Z" if alert.last_triggered else None
    }

# Optimization recommendations
@app.get("/api/v1/recommendations", response_model=List[OptimizationRecommendationResponse])
async def get_recommendations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mock recommendations
    return [
        {
            "id": 1,
            "title": "Switch to Low-Priority VMs",
            "description": "Use low-priority VMs for non-urgent RNA-seq workflows to save up to 80% on compute costs",
            "recommendation_type": "compute",
            "potential_savings": 234.56,
            "confidence_score": 0.92,
            "project_name": "Cancer Genomics",
            "status": "pending"
        },
        {
            "id": 2,
            "title": "Archive Old Data",
            "description": "Move data older than 90 days to Archive storage tier",
            "recommendation_type": "storage",
            "potential_savings": 89.23,
            "confidence_score": 0.87,
            "project_name": None,
            "status": "pending"
        }
    ]

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({
                "type": "cost_update",
                "timestamp": datetime.utcnow().isoformat(),
                "total_cost": 2847.32,
                "active_jobs": 12
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task for cost reconciliation
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(cost_reconciliation_task())

async def cost_reconciliation_task():
    """Background task to reconcile estimated costs with actual Azure costs"""
    while True:
        try:
            # This would run every 4 hours to check for new cost data
            print("Running cost reconciliation...")
            await asyncio.sleep(14400)  # 4 hours
        except Exception as e:
            print(f"Error in cost reconciliation: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)