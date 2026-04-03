"""Tools for the MediaPoolItem object.

Covers: name, metadata, markers, flags, clip color, properties, proxy,
replacement, transcription, audio mapping, marks.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_mpi(clip_id: str):
    conn = get_connection()
    return conn, conn.get(clip_id, "MediaPoolItem")


# ── Name ──────────────────────────────────────────────────────────

@mcp.tool()
def media_pool_item_get_name(clip_id: str) -> str:
    """Get the name of a media pool clip.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetName())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_set_name(clip_id: str, name: str) -> str:
    """Set the name of a media pool clip. Requires Resolve 20.2+.

    Args:
        clip_id: MediaPoolItem ID
        name: New name for the clip
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.SetName(name)
        if result:
            return _ok(f"Clip renamed to '{name}'")
        return _err("Failed to rename clip")
    except Exception as e:
        return _err(str(e))


# ── Metadata ──────────────────────────────────────────────────────

@mcp.tool()
def media_pool_item_get_metadata(clip_id: str, metadata_type: str | None = None) -> str:
    """Get metadata for a media pool clip.

    Args:
        clip_id: MediaPoolItem ID
        metadata_type: Specific metadata key. If None, returns all metadata as a dict.
    """
    try:
        _, mpi = _get_mpi(clip_id)
        if metadata_type:
            return _ok(mpi.GetMetadata(metadata_type))
        return _ok(mpi.GetMetadata())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_set_metadata(clip_id: str, metadata: dict | None = None, key: str | None = None, value: str | None = None) -> str:
    """Set metadata on a media pool clip.

    Use EITHER metadata dict OR key+value pair.

    Args:
        clip_id: MediaPoolItem ID
        metadata: Dict of {key: value} pairs to set
        key: Single metadata key
        value: Value for the key
    """
    try:
        _, mpi = _get_mpi(clip_id)
        if metadata:
            result = mpi.SetMetadata(metadata)
        elif key and value is not None:
            result = mpi.SetMetadata(key, value)
        else:
            return _err("Provide either a metadata dict or key+value pair")
        if result:
            return _ok("Metadata updated")
        return _err("Failed to set metadata")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_third_party_metadata(clip_id: str, metadata_type: str | None = None) -> str:
    """Get third-party metadata for a clip.

    Args:
        clip_id: MediaPoolItem ID
        metadata_type: Specific key. If None, returns all third-party metadata.
    """
    try:
        _, mpi = _get_mpi(clip_id)
        if metadata_type:
            return _ok(mpi.GetThirdPartyMetadata(metadata_type))
        return _ok(mpi.GetThirdPartyMetadata())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_set_third_party_metadata(clip_id: str, metadata: dict | None = None, key: str | None = None, value: str | None = None) -> str:
    """Set third-party metadata on a clip.

    Args:
        clip_id: MediaPoolItem ID
        metadata: Dict of {key: value} pairs
        key: Single metadata key
        value: Value for the key
    """
    try:
        _, mpi = _get_mpi(clip_id)
        if metadata:
            result = mpi.SetThirdPartyMetadata(metadata)
        elif key and value is not None:
            result = mpi.SetThirdPartyMetadata(key, value)
        else:
            return _err("Provide either a metadata dict or key+value pair")
        if result:
            return _ok("Third-party metadata updated")
        return _err("Failed to set third-party metadata")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_media_id(clip_id: str) -> str:
    """Get the unique media ID for a clip.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetMediaId())
    except Exception as e:
        return _err(str(e))


# ── Markers ───────────────────────────────────────────────────────

