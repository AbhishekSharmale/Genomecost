import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface DashboardOverview {
  total_cost_this_month: number;
  total_jobs_running: number;
  total_jobs_completed: number;
  average_cost_per_sample: number;
  cost_trend_percentage: number;
  top_projects: ProjectSummary[];
  recent_alerts: AlertSummary[];
}

export interface ProjectSummary {
  name: string;
  cost: number;
  samples: number;
}

export interface AlertSummary {
  id: number;
  type: string;
  message: string;
  timestamp: string;
  severity: string;
}

export interface GenomicsJob {
  id: number;
  job_id: string;
  workflow_name: string;
  sample_id: string;
  project_name: string;
  user_email: string;
  pipeline_type: string;
  status: string;
  started_at: string;
  completed_at?: string;
  estimated_cost: number;
  actual_cost: number;
  estimated_runtime_hours?: number;
  actual_runtime_hours?: number;
  progress_percentage: number;
}

export interface CostTrendData {
  date: string;
  total_cost: number;
  compute_cost: number;
  storage_cost: number;
  network_cost: number;
  job_count: number;
}

export interface BudgetAlert {
  id: number;
  name: string;
  alert_type: string;
  threshold_amount: number;
  current_amount: number;
  threshold_percentage?: number;
  project_name?: string;
  user_email?: string;
  is_active: boolean;
  last_triggered?: string;
}

export interface OptimizationRecommendation {
  id: number;
  title: string;
  description: string;
  recommendation_type: string;
  potential_savings: number;
  confidence_score: number;
  project_name?: string;
  status: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8000/api/v1';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  // Dashboard endpoints
  getDashboardOverview(): Observable<DashboardOverview> {
    return this.http.get<DashboardOverview>(`${this.apiUrl}/dashboard/overview`, {
      headers: this.getHeaders()
    });
  }

  getCostTrends(days: number = 30): Observable<CostTrendData[]> {
    return this.http.get<CostTrendData[]>(`${this.apiUrl}/dashboard/cost-trends?days=${days}`, {
      headers: this.getHeaders()
    });
  }

  // Jobs endpoints
  getJobs(status?: string, project?: string, limit: number = 50): Observable<GenomicsJob[]> {
    let url = `${this.apiUrl}/jobs?limit=${limit}`;
    if (status) url += `&status=${status}`;
    if (project) url += `&project=${project}`;
    
    return this.http.get<GenomicsJob[]>(url, {
      headers: this.getHeaders()
    });
  }

  createJob(jobData: any): Observable<GenomicsJob> {
    return this.http.post<GenomicsJob>(`${this.apiUrl}/jobs`, jobData, {
      headers: this.getHeaders()
    });
  }

  getJobCostBreakdown(jobId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/jobs/${jobId}/cost-breakdown`, {
      headers: this.getHeaders()
    });
  }

  // Budget alerts endpoints
  getAlerts(): Observable<BudgetAlert[]> {
    return this.http.get<BudgetAlert[]>(`${this.apiUrl}/alerts`, {
      headers: this.getHeaders()
    });
  }

  createAlert(alertData: any): Observable<BudgetAlert> {
    return this.http.post<BudgetAlert>(`${this.apiUrl}/alerts`, alertData, {
      headers: this.getHeaders()
    });
  }

  // Optimization recommendations
  getRecommendations(): Observable<OptimizationRecommendation[]> {
    return this.http.get<OptimizationRecommendation[]>(`${this.apiUrl}/recommendations`, {
      headers: this.getHeaders()
    });
  }
}