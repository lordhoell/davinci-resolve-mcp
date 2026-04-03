"""Tools for the Fusion BezierSpline object.

Covers: keyframe animation management — getting, setting,
adjusting, and deleting keyframes.

BezierSpline is the most common animation modifier in Fusion.
Add one to a tool input with tool_add_modifier("BezierSpline").
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_spline(spline_id: str):
    conn = get_connection()
    return conn, conn.get(spline_id, "FusionSpline")


@mcp.tool()
def spline_get_keyframes(spline_id: str) -> str:
    """Get all keyframes from a BezierSpline.

    Args:
        spline_id: FusionSpline ID

    Returns dict of frame_number -> value.
    """
    try:
        _, spline = _get_spline(spline_id)
        return _ok(spline.GetKeyFrames())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def spline_set_keyframes(spline_id: str, keyframes: dict, replace: bool = False) -> str:
    """Set keyframes on a BezierSpline.

    Args:
        spline_id: FusionSpline ID
        keyframes: Dict of frame_number (int/float) -> value (number).
                   Example: {"0": 0.0, "30": 1.0, "60": 0.0} — fade in/out
        replace: If True, replaces all existing keyframes. If False, merges.
    """
    try:
        _, spline = _get_spline(spline_id)
        # Convert string keys to numbers (JSON keys are always strings)
        kf = {float(k): v for k, v in keyframes.items()}
        spline.SetKeyFrames(kf, replace)
        return _ok(f"Set {len(kf)} keyframe(s)")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def spline_delete_keyframes(spline_id: str, start: int, end: int | None = None) -> str:
    """Delete keyframes in a frame range.

    Args:
        spline_id: FusionSpline ID
        start: Start frame
        end: End frame (optional — if omitted, deletes only the keyframe at start)
    """
    try:
        _, spline = _get_spline(spline_id)
        if end is not None:
            spline.DeleteKeyFrames(start, end)
            return _ok(f"Deleted keyframes from {start} to {end}")
        else:
            spline.DeleteKeyFrames(start)
            return _ok(f"Deleted keyframe at {start}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def spline_adjust_keyframes(
    spline_id: str,
    start: int,
    end: int,
    x: float,
    y: float,
    operation: str = "offset",
    pivot_x: float | None = None,
    pivot_y: float | None = None,
) -> str:
    """Adjust keyframes in a frame range by time and value offset.

    Args:
        spline_id: FusionSpline ID
        start: Start frame of range
        end: End frame of range
        x: Time offset (frames)
        y: Value offset
        operation: "offset" to shift, "scale" to scale around pivot
        pivot_x: Pivot X for scale operation (frame)
        pivot_y: Pivot Y for scale operation (value)
    """
    try:
        _, spline = _get_spline(spline_id)
        args = [start, end, x, y, operation]
        if pivot_x is not None:
            args.append(pivot_x)
        if pivot_y is not None:
            args.append(pivot_y)
        spline.AdjustKeyFrames(*args)
        return _ok(f"Adjusted keyframes in range {start}-{end}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def spline_get_spline_from_input(input_id: str) -> str:
    """Get the BezierSpline modifier attached to a Fusion input.

    This is how you access keyframe animation data for an animated input.
    The input must have a BezierSpline modifier (added via tool_add_modifier).

    Args:
        input_id: FusionInput ID

    Returns a FusionSpline reference if the input has a BezierSpline,
    or an error if no spline modifier is attached.
    """
    try:
        conn = get_connection()
        inp = conn.get(input_id, "FusionInput")
        # The connected output of an animated input is the spline
        out = inp.GetConnectedOutput()
        if out is None:
            return _err("Input has no connected modifier (not animated)")
        tool = out.GetTool()
        if tool is None:
            return _err("Could not get modifier tool")
        # Check if it's a BezierSpline
        attrs = tool.GetAttrs()
        reg_id = attrs.get("TOOLS_RegID", "")
        if "Spline" not in reg_id and "BezierSpline" not in reg_id:
            return _err(f"Connected modifier is '{reg_id}', not a BezierSpline")
        sid = conn.register(tool, "FusionSpline", composite_key=f"fspline:{input_id}")
        return _ok({
            "id": sid,
            "type": "FusionSpline",
            "name": tool.Name,
        })
    except Exception as e:
        return _err(str(e))
