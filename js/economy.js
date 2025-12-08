/* Economy Page Interactive Charts - Waikiki Government Site */

// Chart.js default configuration
Chart.defaults.font.family = "'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = '#555555';

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
                    size: 13,
                    weight: '500'
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(14, 48, 142, 0.95)',
            padding: 12,
            titleFont: {
                size: 14,
                weight: '600'
            },
            bodyFont: {
                size: 13
            },
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
                label: function(context) {
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
                    size: 12
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
                    size: 12,
                    weight: '500'
                }
            }
        }
    }
};

// Initialize all charts when DOM is ready
function initEconomyCharts() {
    // GDP Growth Chart
    const gdpCtx = document.getElementById('gdpChart');
    if (gdpCtx) {
        new Chart(gdpCtx, {
            type: 'bar',
            data: {
                labels: ['1999', '2005', '2010', '2015', '2020', '2025'],
                datasets: [{
                    label: 'Total GDP',
                    data: [75, 429, 14021, 27531, 35181, 41836],
                    backgroundColor: COLORS.primary,
                    borderRadius: 8,
                    borderSkipped: false,
                    formatter: (value) => {
                        if (value >= 1000) return '$' + (value / 1000).toFixed(1) + 'T';
                        return '$' + value + 'B';
                    }
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: {
                        display: false
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function(value) {
                                if (value >= 1000) return '$' + (value / 1000) + 'T';
                                return '$' + value + 'B';
                            }
                        }
                    }
                }
            }
        });
    }

    // GDP Per Capita Chart
    const gdpPerCapitaCtx = document.getElementById('gdpPerCapitaChart');
    if (gdpPerCapitaCtx) {
        new Chart(gdpPerCapitaCtx, {
            type: 'bar',
            data: {
                labels: ['1999', '2005', '2010', '2015', '2020', '2025'],
                datasets: [{
                    label: 'GDP Per Capita',
                    data: [6.3, 28.6, 69.8, 133, 165.9, 196.4],
                    backgroundColor: COLORS.secondary,
                    borderRadius: 8,
                    borderSkipped: false,
                    formatter: (value) => '$' + value + 'k'
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: {
                        display: false
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function(value) {
                                return '$' + value + 'k';
                            }
                        }
                    }
                }
            }
        });
    }

    // State Reserves Chart
    const reservesCtx = document.getElementById('reservesChart');
    if (reservesCtx) {
        new Chart(reservesCtx, {
            type: 'line',
            data: {
                labels: ['2000', '2005', '2010', '2015', '2020', '2025'],
                datasets: [{
                    label: 'State Reserves',
                    data: [30, 610, 4930, 13130, 21390, 25580],
                    borderColor: COLORS.gold,
                    backgroundColor: 'rgba(188, 146, 0, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: COLORS.gold,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    formatter: (value) => {
                        if (value >= 1000) return '$' + (value / 1000).toFixed(1) + 'T';
                        return '$' + value + 'B';
                    }
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: {
                        display: false
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function(value) {
                                if (value >= 1000) return '$' + (value / 1000) + 'T';
                                return '$' + value + 'B';
                            }
                        }
                    }
                }
            }
        });
    }

    // Inflation Chart with target line
    const inflationCtx = document.getElementById('inflationChart');
    if (inflationCtx) {
        new Chart(inflationCtx, {
            type: 'line',
            data: {
                labels: ['2000', '2005', '2010', '2015', '2020', '2025'],
                datasets: [
                    {
                        label: 'Actual Inflation',
                        data: [0.0, -0.8, 0.2, 0.4, 0.6, 0.8],
                        borderColor: COLORS.error,
                        backgroundColor: 'rgba(173, 26, 36, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: COLORS.error,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        formatter: (value) => value.toFixed(1) + '%'
                    },
                    {
                        label: 'Target (1%)',
                        data: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                        borderColor: COLORS.success,
                        borderWidth: 2,
                        borderDash: [8, 4],
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        formatter: (value) => value.toFixed(1) + '%'
                    }
                ]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: {
                        display: false
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        max: 5,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Household Income Chart
    const householdIncomeCtx = document.getElementById('householdIncomeChart');
    if (householdIncomeCtx) {
        new Chart(householdIncomeCtx, {
            type: 'line',
            data: {
                labels: ['1999', '2005', '2010', '2015', '2020', '2025'],
                datasets: [{
                    label: 'Median Household Income',
                    data: [7.9, 23.1, 45.4, 78.1, 86.3, 103.8],
                    borderColor: COLORS.tertiary,
                    backgroundColor: 'rgba(0, 176, 195, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: COLORS.tertiary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    formatter: (value) => '$' + value + 'k'
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    ...commonOptions.plugins,
                    title: {
                        display: false
                    }
                },
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function(value) {
                                return '$' + value + 'k';
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize charts when DOM is ready
    console.log('Economy charts initialized successfully');
}

// Initialize charts when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEconomyCharts);
} else {
    initEconomyCharts();
}
