import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { ApiService, DashboardOverview, CostTrendData } from '../../services/api.service';
import { WebSocketService } from '../../services/websocket.service';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  overview: DashboardOverview | null = null;
  costTrends: CostTrendData[] = [];
  loading = true;
  
  // Chart configurations
  public lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: [],
    datasets: [
      {
        data: [],
        label: 'Total Cost',
        fill: true,
        tension: 0.4,
        borderColor: '#3f51b5',
        backgroundColor: 'rgba(63, 81, 181, 0.1)',
        pointBackgroundColor: '#3f51b5',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3f51b5'
      },
      {
        data: [],
        label: 'Compute Cost',
        fill: false,
        tension: 0.4,
        borderColor: '#ff9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)'
      },
      {
        data: [],
        label: 'Storage Cost',
        fill: false,
        tension: 0.4,
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)'
      }
    ]
  };

  public lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date'
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Cost ($)'
        },
        beginAtZero: true
      }
    }
  };

  public lineChartType: ChartType = 'line';

  // Pie chart for cost breakdown
  public pieChartData: ChartConfiguration<'pie'>['data'] = {
    labels: ['Compute', 'Storage', 'Network'],
    datasets: [{
      data: [],
      backgroundColor: ['#3f51b5', '#4caf50', '#ff9800'],
      hoverBackgroundColor: ['#303f9f', '#388e3c', '#f57c00']
    }]
  };

  public pieChartOptions: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right'
      }
    }
  };

  public pieChartType: ChartType = 'pie';

  constructor(
    private apiService: ApiService,
    private wsService: WebSocketService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
    this.setupWebSocketUpdates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadDashboardData(): void {
    this.loading = true;
    
    // Load overview data
    this.apiService.getDashboardOverview()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.overview = data;
          this.updatePieChart();
        },
        error: (error) => {
          console.error('Error loading dashboard overview:', error);
        }
      });

    // Load cost trends
    this.apiService.getCostTrends(30)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.costTrends = data;
          this.updateLineChart();
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading cost trends:', error);
          this.loading = false;
        }
      });
  }

  private updateLineChart(): void {
    if (this.costTrends.length === 0) return;

    this.lineChartData.labels = this.costTrends.map(item => 
      new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    );
    
    this.lineChartData.datasets[0].data = this.costTrends.map(item => item.total_cost);
    this.lineChartData.datasets[1].data = this.costTrends.map(item => item.compute_cost);
    this.lineChartData.datasets[2].data = this.costTrends.map(item => item.storage_cost);
  }

  private updatePieChart(): void {
    if (!this.overview) return;

    // Calculate total costs by type from recent trends
    const totalCompute = this.costTrends.reduce((sum, item) => sum + item.compute_cost, 0);
    const totalStorage = this.costTrends.reduce((sum, item) => sum + item.storage_cost, 0);
    const totalNetwork = this.costTrends.reduce((sum, item) => sum + item.network_cost, 0);

    this.pieChartData.datasets[0].data = [totalCompute, totalStorage, totalNetwork];
  }

  private setupWebSocketUpdates(): void {
    this.wsService.costUpdates$
      .pipe(takeUntil(this.destroy$))
      .subscribe(update => {
        if (update && update.type === 'cost_update') {
          // Refresh dashboard data when cost updates are received
          this.loadDashboardData();
        }
      });
  }

  getTrendIcon(): string {
    if (!this.overview) return 'trending_flat';
    return this.overview.cost_trend_percentage > 0 ? 'trending_up' : 'trending_down';
  }

  getTrendColor(): string {
    if (!this.overview) return 'primary';
    return this.overview.cost_trend_percentage > 0 ? 'warn' : 'accent';
  }

  refreshData(): void {
    this.loadDashboardData();
  }
}