"""Tools for the Fusion PlainOutput object.

Covers: reading output values, connections, disk caching.

PlainOutput objects represent the data outputs from Fusion tools.
Get them via tool_get_output_list().
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_output(output_id: str):
    conn = get_connection()
    return conn, conn.get(output_id, "FusionOutput")


@mcp.tool()
def output_get_attrs(output_id: str) -> str:
    """Get attributes of a Fusion output.

    Args:
        output_id: FusionOutput ID
    """
    try:
        _, out = _get_output(output_id)
        return _ok(out.GetAttrs())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def output_get_value(output_id: str, time: int | None = None) -> str:
    """Get the value of a Fusion output at a given time.

    For image outputs, this returns image metadata (not pixel data).
    For number/point/text outputs, returns the actual value.

    Args:
        output_id: FusionOutput ID
        time: Frame number (default: current time)
    """
    try:
        _, out = _get_output(output_id)
        if time is not None:
            val = out.GetValue(time)
        else:
            val = out.GetValue()
        # If the value is an Image object, return its metadata
        if hasattr(val, 'Width'):
            return _ok({
                "type": "Image",
                "width": val.Width,
                "height": val.Height,
                "depth": val.Depth,
            })
        return _ok(val)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def output_get_connected_inputs(output_id: str) -> str:
    """Get all inputs that are connected to this output.

    Args:
        output_id: FusionOutput ID

    Returns list of FusionInput references.
    """
    try:
        conn, out = _get_output(output_id)
        inputs = out.GetConnectedInputs()
        if inputs is None:
            return _ok([])
        result = []
        for key, inp in inputs.items():
            attrs = inp.GetAttrs()
            iid = conn.register(
                inp, "FusionInput",
                composite_key=f"finput:from_output:{output_id}:{key}"
            )
            result.append({
                "id": iid,
                "type": "FusionInput",
                "name": attrs.get("INPS_Name", ""),
                "input_id": attrs.get("INPS_ID", ""),
            })
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def output_get_dod(output_id: str, time: int | None = None) -> str:
    """Get the Domain of Definition (DoD) for this output.

    The DoD describes the bounding rectangle of valid image data.

    Args:
        output_id: FusionOutput ID
        time: Frame number (default: current time)
    """
    try:
        _, out = _get_output(output_id)
        if time is not None:
            result = out.GetDoD(time)
        else:
            result = out.GetDoD()
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def output_enable_disk_cache(
    output_id: str,
    enable: bool,
    path: str,
    lock_cache: bool = False,
    lock_branch: bool = False,
) -> str:
    """Enable or disable disk caching for this output.

    Args:
        output_id: FusionOutput ID
        enable: True to enable, False to disable
        path: Cache file path
        lock_cache: Lock the cache to prevent invalidation
        lock_branch: Lock the entire branch
    """
    try:
        _, out = _get_output(output_id)
        result = out.EnableDiskCache(enable, path, lock_cache, lock_branch)
        if result:
            return _ok(f"Disk cache {'enabled' if enable else 'disabled'}")
        return _err("Failed to modify disk cache")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def output_clear_disk_cache(output_id: str, start: int, end: int) -> str:
    """Clear disk cache for a frame range.

    Args:
        output_id: FusionOutput ID
        start: Start frame
        end: End frame
    """
    try:
        _, out = _get_output(output_id)
        result = out.ClearDiskCache(start, end)
        if result:
            return _ok(f"Disk cache cleared for frames {start}-{end}")
        return _err("Failed to clear disk cache")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def output_get_tool(output_id: str) -> str:
    """Get the tool that owns this output.

    Args:
        output_id: FusionOutput ID
    """
    try:
        conn, out = _get_output(output_id)
        tool = out.GetTool()
        if tool is None:
            return _err("No owning tool")
        tid = conn.register(tool, "FusionTool", composite_key=f"ftool:from_output:{tool.Name}")
        return _ok({
            "id": tid,
            "type": "FusionTool",
            "name": tool.Name,
            "tool_type": tool.ID,
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def output_get_data(output_id: str, name: str | None = None) -> str:
    """Get custom data stored on an output.

    Args:
        output_id: FusionOutput ID
        name: Data key name. If omitted, returns all data.
    """
    try:
        _, out = _get_output(output_id)
        result = out.GetData(name) if name else out.GetData()
        return _ok(result)
    except Exception as e:
        return _err(str(e))