@mcp.tool()
def media_pool_item_add_marker(clip_id: str, frame_id: float, color: str, name: str, note: str, duration: float, custom_data: str | None = None) -> str:
    """Add a marker to a media pool clip.

    Args:
        clip_id: MediaPoolItem ID
        frame_id: Frame position for the marker
        color: Marker color (e.g., 'Red', 'Green', 'Blue', 'Cyan', 'Yellow', 'Pink', 'Purple', 'Fuchsia', 'Rose', 'Lavender', 'Sky', 'Mint', 'Lemon', 'Sand', 'Cocoa', 'Cream')
        name: Marker name
        note: Marker note
        duration: Marker duration in frames
        custom_data: Optional custom data string
    """
    try:
        _, mpi = _get_mpi(clip_id)
        if custom_data is not None:
            result = mpi.AddMarker(frame_id, color, name, note, duration, custom_data)
        else:
            result = mpi.AddMarker(frame_id, color, name, note, duration)
        if result:
            return _ok(f"Marker added at frame {frame_id}")
        return _err(f"Failed to add marker at frame {frame_id}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_markers(clip_id: str) -> str:
    """Get all markers on a media pool clip.

    Args:
        clip_id: MediaPoolItem ID

    Returns dict of {frameId: {color, duration, note, name, customData}}.
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetMarkers())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_marker_by_custom_data(clip_id: str, custom_data: str) -> str:
    """Find the first marker with matching custom data.

    Args:
        clip_id: MediaPoolItem ID
        custom_data: Custom data string to search for
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetMarkerByCustomData(custom_data))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_update_marker_custom_data(clip_id: str, frame_id: float, custom_data: str) -> str:
    """Update the custom data for a marker at a specific frame.

    Args:
        clip_id: MediaPoolItem ID
        frame_id: Frame position of the marker
        custom_data: New custom data string
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.UpdateMarkerCustomData(frame_id, custom_data)
        if result:
            return _ok(f"Marker custom data updated at frame {frame_id}")
        return _err(f"Failed to update marker at frame {frame_id}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_marker_custom_data(clip_id: str, frame_id: float) -> str:
    """Get the custom data string for a marker at a specific frame.

    Args:
        clip_id: MediaPoolItem ID
        frame_id: Frame position of the marker
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetMarkerCustomData(frame_id))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_delete_markers_by_color(clip_id: str, color: str) -> str:
    """Delete all markers of a specific color. Use 'All' to delete all markers.

    Args:
        clip_id: MediaPoolItem ID
        color: Marker color to delete, or 'All'
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.DeleteMarkersByColor(color)
        if result:
            return _ok(f"Markers of color '{color}' deleted")
        return _err(f"Failed to delete markers of color '{color}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_delete_marker_at_frame(clip_id: str, frame_num: float) -> str:
    """Delete the marker at a specific frame.

    Args:
        clip_id: MediaPoolItem ID
        frame_num: Frame number of the marker to delete
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.DeleteMarkerAtFrame(frame_num)
        if result:
            return _ok(f"Marker deleted at frame {frame_num}")
        return _err(f"No marker found at frame {frame_num}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_delete_marker_by_custom_data(clip_id: str, custom_data: str) -> str:
    """Delete the first marker with matching custom data.

    Args:
        clip_id: MediaPoolItem ID
        custom_data: Custom data string to match
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.DeleteMarkerByCustomData(custom_data)
        if result:
            return _ok("Marker deleted")
        return _err("No marker found with that custom data")
    except Exception as e:
        return _err(str(e))


# ── Flags & Color ─────────────────────────────────────────────────

@mcp.tool()
def media_pool_item_add_flag(clip_id: str, color: str) -> str:
    """Add a flag to a clip.

    Args:
        clip_id: MediaPoolItem ID
        color: Flag color
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.AddFlag(color)
        if result:
            return _ok(f"Flag '{color}' added")
        return _err(f"Failed to add flag '{color}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_flag_list(clip_id: str) -> str:
    """Get all flag colors assigned to a clip.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetFlagList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_clear_flags(clip_id: str, color: str) -> str:
    """Clear flags of a specific color. Use 'All' to clear all flags.

    Args:
        clip_id: MediaPoolItem ID
        color: Flag color to clear, or 'All'
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.ClearFlags(color)
        if result:
            return _ok(f"Flags '{color}' cleared")
        return _err(f"Failed to clear flags '{color}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_clip_color(clip_id: str) -> str:
    """Get the clip color.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetClipColor())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_set_clip_color(clip_id: str, color_name: str) -> str:
    """Set the clip color.

    Args:
        clip_id: MediaPoolItem ID
        color_name: Color name
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.SetClipColor(color_name)
        if result:
            return _ok(f"Clip color set to '{color_name}'")
        return _err(f"Failed to set clip color to '{color_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_clear_clip_color(clip_id: str) -> str:
    """Clear the clip color.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.ClearClipColor()
        if result:
            return _ok("Clip color cleared")
        return _err("Failed to clear clip color")
    except Exception as e:
        return _err(str(e))


# ── Clip Properties ───────────────────────────────────────────────

@mcp.tool()
def media_pool_item_get_clip_property(clip_id: str, property_name: str | None = None) -> str:
    """Get clip properties.

    Args:
        clip_id: MediaPoolItem ID
        property_name: Specific property key. If None, returns all properties as a dict.
    """
    try:
        _, mpi = _get_mpi(clip_id)
        if property_name:
            return _ok(mpi.GetClipProperty(property_name))
        return _ok(mpi.GetClipProperty())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_set_clip_property(
    clip_id: str,
    property_name: str,
    property_value: str,
    sharpness: float | None = None,
    noise_reduction: float | None = None,
) -> str:
    """Set a clip property.

    Args:
        clip_id: MediaPoolItem ID
        property_name: Property key name
        property_value: New value
        sharpness: For 'Super Scale' 2x Enhanced only (0.0-1.0)
        noise_reduction: For 'Super Scale' 2x Enhanced only (0.0-1.0)
    """
    try:
        _, mpi = _get_mpi(clip_id)
        if property_name == "Super Scale" and sharpness is not None and noise_reduction is not None:
            result = mpi.SetClipProperty(property_name, property_value, sharpness, noise_reduction)
        else:
            result = mpi.SetClipProperty(property_name, property_value)
        if result:
            return _ok(f"Property '{property_name}' set")
        return _err(f"Failed to set property '{property_name}'")
    except Exception as e:
        return _err(str(e))


# ── Proxy & Replace ──────────────────────────────────────────────

@mcp.tool()
def media_pool_item_link_proxy_media(clip_id: str, proxy_media_file_path: str) -> str:
    """Link proxy media to a clip.

    Args:
        clip_id: MediaPoolItem ID
        proxy_media_file_path: Absolute path to proxy media file
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.LinkProxyMedia(proxy_media_file_path)
        if result:
            return _ok("Proxy media linked")
        return _err("Failed to link proxy media")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_link_full_resolution_media(clip_id: str, full_res_media_path: str) -> str:
    """Link full resolution media files to a proxy clip. Requires Resolve 20.0+.

    Args:
        clip_id: MediaPoolItem ID
        full_res_media_path: Path to full resolution media
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.LinkFullResolutionMedia(full_res_media_path)
        if result:
            return _ok("Full resolution media linked")
        return _err("Failed to link full resolution media")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_unlink_proxy_media(clip_id: str) -> str:
    """Unlink proxy media from a clip.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.UnlinkProxyMedia()
        if result:
            return _ok("Proxy media unlinked")
        return _err("Failed to unlink proxy media")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_replace_clip(clip_id: str, file_path: str) -> str:
    """Replace the underlying media of a clip.

    Args:
        clip_id: MediaPoolItem ID
        file_path: Absolute path to the replacement media
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.ReplaceClip(file_path)
        if result:
            return _ok("Clip replaced")
        return _err("Failed to replace clip")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_replace_clip_preserve_sub_clip(clip_id: str, file_path: str) -> str:
    """Replace clip media while preserving sub-clip extents. Requires Resolve 20.0+.

    Args:
        clip_id: MediaPoolItem ID
        file_path: Absolute path to the replacement media
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.ReplaceClipPreserveSubClip(file_path)
        if result:
            return _ok("Clip replaced (sub-clip extents preserved)")
        return _err("Failed to replace clip")
    except Exception as e:
        return _err(str(e))


# ── Transcription ─────────────────────────────────────────────────

@mcp.tool()
def media_pool_item_transcribe_audio(clip_id: str) -> str:
    """Transcribe the audio of a clip.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.TranscribeAudio()
        if result:
            return _ok("Audio transcription started")
        return _err("Failed to start transcription")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_clear_transcription(clip_id: str) -> str:
    """Clear audio transcription for a clip.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.ClearTranscription()
        if result:
            return _ok("Transcription cleared")
        return _err("Failed to clear transcription")
    except Exception as e:
        return _err(str(e))


# ── Audio Mapping ─────────────────────────────────────────────────

@mcp.tool()
def media_pool_item_get_audio_mapping(clip_id: str) -> str:
    """Get the audio mapping information for a clip as JSON.

    Returns embedded channel count, linked audio info, and track mapping.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        mapping_str = mpi.GetAudioMapping()
        try:
            mapping = json.loads(mapping_str)
            return _ok(mapping)
        except (json.JSONDecodeError, TypeError):
            return _ok(mapping_str)
    except Exception as e:
        return _err(str(e))


# ── Marks ─────────────────────────────────────────────────────────

@mcp.tool()
def media_pool_item_get_mark_in_out(clip_id: str) -> str:
    """Get mark in/out points for a clip.

    Args:
        clip_id: MediaPoolItem ID

    Returns dict like {'video': {'in': 0, 'out': 134}, 'audio': {'in': 0, 'out': 134}}.
    Keys are omitted if not set.
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetMarkInOut())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_set_mark_in_out(clip_id: str, mark_in: int, mark_out: int, mark_type: str = "all") -> str:
    """Set mark in/out points for a clip.

    Args:
        clip_id: MediaPoolItem ID
        mark_in: In point frame number
        mark_out: Out point frame number
        mark_type: 'video', 'audio', or 'all' (default 'all')
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.SetMarkInOut(mark_in, mark_out, mark_type)
        if result:
            return _ok(f"Mark in/out set ({mark_type}): {mark_in}-{mark_out}")
        return _err("Failed to set mark in/out")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_clear_mark_in_out(clip_id: str, mark_type: str = "all") -> str:
    """Clear mark in/out points for a clip.

    Args:
        clip_id: MediaPoolItem ID
        mark_type: 'video', 'audio', or 'all' (default 'all')
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.ClearMarkInOut(mark_type)
        if result:
            return _ok(f"Mark in/out cleared ({mark_type})")
        return _err("Failed to clear mark in/out")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_get_unique_id(clip_id: str) -> str:
    """Get the unique ID of a MediaPoolItem.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        return _ok(mpi.GetUniqueId())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_item_monitor_growing_file(clip_id: str) -> str:
    """Monitor a growing file until it stops growing. Requires Resolve 20.0+.

    Args:
        clip_id: MediaPoolItem ID
    """
    try:
        _, mpi = _get_mpi(clip_id)
        result = mpi.MonitorGrowingFile()
        if result:
            return _ok("Monitoring growing file")
        return _err("Failed to monitor growing file")
    except Exception as e:
        return _err(str(e))
