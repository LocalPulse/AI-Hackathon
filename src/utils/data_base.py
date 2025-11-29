"""Alias module for database logging functions."""

try:
    from web.api.utils.database import log_detection
except ImportError:
    # Fallback if web module is not available
    def log_detection(*args, **kwargs):
        """Fallback function if database module is not available."""
        pass

__all__ = ["log_detection"]

