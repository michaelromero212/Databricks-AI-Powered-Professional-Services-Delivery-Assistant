import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import StatusBadge from '../components/StatusBadge'
import HealthScore from '../components/HealthScore'
import InsightCard from '../components/InsightCard'

function EngagementDetail() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [engagement, setEngagement] = useState(null)
    const [insights, setInsights] = useState([])
    const [loading, setLoading] = useState(true)
    const [generating, setGenerating] = useState(false)
    const [activeTab, setActiveTab] = useState('overview')

    const fetchEngagement = useCallback(async () => {
        try {
            const response = await fetch(`/api/engagements/${id}`)
            if (!response.ok) throw new Error('Engagement not found')
            const data = await response.json()
            setEngagement(data)
        } catch (err) {
            console.error('Error:', err)
        } finally {
            setLoading(false)
        }
    }, [id])

    const fetchInsights = useCallback(async () => {
        try {
            const response = await fetch(`/api/insights?engagement_id=${id}`)
            const data = await response.json()
            setInsights(data)
        } catch (err) {
            console.error('Error fetching insights:', err)
        }
    }, [id])

    useEffect(() => {
        fetchEngagement()
        fetchInsights()
    }, [fetchEngagement, fetchInsights])

    const generateInsight = async (insightType) => {
        setGenerating(true)
        try {
            const response = await fetch('/api/insights/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    engagement_id: id,
                    insight_type: insightType
                })
            })
            const result = await response.json()
            if (result.success) {
                fetchInsights() // Refresh insights
            } else {
                alert(result.error || 'Failed to generate insight')
            }
        } catch (err) {
            alert('Error generating insight: ' + err.message)
        } finally {
            setGenerating(false)
        }
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return '-'
        return new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        })
    }

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        )
    }

    if (!engagement) {
        return (
            <div className="empty-state">
                <p>Engagement not found</p>
                <button className="btn btn-primary" onClick={() => navigate('/engagements')}>
                    Back to Engagements
                </button>
            </div>
        )
    }

    const completedTasks = engagement.tasks?.filter(t => t.status === 'Completed').length || 0
    const totalTasks = engagement.tasks?.length || 0
    const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

    return (
        <div>
            {/* Back Button */}
            <button
                className="btn btn-secondary"
                onClick={() => navigate('/engagements')}
                style={{ marginBottom: 'var(--spacing-md)' }}
            >
                ← Back to Engagements
            </button>

            {/* Header */}
            <div className="detail-header">
                <div>
                    <h1 className="detail-title">{engagement.customer_name}</h1>
                    <div className="detail-meta">
                        <span className="meta-item">{engagement.engagement_type}</span>
                        <span className="meta-item">{engagement.engagement_id}</span>
                        <StatusBadge status={engagement.status} />
                    </div>
                </div>
                <div>
                    <HealthScore score={engagement.health_score} />
                </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
                <button
                    className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    Overview
                </button>
                <button
                    className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tasks')}
                >
                    Tasks ({totalTasks})
                </button>
                <button
                    className={`tab ${activeTab === 'notes' ? 'active' : ''}`}
                    onClick={() => setActiveTab('notes')}
                >
                    Delivery Notes ({engagement.notes?.length || 0})
                </button>
                <button
                    className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
                    onClick={() => setActiveTab('insights')}
                >
                    AI Insights ({insights.length})
                </button>
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
                <div className="grid-2">
                    <div className="card">
                        <h3 className="card-title" style={{ marginBottom: 'var(--spacing-md)' }}>
                            Engagement Details
                        </h3>
                        <div style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                            <div>
                                <div className="stat-label">Owner</div>
                                <div style={{ fontWeight: 500 }}>{engagement.owner_name}</div>
                            </div>
                            <div>
                                <div className="stat-label">Timeline</div>
                                <div>{formatDate(engagement.start_date)} → {formatDate(engagement.end_date)}</div>
                            </div>
                            <div>
                                <div className="stat-label">Contract Value</div>
                                <div style={{ fontWeight: 500 }}>
                                    ${(engagement.contract_value || 0).toLocaleString()}
                                </div>
                            </div>
                            <div>
                                <div className="stat-label">Progress</div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                    <div className="progress-bar" style={{ flex: 1 }}>
                                        <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
                                    </div>
                                    <span>{progressPercent}%</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <h3 className="card-title" style={{ marginBottom: 'var(--spacing-md)' }}>
                            Team Members
                        </h3>
                        <div style={{ display: 'grid', gap: 'var(--spacing-sm)' }}>
                            {engagement.team_members?.map((member, idx) => (
                                <div key={idx} style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    padding: 'var(--spacing-sm)',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--border-radius-md)'
                                }}>
                                    <span style={{ fontWeight: 500 }}>{member.name}</span>
                                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>
                                        {member.role}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Tasks Tab */}
            {activeTab === 'tasks' && (
                <div className="card">
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Task</th>
                                    <th>Phase</th>
                                    <th>Status</th>
                                    <th>Progress</th>
                                    <th>Start</th>
                                    <th>End</th>
                                </tr>
                            </thead>
                            <tbody>
                                {engagement.tasks?.map(task => (
                                    <tr key={task.task_id}>
                                        <td style={{ fontWeight: 500 }}>{task.name}</td>
                                        <td>
                                            <span className="badge badge-neutral">{task.phase}</span>
                                        </td>
                                        <td><StatusBadge status={task.status} /></td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                                <div className="progress-bar" style={{ width: '60px' }}>
                                                    <div className="progress-fill" style={{ width: `${task.progress_percent}%` }}></div>
                                                </div>
                                                <span>{task.progress_percent}%</span>
                                            </div>
                                        </td>
                                        <td>{formatDate(task.start_date)}</td>
                                        <td>{formatDate(task.end_date)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Notes Tab */}
            {activeTab === 'notes' && (
                <div className="card">
                    <div style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                        {engagement.notes?.map(note => (
                            <div
                                key={note.note_id}
                                style={{
                                    padding: 'var(--spacing-md)',
                                    background: note.sentiment === 'risk' ? 'var(--color-error-light)' :
                                        note.sentiment === 'positive' ? 'var(--color-success-light)' :
                                            'var(--bg-secondary)',
                                    borderRadius: 'var(--border-radius-md)',
                                    borderLeft: `3px solid ${note.sentiment === 'risk' ? 'var(--color-error)' :
                                            note.sentiment === 'positive' ? 'var(--color-success)' :
                                                'var(--color-gray-300)'
                                        }`
                                }}
                            >
                                <div style={{
                                    fontSize: 'var(--font-size-xs)',
                                    color: 'var(--text-tertiary)',
                                    marginBottom: 'var(--spacing-xs)'
                                }}>
                                    {formatDate(note.created_at)}
                                </div>
                                <p style={{ margin: 0 }}>{note.content}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Insights Tab */}
            {activeTab === 'insights' && (
                <div>
                    {/* Generate Buttons */}
                    <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <div className="card-header">
                            <h3 className="card-title">Generate AI Insight</h3>
                        </div>
                        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap' }}>
                            <button
                                className="btn btn-primary"
                                onClick={() => generateInsight('health_summary')}
                                disabled={generating}
                            >
                                {generating ? 'Generating...' : 'Health Summary'}
                            </button>
                            <button
                                className="btn btn-secondary"
                                onClick={() => generateInsight('risk_detection')}
                                disabled={generating}
                            >
                                Risk Detection
                            </button>
                            <button
                                className="btn btn-secondary"
                                onClick={() => generateInsight('theme_extraction')}
                                disabled={generating}
                            >
                                Theme Analysis
                            </button>
                            <button
                                className="btn btn-secondary"
                                onClick={() => generateInsight('action_recommendation')}
                                disabled={generating}
                            >
                                Next Actions
                            </button>
                        </div>
                    </div>

                    {/* Insights List */}
                    {insights.length === 0 ? (
                        <div className="empty-state">
                            <p>No insights generated yet. Click a button above to generate AI insights.</p>
                        </div>
                    ) : (
                        <div>
                            {insights.map((insight, idx) => (
                                <InsightCard key={idx} insight={insight} />
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export default EngagementDetail
