import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import StatusBadge from '../components/StatusBadge'
import HealthScore from '../components/HealthScore'

function Engagements() {
    const [engagements, setEngagements] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all')
    const navigate = useNavigate()

    useEffect(() => {
        fetchEngagements()
    }, [filter])

    const fetchEngagements = async () => {
        try {
            const url = filter === 'all'
                ? '/api/engagements'
                : `/api/engagements?status=${filter}`
            const response = await fetch(url)
            const data = await response.json()
            setEngagements(data)
        } catch (err) {
            console.error('Error fetching engagements:', err)
        } finally {
            setLoading(false)
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

    const formatCurrency = (value) => {
        if (!value) return '-'
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0
        }).format(value)
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
                <h1 className="page-title">Engagements</h1>
                <p className="page-subtitle">All Professional Services engagements</p>
            </div>

            {/* Filters */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                    {['all', 'Active', 'At Risk', 'Completed', 'On Hold'].map(status => (
                        <button
                            key={status}
                            className={`btn ${filter === status ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setFilter(status)}
                        >
                            {status === 'all' ? 'All' : status}
                        </button>
                    ))}
                </div>
            </div>

            {/* Engagements Table */}
            <div className="card">
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Customer</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Health</th>
                                <th>Owner</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {engagements.map(eng => (
                                <tr
                                    key={eng.engagement_id}
                                    className="engagement-row"
                                    onClick={() => navigate(`/engagements/${eng.engagement_id}`)}
                                >
                                    <td>
                                        <div className="engagement-name">{eng.customer_name}</div>
                                        <div className="engagement-type" style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-tertiary)' }}>
                                            {eng.engagement_id}
                                        </div>
                                    </td>
                                    <td>{eng.engagement_type}</td>
                                    <td><StatusBadge status={eng.status} /></td>
                                    <td><HealthScore score={eng.health_score} /></td>
                                    <td>{eng.owner_name}</td>
                                    <td>{formatDate(eng.start_date)}</td>
                                    <td>{formatDate(eng.end_date)}</td>
                                    <td>{formatCurrency(eng.contract_value)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {engagements.length === 0 && (
                    <div className="empty-state">
                        <p>No engagements found</p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Engagements
