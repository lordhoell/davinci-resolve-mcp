"""Tools for the TimelineItem object.

Covers: properties, markers, flags, clip color, Fusion comps, versions/takes,
CDL, grades, stereo, cache, voice isolation, magic mask, stabilization,
smart reframe, node graph, color groups, LUT export, linked items.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.constants import (
    EXPORT_LUT_TYPES,
    COMPOSITE_MODES,
    RETIME_PROCESSES,
    MOTION_ESTIMATION,
    SCALING_MODES,
    RESIZE_FILTERS,
    DYNAMIC_ZOOM_EASE,
    resolve_enum,
    resolve_int_enum,
)

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_ti(item_id: str):
    conn = get_connection()
    return conn, conn.get(item_id, "TimelineItem")


# ── Name & Duration ──────────────────────────────────────────────

@mcp.tool()
def timeline_item_get_name(item_id: str) -> str:
    """Get the name of a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetName())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_set_name(item_id: str, name: str) -> str:
    """Set the name of a timeline item. Requires Resolve 20.2+.

    Args:
        item_id: TimelineItem ID
        name: New name
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.SetName(name)
        if result:
            return _ok(f"Item renamed to '{name}'")
        return _err("Failed to rename item")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_duration(item_id: str, subframe_precision: bool = False) -> str:
    """Get the duration of a timeline item.

    Args:
        item_id: TimelineItem ID
        subframe_precision: Return fractional frames if True
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetDuration(subframe_precision))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_start(item_id: str, subframe_precision: bool = False) -> str:
    """Get the start frame position on the timeline.

    Args:
        item_id: TimelineItem ID
        subframe_precision: Return fractional frames if True
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetStart(subframe_precision))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_end(item_id: str, subframe_precision: bool = False) -> str:
    """Get the end frame position on the timeline.

    Args:
        item_id: TimelineItem ID
        subframe_precision: Return fractional frames if True
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetEnd(subframe_precision))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_left_offset(item_id: str, subframe_precision: bool = False) -> str:
    """Get the maximum extension by frame for clip from left side.

    Args:
        item_id: TimelineItem ID
        subframe_precision: Return fractional frames if True
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetLeftOffset(subframe_precision))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_right_offset(item_id: str, subframe_precision: bool = False) -> str:
    """Get the maximum extension by frame for clip from right side.

    Args:
        item_id: TimelineItem ID
        subframe_precision: Return fractional frames if True
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetRightOffset(subframe_precision))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_source_start_frame(item_id: str) -> str:
    """Get the start frame position of the media pool clip in the timeline clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetSourceStartFrame())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_source_end_frame(item_id: str) -> str:
    """Get the end frame position of the media pool clip in the timeline clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetSourceEndFrame())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_source_start_time(item_id: str) -> str:
    """Get the start time position of the media pool clip in the timeline clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetSourceStartTime())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_source_end_time(item_id: str) -> str:
    """Get the end time position of the media pool clip in the timeline clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetSourceEndTime())
    except Exception as e:
        return _err(str(e))


