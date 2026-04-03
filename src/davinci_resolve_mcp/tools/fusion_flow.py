"""Tools for the Fusion FlowView object.

Covers: tool positioning on the node graph canvas,
selection, zoom, framing.

FlowView objects are obtained from comp_get_flow_view().
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_flow(flow_id: str):
    conn = get_connection()
    return conn, conn.get(flow_id, "FusionFlow")


@mcp.tool()
def flow_set_pos(flow_id: str, tool_id: str, x: float, y: float) -> str:
    """Set the position of a tool on the flow canvas.

    Args:
        flow_id: FusionFlow ID
        tool_id: FusionTool ID
        x: X position
        y: Y position

    Coordinates: X increases right, Y increases downward.
    Typical spacing: 1.0 horizontally, 1.0 vertically between tools.
    """
    try:
        conn, flow = _get_flow(flow_id)
        tool = conn.get(tool_id, "FusionTool")
        flow.SetPos(tool, x, y)
        return _ok(f"Tool positioned at ({x}, {y})")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def flow_get_pos(flow_id: str, tool_id: str) -> str:
    """Get the position of a tool on the flow canvas.

    Args:
        flow_id: FusionFlow ID
        tool_id: FusionTool ID

    Returns {x, y} position.
    """
    try:
        conn, flow = _get_flow(flow_id)
        tool = conn.get(tool_id, "FusionTool")
        pos = flow.GetPosTable(tool)
        if pos is None:
            return _err("Could not get tool position")
        return _ok({"x": pos.get(1, 0), "y": pos.get(2, 0)})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def flow_queue_set_pos(flow_id: str, tool_id: str, x: float, y: float) -> str:
    """Queue a tool position change (for batch operations).

    More efficient than flow_set_pos when positioning many tools.
    Call flow_flush_set_pos_queue() after all positions are queued.

    Args:
        flow_id: FusionFlow ID
        tool_id: FusionTool ID
        x: X position
        y: Y position
    """
    try:
        conn, flow = _get_flow(flow_id)
        tool = conn.get(tool_id, "FusionTool")
        flow.QueueSetPos(tool, x, y)
        return _ok(f"Position queued for ({x}, {y})")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def flow_flush_set_pos_queue(flow_id: str) -> str:
    """Flush all queued position changes.

    Call this after using flow_queue_set_pos() to apply all positions at once.

    Args:
        flow_id: FusionFlow ID
    """
    try:
        _, flow = _get_flow(flow_id)
        flow.FlushSetPosQueue()
        return _ok("Position queue flushed")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def flow_select(flow_id: str, tool_id: str | None = None, select: bool = True) -> str:
    """Select or deselect a tool in the flow, or deselect all.

    Args:
        flow_id: FusionFlow ID
        tool_id: FusionTool ID. If None, deselects all tools.
        select: True to select, False to deselect
    """
    try:
        conn, flow = _get_flow(flow_id)
        if tool_id:
            tool = conn.get(tool_id, "FusionTool")
            flow.Select(tool, select)
        else:
            flow.Select()
        return _ok("Selection updated")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def flow_frame_all(flow_id: str) -> str:
    """Zoom and pan the flow view to show all tools.

    Args:
        flow_id: FusionFlow ID
    """
    try:
        _, flow = _get_flow(flow_id)
        flow.FrameAll()
        return _ok("Framed all tools")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def flow_get_scale(flow_id: str) -> str:
    """Get the current zoom scale of the flow view.

    Args:
        flow_id: FusionFlow ID
    """
    try:
        _, flow = _get_flow(flow_id)
        return _ok(flow.GetScale())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def flow_set_scale(flow_id: str, scale: float) -> str:
    """Set the zoom scale of the flow view.

    Args:
        flow_id: FusionFlow ID
        scale: Zoom scale (1.0 = 100%)
    """
    try:
        _, flow = _get_flow(flow_id)
        flow.SetScale(scale)
        return _ok(f"Scale set to {scale}")
    except Exception as e:
        return _err(str(e))
