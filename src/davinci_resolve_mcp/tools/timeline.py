"""Tools for the Timeline object.

Covers: tracks, markers, clips, timecodes, generators, titles, stills,
export, import, settings, subtitles, scene cuts, stereo, node graph,
Dolby Vision, voice isolation, marks, Fairlight.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.models import AAFImportOptions, AutoCaptionSettings
from davinci_resolve_mcp.constants import (
    EXPORT_TYPES,
    EXPORT_SUBTYPES,
    SUBTITLE_SETTING_KEYS,
    AUTO_CAPTION_LANGUAGES,
    AUTO_CAPTION_PRESETS,
    AUTO_CAPTION_LINE_BREAKS,
    DOLBY_VISION_ANALYSIS_TYPES,
    resolve_enum,
)

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_tl(timeline_id: str):
    conn = get_connection()
    return conn, conn.get(timeline_id, "Timeline")


def _auto_caption_to_resolve_dict(conn, settings: AutoCaptionSettings) -> dict:
    result = {}
    r = conn.resolve
    if settings.language is not None:
        key = getattr(r, SUBTITLE_SETTING_KEYS["LANGUAGE"])
        result[key] = resolve_enum(r, AUTO_CAPTION_LANGUAGES, settings.language)
    if settings.caption_preset is not None:
        key = getattr(r, SUBTITLE_SETTING_KEYS["CAPTION_PRESET"])
        result[key] = resolve_enum(r, AUTO_CAPTION_PRESETS, settings.caption_preset)
    if settings.chars_per_line is not None:
        key = getattr(r, SUBTITLE_SETTING_KEYS["CHARS_PER_LINE"])
        result[key] = settings.chars_per_line
    if settings.line_break is not None:
        key = getattr(r, SUBTITLE_SETTING_KEYS["LINE_BREAK"])
        result[key] = resolve_enum(r, AUTO_CAPTION_LINE_BREAKS, settings.line_break)
    if settings.gap is not None:
        key = getattr(r, SUBTITLE_SETTING_KEYS["GAP"])
        result[key] = settings.gap
    return result


# ── Basic Info ────────────────────────────────────────────────────

@mcp.tool()
def timeline_get_name(timeline_id: str) -> str:
    """Get the timeline name.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetName())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_name(timeline_id: str, name: str) -> str:
    """Rename a timeline.

    Args:
        timeline_id: Timeline ID
        name: New name (must be unique)
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetName(name)
        if result:
            return _ok(f"Timeline renamed to '{name}'")
        return _err(f"Failed to rename timeline. '{name}' may already exist.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_start_frame(timeline_id: str) -> str:
    """Get the start frame number of a timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetStartFrame())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_end_frame(timeline_id: str) -> str:
    """Get the end frame number of a timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetEndFrame())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_start_timecode(timeline_id: str) -> str:
    """Get the start timecode of a timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetStartTimecode())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_start_timecode(timeline_id: str, timecode: str) -> str:
    """Set the start timecode of a timeline.

    Args:
        timeline_id: Timeline ID
        timecode: Timecode string (e.g., '01:00:00:00')
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetStartTimecode(timecode)
        if result:
            return _ok(f"Start timecode set to '{timecode}'")
        return _err(f"Failed to set start timecode to '{timecode}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_unique_id(timeline_id: str) -> str:
    """Get the unique ID of a timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetUniqueId())
    except Exception as e:
        return _err(str(e))


# ── Track Management ──────────────────────────────────────────────