# ── Properties ────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_get_property(item_id: str, property_key: str | None = None) -> str:
    """Get timeline item properties (Pan, Tilt, Zoom, Rotation, Crop, Opacity, etc.).

    Args:
        item_id: TimelineItem ID
        property_key: Specific key. If None, returns all properties.
    """
    try:
        _, ti = _get_ti(item_id)
        if property_key:
            return _ok(ti.GetProperty(property_key))
        return _ok(ti.GetProperty())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_set_property(item_id: str, property_key: str, property_value: str | int | float | bool) -> str:
    """Set a timeline item property.

    For enum properties, use string names:
    - CompositeMode: NORMAL, ADD, MULTIPLY, SCREEN, OVERLAY, etc.
    - RetimeProcess: USE_PROJECT, NEAREST, FRAME_BLEND, OPTICAL_FLOW
    - MotionEstimation: USE_PROJECT, STANDARD_FASTER, STANDARD_BETTER, etc.
    - Scaling: USE_PROJECT, CROP, FIT, FILL, STRETCH
    - ResizeFilter: USE_PROJECT, SHARPER, SMOOTHER, BICUBIC, LANCZOS, etc.
    - DynamicZoomEase: LINEAR, IN, OUT, IN_AND_OUT

    Args:
        item_id: TimelineItem ID
        property_key: Property name
        property_value: New value
    """
    try:
        _, ti = _get_ti(item_id)
        value = property_value
        if isinstance(value, str):
            enum_map = {
                "CompositeMode": COMPOSITE_MODES,
                "RetimeProcess": RETIME_PROCESSES,
                "MotionEstimation": MOTION_ESTIMATION,
                "Scaling": SCALING_MODES,
                "ResizeFilter": RESIZE_FILTERS,
                "DynamicZoomEase": DYNAMIC_ZOOM_EASE,
            }
            if property_key in enum_map:
                value = resolve_int_enum(enum_map[property_key], value)
        result = ti.SetProperty(property_key, value)
        if result:
            return _ok(f"Property '{property_key}' set")
        return _err(f"Failed to set '{property_key}'")
    except Exception as e:
        return _err(str(e))


