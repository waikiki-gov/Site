// Wealth Fund Page JavaScript

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
                    label: 'Fund Assets (Trillion WUD)',
                    data: [0.03, 0.51, 3.16, 6.56, 9.46, 11.12],
                    borderColor: '#BC9200',
                    backgroundColor: 'rgba(188, 146, 0, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#BC9200',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Fund Assets (Trillion USD)',
                    data: [0.03, 0.61, 4.93, 13.13, 21.39, 25.58],
                    borderColor: '#0071BC',
                    backgroundColor: 'rgba(0, 113, 188, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#0071BC',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }
            ]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                family: "'Inter', sans-serif"
                            },
                            padding: 15,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 14,
                            family: "'Inter', sans-serif"
                        },
                        bodyFont: {
                            size: 13,
                            family: "'Inter', sans-serif"
                        },
                        callbacks: {
                            label: function (context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed.y.toFixed(2) + 'T';
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif"
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif"
                            },
                            callback: function (value) {
                                return '₩ ' + value + 'T';
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        };

        new Chart(ctx, config);
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
                label: 'Fund as % of GDP',
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
                    '#0071BC',
                    '#0E308E',
                    '#00B0C3',
                    '#BC9200',
                    '#0071BC',
                    '#0E308E'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        };

        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 14,
                            family: "'Inter', sans-serif"
                        },
                        bodyFont: {
                            size: 13,
                            family: "'Inter', sans-serif"
                        },
                        callbacks: {
                            label: function (context) {
                                return 'Fund/GDP: ' + context.parsed.y + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif"
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 70,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif"
                            },
                            callback: function (value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        };

        new Chart(ctx, config);
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
                    label: 'Projected Assets (Trillion WUD)',
                    data: [11.12, 11.82, 12.91, 13.68, 14.27, 15.08, 16.14, 16.58],
                    borderColor: '#BC9200',
                    backgroundColor: 'rgba(188, 146, 0, 0.7)',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }
            ]
        };

        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                family: "'Inter', sans-serif"
                            },
                            padding: 15,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 14,
                            family: "'Inter', sans-serif"
                        },
                        bodyFont: {
                            size: 13,
                            family: "'Inter', sans-serif"
                        },
                        callbacks: {
                            label: function (context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed.y.toFixed(2) + 'T';
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif"
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif"
                            },
                            callback: function (value) {
                                return '₩ ' + value + 'T';
                            }
                        }
                    }
                }
            }
        };

        new Chart(ctx, config);
    } catch (error) {
        console.error('Failed to initialize projection chart:', error);
    }
}
