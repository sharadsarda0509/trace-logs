"""
Configuration module for TraceId Log Service.
Supports HashiCorp Vault for secrets with environment variable fallback.
"""

import os
import logging
import logging.config
from typing import Optional

import dotenv

dotenv.load_dotenv()

# Setup basic logging for config module (will be reconfigured by setup_logging())
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Vault configuration (optional)
VAULT_ADDR: str = os.getenv("VAULT_ADDR", "https://vault-amer.adobe.net")
VAULT_ROLE_ID: Optional[str] = os.getenv("VAULT_ROLE_ID")
VAULT_SECRET_ID: Optional[str] = os.getenv("VAULT_SECRET_ID")
VAULT_SECRET_PATH: Optional[str] = os.getenv("VAULT_SECRET_PATH")

# Determine if Vault should be used
_use_vault = bool(VAULT_ROLE_ID and VAULT_SECRET_ID and VAULT_SECRET_PATH)

if _use_vault:
    logger.info("Attempting to fetch secrets from Vault")
    try:
        import hvac

        client = hvac.Client(url=VAULT_ADDR)
        response = client.auth.approle.login(
            role_id=VAULT_ROLE_ID, secret_id=VAULT_SECRET_ID
        )
        if response.get("auth", {}).get("client_token"):
            logger.info("Successfully authenticated with Vault")
            token = response["auth"]["client_token"]
            client = hvac.Client(url=VAULT_ADDR, token=token)
            secrets = client.secrets.kv.v2.read_secret_version(path=VAULT_SECRET_PATH)
            SPLUNK_PASS: str = secrets["data"]["data"]["SPLUNK_PASS"]
            logger.info("Secrets fetched successfully from Vault")
        else:
            raise Exception("Vault authentication failed - no client token received")
    except Exception as e:
        logger.warning(f"Vault authentication failed, falling back to env variables: {e}")
        SPLUNK_PASS: str = os.getenv("SPLUNK_PASS", "")
else:
    logger.info("Using environment variables for configuration")
    SPLUNK_PASS: str = os.getenv("SPLUNK_PASS", "")

# Splunk configuration - Adobe Splunk API defaults (from rca-splunk-agent)
SPLUNK_HOST: str = os.getenv("SPLUNK_HOST", "splunk-api.or1.adobe.net")
SPLUNK_USER: str = os.getenv("SPLUNK_USER", "svc-aem-voodoo-splunk")
SPLUNK_PORT: int = int(os.getenv("SPLUNK_PORT", "443"))  # Adobe Splunk uses HTTPS port
SPLUNK_SCHEME: str = os.getenv("SPLUNK_SCHEME", "https")  # http or https

# Service configuration
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
DEFAULT_TIME_RANGE_HOURS: int = int(os.getenv("DEFAULT_TIME_RANGE_HOURS", "24"))
MAX_TIME_RANGE_HOURS: int = int(os.getenv("MAX_TIME_RANGE_HOURS", "168"))  # 7 days
DEFAULT_LIMIT: int = int(os.getenv("DEFAULT_LIMIT", "500"))

# Authentication configuration
API_KEY: str = os.getenv("API_KEY", "")  # API key for authentication

# Logging configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


def setup_logging() -> None:
    """Configure logging for the service."""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": LOG_LEVEL,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": True,
            },
        },
    }
    logging.config.dictConfig(logging_config)


def validate_config() -> bool:
    """Validate that required configuration is present."""
    errors = []
    
    if not SPLUNK_HOST:
        errors.append("SPLUNK_HOST is required")
    if not SPLUNK_USER:
        errors.append("SPLUNK_USER is required")
    if not SPLUNK_PASS:
        errors.append("SPLUNK_PASS is required (via Vault or environment variable)")
    if not API_KEY:
        errors.append("API_KEY is required for authentication")
    
    if errors:
        for error in errors:
            logging.error(f"Configuration error: {error}")
        return False
    
    return True