# ── Markers ───────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_add_marker(
    item_id: str, frame_id: float, color: str, name: str,
    note: str, duration: float, custom_data: str | None = None,
) -> str:
    """Add a marker to a timeline item (clip-relative frame position).

    Args:
        item_id: TimelineItem ID
        frame_id: Frame position (relative to clip start)
        color: Marker color
        name: Marker name
        note: Marker note
        duration: Duration in frames
        custom_data: Optional custom data
    """
    try:
        _, ti = _get_ti(item_id)
        if custom_data is not None:
            result = ti.AddMarker(frame_id, color, name, note, duration, custom_data)
        else:
            result = ti.AddMarker(frame_id, color, name, note, duration)
        if result:
            return _ok(f"Marker added at frame {frame_id}")
        return _err("Failed to add marker")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_markers(item_id: str) -> str:
    """Get all markers on a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetMarkers())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_marker_by_custom_data(item_id: str, custom_data: str) -> str:
    """Find the first marker matching custom data on a timeline item.

    Args:
        item_id: TimelineItem ID
        custom_data: Custom data to search for
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetMarkerByCustomData(custom_data))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_update_marker_custom_data(item_id: str, frame_id: float, custom_data: str) -> str:
    """Update custom data for a marker on a timeline item.

    Args:
        item_id: TimelineItem ID
        frame_id: Frame position
        custom_data: New custom data
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.UpdateMarkerCustomData(frame_id, custom_data)
        if result:
            return _ok(f"Marker custom data updated at frame {frame_id}")
        return _err(f"Failed to update marker at frame {frame_id}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_marker_custom_data(item_id: str, frame_id: float) -> str:
    """Get custom data for a marker on a timeline item.

    Args:
        item_id: TimelineItem ID
        frame_id: Frame position
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetMarkerCustomData(frame_id))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_delete_markers_by_color(item_id: str, color: str) -> str:
    """Delete all markers of a color on a timeline item. Use 'All' to delete all.

    Args:
        item_id: TimelineItem ID
        color: Color to delete, or 'All'
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.DeleteMarkersByColor(color)
        if result:
            return _ok(f"Markers of color '{color}' deleted")
        return _err("Failed to delete markers")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_delete_marker_at_frame(item_id: str, frame_num: float) -> str:
    """Delete marker at a frame on a timeline item.

    Args:
        item_id: TimelineItem ID
        frame_num: Frame number
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.DeleteMarkerAtFrame(frame_num)
        if result:
            return _ok(f"Marker deleted at frame {frame_num}")
        return _err(f"No marker at frame {frame_num}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_delete_marker_by_custom_data(item_id: str, custom_data: str) -> str:
    """Delete first marker matching custom data on a timeline item.

    Args:
        item_id: TimelineItem ID
        custom_data: Custom data to match
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.DeleteMarkerByCustomData(custom_data)
        if result:
            return _ok("Marker deleted")
        return _err("No matching marker found")
    except Exception as e:
        return _err(str(e))


# ── Flags & Clip Color ────────────────────────────────────────────

@mcp.tool()
def timeline_item_add_flag(item_id: str, color: str) -> str:
    """Add a flag to a timeline item.

    Args:
        item_id: TimelineItem ID
        color: Flag color
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.AddFlag(color)
        if result:
            return _ok(f"Flag '{color}' added")
        return _err("Failed to add flag")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_flag_list(item_id: str) -> str:
    """Get all flag colors on a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetFlagList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_clear_flags(item_id: str, color: str) -> str:
    """Clear flags of a color on a timeline item. Use 'All' to clear all.

    Args:
        item_id: TimelineItem ID
        color: Color to clear, or 'All'
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.ClearFlags(color)
        if result:
            return _ok(f"Flags '{color}' cleared")
        return _err("Failed to clear flags")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_clip_color(item_id: str) -> str:
    """Get the clip color of a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetClipColor())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_set_clip_color(item_id: str, color_name: str) -> str:
    """Set the clip color of a timeline item.

    Args:
        item_id: TimelineItem ID
        color_name: Color name
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.SetClipColor(color_name)
        if result:
            return _ok(f"Clip color set to '{color_name}'")
        return _err("Failed to set clip color")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_clear_clip_color(item_id: str) -> str:
    """Clear the clip color of a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.ClearClipColor()
        if result:
            return _ok("Clip color cleared")
        return _err("Failed to clear clip color")
    except Exception as e:
        return _err(str(e))


# ── Fusion Compositions ──────────────────────────────────────────

@mcp.tool()
def timeline_item_get_fusion_comp_count(item_id: str) -> str:
    """Get the number of Fusion compositions on a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetFusionCompCount())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_fusion_comp_name_list(item_id: str) -> str:
    """Get names of all Fusion compositions on a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetFusionCompNameList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_add_fusion_comp(item_id: str) -> str:
    """Add a new Fusion composition to a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        comp = ti.AddFusionComp()
        if comp is None:
            return _err("Failed to add Fusion composition")
        return _ok("Fusion composition added")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_import_fusion_comp(item_id: str, path: str) -> str:
    """Import a Fusion composition from a file.

    Args:
        item_id: TimelineItem ID
        path: Path to the Fusion composition file
    """
    try:
        _, ti = _get_ti(item_id)
        comp = ti.ImportFusionComp(path)
        if comp is None:
            return _err(f"Failed to import Fusion composition from '{path}'")
        return _ok("Fusion composition imported")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_export_fusion_comp(item_id: str, path: str, comp_index: int) -> str:
    """Export a Fusion composition to a file.

    Args:
        item_id: TimelineItem ID
        path: Output file path
        comp_index: Composition index (1-based)
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.ExportFusionComp(path, comp_index)
        if result:
            return _ok(f"Fusion composition exported to '{path}'")
        return _err("Failed to export composition")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_delete_fusion_comp_by_name(item_id: str, comp_name: str) -> str:
    """Delete a Fusion composition by name.

    Args:
        item_id: TimelineItem ID
        comp_name: Name of the composition to delete
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.DeleteFusionCompByName(comp_name)
        if result:
            return _ok(f"Fusion composition '{comp_name}' deleted")
        return _err(f"Failed to delete composition '{comp_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_load_fusion_comp_by_name(item_id: str, comp_name: str) -> str:
    """Load a Fusion composition as the active composition.

    Args:
        item_id: TimelineItem ID
        comp_name: Name of the composition to load
    """
    try:
        _, ti = _get_ti(item_id)
        comp = ti.LoadFusionCompByName(comp_name)
        if comp is None:
            return _err(f"Failed to load composition '{comp_name}'")
        return _ok(f"Fusion composition '{comp_name}' loaded")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_rename_fusion_comp_by_name(item_id: str, old_name: str, new_name: str) -> str:
    """Rename a Fusion composition.

    Args:
        item_id: TimelineItem ID
        old_name: Current name
        new_name: New name
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.RenameFusionCompByName(old_name, new_name)
        if result:
            return _ok(f"Composition renamed from '{old_name}' to '{new_name}'")
        return _err("Failed to rename composition")
    except Exception as e:
        return _err(str(e))


# ── Color Versions ────────────────────────────────────────────────

@mcp.tool()
def timeline_item_add_version(item_id: str, version_name: str, version_type: int) -> str:
    """Add a new color version.

    Args:
        item_id: TimelineItem ID
        version_name: Name for the new version
        version_type: 0=local, 1=remote
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.AddVersion(version_name, version_type)
        if result:
            return _ok(f"Version '{version_name}' added")
        return _err("Failed to add version")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_current_version(item_id: str) -> str:
    """Get the current color version. Returns dict with 'versionName' and 'versionType' (0=local, 1=remote).

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetCurrentVersion())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_delete_version_by_name(item_id: str, version_name: str, version_type: int) -> str:
    """Delete a color version by name.

    Args:
        item_id: TimelineItem ID
        version_name: Version name
        version_type: 0=local, 1=remote
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.DeleteVersionByName(version_name, version_type)
        if result:
            return _ok(f"Version '{version_name}' deleted")
        return _err("Failed to delete version")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_load_version_by_name(item_id: str, version_name: str, version_type: int) -> str:
    """Load a color version as the active version.

    Args:
        item_id: TimelineItem ID
        version_name: Version name
        version_type: 0=local, 1=remote
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.LoadVersionByName(version_name, version_type)
        if result:
            return _ok(f"Version '{version_name}' loaded")
        return _err("Failed to load version")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_rename_version_by_name(item_id: str, old_name: str, new_name: str, version_type: int) -> str:
    """Rename a color version.

    Args:
        item_id: TimelineItem ID
        old_name: Current version name
        new_name: New version name
        version_type: 0=local, 1=remote
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.RenameVersionByName(old_name, new_name, version_type)
        if result:
            return _ok(f"Version renamed from '{old_name}' to '{new_name}'")
        return _err("Failed to rename version")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_version_name_list(item_id: str, version_type: int) -> str:
    """Get all color version names.

    Args:
        item_id: TimelineItem ID
        version_type: 0=local, 1=remote
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetVersionNameList(version_type))
    except Exception as e:
        return _err(str(e))


# ── CDL ───────────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_set_cdl(
    item_id: str, node_index: str, slope: str, offset: str, power: str, saturation: str,
) -> str:
    """Set CDL values on a node.

    Args:
        item_id: TimelineItem ID
        node_index: Node index (1-based, as string)
        slope: RGB slope as 'R G B' (e.g., '0.5 0.4 0.2')
        offset: RGB offset as 'R G B'
        power: RGB power as 'R G B'
        saturation: Saturation value (e.g., '0.65')
    """
    try:
        _, ti = _get_ti(item_id)
        cdl = {"NodeIndex": node_index, "Slope": slope, "Offset": offset, "Power": power, "Saturation": saturation}
        result = ti.SetCDL(cdl)
        if result:
            return _ok("CDL values set")
        return _err("Failed to set CDL values")
    except Exception as e:
        return _err(str(e))


# ── Takes ─────────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_add_take(item_id: str, media_pool_item_id: str, start_frame: int | None = None, end_frame: int | None = None) -> str:
    """Add a take to a timeline item.

    Args:
        item_id: TimelineItem ID
        media_pool_item_id: MediaPoolItem ID for the take
        start_frame: Optional start frame
        end_frame: Optional end frame
    """
    try:
        conn, ti = _get_ti(item_id)
        mpi = conn.get(media_pool_item_id, "MediaPoolItem")
        if start_frame is not None and end_frame is not None:
            result = ti.AddTake(mpi, start_frame, end_frame)
        else:
            result = ti.AddTake(mpi)
        if result:
            return _ok("Take added")
        return _err("Failed to add take")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_selected_take_index(item_id: str) -> str:
    """Get the index of the currently selected take, or 0 if not a take selector.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetSelectedTakeIndex())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_takes_count(item_id: str) -> str:
    """Get the number of takes, or 0 if not a take selector.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetTakesCount())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_take_by_index(item_id: str, idx: int) -> str:
    """Get take info by index. Returns dict with startFrame, endFrame, mediaPoolItem.

    Args:
        item_id: TimelineItem ID
        idx: Take index (1-based)
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetTakeByIndex(idx))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_delete_take_by_index(item_id: str, idx: int) -> str:
    """Delete a take by index.

    Args:
        item_id: TimelineItem ID
        idx: Take index (1-based)
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.DeleteTakeByIndex(idx)
        if result:
            return _ok(f"Take {idx} deleted")
        return _err("Failed to delete take")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_select_take_by_index(item_id: str, idx: int) -> str:
    """Select a take by index.

    Args:
        item_id: TimelineItem ID
        idx: Take index (1-based)
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.SelectTakeByIndex(idx)
        if result:
            return _ok(f"Take {idx} selected")
        return _err("Failed to select take")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_finalize_take(item_id: str) -> str:
    """Finalize take selection.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.FinalizeTake()
        if result:
            return _ok("Take finalized")
        return _err("Failed to finalize take")
    except Exception as e:
        return _err(str(e))


# ── Grades ────────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_copy_grades(item_id: str, target_item_ids: list[str]) -> str:
    """Copy the current grade to other timeline items.

    Args:
        item_id: Source TimelineItem ID
        target_item_ids: List of target TimelineItem IDs
    """
    try:
        conn, ti = _get_ti(item_id)
        targets = [conn.get(tid, "TimelineItem") for tid in target_item_ids]
        result = ti.CopyGrades(targets)
        if result:
            return _ok(f"Grades copied to {len(targets)} item(s)")
        return _err("Failed to copy grades")
    except Exception as e:
        return _err(str(e))


# ── Enable/Disable & Sidecar ─────────────────────────────────────

@mcp.tool()
def timeline_item_set_clip_enabled(item_id: str, enabled: bool) -> str:
    """Enable or disable a clip.

    Args:
        item_id: TimelineItem ID
        enabled: True to enable, False to disable
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.SetClipEnabled(enabled)
        if result:
            return _ok(f"Clip {'enabled' if enabled else 'disabled'}")
        return _err("Failed to set clip enabled state")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_clip_enabled(item_id: str) -> str:
    """Check if a clip is enabled.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetClipEnabled())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_update_sidecar(item_id: str) -> str:
    """Updates sidecar file for BRAW clips or RMD file for R3D clips.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.UpdateSidecar()
        if result:
            return _ok("Sidecar updated")
        return _err("Failed to update sidecar")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_unique_id(item_id: str) -> str:
    """Get the unique ID of a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetUniqueId())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_load_burn_in_preset(item_id: str, preset_name: str) -> str:
    """Load a burn-in preset for a clip.

    Args:
        item_id: TimelineItem ID
        preset_name: Name of the burn-in preset
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.LoadBurnInPreset(preset_name)
        if result:
            return _ok(f"Burn-in preset '{preset_name}' loaded")
        return _err(f"Failed to load burn-in preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


# ── Magic Mask, Stabilize, Smart Reframe ──────────────────────────

@mcp.tool()
def timeline_item_create_magic_mask(item_id: str, mode: str) -> str:
    """Create a magic mask on a clip.

    Args:
        item_id: TimelineItem ID
        mode: 'F' (forward), 'B' (backward), or 'BI' (bidirectional)
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.CreateMagicMask(mode)
        if result:
            return _ok("Magic mask created")
        return _err("Failed to create magic mask")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_regenerate_magic_mask(item_id: str) -> str:
    """Regenerate magic mask on a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.RegenerateMagicMask()
        if result:
            return _ok("Magic mask regenerated")
        return _err("Failed to regenerate magic mask")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_stabilize(item_id: str) -> str:
    """Stabilize a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.Stabilize()
        if result:
            return _ok("Clip stabilized")
        return _err("Failed to stabilize clip")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_smart_reframe(item_id: str) -> str:
    """Perform Smart Reframe on a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.SmartReframe()
        if result:
            return _ok("Smart Reframe applied")
        return _err("Failed to apply Smart Reframe")
    except Exception as e:
        return _err(str(e))


# ── Node Graph & Color Group ─────────────────────────────────────

@mcp.tool()
def timeline_item_get_node_graph(item_id: str, layer_idx: int | None = None) -> str:
    """Get the clip's node graph.

    Args:
        item_id: TimelineItem ID
        layer_idx: Layer index (1-based, optional). Default: first layer.
    """
    try:
        conn, ti = _get_ti(item_id)
        graph = ti.GetNodeGraph(layer_idx) if layer_idx is not None else ti.GetNodeGraph()
        if graph is None:
            return _err("Failed to get node graph")
        gid = conn.register(graph, "Graph", composite_key=f"graph:item:{item_id}:{layer_idx or 1}")
        return _ok({"id": gid, "type": "Graph"})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_color_group(item_id: str) -> str:
    """Get the color group of a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        conn, ti = _get_ti(item_id)
        cg = ti.GetColorGroup()
        if cg is None:
            return _ok(None)
        name = cg.GetName()
        gid = conn.register(cg, "ColorGroup", composite_key=f"colorgroup:{name}")
        return _ok({"id": gid, "type": "ColorGroup", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_assign_to_color_group(item_id: str, color_group_id: str) -> str:
    """Assign a timeline item to a color group.

    Args:
        item_id: TimelineItem ID
        color_group_id: ColorGroup ID
    """
    try:
        conn, ti = _get_ti(item_id)
        cg = conn.get(color_group_id, "ColorGroup")
        result = ti.AssignToColorGroup(cg)
        if result:
            return _ok("Assigned to color group")
        return _err("Failed to assign to color group")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_remove_from_color_group(item_id: str) -> str:
    """Remove a timeline item from its color group.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.RemoveFromColorGroup()
        if result:
            return _ok("Removed from color group")
        return _err("Failed to remove from color group")
    except Exception as e:
        return _err(str(e))


# ── LUT Export ────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_export_lut(item_id: str, export_type: str, path: str) -> str:
    """Export a LUT from a timeline item.

    Args:
        item_id: TimelineItem ID
        export_type: One of: 17PT_CUBE, 33PT_CUBE, 65PT_CUBE, PANASONIC_VLUT
        path: Output file path (appropriate extension will be appended if missing)
    """
    try:
        conn, ti = _get_ti(item_id)
        etype = resolve_enum(conn.resolve, EXPORT_LUT_TYPES, export_type)
        result = ti.ExportLUT(etype, path)
        if result:
            return _ok(f"LUT exported to '{path}'")
        return _err("Failed to export LUT")
    except Exception as e:
        return _err(str(e))


# ── Linked Items & Track Info ─────────────────────────────────────

@mcp.tool()
def timeline_item_get_linked_items(item_id: str) -> str:
    """Get all items linked to this timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        conn, ti = _get_ti(item_id)
        items = ti.GetLinkedItems()
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
def timeline_item_get_track_type_and_index(item_id: str) -> str:
    """Get the track type and index for a timeline item. Returns [trackType, trackIndex].

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetTrackTypeAndIndex())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_source_audio_channel_mapping(item_id: str) -> str:
    """Get the audio channel mapping for a timeline item as JSON.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        mapping_str = ti.GetSourceAudioChannelMapping()
        try:
            return _ok(json.loads(mapping_str))
        except (json.JSONDecodeError, TypeError):
            return _ok(mapping_str)
    except Exception as e:
        return _err(str(e))


# ── Cache ─────────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_get_is_color_output_cache_enabled(item_id: str) -> str:
    """Check if color output cache is enabled for a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetIsColorOutputCacheEnabled())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_is_fusion_output_cache_enabled(item_id: str) -> str:
    """Check if Fusion output cache is enabled (or auto) for a clip.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetIsFusionOutputCacheEnabled())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_set_color_output_cache(item_id: str, enabled: bool) -> str:
    """Set color output cache enabled or disabled.

    Args:
        item_id: TimelineItem ID
        enabled: True to enable, False to disable
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.SetColorOutputCache(enabled)
        if result:
            return _ok(f"Color output cache {'enabled' if enabled else 'disabled'}")
        return _err("Failed to set color output cache")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_set_fusion_output_cache(item_id: str, cache_value: str) -> str:
    """Set Fusion output cache to auto, enabled, or disabled.

    Args:
        item_id: TimelineItem ID
        cache_value: 'auto', 'enabled', or 'disabled'
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.SetFusionOutputCache(cache_value)
        if result:
            return _ok(f"Fusion output cache set to '{cache_value}'")
        return _err("Failed to set Fusion output cache")
    except Exception as e:
        return _err(str(e))


# ── Voice Isolation ───────────────────────────────────────────────

@mcp.tool()
def timeline_item_get_voice_isolation_state(item_id: str) -> str:
    """Get voice isolation state for a timeline item. Requires Resolve 20.1+.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetVoiceIsolationState())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_set_voice_isolation_state(item_id: str, is_enabled: bool, amount: int) -> str:
    """Set voice isolation state for a timeline item. Requires Resolve 20.1+.

    Args:
        item_id: TimelineItem ID
        is_enabled: Enable/disable voice isolation
        amount: Isolation amount (0-100)
    """
    try:
        _, ti = _get_ti(item_id)
        state = {"isEnabled": is_enabled, "amount": amount}
        result = ti.SetVoiceIsolationState(state)
        if result:
            return _ok("Voice isolation state set")
        return _err("Failed to set voice isolation state")
    except Exception as e:
        return _err(str(e))


