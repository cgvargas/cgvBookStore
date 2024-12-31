// analytics-dashboard.js

// Variáveis globais para os gráficos e intervalos
let visitsChart = null;
let devicesChart = null;
let visitDetailsChart = null;
let updateInterval = null;

// Funções utilitárias
const utils = {
    formatNumber(number) {
        return number ? number.toLocaleString('pt-BR') : '0';
    },

    destroyChart(chart) {
        if (chart) {
            chart.destroy();
            return null;
        }
        return null;
    },

    showError(message) {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        alertContainer.innerHTML = '';
        alertContainer.appendChild(alertDiv);
    },

    formatDeviceInfo(device) {
        if (!device) return 'N/A';
        try {
            if (typeof device === 'string') {
                device = JSON.parse(device);
            }
            return `${device.type || 'N/A'} (${device.os || 'N/A'})`;
        } catch (e) {
            return 'N/A';
        }
    },

    formatDuration(duration) {
        if (!duration) return 'N/A';
        try {
            if (typeof duration === 'string' && duration.includes(':')) {
                return duration;
            }
            const seconds = parseInt(duration);
            if (isNaN(seconds)) return 'N/A';
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return minutes === 0 ? `${remainingSeconds}s` : `${minutes}m ${remainingSeconds}s`;
        } catch (e) {
            return 'N/A';
        }
    }
};

