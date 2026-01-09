function HealthScore({ score }) {
    if (score === null || score === undefined) {
        return <span className="badge badge-neutral">N/A</span>
    }

    const level = score >= 75 ? 'high' : score >= 50 ? 'medium' : 'low'

    return (
        <div className="health-score">
            <div className="health-bar">
                <div
                    className={`health-bar-fill ${level}`}
                    style={{ width: `${score}%` }}
                />
            </div>
            <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>
                {score}
            </span>
        </div>
    )
}

export default HealthScore
