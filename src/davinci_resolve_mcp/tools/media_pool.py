"""Tools for the MediaPool object.

Covers: folders, clips, timelines, importing/exporting, stereo, audio sync,
clip selection, metadata export.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.models import (
    ClipInfo,
    MediaImportInfo,
    AudioSyncSettings,
)
from davinci_resolve_mcp.constants import (
    AUDIO_SYNC_SETTING_KEYS,
    AUDIO_SYNC_MODES,
    AUDIO_SYNC_CHANNELS,
    resolve_enum,
)

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_mp():
    """Get MediaPool from current project."""
    conn = get_connection()
    project = conn.get_current_project()
    mp = project.GetMediaPool()
    if mp is None:
        raise RuntimeError("Failed to get MediaPool")
    return conn, mp


def _audio_sync_to_resolve_dict(conn, settings: AudioSyncSettings) -> dict:
    """Convert AudioSyncSettings to resolve-native dict."""
    result = {}
    resolve_obj = conn.resolve
    if settings.mode is not None:
        key = getattr(resolve_obj, AUDIO_SYNC_SETTING_KEYS["MODE"])
        result[key] = resolve_enum(resolve_obj, AUDIO_SYNC_MODES, settings.mode)
    if settings.channel_number is not None:
        key = getattr(resolve_obj, AUDIO_SYNC_SETTING_KEYS["CHANNEL_NUMBER"])
        if isinstance(settings.channel_number, str):
            result[key] = AUDIO_SYNC_CHANNELS.get(settings.channel_number.upper(), settings.channel_number)
        else:
            result[key] = settings.channel_number
    if settings.retain_embedded_audio is not None:
        key = getattr(resolve_obj, AUDIO_SYNC_SETTING_KEYS["RETAIN_EMBEDDED_AUDIO"])
        result[key] = settings.retain_embedded_audio
    if settings.retain_video_metadata is not None:
        key = getattr(resolve_obj, AUDIO_SYNC_SETTING_KEYS["RETAIN_VIDEO_METADATA"])
        result[key] = settings.retain_video_metadata
    return result


# ── Folder Navigation ────────────────────────────────────────────

@mcp.tool()
def media_pool_get_root_folder() -> str:
    """Get the root folder of the Media Pool."""
    try:
        conn, mp = _get_mp()
        folder = mp.GetRootFolder()
        if folder is None:
            return _err("Failed to get root folder")
        fid = conn.register(folder, "Folder")
        return _ok({"id": fid, "type": "Folder", "name": folder.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_add_sub_folder(folder_id: str, name: str) -> str:
    """Create a new subfolder under a specified folder.

    Args:
        folder_id: ID of the parent folder
        name: Name for the new subfolder
    """
    try:
        conn, mp = _get_mp()
        parent = conn.get(folder_id, "Folder")
        folder = mp.AddSubFolder(parent, name)
        if folder is None:
            return _err(f"Failed to create subfolder '{name}'")
        fid = conn.register(folder, "Folder")
        return _ok({"id": fid, "type": "Folder", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_refresh_folders() -> str:
    """Update folders in collaboration mode."""
    try:
        _, mp = _get_mp()
        result = mp.RefreshFolders()
        if result:
            return _ok("Folders refreshed")
        return _err("Failed to refresh folders")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_get_current_folder() -> str:
    """Get the currently selected Media Pool folder."""
    try:
        conn, mp = _get_mp()
        folder = mp.GetCurrentFolder()
        if folder is None:
            return _err("No folder is currently selected")
        fid = conn.register(folder, "Folder")
        return _ok({"id": fid, "type": "Folder", "name": folder.GetName()})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_set_current_folder(folder_id: str) -> str:
    """Set the current Media Pool folder.

    Args:
        folder_id: ID of the folder to set as current
    """
    try:
        conn, mp = _get_mp()
        folder = conn.get(folder_id, "Folder")
        result = mp.SetCurrentFolder(folder)
        if result:
            return _ok("Current folder set")
        return _err("Failed to set current folder")
    except Exception as e:
        return _err(str(e))


# ── Timeline Creation ─────────────────────────────────────────────

@mcp.tool()
def media_pool_create_empty_timeline(name: str) -> str:
    """Create a new empty timeline.

    Args:
        name: Name for the new timeline
    """
    try:
        conn, mp = _get_mp()
        timeline = mp.CreateEmptyTimeline(name)
        if timeline is None:
            return _err(f"Failed to create timeline '{name}'")
        tid = conn.register(timeline, "Timeline")
        return _ok({"id": tid, "type": "Timeline", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_append_to_timeline(
    clip_ids: list[str] | None = None,
    clip_infos: list[dict] | None = None,
) -> str:
    """Append clips to the current timeline.

    Use EITHER clip_ids (simple append) OR clip_infos (with frame ranges/track targeting).

    Args:
        clip_ids: List of MediaPoolItem IDs to append
        clip_infos: List of dicts with keys: media_pool_item_id, startFrame, endFrame,
                    mediaType (1=Video, 2=Audio), trackIndex, recordFrame

    Returns list of created TimelineItem references.
    """
    try:
        conn, mp = _get_mp()

        if clip_infos:
            resolved_infos = []
            for info_dict in clip_infos:
                info = ClipInfo(**info_dict)
                mpi = conn.get(info.media_pool_item_id, "MediaPoolItem")
                d = {"mediaPoolItem": mpi}
                if info.startFrame is not None:
                    d["startFrame"] = info.startFrame
                if info.endFrame is not None:
                    d["endFrame"] = info.endFrame
                if info.mediaType is not None:
                    d["mediaType"] = info.mediaType
                if info.trackIndex is not None:
                    d["trackIndex"] = info.trackIndex
                if info.recordFrame is not None:
                    d["recordFrame"] = info.recordFrame
                resolved_infos.append(d)
            items = mp.AppendToTimeline(resolved_infos)
        elif clip_ids:
            clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
            items = mp.AppendToTimeline(clips)
        else:
            return _err("Provide either clip_ids or clip_infos")

        if items is None:
            return _err("Failed to append to timeline")

        result = []
        for item in items:
            iid = conn.register(item, "TimelineItem")
            result.append({"id": iid, "type": "TimelineItem", "name": item.GetName()})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_create_timeline_from_clips(
    name: str,
    clip_ids: list[str] | None = None,
    clip_infos: list[dict] | None = None,
) -> str:
    """Create a new timeline from specified clips.

    Use EITHER clip_ids (simple) OR clip_infos (with frame ranges).

    Args:
        name: Name for the new timeline
        clip_ids: List of MediaPoolItem IDs
        clip_infos: List of dicts with: media_pool_item_id, startFrame, endFrame, recordFrame
    """
    try:
        conn, mp = _get_mp()

        if clip_infos:
            resolved_infos = []
            for info_dict in clip_infos:
                info = ClipInfo(**info_dict)
                mpi = conn.get(info.media_pool_item_id, "MediaPoolItem")
                d = {"mediaPoolItem": mpi}
                if info.startFrame is not None:
                    d["startFrame"] = info.startFrame
                if info.endFrame is not None:
                    d["endFrame"] = info.endFrame
                if info.recordFrame is not None:
                    d["recordFrame"] = info.recordFrame
                resolved_infos.append(d)
            timeline = mp.CreateTimelineFromClips(name, resolved_infos)
        elif clip_ids:
            clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
            timeline = mp.CreateTimelineFromClips(name, clips)
        else:
            return _err("Provide either clip_ids or clip_infos")

        if timeline is None:
            return _err(f"Failed to create timeline '{name}'")
        tid = conn.register(timeline, "Timeline")
        return _ok({"id": tid, "type": "Timeline", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_import_timeline_from_file(
    file_path: str,
    timeline_name: str | None = None,
    import_source_clips: bool | None = None,
    source_clips_path: str | None = None,
    source_clips_folder_ids: list[str] | None = None,
    interlace_processing: bool | None = None,
) -> str:
    """Import a timeline from a file (AAF/EDL/XML/FCPXML/DRT/ADL/OTIO).

    Args:
        file_path: Path to the timeline file
        timeline_name: Name for the timeline (not valid for DRT)
        import_source_clips: Import source clips (default True, not valid for DRT)
        source_clips_path: Path to search for source clips
        source_clips_folder_ids: Media Pool folder IDs to search for clips
        interlace_processing: Enable interlace processing (AAF only)
    """
    try:
        conn, mp = _get_mp()
        options = {}
        if timeline_name is not None:
            options["timelineName"] = timeline_name
        if import_source_clips is not None:
            options["importSourceClips"] = import_source_clips
        if source_clips_path is not None:
            options["sourceClipsPath"] = source_clips_path
        if source_clips_folder_ids is not None:
            folders = [conn.get(fid, "Folder") for fid in source_clips_folder_ids]
            options["sourceClipsFolders"] = folders
        if interlace_processing is not None:
            options["interlaceProcessing"] = interlace_processing

        timeline = mp.ImportTimelineFromFile(file_path, options)
        if timeline is None:
            return _err(f"Failed to import timeline from '{file_path}'")
        tid = conn.register(timeline, "Timeline")
        return _ok({"id": tid, "type": "Timeline", "name": timeline.GetName()})
    except Exception as e:
        return _err(str(e))


# ── Clip/Folder Management ───────────────────────────────────────

@mcp.tool()
def media_pool_delete_timelines(timeline_ids: list[str]) -> str:
    """Delete timelines from the media pool.

    Args:
        timeline_ids: List of Timeline IDs to delete
    """
    try:
        conn, mp = _get_mp()
        timelines = [conn.get(tid, "Timeline") for tid in timeline_ids]
        result = mp.DeleteTimelines(timelines)
        if result:
            for tid in timeline_ids:
                conn.remove(tid)
            return _ok(f"Deleted {len(timeline_ids)} timeline(s)")
        return _err("Failed to delete timelines")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_delete_clips(clip_ids: list[str]) -> str:
    """Delete clips or timeline mattes from the media pool.

    Args:
        clip_ids: List of MediaPoolItem IDs to delete
    """
    try:
        conn, mp = _get_mp()
        clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
        result = mp.DeleteClips(clips)
        if result:
            for cid in clip_ids:
                conn.remove(cid)
            return _ok(f"Deleted {len(clip_ids)} clip(s)")
        return _err("Failed to delete clips")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_delete_folders(folder_ids: list[str]) -> str:
    """Delete subfolders from the media pool.

    Args:
        folder_ids: List of Folder IDs to delete
    """
    try:
        conn, mp = _get_mp()
        folders = [conn.get(fid, "Folder") for fid in folder_ids]
        result = mp.DeleteFolders(folders)
        if result:
            for fid in folder_ids:
                conn.remove(fid)
            return _ok(f"Deleted {len(folder_ids)} folder(s)")
        return _err("Failed to delete folders")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_move_clips(clip_ids: list[str], target_folder_id: str) -> str:
    """Move clips to a target folder.

    Args:
        clip_ids: List of MediaPoolItem IDs to move
        target_folder_id: Destination Folder ID
    """
    try:
        conn, mp = _get_mp()
        clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
        target = conn.get(target_folder_id, "Folder")
        result = mp.MoveClips(clips, target)
        if result:
            return _ok(f"Moved {len(clip_ids)} clip(s)")
        return _err("Failed to move clips")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_move_folders(folder_ids: list[str], target_folder_id: str) -> str:
    """Move folders to a target folder.

    Args:
        folder_ids: List of Folder IDs to move
        target_folder_id: Destination Folder ID
    """
    try:
        conn, mp = _get_mp()
        folders = [conn.get(fid, "Folder") for fid in folder_ids]
        target = conn.get(target_folder_id, "Folder")
        result = mp.MoveFolders(folders, target)
        if result:
            return _ok(f"Moved {len(folder_ids)} folder(s)")
        return _err("Failed to move folders")
    except Exception as e:
        return _err(str(e))


# ── Media Import ──────────────────────────────────────────────────

@mcp.tool()
def media_pool_import_media(items: list[str | dict]) -> str:
    """Import media files into the current Media Pool folder.

    Args:
        items: List of items to import. Each can be:
            - A string file/folder path
            - A dict with: FilePath, StartIndex (optional), EndIndex (optional)
              For image sequences: {"FilePath": "file_%03d.dpx", "StartIndex": 1, "EndIndex": 100}

    Returns list of created MediaPoolItem references.
    """
    try:
        conn, mp = _get_mp()

        if items and isinstance(items[0], dict):
            parsed = [MediaImportInfo(**item).model_dump(exclude_none=True) for item in items]
            clips = mp.ImportMedia(parsed)
        else:
            clips = mp.ImportMedia(items)

        if clips is None:
            return _err("Failed to import media")

        result = []
        for clip in clips:
            cid = conn.register(clip, "MediaPoolItem")
            result.append({"id": cid, "type": "MediaPoolItem", "name": clip.GetName()})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_import_folder_from_file(file_path: str, source_clips_path: str = "") -> str:
    """Import a DRB folder file into the media pool.

    Args:
        file_path: Path to the DRB file
        source_clips_path: Optional path to search for source clips
    """
    try:
        _, mp = _get_mp()
        result = mp.ImportFolderFromFile(file_path, source_clips_path)
        if result:
            return _ok(f"Folder imported from '{file_path}'")
        return _err(f"Failed to import folder from '{file_path}'")
    except Exception as e:
        return _err(str(e))


# ── Mattes ────────────────────────────────────────────────────────

@mcp.tool()
def media_pool_get_clip_matte_list(media_pool_item_id: str) -> str:
    """Get matte file paths for a MediaPoolItem.

    Args:
        media_pool_item_id: ID of the MediaPoolItem
    """
    try:
        conn, mp = _get_mp()
        mpi = conn.get(media_pool_item_id, "MediaPoolItem")
        return _ok(mp.GetClipMatteList(mpi))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_get_timeline_matte_list(folder_id: str) -> str:
    """Get timeline mattes in a folder.

    Args:
        folder_id: ID of the folder to list mattes from
    """
    try:
        conn, mp = _get_mp()
        folder = conn.get(folder_id, "Folder")
        mattes = mp.GetTimelineMatteList(folder)
        if mattes is None:
            return _ok([])
        result = []
        for matte in mattes:
            mid = conn.register(matte, "MediaPoolItem")
            result.append({"id": mid, "type": "MediaPoolItem", "name": matte.GetName()})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_delete_clip_mattes(media_pool_item_id: str, paths: list[str]) -> str:
    """Delete matte files from a MediaPoolItem.

    Args:
        media_pool_item_id: ID of the MediaPoolItem
        paths: List of matte file paths to delete
    """
    try:
        conn, mp = _get_mp()
        mpi = conn.get(media_pool_item_id, "MediaPoolItem")
        result = mp.DeleteClipMattes(mpi, paths)
        if result:
            return _ok("Clip mattes deleted")
        return _err("Failed to delete clip mattes")
    except Exception as e:
        return _err(str(e))


# ── Relinking ─────────────────────────────────────────────────────

@mcp.tool()
def media_pool_relink_clips(clip_ids: list[str], folder_path: str) -> str:
    """Update the media folder location of clips.

    Args:
        clip_ids: List of MediaPoolItem IDs to relink
        folder_path: New folder path for the media files
    """
    try:
        conn, mp = _get_mp()
        clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
        result = mp.RelinkClips(clips, folder_path)
        if result:
            return _ok(f"Relinked {len(clip_ids)} clip(s) to '{folder_path}'")
        return _err("Failed to relink clips")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_unlink_clips(clip_ids: list[str]) -> str:
    """Unlink media pool clips from their source media.

    Args:
        clip_ids: List of MediaPoolItem IDs to unlink
    """
    try:
        conn, mp = _get_mp()
        clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
        result = mp.UnlinkClips(clips)
        if result:
            return _ok(f"Unlinked {len(clip_ids)} clip(s)")
        return _err("Failed to unlink clips")
    except Exception as e:
        return _err(str(e))


# ── Metadata Export ───────────────────────────────────────────────

@mcp.tool()
def media_pool_export_metadata(file_name: str, clip_ids: list[str] | None = None) -> str:
    """Export clip metadata to a CSV file.

    Args:
        file_name: Output CSV file path
        clip_ids: Optional list of MediaPoolItem IDs. If None, exports all clips.
    """
    try:
        conn, mp = _get_mp()
        if clip_ids:
            clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
            result = mp.ExportMetadata(file_name, clips)
        else:
            result = mp.ExportMetadata(file_name)
        if result:
            return _ok(f"Metadata exported to '{file_name}'")
        return _err(f"Failed to export metadata to '{file_name}'")
    except Exception as e:
        return _err(str(e))


# ── Stereo ────────────────────────────────────────────────────────

@mcp.tool()
def media_pool_create_stereo_clip(left_clip_id: str, right_clip_id: str) -> str:
    """Create a 3D stereoscopic clip from two existing clips.

    Replaces the input clips in the media pool.

    Args:
        left_clip_id: MediaPoolItem ID for the left eye
        right_clip_id: MediaPoolItem ID for the right eye
    """
    try:
        conn, mp = _get_mp()
        left = conn.get(left_clip_id, "MediaPoolItem")
        right = conn.get(right_clip_id, "MediaPoolItem")
        stereo = mp.CreateStereoClip(left, right)
        if stereo is None:
            return _err("Failed to create stereo clip")
        sid = conn.register(stereo, "MediaPoolItem")
        return _ok({"id": sid, "type": "MediaPoolItem", "name": stereo.GetName()})
    except Exception as e:
        return _err(str(e))


# ── Audio Sync ────────────────────────────────────────────────────

@mcp.tool()
def media_pool_auto_sync_audio(
    clip_ids: list[str],
    mode: str | None = None,
    channel_number: int | None = None,
    retain_embedded_audio: bool | None = None,
    retain_video_metadata: bool | None = None,
) -> str:
    """Sync audio for a list of MediaPoolItems (minimum 2: at least 1 video + 1 audio).

    Args:
        clip_ids: List of MediaPoolItem IDs (min 2)
        mode: 'WAVEFORM' or 'TIMECODE' (default: TIMECODE)
        channel_number: Channel offset for waveform mode. -1=automatic, -2=mix, or 1-N
        retain_embedded_audio: Keep embedded audio (default False)
        retain_video_metadata: Keep video metadata (default False)
    """
    try:
        conn, mp = _get_mp()
        clips = [conn.get(cid, "MediaPoolItem") for cid in clip_ids]
        settings = AudioSyncSettings(
            mode=mode,
            channel_number=channel_number,
            retain_embedded_audio=retain_embedded_audio,
            retain_video_metadata=retain_video_metadata,
        )
        resolve_settings = _audio_sync_to_resolve_dict(conn, settings)
        result = mp.AutoSyncAudio(clips, resolve_settings)
        if result:
            return _ok("Audio synced successfully")
        return _err("Failed to sync audio")
    except Exception as e:
        return _err(str(e))


# ── Clip Selection ────────────────────────────────────────────────

@mcp.tool()
def media_pool_get_selected_clips() -> str:
    """Get the currently selected MediaPoolItems in the UI."""
    try:
        conn, mp = _get_mp()
        clips = mp.GetSelectedClips()
        if clips is None:
            return _ok([])
        result = []
        for clip in clips:
            cid = conn.register(clip, "MediaPoolItem")
            result.append({"id": cid, "type": "MediaPoolItem", "name": clip.GetName()})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_set_selected_clip(clip_id: str) -> str:
    """Set the selected MediaPoolItem in the UI.

    Args:
        clip_id: ID of the MediaPoolItem to select
    """
    try:
        conn, mp = _get_mp()
        clip = conn.get(clip_id, "MediaPoolItem")
        result = mp.SetSelectedClip(clip)
        if result:
            return _ok("Clip selected")
        return _err("Failed to select clip")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_pool_get_unique_id() -> str:
    """Get the unique ID of the Media Pool."""
    try:
        _, mp = _get_mp()
        return _ok(mp.GetUniqueId())
    except Exception as e:
        return _err(str(e))
