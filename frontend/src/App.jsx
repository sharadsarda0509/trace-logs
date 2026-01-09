import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import Login from './components/Login';
import TraceSearch from './pages/TraceSearch';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is already authenticated (API key in localStorage)
  useEffect(() => {
    const apiKey = localStorage.getItem('apiKey');
    if (apiKey) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (apiKey) => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('apiKey');
    setIsAuthenticated(false);
  };

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <BrowserRouter>
      <div className="app">
        <AppHeader onLogout={handleLogout} />
        <main className="app-main">
          <div className="container">
            <Routes>
              <Route path="/" element={<Navigate to="/trace-search" replace />} />
              <Route path="/trace-search" element={<TraceSearch />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </div>
        </main>
        <footer className="app-footer">
          <p>TraceID Log Service v1.0.0</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}

function AppHeader({ onLogout }) {
  const location = useLocation();

  return (
    <header className="app-header">
      <div className="header-content">
        <h1>🔍 TraceID Log Search</h1>
        <p className="subtitle">Query Splunk logs and analyze API performance</p>
      </div>
      
      <nav className="main-navigation">
        <Link 
          to="/trace-search" 
          className={`nav-tab ${location.pathname === '/trace-search' ? 'active' : ''}`}
        >
          📍 Trace Search
        </Link>
        <Link 
          to="/dashboard" 
          className={`nav-tab ${location.pathname === '/dashboard' ? 'active' : ''}`}
        >
          📊 API Dashboard
        </Link>
      </nav>

      <button onClick={onLogout} className="logout-button">
        Logout
      </button>
    </header>
  );
}

export default App;
