"""Tools for the ColorGroup object.

Covers: group naming, clip listing within a group,
pre-clip and post-clip node graphs.

ColorGroup objects are obtained from:
- Project.GetColorGroupsList()
- Project.AddColorGroup(groupName)
- TimelineItem.GetColorGroup()
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_cg(group_id: str):
    conn = get_connection()
    return conn, conn.get(group_id, "ColorGroup")


@mcp.tool()
def color_group_get_name(group_id: str) -> str:
    """Get the name of a color group.

    Args:
        group_id: ColorGroup ID
    """
    try:
        _, cg = _get_cg(group_id)
        return _ok(cg.GetName())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def color_group_set_name(group_id: str, group_name: str) -> str:
    """Rename a color group.

    Args:
        group_id: ColorGroup ID
        group_name: New name for the group
    """
    try:
        _, cg = _get_cg(group_id)
        result = cg.SetName(group_name)
        if result:
            return _ok(f"Color group renamed to '{group_name}'")
        return _err("Failed to rename color group")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def color_group_get_clips_in_timeline(group_id: str, timeline_id: str | None = None) -> str:
    """Get all timeline items in this color group for a given timeline.

    Args:
        group_id: ColorGroup ID
        timeline_id: Optional Timeline ID. Uses current timeline if not provided.

    Returns list of TimelineItem references.
    """
    try:
        conn, cg = _get_cg(group_id)
        if timeline_id:
            timeline = conn.get(timeline_id, "Timeline")
            items = cg.GetClipsInTimeline(timeline)
        else:
            items = cg.GetClipsInTimeline()

        if items is None:
            return _ok([])
        result = []
        for item in items:
            iid = conn.register(item, "TimelineItem")
            result.append({"id": iid, "type": "TimelineItem", "name": item.GetName()})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def color_group_get_pre_clip_node_graph(group_id: str) -> str:
    """Get the pre-clip node graph for a color group. This graph applies before the individual clip grade.

    Args:
        group_id: ColorGroup ID
    """
    try:
        conn, cg = _get_cg(group_id)
        graph = cg.GetPreClipNodeGraph()
        if graph is None:
            return _err("Failed to get pre-clip node graph")
        gid = conn.register(graph, "Graph", composite_key=f"graph:cg_pre:{group_id}")
        return _ok({"id": gid, "type": "Graph"})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def color_group_get_post_clip_node_graph(group_id: str) -> str:
    """Get the post-clip node graph for a color group. This graph applies after the individual clip grade.

    Args:
        group_id: ColorGroup ID
    """
    try:
        conn, cg = _get_cg(group_id)
        graph = cg.GetPostClipNodeGraph()
        if graph is None:
            return _err("Failed to get post-clip node graph")
        gid = conn.register(graph, "Graph", composite_key=f"graph:cg_post:{group_id}")
        return _ok({"id": gid, "type": "Graph"})
    except Exception as e:
        return _err(str(e))
