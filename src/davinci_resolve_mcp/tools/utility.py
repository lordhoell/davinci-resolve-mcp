"""Utility tools for managing the MCP server state.

These tools help with connection management and debugging.
They are not part of the DaVinci Resolve API.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


@mcp.tool()
def clear_object_cache() -> str:
    """Clear all cached Resolve object handles.

    Use this when:
    - You've switched projects through the Resolve UI (not via API)
    - Objects seem stale or produce errors
    - You want a fresh start

    After clearing, you'll need to re-fetch objects (e.g., call
    project_manager_get_current_project, project_get_current_timeline, etc.)
    before using them.
    """
    try:
        conn = get_connection()
        info = conn.get_cache_info()
        conn.clear()
        return _ok({
            "cleared": info["total"],
            "was_by_type": info["by_type"],
            "message": "Cache cleared. Re-fetch objects before using them.",
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def get_object_cache_info() -> str:
    """Get a summary of all cached Resolve object handles.

    Returns the total count and breakdown by type. Useful for debugging
    when objects seem stale or you want to understand the cache state.
    """
    try:
        conn = get_connection()
        return _ok(conn.get_cache_info())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def initialize() -> str:
    """Re-initialize the connection to DaVinci Resolve.

    Use this if DaVinci Resolve was restarted after the MCP server started.
    This will:
    1. Clear all cached object handles
    2. Re-establish the connection to Resolve
    3. Verify the connection is working

    Returns version info on success.
    """
    try:
        conn = get_connection()
        conn.clear()
        conn.connect()
        version = conn.resolve.GetVersionString()
        product = conn.resolve.GetProductName()
        return _ok({
            "product": product,
            "version": version,
            "message": f"Reconnected to {product} {version}",
        })
    except Exception as e:
        return _err(f"Failed to reconnect: {str(e)}. Is DaVinci Resolve running?")
