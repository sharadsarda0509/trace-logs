import axios from 'axios';

// Base URL for API - will use proxy in development, direct path in production
const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:8002';

/**
 * Get API key from localStorage
 * @returns {string|null} API key or null if not found
 */
function getApiKey() {
  return localStorage.getItem('apiKey');
}

/**
 * Get headers with API key
 * @returns {Object} Headers object with API key
 */
function getAuthHeaders() {
  const apiKey = getApiKey();
  return {
    'Content-Type': 'application/json',
    ...(apiKey && { 'X-API-Key': apiKey }),
  };
}

/**
 * Search Splunk logs by trace ID
 * @param {Object} searchParams - Search parameters
 * @param {string} searchParams.trace_id - Trace ID to search for
 * @param {string} searchParams.aem_service - AEM service identifier
 * @param {string} searchParams.index - Splunk index
 * @param {string} searchParams.aem_tier - AEM tier (author/publish)
 * @param {number} searchParams.time_range_hours - Time range in hours
 * @param {number} searchParams.limit - Maximum number of results
 * @returns {Promise<Object>} Search results
 */
export async function searchLogs(searchParams) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/logs/search`, searchParams, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error) {
    // Extract error message from response or use default
    const errorMessage = error.response?.data?.detail 
      || error.response?.data?.message 
      || error.message 
      || 'Failed to search logs';
    
    throw new Error(errorMessage);
  }
}

/**
 * Check API health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    throw new Error('Health check failed');
  }
}

/**
 * Validate API key by making a test request
 * @param {string} apiKey - API key to validate
 * @returns {Promise<boolean>} True if valid, throws error if invalid
 */
export async function validateApiKey(apiKey) {
  try {
    // Make a test request with the API key to validate it
    // We'll use the search endpoint with minimal data to test authentication
    const response = await axios.post(
      `${API_BASE_URL}/api/logs/search`,
      {
        trace_id: 'validation-test',
        aem_service: 'validation-test',
        index: 'validation-test',
        aem_tier: 'author',
        time_range_hours: 1,
        limit: 1
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        validateStatus: function (status) {
          // Consider 401/403 as "handled" errors for validation
          // 500 might mean API key is valid but other error occurred
          return status < 500;
        }
      }
    );

    // If we get 401 or 403, the API key is invalid
    if (response.status === 401 || response.status === 403) {
      throw new Error('Invalid API Key');
    }

    // Any other response (including 500 from bad parameters) means API key is valid
    return true;
  } catch (error) {
    if (error.response) {
      if (error.response.status === 401) {
        throw new Error('Invalid API Key: Authentication required');
      } else if (error.response.status === 403) {
        throw new Error('Invalid API Key: Access forbidden');
      }
    }
    // Network error or other issue
    throw new Error(error.message || 'Unable to validate API key');
  }
}

