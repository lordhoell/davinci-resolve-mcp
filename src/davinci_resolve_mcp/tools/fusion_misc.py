"""Miscellaneous Fusion tools.

Covers: Fusion app object, Registry (tool type discovery),
FontList, ImageCacheManager, Loader, PolylineMask, TimeRegion.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


# ── Fusion App ───────────────────────────────────────────────────

@mcp.tool()
def fusion_get_version() -> str:
    """Get the Fusion application version.

    Returns version info including build number.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        return _ok({
            "version": fusion.Version,
            "build": fusion.Build,
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def fusion_get_global_path_map() -> str:
    """Get all Fusion global path maps.

    Path maps define shortcuts like "Scripts:", "Comp:", "Temp:" etc.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        return _ok(fusion.GetGlobalPathMap())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def fusion_get_prefs(pref_name: str | None = None) -> str:
    """Get Fusion application preferences.

    Args:
        pref_name: Optional specific preference key.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        result = fusion.GetPrefs(pref_name) if pref_name else fusion.GetPrefs()
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Registry (Tool Type Discovery) ──────────────────────────────

@mcp.tool()
def fusion_get_reg_list(type_mask: str = "CT_Tool") -> str:
    """Get a list of registered tool types.

    Use this to discover what tool types are available for comp_add_tool().

    Args:
        type_mask: Registry type filter. Options:
                   "CT_Tool" — regular tools (Background, Merge, Transform, etc.)
                   "CT_Filter" — filter tools (Blur, Sharpen, etc.)
                   "CT_FilterSource" — source/generator tools (TextPlus, Plasma, etc.)
                   "CT_Modifier" — modifiers (BezierSpline, Expression, etc.)
                   "CT_Mask" — mask tools (Rectangle, Ellipse, Polygon, etc.)
                   "CT_3D" — 3D tools
                   "CT_ParticleTool" — particle tools

    Returns list of tool registry entries with ID and name.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        from davinci_resolve_mcp.constants import FUSION_REG_TYPES
        mask = FUSION_REG_TYPES.get(type_mask)
        if mask is None:
            return _err(f"Unknown type mask '{type_mask}'. Valid: {list(FUSION_REG_TYPES.keys())}")
        regs = fusion.GetRegList(mask)
        if regs is None:
            return _ok([])
        result = []
        for key, reg in regs.items():
            attrs = fusion.GetRegAttrs(reg.ID)
            result.append({
                "id": reg.ID,
                "name": attrs.get("REGS_Name", reg.ID),
            })
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def fusion_get_reg_attrs(tool_type: str) -> str:
    """Get detailed attributes for a registered tool type.

    Use this to learn about a tool type's capabilities before creating it.

    Args:
        tool_type: Tool registry ID (e.g., "TextPlus", "Merge", "Background")

    Returns dict of registry attributes including name, category,
    help text, input/output types, etc.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        attrs = fusion.GetRegAttrs(tool_type)
        if attrs is None:
            return _err(f"Unknown tool type '{tool_type}'")
        return _ok(attrs)
    except Exception as e:
        return _err(str(e))


# ── Font List ────────────────────────────────────────────────────

@mcp.tool()
def fusion_get_font_list() -> str:
    """Get a list of all available fonts in Fusion.

    Returns font names that can be used with TextPlus and other text tools.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        fonts = fusion.FontManager.GetFontList()
        return _ok(fonts)
    except Exception as e:
        return _err(str(e))


# ── Image Cache ──────────────────────────────────────────────────

@mcp.tool()
def fusion_cache_get_size() -> str:
    """Get the current size of Fusion's image cache.

    Returns the cache size in bytes.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        return _ok(fusion.CacheManager.GetSize())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def fusion_cache_purge() -> str:
    """Purge Fusion's image cache.

    Frees all cached image data from memory.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        fusion.CacheManager.Purge()
        return _ok("Image cache purged")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def fusion_cache_free_space() -> str:
    """Get the free space available in the image cache.

    Returns bytes available.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        return _ok(fusion.CacheManager.FreeSpace())
    except Exception as e:
        return _err(str(e))


# ── Loader ───────────────────────────────────────────────────────

@mcp.tool()
def loader_set_multi_clip(tool_id: str, filename: str, start_frame: int | None = None, trim_in: int | None = None, trim_out: int | None = None) -> str:
    """Set a Loader tool's clip from a multi-frame file sequence.

    Args:
        tool_id: FusionTool ID (must be a Loader tool)
        filename: File path (can include frame padding like "image_####.exr")
        start_frame: Optional start frame number
        trim_in: Optional trim in frame
        trim_out: Optional trim out frame
    """
    try:
        conn = get_connection()
        tool = conn.get(tool_id, "FusionTool")
        args = [filename]
        if start_frame is not None:
            args.append(start_frame)
        if trim_in is not None:
            args.append(trim_in)
        if trim_out is not None:
            args.append(trim_out)
        tool.SetMultiClip(*args)
        return _ok(f"Loader clip set to '{filename}'")
    except Exception as e:
        return _err(str(e))


# ── PolylineMask ─────────────────────────────────────────────────

@mcp.tool()
def polyline_mask_get_bezier_polyline(tool_id: str, time: int | None = None) -> str:
    """Get the bezier polyline points of a mask at a given time.

    Args:
        tool_id: FusionTool ID (must be a PolylineMask)
        time: Frame number (default: current time)

    Returns the polyline point data.
    """
    try:
        conn = get_connection()
        tool = conn.get(tool_id, "FusionTool")
        if time is not None:
            result = tool.GetBezierPolyline(time)
        else:
            result = tool.GetBezierPolyline()
        return _ok(result)
    except Exception as e:
        return _err(str(e))
