"""
Splunk client for querying logs by traceId.
Adapted from rca-splunk-agent/fetchers/splunk_aemerror.py
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from splunklib import results, client

import config

logger = logging.getLogger(__name__)


class SplunkClient:
    """Client for querying Splunk logs by journeyId."""

    def __init__(self) -> None:
        """Initialize Splunk connection."""
        self.service = client.connect(
            host=config.SPLUNK_HOST,
            port=config.SPLUNK_PORT,
            username=config.SPLUNK_USER,
            password=config.SPLUNK_PASS,
            scheme=config.SPLUNK_SCHEME,
            autologin=True,
        )
        logger.info(f"Connected to Splunk at {config.SPLUNK_SCHEME}://{config.SPLUNK_HOST}:{config.SPLUNK_PORT}")

    def search_by_trace_id(
        self,
        trace_id: str,
        aem_service: str,
        index: str,
        aem_tier: str,
        time_range_hours: int = config.DEFAULT_TIME_RANGE_HOURS,
        limit: int = config.DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        """
        Search Splunk logs by journeyId.

        Args:
            trace_id: The journey ID to search for (field name kept for API compatibility)
            aem_service: AEM service identifier(s) - comma-separated for multiple
                        (e.g., "cm-p153560-e1607906" or "cm-p153560-e1607906, cm-p123456-e7890123")
            index: Splunk index to search (e.g., "dx_aem_engineering")
            aem_tier: AEM tier (e.g., "author", "publish")
            time_range_hours: How far back to search (default: 24 hours, max: 168 hours)
            limit: Maximum number of logs to return (default: 500)

        Returns:
            Dict containing logs and metadata
        """
        # Validate and cap time range
        time_range_hours = min(time_range_hours, config.MAX_TIME_RANGE_HOURS)
        
        # Calculate time bounds
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)

        # Handle multiple AEM services (comma-separated)
        aem_services = [s.strip() for s in aem_service.split(',') if s.strip()]
        if len(aem_services) > 1:
            # Multiple services: use OR condition
            service_filter = '(' + ' OR '.join([f'aem_service="{svc}"' for svc in aem_services]) + ')'
        else:
            # Single service
            service_filter = f'aem_service="{aem_services[0]}"'

        # Build SPL query using journeyId field
        query = (
            f'search index="{index}" '
            f'{service_filter} '
            f'aem_tier="{aem_tier}" '
            f'journeyId="{trace_id}" '
            f'| sort -_time '
            f'| head {limit}'
        )

        logger.debug(f"Executing Splunk query: {query}")
        logger.debug(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")

        # Execute query with retry logic
        query_start = time.time()
        logs = self._execute_query(query, start_time, end_time)
        query_time = time.time() - query_start

        return {
            "logs": logs,
            "total_count": len(logs),
            "query_time_seconds": round(query_time, 2),
        }

    def _execute_query(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Splunk query with retry logic.

        Adapted from rca-splunk-agent/fetchers/splunk_aemerror.py:83-117

        Args:
            query: SPL query string
            start_time: Query start time
            end_time: Query end time

        Returns:
            List of log entries as dictionaries
        """
        reader = None

        for attempt in range(config.MAX_RETRIES):
            try:
                job_results = self.service.jobs.oneshot(
                    query,
                    output_mode="json",
                    count=0,  # Fetch all results (up to limit in query)
                    earliest_time=start_time.isoformat(),
                    latest_time=end_time.isoformat(),
                )
                current_reader = results.JSONResultsReader(job_results)
                if current_reader is not None:
                    reader = current_reader
                    break
                
                logger.warning(f"Attempt {attempt + 1}: Reader was None, retrying...")
                time.sleep(attempt + 1)  # Exponential backoff

            except Exception as e:
                logger.warning(
                    f"Splunk query attempt {attempt + 1}/{config.MAX_RETRIES} failed: {e}"
                )
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(attempt + 1)  # Exponential backoff
                else:
                    logger.error(f"All {config.MAX_RETRIES} attempts failed")
                    raise

        if reader is None:
            logger.warning("No reader available after all retries")
            return []

        try:
            # Extract results from reader
            result_list = [r for r in reader if isinstance(r, dict)]
            logger.info(f"Query returned {len(result_list)} log entries")
            return result_list

        except Exception as e:
            logger.error(f"Error reading Splunk results: {e}")
            return []


# Singleton instance for reuse
_client_instance: Optional[SplunkClient] = None


def get_splunk_client() -> SplunkClient:
    """Get or create a Splunk client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = SplunkClient()
    return _client_instance

