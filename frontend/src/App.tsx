import { useState, useEffect } from 'react'
import './App.css'

interface HealthStatus {
  status: string
  service: string
  version: string
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setError('Unable to connect to backend'))
  }, [])

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

        <section className="placeholder-section">
          <h2>Welcome</h2>
          <p>
            This application helps university staff identify potential matches
            between lost and found item reports using an automated scoring system.
          </p>
          <p className="placeholder-text">
            🚀 Ready for Phase 2 implementation
          </p>
        </section>
      </main>

      <footer className="footer">
        <p>University Lost & Found Matcher • Phase 1 Complete</p>
      </footer>
    </div>
  )
}

export default App
