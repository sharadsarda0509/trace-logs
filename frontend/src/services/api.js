import axios from 'axios';

// Base URL for API - will use proxy in development, direct path in production
const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:8002';

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
      headers: {
        'Content-Type': 'application/json',
      },
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

