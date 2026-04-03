"""Tools for the MediaStorage object.

Covers: volume listing, folder/file browsing, importing media into the media pool,
adding clip mattes and timeline mattes.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.models import MediaStorageItemInfo

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_ms():
    conn = get_connection()
    return conn, conn.get_media_storage()


@mcp.tool()
def media_storage_get_mounted_volume_list() -> str:
    """Get list of mounted volume paths displayed in Resolve's Media Storage."""
    try:
        _, ms = _get_ms()
        return _ok(ms.GetMountedVolumeList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_storage_get_sub_folder_list(folder_path: str) -> str:
    """Get subfolders within an absolute folder path.

    Args:
        folder_path: Absolute path to the folder
    """
    try:
        _, ms = _get_ms()
        return _ok(ms.GetSubFolderList(folder_path))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_storage_get_file_list(folder_path: str) -> str:
    """Get media and file listings in an absolute folder path.

    Note: media listings may be logically consolidated entries (e.g., image sequences).

    Args:
        folder_path: Absolute path to the folder
    """
    try:
        _, ms = _get_ms()
        return _ok(ms.GetFileList(folder_path))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_storage_reveal_in_storage(path: str) -> str:
    """Expand and display a file or folder path in Resolve's Media Storage panel.

    Args:
        path: Absolute file or folder path to reveal
    """
    try:
        _, ms = _get_ms()
        result = ms.RevealInStorage(path)
        if result:
            return _ok(f"Revealed '{path}' in Media Storage")
        return _err(f"Failed to reveal '{path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_storage_add_item_list_to_media_pool(items: list[str | dict]) -> str:
    """Add files/folders from Media Storage into the current Media Pool folder.

    Args:
        items: List of items to add. Each item can be:
            - A string file/folder path
            - A dict with keys: 'media' (path), 'startFrame' (int), 'endFrame' (int)

    Returns list of created MediaPoolItem references.
    """
    try:
        conn, ms = _get_ms()

        if items and isinstance(items[0], dict):
            parsed = []
            for item in items:
                info = MediaStorageItemInfo(**item)
                d = {"media": info.media}
                if info.startFrame is not None:
                    d["startFrame"] = info.startFrame
                if info.endFrame is not None:
                    d["endFrame"] = info.endFrame
                parsed.append(d)
            clips = ms.AddItemListToMediaPool(parsed)
        else:
            clips = ms.AddItemListToMediaPool(items)

        if clips is None:
            return _err("Failed to add items to media pool")

        result = []
        for clip in clips:
            cid = conn.register(clip, "MediaPoolItem")
            result.append({
                "id": cid,
                "type": "MediaPoolItem",
                "name": clip.GetName(),
            })
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_storage_add_clip_mattes_to_media_pool(
    media_pool_item_id: str,
    paths: list[str],
    stereo_eye: str | None = None,
) -> str:
    """Add media files as mattes for a specific MediaPoolItem.

    Args:
        media_pool_item_id: ID of the MediaPoolItem to add mattes to
        paths: List of matte file paths
        stereo_eye: For stereo clips: 'left' or 'right' (optional)
    """
    try:
        conn, ms = _get_ms()
        mpi = conn.get(media_pool_item_id, "MediaPoolItem")
        if stereo_eye:
            result = ms.AddClipMattesToMediaPool(mpi, paths, stereo_eye)
        else:
            result = ms.AddClipMattesToMediaPool(mpi, paths)
        if result:
            return _ok("Clip mattes added")
        return _err("Failed to add clip mattes")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def media_storage_add_timeline_mattes_to_media_pool(paths: list[str]) -> str:
    """Add media files as timeline mattes in the current media pool folder.

    Args:
        paths: List of matte file paths

    Returns list of created MediaPoolItem references.
    """
    try:
        conn, ms = _get_ms()
        clips = ms.AddTimelineMattesToMediaPool(paths)
        if clips is None:
            return _err("Failed to add timeline mattes")
        result = []
        for clip in clips:
            cid = conn.register(clip, "MediaPoolItem")
            result.append({"id": cid, "type": "MediaPoolItem", "name": clip.GetName()})
        return _ok(result)
    except Exception as e:
        return _err(str(e))
