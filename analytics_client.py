"""
Analytics client for aggregated Splunk queries.
Provides dashboard metrics and statistics.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

from splunklib import results, client

import config

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """Client for querying aggregated analytics from Splunk."""

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
        logger.info(f"Analytics client connected to Splunk at {config.SPLUNK_SCHEME}://{config.SPLUNK_HOST}:{config.SPLUNK_PORT}")

    def get_dashboard_summary(
        self,
        aem_service: str,
        index: str,
        aem_tier: str,
        time_range_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get aggregated dashboard metrics.

        Args:
            aem_service: AEM service identifier(s) - comma-separated for multiple
                        (e.g., "cm-p153560-e1607906" or "cm-p153560-e1607906, cm-p123456-e7890123")
            index: Splunk index to search
            aem_tier: AEM tier (author or publish)
            time_range_days: Days to look back (1, 7, or 30)

        Returns:
            Dict containing aggregated metrics
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=time_range_days)

        # Parse multiple services
        aem_services = [s.strip() for s in aem_service.split(',') if s.strip()]
        logger.info(f"Fetching dashboard metrics for {len(aem_services)} service(s) over {time_range_days} days")

        # Build service filter for Splunk queries
        service_filter = self._build_service_filter(aem_services)

        # Run multiple queries in parallel for better performance
        response_codes = self._get_response_code_distribution(
            service_filter, index, aem_tier, start_time, end_time
        )
        
        time_series = self._get_time_series(
            service_filter, index, aem_tier, start_time, end_time, time_range_days
        )
        
        top_errors = self._get_top_errors(
            service_filter, index, aem_tier, start_time, end_time
        )
        
        endpoints = self._get_endpoint_performance(
            service_filter, index, aem_tier, start_time, end_time
        )

        # Calculate summary metrics
        total_calls = sum(rc.get('count', 0) for rc in response_codes.values())
        total_errors = sum(
            rc.get('count', 0) for code, rc in response_codes.items()
            if int(code) >= 400
        )
        error_rate = round((total_errors / total_calls * 100), 2) if total_calls > 0 else 0

        return {
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": time_range_days
            },
            "summary": {
                "total_calls": total_calls,
                "total_errors": total_errors,
                "error_rate": error_rate,
                "unique_endpoints": len(endpoints)
            },
            "response_codes": response_codes,
            "time_series": time_series,
            "top_errors": top_errors,
            "endpoints": endpoints
        }

    def _build_service_filter(self, aem_services: List[str]) -> str:
        """Build service filter for Splunk query."""
        if len(aem_services) > 1:
            # Multiple services: use OR condition
            return '(' + ' OR '.join([f'aem_service="{svc}"' for svc in aem_services]) + ')'
        else:
            # Single service
            return f'aem_service="{aem_services[0]}"'

    def _get_response_code_distribution(
        self, service_filter: str, index: str, aem_tier: str,
        start_time: datetime, end_time: datetime
    ) -> Dict[str, Dict[str, Any]]:
        """Get response code distribution."""
        query = (
            f'search index="{index}" '
            f'{service_filter} '
            f'aem_tier="{aem_tier}" '
            f'response_code=* '
            f'| stats count by response_code '
            f'| eval percentage = round((count / sum(count) * 100), 2)'
        )

        results_list = self._execute_query(query, start_time, end_time)
        
        response_codes = {}
        for result in results_list:
            code = result.get('response_code', 'unknown')
            response_codes[code] = {
                'count': int(result.get('count', 0)),
                'percentage': float(result.get('percentage', 0))
            }
        
        return response_codes

    def _get_time_series(
        self, service_filter: str, index: str, aem_tier: str,
        start_time: datetime, end_time: datetime, days: int
    ) -> List[Dict[str, Any]]:
        """Get time series data for API calls."""
        # Determine timechart span based on time range
        if days == 1:
            span = '1h'
        elif days <= 7:
            span = '6h'
        else:
            span = '1d'

        query = (
            f'search index="{index}" '
            f'{service_filter} '
            f'aem_tier="{aem_tier}" '
            f'| timechart span={span} count by response_code'
        )

        results_list = self._execute_query(query, start_time, end_time)
        
        time_series = []
        for result in results_list:
            entry = {
                'timestamp': result.get('_time', ''),
                'total_calls': 0,
                'by_code': {}
            }
            
            for key, value in result.items():
                if key != '_time' and value:
                    try:
                        count = int(value)
                        entry['by_code'][key] = count
                        entry['total_calls'] += count
                    except (ValueError, TypeError):
                        pass
            
            time_series.append(entry)
        
        return time_series

    def _get_top_errors(
        self, service_filter: str, index: str, aem_tier: str,
        start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get top errors and failure patterns."""
        query = (
            f'search index="{index}" '
            f'{service_filter} '
            f'aem_tier="{aem_tier}" '
            f'(response_code>=400 OR level=ERROR) '
            f'| stats count, '
            f'  earliest(_time) as first_seen, '
            f'  latest(_time) as last_seen, '
            f'  values(msg) as messages '
            f'  by endpoint, response_code '
            f'| sort -count '
            f'| head 20'
        )

        results_list = self._execute_query(query, start_time, end_time)
        
        top_errors = []
        for result in results_list:
            messages = result.get('messages', '')
            if isinstance(messages, list):
                message = messages[0] if messages else 'Unknown error'
            else:
                message = str(messages) if messages else 'Unknown error'
            
            top_errors.append({
                'endpoint': result.get('endpoint', 'unknown'),
                'response_code': result.get('response_code', 'unknown'),
                'count': int(result.get('count', 0)),
                'message': message[:200],  # Limit message length
                'first_seen': result.get('first_seen', ''),
                'last_seen': result.get('last_seen', '')
            })
        
        return top_errors

    def _get_endpoint_performance(
        self, service_filter: str, index: str, aem_tier: str,
        start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get endpoint performance metrics."""
        query = (
            f'search index="{index}" '
            f'{service_filter} '
            f'aem_tier="{aem_tier}" '
            f'endpoint=* '
            f'| stats count, '
            f'  sum(eval(if(response_code>=400,1,0))) as error_count, '
            f'  avg(response_time_ms) as avg_response_time '
            f'  by endpoint '
            f'| eval error_rate = round((error_count / count * 100), 2) '
            f'| sort -count '
            f'| head 20'
        )

        results_list = self._execute_query(query, start_time, end_time)
        
        endpoints = []
        for result in results_list:
            endpoints.append({
                'path': result.get('endpoint', 'unknown'),
                'total_calls': int(result.get('count', 0)),
                'error_count': int(result.get('error_count', 0)),
                'error_rate': float(result.get('error_rate', 0)),
                'avg_response_time_ms': round(float(result.get('avg_response_time', 0)), 2)
            })
        
        return endpoints

    def _execute_query(
        self, query: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Execute a Splunk query with retry logic."""
        reader = None

        for attempt in range(config.MAX_RETRIES):
            try:
                job_results = self.service.jobs.oneshot(
                    query,
                    output_mode="json",
                    count=0,
                    earliest_time=start_time.isoformat(),
                    latest_time=end_time.isoformat(),
                )
                current_reader = results.JSONResultsReader(job_results)
                if current_reader is not None:
                    reader = current_reader
                    break

                logger.warning(f"Attempt {attempt + 1}: Reader was None, retrying...")
                time.sleep(attempt + 1)

            except Exception as e:
                logger.warning(
                    f"Analytics query attempt {attempt + 1}/{config.MAX_RETRIES} failed: {e}"
                )
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(attempt + 1)
                else:
                    logger.error(f"All {config.MAX_RETRIES} attempts failed")
                    raise

        if reader is None:
            logger.warning("No reader available after all retries")
            return []

        try:
            result_list = [r for r in reader if isinstance(r, dict)]
            logger.info(f"Analytics query returned {len(result_list)} results")
            return result_list

        except Exception as e:
            logger.error(f"Error reading analytics results: {e}")
            return []


# Singleton instance
_analytics_client_instance = None


def get_analytics_client() -> AnalyticsClient:
    """Get or create analytics client instance."""
    global _analytics_client_instance
    if _analytics_client_instance is None:
        _analytics_client_instance = AnalyticsClient()
    return _analytics_client_instance

