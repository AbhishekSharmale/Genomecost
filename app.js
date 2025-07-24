// GenomeCostTracker App JavaScript
class GenomeCostTracker {
    constructor() {
        this.currentPage = 'dashboard';
        this.charts = {};
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadDashboard();
        this.loadJobs();
        this.setupCharts();
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.showPage(page);
                
                // Update active nav
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show selected page
        document.getElementById(pageId).classList.add('active');
        this.currentPage = pageId;
        
        // Load page-specific content
        switch(pageId) {
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'jobs':
                this.refreshJobs();
                break;
        }
    }

    loadDashboard() {
        // Dashboard is loaded by default
        this.setupDashboardCharts();
    }

    setupDashboardCharts() {
        // Cost Trend Chart
        const ctx1 = document.getElementById('costTrendChart');
        if (ctx1) {
            ctx1.height = 300;
            this.charts.costTrend = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Total Cost ($)',
                        data: [1200, 1450, 1680, 1847],
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#6366f1',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                font: {
                                    size: 12
                                },
                                color: '#6b7280',
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: {
                                    size: 12
                                },
                                color: '#6b7280'
                            }
                        }
                    }
                }
            });
        }

        // Resource Breakdown Chart
        const ctx2 = document.getElementById('resourceChart');
        if (ctx2) {
            ctx2.height = 300;
            this.charts.resource = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['Compute (65%)', 'Storage (23%)', 'Network (12%)'],
                    datasets: [{
                        data: [1850, 650, 347],
                        backgroundColor: ['#6366f1', '#10b981', '#f59e0b'],
                        borderWidth: 4,
                        borderColor: '#ffffff',
                        hoverOffset: 15,
                        hoverBorderWidth: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                usePointStyle: true,
                                font: {
                                    size: 12
                                },
                                color: '#374151'
                            }
                        }
                    },
                    cutout: '65%'
                }
            });
        }
    }

    loadJobs() {
        const jobs = [
            {
                id: 'nf-core-rnaseq-001',
                pipeline: 'RNA-seq',
                sample: 'SAMPLE_001',
                project: 'Cancer Genomics',
                status: 'running',
                progress: 65,
                cost: 23.45
            },
            {
                id: 'nf-core-wgs-002',
                pipeline: 'WGS',
                sample: 'SAMPLE_002',
                project: 'Rare Disease Study',
                status: 'completed',
                progress: 100,
                cost: 92.18
            },
            {
                id: 'nf-core-chipseq-003',
                pipeline: 'ChIP-seq',
                sample: 'SAMPLE_003',
                project: 'Epigenomics',
                status: 'completed',
                progress: 100,
                cost: 34.67
            },
            {
                id: 'custom-pipeline-004',
                pipeline: 'scRNA-seq',
                sample: 'SAMPLE_004',
                project: 'Single Cell Atlas',
                status: 'failed',
                progress: 45,
                cost: 12.34
            },
            {
                id: 'nf-core-atacseq-005',
                pipeline: 'ATAC-seq',
                sample: 'SAMPLE_005',
                project: 'Chromatin Study',
                status: 'running',
                progress: 30,
                cost: 18.92
            }
        ];

        this.renderJobsTable(jobs);
    }

    renderJobsTable(jobs) {
        const tbody = document.getElementById('jobsTableBody');
        if (!tbody) return;

        tbody.innerHTML = jobs.map(job => `
            <tr>
                <td>
                    <div style="font-weight: 500; color: #374151;">${job.id}</div>
                </td>
                <td>
                    <span style="background: rgba(99, 102, 241, 0.1); color: #6366f1; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500;">
                        ${job.pipeline}
                    </span>
                </td>
                <td>${job.sample}</td>
                <td>${job.project}</td>
                <td>
                    <span class="status-badge ${job.status}">${job.status}</span>
                </td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${job.progress}%"></div>
                        </div>
                        <span style="font-size: 0.875rem; color: #6b7280;">${job.progress}%</span>
                    </div>
                </td>
                <td style="font-weight: 600; color: #6366f1;">$${job.cost.toFixed(2)}</td>
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn-ghost" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-ghost" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    refreshJobs() {
        // Simulate real-time updates
        setTimeout(() => {
            this.loadJobs();
        }, 100);
    }

    loadAnalytics() {
        this.setupAnalyticsCharts();
    }

    setupAnalyticsCharts() {
        // Pipeline Cost Chart
        const ctx1 = document.getElementById('pipelineChart');
        if (ctx1 && !this.charts.pipeline) {
            ctx1.height = 250;
            this.charts.pipeline = new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['WGS', 'RNA-seq', 'ChIP-seq', 'ATAC-seq', 'scRNA-seq'],
                    datasets: [{
                        label: 'Avg Cost ($)',
                        data: [89, 23, 34, 18, 45],
                        backgroundColor: [
                            '#6366f1',
                            '#10b981',
                            '#f59e0b',
                            '#ef4444',
                            '#8b5cf6'
                        ],
                        borderRadius: 6,
                        borderSkipped: false,
                        barThickness: 40
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                font: { size: 11 },
                                color: '#6b7280',
                                callback: function(value) {
                                    return '$' + value;
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: { size: 11 },
                                color: '#6b7280'
                            }
                        }
                    }
                }
            });
        }

        // Monthly Trends Chart
        const ctx2 = document.getElementById('monthlyChart');
        if (ctx2 && !this.charts.monthly) {
            ctx2.height = 250;
            this.charts.monthly = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: ['October', 'November', 'December', 'January'],
                    datasets: [{
                        label: 'Monthly Spend ($)',
                        data: [2100, 2450, 2680, 2847],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointBackgroundColor: '#10b981',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                font: { size: 11 },
                                color: '#6b7280',
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: { size: 11 },
                                color: '#6b7280'
                            }
                        }
                    }
                }
            });
        }

        // Efficiency Chart
        const ctx3 = document.getElementById('efficiencyChart');
        if (ctx3 && !this.charts.efficiency) {
            ctx3.height = 250;
            this.charts.efficiency = new Chart(ctx3, {
                type: 'doughnut',
                data: {
                    labels: ['Efficient (85%)', 'Needs Optimization (15%)'],
                    datasets: [{
                        data: [85, 15],
                        backgroundColor: ['#10b981', '#f59e0b'],
                        borderWidth: 4,
                        borderColor: '#ffffff',
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                usePointStyle: true,
                                font: { size: 11 },
                                color: '#374151'
                            }
                        }
                    },
                    cutout: '60%'
                }
            });
        }

        // Utilization Chart
        const ctx4 = document.getElementById('utilizationChart');
        if (ctx4 && !this.charts.utilization) {
            ctx4.height = 250;
            this.charts.utilization = new Chart(ctx4, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Usage %',
                        data: [85, 92, 78, 96, 73, 45, 32],
                        backgroundColor: '#6366f1',
                        borderRadius: 4,
                        barThickness: 25
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: 'rgba(0,0,0,0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                font: { size: 11 },
                                color: '#6b7280',
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: { size: 11 },
                                color: '#6b7280'
                            }
                        }
                    }
                }
            });
        }
    }

    setupCharts() {
        // Initialize all charts when DOM is ready
        setTimeout(() => {
            this.setupDashboardCharts();
        }, 100);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GenomeCostTracker();
});

// Add some interactive features
document.addEventListener('click', (e) => {
    // Handle metric card clicks
    if (e.target.closest('.metric-card')) {
        const card = e.target.closest('.metric-card');
        card.style.transform = 'scale(0.98)';
        setTimeout(() => {
            card.style.transform = '';
        }, 150);
    }
    
    // Handle optimization card actions
    if (e.target.closest('.optimization-actions .btn-primary')) {
        e.preventDefault();
        const card = e.target.closest('.optimization-card');
        const savings = card.querySelector('.optimization-savings').textContent;
        
        // Show success message
        const btn = e.target.closest('.btn-primary');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Implemented';
        btn.style.background = '#10b981';
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
        }, 2000);
    }
});

// Add real-time updates simulation
setInterval(() => {
    // Update random metric values slightly
    const metricValues = document.querySelectorAll('.metric-value');
    metricValues.forEach(value => {
        if (value.textContent.includes('$')) {
            const current = parseFloat(value.textContent.replace('$', '').replace(',', ''));
            const change = (Math.random() - 0.5) * 2; // Random change between -1 and 1
            const newValue = Math.max(0, current + change);
            value.textContent = '$' + newValue.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    });
}, 5000); // Update every 5 seconds