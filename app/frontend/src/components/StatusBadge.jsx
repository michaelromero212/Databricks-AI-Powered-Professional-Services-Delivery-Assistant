function StatusBadge({ status }) {
    const statusMap = {
        'Active': 'badge-success',
        'Completed': 'badge-info',
        'At Risk': 'badge-error',
        'On Hold': 'badge-warning',
        'Not Started': 'badge-neutral',
        'In Progress': 'badge-info'
    }

    const className = statusMap[status] || 'badge-neutral'

    return (
        <span className={`badge ${className}`}>
            {status}
        </span>
    )
}

export default StatusBadge
