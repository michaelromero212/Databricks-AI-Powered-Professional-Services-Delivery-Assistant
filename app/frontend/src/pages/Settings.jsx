import { useState, useEffect } from 'react'

function Settings() {
    const [health, setHealth] = useState(null)
    const [loading, setLoading] = useState(true)
    const [uploading, setUploading] = useState(false)
    const [generating, setGenerating] = useState(false)
    const [syncing, setSyncing] = useState(false)
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

    // Step 1: Load data locally
    const regenerateData = async () => {
        setGenerating(true)
        setMessage(null)
        try {
            const response = await fetch('/api/data/regenerate', { method: 'POST' })
            const result = await response.json()
            if (result.success) {
                setMessage({ type: 'success', text: '✓ Step 1 Complete: Sample data generated locally' })
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
                setMessage({ type: 'success', text: `✓ Step 1 Complete: Uploaded ${result.records} ${dataType} records` })
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

    // Step 2: Sync to Databricks
    const syncToDataricks = async () => {
        setSyncing(true)
        setMessage(null)
        try {
            const response = await fetch('/api/notebooks/sync', { method: 'POST' })
            const result = await response.json()
            if (response.ok && result.success) {
                setMessage({ type: 'success', text: `✓ Step 2 Complete: Synced ${result.synced}/${result.total} files to Databricks` })
            } else if (response.ok) {
                setMessage({ type: 'warning', text: `Partial sync: ${result.synced}/${result.total} files` })
            } else {
                setMessage({ type: 'error', text: result.detail || 'Sync failed' })
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Error: ' + err.message })
        } finally {
            setSyncing(false)
        }
    }

    // Step 3: Run notebook
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
                setMessage({ type: 'success', text: `✓ Step 3 Started: ${result.notebook_name} is running...` })
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

    const stepStyle = {
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--spacing-md)',
        padding: 'var(--spacing-lg)',
        background: 'var(--bg-secondary)',
        borderRadius: 'var(--radius-md)',
        marginBottom: 'var(--spacing-md)'
    }

    const stepNumberStyle = {
        width: '36px',
        height: '36px',
        borderRadius: '50%',
        background: 'var(--color-primary)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        fontSize: 'var(--font-size-lg)',
        flexShrink: 0
    }

    const stepContentStyle = {
        flex: 1
    }

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Settings & Data</h1>
                <p className="page-subtitle">Configure data pipeline and manage system settings</p>
            </div>

            {/* Status Message */}
            {message && (
                <div className="card" style={{
                    marginBottom: 'var(--spacing-lg)',
                    background: message.type === 'success' ? 'var(--color-success-light)' :
                        message.type === 'warning' ? 'var(--color-warning-light)' : 'var(--color-error-light)',
                    borderColor: message.type === 'success' ? 'var(--color-success)' :
                        message.type === 'warning' ? 'var(--color-warning)' : 'var(--color-error)'
                }}>
                    {message.text}
                </div>
            )}

            {/* System Status */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <div className="card-header">
                    <h3 className="card-title">System Status</h3>
                    <button className="btn btn-secondary" onClick={checkHealth}>Refresh</button>
                </div>
                <div style={{ display: 'flex', gap: 'var(--spacing-lg)', flexWrap: 'wrap' }}>
                    <div>
                        <span style={{ color: 'var(--text-secondary)', marginRight: 'var(--spacing-sm)' }}>API:</span>
                        <span className="badge badge-success">{health?.status || 'Unknown'}</span>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-secondary)', marginRight: 'var(--spacing-sm)' }}>AI Model:</span>
                        <span className={`badge ${health?.ai_connected ? 'badge-success' : 'badge-warning'}`}>
                            {health?.ai_connected ? 'Connected' : 'Not Connected'}
                        </span>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-secondary)', marginRight: 'var(--spacing-sm)' }}>Databricks:</span>
                        <span className={`badge ${databricksStatus?.connected ? 'badge-success' : 'badge-warning'}`}>
                            {databricksStatus?.connected ? 'Connected' : 'Not Connected'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Data Pipeline Workflow */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <div className="card-header">
                    <h3 className="card-title">Data Pipeline Workflow</h3>
                    <a
                        href="https://dbc-3a8386b7-5ab6.cloud.databricks.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary"
                    >
                        Open Databricks →
                    </a>
                </div>

                <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--spacing-lg)' }}>
                    Follow these steps to load data into Databricks Delta tables:
                </p>

                {/* Step 1 */}
                <div style={stepStyle}>
                    <div style={stepNumberStyle}>1</div>
                    <div style={stepContentStyle}>
                        <h4 style={{ margin: '0 0 var(--spacing-sm) 0' }}>Load Data Locally</h4>
                        <p style={{ color: 'var(--text-secondary)', margin: '0 0 var(--spacing-md) 0', fontSize: 'var(--font-size-sm)' }}>
                            Generate sample data or upload your own JSON files
                        </p>
                        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap' }}>
                            <button
                                className="btn btn-primary"
                                onClick={regenerateData}
                                disabled={generating}
                            >
                                {generating ? '⏳ Generating...' : '🎲 Generate Sample Data'}
                            </button>
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
                            <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                                <input
                                    type="file"
                                    accept=".json"
                                    style={{ display: 'none' }}
                                    onChange={(e) => handleFileUpload(e, 'delivery_notes')}
                                    disabled={uploading}
                                />
                                📝 Upload Notes
                            </label>
                        </div>
                    </div>
                </div>

                {/* Step 2 */}
                <div style={stepStyle}>
                    <div style={stepNumberStyle}>2</div>
                    <div style={stepContentStyle}>
                        <h4 style={{ margin: '0 0 var(--spacing-sm) 0' }}>Sync to Databricks</h4>
                        <p style={{ color: 'var(--text-secondary)', margin: '0 0 var(--spacing-md) 0', fontSize: 'var(--font-size-sm)' }}>
                            Upload local data files to Unity Catalog Volumes
                        </p>
                        <button
                            className="btn btn-primary"
                            onClick={syncToDataricks}
                            disabled={!databricksStatus?.connected || syncing}
                        >
                            {syncing ? '⏳ Syncing...' : '☁️ Sync Data to Databricks'}
                        </button>
                        {!databricksStatus?.connected && (
                            <span style={{ marginLeft: 'var(--spacing-sm)', color: 'var(--color-warning)', fontSize: 'var(--font-size-sm)' }}>
                                ⚠️ Databricks not connected
                            </span>
                        )}
                    </div>
                </div>

                {/* Step 3 */}
                <div style={stepStyle}>
                    <div style={stepNumberStyle}>3</div>
                    <div style={stepContentStyle}>
                        <h4 style={{ margin: '0 0 var(--spacing-sm) 0' }}>Process in Databricks</h4>
                        <p style={{ color: 'var(--text-secondary)', margin: '0 0 var(--spacing-md) 0', fontSize: 'var(--font-size-sm)' }}>
                            Run the ingestion notebook to create Delta tables
                        </p>
                        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap' }}>
                            {notebooks.map(nb => (
                                <button
                                    key={nb.id}
                                    className="btn btn-primary"
                                    onClick={() => runNotebook(nb.id)}
                                    disabled={!databricksStatus?.connected || runningNotebooks[nb.id]}
                                    title={nb.description}
                                >
                                    {runningNotebooks[nb.id] ? '⏳' : '▶'} {nb.name}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Job Runs */}
            {runs.length > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Recent Job Runs</h3>
                        <button className="btn btn-secondary" onClick={fetchRuns}>Refresh</button>
                    </div>

                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Notebook</th>
                                    <th>Submitted</th>
                                    <th>Status</th>
                                    <th>View</th>
                                </tr>
                            </thead>
                            <tbody>
                                {runs.slice(0, 5).map(run => (
                                    <tr key={run.run_id}>
                                        <td>{run.notebook_name}</td>
                                        <td>{run.submitted_at ? new Date(run.submitted_at).toLocaleTimeString() : '-'}</td>
                                        <td>
                                            <span className={`badge ${getStatusBadge(run.status)}`}>
                                                {run.status}
                                            </span>
                                        </td>
                                        <td>
                                            {run.run_page_url ? (
                                                <a href={run.run_page_url} target="_blank" rel="noopener noreferrer">
                                                    View →
                                                </a>
                                            ) : '-'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Settings
