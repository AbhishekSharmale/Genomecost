#!/usr/bin/env python3
"""
GenomeCostTracker Demo Data Generator
Generates realistic sample data for demonstration purposes
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

class GenomicsDataGenerator:
    def __init__(self):
        self.projects = [
            "Cancer Genomics Study",
            "Rare Disease Research",
            "Population Genetics",
            "Pharmacogenomics",
            "Microbiome Analysis",
            "Agricultural Genomics"
        ]
        
        self.pipeline_types = [
            "WGS", "RNA-seq", "ChIP-seq", "ATAC-seq", 
            "scRNA-seq", "Exome-seq", "Methylation"
        ]
        
        self.users = [
            "researcher@lab.com",
            "analyst@biotech.com", 
            "scientist@university.edu",
            "bioinformatician@hospital.org",
            "postdoc@institute.gov"
        ]
        
        self.workflows = [
            "nf-core/rnaseq",
            "nf-core/sarek",
            "nf-core/chipseq",
            "nf-core/atacseq",
            "nf-core/scrnaseq",
            "custom/wgs-pipeline"
        ]

    def generate_sample_id(self) -> str:
        """Generate realistic sample ID"""
        prefixes = ["SAMPLE", "TCGA", "GTEX", "HG", "NA", "GM"]
        return f"{random.choice(prefixes)}_{random.randint(10000, 99999)}"

    def generate_job_id(self) -> str:
        """Generate Nextflow-style job ID"""
        adjectives = ["amazing", "clever", "dreamy", "elegant", "focused", "gentle"]
        nouns = ["darwin", "mendel", "watson", "crick", "franklin", "mcclintock"]
        return f"{random.choice(adjectives)}_{random.choice(nouns)}"

    def estimate_cost_by_pipeline(self, pipeline_type: str, runtime_hours: float) -> Dict:
        """Estimate costs based on pipeline type and runtime"""
        
        # Base costs per hour for different resource types
        compute_cost_per_hour = {
            "WGS": 12.50,
            "RNA-seq": 8.75,
            "ChIP-seq": 6.25,
            "ATAC-seq": 5.50,
            "scRNA-seq": 15.00,
            "Exome-seq": 7.80,
            "Methylation": 9.20
        }
        
        storage_cost_base = {
            "WGS": 45.00,
            "RNA-seq": 18.50,
            "ChIP-seq": 12.00,
            "ATAC-seq": 8.50,
            "scRNA-seq": 25.00,
            "Exome-seq": 15.00,
            "Methylation": 20.00
        }
        
        network_cost_base = {
            "WGS": 8.50,
            "RNA-seq": 4.20,
            "ChIP-seq": 2.80,
            "ATAC-seq": 2.10,
            "scRNA-seq": 6.50,
            "Exome-seq": 3.50,
            "Methylation": 4.80
        }
        
        compute_cost = compute_cost_per_hour.get(pipeline_type, 8.00) * runtime_hours
        storage_cost = storage_cost_base.get(pipeline_type, 15.00)
        network_cost = network_cost_base.get(pipeline_type, 3.00)
        
        # Add some randomness
        compute_cost *= random.uniform(0.85, 1.15)
        storage_cost *= random.uniform(0.90, 1.10)
        network_cost *= random.uniform(0.80, 1.20)
        
        total_cost = compute_cost + storage_cost + network_cost
        
        return {
            "compute_cost": round(compute_cost, 2),
            "storage_cost": round(storage_cost, 2),
            "network_cost": round(network_cost, 2),
            "total_cost": round(total_cost, 2)
        }

    def generate_genomics_jobs(self, count: int = 50) -> List[Dict]:
        """Generate sample genomics jobs"""
        jobs = []
        
        for i in range(count):
            pipeline_type = random.choice(self.pipeline_types)
            project_name = random.choice(self.projects)
            user_email = random.choice(self.users)
            workflow_name = random.choice(self.workflows)
            
            # Generate realistic runtime based on pipeline type
            runtime_ranges = {
                "WGS": (8, 24),
                "RNA-seq": (3, 12),
                "ChIP-seq": (2, 8),
                "ATAC-seq": (1, 6),
                "scRNA-seq": (4, 16),
                "Exome-seq": (4, 10),
                "Methylation": (6, 14)
            }
            
            min_hours, max_hours = runtime_ranges.get(pipeline_type, (2, 8))
            estimated_runtime = round(random.uniform(min_hours, max_hours), 1)
            actual_runtime = round(estimated_runtime * random.uniform(0.8, 1.2), 1)
            
            # Generate timestamps
            start_time = datetime.now() - timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            status = random.choices(
                ["completed", "running", "failed", "cancelled"],
                weights=[70, 20, 8, 2]
            )[0]
            
            completed_time = None
            if status == "completed":
                completed_time = start_time + timedelta(hours=actual_runtime)
            elif status == "failed":
                completed_time = start_time + timedelta(hours=actual_runtime * 0.6)
            
            # Calculate costs
            cost_info = self.estimate_cost_by_pipeline(pipeline_type, actual_runtime if status == "completed" else estimated_runtime)
            
            job = {
                "id": i + 1,
                "job_id": self.generate_job_id(),
                "workflow_name": workflow_name,
                "sample_id": self.generate_sample_id(),
                "project_name": project_name,
                "user_email": user_email,
                "pipeline_type": pipeline_type,
                "status": status,
                "started_at": start_time.isoformat() + "Z",
                "completed_at": completed_time.isoformat() + "Z" if completed_time else None,
                "estimated_cost": cost_info["total_cost"],
                "actual_cost": cost_info["total_cost"] if status == "completed" else 0.0,
                "estimated_runtime_hours": estimated_runtime,
                "actual_runtime_hours": actual_runtime if status == "completed" else None,
                "progress_percentage": 100 if status == "completed" else (
                    0 if status == "failed" else random.randint(10, 90)
                ),
                "azure_resource_group": "genomics-rg",
                "azure_batch_pool_id": "genomics-pool",
                "cost_breakdown": {
                    "compute_cost": cost_info["compute_cost"],
                    "storage_cost": cost_info["storage_cost"],
                    "network_cost": cost_info["network_cost"]
                }
            }
            
            jobs.append(job)
        
        return jobs

    def generate_cost_trends(self, days: int = 30) -> List[Dict]:
        """Generate daily cost trend data"""
        trends = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Simulate weekly patterns (higher usage mid-week)
            day_of_week = date.weekday()
            weekly_multiplier = 1.0
            if day_of_week in [1, 2, 3]:  # Tue, Wed, Thu
                weekly_multiplier = 1.3
            elif day_of_week in [5, 6]:  # Sat, Sun
                weekly_multiplier = 0.6
            
            # Base costs with some randomness and growth trend
            base_total = 85.0 + (i * 1.2) + random.uniform(-15, 25)
            base_total *= weekly_multiplier
            
            compute_cost = base_total * random.uniform(0.65, 0.75)
            storage_cost = base_total * random.uniform(0.15, 0.25)
            network_cost = base_total * random.uniform(0.08, 0.15)
            
            # Job count correlation with costs
            job_count = max(1, int((base_total / 20) + random.uniform(-2, 3)))
            
            trend = {
                "date": date.strftime("%Y-%m-%d"),
                "total_cost": round(base_total, 2),
                "compute_cost": round(compute_cost, 2),
                "storage_cost": round(storage_cost, 2),
                "network_cost": round(network_cost, 2),
                "job_count": job_count
            }
            
            trends.append(trend)
        
        return trends

    def generate_budget_alerts(self) -> List[Dict]:
        """Generate sample budget alerts"""
        alerts = []
        
        alert_templates = [
            {
                "name": "Monthly Project Budget - Cancer Genomics",
                "alert_type": "project",
                "threshold_amount": 2000.0,
                "current_amount": 1650.0,
                "project_name": "Cancer Genomics Study",
                "severity": "warning"
            },
            {
                "name": "User Spending Alert - researcher@lab.com",
                "alert_type": "user",
                "threshold_amount": 500.0,
                "current_amount": 520.0,
                "user_email": "researcher@lab.com",
                "severity": "error"
            },
            {
                "name": "Daily Spending Limit",
                "alert_type": "total",
                "threshold_amount": 200.0,
                "current_amount": 185.0,
                "severity": "warning"
            }
        ]
        
        for i, template in enumerate(alert_templates):
            alert = {
                "id": i + 1,
                "name": template["name"],
                "alert_type": template["alert_type"],
                "threshold_amount": template["threshold_amount"],
                "current_amount": template["current_amount"],
                "threshold_percentage": 80.0,
                "project_name": template.get("project_name"),
                "user_email": template.get("user_email"),
                "is_active": True,
                "last_triggered": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat() + "Z"
            }
            alerts.append(alert)
        
        return alerts

    def generate_optimization_recommendations(self) -> List[Dict]:
        """Generate cost optimization recommendations"""
        recommendations = [
            {
                "id": 1,
                "title": "Switch to Low-Priority VMs for RNA-seq Workflows",
                "description": "Your RNA-seq workflows can use low-priority VMs to reduce compute costs by up to 80%. These workflows are typically fault-tolerant and can handle interruptions.",
                "recommendation_type": "compute",
                "potential_savings": 450.25,
                "confidence_score": 0.92,
                "project_name": "Cancer Genomics Study",
                "status": "pending"
            },
            {
                "id": 2,
                "title": "Archive Old Analysis Results",
                "description": "Move analysis results older than 90 days to Archive storage tier. This can reduce storage costs by 70% for long-term data retention.",
                "recommendation_type": "storage",
                "potential_savings": 125.80,
                "confidence_score": 0.87,
                "project_name": None,
                "status": "pending"
            },
            {
                "id": 3,
                "title": "Optimize Batch Pool Auto-scaling",
                "description": "Adjust your batch pool auto-scaling formula to reduce idle time. Current analysis shows 15% idle capacity during off-peak hours.",
                "recommendation_type": "compute",
                "potential_savings": 89.50,
                "confidence_score": 0.78,
                "project_name": None,
                "status": "pending"
            },
            {
                "id": 4,
                "title": "Use Spot Instances for Development Workflows",
                "description": "Development and testing workflows can use Azure Spot VMs for significant cost savings. Consider implementing checkpointing for fault tolerance.",
                "recommendation_type": "compute",
                "potential_savings": 234.75,
                "confidence_score": 0.85,
                "project_name": "Population Genetics",
                "status": "implemented"
            }
        ]
        
        return recommendations

    def generate_dashboard_overview(self, jobs: List[Dict], trends: List[Dict]) -> Dict:
        """Generate dashboard overview data"""
        
        # Calculate metrics from jobs
        running_jobs = [j for j in jobs if j["status"] == "running"]
        completed_jobs = [j for j in jobs if j["status"] == "completed"]
        
        total_cost_this_month = sum(t["total_cost"] for t in trends[-30:]) if trends else 0
        
        # Calculate average cost per sample
        completed_costs = [j["actual_cost"] for j in completed_jobs if j["actual_cost"] > 0]
        avg_cost_per_sample = sum(completed_costs) / len(completed_costs) if completed_costs else 0
        
        # Calculate cost trend percentage (last 7 days vs previous 7 days)
        if len(trends) >= 14:
            recent_avg = sum(t["total_cost"] for t in trends[-7:]) / 7
            previous_avg = sum(t["total_cost"] for t in trends[-14:-7]) / 7
            cost_trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100 if previous_avg > 0 else 0
        else:
            cost_trend_percentage = 5.2  # Default value
        
        # Top projects by cost
        project_costs = {}
        project_samples = {}
        
        for job in completed_jobs:
            project = job["project_name"]
            if project not in project_costs:
                project_costs[project] = 0
                project_samples[project] = 0
            project_costs[project] += job["actual_cost"]
            project_samples[project] += 1
        
        top_projects = [
            {
                "name": project,
                "cost": cost,
                "samples": project_samples[project]
            }
            for project, cost in sorted(project_costs.items(), key=lambda x: x[1], reverse=True)[:3]
        ]
        
        # Recent alerts
        project_name = top_projects[0]["name"] if top_projects else "Cancer Genomics"
        recent_alerts = [
            {
                "id": 1,
                "type": "budget_exceeded",
                "message": f"Project '{project_name}' exceeded 80% of monthly budget",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat() + "Z",
                "severity": "warning"
            }
        ]
        
        overview = {
            "total_cost_this_month": round(sum(t["total_cost"] for t in trends[-30:]) if len(trends) >= 30 else sum(t["total_cost"] for t in trends), 2),
            "total_jobs_running": len(running_jobs),
            "total_jobs_completed": len(completed_jobs),
            "average_cost_per_sample": round(avg_cost_per_sample, 2),
            "cost_trend_percentage": round(cost_trend_percentage, 1),
            "top_projects": top_projects,
            "recent_alerts": recent_alerts
        }
        
        return overview

    def generate_all_demo_data(self) -> Dict:
        """Generate complete demo dataset"""
        print("Generating genomics jobs...")
        jobs = self.generate_genomics_jobs(75)
        
        print("Generating cost trends...")
        trends = self.generate_cost_trends(45)
        
        print("Generating budget alerts...")
        alerts = self.generate_budget_alerts()
        
        print("Generating optimization recommendations...")
        recommendations = self.generate_optimization_recommendations()
        
        print("Generating dashboard overview...")
        overview = self.generate_dashboard_overview(jobs, trends)
        
        return {
            "jobs": jobs,
            "cost_trends": trends,
            "budget_alerts": alerts,
            "optimization_recommendations": recommendations,
            "dashboard_overview": overview,
            "metadata": {
                "generated_at": datetime.now().isoformat() + "Z",
                "total_jobs": len(jobs),
                "date_range": f"{trends[0]['date']} to {trends[-1]['date']}" if trends else "N/A",
                "generator_version": "1.0.0"
            }
        }

def main():
    """Main function to generate and save demo data"""
    generator = GenomicsDataGenerator()
    
    print("GenomeCostTracker Demo Data Generator")
    print("=" * 40)
    
    # Generate all demo data
    demo_data = generator.generate_all_demo_data()
    
    # Save to JSON file
    output_file = "demo_data.json"
    with open(output_file, 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print(f"\nDemo data generated successfully!")
    print(f"Saved to: {output_file}")
    print(f"Generated {demo_data['metadata']['total_jobs']} jobs")
    print(f"Cost trends for {len(demo_data['cost_trends'])} days")
    print(f"{len(demo_data['budget_alerts'])} budget alerts")
    print(f"{len(demo_data['optimization_recommendations'])} optimization recommendations")
    
    # Print summary statistics
    total_cost = sum(job["actual_cost"] for job in demo_data["jobs"] if job["status"] == "completed")
    avg_cost = total_cost / len([j for j in demo_data["jobs"] if j["status"] == "completed"]) if demo_data["jobs"] else 0
    
    print(f"\nSummary Statistics:")
    print(f"   Total completed cost: ${total_cost:,.2f}")
    print(f"   Average cost per job: ${avg_cost:.2f}")
    print(f"   Most expensive pipeline: {max(demo_data['jobs'], key=lambda x: x['estimated_cost'])['pipeline_type']}")
    
    print(f"\nReady to use with GenomeCostTracker!")

if __name__ == "__main__":
    main()