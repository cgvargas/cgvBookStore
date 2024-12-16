class VisitDetailsModal {
    constructor() {
        this.modal = null;
        this.charts = {
            timeline: null,
            distribution: null
        };
        this.initialize();
    }

    initialize() {
        console.log('Iniciando inicialização do modal');
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        const modalElement = document.getElementById('visitDetailsModal');
        if (modalElement) {
            this.modal = $(modalElement);
            console.log('Modal inicializado');
        } else {
            console.error('Elemento do modal não encontrado');
            return;
        }

        const metricCards = document.querySelectorAll('.metric-card');
        console.log('Cards encontrados:', metricCards.length);

        metricCards.forEach(card => {
            card.addEventListener('click', (e) => {
                console.log('Card clicado');
                e.preventDefault();
                this.show();
            });
        });
    }

    async show() {
        try {
            const data = await this.fetchVisitDetails();
            if (!data) {
                console.error('Nenhum dado recebido');
                return;
            }

            this.updateMetrics(data);
            this.updateCharts(data);
            this.updateTable(data.recentVisits);

            this.modal.modal('show');
        } catch (error) {
            console.error('Erro ao carregar detalhes das visitas:', error);
            alert('Erro ao carregar detalhes das visitas');
        }
    }

    async fetchVisitDetails() {
        try {
            const response = await fetch('/analytics/api/visit-details/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Erro na requisição:', error);
            return null;
        }
    }

    updateMetrics(data) {
        const elements = {
            'todayVisits': data.todayVisits,
            'registeredVisits': data.registeredVisits,
            'anonymousVisits': data.anonymousVisits,
            'conversionRate': `${data.conversionRate}%`
        };

        for (const [id, value] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }
    }

    updateCharts(data) {
        if (data.timeline) this.updateTimelineChart(data.timeline);
        if (data.distribution) this.updateDistributionChart(data.distribution);
    }

    updateTimelineChart(data) {
        const canvas = document.getElementById('visitsTimelineChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }

        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Visitas',
                    data: data.values,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    updateDistributionChart(data) {
        const canvas = document.getElementById('visitorsPieChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        if (this.charts.distribution) {
            this.charts.distribution.destroy();
        }

        this.charts.distribution = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Registrados', 'Anônimos'],
                datasets: [{
                    data: [data.registered, data.anonymous],
                    backgroundColor: ['rgb(54, 162, 235)', 'rgb(255, 99, 132)']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    updateTable(visits) {
        if (!visits || !Array.isArray(visits)) return;

        const tbody = document.querySelector('#visitsDetailsTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        visits.forEach(visit => {
            const row = document.createElement('tr');

            const deviceInfo = typeof visit.device === 'object' ?
                `<small>
                    Tipo: ${visit.device.type || 'N/A'}<br>
                    SO: ${visit.device.os || 'N/A'}
                    ${visit.device.brand && visit.device.brand !== 'unknown' ? `<br>Marca: ${visit.device.brand}` : ''}
                    ${visit.device.model && visit.device.model !== 'unknown' ? `<br>Modelo: ${visit.device.model}` : ''}
                </small>` :
                (visit.device || 'N/A');

            row.innerHTML = `
                <td>${this.formatDateTime(visit.timestamp)}</td>
                <td>${visit.user || 'Anônimo'}</td>
                <td>${visit.page || 'N/A'}</td>
                <td>${visit.duration || 'N/A'}</td>
                <td>${deviceInfo}</td>
            `;
            tbody.appendChild(row);
        });
    }

    formatDateTime(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return timestamp || 'Data inválida';
        }
    }
}

// Inicialização
console.log('Iniciando script do modal');
const visitDetailsModal = new VisitDetailsModal();