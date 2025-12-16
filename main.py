"""
TraceId Log Service - FastAPI Application

A lightweight API for querying Splunk logs by traceId.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

import config
from models import LogSearchRequest, LogSearchResponse, HealthResponse
from splunk_client import get_splunk_client

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


# Mount static files (built React app)
# Note: API routes defined above take precedence over static files
try:
    static_dir = Path(__file__).parent / "static"
    app.mount(
        "/",
        StaticFiles(directory=static_dir, html=True),
        name="static"
    )
    logger.info(f"Static files mounted from {static_dir}")
except (RuntimeError, FileNotFoundError) as e:
    logger.warning(f"Static directory not found. Frontend will not be served. ({e})")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

