// Dashboard JavaScript for Bot Statistics

let responseTimeChart, tokensPerSecChart, messagesByUserChart, commandsChart;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadDashboardData();
});

// Initialize Chart.js charts
function initializeCharts() {
    // Response Time Chart
    const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
    responseTimeChart = new Chart(responseTimeCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tiempo de Respuesta (s)',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Segundos'
                    }
                }
            }
        }
    });

    // Tokens Per Second Chart
    const tokensPerSecCtx = document.getElementById('tokensPerSecChart').getContext('2d');
    tokensPerSecChart = new Chart(tokensPerSecCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tokens/Segundo',
                data: [],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Tokens/s'
                    }
                }
            }
        }
    });

    // Messages by User Chart
    const messagesByUserCtx = document.getElementById('messagesByUserChart').getContext('2d');
    messagesByUserChart = new Chart(messagesByUserCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Mensajes',
                data: [],
                backgroundColor: 'rgba(23, 162, 184, 0.8)',
                borderColor: '#17a2b8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cantidad'
                    }
                }
            }
        }
    });

    // Commands Usage Chart
    const commandsCtx = document.getElementById('commandsChart').getContext('2d');
    commandsChart = new Chart(commandsCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#007bff',
                    '#28a745',
                    '#ffc107',
                    '#dc3545',
                    '#6f42c1',
                    '#e83e8c',
                    '#fd7e14'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load dashboard data from API
async function loadDashboardData() {
    try {
        // Load summary statistics
        const summaryResponse = await fetch('/api/stats/summary');
        const summary = await summaryResponse.json();

        // Update summary cards
        document.getElementById('total-messages').textContent = summary.total_messages;
        document.getElementById('avg-response-time').textContent = `${summary.avg_response_time.toFixed(2)}s`;
        document.getElementById('avg-tokens-sec').textContent = summary.avg_tokens_per_second.toFixed(1);
        document.getElementById('total-users').textContent = summary.total_users;

        // Load chart data
        const chartResponse = await fetch('/api/stats/charts');
        const chartData = await chartResponse.json();

        // Update charts
        updateResponseTimeChart(chartData.response_times);
        updateTokensPerSecChart(chartData.tokens_per_second);
        updateMessagesByUserChart(chartData.messages_by_user);
        updateCommandsChart(chartData.commands_usage);

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Error al cargar los datos del dashboard');
    }
}

// Update Response Time Chart
function updateResponseTimeChart(data) {
    responseTimeChart.data.labels = data.labels;
    responseTimeChart.data.datasets[0].data = data.data;
    responseTimeChart.update();
}

// Update Tokens Per Second Chart
function updateTokensPerSecChart(data) {
    tokensPerSecChart.data.labels = data.labels;
    tokensPerSecChart.data.datasets[0].data = data.data;
    tokensPerSecChart.update();
}

// Update Messages by User Chart
function updateMessagesByUserChart(data) {
    messagesByUserChart.data.labels = data.labels;
    messagesByUserChart.data.datasets[0].data = data.data;
    messagesByUserChart.update();
}

// Update Commands Chart
function updateCommandsChart(data) {
    commandsChart.data.labels = data.labels;
    commandsChart.data.datasets[0].data = data.data;
    commandsChart.update();
}

// Refresh data manually
function refreshData() {
    const refreshBtn = event.target;
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando...';
    refreshBtn.classList.add('loading');

    loadDashboardData().finally(() => {
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Actualizar';
        refreshBtn.classList.remove('loading');
    });
}

// Show different sections
function showSection(sectionName) {
    // Hide all sections
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('chats-section').style.display = 'none';
    document.getElementById('personalities-section').style.display = 'none';

    // Show selected section
    document.getElementById(sectionName + '-section').style.display = 'block';

    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'chats': 'Gestión de Chats',
        'personalities': 'Personalidades'
    };
    document.querySelector('h1').textContent = titles[sectionName];
}

// Show error message
function showError(message) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Auto refresh data every 30 seconds
setInterval(loadDashboardData, 30000);
