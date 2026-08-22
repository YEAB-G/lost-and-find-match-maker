import { useState, useEffect } from 'react'
import './App.css'
import ReportForm from './components/ReportForm'
import ReportList from './components/ReportList'

interface HealthStatus {
  status: string
  service: string
  version: string
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setError('Unable to connect to backend'))
  }, [])

  const handleReportCreated = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  const handleViewMatches = (reportId: number) => {
    // Phase 7 will implement this
    console.log('View matches for report:', reportId)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>University Lost & Found Matcher</h1>
        <p className="subtitle">
          Help reunite students with their lost items
        </p>
      </header>

      <main className="main">
        <section className="status-section">
          <h2>System Status</h2>
          {error ? (
            <div className="status-error">
              <span className="status-icon">⚠️</span>
              <span>{error}</span>
            </div>
          ) : health ? (
            <div className="status-connected">
              <span className="status-icon">✅</span>
              <span>Backend connected ({health.service} v{health.version})</span>
            </div>
          ) : (
            <div className="status-loading">
              <span className="status-icon">⏳</span>
              <span>Connecting to backend...</span>
            </div>
          )}
        </section>

        <ReportForm onReportCreated={handleReportCreated} />

        <ReportList
          refreshTrigger={refreshTrigger}
          onViewMatches={handleViewMatches}
        />
      </main>

      <footer className="footer">
        <p>University Lost & Found Matcher • Phase 8 Complete</p>
      </footer>
    </div>
  )
}

export default App
