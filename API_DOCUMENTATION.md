# TraceID Log Service - API Documentation

**Version:** 1.0.0  
**Base URL:** `https://traceid-log-service.onrender.com` (or your deployment URL)  
**Protocol:** HTTPS  
**Authentication:** API Key (X-API-Key header)

---

## Overview

The TraceID Log Service API provides a simple and secure way to search Splunk logs by trace ID. It's designed for querying Adobe Experience Manager (AEM) logs across different services, environments, and time ranges.

### Key Features

- 🔍 **Trace ID Search** - Find all logs related to a specific trace ID
- 🔐 **Secure Authentication** - API key-based access control
- ⚡ **Fast Queries** - Optimized Splunk queries with retry logic
- 📊 **Flexible Filtering** - Filter by service, index, tier, and time range
- 🎯 **Result Limiting** - Control the number of results returned

---

## Authentication

All API requests (except `/health`) require authentication using an API key.

### Required Header

```http
X-API-Key: your-api-key-here
```

### Example

```bash
curl -X POST https://traceid-log-service.onrender.com/api/logs/search \
  -H "X-API-Key: n5a-BCkPunZNt2VkscD-VhRYhJWvX1HIHKbrjjk-uco" \
  -H "Content-Type: application/json" \
  -d '{"trace_id": "abc-123-def-456", ...}'
```

### Authentication Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| `401` | Missing API Key | `X-API-Key` header not provided |
| `403` | Invalid API Key | API key is incorrect or expired |

---

## Endpoints

### 1. Search Logs by Trace ID

Retrieves all log entries from Splunk matching the specified trace ID.

#### Endpoint

```
POST /api/logs/search
```

#### Request Headers

```http
Content-Type: application/json
X-API-Key: your-api-key-here
```

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `trace_id` | string | ✅ Yes | - | The trace ID to search for (e.g., "abc-123-def-456") |
| `aem_service` | string | ✅ Yes | - | AEM service identifier (e.g., "cm-p153560-e1607906") |
| `index` | string | ✅ Yes | - | Splunk index to search (e.g., "dx_aem_engineering") |
| `aem_tier` | string | ✅ Yes | - | AEM tier: "author" or "publish" |
| `time_range_hours` | integer | ❌ No | 24 | Hours to search back (1-168) |
| `limit` | integer | ❌ No | 500 | Maximum results to return (1-1000) |

#### Example Request

```bash
curl -X POST https://traceid-log-service.onrender.com/api/logs/search \
  -H "X-API-Key: n5a-BCkPunZNt2VkscD-VhRYhJWvX1HIHKbrjjk-uco" \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "abc-123-def-456",
    "aem_service": "cm-p153560-e1607906",
    "index": "dx_aem_engineering",
    "aem_tier": "author",
    "time_range_hours": 24,
    "limit": 500
  }'
```

#### Request Body (JSON)

```json
{
  "trace_id": "abc-123-def-456",
  "aem_service": "cm-p153560-e1607906",
  "index": "dx_aem_engineering",
  "aem_tier": "author",
  "time_range_hours": 24,
  "limit": 500
}
```

#### Response (Success - 200 OK)

