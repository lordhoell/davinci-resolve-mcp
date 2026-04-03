"""Tools for the Media Pool Folder object.

Covers: clip listing, subfolder listing, export, transcription.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


@mcp.tool()
def folder_get_clip_list(folder_id: str) -> str:
    """Get all clips in a Media Pool folder.

    Args:
        folder_id: ID of the folder

    Returns list of MediaPoolItem references.
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        clips = folder.GetClipList()
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
def folder_get_name(folder_id: str) -> str:
    """Get the name of a Media Pool folder.

    Args:
        folder_id: ID of the folder
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        return _ok(folder.GetName())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def folder_get_sub_folder_list(folder_id: str) -> str:
    """Get all subfolders in a Media Pool folder.

    Args:
        folder_id: ID of the folder

    Returns list of Folder references.
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        subfolders = folder.GetSubFolderList()
        if subfolders is None:
            return _ok([])
        result = []
        for sf in subfolders:
            sfid = conn.register(sf, "Folder")
            result.append({"id": sfid, "type": "Folder", "name": sf.GetName()})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def folder_get_is_folder_stale(folder_id: str) -> str:
    """Check if a folder is stale in collaboration mode.

    Args:
        folder_id: ID of the folder
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        return _ok(folder.GetIsFolderStale())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def folder_get_unique_id(folder_id: str) -> str:
    """Get the unique ID of a folder.

    Args:
        folder_id: ID of the folder
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        return _ok(folder.GetUniqueId())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def folder_export(folder_id: str, file_path: str) -> str:
    """Export a Media Pool folder as a DRB file.

    Args:
        folder_id: ID of the folder to export
        file_path: Destination file path
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        result = folder.Export(file_path)
        if result:
            return _ok(f"Folder exported to '{file_path}'")
        return _err(f"Failed to export folder to '{file_path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def folder_transcribe_audio(folder_id: str) -> str:
    """Transcribe audio for all MediaPoolItems in a folder and nested subfolders.

    Args:
        folder_id: ID of the folder
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        result = folder.TranscribeAudio()
        if result:
            return _ok("Audio transcription started")
        return _err("Failed to start audio transcription")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def folder_clear_transcription(folder_id: str) -> str:
    """Clear audio transcription for all MediaPoolItems in a folder and nested subfolders.

    Args:
        folder_id: ID of the folder
    """
    try:
        conn = get_connection()
        folder = conn.get(folder_id, "Folder")
        result = folder.ClearTranscription()
        if result:
            return _ok("Transcriptions cleared")
        return _err("Failed to clear transcriptions")
    except Exception as e:
        return _err(str(e))
