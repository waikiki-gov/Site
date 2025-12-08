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

    // Employment Rate Doughnut Chart
    const employmentRateCtx = document.getElementById('employmentRateChart');
    if (employmentRateCtx) {
        new Chart(employmentRateCtx, {
            type: 'doughnut',
            data: {
                labels: ['Employed', 'Unemployed'],
                datasets: [{
                    data: [94, 6],
                    backgroundColor: [COLORS.tertiary, '#e0e0e0'],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: function(chart) {
                    const ctx = chart.ctx;
                    const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
                    const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
                    ctx.save();
                    ctx.font = 'bold 2.5rem Inter, sans-serif';
                    ctx.fillStyle = COLORS.primary;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('94%', centerX, centerY);
                    ctx.restore();
                }
            }]
        });
    }

    // Inflation Rate Doughnut Chart
    const inflationRateCtx = document.getElementById('inflationRateChart');
    if (inflationRateCtx) {
        new Chart(inflationRateCtx, {
            type: 'doughnut',
            data: {
                labels: ['Inflation', 'Remaining'],
                datasets: [{
                    data: [0.8, 99.2],
                    backgroundColor: [COLORS.secondary, '#e0e0e0'],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: function(chart) {
                    const ctx = chart.ctx;
                    const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
                    const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
                    ctx.save();
                    ctx.font = 'bold 2.5rem Inter, sans-serif';
                    ctx.fillStyle = COLORS.primary;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('0.8%', centerX, centerY);
                    ctx.restore();
                }
            }]
        });
    }

    // Employment Distribution Doughnut Chart
    const employmentDistributionCtx = document.getElementById('employmentDistributionChart');
    if (employmentDistributionCtx) {
        new Chart(employmentDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Healthcare & Education', 'Trade & Logistics', 'Administration', 'Other Services', 'ICT', 'Finance', 'Manufacturing', 'Other'],
                datasets: [{
                    data: [22.4, 18.1, 13.9, 11, 10.4, 9, 7.7, 7.5],
                    backgroundColor: [
                        COLORS.primary,
                        COLORS.tertiary,
                        COLORS.secondary,
                        COLORS.gold,
                        '#00B0C3',
                        '#0071BC',
                        '#0E308E',
                        COLORS.silver
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            padding: 12,
                            usePointStyle: true,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Sector GDP Contribution Chart
    const sectorGdpCtx = document.getElementById('sectorGdpChart');
    if (sectorGdpCtx) {
        new Chart(sectorGdpCtx, {
            type: 'bar',
            data: {
                labels: ['Services', 'Industry', 'Finance', 'Technology', 'Agriculture'],
                datasets: [{
                    label: 'GDP Contribution',
                    data: [45, 25, 15, 12, 3],
                    backgroundColor: [
                        COLORS.primary,
                        COLORS.secondary,
                        COLORS.gold,
                        COLORS.tertiary,
                        COLORS.success
                    ],
                    borderRadius: 8,
                    borderSkipped: false,
                    formatter: (value) => value + '%'
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                plugins: {
                    ...commonOptions.plugins,
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ...commonOptions.scales.x,
                        max: 50,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    y: {
                        ...commonOptions.scales.y,
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Budget Allocation Chart
    const budgetCtx = document.getElementById('budgetChart');
    if (budgetCtx) {
        new Chart(budgetCtx, {
            type: 'bar',
            data: {
                labels: ['Healthcare', 'R&D', 'Education', 'Infrastructure', 'Defense', 'Administration', 'Public Safety', 'Social Programs', 'Culture & Sports'],
                datasets: [{
                    label: 'Budget Share',
                    data: [36.6, 24, 9.6, 6.8, 6.6, 3.9, 3.4, 3, 2],
                    backgroundColor: [
                        COLORS.primary,
                        COLORS.secondary,
                        COLORS.tertiary,
                        COLORS.gold,
                        COLORS.primary,
                        COLORS.secondary,
                        COLORS.tertiary,
                        COLORS.silver,
                        COLORS.gold
                    ],
                    borderRadius: 8,
                    borderSkipped: false,
                    formatter: (value) => value + '%'
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                plugins: {
                    ...commonOptions.plugins,
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ...commonOptions.scales.x,
                        max: 40,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    y: {
                        ...commonOptions.scales.y,
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Wealth Distribution Chart
    const wealthDistributionCtx = document.getElementById('wealthDistributionChart');
    if (wealthDistributionCtx) {
        new Chart(wealthDistributionCtx, {
            type: 'bar',
            data: {
                labels: ['Bottom 20%', '20-40%', '40-60%', '60-90%', 'Top 5%'],
                datasets: [{
                    label: 'Wealth Share',
                    data: [1.9, 9.3, 16.6, 32.6, 34.8],
                    backgroundColor: [
                        COLORS.silver,
                        COLORS.primary,
                        COLORS.tertiary,
                        COLORS.secondary,
                        COLORS.gold
                    ],
                    borderRadius: 8,
                    borderSkipped: false,
                    formatter: (value) => value + '%'
                }]
            },
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
                        max: 40,
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

    // Gini Coefficient Chart
    const giniCtx = document.getElementById('giniChart');
    if (giniCtx) {
        new Chart(giniCtx, {
            type: 'line',
            data: {
                labels: ['2000', '2005', '2010', '2015', '2020', '2025'],
                datasets: [{
                    label: 'Gini Coefficient',
                    data: [0.42, 0.39, 0.35, 0.32, 0.29, 0.28],
                    borderColor: COLORS.success,
                    backgroundColor: 'rgba(0, 128, 0, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: COLORS.success,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    formatter: (value) => value.toFixed(2)
                }]
            },
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
                        min: 0.2,
                        max: 0.5,
                        ticks: {
                            ...commonOptions.scales.y.ticks,
                            callback: function(value) {
                                return value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }

    // National Savings Rate Chart
    const savingsRateCtx = document.getElementById('savingsRateChart');
    if (savingsRateCtx) {
        new Chart(savingsRateCtx, {
            type: 'line',
            data: {
                labels: ['2000', '2005', '2010', '2015', '2020', '2025'],
                datasets: [{
                    label: 'Savings Rate',
                    data: [12, 15, 18, 23, 28, 32],
                    borderColor: COLORS.primary,
                    backgroundColor: 'rgba(0, 113, 188, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: COLORS.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    formatter: (value) => value + '%'
                }]
            },
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
                        max: 40,
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

    // Price Indices Chart
    const priceIndicesCtx = document.getElementById('priceIndicesChart');
    if (priceIndicesCtx) {
        new Chart(priceIndicesCtx, {
            type: 'line',
            data: {
                labels: ['2010', '2013', '2016', '2019', '2022', '2025'],
                datasets: [
                    {
                        label: 'Consumer Price Index (CPI)',
                        data: [100, 103, 106, 109, 112, 115],
                        borderColor: COLORS.primary,
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: COLORS.primary,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        formatter: (value) => value
                    },
                    {
                        label: 'Producer Price Index (PPI)',
                        data: [100, 105, 112, 120, 126, 132],
                        borderColor: COLORS.secondary,
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: COLORS.secondary,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        formatter: (value) => value
                    },
                    {
                        label: 'Housing Price Index (HPI)',
                        data: [100, 103, 107, 111, 115, 119],
                        borderColor: COLORS.tertiary,
                        backgroundColor: 'transparent',
                        borderWidth: 3,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: COLORS.tertiary,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        formatter: (value) => value
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
                        min: 95,
                        max: 140
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
