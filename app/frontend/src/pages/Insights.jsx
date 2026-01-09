import { useState, useEffect } from 'react'
import InsightCard from '../components/InsightCard'

function Insights() {
    const [insights, setInsights] = useState([])
    const [engagements, setEngagements] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedEngagement, setSelectedEngagement] = useState('')
    const [selectedType, setSelectedType] = useState('')
    const [generating, setGenerating] = useState(false)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [insightsRes, engagementsRes] = await Promise.all([
                fetch('/api/insights'),
                fetch('/api/engagements')
            ])
            const insightsData = await insightsRes.json()
            const engagementsData = await engagementsRes.json()
            setInsights(insightsData)
            setEngagements(engagementsData)
        } catch (err) {
            console.error('Error:', err)
        } finally {
            setLoading(false)
        }
    }

    const generateInsight = async () => {
        if (!selectedEngagement) {
            alert('Please select an engagement')
            return
        }

        setGenerating(true)
        try {
            const response = await fetch('/api/insights/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    engagement_id: selectedEngagement,
                    insight_type: selectedType || 'health_summary'
                })
            })
            const result = await response.json()
            if (result.success) {
                // Refresh insights
                const insightsRes = await fetch('/api/insights')
                const insightsData = await insightsRes.json()
                setInsights(insightsData)
            } else {
                alert(result.error || 'Failed to generate insight')
            }
        } catch (err) {
            alert('Error: ' + err.message)
        } finally {
            setGenerating(false)
        }
    }

    const insightTypes = [
        { value: 'health_summary', label: 'Health Summary' },
        { value: 'risk_detection', label: 'Risk Detection' },
        { value: 'theme_extraction', label: 'Theme Analysis' },
        { value: 'action_recommendation', label: 'Next Actions' }
    ]

    // Filter insights
    let filteredInsights = insights
    if (selectedEngagement) {
        filteredInsights = filteredInsights.filter(i => i.engagement_id === selectedEngagement)
    }
    if (selectedType) {
        filteredInsights = filteredInsights.filter(i => i.insight_type === selectedType)
    }

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        )
    }

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">AI Insights</h1>
                <p className="page-subtitle">AI-generated delivery intelligence</p>
            </div>

            {/* Generate New Insight */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <div className="card-header">
                    <h3 className="card-title">Generate New Insight</h3>
                </div>
                <div style={{ display: 'flex', gap: 'var(--spacing-md)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                    <div className="form-group" style={{ margin: 0, minWidth: '250px' }}>
                        <label className="form-label">Engagement</label>
                        <select
                            className="form-select"
                            value={selectedEngagement}
                            onChange={(e) => setSelectedEngagement(e.target.value)}
                        >
                            <option value="">Select engagement...</option>
                            {engagements.map(eng => (
                                <option key={eng.engagement_id} value={eng.engagement_id}>
                                    {eng.customer_name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group" style={{ margin: 0, minWidth: '200px' }}>
                        <label className="form-label">Insight Type</label>
                        <select
                            className="form-select"
                            value={selectedType}
                            onChange={(e) => setSelectedType(e.target.value)}
                        >
                            {insightTypes.map(type => (
                                <option key={type.value} value={type.value}>
                                    {type.label}
                                </option>
                            ))}
                        </select>
                    </div>
                    <button
                        className="btn btn-primary"
                        onClick={generateInsight}
                        disabled={generating || !selectedEngagement}
                    >
                        {generating ? 'Generating...' : 'Generate Insight'}
                    </button>
                </div>
            </div>

            {/* Insights List */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Recent Insights ({filteredInsights.length})</h3>
                    {(selectedEngagement || selectedType) && (
                        <button
                            className="btn btn-secondary"
                            onClick={() => {
                                setSelectedEngagement('')
                                setSelectedType('')
                            }}
                        >
                            Clear Filters
                        </button>
                    )}
                </div>

                {filteredInsights.length === 0 ? (
                    <div className="empty-state">
                        <p>No insights found. Generate one above to get started.</p>
                    </div>
                ) : (
                    <div>
                        {filteredInsights.map((insight, idx) => (
                            <InsightCard key={idx} insight={insight} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

export default Insights
