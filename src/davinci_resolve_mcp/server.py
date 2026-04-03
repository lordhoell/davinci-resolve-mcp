"""DaVinci Resolve MCP Server — main application."""

import logging
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from davinci_resolve_mcp.resolve_connection import ResolveConnection

logger = logging.getLogger(__name__)

# Global connection instance — tools access this via get_connection()
_connection: ResolveConnection | None = None


def get_connection() -> ResolveConnection:
    """Get the active Resolve connection. Called by all tool modules."""
    if _connection is None:
        raise ConnectionError("Resolve connection not initialized")
    _connection.ensure_connected()
    return _connection


@asynccontextmanager
async def app_lifespan(server):
    """Manage Resolve connection lifecycle."""
    global _connection
    conn = ResolveConnection()
    try:
        conn.connect()
        _connection = conn
        logger.info("DaVinci Resolve MCP server started")
        yield
    except Exception as e:
        logger.error(f"Failed to connect to DaVinci Resolve: {e}")
        raise
    finally:
        conn.disconnect()
        _connection = None
        logger.info("DaVinci Resolve MCP server stopped")


mcp = FastMCP(
    "DaVinci Resolve",
    instructions=(
        "Full DaVinci Resolve scripting API exposed as MCP tools. "
        "Control projects, timelines, media pool, color grading, rendering, and more."
    ),
    lifespan=app_lifespan,
)

# Import all tool modules — each module registers its tools with @mcp.tool()
import davinci_resolve_mcp.tools  # noqa: E402, F401


def main():
    """Entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
