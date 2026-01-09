import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import StatCard from '../components/StatCard'

function Metrics() {
    const [metrics, setMetrics] = useState(null)
    const [dailyMetrics, setDailyMetrics] = useState([])
    const [loading, setLoading] = useState(true)
    const [aiStatus, setAiStatus] = useState(null)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [metricsRes, dailyRes, healthRes] = await Promise.all([
                fetch('/api/metrics'),
                fetch('/api/metrics/daily'),
                fetch('/api/health')
            ])

            const metricsData = await metricsRes.json()
            const dailyData = await dailyRes.json()
            const healthData = await healthRes.json()

            setMetrics(metricsData)
            setDailyMetrics(dailyData)
            setAiStatus(healthData)
        } catch (err) {
            console.error('Error fetching metrics:', err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        )
    }

    // Prepare chart data - insights by role
    const roleData = metrics?.by_role || {}
    const roleChartData = [{
        x: Object.keys(roleData),
        y: Object.values(roleData).map(r => r.insights),
        type: 'bar',
        marker: { color: '#FF3621' }
    }]

    // Daily trend from metrics
    const trendData = [{
        x: metrics?.daily_trend?.map(d => d.date) || [],
        y: metrics?.daily_trend?.map(d => d.insights) || [],
        type: 'scatter',
        mode: 'lines+markers',
        fill: 'tozeroy',
        fillcolor: 'rgba(255, 54, 33, 0.1)',
        line: { color: '#FF3621', width: 2 }
    }]

    // Time saved by role
    const timeSavedData = [{
        labels: Object.keys(roleData),
        values: Object.values(roleData).map(r => r.time_saved),
        type: 'pie',
        hole: 0.5,
        marker: {
            colors: ['#FF3621', '#10B981', '#3B82F6', '#F59E0B']
        }
    }]

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Adoption Metrics</h1>
                <p className="page-subtitle">AI tool usage and impact tracking</p>
            </div>

            {/* AI Status Banner */}
            <div className="card" style={{
                marginBottom: 'var(--spacing-lg)',
                background: aiStatus?.ai_connected ? 'var(--color-success-light)' : 'var(--color-warning-light)',
                borderColor: aiStatus?.ai_connected ? 'var(--color-success)' : 'var(--color-warning)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                        <div style={{
                            width: '12px',
                            height: '12px',
                            borderRadius: '50%',
                            background: aiStatus?.ai_connected ? 'var(--color-success)' : 'var(--color-warning)'
                        }}></div>
                        <div>
                            <strong>AI Model Status:</strong>{' '}
                            {aiStatus?.ai_connected ? 'Connected (Mistral-7B-Instruct)' : 'Not Connected'}
                        </div>
                    </div>
                    <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                        Data Mode: {aiStatus?.data_mode || 'local'}
                    </div>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="stats-grid">
                <StatCard
                    label="Total Engagements"
                    value={metrics?.total_engagements || 0}
                />
                <StatCard
                    label="AI Insights Generated"
                    value={(metrics?.total_insights_generated || 0).toLocaleString()}
                />
                <StatCard
                    label="Stored Insights"
                    value={metrics?.stored_insights || 0}
                />
                <StatCard
                    label="Est. Hours Saved"
                    value={metrics?.estimated_time_saved_hours || 0}
                    change="Based on 10 min/insight"
                />
            </div>

            {/* Charts */}
            <div className="grid-2" style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Insights by Role</h3>
                    </div>
                    <div className="chart-container">
                        <Plot
                            data={roleChartData}
                            layout={{
                                autosize: true,
                                margin: { t: 20, b: 80, l: 40, r: 20 },
                                xaxis: { tickangle: -30 },
                                yaxis: { title: 'Insights' },
                                paper_bgcolor: 'transparent',
                                plot_bgcolor: 'transparent'
                            }}
                            config={{ displayModeBar: false, responsive: true }}
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Time Saved by Role (minutes)</h3>
                    </div>
                    <div className="chart-container">
                        <Plot
                            data={timeSavedData}
                            layout={{
                                autosize: true,
                                margin: { t: 20, b: 20, l: 20, r: 20 },
                                showlegend: true,
                                legend: { orientation: 'h', y: -0.1 },
                                paper_bgcolor: 'transparent',
                                plot_bgcolor: 'transparent'
                            }}
                            config={{ displayModeBar: false, responsive: true }}
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                </div>
            </div>

            {/* Daily Trend */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Daily AI Usage Trend</h3>
                </div>
                <div className="chart-container tall">
                    <Plot
                        data={trendData}
                        layout={{
                            autosize: true,
                            margin: { t: 20, b: 60, l: 40, r: 20 },
                            xaxis: { tickangle: -45, title: 'Date' },
                            yaxis: { title: 'Insights Generated' },
                            paper_bgcolor: 'transparent',
                            plot_bgcolor: 'transparent'
                        }}
                        config={{ displayModeBar: false, responsive: true }}
                        style={{ width: '100%', height: '100%' }}
                    />
                </div>
            </div>

            {/* Role Breakdown Table */}
            <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-header">
                    <h3 className="card-title">Adoption by Role</h3>
                </div>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Role</th>
                                <th>Insights Generated</th>
                                <th>Time Saved (min)</th>
                                <th>Avg per Day</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(roleData).map(([role, data]) => (
                                <tr key={role}>
                                    <td style={{ fontWeight: 500 }}>{role}</td>
                                    <td>{data.insights.toLocaleString()}</td>
                                    <td>{data.time_saved.toLocaleString()}</td>
                                    <td>{(data.insights / 30).toFixed(1)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

export default Metrics
