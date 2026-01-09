import { useState, useEffect } from 'react';
import SearchForm from './components/SearchForm';
import LogViewer from './components/LogViewer';
import Login from './components/Login';
import { searchLogs } from './services/api';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
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
    setResults(null);
    setError(null);
  };

  const handleSearch = async (searchParams) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await searchLogs(searchParams);
      setResults(data);
    } catch (err) {
      // Check if error is authentication related
      if (err.message.includes('API Key') || err.message.includes('401') || err.message.includes('403')) {
        setError('Authentication failed. Please log in again.');
        handleLogout();
      } else {
        setError(err.message);
      }
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🔍 TraceID Log Search</h1>
          <p className="subtitle">Query Splunk logs by trace ID</p>
        </div>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </header>

      <main className="app-main">
        <div className="container">
          <SearchForm onSearch={handleSearch} isLoading={isLoading} />
          <LogViewer results={results} error={error} />
        </div>
      </main>

      <footer className="app-footer">
        <p>TraceID Log Service v1.0.0</p>
      </footer>
    </div>
  );
}

export default App;
