import { useState } from 'react';
import { validateApiKey } from '../services/api';
import './Login.css';

export default function Login({ onLogin }) {
  const [apiKey, setApiKey] = useState('');
  const [error, setError] = useState('');
  const [isValidating, setIsValidating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      setError('Please enter an API key');
      return;
    }

    // Validate API key with backend
    setIsValidating(true);
    setError('');

    try {
      await validateApiKey(apiKey.trim());
      
      // API key is valid - store it and login
      localStorage.setItem('apiKey', apiKey.trim());
      onLogin(apiKey.trim());
    } catch (err) {
      // API key is invalid
      setError(err.message || 'Invalid API key. Please try again.');
      setIsValidating(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>Journey Log Search</h1>
          <p>Authentication Required</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="apiKey">API Key</label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value);
                setError('');
              }}
              placeholder="Enter your API key"
              autoFocus
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={isValidating}>
            {isValidating ? (
              <>
                <span className="spinner"></span> Validating...
              </>
            ) : (
              'Login'
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>Please contact your administrator for an API key.</p>
        </div>
      </div>
    </div>
  );
}

