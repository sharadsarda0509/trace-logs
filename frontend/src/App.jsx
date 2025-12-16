import { useState } from 'react';
import SearchForm from './components/SearchForm';
import LogViewer from './components/LogViewer';
import { searchLogs } from './services/api';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (searchParams) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await searchLogs(searchParams);
      setResults(data);
    } catch (err) {
      setError(err.message);
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🔍 TraceID Log Search</h1>
          <p className="subtitle">Query Splunk logs by trace ID</p>
        </div>
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
