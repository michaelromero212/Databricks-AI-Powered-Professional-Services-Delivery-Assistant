function InsightCard({ insight }) {
    const formatDate = (dateStr) => {
        if (!dateStr) return ''
        const date = new Date(dateStr)
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const typeLabels = {
        'health_summary': 'Health Summary',
        'risk_detection': 'Risk Detection',
        'theme_extraction': 'Theme Analysis',
        'action_recommendation': 'Recommended Actions'
    }

    return (
        <div className="insight-card">
            <div className="insight-header">
                <span className="insight-type">
                    {typeLabels[insight.insight_type] || insight.insight_type}
                </span>
                <span className="insight-time">
                    {formatDate(insight.generated_at)}
                </span>
            </div>
            <p className="insight-content">
                {insight.content}
            </p>
            {insight.customer_name && (
                <div style={{
                    marginTop: 'var(--spacing-md)',
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--text-tertiary)'
                }}>
                    {insight.customer_name}
                </div>
            )}
        </div>
    )
}

export default InsightCard
