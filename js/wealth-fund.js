// Wealth Fund Page JavaScript - Waikiki Government Site

// Chart.js default configuration
Chart.defaults.font.family = "'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = '#555555';

const isHu = (document.documentElement.lang || '').toLowerCase().startsWith('hu');

// Color constants
const COLORS = {
    primary: '#0071BC',
    secondary: '#0E308E',
    tertiary: '#00B0C3',
    gold: '#BC9200',
    error: '#AD1A24',
    success: '#008000'
};

// Common chart options for responsive behavior
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        mode: 'index',
        intersect: false,
    },
    plugins: {
        legend: {
            display: true,
            position: 'bottom',
            labels: {
                padding: 15,
                usePointStyle: true,
                font: {
                    size: 14,
                    weight: '500'
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(14, 48, 142, 0.95)',
            padding: 12,
            titleFont: {
                size: 15,
                weight: '600'
            },
            bodyFont: {
                size: 14
            },
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
                label: function (context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += context.dataset.formatter
                            ? context.dataset.formatter(context.parsed.y)
                            : context.parsed.y;
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0, 0, 0, 0.05)',
                drawBorder: false
            },
            ticks: {
                padding: 10,
                font: {
                    size: 14
                }
            }
        },
        x: {
            grid: {
                display: false,
                drawBorder: false
            },
            ticks: {
                padding: 10,
                font: {
                    size: 14,
                    weight: '500'
                }
            }
        }
    }
};

/**
 * Initialize wealth fund page specific features
 */
function initWealthFund() {
    initFundGrowthChart();
    initGDPRatioChart();
    initProjectionChart();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWealthFund);
} else {
    initWealthFund();
}

// Fund Growth Chart
function initFundGrowthChart() {
    const ctx = document.getElementById('fundGrowthChart');
    if (!ctx) return;

    try {
        const data = {
            labels: ['2000', '2005', '2010', '2015', '2020', '2025'],
            datasets: [
                {
                    label: isHu ? 'Alap vagyona (billió WUD)' : 'Fund Assets (Trillion WUD)',
                    data: [0.03, 0.51, 3.16, 6.56, 9.46, 11.12],
                    borderColor: COLORS.gold,
                    backgroundColor: 'rgba(188, 146, 0, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: COLORS.gold,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    formatter: (value) => value.toFixed(2) + 'T'
                },
                {
                    label: isHu ? 'Alap vagyona (billió USD)' : 'Fund Assets (Trillion USD)',
                    data: [0.03, 0.61, 4.93, 13.13, 21.39, 25.58],
                    borderColor: COLORS.primary,
                    backgroundColor: 'rgba(0, 113, 188, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: COLORS.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    formatter: (value) => value.toFixed(2) + 'T'
                }
            ]
        };

        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                ...commonOptions,
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function (value) {
                                return '₩ ' + value + 'T';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to initialize fund growth chart:', error);
    }
}

// GDP Ratio Chart
function initGDPRatioChart() {
    const ctx = document.getElementById('gdpRatioChart');
    if (!ctx) return;

    try {
        const data = {
            labels: ['2000', '2005', '2010', '2015', '2020', '2025'],
            datasets: [{
                label: isHu ? 'Alap a GDP százalékában' : 'Fund as % of GDP',
                data: [2, 11, 35, 48, 61, 61],
                backgroundColor: [
                    'rgba(0, 113, 188, 0.8)',
                    'rgba(14, 48, 142, 0.8)',
                    'rgba(0, 176, 195, 0.8)',
                    'rgba(188, 146, 0, 0.8)',
                    'rgba(0, 113, 188, 0.8)',
                    'rgba(14, 48, 142, 0.8)'
                ],
                borderColor: [
                    COLORS.primary,
                    COLORS.secondary,
                    COLORS.tertiary,
                    COLORS.gold,
                    COLORS.primary,
                    COLORS.secondary
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
                formatter: (value) => value + '%'
            }]
        };

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    legend: {
                        display: false
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        max: 70,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function (value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to initialize GDP ratio chart:', error);
    }
}

// Projection Chart
function initProjectionChart() {
    const ctx = document.getElementById('projectionChart');
    if (!ctx) return;

    try {
        const data = {
            labels: ['2025', '2027', '2029', '2031', '2033', '2035', '2037', '2039'],
            datasets: [
                {
                    label: isHu ? 'Tervezett vagyon (billió WUD)' : 'Projected Assets (Trillion WUD)',
                    data: [11.12, 11.82, 12.91, 13.68, 14.27, 15.08, 16.14, 16.58],
                    borderColor: COLORS.gold,
                    backgroundColor: 'rgba(188, 146, 0, 0.7)',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                    formatter: (value) => value.toFixed(2) + 'T'
                }
            ]
        };

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                ...commonOptions,
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function (value) {
                                return '₩ ' + value + 'T';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to initialize projection chart:', error);
    }
}
