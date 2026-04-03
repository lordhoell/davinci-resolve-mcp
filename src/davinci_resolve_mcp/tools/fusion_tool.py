"""Tools for the Fusion Operator (Tool) object.

Covers: tool properties, inputs/outputs, connections,
settings, modifiers, selection, deletion.

Every node in Fusion's flow graph is an Operator (commonly called a "Tool").
Examples: TextPlus, Merge, Background, Blur, Transform, MediaIn, MediaOut.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_tool(tool_id: str):
    conn = get_connection()
    return conn, conn.get(tool_id, "FusionTool")


# ── Tool Properties ──────────────────────────────────────────────

@mcp.tool()
def tool_get_attrs(tool_id: str) -> str:
    """Get all attributes of a Fusion tool.

    Args:
        tool_id: FusionTool ID

    Returns dict including:
    - TOOLS_Name: tool name
    - TOOLS_RegID: registry ID (tool type)
    - TOOLB_Locked: is locked
    - TOOLB_PassThrough: pass-through mode
    - TOOLB_HoldOutput: hold output
    - TOOLB_Visible: visibility
    """
    try:
        _, tool = _get_tool(tool_id)
        return _ok(tool.GetAttrs())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_get_name(tool_id: str) -> str:
    """Get the name of a Fusion tool.

    Args:
        tool_id: FusionTool ID
    """
    try:
        _, tool = _get_tool(tool_id)
        return _ok(tool.Name)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_get_id(tool_id: str) -> str:
    """Get the registry type ID of a Fusion tool.

    Args:
        tool_id: FusionTool ID

    Returns the type string (e.g., "TextPlus", "Merge", "Background").
    """
    try:
        _, tool = _get_tool(tool_id)
        return _ok(tool.ID)
    except Exception as e:
        return _err(str(e))


# ── Input/Output Discovery ──────────────────────────────────────

@mcp.tool()
def tool_get_input_list(tool_id: str, input_type: str | None = None) -> str:
    """Get all inputs of a Fusion tool.

    This is how you discover what parameters a tool has.
    Each input can be read/written with tool_set_input/tool_get_input.

    Args:
        tool_id: FusionTool ID
        input_type: Optional filter by data type

    Returns dict of input ID -> FusionInput reference.
    """
    try:
        conn, tool = _get_tool(tool_id)
        inputs = tool.GetInputList(input_type)
        if inputs is None:
            return _ok({})
        result = {}
        for key, inp in inputs.items():
            attrs = inp.GetAttrs()
            iid = conn.register(
                inp, "FusionInput",
                composite_key=f"finput:{tool_id}:{attrs.get('INPS_ID', key)}"
            )
            result[str(key)] = {
                "id": iid,
                "type": "FusionInput",
                "name": attrs.get("INPS_Name", ""),
                "input_id": attrs.get("INPS_ID", ""),
                "data_type": attrs.get("INPS_DataType", ""),
            }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_get_output_list(tool_id: str) -> str:
    """Get all outputs of a Fusion tool.

    Args:
        tool_id: FusionTool ID

    Returns dict of output ID -> FusionOutput reference.
    """
    try:
        conn, tool = _get_tool(tool_id)
        outputs = tool.GetOutputList()
        if outputs is None:
            return _ok({})
        result = {}
        for key, out in outputs.items():
            attrs = out.GetAttrs()
            oid = conn.register(
                out, "FusionOutput",
                composite_key=f"foutput:{tool_id}:{attrs.get('OUTS_ID', key)}"
            )
            result[str(key)] = {
                "id": oid,
                "type": "FusionOutput",
                "name": attrs.get("OUTS_Name", ""),
                "output_id": attrs.get("OUTS_ID", ""),
                "data_type": attrs.get("OUTS_DataType", ""),
            }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Setting Values ───────────────────────────────────────────────

@mcp.tool()
def tool_set_input(tool_id: str, input_name: str, value: str | int | float | bool, time: int | None = None) -> str:
    """Set a value on a tool's input.

    This is the primary way to configure tool parameters.

    Args:
        tool_id: FusionTool ID
        input_name: Input ID (e.g., "StyledText" for TextPlus text content,
                    "TopLeftRed" for color, "Size" for font size, "Center" for position,
                    "Blend" for opacity). Use tool_get_input_list() to discover inputs.
        value: Value to set (type depends on the input)
        time: Optional frame number for keyframed values. If omitted, sets a static value.

    Common TextPlus inputs: StyledText, Font, Size, Red1/Green1/Blue1 (color),
    Center (position), Tracking, LineSpacing, ShadingEnabled, etc.

    Common Merge inputs: Center, Size, Angle, Blend, BlendClone.

    Common Background inputs: TopLeftRed, TopLeftGreen, TopLeftBlue, TopLeftAlpha,
    Width, Height, Depth.
    """
    try:
        _, tool = _get_tool(tool_id)
        if time is not None:
            tool.SetInput(input_name, value, time)
        else:
            tool.SetInput(input_name, value)
        return _ok(f"Input '{input_name}' set to {value}" + (f" at frame {time}" if time else ""))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_get_input(tool_id: str, input_name: str, time: int | None = None) -> str:
    """Get the current value of a tool's input.

    Args:
        tool_id: FusionTool ID
        input_name: Input ID (e.g., "StyledText", "Size", "Center")
        time: Optional frame number. If omitted, returns value at current time.
    """
    try:
        _, tool = _get_tool(tool_id)
        if time is not None:
            result = tool.GetInput(input_name, time)
        else:
            result = tool.GetInput(input_name)
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Connections ──────────────────────────────────────────────────

@mcp.tool()
def tool_connect_input(tool_id: str, input_name: str, target_tool_id: str, target_output: str = "Output") -> str:
    """Connect a tool's input to another tool's output.

    This creates a pipe (connection) between two nodes in the flow.

    Args:
        tool_id: FusionTool ID (the receiving tool)
        input_name: Input ID on the receiving tool (e.g., "Background", "Foreground",
                    "Input", "EffectMask")
        target_tool_id: FusionTool ID of the source tool
        target_output: Output ID on the source tool (default: "Output")

    Common connection patterns:
    - Merge.Background <- Background.Output
    - Merge.Foreground <- TextPlus.Output
    - Blur.Input <- Merge.Output
    """
    try:
        conn, tool = _get_tool(tool_id)
        target = conn.get(target_tool_id, "FusionTool")
        result = tool.ConnectInput(input_name, target)
        if result:
            return _ok(f"Connected {input_name} to {target.Name}")
        return _err(f"Failed to connect {input_name}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_disconnect_input(tool_id: str, input_name: str) -> str:
    """Disconnect a tool's input (remove the pipe).

    Args:
        tool_id: FusionTool ID
        input_name: Input ID to disconnect
    """
    try:
        _, tool = _get_tool(tool_id)
        result = tool.ConnectInput(input_name, None)
        if result:
            return _ok(f"Disconnected {input_name}")
        return _err(f"Failed to disconnect {input_name}")
    except Exception as e:
        return _err(str(e))


# ── Modifiers ────────────────────────────────────────────────────

@mcp.tool()
def tool_add_modifier(tool_id: str, input_name: str, modifier_type: str) -> str:
    """Add a modifier (animation, expression, etc.) to a tool's input.

    Args:
        tool_id: FusionTool ID
        input_name: Input ID to add the modifier to
        modifier_type: Modifier registry ID. Common types:
                       "BezierSpline" — keyframe animation
                       "XYPath" — animated position path
                       "PolyPath" — polyline animation path
                       "Expression" — expression modifier
                       "Calculation" — math expression
                       "Perturbation" — random/noise
                       "Probe" — probe another value
    """
    try:
        _, tool = _get_tool(tool_id)
        result = tool.AddModifier(input_name, modifier_type)
        if result:
            return _ok(f"Modifier '{modifier_type}' added to '{input_name}'")
        return _err(f"Failed to add modifier to '{input_name}'")
    except Exception as e:
        return _err(str(e))


# ── Settings Save/Load ───────────────────────────────────────────

@mcp.tool()
def tool_save_settings(tool_id: str, filename: str | None = None) -> str:
    """Save a tool's settings to a file or return as a dict.

    Args:
        tool_id: FusionTool ID
        filename: Optional file path (.setting). If omitted, returns settings dict.
    """
    try:
        _, tool = _get_tool(tool_id)
        if filename:
            result = tool.SaveSettings(filename)
            if result:
                return _ok(f"Settings saved to '{filename}'")
            return _err("Failed to save settings")
        else:
            settings = tool.SaveSettings()
            return _ok(settings)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_load_settings(tool_id: str, filename_or_settings: str | dict) -> str:
    """Load settings onto a tool from a file or dict.

    Args:
        tool_id: FusionTool ID
        filename_or_settings: File path (.setting) or settings dict
    """
    try:
        _, tool = _get_tool(tool_id)
        result = tool.LoadSettings(filename_or_settings)
        if result:
            return _ok("Settings loaded")
        return _err("Failed to load settings")
    except Exception as e:
        return _err(str(e))


# ── Tool State ───────────────────────────────────────────────────

@mcp.tool()
def tool_delete(tool_id: str) -> str:
    """Delete a tool from the composition.

    Warning: This is destructive and cannot be undone unless inside an undo block.

    Args:
        tool_id: FusionTool ID
    """
    try:
        conn, tool = _get_tool(tool_id)
        tool.Delete()
        conn.remove(tool_id)
        return _ok("Tool deleted")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_refresh(tool_id: str) -> str:
    """Force a refresh/recalculation of the tool.

    Args:
        tool_id: FusionTool ID
    """
    try:
        _, tool = _get_tool(tool_id)
        tool.Refresh()
        return _ok("Tool refreshed")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_get_keyframes(tool_id: str) -> str:
    """Get all keyframe times for a tool (across all animated inputs).

    Args:
        tool_id: FusionTool ID

    Returns dict of frame number -> keyframe info.
    """
    try:
        _, tool = _get_tool(tool_id)
        return _ok(tool.GetKeyFrames())
    except Exception as e:
        return _err(str(e))


# ── Custom Data ──────────────────────────────────────────────────

@mcp.tool()
def tool_get_data(tool_id: str, name: str | None = None) -> str:
    """Get custom persistent data stored on a tool.

    Args:
        tool_id: FusionTool ID
        name: Data key name. If omitted, returns all stored data.
    """
    try:
        _, tool = _get_tool(tool_id)
        result = tool.GetData(name) if name else tool.GetData()
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_set_data(tool_id: str, name: str, value: str | int | float | bool | None) -> str:
    """Set custom persistent data on a tool.

    Args:
        tool_id: FusionTool ID
        name: Data key name
        value: Data value (or None to delete)
    """
    try:
        _, tool = _get_tool(tool_id)
        tool.SetData(name, value)
        return _ok(f"Data '{name}' set")
    except Exception as e:
        return _err(str(e))


# ── Control Pages ────────────────────────────────────────────────

@mcp.tool()
def tool_get_control_page_names(tool_id: str) -> str:
    """Get the names of control pages for a tool.

    Control pages organize the tool's inputs into logical groups
    in the Inspector panel.

    Args:
        tool_id: FusionTool ID
    """
    try:
        _, tool = _get_tool(tool_id)
        return _ok(tool.GetControlPageNames())
    except Exception as e:
        return _err(str(e))


# ── Tool Appearance ──────────────────────────────────────────────

@mcp.tool()
def tool_set_tile_color(tool_id: str, r: float, g: float, b: float) -> str:
    """Set the background tile color of a tool in the flow.

    Args:
        tool_id: FusionTool ID
        r: Red (0.0-1.0)
        g: Green (0.0-1.0)
        b: Blue (0.0-1.0)
    """
    try:
        _, tool = _get_tool(tool_id)
        tool.TileColor = {"R": r, "G": g, "B": b}
        return _ok(f"Tile color set to ({r}, {g}, {b})")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def tool_set_text_color(tool_id: str, r: float, g: float, b: float) -> str:
    """Set the text label color of a tool in the flow.

    Args:
        tool_id: FusionTool ID
        r: Red (0.0-1.0)
        g: Green (0.0-1.0)
        b: Blue (0.0-1.0)
    """
    try:
        _, tool = _get_tool(tool_id)
        tool.TextColor = {"R": r, "G": g, "B": b}
        return _ok(f"Text color set to ({r}, {g}, {b})")
    except Exception as e:
        return _err(str(e))
