"""Tools for the Project object.

Covers: timelines, render jobs, settings, formats/codecs, presets,
color groups, Fairlight, LUTs, and more.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.models import RenderSettings, QuickExportSettings

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_project():
    """Get the current project from the connection."""
    conn = get_connection()
    project = conn.get_current_project()
    return conn, project


# ── Basic Info ────────────────────────────────────────────────────

@mcp.tool()
def project_get_name() -> str:
    """Get the name of the current project."""
    try:
        _, project = _get_project()
        return _ok(project.GetName())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_set_name(project_name: str) -> str:
    """Rename the current project.

    Args:
        project_name: New name (must be unique in the database folder)
    """
    try:
        _, project = _get_project()
        result = project.SetName(project_name)
        if result:
            return _ok(f"Project renamed to '{project_name}'")
        return _err(f"Failed to rename project. Name '{project_name}' may already exist.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_unique_id() -> str:
    """Get the unique ID of the current project."""
    try:
        _, project = _get_project()
        return _ok(project.GetUniqueId())
    except Exception as e:
        return _err(str(e))


# ── Media Pool ────────────────────────────────────────────────────

@mcp.tool()
def project_get_media_pool() -> str:
    """Get the Media Pool object for the current project."""
    try:
        conn, project = _get_project()
        mp = project.GetMediaPool()
        if mp is None:
            return _err("Failed to get Media Pool")
        mp_id = conn.register(mp, "MediaPool")
        return _ok({"id": mp_id, "type": "MediaPool"})
    except Exception as e:
        return _err(str(e))


# ── Timeline Management ──────────────────────────────────────────

@mcp.tool()
def project_get_timeline_count() -> str:
    """Get the number of timelines in the current project."""
    try:
        _, project = _get_project()
        return _ok(project.GetTimelineCount())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_timeline_by_index(index: int) -> str:
    """Get a timeline by its index (1-based).

    Args:
        index: Timeline index, 1 <= index <= GetTimelineCount()
    """
    try:
        conn, project = _get_project()
        timeline = project.GetTimelineByIndex(index)
        if timeline is None:
            count = project.GetTimelineCount()
            return _err(f"No timeline at index {index}. Project has {count} timelines (1-based index).")
        tid = conn.register(timeline, "Timeline")
        return _ok({"id": tid, "type": "Timeline", "name": timeline.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_current_timeline() -> str:
    """Get the currently active timeline."""
    try:
        conn, project = _get_project()
        timeline = project.GetCurrentTimeline()
        if timeline is None:
            return _err("No timeline is currently active")
        tid = conn.register(timeline, "Timeline")
        return _ok({"id": tid, "type": "Timeline", "name": timeline.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_set_current_timeline(timeline_id: str) -> str:
    """Set a timeline as the current active timeline.

    Args:
        timeline_id: ID of the timeline (from timeline tools)
    """
    try:
        conn, project = _get_project()
        timeline = conn.get(timeline_id, "Timeline")
        result = project.SetCurrentTimeline(timeline)
        if result:
            return _ok("Timeline set as current")
        return _err("Failed to set current timeline")
    except Exception as e:
        return _err(str(e))


# ── Gallery ───────────────────────────────────────────────────────

@mcp.tool()
def project_get_gallery() -> str:
    """Get the Gallery object for the current project."""
    try:
        conn, project = _get_project()
        gallery = project.GetGallery()
        if gallery is None:
            return _err("Failed to get Gallery")
        project_id = project.GetUniqueId()
        gid = conn.register(gallery, "Gallery", composite_key=f"gallery:{project_id}")
        return _ok({"id": gid, "type": "Gallery"})
    except Exception as e:
        return _err(str(e))


# ── Presets ───────────────────────────────────────────────────────

@mcp.tool()
def project_get_preset_list() -> str:
    """Get a list of available project presets."""
    try:
        _, project = _get_project()
        return _ok(project.GetPresetList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_set_preset(preset_name: str) -> str:
    """Apply a project preset.

    Args:
        preset_name: Name of the preset to apply
    """
    try:
        _, project = _get_project()
        result = project.SetPreset(preset_name)
        if result:
            return _ok(f"Preset '{preset_name}' applied")
        return _err(f"Failed to apply preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


# ── Render Jobs ───────────────────────────────────────────────────

@mcp.tool()
def project_add_render_job() -> str:
    """Add a render job to the queue based on current render settings.

    Returns the unique job ID for the new render job.
    """
    try:
        _, project = _get_project()
        job_id = project.AddRenderJob()
        if job_id:
            return _ok({"job_id": job_id})
        return _err("Failed to add render job. Check render settings are valid.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_delete_render_job(job_id: str) -> str:
    """Delete a render job from the queue.

    Args:
        job_id: Unique ID of the render job to delete
    """
    try:
        _, project = _get_project()
        result = project.DeleteRenderJob(job_id)
        if result:
            return _ok(f"Render job '{job_id}' deleted")
        return _err(f"Failed to delete render job '{job_id}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_delete_all_render_jobs() -> str:
    """Delete all render jobs from the queue."""
    try:
        _, project = _get_project()
        result = project.DeleteAllRenderJobs()
        if result:
            return _ok("All render jobs deleted")
        return _err("Failed to delete render jobs")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_render_job_list() -> str:
    """Get a list of all render jobs and their information."""
    try:
        _, project = _get_project()
        return _ok(project.GetRenderJobList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_render_job_status(job_id: str) -> str:
    """Get the status and completion percentage of a render job.

    Args:
        job_id: Unique ID of the render job
    """
    try:
        _, project = _get_project()
        return _ok(project.GetRenderJobStatus(job_id))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_start_rendering(
    job_ids: list[str] | None = None,
    is_interactive_mode: bool = False
) -> str:
    """Start rendering jobs.

    Args:
        job_ids: Optional list of specific job IDs to render. If None, renders all queued jobs.
        is_interactive_mode: Enable error feedback in UI during rendering (default False)
    """
    try:
        _, project = _get_project()
        if job_ids:
            result = project.StartRendering(job_ids, is_interactive_mode)
        else:
            result = project.StartRendering(is_interactive_mode)
        if result:
            return _ok("Rendering started")
        return _err("Failed to start rendering")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_stop_rendering() -> str:
    """Stop any current render processes."""
    try:
        _, project = _get_project()
        project.StopRendering()
        return _ok("Rendering stopped")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_is_rendering_in_progress() -> str:
    """Check if rendering is currently in progress."""
    try:
        _, project = _get_project()
        return _ok(project.IsRenderingInProgress())
    except Exception as e:
        return _err(str(e))


# ── Render Presets ────────────────────────────────────────────────

@mcp.tool()
def project_get_render_preset_list() -> str:
    """Get a list of available render presets."""
    try:
        _, project = _get_project()
        return _ok(project.GetRenderPresetList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_load_render_preset(preset_name: str) -> str:
    """Load a render preset as the current rendering preset.

    Args:
        preset_name: Name of the preset to load
    """
    try:
        _, project = _get_project()
        result = project.LoadRenderPreset(preset_name)
        if result:
            return _ok(f"Render preset '{preset_name}' loaded")
        return _err(f"Failed to load render preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_save_as_new_render_preset(preset_name: str) -> str:
    """Save current render settings as a new preset.

    Args:
        preset_name: Unique name for the new preset
    """
    try:
        _, project = _get_project()
        result = project.SaveAsNewRenderPreset(preset_name)
        if result:
            return _ok(f"Render preset '{preset_name}' saved")
        return _err(f"Failed to save render preset. Name '{preset_name}' may already exist.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_delete_render_preset(preset_name: str) -> str:
    """Delete a render preset.

    Args:
        preset_name: Name of the preset to delete
    """
    try:
        _, project = _get_project()
        result = project.DeleteRenderPreset(preset_name)
        if result:
            return _ok(f"Render preset '{preset_name}' deleted")
        return _err(f"Failed to delete render preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


# ── Render Settings ──────────────────────────────────────────────

@mcp.tool()
def project_set_render_settings(
    SelectAllFrames: bool | None = None,
    MarkIn: int | None = None,
    MarkOut: int | None = None,
    TargetDir: str | None = None,
    CustomName: str | None = None,
    UniqueFilenameStyle: int | None = None,
    ExportVideo: bool | None = None,
    ExportAudio: bool | None = None,
    FormatWidth: int | None = None,
    FormatHeight: int | None = None,
    FrameRate: float | None = None,
    PixelAspectRatio: str | None = None,
    VideoQuality: int | str | None = None,
    AudioCodec: str | None = None,
    AudioBitDepth: int | None = None,
    AudioSampleRate: int | None = None,
    ColorSpaceTag: str | None = None,
    GammaTag: str | None = None,
    ExportAlpha: bool | None = None,
    EncodingProfile: str | None = None,
    MultiPassEncode: bool | None = None,
    AlphaMode: int | None = None,
    NetworkOptimization: bool | None = None,
    ClipStartFrame: int | None = None,
    TimelineStartTimecode: str | None = None,
    ReplaceExistingFilesInPlace: bool | None = None,
    ExportSubtitle: bool | None = None,
    SubtitleFormat: str | None = None,
) -> str:
    """Set render settings. Only provided parameters are changed; others remain unchanged.

    Args:
        SelectAllFrames: When True, MarkIn/MarkOut are ignored
        MarkIn: Start frame for render range
        MarkOut: End frame for render range
        TargetDir: Output directory path
        CustomName: Custom output filename
        UniqueFilenameStyle: 0=Prefix, 1=Suffix
        ExportVideo: Export video track
        ExportAudio: Export audio track
        FormatWidth: Output width in pixels
        FormatHeight: Output height in pixels
        FrameRate: Output frame rate (e.g., 23.976, 24, 29.97)
        PixelAspectRatio: SD: '16_9'/'4_3'. Other: 'square'/'cinemascope'
        VideoQuality: 0=auto, 1-MAX=bitrate, or 'Least'/'Low'/'Medium'/'High'/'Best'
        AudioCodec: e.g., 'aac'
        AudioBitDepth: Audio bit depth
        AudioSampleRate: Audio sample rate
        ColorSpaceTag: e.g., 'Same as Project'
        GammaTag: e.g., 'Same as Project', 'ACEScct'
        ExportAlpha: Export alpha channel
        EncodingProfile: e.g., 'Main10' (H.264/H.265 only)
        MultiPassEncode: Multi-pass encoding (H.264 only)
        AlphaMode: 0=Premultiplied, 1=Straight
        NetworkOptimization: QuickTime/MP4 only
        ClipStartFrame: Start frame number for clips
        TimelineStartTimecode: e.g., '01:00:00:00'
        ReplaceExistingFilesInPlace: Overwrite existing files
        ExportSubtitle: Export subtitles
        SubtitleFormat: 'BurnIn', 'EmbeddedCaptions', or 'SeparateFile'
    """
    try:
        settings = RenderSettings(
            SelectAllFrames=SelectAllFrames, MarkIn=MarkIn, MarkOut=MarkOut,
            TargetDir=TargetDir, CustomName=CustomName,
            UniqueFilenameStyle=UniqueFilenameStyle,
            ExportVideo=ExportVideo, ExportAudio=ExportAudio,
            FormatWidth=FormatWidth, FormatHeight=FormatHeight,
            FrameRate=FrameRate, PixelAspectRatio=PixelAspectRatio,
            VideoQuality=VideoQuality, AudioCodec=AudioCodec,
            AudioBitDepth=AudioBitDepth, AudioSampleRate=AudioSampleRate,
            ColorSpaceTag=ColorSpaceTag, GammaTag=GammaTag,
            ExportAlpha=ExportAlpha, EncodingProfile=EncodingProfile,
            MultiPassEncode=MultiPassEncode, AlphaMode=AlphaMode,
            NetworkOptimization=NetworkOptimization,
            ClipStartFrame=ClipStartFrame,
            TimelineStartTimecode=TimelineStartTimecode,
            ReplaceExistingFilesInPlace=ReplaceExistingFilesInPlace,
            ExportSubtitle=ExportSubtitle, SubtitleFormat=SubtitleFormat,
        )
        _, project = _get_project()
        settings_dict = settings.to_resolve_dict()
        if not settings_dict:
            return _err("No settings provided")
        result = project.SetRenderSettings(settings_dict)
        if result:
            return _ok({"applied": list(settings_dict.keys())})
        return _err("Failed to set render settings. Check values are valid for the current format/codec.")
    except Exception as e:
        return _err(str(e))


# ── Render Formats & Codecs ──────────────────────────────────────

@mcp.tool()
def project_get_render_formats() -> str:
    """Get available render formats as a dict of format -> file extension."""
    try:
        _, project = _get_project()
        return _ok(project.GetRenderFormats())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_render_codecs(render_format: str) -> str:
    """Get available codecs for a render format.

    Args:
        render_format: Render format name (from project_get_render_formats)

    Returns dict of codec_description -> codec_name.
    """
    try:
        _, project = _get_project()
        return _ok(project.GetRenderCodecs(render_format))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_current_render_format_and_codec() -> str:
    """Get the currently selected render format and codec."""
    try:
        _, project = _get_project()
        return _ok(project.GetCurrentRenderFormatAndCodec())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_set_current_render_format_and_codec(format: str, codec: str) -> str:
    """Set the render format and codec.

    Args:
        format: Render format name
        codec: Codec name (from project_get_render_codecs)
    """
    try:
        _, project = _get_project()
        result = project.SetCurrentRenderFormatAndCodec(format, codec)
        if result:
            return _ok(f"Render format set to '{format}' with codec '{codec}'")
        return _err(f"Failed to set format '{format}' / codec '{codec}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_current_render_mode() -> str:
    """Get the current render mode.

    Returns 0 for 'Individual clips' or 1 for 'Single clip'.
    """
    try:
        _, project = _get_project()
        mode = project.GetCurrentRenderMode()
        mode_name = {0: "Individual clips", 1: "Single clip"}.get(mode, f"Unknown({mode})")
        return _ok({"mode": mode, "name": mode_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_set_current_render_mode(render_mode: int) -> str:
    """Set the render mode.

    Args:
        render_mode: 0 for 'Individual clips', 1 for 'Single clip'
    """
    try:
        _, project = _get_project()
        result = project.SetCurrentRenderMode(render_mode)
        if result:
            mode_name = {0: "Individual clips", 1: "Single clip"}.get(render_mode)
            return _ok(f"Render mode set to '{mode_name}'")
        return _err(f"Failed to set render mode to {render_mode}")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_get_render_resolutions(format: str | None = None, codec: str | None = None) -> str:
    """Get available render resolutions.

    Args:
        format: Optional render format to filter by
        codec: Optional codec to filter by (requires format)

    Returns list of dicts with 'Width' and 'Height' keys.
    """
    try:
        _, project = _get_project()
        if format and codec:
            result = project.GetRenderResolutions(format, codec)
        else:
            result = project.GetRenderResolutions()
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Quick Export ──────────────────────────────────────────────────

@mcp.tool()
def project_get_quick_export_render_presets() -> str:
    """Get a list of Quick Export render preset names."""
    try:
        _, project = _get_project()
        return _ok(project.GetQuickExportRenderPresets())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_render_with_quick_export(
    preset_name: str,
    TargetDir: str | None = None,
    CustomName: str | None = None,
    VideoQuality: int | str | None = None,
    EnableUpload: bool | None = None,
) -> str:
    """Start a quick export render for the current timeline.

    Args:
        preset_name: Preset name from project_get_quick_export_render_presets
        TargetDir: Output directory
        CustomName: Custom output filename
        VideoQuality: Quality setting
        EnableUpload: Enable direct upload for supported web presets
    """
    try:
        settings = QuickExportSettings(
            TargetDir=TargetDir, CustomName=CustomName,
            VideoQuality=VideoQuality, EnableUpload=EnableUpload,
        )
        _, project = _get_project()
        result = project.RenderWithQuickExport(preset_name, settings.to_resolve_dict())
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Project Settings ─────────────────────────────────────────────

@mcp.tool()
def project_get_setting(setting_name: str | None = None) -> str:
    """Get a project setting value.

    Args:
        setting_name: Setting key name. If None, returns all settings as a dict.

    Common settings: 'timelineFrameRate', 'timelineResolutionWidth', 'timelineResolutionHeight',
    'timelinePlaybackFrameRate', 'superScale', 'audioCaptureNumChannels', etc.
    """
    try:
        _, project = _get_project()
        if setting_name:
            result = project.GetSetting(setting_name)
        else:
            result = project.GetSetting("")
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_set_setting(
    setting_name: str,
    setting_value: str,
    sharpness: float | None = None,
    noise_reduction: float | None = None,
) -> str:
    """Set a project setting value.

    Args:
        setting_name: Setting key name
        setting_value: New value (string)
        sharpness: For superScale '2x Enhanced' only — float 0.0 to 1.0
        noise_reduction: For superScale '2x Enhanced' only — float 0.0 to 1.0

    For superScale '2x Enhanced', pass setting_name='superScale', setting_value='2',
    plus sharpness and noise_reduction values.
    """
    try:
        _, project = _get_project()
        if setting_name == "superScale" and sharpness is not None and noise_reduction is not None:
            result = project.SetSetting(setting_name, setting_value, sharpness, noise_reduction)
        else:
            result = project.SetSetting(setting_name, setting_value)
        if result:
            return _ok(f"Setting '{setting_name}' set to '{setting_value}'")
        return _err(f"Failed to set '{setting_name}'. The key or value may be invalid.")
    except Exception as e:
        return _err(str(e))


# ── LUTs ──────────────────────────────────────────────────────────

@mcp.tool()
def project_refresh_lut_list() -> str:
    """Refresh the LUT list so newly added LUTs are discoverable."""
    try:
        _, project = _get_project()
        result = project.RefreshLUTList()
        if result:
            return _ok("LUT list refreshed")
        return _err("Failed to refresh LUT list")
    except Exception as e:
        return _err(str(e))


# ── Fairlight / Audio ─────────────────────────────────────────────

@mcp.tool()
def project_insert_audio_to_current_track_at_playhead(
    media_path: str,
    start_offset_in_samples: int,
    duration_in_samples: int,
) -> str:
    """Insert audio at the playhead on the selected Fairlight track.

    Must be on the Fairlight page with a track selected.

    Args:
        media_path: Path to the audio file
        start_offset_in_samples: Sample offset to start from
        duration_in_samples: Duration in samples
    """
    try:
        _, project = _get_project()
        result = project.InsertAudioToCurrentTrackAtPlayhead(
            media_path, start_offset_in_samples, duration_in_samples
        )
        if result:
            return _ok("Audio inserted at playhead")
        return _err("Failed to insert audio. Ensure Fairlight page is active with a track selected.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_apply_fairlight_preset_to_current_timeline(preset_name: str) -> str:
    """Apply a Fairlight preset to the current timeline.

    Args:
        preset_name: Name of the Fairlight preset
    """
    try:
        _, project = _get_project()
        result = project.ApplyFairlightPresetToCurrentTimeline(preset_name)
        if result:
            return _ok(f"Fairlight preset '{preset_name}' applied")
        return _err(f"Failed to apply Fairlight preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


# ── Burn-In ───────────────────────────────────────────────────────

@mcp.tool()
def project_load_burn_in_preset(preset_name: str) -> str:
    """Load a data burn-in preset for the project.

    Args:
        preset_name: Name of the burn-in preset
    """
    try:
        _, project = _get_project()
        result = project.LoadBurnInPreset(preset_name)
        if result:
            return _ok(f"Burn-in preset '{preset_name}' loaded")
        return _err(f"Failed to load burn-in preset '{preset_name}'")
    except Exception as e:
        return _err(str(e))


# ── Still Export ──────────────────────────────────────────────────

@mcp.tool()
def project_export_current_frame_as_still(file_path: str) -> str:
    """Export the current frame as a still image.

    Args:
        file_path: Output path (must end with valid image extension, e.g., .png, .jpg, .tif)
    """
    try:
        _, project = _get_project()
        result = project.ExportCurrentFrameAsStill(file_path)
        if result:
            return _ok(f"Frame exported to '{file_path}'")
        return _err("Failed to export frame. Check the file path has a valid image extension.")
    except Exception as e:
        return _err(str(e))


# ── Color Groups ─────────────────────────────────────────────────

@mcp.tool()
def project_get_color_groups_list() -> str:
    """Get all color groups in the current project."""
    try:
        conn, project = _get_project()
        groups = project.GetColorGroupsList()
        result = []
        for g in (groups or []):
            name = g.GetName()
            gid = conn.register(g, "ColorGroup", composite_key=f"colorgroup:{name}")
            result.append({"id": gid, "type": "ColorGroup", "name": name})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_add_color_group(group_name: str) -> str:
    """Create a new color group.

    Args:
        group_name: Unique name for the color group
    """
    try:
        conn, project = _get_project()
        group = project.AddColorGroup(group_name)
        if group is None:
            return _err(f"Failed to create color group '{group_name}'. Name may already exist.")
        gid = conn.register(group, "ColorGroup", composite_key=f"colorgroup:{group_name}")
        return _ok({"id": gid, "type": "ColorGroup", "name": group_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_delete_color_group(color_group_id: str) -> str:
    """Delete a color group. Clips in the group will be set to ungrouped.

    Args:
        color_group_id: ID of the color group to delete
    """
    try:
        conn, project = _get_project()
        group = conn.get(color_group_id, "ColorGroup")
        result = project.DeleteColorGroup(group)
        if result:
            conn.remove(color_group_id)
            return _ok("Color group deleted")
        return _err("Failed to delete color group")
    except Exception as e:
        return _err(str(e))
