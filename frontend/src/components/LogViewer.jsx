import ReactJson from 'react-json-view';
import './LogViewer.css';

export default function LogViewer({ results, error }) {
  if (error) {
    return (
      <div className="log-viewer">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  const { success, trace_id, total_count, logs, query_time_seconds } = results;

  return (
    <div className="log-viewer">
      <div className="results-header">
        <h2>Search Results</h2>
        <div className="results-summary">
          <div className="summary-item">
            <span className="label">Journey ID:</span>
            <span className="value">{trace_id}</span>
          </div>
          <div className="summary-item">
            <span className="label">Total Logs:</span>
            <span className="value count">{total_count}</span>
          </div>
          <div className="summary-item">
            <span className="label">Query Time:</span>
            <span className="value">{query_time_seconds}s</span>
          </div>
        </div>
      </div>

      {total_count === 0 ? (
        <div className="no-results">
          <p>No logs found for this journey ID.</p>
          <p className="hint">Try adjusting the time range or check if the journey ID is correct.</p>
        </div>
      ) : (
        <div className="logs-container">
          <div className="logs-header">
            <h3>Log Entries ({total_count})</h3>
            <button
              className="copy-button"
              onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(logs, null, 2));
                alert('Logs copied to clipboard!');
              }}
            >
              📋 Copy JSON
            </button>
          </div>
          
          {logs.map((log, index) => (
            <div key={index} className="log-entry">
              <div className="log-entry-header">
                <span className="log-index">Log #{index + 1}</span>
                {log._time && (
                  <span className="log-time">{log._time}</span>
                )}
                {log.level && (
                  <span className={`log-level level-${log.level.toLowerCase()}`}>
                    {log.level}
                  </span>
                )}
              </div>
              
              <ReactJson
                src={log}
                theme="rjv-default"
                collapsed={1}
                displayDataTypes={false}
                displayObjectSize={true}
                enableClipboard={true}
                name={false}
                indentWidth={2}
                collapseStringsAfterLength={100}
                style={{
                  padding: '1rem',
                  borderRadius: '4px',
                  fontSize: '0.9rem',
                }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

