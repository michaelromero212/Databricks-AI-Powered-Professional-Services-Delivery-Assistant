import { NavLink } from 'react-router-dom'

// Icons as simple SVG components
const DashboardIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
)

const EngagementsIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
)

const InsightsIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2a10 10 0 1 0 0 20 10 10 0 1 0 0-20z" />
        <path d="M12 16v-4M12 8h.01" />
    </svg>
)

const MetricsIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M18 20V10M12 20V4M6 20v-6" />
    </svg>
)

const SettingsIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
    </svg>
)

function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <svg viewBox="0 0 32 32" fill="none">
                        <rect width="32" height="32" rx="4" fill="#FF3621" />
                        <path d="M8 10h16v2H8zM8 15h12v2H8zM8 20h8v2H8z" fill="white" />
                    </svg>
                    <span className="sidebar-logo-text">PS Assistant</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <DashboardIcon />
                    <span>Dashboard</span>
                </NavLink>

                <NavLink to="/engagements" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <EngagementsIcon />
                    <span>Engagements</span>
                </NavLink>

                <NavLink to="/insights" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <InsightsIcon />
                    <span>AI Insights</span>
                </NavLink>

                <NavLink to="/metrics" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <MetricsIcon />
                    <span>Adoption Metrics</span>
                </NavLink>

                <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <SettingsIcon />
                    <span>Settings & Data</span>
                </NavLink>
            </nav>

            <div style={{ padding: 'var(--spacing-md)', borderTop: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-tertiary)' }}>
                    Databricks PS Tooling
                </div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-tertiary)' }}>
                    v1.0.0 POC
                </div>
            </div>
        </aside>
    )
}

export default Sidebar
