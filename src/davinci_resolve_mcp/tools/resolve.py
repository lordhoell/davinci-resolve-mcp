"""Tools for the top-level Resolve object.

Covers: app control, page navigation, layout presets, render presets,
burn-in presets, keyframe mode, Fairlight presets.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.constants import KEYFRAME_MODES, resolve_enum

logger = logging.getLogger(__name__)


# ── Helper: standard response wrappers ────────────────────────────

def _ok(result=None) -> str:
    """Return a success response as a JSON-compatible string."""
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    """Return an error response as a JSON-compatible string."""
    return json.dumps({"success": False, "error": message})


# ── Tools ─────────────────────────────────────────────────────────

@mcp.tool()
def resolve_get_product_name() -> str:
    """Get the product name of the running DaVinci Resolve instance."""
    try:
        conn = get_connection()
        return _ok(conn.resolve.GetProductName())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_get_version() -> str:
    """Get DaVinci Resolve version as [major, minor, patch, build, suffix]."""
    try:
        conn = get_connection()
        return _ok(conn.resolve.GetVersion())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_get_version_string() -> str:
    """Get DaVinci Resolve version as a formatted string like '19.1.2.0009'."""
    try:
        conn = get_connection()
        return _ok(conn.resolve.GetVersionString())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_get_current_page() -> str:
    """Get the currently active page in DaVinci Resolve.

    Returns one of: 'media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver', or null.
    """
    try:
        conn = get_connection()
        return _ok(conn.resolve.GetCurrentPage())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_open_page(page_name: str) -> str:
    """Switch to a specific page in DaVinci Resolve.

    Args:
        page_name: One of 'media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver'
    """
    try:
        valid_pages = ("media", "cut", "edit", "fusion", "color", "fairlight", "deliver")
        if page_name.lower() not in valid_pages:
            return _err(f"Invalid page '{page_name}'. Must be one of: {', '.join(valid_pages)}")
        conn = get_connection()
        result = conn.resolve.OpenPage(page_name.lower())
        if result:
            return _ok(f"Switched to {page_name} page")
        return _err(f"Failed to switch to {page_name} page")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_get_project_manager() -> str:
    """Get the ProjectManager object for the current database.

    Returns the ProjectManager ID for use in subsequent project management calls.
    """
    try:
        conn = get_connection()
        pm = conn.get_project_manager()
        pm_id = conn.register(pm, "ProjectManager", composite_key="project_manager")
        return _ok({"id": pm_id, "type": "ProjectManager"})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_get_media_storage() -> str:
    """Get the MediaStorage object to query and act on media locations.

    Returns the MediaStorage ID for use in media storage calls.
    """
    try:
        conn = get_connection()
        ms = conn.get_media_storage()
        ms_id = conn.register(ms, "MediaStorage", composite_key="media_storage")
        return _ok({"id": ms_id, "type": "MediaStorage"})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_fusion() -> str:
    """Get the Fusion object (starting point for Fusion scripting).

    Returns the Fusion object ID.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Failed to get Fusion object")
        fid = conn.register(fusion, "Fusion", composite_key="fusion")
        return _ok({"id": fid, "type": "Fusion"})
    except Exception as e:
        return _err(str(e))


# ── Layout Presets ────────────────────────────────────────────────

