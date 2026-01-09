import { useState } from 'react';
import SearchForm from '../components/SearchForm';
import LogViewer from '../components/LogViewer';
import { searchLogs } from '../services/api';

export default function TraceSearch() {
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
    <div className="page-content">
      <SearchForm onSearch={handleSearch} isLoading={isLoading} />
      <LogViewer results={results} error={error} />
    </div>
  );
}

