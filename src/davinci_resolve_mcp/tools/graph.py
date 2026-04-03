"""Tools for the Graph (node graph) object.

Covers: node management, LUTs, cache modes, labels, tools,
grade application, reset.

Graph objects are obtained from:
- Timeline.GetNodeGraph()
- TimelineItem.GetNodeGraph(layerIdx)
- ColorGroup.GetPreClipNodeGraph()
- ColorGroup.GetPostClipNodeGraph()
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.constants import CACHE_MODES, resolve_enum

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_graph(graph_id: str):
    conn = get_connection()
    return conn, conn.get(graph_id, "Graph")


@mcp.tool()
def graph_get_num_nodes(graph_id: str) -> str:
    """Get the number of nodes in a graph.

    Args:
        graph_id: Graph ID
    """
    try:
        _, graph = _get_graph(graph_id)
        return _ok(graph.GetNumNodes())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_set_lut(graph_id: str, node_index: int, lut_path: str) -> str:
    """Set a LUT on a node.

    Args:
        graph_id: Graph ID
        node_index: Node index (1-based, 1 <= nodeIndex <= GetNumNodes())
        lut_path: Absolute or relative LUT path. Resolve must have already discovered the LUT.
    """
    try:
        _, graph = _get_graph(graph_id)
        result = graph.SetLUT(node_index, lut_path)
        if result:
            return _ok(f"LUT set on node {node_index}")
        return _err(f"Failed to set LUT on node {node_index}. Check path is valid and LUT is discovered.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_get_lut(graph_id: str, node_index: int) -> str:
    """Get the LUT path applied to a node. Returns empty string if no LUT.

    Args:
        graph_id: Graph ID
        node_index: Node index (1-based)
    """
    try:
        _, graph = _get_graph(graph_id)
        return _ok(graph.GetLUT(node_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_set_node_cache_mode(graph_id: str, node_index: int, cache_value: str) -> str:
    """Set the cache mode for a node.

    Args:
        graph_id: Graph ID
        node_index: Node index (1-based)
        cache_value: One of 'AUTO', 'DISABLED', 'ENABLED'
    """
    try:
        conn, graph = _get_graph(graph_id)
        cv = resolve_enum(conn.resolve, CACHE_MODES, cache_value)
        result = graph.SetNodeCacheMode(node_index, cv)
        if result:
            return _ok(f"Node {node_index} cache mode set to '{cache_value}'")
        return _err(f"Failed to set cache mode on node {node_index}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_get_node_cache_mode(graph_id: str, node_index: int) -> str:
    """Get the cache mode of a node. Returns -1 (AUTO), 0 (DISABLED), or 1 (ENABLED).

    Args:
        graph_id: Graph ID
        node_index: Node index (1-based)
    """
    try:
        _, graph = _get_graph(graph_id)
        mode = graph.GetNodeCacheMode(node_index)
        mode_name = {-1: "AUTO", 0: "DISABLED", 1: "ENABLED"}.get(mode, f"UNKNOWN({mode})")
        return _ok({"mode": mode, "name": mode_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_get_node_label(graph_id: str, node_index: int) -> str:
    """Get the label of a node.

    Args:
        graph_id: Graph ID
        node_index: Node index (1-based)
    """
    try:
        _, graph = _get_graph(graph_id)
        return _ok(graph.GetNodeLabel(node_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_get_tools_in_node(graph_id: str, node_index: int) -> str:
    """Get the list of tools used in a node.

    Args:
        graph_id: Graph ID
        node_index: Node index (1-based)

    Returns list of tool name strings.
    """
    try:
        _, graph = _get_graph(graph_id)
        return _ok(graph.GetToolsInNode(node_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_set_node_enabled(graph_id: str, node_index: int, is_enabled: bool) -> str:
    """Enable or disable a node.

    Args:
        graph_id: Graph ID
        node_index: Node index (1-based)
        is_enabled: True to enable, False to disable
    """
    try:
        _, graph = _get_graph(graph_id)
        result = graph.SetNodeEnabled(node_index, is_enabled)
        if result:
            return _ok(f"Node {node_index} {'enabled' if is_enabled else 'disabled'}")
        return _err(f"Failed to set node {node_index} enabled state")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_apply_grade_from_drx(graph_id: str, path: str, grade_mode: int) -> str:
    """Apply a grade from a DRX file.

    Args:
        graph_id: Graph ID
        path: Path to the DRX still file
        grade_mode: 0 = No keyframes, 1 = Source Timecode aligned, 2 = Start Frames aligned
    """
    try:
        _, graph = _get_graph(graph_id)
        result = graph.ApplyGradeFromDRX(path, grade_mode)
        if result:
            return _ok(f"Grade applied from '{path}'")
        return _err(f"Failed to apply grade from '{path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_apply_arri_cdl_lut(graph_id: str) -> str:
    """Apply ARRI CDL and LUT to the graph.

    Args:
        graph_id: Graph ID
    """
    try:
        _, graph = _get_graph(graph_id)
        result = graph.ApplyArriCdlLut()
        if result:
            return _ok("ARRI CDL and LUT applied")
        return _err("Failed to apply ARRI CDL and LUT")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def graph_reset_all_grades(graph_id: str) -> str:
    """Reset all grades in the graph.

    Args:
        graph_id: Graph ID
    """
    try:
        _, graph = _get_graph(graph_id)
        result = graph.ResetAllGrades()
        if result:
            return _ok("All grades reset")
        return _err("Failed to reset grades")
    except Exception as e:
        return _err(str(e))
