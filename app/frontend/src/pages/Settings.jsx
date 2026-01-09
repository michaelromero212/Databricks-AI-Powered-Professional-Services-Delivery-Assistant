import { useState, useEffect } from 'react'

function Settings() {
    const [health, setHealth] = useState(null)
    const [loading, setLoading] = useState(true)
    const [uploading, setUploading] = useState(false)
    const [generating, setGenerating] = useState(false)
    const [message, setMessage] = useState(null)

    useEffect(() => {
        checkHealth()
    }, [])

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
            const response = await fetch('/api/data/upload', {
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
            event.target.value = '' // Reset file input
        }
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
                                <td style={{ fontWeight: 500 }}>Data Mode</td>
                                <td>
                                    <span className="badge badge-info">
                                        {health?.data_mode || 'local'}
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td style={{ fontWeight: 500 }}>Last Updated</td>
                                <td>{health?.timestamp ? new Date(health.timestamp).toLocaleString() : '-'}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

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

            {/* Databricks Integration */}
            <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-header">
                    <h3 className="card-title">Databricks Integration</h3>
                </div>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--spacing-md)' }}>
                    Notebooks are available in your Databricks workspace.
                </p>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Notebook</th>
                                <th>Path</th>
                                <th>Purpose</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style={{ fontWeight: 500 }}>01_data_ingestion</td>
                                <td><code>/Shared/ps_delivery_assistant/01_data_ingestion</code></td>
                                <td>Load data into Delta tables</td>
                            </tr>
                            <tr>
                                <td style={{ fontWeight: 500 }}>02_feature_engineering</td>
                                <td><code>/Shared/ps_delivery_assistant/02_feature_engineering</code></td>
                                <td>Create views and aggregations</td>
                            </tr>
                            <tr>
                                <td style={{ fontWeight: 500 }}>03_ai_insights</td>
                                <td><code>/Shared/ps_delivery_assistant/03_ai_insights</code></td>
                                <td>Generate AI insights in Databricks</td>
                            </tr>
                            <tr>
                                <td style={{ fontWeight: 500 }}>04_metrics_tracking</td>
                                <td><code>/Shared/ps_delivery_assistant/04_metrics_tracking</code></td>
                                <td>Track adoption metrics</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div style={{ marginTop: 'var(--spacing-md)' }}>
                    <a
                        href="https://dbc-3a8386b7-5ab6.cloud.databricks.com/browse/folders/3189197179201795?o=3002206614984756"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-primary"
                    >
                        Open Databricks Workspace →
                    </a>
                </div>
            </div>
        </div>
    )
}

export default Settings
