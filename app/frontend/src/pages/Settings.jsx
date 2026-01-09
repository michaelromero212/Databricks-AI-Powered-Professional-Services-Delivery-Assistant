import { useState, useEffect, useCallback } from 'react'

function Settings() {
    const [health, setHealth] = useState(null)
    const [loading, setLoading] = useState(true)
    const [uploading, setUploading] = useState(false)
    const [generating, setGenerating] = useState(false)
    const [message, setMessage] = useState(null)

    // Databricks state
    const [notebooks, setNotebooks] = useState([])
    const [databricksStatus, setDatabricksStatus] = useState(null)
    const [runs, setRuns] = useState([])
    const [runningNotebooks, setRunningNotebooks] = useState({})

    useEffect(() => {
        checkHealth()
        fetchNotebooks()
        fetchRuns()
    }, [])

    // Poll for run status updates
    useEffect(() => {
        const activeRuns = runs.filter(r =>
            r.status === 'PENDING' || r.status === 'RUNNING'
        )

        if (activeRuns.length > 0) {
            const interval = setInterval(() => {
                activeRuns.forEach(run => pollRunStatus(run.run_id))
            }, 5000)
            return () => clearInterval(interval)
        }
    }, [runs])

    const checkHealth = async () => {
        try {
            const response = await fetch('/api/health')
            const data = await response.json()
            setHealth(data)
        } catch (err) {
            console.error('Health check failed:', err)
        } finally {
            setLoading(false)
        }
    }

    const fetchNotebooks = async () => {
        try {
            const response = await fetch('/api/notebooks')
            const data = await response.json()
            setNotebooks(data.notebooks || [])
            setDatabricksStatus({
                connected: data.connected,
                configured: data.configured
            })
        } catch (err) {
            console.error('Failed to fetch notebooks:', err)
        }
    }

    const fetchRuns = async () => {
        try {
            const response = await fetch('/api/notebooks/runs')
            const data = await response.json()
            setRuns(data.runs || [])
        } catch (err) {
            console.error('Failed to fetch runs:', err)
        }
    }

    const pollRunStatus = async (runId) => {
        try {
            const response = await fetch(`/api/notebooks/runs/${runId}`)
            const data = await response.json()

            if (data.success) {
                setRuns(prev => prev.map(r =>
                    r.run_id === runId
                        ? { ...r, status: data.status, run_page_url: data.run_page_url }
                        : r
                ))

                // Clear running state if complete
                if (['SUCCESS', 'FAILED', 'CANCELLED'].includes(data.status)) {
                    setRunningNotebooks(prev => {
                        const next = { ...prev }
                        delete next[runId]
                        return next
                    })
                }
            }
        } catch (err) {
            console.error('Failed to poll run status:', err)
        }
    }

    const runNotebook = async (notebookId) => {
        setRunningNotebooks(prev => ({ ...prev, [notebookId]: true }))
        setMessage(null)

        try {
            const response = await fetch('/api/notebooks/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notebook_id: notebookId })
            })
            const result = await response.json()

            if (response.ok && result.success) {
                setMessage({ type: 'success', text: `Started ${result.notebook_name}` })
                // Add to runs list
                setRuns(prev => [{
                    run_id: result.run_id,
                    notebook_id: result.notebook_id,
                    notebook_name: result.notebook_name,
                    submitted_at: new Date().toISOString(),
                    status: 'PENDING'
                }, ...prev])
            } else {
                setMessage({ type: 'error', text: result.detail || 'Failed to start notebook' })
                setRunningNotebooks(prev => {
                    const next = { ...prev }
                    delete next[notebookId]
                    return next
                })
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Error: ' + err.message })
            setRunningNotebooks(prev => {
                const next = { ...prev }
                delete next[notebookId]
                return next
            })
        }
    }

    const regenerateData = async () => {
        setGenerating(true)
        setMessage(null)
        try {
            const response = await fetch('/api/data/regenerate', {
                method: 'POST'
            })
            const result = await response.json()
            if (result.success) {
                setMessage({ type: 'success', text: 'Sample data regenerated successfully!' })
            } else {
                setMessage({ type: 'error', text: result.error || 'Failed to regenerate data' })
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Error: ' + err.message })
        } finally {
            setGenerating(false)
        }
    }

    const handleFileUpload = async (event, dataType) => {
        const file = event.target.files[0]
        if (!file) return

        setUploading(true)
        setMessage(null)

        const formData = new FormData()
        formData.append('file', file)
        formData.append('data_type', dataType)

        try {
            const response = await fetch('/api/data/upload-file', {
                method: 'POST',
                body: formData
            })
            const result = await response.json()
            if (result.success) {
                setMessage({ type: 'success', text: `Uploaded ${result.records} ${dataType} records` })
            } else {
                setMessage({ type: 'error', text: result.error || 'Upload failed' })
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Error: ' + err.message })
        } finally {
            setUploading(false)
            event.target.value = ''
        }
    }

    const getStatusBadge = (status) => {
        const statusStyles = {
            PENDING: 'badge-warning',
            RUNNING: 'badge-info',
            SUCCESS: 'badge-success',
            FAILED: 'badge-error',
            CANCELLED: 'badge-secondary'
        }
        return statusStyles[status] || 'badge-secondary'
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
                <h1 className="page-title">Settings & Data</h1>
                <p className="page-subtitle">System configuration and data management</p>
            </div>

            {/* Status Message */}
            {message && (
                <div className="card" style={{
                    marginBottom: 'var(--spacing-lg)',
                    background: message.type === 'success' ? 'var(--color-success-light)' : 'var(--color-error-light)',
                    borderColor: message.type === 'success' ? 'var(--color-success)' : 'var(--color-error)'
                }}>
                    {message.text}
                </div>
            )}

            {/* System Status */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <div className="card-header">
                    <h3 className="card-title">System Status</h3>
                    <button className="btn btn-secondary" onClick={checkHealth}>
                        Refresh
                    </button>
                </div>

                <div className="table-container">
                    <table>
                        <tbody>
                            <tr>
                                <td style={{ fontWeight: 500 }}>API Status</td>
                                <td>
                                    <span className="badge badge-success">
                                        {health?.status || 'Unknown'}
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td style={{ fontWeight: 500 }}>AI Model</td>
                                <td>
                                    <span className={`badge ${health?.ai_connected ? 'badge-success' : 'badge-warning'}`}>
                                        {health?.ai_connected ? 'Connected' : 'Not Connected'}
                                    </span>
                                    {health?.ai_connected && (
                                        <span style={{ marginLeft: 'var(--spacing-sm)', color: 'var(--text-secondary)' }}>
                                            Mistral-7B-Instruct
                                        </span>
                                    )}
                                </td>
                            </tr>
                            <tr>
                                <td style={{ fontWeight: 500 }}>Databricks</td>
                                <td>
                                    <span className={`badge ${databricksStatus?.connected ? 'badge-success' : databricksStatus?.configured ? 'badge-warning' : 'badge-secondary'}`}>
                                        {databricksStatus?.connected ? 'Connected' : databricksStatus?.configured ? 'Configured' : 'Not Configured'}
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td style={{ fontWeight: 500 }}>Data Mode</td>
                                <td>
                                    <span className="badge badge-info">
                                        {health?.data_mode || 'local'}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Databricks Notebooks */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <div className="card-header">
                    <h3 className="card-title">Databricks Notebooks</h3>
                    <a
                        href="https://dbc-3a8386b7-5ab6.cloud.databricks.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary"
                    >
                        Open Workspace →
                    </a>
                </div>

                {!databricksStatus?.connected && (
                    <div style={{
                        padding: 'var(--spacing-md)',
                        background: 'var(--color-warning-light)',
                        borderRadius: 'var(--radius-sm)',
                        marginBottom: 'var(--spacing-md)'
                    }}>
                        ⚠️ Databricks not connected. Set DATABRICKS_HOST, DATABRICKS_TOKEN, and DATABRICKS_CLUSTER_ID in .env
                    </div>
                )}

                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Notebook</th>
                                <th>Description</th>
                                <th>Path</th>
                                <th style={{ width: '120px' }}>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {notebooks.map(nb => (
                                <tr key={nb.id}>
                                    <td style={{ fontWeight: 500 }}>{nb.name}</td>
                                    <td style={{ color: 'var(--text-secondary)' }}>{nb.description}</td>
                                    <td><code style={{ fontSize: 'var(--font-size-xs)' }}>{nb.path}</code></td>
                                    <td>
                                        <button
                                            className="btn btn-primary"
                                            style={{ padding: '4px 12px', fontSize: 'var(--font-size-sm)' }}
                                            onClick={() => runNotebook(nb.id)}
                                            disabled={!databricksStatus?.connected || runningNotebooks[nb.id]}
                                        >
                                            {runningNotebooks[nb.id] ? '⏳ Running...' : '▶ Run'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Recent Job Runs */}
            {runs.length > 0 && (
                <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <div className="card-header">
                        <h3 className="card-title">Recent Job Runs</h3>
                        <button className="btn btn-secondary" onClick={fetchRuns}>
                            Refresh
                        </button>
                    </div>

                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Run ID</th>
                                    <th>Notebook</th>
                                    <th>Submitted</th>
                                    <th>Status</th>
                                    <th>Link</th>
                                </tr>
                            </thead>
                            <tbody>
                                {runs.slice(0, 10).map(run => (
                                    <tr key={run.run_id}>
                                        <td><code>{run.run_id}</code></td>
                                        <td>{run.notebook_name}</td>
                                        <td>{run.submitted_at ? new Date(run.submitted_at).toLocaleString() : '-'}</td>
                                        <td>
                                            <span className={`badge ${getStatusBadge(run.status)}`}>
                                                {run.status}
                                            </span>
                                        </td>
                                        <td>
                                            {run.run_page_url && (
                                                <a href={run.run_page_url} target="_blank" rel="noopener noreferrer">
                                                    View →
                                                </a>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Data Management */}
            <div className="grid-2">
                {/* Generate Sample Data */}
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Sample Data</h3>
                    </div>
                    <p style={{ marginBottom: 'var(--spacing-md)', color: 'var(--text-secondary)' }}>
                        Generate realistic mock data for testing and demonstrations.
                    </p>
                    <button
                        className="btn btn-primary"
                        onClick={regenerateData}
                        disabled={generating}
                    >
                        {generating ? 'Generating...' : 'Regenerate Sample Data'}
                    </button>
                    <p style={{
                        marginTop: 'var(--spacing-sm)',
                        fontSize: 'var(--font-size-xs)',
                        color: 'var(--text-tertiary)'
                    }}>
                        Creates 15 engagements, tasks, notes, and metrics
                    </p>
                </div>

                {/* Upload Data */}
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Upload Data</h3>
                    </div>
                    <p style={{ marginBottom: 'var(--spacing-md)', color: 'var(--text-secondary)' }}>
                        Upload JSON files to add or replace engagement data.
                    </p>

                    <div style={{ display: 'grid', gap: 'var(--spacing-sm)' }}>
                        <div>
                            <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                                <input
                                    type="file"
                                    accept=".json"
                                    style={{ display: 'none' }}
                                    onChange={(e) => handleFileUpload(e, 'engagements')}
                                    disabled={uploading}
                                />
                                📁 Upload Engagements
                            </label>
                        </div>
                        <div>
                            <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                                <input
                                    type="file"
                                    accept=".json"
                                    style={{ display: 'none' }}
                                    onChange={(e) => handleFileUpload(e, 'delivery_notes')}
                                    disabled={uploading}
                                />
                                📝 Upload Delivery Notes
                            </label>
                        </div>
                        <div>
                            <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                                <input
                                    type="file"
                                    accept=".json"
                                    style={{ display: 'none' }}
                                    onChange={(e) => handleFileUpload(e, 'tasks')}
                                    disabled={uploading}
                                />
                                ✅ Upload Tasks
                            </label>
                        </div>
                    </div>

                    {uploading && (
                        <div style={{ marginTop: 'var(--spacing-md)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                            <div className="spinner"></div>
                            <span>Uploading...</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Settings