```json
{
  "success": true,
  "trace_id": "abc-123-def-456",
  "total_count": 42,
  "query_time_seconds": 1.23,
  "logs": [
    {
      "_time": "2024-01-15T10:30:00.000Z",
      "level": "ERROR",
      "msg": "Connection timeout to external service",
      "aem_service": "cm-p153560-e1607906",
      "aem_tier": "author",
      "traceId": "abc-123-def-456",
      "userId": "user@example.com",
      "path": "/content/page.html",
      "_raw": "2024-01-15 10:30:00 ERROR [pool-1-thread-3] Connection timeout...",
      "host": "aem-author-12345",
      "source": "/var/log/aem/error.log"
    },
    {
      "_time": "2024-01-15T10:29:58.500Z",
      "level": "INFO",
      "msg": "Request started",
      "aem_service": "cm-p153560-e1607906",
      "aem_tier": "author",
      "traceId": "abc-123-def-456",
      "userId": "user@example.com",
      "path": "/content/page.html",
      "_raw": "2024-01-15 10:29:58 INFO [pool-1-thread-3] Request started...",
      "host": "aem-author-12345",
      "source": "/var/log/aem/request.log"
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the search completed successfully |
| `trace_id` | string | The trace ID that was searched |
| `total_count` | integer | Number of log entries returned |
| `query_time_seconds` | float | Time taken to execute the Splunk query |
| `logs` | array | Array of log entry objects (see below) |

#### Log Entry Object

Each log entry in the `logs` array contains Splunk fields. Common fields include:

| Field | Type | Description |
|-------|------|-------------|
| `_time` | string | Timestamp (ISO 8601 format) |
| `level` | string | Log level (ERROR, WARN, INFO, DEBUG) |
| `msg` | string | Log message |
| `traceId` | string | Trace ID |
| `aem_service` | string | AEM service identifier |
| `aem_tier` | string | AEM tier (author/publish) |
| `userId` | string | User ID (if available) |
| `path` | string | Request path (if available) |
| `_raw` | string | Raw log line from Splunk |
| `host` | string | Host/server name |
| `source` | string | Log file source |

**Note:** Fields vary based on log format and Splunk index configuration.

#### Error Response (400 Bad Request)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "trace_id"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

#### Error Response (401 Unauthorized)

```json
{
  "detail": "Missing API Key. Please provide X-API-Key header."
}
```

#### Error Response (403 Forbidden)

```json
{
  "detail": "Invalid API Key"
}
```

#### Error Response (500 Internal Server Error)

```json
{
  "detail": "Failed to search logs: Splunk connection timeout"
}
```

---

### 2. Health Check

Check if the service is running and healthy.

#### Endpoint

```
GET /health
```

#### Authentication

**Not required** - This endpoint is public for monitoring purposes.

#### Example Request

```bash
curl https://traceid-log-service.onrender.com/health
```

#### Response (200 OK)

```json
{
  "status": "healthy",
  "service": "traceid-log-service"
}
```

---

### 2. Get Analytics Dashboard Summary

Retrieves aggregated API metrics including response codes, time series, errors, and endpoint performance.

#### Endpoint

```
POST /api/analytics/summary
```

#### Request Headers

```http
Content-Type: application/json
X-API-Key: your-api-key-here
```

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `aem_service` | string | ✅ Yes | - | AEM service identifier (e.g., "cm-p153560-e1607906") |
| `index` | string | ✅ Yes | - | Splunk index to search (e.g., "dx_aem_engineering") |
| `aem_tier` | string | ✅ Yes | - | AEM tier: "author" or "publish" |
| `time_range_days` | integer | ❌ No | 7 | Days to look back: 1, 7, or 30 (max: 30) |

#### Example Request

```bash
curl -X POST https://traceid-log-service.onrender.com/api/analytics/summary \
  -H "X-API-Key: n5a-BCkPunZNt2VkscD-VhRYhJWvX1HIHKbrjjk-uco" \
  -H "Content-Type: application/json" \
  -d '{
    "aem_service": "cm-p153560-e1607906",
    "index": "dx_aem_engineering",
    "aem_tier": "author",
    "time_range_days": 7
  }'
```

#### Request Body (JSON)

```json
{
  "aem_service": "cm-p153560-e1607906",
  "index": "dx_aem_engineering",
  "aem_tier": "author",
  "time_range_days": 7
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "time_range": {
    "start": "2026-01-02T00:00:00",
    "end": "2026-01-09T00:00:00",
    "days": 7
  },
  "summary": {
    "total_calls": 45623,
    "total_errors": 1234,
    "error_rate": 2.7,
    "unique_endpoints": 42
  },
  "response_codes": {
    "200": {
      "count": 42389,
      "percentage": 92.9
    },
    "400": {
      "count": 500,
      "percentage": 1.1
    },
    "404": {
      "count": 234,
      "percentage": 0.5
    },
    "500": {
      "count": 500,
      "percentage": 1.1
    }
  },
  "time_series": [
    {
      "timestamp": "2026-01-08T00:00:00",
      "total_calls": 6523,
      "by_code": {
        "200": 6100,
        "400": 200,
        "500": 223
      }
    }
  ],
  "top_errors": [
    {
      "endpoint": "/api/v1/content/pages",
      "response_code": "500",
      "count": 234,
      "message": "Internal server error: Database connection timeout",
      "first_seen": "2026-01-02T14:23:10",
      "last_seen": "2026-01-09T09:45:32"
    }
  ],
  "endpoints": [
    {
      "path": "/api/v1/content/pages",
      "total_calls": 15234,
      "error_count": 234,
      "error_rate": 1.54,
      "avg_response_time_ms": 125.45
    }
  ],
  "query_time_seconds": 3.42
}
```

#### Response Fields

**Summary Metrics**
- `total_calls`: Total number of API calls in the time range
- `total_errors`: Total number of errors (response code >= 400)
- `error_rate`: Percentage of errors out of total calls
- `unique_endpoints`: Number of distinct API endpoints called

**Response Codes**
- Distribution of HTTP response codes with count and percentage

**Time Series**
- API call trends over time
- Grouped by response codes
- Time span varies by time range:
  - **1 day**: 1-hour intervals
  - **7 days**: 6-hour intervals
  - **30 days**: 1-day intervals

**Top Errors**
- Up to 20 most frequent errors
- Includes endpoint, response code, count, error message, first/last occurrence

**Endpoints**
- Up to 20 most called endpoints
- Performance metrics including:
  - Total calls
  - Error count and rate
  - Average response time in milliseconds

#### Error Responses

| Status Code | Description | Example |
|-------------|-------------|---------|
| `400` | Invalid request parameters | `{"detail": "time_range_days must be between 1 and 30"}` |
| `401` | Missing API Key | `{"detail": "Missing X-API-Key header"}` |
| `403` | Invalid API Key | `{"detail": "Invalid API key"}` |
| `500` | Splunk connection or query failure | `{"detail": "Failed to fetch analytics: Connection timeout"}` |

#### Python Example

```python
import requests