// Funções de atualização de UI
const dashboard = {
    updateDashboard(data) {
        if (!data || typeof data !== 'object') {
            console.error('Dados inválidos recebidos:', data);
            return;
        }

        try {
            const mainMetrics = data.main_metrics || {};
            document.getElementById('totalVisits').textContent = utils.formatNumber(mainMetrics.total_visits || 0);
            document.getElementById('activeUsers').textContent = utils.formatNumber(mainMetrics.active_users || 0);
            document.getElementById('bookViews').textContent = utils.formatNumber(mainMetrics.book_views || 0);
            document.getElementById('totalShares').textContent = utils.formatNumber(data.total_shares || 0);

            if (data.trend_data?.length > 0) {
                this.updateVisitsChart(data.trend_data);
            }

            if (data.devices_data && Object.keys(data.devices_data).length > 0) {
                this.updateDevicesChart(data.devices_data);
            }
        } catch (error) {
            console.error('Erro ao atualizar dashboard:', error);
            utils.showError('Erro ao atualizar dashboard. Por favor, recarregue a página.');
        }
    },

    updateVisitsChart(trendData) {
        const ctx = document.getElementById('visitsChart')?.getContext('2d');
        if (!ctx) return;

        visitsChart = utils.destroyChart(visitsChart);

        const labels = trendData.map(item => item.date);
        const totalData = trendData.map(item => item.total || 0);
        const authenticatedData = trendData.map(item => item.authenticated || 0);
        const anonymousData = trendData.map(item => item.anonymous || 0);

        const maxValue = Math.max(...totalData, ...authenticatedData, ...anonymousData);

        visitsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Total de Visitas',
                        data: totalData,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Visitas Autenticadas',
                        data: authenticatedData,
                        borderColor: 'rgb(54, 162, 235)',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Visitas Anônimas',
                        data: anonymousData,
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: Math.ceil(maxValue * 1.1),
                        ticks: {
                            stepSize: Math.max(1, Math.ceil(maxValue / 10))
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    },

    updateDevicesChart(devicesData) {
        const ctx = document.getElementById('devicesChart')?.getContext('2d');
        if (!ctx) return;

        devicesChart = utils.destroyChart(devicesChart);

        const processedData = {
            desktop: 0,
            mobile: 0,
            tablet: 0,
            other: 0
        };

        Object.entries(devicesData).forEach(([device, count]) => {
            let deviceType = 'other';
            try {
                if (typeof device === 'string') {
                    const deviceLower = device.toLowerCase();
                    if (deviceLower.includes('desktop')) deviceType = 'desktop';
                    else if (deviceLower.includes('mobile')) deviceType = 'mobile';
                    else if (deviceLower.includes('tablet')) deviceType = 'tablet';
                }
                processedData[deviceType] += count;
            } catch (e) {
                processedData.other += count;
            }
        });

        const labels = ['Desktop', 'Mobile', 'Tablet', 'Outros'];
        const values = Object.values(processedData);

        devicesChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        'rgb(54, 162, 235)',
                        'rgb(255, 99, 132)',
                        'rgb(255, 206, 86)',
                        'rgb(75, 192, 192)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    },

    updateVisitDetailsModal(data) {
        try {
            document.getElementById('todayVisits').textContent = utils.formatNumber(data.todayVisits || 0);
            document.getElementById('modalRegisteredVisits').textContent = utils.formatNumber(data.registeredVisits || 0);
            document.getElementById('modalAnonymousVisits').textContent = utils.formatNumber(data.anonymousVisits || 0);
            document.getElementById('modalConversionRate').textContent = `${utils.formatNumber(data.conversionRate || 0)}%`;

            this.updateVisitDetailsChart(data.timeline);
            this.updateVisitDetailsTable(data.recentVisits);
        } catch (error) {
            console.error('Erro ao atualizar modal de detalhes:', error);
            utils.showError('Erro ao carregar detalhes das visitas');
        }
    },

    updateVisitDetailsChart(timelineData) {
        const ctx = document.getElementById('visitsDetailChart')?.getContext('2d');
        if (!ctx) return;

        visitDetailsChart = utils.destroyChart(visitDetailsChart);

        visitDetailsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timelineData.labels,
                datasets: [{
                    label: 'Visitas',
                    data: timelineData.values,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    },

    updateVisitDetailsTable(visits) {
        const tbody = document.getElementById('visitsDetailTable');
        if (!tbody) return;

        tbody.innerHTML = '';

        visits.forEach(visit => {
            const row = document.createElement('tr');
            const timestamp = new Date(visit.timestamp);

            row.innerHTML = `
                <td>${timestamp.toLocaleDateString('pt-BR')} ${timestamp.toLocaleTimeString('pt-BR')}</td>
                <td>${visit.user}</td>
                <td>${visit.page}</td>
                <td>${utils.formatDeviceInfo(visit.device)}</td>
                <td>${utils.formatDuration(visit.duration)}</td>
            `;

            tbody.appendChild(row);
        });
    }
};

// Funções de API
const api = {
    loadAnalyticsData(startDate = null, endDate = null) {
        const url = new URL('/analytics/api/data/', window.location.origin);
        if (startDate && endDate) {
            url.searchParams.set('start_date', startDate);
            url.searchParams.set('end_date', endDate);
        }
        url.searchParams.set('_', Date.now());

        fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) throw new Error(data.error);
            dashboard.updateDashboard(data);
        })
        .catch(error => {
            console.error('Erro ao carregar dados:', error);
            utils.showError('Erro ao carregar dados. Por favor, tente novamente.');
        });
    },

    resetAnalyticsData() {
        if (!confirm('Tem certeza que deseja resetar todos os dados? Esta ação não pode ser desfeita.')) {
            return;
        }

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) {
            utils.showError('Token CSRF não encontrado. Por favor, recarregue a página.');
            return;
        }

        fetch('/analytics/reset/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Dados resetados com sucesso!');
                this.loadAnalyticsData();
            } else {
                throw new Error(data.error || 'Erro desconhecido');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            utils.showError('Erro ao resetar dados: ' + error.message);
        });
    },

    loadVisitDetails() {
        fetch('/analytics/api/visit-details/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) throw new Error(data.error);
            dashboard.updateVisitDetailsModal(data);
        })
        .catch(error => {
            console.error('Erro ao carregar detalhes:', error);
            utils.showError('Erro ao carregar detalhes das visitas. Por favor, tente novamente.');
        });
    },

    exportReport(format) {
        const dateRange = $('#daterange').data('daterangepicker');
        const startDate = dateRange.startDate.format('YYYY-MM-DD');
        const endDate = dateRange.endDate.format('YYYY-MM-DD');

        const urls = {
            excel: '/analytics/export/excel/',
            csv: '/analytics/export/csv/',
            pdf: '/analytics/export/pdf/'
        };

        const url = new URL(urls[format], window.location.origin);
        url.searchParams.set('start_date', startDate);
        url.searchParams.set('end_date', endDate);

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Erro ao exportar dados');
                });
            }
            window.location.href = url.toString();
        })
        .catch(error => {
            console.error('Erro:', error);
            utils.showError('Erro ao exportar dados: ' + error.message);
        });
    }
};

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Configuração do DateRangePicker
        $('#daterange').daterangepicker({
            startDate: moment().subtract(6, 'days'),
            endDate: moment(),
            ranges: {
                'Últimos 7 dias': [moment().subtract(6, 'days'), moment()],
                'Últimos 30 dias': [moment().subtract(29, 'days'), moment()],
                'Este mês': [moment().startOf('month'), moment().endOf('month')]
            },
            locale: {
                format: 'DD/MM/YYYY',
                applyLabel: 'Aplicar',
                cancelLabel: 'Cancelar',
                customRangeLabel: 'Período personalizado',
                daysOfWeek: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
                monthNames: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            }
        }, function(start, end) {
            api.loadAnalyticsData(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
        });

        // Carrega dados iniciais
        api.loadAnalyticsData();

        // Configura atualização automática
        if (updateInterval) {
            clearInterval(updateInterval);
        }
        updateInterval = setInterval(() => api.loadAnalyticsData(), 120000); // Mudado para 1 minuto e 20 segundos

        // Configura botões de exportação
        const exportButtons = {
            'exportExcel': () => api.exportReport('excel'),
            'exportCsv': () => api.exportReport('csv'),
            'exportPdf': () => api.exportReport('pdf')
        };

        Object.entries(exportButtons).forEach(([id, handler]) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            }
        });

        // Configura botão de reset
        const resetButton = document.getElementById('resetAnalytics');
        if (resetButton) {
            resetButton.addEventListener('click', () => api.resetAnalyticsData());
        }

        // Configura modal de detalhes
        const visitDetailsModal = document.getElementById('visitDetailsModal');
        if (visitDetailsModal) {
            $(visitDetailsModal).on('show.bs.modal', api.loadVisitDetails);
            $(visitDetailsModal).on('hidden.bs.modal', () => {
                if (visitDetailsChart) {
                    visitDetailsChart = utils.destroyChart(visitDetailsChart);
                }
            });
        }

    } catch (error) {
        console.error('Erro na inicialização:', error);
        utils.showError('Erro ao inicializar o dashboard. Por favor, recarregue a página.');
    }
});

// Limpar recursos ao fechar a página
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});