@mcp.tool()
def resolve_save_layout_preset(preset_name: str) -> str:
    """Save the current UI layout as a preset.

    Args:
        preset_name: Name for the new preset
    """
    try:
        conn = get_connection()
        result = conn.resolve.SaveLayoutPreset(preset_name)
        if result:
            return _ok(f"Layout preset '{preset_name}' saved")
        return _err(f"Failed to save layout preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_load_layout_preset(preset_name: str) -> str:
    """Load a saved UI layout preset.

    Args:
        preset_name: Name of the preset to load
    """
    try:
        conn = get_connection()
        result = conn.resolve.LoadLayoutPreset(preset_name)
        if result:
            return _ok(f"Layout preset '{preset_name}' loaded")
        return _err(f"Failed to load layout preset '{preset_name}'. Check the name is correct.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_update_layout_preset(preset_name: str) -> str:
    """Overwrite an existing layout preset with the current UI layout.

    Args:
        preset_name: Name of the preset to overwrite
    """
    try:
        conn = get_connection()
        result = conn.resolve.UpdateLayoutPreset(preset_name)
        if result:
            return _ok(f"Layout preset '{preset_name}' updated")
        return _err(f"Failed to update layout preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_delete_layout_preset(preset_name: str) -> str:
    """Delete a saved UI layout preset.

    Args:
        preset_name: Name of the preset to delete
    """
    try:
        conn = get_connection()
        result = conn.resolve.DeleteLayoutPreset(preset_name)
        if result:
            return _ok(f"Layout preset '{preset_name}' deleted")
        return _err(f"Failed to delete layout preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_export_layout_preset(preset_name: str, preset_file_path: str) -> str:
    """Export a layout preset to a file.

    Args:
        preset_name: Name of the preset to export
        preset_file_path: File path to export the preset to
    """
    try:
        conn = get_connection()
        result = conn.resolve.ExportLayoutPreset(preset_name, preset_file_path)
        if result:
            return _ok(f"Layout preset '{preset_name}' exported to '{preset_file_path}'")
        return _err(f"Failed to export layout preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_import_layout_preset(preset_file_path: str, preset_name: str | None = None) -> str:
    """Import a layout preset from a file.

    Args:
        preset_file_path: Path to the preset file to import
        preset_name: Optional name for the imported preset. If not specified, uses the filename.
    """
    try:
        conn = get_connection()
        if preset_name:
            result = conn.resolve.ImportLayoutPreset(preset_file_path, preset_name)
        else:
            result = conn.resolve.ImportLayoutPreset(preset_file_path)
        if result:
            name_info = f" as '{preset_name}'" if preset_name else ""
            return _ok(f"Layout preset imported from '{preset_file_path}'{name_info}")
        return _err(f"Failed to import layout preset from '{preset_file_path}'")
    except Exception as e:
        return _err(str(e))


# ── Render Presets ────────────────────────────────────────────────

@mcp.tool()
def resolve_import_render_preset(preset_path: str) -> str:
    """Import a render preset from a file and set it as the current rendering preset.

    Args:
        preset_path: File path to the render preset
    """
    try:
        conn = get_connection()
        result = conn.resolve.ImportRenderPreset(preset_path)
        if result:
            return _ok(f"Render preset imported from '{preset_path}'")
        return _err(f"Failed to import render preset from '{preset_path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_export_render_preset(preset_name: str, export_path: str) -> str:
    """Export a render preset to a file.

    Args:
        preset_name: Name of the render preset to export
        export_path: File path to export the preset to
    """
    try:
        conn = get_connection()
        result = conn.resolve.ExportRenderPreset(preset_name, export_path)
        if result:
            return _ok(f"Render preset '{preset_name}' exported to '{export_path}'")
        return _err(f"Failed to export render preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


# ── Burn-In Presets ───────────────────────────────────────────────

@mcp.tool()
def resolve_import_burn_in_preset(preset_path: str) -> str:
    """Import a data burn-in preset from a file.

    Args:
        preset_path: File path to the burn-in preset
    """
    try:
        conn = get_connection()
        result = conn.resolve.ImportBurnInPreset(preset_path)
        if result:
            return _ok(f"Burn-in preset imported from '{preset_path}'")
        return _err(f"Failed to import burn-in preset from '{preset_path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_export_burn_in_preset(preset_name: str, export_path: str) -> str:
    """Export a data burn-in preset to a file.

    Args:
        preset_name: Name of the burn-in preset to export
        export_path: File path to export the preset to
    """
    try:
        conn = get_connection()
        result = conn.resolve.ExportBurnInPreset(preset_name, export_path)
        if result:
            return _ok(f"Burn-in preset '{preset_name}' exported to '{export_path}'")
        return _err(f"Failed to export burn-in preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


# ── Keyframe Mode ─────────────────────────────────────────────────

@mcp.tool()
def resolve_get_keyframe_mode() -> str:
    """Get the current keyframe mode.

    Returns one of: ALL (0), COLOR (1), SIZING (2).
    """
    try:
        conn = get_connection()
        mode = conn.resolve.GetKeyframeMode()
        mode_name = {0: "ALL", 1: "COLOR", 2: "SIZING"}.get(mode, f"UNKNOWN({mode})")
        return _ok({"mode": mode, "name": mode_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def resolve_set_keyframe_mode(keyframe_mode: str) -> str:
    """Set the keyframe mode.

    Args:
        keyframe_mode: One of 'ALL', 'COLOR', 'SIZING'
    """
    try:
        conn = get_connection()
        mode_value = resolve_enum(conn.resolve, KEYFRAME_MODES, keyframe_mode)
        result = conn.resolve.SetKeyframeMode(mode_value)
        if result:
            return _ok(f"Keyframe mode set to '{keyframe_mode.upper()}'")
        return _err(f"Failed to set keyframe mode to '{keyframe_mode}'")
    except Exception as e:
        return _err(str(e))


# ── Fairlight Presets ─────────────────────────────────────────────

@mcp.tool()
def resolve_get_fairlight_presets() -> str:
    """Get a list of available Fairlight audio presets.

    Requires DaVinci Resolve 20.2.2 or later.
    """
    try:
        conn = get_connection()
        presets = conn.resolve.GetFairlightPresets()
        return _ok(presets)
    except AttributeError:
        return _err("GetFairlightPresets is not available in this version of DaVinci Resolve (requires 20.2.2+)")
    except Exception as e:
        return _err(str(e))


# ── Quit ──────────────────────────────────────────────────────────

@mcp.tool()
def resolve_quit() -> str:
    """Quit DaVinci Resolve.

    WARNING: This will close DaVinci Resolve entirely. Any unsaved work will be lost.
    Make sure to save your project first using project_manager_save_project.
    """
    try:
        conn = get_connection()
        conn.resolve.Quit()
        return _ok("DaVinci Resolve is quitting")
    except Exception as e:
        return _err(str(e))
