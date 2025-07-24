from azure.identity import ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.batch import BatchManagementClient
from datetime import datetime, timedelta
import asyncio
import httpx
from typing import Dict, List, Optional
import json

from ..config.settings import settings
from ..models.database import GenomicsJob, CostData, AzureConnection

class AzureCostService:
    def __init__(self, azure_connection: AzureConnection):
        self.connection = azure_connection
        self.credential = ClientSecretCredential(
            tenant_id=azure_connection.tenant_id,
            client_id=azure_connection.client_id,
            client_secret=azure_connection.client_secret
        )
        
        self.cost_client = CostManagementClient(
            credential=self.credential,
            subscription_id=azure_connection.subscription_id
        )
        
        self.resource_client = ResourceManagementClient(
            credential=self.credential,
            subscription_id=azure_connection.subscription_id
        )
        
        self.batch_client = BatchManagementClient(
            credential=self.credential,
            subscription_id=azure_connection.subscription_id
        )

    async def get_cost_data(self, start_date: datetime, end_date: datetime, 
                           resource_group: Optional[str] = None) -> List[Dict]:
        """Fetch cost data from Azure Cost Management API"""
        
        # Build query parameters
        query_definition = {
            "type": "ActualCost",
            "timeframe": "Custom",
            "timePeriod": {
                "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
            },
            "dataset": {
                "granularity": "Daily",
                "aggregation": {
                    "totalCost": {
                        "name": "PreTaxCost",
                        "function": "Sum"
                    }
                },
                "grouping": [
                    {
                        "type": "Dimension",
                        "name": "ResourceId"
                    },
                    {
                        "type": "Dimension", 
                        "name": "ServiceName"
                    },
                    {
                        "type": "TagKey",
                        "name": "sample_id"
                    },
                    {
                        "type": "TagKey",
                        "name": "project"
                    },
                    {
                        "type": "TagKey",
                        "name": "workflow_type"
                    },
                    {
                        "type": "TagKey",
                        "name": "user"
                    }
                ]
            }
        }
        
        # Add resource group filter if specified
        if resource_group:
            query_definition["dataset"]["filter"] = {
                "dimensions": {
                    "name": "ResourceGroupName",
                    "operator": "In",
                    "values": [resource_group]
                }
            }
        
        # Execute query
        scope = f"/subscriptions/{self.connection.subscription_id}"
        if resource_group:
            scope += f"/resourceGroups/{resource_group}"
            
        try:
            result = self.cost_client.query.usage(scope=scope, parameters=query_definition)
            return self._parse_cost_response(result)
        except Exception as e:
            print(f"Error fetching cost data: {e}")
            return []

    def _parse_cost_response(self, response) -> List[Dict]:
        """Parse Azure Cost Management API response"""
        cost_data = []
        
        if hasattr(response, 'rows') and response.rows:
            columns = [col.name for col in response.columns]
            
            for row in response.rows:
                row_dict = dict(zip(columns, row))
                
                cost_entry = {
                    "resource_id": row_dict.get("ResourceId", ""),
                    "service_name": row_dict.get("ServiceName", ""),
                    "cost_amount": float(row_dict.get("PreTaxCost", 0)),
                    "currency": row_dict.get("Currency", "USD"),
                    "usage_date": row_dict.get("UsageDate", ""),
                    "sample_id": row_dict.get("sample_id", ""),
                    "project": row_dict.get("project", ""),
                    "workflow_type": row_dict.get("workflow_type", ""),
                    "user": row_dict.get("user", "")
                }
                cost_data.append(cost_entry)
        
        return cost_data

    async def estimate_job_cost(self, job: GenomicsJob) -> float:
        """Estimate cost for a genomics job before completion"""
        
        estimated_cost = 0.0
        
        # Compute cost estimation (Azure Batch)
        if job.estimated_runtime_hours:
            # Get current batch pool info
            batch_cost = await self._estimate_batch_cost(
                job.azure_batch_pool_id, 
                job.estimated_runtime_hours
            )
            estimated_cost += batch_cost
        
        # Storage cost estimation
        storage_cost = await self._estimate_storage_cost(job)
        estimated_cost += storage_cost
        
        # Network cost estimation  
        network_cost = await self._estimate_network_cost(job)
        estimated_cost += network_cost
        
        return round(estimated_cost, 2)

    async def _estimate_batch_cost(self, pool_id: Optional[str], runtime_hours: float) -> float:
        """Estimate Azure Batch compute costs"""
        
        if not pool_id:
            # Use default pricing for Standard_D2s_v3
            return runtime_hours * settings.AZURE_BATCH_COST_PER_HOUR
        
        try:
            # Get actual pool configuration
            pools = self.batch_client.pool.list()
            for pool in pools:
                if pool.id == pool_id:
                    vm_size = pool.vm_size
                    target_dedicated_nodes = pool.target_dedicated_nodes or 0
                    target_low_priority_nodes = pool.target_low_priority_nodes or 0
                    
                    # Calculate cost based on VM size and node count
                    dedicated_cost = target_dedicated_nodes * runtime_hours * self._get_vm_cost_per_hour(vm_size)
                    low_priority_cost = target_low_priority_nodes * runtime_hours * self._get_vm_cost_per_hour(vm_size, low_priority=True)
                    
                    return dedicated_cost + low_priority_cost
        except Exception as e:
            print(f"Error estimating batch cost: {e}")
        
        # Fallback to default pricing
        return runtime_hours * settings.AZURE_BATCH_COST_PER_HOUR

    def _get_vm_cost_per_hour(self, vm_size: str, low_priority: bool = False) -> float:
        """Get VM cost per hour based on size"""
        
        # Simplified pricing model - in production, use Azure Pricing API
        vm_pricing = {
            "Standard_D2s_v3": 0.096,
            "Standard_D4s_v3": 0.192,
            "Standard_D8s_v3": 0.384,
            "Standard_D16s_v3": 0.768,
            "Standard_F4s_v2": 0.169,
            "Standard_F8s_v2": 0.338,
            "Standard_F16s_v2": 0.676
        }
        
        base_cost = vm_pricing.get(vm_size, 0.096)  # Default to D2s_v3
        
        if low_priority:
            return base_cost * 0.2  # Low-priority is ~80% cheaper
        
        return base_cost

    async def _estimate_storage_cost(self, job: GenomicsJob) -> float:
        """Estimate Azure Storage costs"""
        
        # Estimate based on typical genomics data sizes
        workflow_storage_estimates = {
            "WGS": 200,  # GB for whole genome sequencing
            "RNA-seq": 50,  # GB for RNA sequencing
            "ChIP-seq": 20,  # GB for ChIP sequencing
            "ATAC-seq": 15,  # GB for ATAC sequencing
        }
        
        estimated_gb = workflow_storage_estimates.get(job.pipeline_type, 100)
        
        # Assume 30 days retention in hot storage, then move to cool
        hot_storage_cost = estimated_gb * settings.AZURE_STORAGE_HOT_COST_PER_GB * 30
        cool_storage_cost = estimated_gb * settings.AZURE_STORAGE_COOL_COST_PER_GB * 335  # Rest of year
        
        return hot_storage_cost + cool_storage_cost

    async def _estimate_network_cost(self, job: GenomicsJob) -> float:
        """Estimate Azure network/data transfer costs"""
        
        # Estimate based on typical data movement patterns
        workflow_network_estimates = {
            "WGS": 50,   # GB data transfer
            "RNA-seq": 20,
            "ChIP-seq": 10,
            "ATAC-seq": 8,
        }
        
        estimated_transfer_gb = workflow_network_estimates.get(job.pipeline_type, 25)
        return estimated_transfer_gb * settings.AZURE_NETWORK_COST_PER_GB

    async def tag_resources_for_job(self, job: GenomicsJob, resource_group: str) -> bool:
        """Tag Azure resources for cost attribution"""
        
        tags = {
            "sample_id": job.sample_id,
            "project": job.project_name,
            "workflow_type": job.pipeline_type,
            "user": job.user_email,
            "job_id": job.job_id,
            "created_by": "GenomeCostTracker"
        }
        
        try:
            # Get all resources in the resource group
            resources = self.resource_client.resources.list_by_resource_group(resource_group)
            
            tagged_count = 0
            for resource in resources:
                try:
                    # Update resource tags
                    existing_tags = resource.tags or {}
                    existing_tags.update(tags)
                    
                    # Apply tags to resource
                    self.resource_client.resources.update_by_id(
                        resource_id=resource.id,
                        api_version="2021-04-01",
                        parameters={
                            "tags": existing_tags
                        }
                    )
                    tagged_count += 1
                    
                except Exception as e:
                    print(f"Error tagging resource {resource.id}: {e}")
            
            print(f"Successfully tagged {tagged_count} resources for job {job.job_id}")
            return tagged_count > 0
            
        except Exception as e:
            print(f"Error tagging resources: {e}")
            return False

    async def get_batch_job_metrics(self, job_id: str, pool_id: str) -> Dict:
        """Get real-time metrics from Azure Batch job"""
        
        try:
            # This would integrate with Azure Batch API to get job metrics
            # For now, return mock data
            return {
                "status": "running",
                "progress_percentage": 65,
                "active_nodes": 4,
                "running_tasks": 12,
                "completed_tasks": 45,
                "failed_tasks": 1,
                "estimated_completion": "2024-01-15T14:30:00Z"
            }
        except Exception as e:
            print(f"Error getting batch job metrics: {e}")
            return {}