url = "https://traceid-log-service.onrender.com/api/analytics/summary"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "n5a-BCkPunZNt2VkscD-VhRYhJWvX1HIHKbrjjk-uco"
}
payload = {
    "aem_service": "cm-p153560-e1607906",
    "index": "dx_aem_engineering",
    "aem_tier": "author",
    "time_range_days": 7
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

print(f"Total API Calls: {data['summary']['total_calls']}")
print(f"Error Rate: {data['summary']['error_rate']}%")
```

#### JavaScript Example

```javascript
const url = 'https://traceid-log-service.onrender.com/api/analytics/summary';
const apiKey = 'n5a-BCkPunZNt2VkscD-VhRYhJWvX1HIHKbrjjk-uco';

const payload = {
  aem_service: 'cm-p153560-e1607906',
  index: 'dx_aem_engineering',
  aem_tier: 'author',
  time_range_days: 7
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => {
    console.log('Total API Calls:', data.summary.total_calls);
    console.log('Error Rate:', data.summary.error_rate + '%');
  })
  .catch(error => console.error('Error:', error));
```

---

## Usage Examples

### Example 1: Basic Search (curl)

```bash
curl -X POST https://traceid-log-service.onrender.com/api/logs/search \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "abc-123-def-456",
    "aem_service": "cm-p153560-e1607906",
    "index": "dx_aem_engineering",
    "aem_tier": "author"
  }'
```

### Example 2: Search Last 48 Hours (curl)

```bash
curl -X POST https://traceid-log-service.onrender.com/api/logs/search \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "xyz-789-abc-012",
    "aem_service": "cm-p153560-e1607906",
    "index": "dx_aem_engineering",
    "aem_tier": "publish",
    "time_range_hours": 48,
    "limit": 1000
  }'
```

### Example 3: Python Client

```python
import requests

API_URL = "https://traceid-log-service.onrender.com/api/logs/search"
API_KEY = "your-api-key"

def search_logs(trace_id, aem_service, index="dx_aem_engineering", aem_tier="author"):
    """Search Splunk logs by trace ID."""
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "trace_id": trace_id,
        "aem_service": aem_service,
        "index": index,
        "aem_tier": aem_tier,
        "time_range_hours": 24,
        "limit": 500
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Usage
try:
    results = search_logs(
        trace_id="abc-123-def-456",
        aem_service="cm-p153560-e1607906",
        aem_tier="author"
    )
    
    print(f"Found {results['total_count']} logs")
    print(f"Query took {results['query_time_seconds']}s")
    
    for log in results['logs']:
        print(f"{log['_time']} {log['level']}: {log['msg']}")
        
except requests.exceptions.HTTPError as e:
    print(f"API Error: {e.response.json()}")
```

### Example 4: JavaScript/Node.js Client

```javascript
const axios = require('axios');

const API_URL = 'https://traceid-log-service.onrender.com/api/logs/search';
const API_KEY = 'your-api-key';

