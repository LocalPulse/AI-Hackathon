"""Alias module for shared state functions."""

from typing import Any, Optional

try:
    from web.api.utils.shared_state import get_shared_state
except ImportError:
    # Fallback if web module is not available
    def get_shared_state() -> Optional[Any]:
        """Fallback function if shared state module is not available."""
        return None

__all__ = ["get_shared_state"]
