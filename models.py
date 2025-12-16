"""
Pydantic models for request validation and response structure.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

import config


class LogSearchRequest(BaseModel):
    """Request model for log search endpoint."""

    trace_id: str = Field(
        ...,
        description="The trace ID to search for",
        min_length=1,
        examples=["abc-123-def-456"],
    )
    aem_service: str = Field(
        ...,
        description="AEM service identifier",
        min_length=1,
        examples=["cm-p153560-e1607906"],
    )
    index: str = Field(
        ...,
        description="Splunk index to search",
        min_length=1,
        examples=["dx_aem_engineering"],
    )
    aem_tier: str = Field(
        ...,
        description="AEM tier (author or publish)",
        min_length=1,
        examples=["author", "publish"],
    )
    time_range_hours: int = Field(
        default=config.DEFAULT_TIME_RANGE_HOURS,
        ge=1,
        le=config.MAX_TIME_RANGE_HOURS,
        description=f"How far back to search in hours (max: {config.MAX_TIME_RANGE_HOURS})",
    )
    limit: int = Field(
        default=config.DEFAULT_LIMIT,
        ge=1,
        le=1000,
        description="Maximum number of logs to return",
    )


class LogSearchResponse(BaseModel):
    """Response model for log search endpoint."""

    success: bool = Field(..., description="Whether the search was successful")
    trace_id: str = Field(..., description="The trace ID that was searched")
    total_count: int = Field(..., description="Total number of logs returned")
    logs: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of log entries",
    )
    query_time_seconds: float = Field(
        ..., 
        description="Time taken to execute the query in seconds"
    )
    error: Optional[str] = Field(None, description="Error message if search failed")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")