async function searchLogs(traceId, aemService, options = {}) {
  try {
    const response = await axios.post(API_URL, {
      trace_id: traceId,
      aem_service: aemService,
      index: options.index || 'dx_aem_engineering',
      aem_tier: options.aemTier || 'author',
      time_range_hours: options.timeRangeHours || 24,
      limit: options.limit || 500
    }, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else {
      console.error('Network Error:', error.message);
    }
    throw error;
  }
}

// Usage
(async () => {
  try {
    const results = await searchLogs(
      'abc-123-def-456',
      'cm-p153560-e1607906',
      { aemTier: 'author', timeRangeHours: 48 }
    );
    
    console.log(`Found ${results.total_count} logs`);
    console.log(`Query took ${results.query_time_seconds}s`);
    
    results.logs.forEach(log => {
      console.log(`${log._time} ${log.level}: ${log.msg}`);
    });
  } catch (error) {
    console.error('Failed to search logs:', error);
  }
})();
```

---

## Rate Limiting

Currently, there is **no rate limiting** implemented. However, consider the following:

- Splunk queries can be resource-intensive
- Large time ranges or high limits may take longer to execute
- Recommended: Keep `time_range_hours` ≤ 24 and `limit` ≤ 500 for best performance

**Best Practice:** If you need to query frequently, implement client-side rate limiting or caching.

---

## Timeouts

- **Connection Timeout:** 30 seconds
- **Read Timeout:** 60 seconds
- **Retry Logic:** 3 attempts with exponential backoff (built-in)

If queries consistently timeout, reduce `time_range_hours` or `limit`.

---

## Common Parameters

### AEM Service Identifiers

Format: `cm-p{programId}-e{environmentId}`

Examples:
- `cm-p153560-e1607906` - Production environment
- `cm-p153560-e1607907` - Staging environment

### Splunk Indices

Common indices:
- `dx_aem_engineering` - Engineering logs
- `dx_aem_production` - Production logs
- `dx_aem_staging` - Staging logs

Contact your Splunk administrator for available indices.

### AEM Tiers

- `author` - Author instances (content creation)
- `publish` - Publish instances (content delivery)

---

## Error Handling Best Practices

### 1. Handle Authentication Errors

```python
try:
    results = search_logs(trace_id, aem_service)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Missing or invalid API key")
    elif e.response.status_code == 403:
        print("API key is invalid")
    else:
        print(f"Error: {e.response.json()}")
```

### 2. Handle Validation Errors

```python
try:
    results = search_logs(trace_id="", aem_service="test")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        errors = e.response.json()['detail']
        for error in errors:
            print(f"Validation error: {error['msg']}")
```

### 3. Handle Server Errors

```python
try:
    results = search_logs(trace_id, aem_service)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 500:
        print("Server error - Splunk may be unavailable")
        # Implement retry logic or fallback
```

---

## Troubleshooting

### No Results Returned

**Possible causes:**
1. Trace ID doesn't exist in the specified time range
2. Wrong `aem_service` or `aem_tier`
3. Wrong Splunk `index`
4. Time range too narrow

**Solution:** Increase `time_range_hours` or verify parameters.

### Slow Queries

**Possible causes:**
1. Very large time range
2. High result limit
3. Splunk under heavy load

**Solution:**
- Reduce `time_range_hours` (e.g., 24 hours instead of 168)
- Lower `limit` (e.g., 100 instead of 1000)
- Query during off-peak hours

### Authentication Failures

**Possible causes:**
1. Missing `X-API-Key` header
2. Incorrect API key
3. API key expired or rotated

**Solution:** Verify API key with administrator.

---

## API Specifications

### Interactive Documentation

Visit your deployment URL to access interactive API documentation:

- **Swagger UI:** `https://traceid-log-service.onrender.com/docs`
- **ReDoc:** `https://traceid-log-service.onrender.com/redoc`

These provide:
- Interactive API testing
- Request/response schemas
- Example payloads
- Try-it-out functionality

---

## Support

For API support, contact:
- **Technical Issues:** Check application logs in Render dashboard
- **Authentication Issues:** Contact your administrator for API key
- **Splunk Issues:** Contact Splunk team

---

## Changelog

### Version 1.0.0 (Current)

- Initial release
- POST `/api/logs/search` - Search logs by trace ID
- GET `/health` - Health check endpoint
- API key authentication
- Splunk integration with retry logic
- Support for AEM services and tiers

---

## Security Notes

1. **HTTPS Only:** All API calls must use HTTPS in production
2. **API Key Protection:** Never expose API keys in client-side code or public repositories
3. **Access Control:** API key provides access to all Splunk logs - keep it secure
4. **Log Data:** Response contains raw log data - handle sensitively

---

## Contact

For questions or issues with this API:
- Repository: https://github.com/sharadsarda0509/trace-logs
- Documentation: See README.md and AUTHENTICATION.md

---

**Last Updated:** January 9, 2026  
**API Version:** 1.0.0