# Cost reconciliation service
class CostReconciliationService:
    def __init__(self, azure_service: AzureCostService):
        self.azure_service = azure_service

    async def reconcile_job_costs(self, job: GenomicsJob, db_session) -> Dict:
        """Reconcile estimated costs with actual Azure costs"""
        
        if not job.completed_at:
            return {"status": "job_not_completed"}
        
        # Get actual costs from Azure (with 24-48h delay)
        end_date = job.completed_at + timedelta(days=2)  # Account for billing delay
        start_date = job.started_at - timedelta(hours=1)  # Buffer for job start
        
        actual_costs = await self.azure_service.get_cost_data(
            start_date=start_date,
            end_date=end_date,
            resource_group=job.azure_resource_group
        )
        
        # Filter costs for this specific job
        job_costs = [
            cost for cost in actual_costs 
            if cost.get("sample_id") == job.sample_id
        ]
        
        total_actual_cost = sum(cost["cost_amount"] for cost in job_costs)
        
        # Update job with actual cost
        job.actual_cost = total_actual_cost
        job.cost_last_updated = datetime.utcnow()
        
        # Calculate accuracy metrics
        if job.estimated_cost > 0:
            accuracy_percentage = (1 - abs(total_actual_cost - job.estimated_cost) / job.estimated_cost) * 100
        else:
            accuracy_percentage = 0
        
        # Store detailed cost data
        for cost in job_costs:
            cost_record = CostData(
                genomics_job_id=job.id,
                resource_id=cost["resource_id"],
                resource_type=self._extract_resource_type(cost["resource_id"]),
                service_name=cost["service_name"],
                cost_amount=cost["cost_amount"],
                currency=cost["currency"],
                billing_period=cost["usage_date"][:10],
                usage_date=datetime.fromisoformat(cost["usage_date"].replace("Z", "+00:00")),
                sample_id=cost["sample_id"],
                project_name=cost["project"],
                user_email=cost["user"],
                azure_tags=cost
            )
            db_session.add(cost_record)
        
        db_session.commit()
        
        return {
            "status": "reconciled",
            "estimated_cost": job.estimated_cost,
            "actual_cost": total_actual_cost,
            "accuracy_percentage": accuracy_percentage,
            "cost_variance": total_actual_cost - job.estimated_cost
        }

    def _extract_resource_type(self, resource_id: str) -> str:
        """Extract resource type from Azure resource ID"""
        
        if "/batchAccounts/" in resource_id:
            return "Batch"
        elif "/storageAccounts/" in resource_id:
            return "Storage"
        elif "/networkInterfaces/" in resource_id:
            return "Network"
        elif "/virtualMachines/" in resource_id:
            return "Compute"
        else:
            return "Other"