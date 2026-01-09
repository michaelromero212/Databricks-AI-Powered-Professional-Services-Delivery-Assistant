function StatCard({ label, value, change, changeType }) {
    return (
        <div className="stat-card">
            <div className="stat-label">{label}</div>
            <div className="stat-value">{value}</div>
            {change && (
                <div className={`stat-change ${changeType || ''}`}>
                    {change}
                </div>
            )}
        </div>
    )
}

export default StatCard
