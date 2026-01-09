import { useState } from 'react';
import './Dashboard.css';

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState('30');

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h2>API Analytics Dashboard</h2>
        <p className="dashboard-subtitle">High-level overview of API performance and health</p>
      </div>

      <div className="dashboard-filters">
        <label>
          Time Range:
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="7">Last 7 Days</option>
            <option value="14">Last 14 Days</option>
            <option value="30">Last 30 Days</option>
          </select>
        </label>
        <button className="filter-button">Apply Filters</button>
      </div>

      <div className="metrics-cards">
        <div className="metric-card">
          <div className="metric-label">Total API Calls</div>
          <div className="metric-value">---</div>
          <div className="metric-change">Coming Soon</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Error Rate</div>
          <div className="metric-value">---%</div>
          <div className="metric-change">Coming Soon</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Avg Response Time</div>
          <div className="metric-value">--- ms</div>
          <div className="metric-change">Coming Soon</div>
        </div>
      </div>

      <div className="dashboard-placeholder">
        <div className="placeholder-icon">📊</div>
        <h3>Dashboard Under Construction</h3>
        <p>API analytics features coming soon!</p>
        <ul className="feature-list">
          <li>✓ Response code distribution charts</li>
          <li>✓ API call trends over time</li>
          <li>✓ Top errors and failure patterns</li>
          <li>✓ Endpoint performance metrics</li>
          <li>✓ Drill-down to detailed logs</li>
        </ul>
      </div>
    </div>
  );
}

