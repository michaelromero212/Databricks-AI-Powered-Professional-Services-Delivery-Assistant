import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Plot from 'react-plotly.js'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import HealthScore from '../components/HealthScore'
import InsightCard from '../components/InsightCard'

function Dashboard() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    useEffect(() => {
        fetchDashboard()
    }, [])

    const fetchDashboard = async () => {
        try {
            const response = await fetch('/api/dashboard')
            if (!response.ok) throw new Error('Failed to fetch dashboard data')
            const result = await response.json()
            setData(result)
        } catch (err) {
            setError(err.message)
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

    if (error) {
        return (
            <div className="empty-state">
                <p>Error loading dashboard: {error}</p>
                <button className="btn btn-primary" onClick={fetchDashboard}>
                    Retry
                </button>
            </div>
        )
    }

    const { engagements, health_distribution, metrics, recent_insights } = data

    // Health distribution chart data
    const healthChartData = [{
        values: [
            health_distribution.healthy,
            health_distribution.warning,
            health_distribution.critical
        ],
        labels: ['Healthy (75+)', 'Warning (50-74)', 'Critical (<50)'],
        type: 'pie',
        hole: 0.6,
        marker: {
            colors: ['#10B981', '#F59E0B', '#EF4444']
        },
        textinfo: 'value',
        textposition: 'inside'
    }]

    // Daily insights trend
    const trendData = [{
        x: metrics.daily_trend?.map(d => d.date) || [],
        y: metrics.daily_trend?.map(d => d.insights) || [],
        type: 'scatter',
        mode: 'lines+markers',
        fill: 'tozeroy',
        fillcolor: 'rgba(255, 54, 33, 0.1)',
        line: { color: '#FF3621', width: 2 },
        marker: { size: 6 }
    }]

    // At-risk engagements
    const atRiskEngagements = engagements.filter(e =>
        e.status === 'At Risk' || (e.health_score && e.health_score < 50)
    ).slice(0, 5)

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Dashboard</h1>
                <p className="page-subtitle">Professional Services delivery overview</p>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <StatCard
                    label="Active Engagements"
                    value={metrics.active_engagements}
                />
                <StatCard
                    label="At Risk"
                    value={metrics.at_risk_engagements}
                />
                <StatCard
                    label="AI Insights Generated"
                    value={metrics.total_insights_generated?.toLocaleString() || '0'}
                />
                <StatCard
                    label="Est. Hours Saved"
                    value={metrics.estimated_time_saved_hours || '0'}
                    change="+12% this week"
                    changeType="positive"
                />
            </div>

            {/* Charts Row */}
            <div className="grid-2" style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Engagement Health Distribution</h3>
                    </div>
                    <div className="chart-container">
                        <Plot
                            data={healthChartData}
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

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">AI Insights Trend (30 Days)</h3>
                    </div>
                    <div className="chart-container">
                        <Plot
                            data={trendData}
                            layout={{
                                autosize: true,
                                margin: { t: 20, b: 40, l: 40, r: 20 },
                                xaxis: {
                                    showgrid: false,
                                    tickangle: -45
                                },
                                yaxis: {
                                    showgrid: true,
                                    gridcolor: '#E2E8F0'
                                },
                                paper_bgcolor: 'transparent',
                                plot_bgcolor: 'transparent'
                            }}
                            config={{ displayModeBar: false, responsive: true }}
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                </div>
            </div>

            {/* At-Risk Engagements and Recent Insights */}
            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Needs Attention</h3>
                        <button
                            className="btn btn-secondary"
                            onClick={() => navigate('/engagements')}
                        >
                            View All
                        </button>
                    </div>

                    {atRiskEngagements.length === 0 ? (
                        <div className="empty-state">
                            <p>No at-risk engagements 🎉</p>
                        </div>
                    ) : (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Customer</th>
                                        <th>Status</th>
                                        <th>Health</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {atRiskEngagements.map(eng => (
                                        <tr
                                            key={eng.engagement_id}
                                            className="engagement-row"
                                            onClick={() => navigate(`/engagements/${eng.engagement_id}`)}
                                        >
                                            <td>
                                                <div className="engagement-name">{eng.customer_name}</div>
                                                <div className="engagement-type">{eng.engagement_type}</div>
                                            </td>
                                            <td><StatusBadge status={eng.status} /></td>
                                            <td><HealthScore score={eng.health_score} /></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Recent AI Insights</h3>
                        <button
                            className="btn btn-secondary"
                            onClick={() => navigate('/insights')}
                        >
                            View All
                        </button>
                    </div>

                    {(!recent_insights || recent_insights.length === 0) ? (
                        <div className="empty-state">
                            <p>No insights generated yet</p>
                            <button className="btn btn-primary" onClick={() => navigate('/insights')}>
                                Generate Insights
                            </button>
                        </div>
                    ) : (
                        <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                            {recent_insights.slice(0, 3).map((insight, idx) => (
                                <InsightCard key={idx} insight={insight} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Dashboard
