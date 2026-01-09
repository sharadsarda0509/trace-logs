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
        description="AEM service identifier(s) - comma-separated for multiple services",
        min_length=1,
        examples=["cm-p153560-e1607906", "cm-p153560-e1607906, cm-p123456-e7890123"],
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


class AnalyticsSummaryRequest(BaseModel):
    """Request model for analytics summary endpoint."""

    aem_service: str = Field(
        ...,
        description="AEM service identifier(s) - comma-separated for multiple services",
        min_length=1,
        examples=["cm-p153560-e1607906", "cm-p153560-e1607906, cm-p123456-e7890123"],
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
    time_range_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Days to look back (1, 7, or 30)",
    )


class AnalyticsSummaryResponse(BaseModel):
    """Response model for analytics summary endpoint."""

    success: bool = Field(..., description="Whether the query was successful")
    time_range: Dict[str, Any] = Field(..., description="Time range for the analytics")
    summary: Dict[str, Any] = Field(..., description="Summary metrics")
    response_codes: Dict[str, Any] = Field(..., description="Response code distribution")
    time_series: List[Dict[str, Any]] = Field(..., description="Time series data")
    top_errors: List[Dict[str, Any]] = Field(..., description="Top errors")
    endpoints: List[Dict[str, Any]] = Field(..., description="Endpoint performance")
    query_time_seconds: float = Field(..., description="Time taken to execute queries")
    error: Optional[str] = Field(None, description="Error message if failed")

