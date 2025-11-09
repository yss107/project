// Air Pollution Dashboard JavaScript

// Real-time monitoring state
let realtimeData = { nyc: [], bogota: [] };
let eventSource = null;
let realtimeActive = false;

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load data for the tab
    if (tabName === 'realtime') {
        startRealTimeMonitoring();
    } else {
        stopRealTimeMonitoring();
        if (tabName === 'overview') {
            loadOverview();
        } else if (tabName === 'timeseries') {
            loadTimeSeries();
        } else if (tabName === 'patterns') {
            loadPatterns();
        } else if (tabName === 'comparison') {
            loadComparison();
        } else if (tabName === 'who-limits') {
            loadWHOLimits();
        }
    }
}

// Load overview data
async function loadOverview() {
    try {
        // Load NYC stats
        const nycStats = await fetch('/api/stats/NYC').then(r => r.json());
        displayStats('nyc-stats', nycStats);
        
        // Load Bogota stats
        const bogotaStats = await fetch('/api/stats/Bogota').then(r => r.json());
        displayStats('bogota-stats', bogotaStats);
        
        // Load insights
        loadInsights(nycStats, bogotaStats);
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

function displayStats(containerId, stats) {
    const container = document.getElementById(containerId);
    const pm25 = stats.pm25;
    
    let html = `
        <div class="stat-item">
            <span class="stat-label">Mean PM2.5</span>
            <span class="stat-value">${pm25.mean.toFixed(2)} μg/m³</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Median PM2.5</span>
            <span class="stat-value">${pm25.median.toFixed(2)} μg/m³</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Std Dev</span>
            <span class="stat-value">${pm25.std.toFixed(2)} μg/m³</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Min / Max</span>
            <span class="stat-value">${pm25.min.toFixed(2)} / ${pm25.max.toFixed(2)} μg/m³</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Data Points</span>
            <span class="stat-value">${pm25.count.toLocaleString()}</span>
        </div>
    `;
    
    if (stats.pm10) {
        html += `
            <div class="stat-item">
                <span class="stat-label">Mean PM10</span>
                <span class="stat-value">${stats.pm10.mean.toFixed(2)} μg/m³</span>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

async function loadInsights(nycStats, bogotaStats) {
    const container = document.getElementById('insights');
    const comparison = await fetch('/api/compare').then(r => r.json());
    
    const nycMean = nycStats.pm25.mean;
    const bogotaMean = bogotaStats.pm25.mean;
    const percentDiff = ((bogotaMean - nycMean) / nycMean * 100).toFixed(1);
    
    let html = `
        <div class="insight-item">
            <strong>📍 Geographic Comparison:</strong> 
            Bogota has ${percentDiff}% higher average PM2.5 levels than NYC 
            (${bogotaMean.toFixed(2)} vs ${nycMean.toFixed(2)} μg/m³).
        </div>
        <div class="insight-item ${Math.abs(comparison.correlation) > 0.3 ? 'success' : 'warning'}">
            <strong>📊 Correlation:</strong> 
            The two cities show a correlation of ${comparison.correlation.toFixed(3)}. 
            ${Math.abs(comparison.correlation) > 0.3 ? 'There is a moderate correlation between the cities.' : 'The cities show weak correlation, suggesting independent pollution sources.'}
        </div>
        <div class="insight-item">
            <strong>🔄 Relative Pollution:</strong> 
            NYC pollution is higher than Bogota ${comparison.nyc_higher_percent.toFixed(1)}% of the time 
            (${comparison.nyc_higher_count} out of ${comparison.total_count} hours).
        </div>
    `;
    
    // Add WHO compliance insights
    const nycWHO = await fetch('/api/who-limits/NYC').then(r => r.json());
    const bogotaWHO = await fetch('/api/who-limits/Bogota').then(r => r.json());
    
    html += `
        <div class="insight-item ${nycWHO.annual_compliant ? 'success' : 'danger'}">
            <strong>🏥 NYC WHO Compliance:</strong> 
            Annual mean PM2.5 is ${nycWHO.pm25_annual_mean.toFixed(2)} μg/m³ 
            ${nycWHO.annual_compliant ? '✓ (Compliant)' : '✗ (Non-compliant)'} 
            with WHO guidelines (≤5 μg/m³).
        </div>
        <div class="insight-item ${bogotaWHO.annual_compliant ? 'success' : 'danger'}">
            <strong>🏥 Bogota WHO Compliance:</strong> 
            Annual mean PM2.5 is ${bogotaWHO.pm25_annual_mean.toFixed(2)} μg/m³ 
            ${bogotaWHO.annual_compliant ? '✓ (Compliant)' : '✗ (Non-compliant)'} 
            with WHO guidelines (≤5 μg/m³).
        </div>
    `;
    
    container.innerHTML = html;
}

// Load time series
async function loadTimeSeries() {
    await updateTimeSeries();
    await loadDailySeries();
}

async function updateTimeSeries() {
    const showNYC = document.getElementById('show-nyc').checked;
    const showBogota = document.getElementById('show-bogota').checked;
    
    const traces = [];
    
    if (showNYC) {
        const nycData = await fetch('/api/timeseries/NYC/PM2.5').then(r => r.json());
        traces.push({
            x: nycData.map(d => d.date),
            y: nycData.map(d => d.value),
            type: 'scatter',
            mode: 'lines',
            name: 'NYC PM2.5',
            line: { color: '#3498db', width: 1.5 }
        });
    }
    
    if (showBogota) {
        const bogotaData = await fetch('/api/timeseries/Bogota/PM2.5').then(r => r.json());
        traces.push({
            x: bogotaData.map(d => d.date),
            y: bogotaData.map(d => d.value),
            type: 'scatter',
            mode: 'lines',
            name: 'Bogota PM2.5',
            line: { color: '#e74c3c', width: 1.5 }
        });
    }
    
    // Add WHO guideline
    traces.push({
        x: traces.length > 0 ? [traces[0].x[0], traces[0].x[traces[0].x.length - 1]] : [],
        y: [15, 15],
        type: 'scatter',
        mode: 'lines',
        name: 'WHO 24h Limit',
        line: { color: '#f39c12', width: 2, dash: 'dash' }
    });
    
    const layout = {
        title: 'PM2.5 Hourly Measurements',
        xaxis: { title: 'Date' },
        yaxis: { title: 'PM2.5 (μg/m³)' },
        hovermode: 'closest',
        showlegend: true,
        height: 450
    };
    
    Plotly.newPlot('timeseries-plot', traces, layout, {responsive: true});
}

async function loadDailySeries() {
    const nycDaily = await fetch('/api/daily/NYC/PM2.5').then(r => r.json());
    const bogotaDaily = await fetch('/api/daily/Bogota/PM2.5').then(r => r.json());
    
    const traces = [
        {
            x: nycDaily.map(d => d.date),
            y: nycDaily.map(d => d.value),
            type: 'scatter',
            mode: 'lines',
            name: 'NYC Daily Avg',
            line: { color: '#3498db', width: 2 }
        },
        {
            x: bogotaDaily.map(d => d.date),
            y: bogotaDaily.map(d => d.value),
            type: 'scatter',
            mode: 'lines',
            name: 'Bogota Daily Avg',
            line: { color: '#e74c3c', width: 2 }
        },
        {
            x: [nycDaily[0].date, nycDaily[nycDaily.length - 1].date],
            y: [15, 15],
            type: 'scatter',
            mode: 'lines',
            name: 'WHO 24h Limit',
            line: { color: '#f39c12', width: 2, dash: 'dash' }
        }
    ];
    
    const layout = {
        title: 'PM2.5 Daily Averages',
        xaxis: { title: 'Date' },
        yaxis: { title: 'PM2.5 (μg/m³)' },
        hovermode: 'closest',
        showlegend: true,
        height: 450
    };
    
    Plotly.newPlot('daily-plot', traces, layout, {responsive: true});
}

// Load patterns
async function loadPatterns() {
    await loadHourlyPattern();
    await loadMonthlyPattern();
}

async function loadHourlyPattern() {
    const nycHourly = await fetch('/api/hourly/NYC/PM2.5').then(r => r.json());
    const bogotaHourly = await fetch('/api/hourly/Bogota/PM2.5').then(r => r.json());
    
    const traces = [
        {
            x: nycHourly.map(d => d.hour),
            y: nycHourly.map(d => d.value),
            type: 'bar',
            name: 'NYC',
            marker: { color: '#3498db' }
        },
        {
            x: bogotaHourly.map(d => d.hour),
            y: bogotaHourly.map(d => d.value),
            type: 'bar',
            name: 'Bogota',
            marker: { color: '#e74c3c' }
        }
    ];
    
    const layout = {
        title: 'Average PM2.5 by Hour of Day',
        xaxis: { title: 'Hour of Day', tickmode: 'linear' },
        yaxis: { title: 'Average PM2.5 (μg/m³)' },
        barmode: 'group',
        height: 400
    };
    
    Plotly.newPlot('hourly-plot', traces, layout, {responsive: true});
}

async function loadMonthlyPattern() {
    const nycMonthly = await fetch('/api/monthly/NYC/PM2.5').then(r => r.json());
    const bogotaMonthly = await fetch('/api/monthly/Bogota/PM2.5').then(r => r.json());
    
    const traces = [
        {
            x: nycMonthly.map(d => d.month),
            y: nycMonthly.map(d => d.value),
            type: 'bar',
            name: 'NYC',
            marker: { color: '#3498db' }
        },
        {
            x: bogotaMonthly.map(d => d.month),
            y: bogotaMonthly.map(d => d.value),
            type: 'bar',
            name: 'Bogota',
            marker: { color: '#e74c3c' }
        }
    ];
    
    const layout = {
        title: 'Average PM2.5 by Month',
        xaxis: { title: 'Month' },
        yaxis: { title: 'Average PM2.5 (μg/m³)' },
        barmode: 'group',
        height: 400
    };
    
    Plotly.newPlot('monthly-plot', traces, layout, {responsive: true});
}

// Load comparison
async function loadComparison() {
    const comparison = await fetch('/api/compare').then(r => r.json());
    
    // Display comparison stats
    const statsContainer = document.getElementById('comparison-stats');
    statsContainer.innerHTML = `
        <div class="comparison-stat">
            <span><strong>Correlation Coefficient:</strong></span>
            <span>${comparison.correlation.toFixed(3)}</span>
        </div>
        <div class="comparison-stat">
            <span><strong>NYC Higher:</strong></span>
            <span>${comparison.nyc_higher_count} times (${comparison.nyc_higher_percent.toFixed(1)}%)</span>
        </div>
        <div class="comparison-stat">
            <span><strong>Bogota Higher:</strong></span>
            <span>${comparison.total_count - comparison.nyc_higher_count} times (${(100 - comparison.nyc_higher_percent).toFixed(1)}%)</span>
        </div>
    `;
    
    // Create comparison plot
    const data = comparison.comparison_data;
    const traces = [
        {
            x: data.map(d => d.date),
            y: data.map(d => d.nyc),
            type: 'scatter',
            mode: 'lines',
            name: 'NYC PM2.5',
            line: { color: '#3498db', width: 1.5 }
        },
        {
            x: data.map(d => d.date),
            y: data.map(d => d.bogota),
            type: 'scatter',
            mode: 'lines',
            name: 'Bogota PM2.5',
            line: { color: '#e74c3c', width: 1.5 }
        }
    ];
    
    const layout = {
        title: 'PM2.5 Comparison Over Time',
        xaxis: { title: 'Date' },
        yaxis: { title: 'PM2.5 (μg/m³)' },
        hovermode: 'closest',
        showlegend: true,
        height: 450
    };
    
    Plotly.newPlot('comparison-plot', traces, layout, {responsive: true});
}

// Load WHO limits
async function loadWHOLimits() {
    const nycWHO = await fetch('/api/who-limits/NYC').then(r => r.json());
    const bogotaWHO = await fetch('/api/who-limits/Bogota').then(r => r.json());
    
    // Display NYC WHO results
    displayWHOResults('nyc-who', nycWHO);
    displayWHOResults('bogota-who', bogotaWHO);
    
    // Create exceedance plot
    createExceedancePlot(nycWHO, bogotaWHO);
}

function displayWHOResults(containerId, data) {
    const container = document.getElementById(containerId);
    
    const annualClass = data.annual_compliant ? 'compliant' : 'non-compliant';
    const annualBadge = data.annual_compliant ? 'success' : 'danger';
    const annualText = data.annual_compliant ? 'Compliant' : 'Non-compliant';
    
    let html = `
        <div class="who-item ${annualClass}">
            <div>
                <strong>Annual Mean PM2.5:</strong> ${data.pm25_annual_mean.toFixed(2)} μg/m³
                <br><small>WHO Limit: ${data.who_annual_limit} μg/m³</small>
            </div>
            <span class="badge ${annualBadge}">${annualText}</span>
        </div>
        <div class="who-item">
            <div>
                <strong>24-hour Exceedances:</strong> ${data.exceedance_count} days (${data.exceedance_percent.toFixed(1)}%)
                <br><small>WHO 24h Limit: ${data.who_24h_limit} μg/m³</small>
            </div>
        </div>
    `;
    
    if (data.pm10_annual_mean !== undefined) {
        const pm10Class = data.pm10_annual_compliant ? 'compliant' : 'non-compliant';
        const pm10Badge = data.pm10_annual_compliant ? 'success' : 'danger';
        const pm10Text = data.pm10_annual_compliant ? 'Compliant' : 'Non-compliant';
        
        html += `
            <div class="who-item ${pm10Class}">
                <div>
                    <strong>Annual Mean PM10:</strong> ${data.pm10_annual_mean.toFixed(2)} μg/m³
                    <br><small>WHO Limit: ${data.who_pm10_annual_limit} μg/m³</small>
                </div>
                <span class="badge ${pm10Badge}">${pm10Text}</span>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function createExceedancePlot(nycWHO, bogotaWHO) {
    const traces = [
        {
            x: nycWHO.exceedances_24h.map(d => d.date),
            y: nycWHO.exceedances_24h.map(d => d.value),
            type: 'scatter',
            mode: 'markers',
            name: 'NYC Exceedances',
            marker: { color: '#3498db', size: 8 }
        },
        {
            x: bogotaWHO.exceedances_24h.map(d => d.date),
            y: bogotaWHO.exceedances_24h.map(d => d.value),
            type: 'scatter',
            mode: 'markers',
            name: 'Bogota Exceedances',
            marker: { color: '#e74c3c', size: 8 }
        },
        {
            x: [nycWHO.exceedances_24h[0]?.date || '2016-09-01', 
                nycWHO.exceedances_24h[nycWHO.exceedances_24h.length - 1]?.date || '2017-04-01'],
            y: [15, 15],
            type: 'scatter',
            mode: 'lines',
            name: 'WHO 24h Limit',
            line: { color: '#f39c12', width: 2, dash: 'dash' }
        }
    ];
    
    const layout = {
        title: 'Days Exceeding WHO 24-hour PM2.5 Limit (15 μg/m³)',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Daily Mean PM2.5 (μg/m³)' },
        hovermode: 'closest',
        showlegend: true,
        height: 450
    };
    
    Plotly.newPlot('exceedance-plot', traces, layout, {responsive: true});
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadOverview();
});

function startRealTimeMonitoring() {
    if (realtimeActive) return;
    
    realtimeActive = true;
    realtimeData = { nyc: [], bogota: [] };
    
    // Connect to SSE stream
    eventSource = new EventSource('/api/realtime/stream');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateRealTimeDisplay(data);
    };
    
    eventSource.onerror = function(error) {
        console.error('SSE Error:', error);
        document.getElementById('last-update').textContent = 'Connection lost - Reconnecting...';
        stopRealTimeMonitoring();
        setTimeout(startRealTimeMonitoring, 5000);
    };
}

function stopRealTimeMonitoring() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }
    realtimeActive = false;
}

