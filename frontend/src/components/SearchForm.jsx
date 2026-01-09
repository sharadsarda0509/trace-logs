import { useState } from 'react';
import './SearchForm.css';

export default function SearchForm({ onSearch, isLoading }) {
  const [traceId, setTraceId] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Advanced options with defaults
  const [aemService, setAemService] = useState('cm-p153560-e1607906');
  const [index, setIndex] = useState('dx_aem_engineering');
  const [aemTier, setAemTier] = useState('publish'); // Production default
  const [timeRangeHours, setTimeRangeHours] = useState(24);
  const [limit, setLimit] = useState(500);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!traceId.trim()) {
      alert('Please enter a journey ID');
      return;
    }

    onSearch({
      trace_id: traceId.trim(),
      aem_service: aemService,
      index: index,
      aem_tier: aemTier,
      time_range_hours: parseInt(timeRangeHours, 10),
      limit: parseInt(limit, 10),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <div className="form-group">
        <label htmlFor="traceId">
          Journey ID <span className="required">*</span>
        </label>
        <input
          type="text"
          id="traceId"
          value={traceId}
          onChange={(e) => setTraceId(e.target.value)}
          placeholder="Enter journey ID (e.g., abc-123-def-456)"
          disabled={isLoading}
          required
        />
      </div>

      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="toggle-advanced"
      >
        {showAdvanced ? '▼' : '▶'} Advanced Options
      </button>

      {showAdvanced && (
        <div className="advanced-options">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="aemService">
                AEM Service(s)
                <span className="field-hint"> (comma-separated for multiple)</span>
              </label>
              <input
                type="text"
                id="aemService"
                value={aemService}
                onChange={(e) => setAemService(e.target.value)}
                placeholder="e.g., cm-p153560-e1607906, cm-p123456-e7890123"
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="index">Index</label>
              <input
                type="text"
                id="index"
                value={index}
                onChange={(e) => setIndex(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="aemTier">AEM Tier</label>
              <select
                id="aemTier"
                value={aemTier}
                onChange={(e) => setAemTier(e.target.value)}
                disabled={isLoading}
              >
                <option value="publish">Publish</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="timeRangeHours">Time Range (hours)</label>
              <input
                type="number"
                id="timeRangeHours"
                value={timeRangeHours}
                onChange={(e) => setTimeRangeHours(e.target.value)}
                min="1"
                max="168"
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="limit">Result Limit</label>
              <input
                type="number"
                id="limit"
                value={limit}
                onChange={(e) => setLimit(e.target.value)}
                min="1"
                max="1000"
                disabled={isLoading}
              />
            </div>
          </div>
        </div>
      )}

      <button type="submit" className="search-button" disabled={isLoading}>
        {isLoading ? (
          <>
            <span className="spinner"></span> Searching...
          </>
        ) : (
          'Search Logs'
        )}
      </button>
    </form>
  );
}

