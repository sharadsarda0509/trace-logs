import { useState, useEffect } from 'react';
import { getAnalyticsSummary } from '../services/api';
import './Dashboard.css';

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState('7');
  const [aemService, setAemService] = useState('cm-p153560-e1607906');
  const [index, setIndex] = useState('dx_aem_engineering');
  const [aemTier, setAemTier] = useState('publish'); // Production default
  
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch analytics on component mount and when filters change
  useEffect(() => {
    fetchAnalytics();
  }, []); // Initial load only

  const fetchAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getAnalyticsSummary({
        aem_service: aemService,
        index: index,
        aem_tier: aemTier,
        time_range_days: parseInt(timeRange),
      });
      setAnalytics(data);
    } catch (err) {
      setError(err.message);
      console.error('Analytics error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyFilters = () => {
    fetchAnalytics();
  };

  const formatNumber = (num) => {
    return num ? num.toLocaleString() : '0';
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h2>API Analytics Dashboard</h2>
        <p className="dashboard-subtitle">High-level overview of API performance and health</p>
      </div>

      <div className="dashboard-filters">
        <label>
          Service(s):
          <span className="field-hint"> (comma-separated)</span>
          <input
            type="text"
            value={aemService}
            onChange={(e) => setAemService(e.target.value)}
            placeholder="e.g., cm-p153560-e1607906, cm-p123456-e7890123"
            disabled={isLoading}
          />
        </label>
        <label>
          Index:
          <input
            type="text"
            value={index}
            onChange={(e) => setIndex(e.target.value)}
            disabled={isLoading}
          />
        </label>
        <label>
          Tier:
          <select value={aemTier} onChange={(e) => setAemTier(e.target.value)} disabled={isLoading}>
            <option value="publish">Publish</option>
          </select>
        </label>
        <label>
          Time Range:
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)} disabled={isLoading}>
            <option value="1">Last 1 Day</option>
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
          </select>
        </label>
        <button className="filter-button" onClick={handleApplyFilters} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Apply Filters'}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      {isLoading && (
        <div className="loading-banner">
          <div className="spinner"></div> Loading analytics data...
        </div>
      )}

      {analytics && (
        <>
          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-label">Total API Calls</div>
              <div className="metric-value">{formatNumber(analytics.summary.total_calls)}</div>
              <div className="metric-change">Last {timeRange} day{timeRange > 1 ? 's' : ''}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Error Rate</div>
              <div className="metric-value">{analytics.summary.error_rate}%</div>
              <div className="metric-change">{formatNumber(analytics.summary.total_errors)} errors</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Unique Endpoints</div>
              <div className="metric-value">{analytics.summary.unique_endpoints}</div>
              <div className="metric-change">Monitored APIs</div>
            </div>
          </div>

          <div className="response-code-section">
            <h3>Response Code Distribution</h3>
            <div className="response-codes-grid">
              {Object.entries(analytics.response_codes).map(([code, data]) => (
                <div key={code} className={`response-code-item code-${code}`}>
                  <div className="code-label">HTTP {code}</div>
                  <div className="code-count">{formatNumber(data.count)}</div>
                  <div className="code-percentage">{data.percentage}%</div>
                </div>
              ))}
            </div>
          </div>

          {analytics.top_errors && analytics.top_errors.length > 0 && (
            <div className="errors-section">
              <h3>Top Errors</h3>
              <div className="errors-table">
                <table>
                  <thead>
                    <tr>
                      <th>Endpoint</th>
                      <th>Code</th>
                      <th>Count</th>
                      <th>Message</th>
                      <th>Last Seen</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.top_errors.slice(0, 10).map((error, idx) => (
                      <tr key={idx}>
                        <td className="endpoint-cell">{error.endpoint}</td>
                        <td className="code-cell">{error.response_code}</td>
                        <td className="count-cell">{formatNumber(error.count)}</td>
                        <td className="message-cell">{error.message}</td>
                        <td className="time-cell">{new Date(error.last_seen).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {analytics.endpoints && analytics.endpoints.length > 0 && (
            <div className="endpoints-section">
              <h3>Endpoint Performance</h3>
              <div className="endpoints-table">
                <table>
                  <thead>
                    <tr>
                      <th>Endpoint</th>
                      <th>Total Calls</th>
                      <th>Errors</th>
                      <th>Error Rate</th>
                      <th>Avg Response Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.endpoints.slice(0, 10).map((endpoint, idx) => (
                      <tr key={idx}>
                        <td className="endpoint-cell">{endpoint.path}</td>
                        <td className="count-cell">{formatNumber(endpoint.total_calls)}</td>
                        <td className="count-cell">{formatNumber(endpoint.error_count)}</td>
                        <td className="rate-cell">{endpoint.error_rate}%</td>
                        <td className="time-cell">{endpoint.avg_response_time_ms.toFixed(2)} ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="query-info">
            Query completed in {analytics.query_time_seconds}s
          </div>
        </>
      )}

      {!analytics && !isLoading && !error && (
        <div className="dashboard-placeholder">
          <h3>Click "Apply Filters" to Load Analytics</h3>
          <p>Configure your filters above and click Apply to see dashboard metrics.</p>
        </div>
      )}
    </div>
  );
}