# ── Stereo ────────────────────────────────────────────────────────

@mcp.tool()
def timeline_item_get_stereo_convergence_values(item_id: str) -> str:
    """Get stereo convergence keyframe values. Returns dict of {offset: value}.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetStereoConvergenceValues())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_stereo_left_floating_window_params(item_id: str) -> str:
    """Get left eye stereo floating window params. Returns dict of {offset: {left, right, top, bottom}}.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetStereoLeftFloatingWindowParams())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_stereo_right_floating_window_params(item_id: str) -> str:
    """Get right eye stereo floating window params. Returns dict of {offset: {left, right, top, bottom}}.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        return _ok(ti.GetStereoRightFloatingWindowParams())
    except Exception as e:
        return _err(str(e))


# ── Media Pool Item & Reset ───────────────────────────────────────

@mcp.tool()
def timeline_item_get_media_pool_item(item_id: str) -> str:
    """Get the MediaPoolItem corresponding to a timeline item.

    Args:
        item_id: TimelineItem ID
    """
    try:
        conn, ti = _get_ti(item_id)
        mpi = ti.GetMediaPoolItem()
        if mpi is None:
            return _err("No MediaPoolItem for this timeline item")
        mid = conn.register(mpi, "MediaPoolItem")
        return _ok({"id": mid, "type": "MediaPoolItem", "name": mpi.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_reset_all_node_colors(item_id: str) -> str:
    """Reset node color for all nodes in the active version. Requires Resolve 20.2+.

    Args:
        item_id: TimelineItem ID
    """
    try:
        _, ti = _get_ti(item_id)
        result = ti.ResetAllNodeColors()
        if result:
            return _ok("All node colors reset")
        return _err("Failed to reset node colors")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_fusion_comp_by_index(item_id: str, comp_index: int) -> str:
    """Get a Fusion composition by index.

    Args:
        item_id: TimelineItem ID
        comp_index: Composition index (1-based)
    """
    try:
        _, ti = _get_ti(item_id)
        comp = ti.GetFusionCompByIndex(comp_index)
        if comp is None:
            return _err(f"No Fusion composition at index {comp_index}")
        return _ok(f"Fusion composition at index {comp_index} retrieved")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_item_get_fusion_comp_by_name(item_id: str, comp_name: str) -> str:
    """Get a Fusion composition by name.

    Args:
        item_id: TimelineItem ID
        comp_name: Composition name
    """
    try:
        _, ti = _get_ti(item_id)
        comp = ti.GetFusionCompByName(comp_name)
        if comp is None:
            return _err(f"No Fusion composition named '{comp_name}'")
        return _ok(f"Fusion composition '{comp_name}' retrieved")
    except Exception as e:
        return _err(str(e))