function updateRealTimeDisplay(data) {
    // Update timestamp
    const timestamp = new Date(data.timestamp);
    document.getElementById('last-update').textContent = 
        `Last update: ${timestamp.toLocaleTimeString()}`;
    
    // Update NYC data
    updateCityRealTime('nyc', data.nyc);
    
    // Update Bogota data
    updateCityRealTime('bogota', data.bogota);
    
    // Store data for chart (keep last 10 readings)
    realtimeData.nyc.push({ time: timestamp, value: data.nyc.pm25 });
    realtimeData.bogota.push({ time: timestamp, value: data.bogota.pm25 });
    
    if (realtimeData.nyc.length > 10) {
        realtimeData.nyc.shift();
        realtimeData.bogota.shift();
    }
    
    // Update chart
    updateRealTimeChart();
    
    // Check for alerts
    updateAlerts(data.nyc, data.bogota);
}

function updateCityRealTime(city, data) {
    const container = document.querySelector(`#${city}-realtime .realtime-data`);
    
    const aqiColor = data.aqi_category.color;
    const aqiLevel = data.aqi_category.level;
    
    let html = `
        <div class="pm-reading">
            <div class="pm-label">PM2.5</div>
            <div class="pm-value" style="color: ${aqiColor}">
                ${data.pm25}<span class="pm-unit">μg/m³</span>
            </div>
            <div class="aqi-badge" style="background-color: ${aqiColor}">
                ${aqiLevel}
            </div>
        </div>
        
        <div class="compliance-status ${data.who_compliant ? 'compliant' : 'non-compliant'}">
            ${data.who_compliant ? '✓' : '✗'} WHO Annual Limit (5 μg/m³)
        </div>
    `;
    
    if (data.pm10 !== undefined) {
        html += `
            <div class="pm-secondary">
                <strong>PM10:</strong> ${data.pm10} μg/m³
                ${data.pm10_alert ? '⚠️ Exceeds WHO 24h limit' : ''}
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function updateRealTimeChart() {
    if (realtimeData.nyc.length === 0) return;
    
    const traces = [
        {
            x: realtimeData.nyc.map(d => d.time),
            y: realtimeData.nyc.map(d => d.value),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'NYC',
            line: { color: '#3498db', width: 2 },
            marker: { size: 6 }
        },
        {
            x: realtimeData.bogota.map(d => d.time),
            y: realtimeData.bogota.map(d => d.value),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Bogota',
            line: { color: '#e74c3c', width: 2 },
            marker: { size: 6 }
        }
    ];
    
    const layout = {
        title: 'Live PM2.5 Trends',
        xaxis: { 
            title: 'Time',
            type: 'date'
        },
        yaxis: { title: 'PM2.5 (μg/m³)' },
        hovermode: 'closest',
        showlegend: true,
        height: 300,
        margin: { t: 40, b: 40, l: 50, r: 20 }
    };
    
    Plotly.newPlot('realtime-chart', traces, layout, {responsive: true});
}

function updateAlerts(nycData, bogotaData) {
    const alertsContainer = document.getElementById('active-alerts');
    let alerts = [];
    
    // WHO 24-hour limit alert
    if (nycData.alert) {
        alerts.push({
            city: 'New York City',
            message: `PM2.5 level (${nycData.pm25} μg/m³) exceeds WHO 24-hour limit (15 μg/m³)`,
            critical: nycData.pm25 > 35
        });
    }
    
    if (bogotaData.alert) {
        alerts.push({
            city: 'Bogota',
            message: `PM2.5 level (${bogotaData.pm25} μg/m³) exceeds WHO 24-hour limit (15 μg/m³)`,
            critical: bogotaData.pm25 > 35
        });
    }
    
    if (bogotaData.pm10_alert) {
        alerts.push({
            city: 'Bogota',
            message: `PM10 level (${bogotaData.pm10} μg/m³) exceeds WHO 24-hour limit (45 μg/m³)`,
            critical: bogotaData.pm10 > 100
        });
    }
    
    if (alerts.length === 0) {
        alertsContainer.innerHTML = '<p class="no-alerts">No active alerts</p>';
    } else {
        let html = alerts.map(alert => `
            <div class="alert-item ${alert.critical ? 'critical' : ''}">
                <strong>${alert.city}</strong>
                ${alert.message}
            </div>
        `).join('');
        alertsContainer.innerHTML = html;
    }
}
