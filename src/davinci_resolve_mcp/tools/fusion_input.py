"""Tools for the Fusion PlainInput object.

Covers: reading input state, connections, expressions,
keyframe queries, visibility control.

PlainInput objects represent the connectable inputs on Fusion tools.
Get them via tool_get_input_list().
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_input(input_id: str):
    conn = get_connection()
    return conn, conn.get(input_id, "FusionInput")


@mcp.tool()
def input_get_attrs(input_id: str) -> str:
    """Get attributes of a Fusion input.

    Args:
        input_id: FusionInput ID

    Returns dict including:
    - INPS_Name: display name
    - INPS_ID: input ID string
    - INPS_DataType: data type (Number, Point, Text, Image, etc.)
    - INPB_Connected: whether something is connected
    - INPB_External: whether exposed externally
    - INP_MinAllowed / INP_MaxAllowed: value range
    - INP_Default: default value
    """
    try:
        _, inp = _get_input(input_id)
        return _ok(inp.GetAttrs())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_get_expression(input_id: str) -> str:
    """Get the expression set on an input.

    Args:
        input_id: FusionInput ID

    Returns the expression string, or empty if no expression is set.
    """
    try:
        _, inp = _get_input(input_id)
        return _ok(inp.GetExpression())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_set_expression(input_id: str, expression: str) -> str:
    """Set an expression on an input.

    Expressions are evaluated every frame to produce the input's value.

    Args:
        input_id: FusionInput ID
        expression: Expression string (Fusion expression syntax).
                    Examples:
                    - "time / 30" — linear ramp based on frame number
                    - "Background1.TopLeftRed" — reference another tool's value
                    - "math.sin(time * 0.1) * 0.5 + 0.5" — oscillation
    """
    try:
        _, inp = _get_input(input_id)
        inp.SetExpression(expression)
        return _ok(f"Expression set: {expression}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_connect_to(input_id: str, output_id: str | None = None) -> str:
    """Connect an input to an output, or disconnect it.

    Args:
        input_id: FusionInput ID
        output_id: FusionOutput ID to connect to. If None, disconnects.
    """
    try:
        conn, inp = _get_input(input_id)
        if output_id:
            out = conn.get(output_id, "FusionOutput")
            result = inp.ConnectTo(out)
        else:
            result = inp.ConnectTo()
        if result:
            return _ok("Connected" if output_id else "Disconnected")
        return _err("Connection failed")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_get_connected_output(input_id: str) -> str:
    """Get the output that is connected to this input.

    Args:
        input_id: FusionInput ID

    Returns a FusionOutput reference, or null if not connected.
    """
    try:
        conn, inp = _get_input(input_id)
        out = inp.GetConnectedOutput()
        if out is None:
            return _ok(None)
        attrs = out.GetAttrs()
        oid = conn.register(out, "FusionOutput", composite_key=f"foutput:connected:{input_id}")
        return _ok({
            "id": oid,
            "type": "FusionOutput",
            "name": attrs.get("OUTS_Name", ""),
            "output_id": attrs.get("OUTS_ID", ""),
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_get_keyframes(input_id: str) -> str:
    """Get all keyframe times for this input.

    Args:
        input_id: FusionInput ID

    Returns dict/table of keyframe times.
    """
    try:
        _, inp = _get_input(input_id)
        return _ok(inp.GetKeyFrames())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_get_tool(input_id: str) -> str:
    """Get the tool that owns this input.

    Args:
        input_id: FusionInput ID
    """
    try:
        conn, inp = _get_input(input_id)
        tool = inp.GetTool()
        if tool is None:
            return _err("No owning tool")
        tid = conn.register(tool, "FusionTool", composite_key=f"ftool:from_input:{tool.Name}")
        return _ok({
            "id": tid,
            "type": "FusionTool",
            "name": tool.Name,
            "tool_type": tool.ID,
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_hide_view_controls(input_id: str, hide: bool = True) -> str:
    """Hide or show the on-screen view controls for this input.

    Args:
        input_id: FusionInput ID
        hide: True to hide, False to show
    """
    try:
        _, inp = _get_input(input_id)
        inp.HideViewControls(hide)
        return _ok(f"View controls {'hidden' if hide else 'shown'}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_hide_window_controls(input_id: str, hide: bool = True) -> str:
    """Hide or show the inspector panel controls for this input.

    Args:
        input_id: FusionInput ID
        hide: True to hide, False to show
    """
    try:
        _, inp = _get_input(input_id)
        inp.HideWindowControls(hide)
        return _ok(f"Window controls {'hidden' if hide else 'shown'}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_view_controls_visible(input_id: str) -> str:
    """Check if the on-screen view controls are visible for this input.

    Args:
        input_id: FusionInput ID
    """
    try:
        _, inp = _get_input(input_id)
        return _ok(inp.ViewControlsVisible())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_window_controls_visible(input_id: str) -> str:
    """Check if the inspector panel controls are visible for this input.

    Args:
        input_id: FusionInput ID
    """
    try:
        _, inp = _get_input(input_id)
        return _ok(inp.WindowControlsVisible())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def input_get_data(input_id: str, name: str | None = None) -> str:
    """Get custom data stored on an input.

    Args:
        input_id: FusionInput ID
        name: Data key name. If omitted, returns all data.
    """
    try:
        _, inp = _get_input(input_id)
        result = inp.GetData(name) if name else inp.GetData()
        return _ok(result)
    except Exception as e:
        return _err(str(e))
