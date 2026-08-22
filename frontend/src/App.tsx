import { useState, useEffect } from 'react'
import './App.css'
import ReportForm from './components/ReportForm'
import ReportList from './components/ReportList'
import MatchResults from './components/MatchResults'

interface HealthStatus {
  status: string
  service: string
  version: string
}

type View = 'home' | 'matches'

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [currentView, setCurrentView] = useState<View>('home')
  const [selectedReportId, setSelectedReportId] = useState<number | null>(null)

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
    setSelectedReportId(reportId)
    setCurrentView('matches')
  }

  const handleBackToReports = () => {
    setCurrentView('home')
    setSelectedReportId(null)
    setRefreshTrigger((prev) => prev + 1)
  }

  return (
    <div className="app">
      <header className="header">
        <h1
          className="header-title"
          onClick={handleBackToReports}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') handleBackToReports();
          }}
          style={{ cursor: 'pointer' }}
          role="button"
          tabIndex={0}
        >
          University Lost & Found Matcher
        </h1>
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

        {currentView === 'home' && (
          <>
            <ReportForm onReportCreated={handleReportCreated} />
            <ReportList
              refreshTrigger={refreshTrigger}
              onViewMatches={handleViewMatches}
            />
          </>
        )}

        {currentView === 'matches' && selectedReportId && (
          <MatchResults
            reportId={selectedReportId}
            onBack={handleBackToReports}
          />
        )}
      </main>

      <footer className="footer">
        <p>University Lost & Found Matcher</p>
      </footer>
    </div>
  )
}

export default App
