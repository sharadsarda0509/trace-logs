"""
TraceId Log Service - FastAPI Application

A lightweight API for querying Splunk logs by traceId.
"""

import logging
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

import config
from models import LogSearchRequest, LogSearchResponse, HealthResponse, AnalyticsSummaryRequest, AnalyticsSummaryResponse
from splunk_client import get_splunk_client
from analytics_client import get_analytics_client

# Initialize configuration
config.setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TraceId Log Service",
    version="1.0.0",
    description="A lightweight API for querying Splunk logs by traceId",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Key Authentication Middleware
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """
    Verify API key for all requests except health check and static files.
    Expects X-API-Key header to match configured API_KEY.
    """
    # Skip authentication for health check endpoint
    if request.url.path == "/health":
        return await call_next(request)
    
    # Skip authentication for static files (HTML, CSS, JS, etc.)
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        logger.warning(f"Missing API key for request to {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing API Key. Please provide X-API-Key header."},
        )
    
    if api_key != config.API_KEY:
        logger.warning(f"Invalid API key attempted for {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid API Key"},
        )
    
    # API key is valid, proceed with request
    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    if not config.validate_config():
        logger.error("Configuration validation failed. Service may not work correctly.")


@app.post(
    "/api/logs/search",
    response_model=LogSearchResponse,
    summary="Search logs by traceId",
    description="Search Splunk logs for a specific traceId within the given AEM service and time range.",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error or Splunk connection failure"},
    },
)
async def search_logs(request: LogSearchRequest) -> LogSearchResponse:
    """
    Search Splunk logs by traceId.

    This endpoint queries Splunk for logs matching the provided traceId
    within the specified AEM service, index, and time range.
    """
    logger.info(
        f"Searching logs for traceId={request.trace_id}, "
        f"aem_service={request.aem_service}, "
        f"index={request.index}, "
        f"aem_tier={request.aem_tier}, "
        f"time_range_hours={request.time_range_hours}"
    )

    try:
        # Get Splunk client and execute search
        splunk_client = get_splunk_client()
        result = splunk_client.search_by_trace_id(
            trace_id=request.trace_id,
            aem_service=request.aem_service,
            index=request.index,
            aem_tier=request.aem_tier,
            time_range_hours=request.time_range_hours,
            limit=request.limit,
        )

        logger.info(
            f"Search completed: {result['total_count']} logs found "
            f"in {result['query_time_seconds']}s"
        )

        return LogSearchResponse(
            success=True,
            trace_id=request.trace_id,
            total_count=result["total_count"],
            logs=result["logs"],
            query_time_seconds=result["query_time_seconds"],
        )

    except Exception as e:
        logger.error(f"Search failed for traceId={request.trace_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search logs: {str(e)}",
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the service is running.",
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="traceid-log-service")


@app.post(
    "/api/auth/validate",
    summary="Validate API key",
    description="Validate if the provided API key is correct.",
    responses={
        200: {"description": "API key is valid"},
        401: {"description": "Missing API key"},
        403: {"description": "Invalid API key"},
    },
)
async def validate_api_key(request: Request):
    """
    Validate API key without making Splunk queries.
    This endpoint is used by the login page to verify credentials.
    
    Note: This endpoint is NOT excluded from authentication middleware,
    so it will automatically validate the X-API-Key header.
    """
    # If we reach here, the API key is valid (middleware already checked it)
    return {"valid": True, "message": "API key is valid"}


@app.post(
    "/api/analytics/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get analytics dashboard summary",
    description="Get aggregated API metrics including response codes, time series, errors, and endpoint performance.",
    responses={
        200: {"description": "Analytics retrieved successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error or Splunk connection failure"},
    },
)
async def get_analytics_summary(request: AnalyticsSummaryRequest) -> AnalyticsSummaryResponse:
    """
    Get aggregated analytics for dashboard.

    This endpoint queries Splunk for aggregated metrics including:
    - Total API calls and error rates
    - Response code distribution
    - Time series data (calls over time)
    - Top errors and failure patterns
    - Endpoint performance metrics
    """
    logger.info(
        f"Fetching analytics summary for aem_service={request.aem_service}, "
        f"index={request.index}, aem_tier={request.aem_tier}, "
        f"time_range_days={request.time_range_days}"
    )

    try:
        # Get analytics client and execute queries
        analytics_client = get_analytics_client()
        query_start = time.time()
        
        result = analytics_client.get_dashboard_summary(
            aem_service=request.aem_service,
            index=request.index,
            aem_tier=request.aem_tier,
            time_range_days=request.time_range_days,
        )
        
        query_time = time.time() - query_start

        logger.info(f"Analytics query completed in {query_time:.2f}s")

        return AnalyticsSummaryResponse(
            success=True,
            time_range=result["time_range"],
            summary=result["summary"],
            response_codes=result["response_codes"],
            time_series=result["time_series"],
            top_errors=result["top_errors"],
            endpoints=result["endpoints"],
            query_time_seconds=round(query_time, 2),
        )

    except Exception as e:
        logger.error(f"Analytics query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analytics: {str(e)}",
        )


# Mount static files (built React app)
# Note: API routes defined above take precedence over static files
static_dir = Path(__file__).parent / "static"

if static_dir.exists():
    # Mount static files for assets (CSS, JS, images)
    app.mount(
        "/assets",
        StaticFiles(directory=static_dir / "assets"),
        name="assets"
    )
    logger.info(f"Static assets mounted from {static_dir / 'assets'}")
    
    # Catch-all route for SPA routing - serves index.html for all non-API routes
    # This must be defined AFTER all API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Catch-all route to serve index.html for client-side routing.
        This allows React Router to handle routes like /dashboard, /trace-search, etc.
        """
        # Serve index.html for all paths (API routes are already handled above)
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Frontend not found",
                    "message": "index.html not found in static directory",
                    "api_docs": "/docs",
                    "health": "/health"
                }
            )
    
    logger.info(f"SPA routing enabled - serving index.html for all non-API routes")
else:
    logger.error(f"Static directory not found at {static_dir}. Frontend will not be served.")
    logger.error("Please build the frontend with: cd frontend && npm install && npm run build")
    
    # Serve a simple error page as fallback
    @app.get("/")
    async def root():
        return {
            "error": "Frontend not built",
            "message": "The React frontend has not been built. Please run: cd frontend && npm install && npm run build",
            "api_docs": "/docs",
            "health": "/health"
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

