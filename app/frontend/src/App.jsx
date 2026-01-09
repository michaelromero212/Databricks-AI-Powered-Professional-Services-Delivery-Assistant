import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Engagements from './pages/Engagements'
import EngagementDetail from './pages/EngagementDetail'
import Insights from './pages/Insights'
import Metrics from './pages/Metrics'
import Settings from './pages/Settings'

function App() {
    return (
        <div className="app-container">
            <Sidebar />
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/engagements" element={<Engagements />} />
                    <Route path="/engagements/:id" element={<EngagementDetail />} />
                    <Route path="/insights" element={<Insights />} />
                    <Route path="/metrics" element={<Metrics />} />
                    <Route path="/settings" element={<Settings />} />
                </Routes>
            </main>
        </div>
    )
}

export default App