@mcp.tool()
def timeline_get_track_count(timeline_id: str, track_type: str) -> str:
    """Get the number of tracks of a given type.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetTrackCount(track_type))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_add_track(
    timeline_id: str,
    track_type: str,
    sub_track_type: str | None = None,
    index: int | None = None,
) -> str:
    """Add a track to the timeline.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        sub_track_type: Audio format (mono, stereo, 5.1, 7.1, adaptive1-36, etc.). Defaults to 'mono' for audio.
        index: Insert position (1-based). If omitted, appends at end.
    """
    try:
        _, tl = _get_tl(timeline_id)
        if index is not None or (sub_track_type and track_type == "audio"):
            options = {}
            if sub_track_type:
                options["audioType"] = sub_track_type
            if index is not None:
                options["index"] = index
            result = tl.AddTrack(track_type, options)
        elif sub_track_type:
            result = tl.AddTrack(track_type, sub_track_type)
        else:
            result = tl.AddTrack(track_type)
        if result:
            return _ok(f"{track_type} track added")
        return _err(f"Failed to add {track_type} track")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_delete_track(timeline_id: str, track_type: str, track_index: int) -> str:
    """Delete a track from the timeline.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.DeleteTrack(track_type, track_index)
        if result:
            return _ok(f"{track_type} track {track_index} deleted")
        return _err(f"Failed to delete {track_type} track {track_index}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_track_sub_type(timeline_id: str, track_type: str, track_index: int) -> str:
    """Get the audio format of a track (e.g., mono, stereo, 5.1, 7.1). Returns blank for non-audio tracks.

    Args:
        timeline_id: Timeline ID
        track_type: 'audio' (returns blank for video/subtitle)
        track_index: Track index (1-based)
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetTrackSubType(track_type, track_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_track_enable(timeline_id: str, track_type: str, track_index: int, enabled: bool) -> str:
    """Enable or disable a track.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)
        enabled: True to enable, False to disable
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetTrackEnable(track_type, track_index, enabled)
        if result:
            return _ok(f"{track_type} track {track_index} {'enabled' if enabled else 'disabled'}")
        return _err("Failed to set track enable state")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_is_track_enabled(timeline_id: str, track_type: str, track_index: int) -> str:
    """Check if a track is enabled.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetIsTrackEnabled(track_type, track_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_track_lock(timeline_id: str, track_type: str, track_index: int, locked: bool) -> str:
    """Lock or unlock a track.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)
        locked: True to lock, False to unlock
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetTrackLock(track_type, track_index, locked)
        if result:
            return _ok(f"{track_type} track {track_index} {'locked' if locked else 'unlocked'}")
        return _err("Failed to set track lock state")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_is_track_locked(timeline_id: str, track_type: str, track_index: int) -> str:
    """Check if a track is locked.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetIsTrackLocked(track_type, track_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_track_name(timeline_id: str, track_type: str, track_index: int) -> str:
    """Get the name of a track.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetTrackName(track_type, track_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_track_name(timeline_id: str, track_type: str, track_index: int, name: str) -> str:
    """Rename a track.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)
        name: New track name
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetTrackName(track_type, track_index, name)
        if result:
            return _ok(f"Track renamed to '{name}'")
        return _err("Failed to rename track")
    except Exception as e:
        return _err(str(e))


# ── Timeline Items ────────────────────────────────────────────────

@mcp.tool()
def timeline_get_item_list_in_track(timeline_id: str, track_type: str, track_index: int) -> str:
    """Get all clips/items on a specific track.

    Args:
        timeline_id: Timeline ID
        track_type: 'video', 'audio', or 'subtitle'
        track_index: Track index (1-based)

    Returns list of TimelineItem references.
    """
    try:
        conn, tl = _get_tl(timeline_id)
        items = tl.GetItemListInTrack(track_type, track_index)
        if items is None:
            return _ok([])
        result = []
        for item in items:
            iid = conn.register(item, "TimelineItem")
            result.append({
                "id": iid,
                "type": "TimelineItem",
                "name": item.GetName(),
                "start": item.GetStart(),
                "end": item.GetEnd(),
                "duration": item.GetDuration(),
            })
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_delete_clips(timeline_id: str, item_ids: list[str], ripple: bool = False) -> str:
    """Delete clips from the timeline.

    Args:
        timeline_id: Timeline ID
        item_ids: List of TimelineItem IDs to delete
        ripple: If True, performs ripple delete (closes gaps). Default False.
    """
    try:
        conn, tl = _get_tl(timeline_id)
        items = [conn.get(iid, "TimelineItem") for iid in item_ids]
        result = tl.DeleteClips(items, ripple)
        if result:
            for iid in item_ids:
                conn.remove(iid)
            return _ok(f"Deleted {len(item_ids)} clip(s)")
        return _err("Failed to delete clips")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_clips_linked(timeline_id: str, item_ids: list[str], linked: bool) -> str:
    """Link or unlink timeline items.

    Args:
        timeline_id: Timeline ID
        item_ids: List of TimelineItem IDs
        linked: True to link, False to unlink
    """
    try:
        conn, tl = _get_tl(timeline_id)
        items = [conn.get(iid, "TimelineItem") for iid in item_ids]
        result = tl.SetClipsLinked(items, linked)
        if result:
            return _ok(f"Clips {'linked' if linked else 'unlinked'}")
        return _err("Failed to set clip link state")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_current_video_item(timeline_id: str) -> str:
    """Get the current video timeline item (at the playhead).

    Args:
        timeline_id: Timeline ID
    """
    try:
        conn, tl = _get_tl(timeline_id)
        item = tl.GetCurrentVideoItem()
        if item is None:
            return _err("No video item at current playhead position")
        iid = conn.register(item, "TimelineItem")
        return _ok({"id": iid, "type": "TimelineItem", "name": item.GetName()})
    except Exception as e:
        return _err(str(e))


# ── Markers ───────────────────────────────────────────────────────

@mcp.tool()
def timeline_add_marker(
    timeline_id: str, frame_id: float, color: str, name: str,
    note: str, duration: float, custom_data: str | None = None,
) -> str:
    """Add a marker to the timeline.

    Args:
        timeline_id: Timeline ID
        frame_id: Frame position
        color: Marker color
        name: Marker name
        note: Marker note
        duration: Duration in frames
        custom_data: Optional custom data
    """
    try:
        _, tl = _get_tl(timeline_id)
        if custom_data is not None:
            result = tl.AddMarker(frame_id, color, name, note, duration, custom_data)
        else:
            result = tl.AddMarker(frame_id, color, name, note, duration)
        if result:
            return _ok(f"Marker added at frame {frame_id}")
        return _err(f"Failed to add marker at frame {frame_id}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_markers(timeline_id: str) -> str:
    """Get all timeline markers.

    Args:
        timeline_id: Timeline ID

    Returns dict of {frameId: {color, duration, note, name, customData}}.
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetMarkers())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_marker_by_custom_data(timeline_id: str, custom_data: str) -> str:
    """Find the first timeline marker matching custom data.

    Args:
        timeline_id: Timeline ID
        custom_data: Custom data to search for
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetMarkerByCustomData(custom_data))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_update_marker_custom_data(timeline_id: str, frame_id: float, custom_data: str) -> str:
    """Update custom data for a timeline marker.

    Args:
        timeline_id: Timeline ID
        frame_id: Frame position of the marker
        custom_data: New custom data
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.UpdateMarkerCustomData(frame_id, custom_data)
        if result:
            return _ok(f"Marker custom data updated at frame {frame_id}")
        return _err(f"Failed to update marker at frame {frame_id}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_get_marker_custom_data(timeline_id: str, frame_id: float) -> str:
    """Get custom data for a timeline marker.

    Args:
        timeline_id: Timeline ID
        frame_id: Frame position
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetMarkerCustomData(frame_id))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_delete_markers_by_color(timeline_id: str, color: str) -> str:
    """Delete all timeline markers of a color. Use 'All' to delete all.

    Args:
        timeline_id: Timeline ID
        color: Color to delete, or 'All'
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.DeleteMarkersByColor(color)
        if result:
            return _ok(f"Markers of color '{color}' deleted")
        return _err("Failed to delete markers")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_delete_marker_at_frame(timeline_id: str, frame_num: float) -> str:
    """Delete the timeline marker at a specific frame.

    Args:
        timeline_id: Timeline ID
        frame_num: Frame number
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.DeleteMarkerAtFrame(frame_num)
        if result:
            return _ok(f"Marker deleted at frame {frame_num}")
        return _err(f"No marker at frame {frame_num}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_delete_marker_by_custom_data(timeline_id: str, custom_data: str) -> str:
    """Delete the first timeline marker matching custom data.

    Args:
        timeline_id: Timeline ID
        custom_data: Custom data to match
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.DeleteMarkerByCustomData(custom_data)
        if result:
            return _ok("Marker deleted")
        return _err("No matching marker found")
    except Exception as e:
        return _err(str(e))


# ── Timecode & Playhead ──────────────────────────────────────────

@mcp.tool()
def timeline_get_current_timecode(timeline_id: str) -> str:
    """Get the current playhead timecode. Works on Cut, Edit, Color, Fairlight, Deliver pages.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetCurrentTimecode())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_current_timecode(timeline_id: str, timecode: str) -> str:
    """Set the playhead position. Works on Cut, Edit, Color, Fairlight, Deliver pages.

    Args:
        timeline_id: Timeline ID
        timecode: Timecode string (e.g., '01:00:05:12')
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetCurrentTimecode(timecode)
        if result:
            return _ok(f"Playhead moved to {timecode}")
        return _err(f"Failed to set timecode to '{timecode}'")
    except Exception as e:
        return _err(str(e))


# ── Thumbnail ─────────────────────────────────────────────────────

@mcp.tool()
def timeline_get_current_clip_thumbnail_image(timeline_id: str) -> str:
    """Get a thumbnail of the current clip in the Color page. Returns base64-encoded RGB 8-bit image data.

    Must be on the Color page.

    Args:
        timeline_id: Timeline ID

    Returns dict with 'width', 'height', 'format', and 'data' (base64 RGB).
    """
    try:
        _, tl = _get_tl(timeline_id)
        thumb = tl.GetCurrentClipThumbnailImage()
        if thumb is None:
            return _err("Failed to get thumbnail. Ensure Color page is active.")
        return _ok(thumb)
    except Exception as e:
        return _err(str(e))


# ── Compound & Fusion Clips ──────────────────────────────────────

@mcp.tool()
def timeline_duplicate_timeline(timeline_id: str, timeline_name: str | None = None) -> str:
    """Duplicate a timeline.

    Args:
        timeline_id: Timeline ID
        timeline_name: Optional name for the duplicate
    """
    try:
        conn, tl = _get_tl(timeline_id)
        if timeline_name:
            dup = tl.DuplicateTimeline(timeline_name)
        else:
            dup = tl.DuplicateTimeline()
        if dup is None:
            return _err("Failed to duplicate timeline")
        did = conn.register(dup, "Timeline")
        return _ok({"id": did, "type": "Timeline", "name": dup.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_create_compound_clip(
    timeline_id: str, item_ids: list[str],
    start_timecode: str | None = None, name: str | None = None,
) -> str:
    """Create a compound clip from selected timeline items.

    Args:
        timeline_id: Timeline ID
        item_ids: List of TimelineItem IDs to compound
        start_timecode: Optional start timecode (e.g., '00:00:00:00')
        name: Optional name (e.g., 'Compound Clip 1')
    """
    try:
        conn, tl = _get_tl(timeline_id)
        items = [conn.get(iid, "TimelineItem") for iid in item_ids]
        clip_info = {}
        if start_timecode:
            clip_info["startTimecode"] = start_timecode
        if name:
            clip_info["name"] = name
        compound = tl.CreateCompoundClip(items, clip_info) if clip_info else tl.CreateCompoundClip(items)
        if compound is None:
            return _err("Failed to create compound clip")
        cid = conn.register(compound, "TimelineItem")
        return _ok({"id": cid, "type": "TimelineItem", "name": compound.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_create_fusion_clip(timeline_id: str, item_ids: list[str]) -> str:
    """Create a Fusion clip from selected timeline items.

    Args:
        timeline_id: Timeline ID
        item_ids: List of TimelineItem IDs
    """
    try:
        conn, tl = _get_tl(timeline_id)
        items = [conn.get(iid, "TimelineItem") for iid in item_ids]
        fusion_clip = tl.CreateFusionClip(items)
        if fusion_clip is None:
            return _err("Failed to create Fusion clip")
        fid = conn.register(fusion_clip, "TimelineItem")
        return _ok({"id": fid, "type": "TimelineItem", "name": fusion_clip.GetName()})
    except Exception as e:
        return _err(str(e))


# ── Import & Export ───────────────────────────────────────────────

@mcp.tool()
def timeline_import_into_timeline(
    timeline_id: str, file_path: str,
    auto_import_source_clips: bool | None = None,
    ignore_file_extensions: bool | None = None,
    link_to_source_camera_files: bool | None = None,
    use_sizing_info: bool | None = None,
    import_multichannel_as_linked: bool | None = None,
    insert_additional_tracks: bool | None = None,
    insert_with_offset: str | None = None,
    source_clips_path: str | None = None,
) -> str:
    """Import timeline items from an AAF file into this timeline.

    Args:
        timeline_id: Timeline ID
        file_path: Path to the AAF file
        auto_import_source_clips: Import source clips into media pool (default True)
        ignore_file_extensions: Ignore extensions when matching (default False)
        link_to_source_camera_files: Link to camera files (default False)
        use_sizing_info: Use sizing information (default False)
        import_multichannel_as_linked: Import multi-channel audio as linked groups (default False)
        insert_additional_tracks: Insert additional tracks (default True)
        insert_with_offset: Timecode offset for insert (e.g., '00:00:00:00')
        source_clips_path: Path to search for source clips
    """
    try:
        _, tl = _get_tl(timeline_id)
        options = AAFImportOptions(
            autoImportSourceClipsIntoMediaPool=auto_import_source_clips,
            ignoreFileExtensionsWhenMatching=ignore_file_extensions,
            linkToSourceCameraFiles=link_to_source_camera_files,
            useSizingInfo=use_sizing_info,
            importMultiChannelAudioTracksAsLinkedGroups=import_multichannel_as_linked,
            insertAdditionalTracks=insert_additional_tracks,
            insertWithOffset=insert_with_offset,
            sourceClipsPath=source_clips_path,
        )
        result = tl.ImportIntoTimeline(file_path, options.to_resolve_dict())
        if result:
            return _ok(f"Imported from '{file_path}' into timeline")
        return _err(f"Failed to import from '{file_path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_export(
    timeline_id: str, file_name: str, export_type: str, export_subtype: str = "NONE",
) -> str:
    """Export a timeline to a file.

    Args:
        timeline_id: Timeline ID
        file_name: Output file path
        export_type: AAF, DRT, EDL, FCP_7_XML, FCPXML_1_8, FCPXML_1_9, FCPXML_1_10,
                     HDR_10_PROFILE_A, HDR_10_PROFILE_B, TEXT_CSV, TEXT_TAB,
                     DOLBY_VISION_VER_2_9, DOLBY_VISION_VER_4_0, DOLBY_VISION_VER_5_1,
                     OTIO, ALE, ALE_CDL
        export_subtype: For AAF: AAF_NEW or AAF_EXISTING. For EDL: CDL, SDL, MISSING_CLIPS, or NONE. Default: NONE.
    """
    try:
        conn, tl = _get_tl(timeline_id)
        r = conn.resolve
        etype = resolve_enum(r, EXPORT_TYPES, export_type)
        esub = resolve_enum(r, EXPORT_SUBTYPES, export_subtype)
        result = tl.Export(file_name, etype, esub)
        if result:
            return _ok(f"Timeline exported to '{file_name}'")
        return _err("Failed to export timeline")
    except Exception as e:
        return _err(str(e))


# ── Settings ──────────────────────────────────────────────────────

@mcp.tool()
def timeline_get_setting(timeline_id: str, setting_name: str | None = None) -> str:
    """Get a timeline setting.

    Args:
        timeline_id: Timeline ID
        setting_name: Setting key. If None, returns all settings.
    """
    try:
        _, tl = _get_tl(timeline_id)
        if setting_name:
            return _ok(tl.GetSetting(setting_name))
        return _ok(tl.GetSetting(""))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_setting(timeline_id: str, setting_name: str, setting_value: str) -> str:
    """Set a timeline setting.

    Args:
        timeline_id: Timeline ID
        setting_name: Setting key
        setting_value: New value
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetSetting(setting_name, setting_value)
        if result:
            return _ok(f"Setting '{setting_name}' set to '{setting_value}'")
        return _err(f"Failed to set '{setting_name}'")
    except Exception as e:
        return _err(str(e))


# ── Generators & Titles ──────────────────────────────────────────

@mcp.tool()
def timeline_insert_generator_into_timeline(timeline_id: str, generator_name: str) -> str:
    """Insert a generator into the timeline.

    Args:
        timeline_id: Timeline ID
        generator_name: Name of the generator
    """
    try:
        conn, tl = _get_tl(timeline_id)
        item = tl.InsertGeneratorIntoTimeline(generator_name)
        if item is None:
            return _err(f"Failed to insert generator '{generator_name}'")
        iid = conn.register(item, "TimelineItem")
        return _ok({"id": iid, "type": "TimelineItem", "name": item.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_insert_fusion_generator_into_timeline(timeline_id: str, generator_name: str) -> str:
    """Insert a Fusion generator into the timeline.

    Args:
        timeline_id: Timeline ID
        generator_name: Name of the Fusion generator
    """
    try:
        conn, tl = _get_tl(timeline_id)
        item = tl.InsertFusionGeneratorIntoTimeline(generator_name)
        if item is None:
            return _err(f"Failed to insert Fusion generator '{generator_name}'")
        iid = conn.register(item, "TimelineItem")
        return _ok({"id": iid, "type": "TimelineItem", "name": item.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_insert_fusion_composition_into_timeline(timeline_id: str) -> str:
    """Insert a Fusion composition into the timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        conn, tl = _get_tl(timeline_id)
        item = tl.InsertFusionCompositionIntoTimeline()
        if item is None:
            return _err("Failed to insert Fusion composition")
        iid = conn.register(item, "TimelineItem")
        return _ok({"id": iid, "type": "TimelineItem", "name": item.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_insert_ofx_generator_into_timeline(timeline_id: str, generator_name: str) -> str:
    """Insert an OFX generator into the timeline.

    Args:
        timeline_id: Timeline ID
        generator_name: Name of the OFX generator
    """
    try:
        conn, tl = _get_tl(timeline_id)
        item = tl.InsertOFXGeneratorIntoTimeline(generator_name)
        if item is None:
            return _err(f"Failed to insert OFX generator '{generator_name}'")
        iid = conn.register(item, "TimelineItem")
        return _ok({"id": iid, "type": "TimelineItem", "name": item.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_insert_title_into_timeline(timeline_id: str, title_name: str) -> str:
    """Insert a title into the timeline.

    Args:
        timeline_id: Timeline ID
        title_name: Name of the title template
    """
    try:
        conn, tl = _get_tl(timeline_id)
        item = tl.InsertTitleIntoTimeline(title_name)
        if item is None:
            return _err(f"Failed to insert title '{title_name}'")
        iid = conn.register(item, "TimelineItem")
        return _ok({"id": iid, "type": "TimelineItem", "name": item.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_insert_fusion_title_into_timeline(timeline_id: str, title_name: str) -> str:
    """Insert a Fusion title into the timeline.

    Args:
        timeline_id: Timeline ID
        title_name: Name of the Fusion title template
    """
    try:
        conn, tl = _get_tl(timeline_id)
        item = tl.InsertFusionTitleIntoTimeline(title_name)
        if item is None:
            return _err(f"Failed to insert Fusion title '{title_name}'")
        iid = conn.register(item, "TimelineItem")
        return _ok({"id": iid, "type": "TimelineItem", "name": item.GetName()})
    except Exception as e:
        return _err(str(e))


# ── Stills ────────────────────────────────────────────────────────

@mcp.tool()
def timeline_grab_still(timeline_id: str) -> str:
    """Grab a still from the current video clip.

    Args:
        timeline_id: Timeline ID
    """
    try:
        conn, tl = _get_tl(timeline_id)
        still = tl.GrabStill()
        if still is None:
            return _err("Failed to grab still")
        sid = conn.register(still, "GalleryStill", composite_key=f"still:{id(still)}")
        return _ok({"id": sid, "type": "GalleryStill"})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_grab_all_stills(timeline_id: str, still_frame_source: int) -> str:
    """Grab stills from all clips in the timeline.

    Args:
        timeline_id: Timeline ID
        still_frame_source: 1 = First frame, 2 = Middle frame
    """
    try:
        conn, tl = _get_tl(timeline_id)
        stills = tl.GrabAllStills(still_frame_source)
        if stills is None:
            return _err("Failed to grab stills")
        result = []
        for still in stills:
            sid = conn.register(still, "GalleryStill", composite_key=f"still:{id(still)}")
            result.append({"id": sid, "type": "GalleryStill"})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Subtitles & Scene Detection ───────────────────────────────────

@mcp.tool()
def timeline_create_subtitles_from_audio(
    timeline_id: str, language: str | None = None, caption_preset: str | None = None,
    chars_per_line: int | None = None, line_break: str | None = None, gap: int | None = None,
) -> str:
    """Create subtitles from the timeline's audio.

    Args:
        timeline_id: Timeline ID
        language: AUTO, ENGLISH, FRENCH, GERMAN, SPANISH, JAPANESE, KOREAN, etc.
        caption_preset: DEFAULT, TELETEXT, or NETFLIX
        chars_per_line: 1-60 (default depends on language/preset)
        line_break: SINGLE or DOUBLE
        gap: 0-10 frames between subtitles
    """
    try:
        conn, tl = _get_tl(timeline_id)
        settings = AutoCaptionSettings(
            language=language, caption_preset=caption_preset,
            chars_per_line=chars_per_line, line_break=line_break, gap=gap,
        )
        resolve_dict = _auto_caption_to_resolve_dict(conn, settings)
        result = tl.CreateSubtitlesFromAudio(resolve_dict) if resolve_dict else tl.CreateSubtitlesFromAudio()
        if result:
            return _ok("Subtitles created from audio")
        return _err("Failed to create subtitles")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_detect_scene_cuts(timeline_id: str) -> str:
    """Detect and create scene cuts along the timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.DetectSceneCuts()
        if result:
            return _ok("Scene cuts detected")
        return _err("Failed to detect scene cuts")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_convert_timeline_to_stereo(timeline_id: str) -> str:
    """Convert timeline to stereo.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.ConvertTimelineToStereo()
        if result:
            return _ok("Timeline converted to stereo")
        return _err("Failed to convert to stereo")
    except Exception as e:
        return _err(str(e))


# ── Node Graph ────────────────────────────────────────────────────

@mcp.tool()
def timeline_get_node_graph(timeline_id: str) -> str:
    """Get the timeline's node graph object.

    Args:
        timeline_id: Timeline ID
    """
    try:
        conn, tl = _get_tl(timeline_id)
        graph = tl.GetNodeGraph()
        if graph is None:
            return _err("Failed to get node graph")
        gid = conn.register(graph, "Graph", composite_key=f"graph:timeline:{timeline_id}")
        return _ok({"id": gid, "type": "Graph"})
    except Exception as e:
        return _err(str(e))


# ── Dolby Vision ──────────────────────────────────────────────────

@mcp.tool()
def timeline_analyze_dolby_vision(
    timeline_id: str, item_ids: list[str] | None = None, analysis_type: str | None = None,
) -> str:
    """Analyze Dolby Vision on timeline clips.

    Args:
        timeline_id: Timeline ID
        item_ids: Optional TimelineItem IDs. If empty, analyzes all clips.
        analysis_type: Optional 'BLEND_SHOTS' for blend setting
    """
    try:
        conn, tl = _get_tl(timeline_id)
        items = [conn.get(iid, "TimelineItem") for iid in item_ids] if item_ids else []
        if analysis_type:
            at = resolve_enum(conn.resolve, DOLBY_VISION_ANALYSIS_TYPES, analysis_type)
            result = tl.AnalyzeDolbyVision(items, at)
        else:
            result = tl.AnalyzeDolbyVision(items)
        if result:
            return _ok("Dolby Vision analysis started")
        return _err("Failed to start Dolby Vision analysis")
    except Exception as e:
        return _err(str(e))


# ── Media Pool Item reference ─────────────────────────────────────

@mcp.tool()
def timeline_get_media_pool_item(timeline_id: str) -> str:
    """Get the MediaPoolItem corresponding to a timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        conn, tl = _get_tl(timeline_id)
        mpi = tl.GetMediaPoolItem()
        if mpi is None:
            return _err("No MediaPoolItem for this timeline")
        mid = conn.register(mpi, "MediaPoolItem")
        return _ok({"id": mid, "type": "MediaPoolItem", "name": mpi.GetName()})
    except Exception as e:
        return _err(str(e))


# ── Marks ─────────────────────────────────────────────────────────

@mcp.tool()
def timeline_get_mark_in_out(timeline_id: str) -> str:
    """Get mark in/out points for the timeline.

    Args:
        timeline_id: Timeline ID
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetMarkInOut())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_mark_in_out(timeline_id: str, mark_in: int, mark_out: int, mark_type: str = "all") -> str:
    """Set mark in/out points for the timeline.

    Args:
        timeline_id: Timeline ID
        mark_in: In point frame
        mark_out: Out point frame
        mark_type: 'video', 'audio', or 'all' (default)
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.SetMarkInOut(mark_in, mark_out, mark_type)
        if result:
            return _ok(f"Mark in/out set: {mark_in}-{mark_out}")
        return _err("Failed to set marks")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_clear_mark_in_out(timeline_id: str, mark_type: str = "all") -> str:
    """Clear mark in/out points.

    Args:
        timeline_id: Timeline ID
        mark_type: 'video', 'audio', or 'all' (default)
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.ClearMarkInOut(mark_type)
        if result:
            return _ok("Marks cleared")
        return _err("Failed to clear marks")
    except Exception as e:
        return _err(str(e))


# ── Voice Isolation ───────────────────────────────────────────────

@mcp.tool()
def timeline_get_voice_isolation_state(timeline_id: str, track_index: int) -> str:
    """Get voice isolation state for an audio track. Requires Resolve 20.1+.

    Args:
        timeline_id: Timeline ID
        track_index: Audio track index (1-based)
    """
    try:
        _, tl = _get_tl(timeline_id)
        return _ok(tl.GetVoiceIsolationState(track_index))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def timeline_set_voice_isolation_state(
    timeline_id: str, track_index: int, is_enabled: bool, amount: int,
) -> str:
    """Set voice isolation state for an audio track. Requires Resolve 20.1+.

    Args:
        timeline_id: Timeline ID
        track_index: Audio track index (1-based)
        is_enabled: Enable/disable voice isolation
        amount: Isolation amount (0-100)
    """
    try:
        _, tl = _get_tl(timeline_id)
        state = {"isEnabled": is_enabled, "amount": amount}
        result = tl.SetVoiceIsolationState(track_index, state)
        if result:
            return _ok("Voice isolation state set")
        return _err("Failed to set voice isolation state")
    except Exception as e:
        return _err(str(e))


# ── Fairlight Preset ──────────────────────────────────────────────

@mcp.tool()
def timeline_apply_fairlight_preset(timeline_id: str, preset_name: str) -> str:
    """Apply a Fairlight preset to a timeline. Requires Resolve 20.2.2+.

    Args:
        timeline_id: Timeline ID
        preset_name: Fairlight preset name
    """
    try:
        _, tl = _get_tl(timeline_id)
        result = tl.ApplyFairlightPreset(preset_name)
        if result:
            return _ok(f"Fairlight preset '{preset_name}' applied")
        return _err(f"Failed to apply preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))
