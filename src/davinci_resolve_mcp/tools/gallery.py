"""Tools for Gallery and GalleryStillAlbum objects.

Covers: still albums, power grade albums, stills management,
labels, import/export.

Note: GalleryStill is an opaque handle with no methods of its own.
It's used as a parameter in GalleryStillAlbum methods.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


# ── Gallery Tools ─────────────────────────────────────────────────

@mcp.tool()
def gallery_get_album_name(gallery_id: str, album_id: str) -> str:
    """Get the name of a gallery still album.

    Args:
        gallery_id: Gallery ID (from project_get_gallery)
        album_id: GalleryStillAlbum ID
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        album = conn.get(album_id, "GalleryStillAlbum")
        return _ok(gallery.GetAlbumName(album))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_set_album_name(gallery_id: str, album_id: str, album_name: str) -> str:
    """Rename a gallery still album.

    Args:
        gallery_id: Gallery ID
        album_id: GalleryStillAlbum ID
        album_name: New name for the album
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        album = conn.get(album_id, "GalleryStillAlbum")
        result = gallery.SetAlbumName(album, album_name)
        if result:
            return _ok(f"Album renamed to '{album_name}'")
        return _err("Failed to rename album")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_get_current_still_album(gallery_id: str) -> str:
    """Get the currently selected still album.

    Args:
        gallery_id: Gallery ID
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        album = gallery.GetCurrentStillAlbum()
        if album is None:
            return _err("No album is currently selected")
        name = gallery.GetAlbumName(album)
        aid = conn.register(album, "GalleryStillAlbum", composite_key=f"album:{name}")
        return _ok({"id": aid, "type": "GalleryStillAlbum", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_set_current_still_album(gallery_id: str, album_id: str) -> str:
    """Set the current still album.

    Args:
        gallery_id: Gallery ID
        album_id: GalleryStillAlbum ID
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        album = conn.get(album_id, "GalleryStillAlbum")
        result = gallery.SetCurrentStillAlbum(album)
        if result:
            return _ok("Current album set")
        return _err("Failed to set current album")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_get_gallery_still_albums(gallery_id: str) -> str:
    """Get all still albums in the gallery.

    Args:
        gallery_id: Gallery ID

    Returns list of GalleryStillAlbum references.
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        albums = gallery.GetGalleryStillAlbums()
        if albums is None:
            return _ok([])
        result = []
        for album in albums:
            name = gallery.GetAlbumName(album)
            aid = conn.register(album, "GalleryStillAlbum", composite_key=f"album:still:{name}")
            result.append({"id": aid, "type": "GalleryStillAlbum", "name": name})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_get_gallery_power_grade_albums(gallery_id: str) -> str:
    """Get all PowerGrade albums in the gallery.

    Args:
        gallery_id: Gallery ID

    Returns list of GalleryStillAlbum references (PowerGrade type).
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        albums = gallery.GetGalleryPowerGradeAlbums()
        if albums is None:
            return _ok([])
        result = []
        for album in albums:
            name = gallery.GetAlbumName(album)
            aid = conn.register(album, "GalleryStillAlbum", composite_key=f"album:pg:{name}")
            result.append({"id": aid, "type": "GalleryStillAlbum", "name": name})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_create_gallery_still_album(gallery_id: str) -> str:
    """Create a new still album in the gallery.

    Args:
        gallery_id: Gallery ID
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        album = gallery.CreateGalleryStillAlbum()
        if album is None:
            return _err("Failed to create still album")
        name = gallery.GetAlbumName(album)
        aid = conn.register(album, "GalleryStillAlbum", composite_key=f"album:still:{name}")
        return _ok({"id": aid, "type": "GalleryStillAlbum", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_create_gallery_power_grade_album(gallery_id: str) -> str:
    """Create a new PowerGrade album in the gallery.

    Args:
        gallery_id: Gallery ID
    """
    try:
        conn = get_connection()
        gallery = conn.get(gallery_id, "Gallery")
        album = gallery.CreateGalleryPowerGradeAlbum()
        if album is None:
            return _err("Failed to create PowerGrade album")
        name = gallery.GetAlbumName(album)
        aid = conn.register(album, "GalleryStillAlbum", composite_key=f"album:pg:{name}")
        return _ok({"id": aid, "type": "GalleryStillAlbum", "name": name})
    except Exception as e:
        return _err(str(e))


# ── GalleryStillAlbum Tools ───────────────────────────────────────

@mcp.tool()
def gallery_still_album_get_stills(album_id: str) -> str:
    """Get all stills in an album.

    Args:
        album_id: GalleryStillAlbum ID

    Returns list of GalleryStill references.
    """
    try:
        conn = get_connection()
        album = conn.get(album_id, "GalleryStillAlbum")
        stills = album.GetStills()
        if stills is None:
            return _ok([])
        result = []
        for i, still in enumerate(stills):
            sid = conn.register(still, "GalleryStill", composite_key=f"still:{album_id}:{i}")
            result.append({"id": sid, "type": "GalleryStill", "index": i})
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_still_album_get_label(album_id: str, still_id: str) -> str:
    """Get the label of a gallery still.

    Args:
        album_id: GalleryStillAlbum ID
        still_id: GalleryStill ID
    """
    try:
        conn = get_connection()
        album = conn.get(album_id, "GalleryStillAlbum")
        still = conn.get(still_id, "GalleryStill")
        return _ok(album.GetLabel(still))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_still_album_set_label(album_id: str, still_id: str, label: str) -> str:
    """Set the label of a gallery still.

    Args:
        album_id: GalleryStillAlbum ID
        still_id: GalleryStill ID
        label: New label text
    """
    try:
        conn = get_connection()
        album = conn.get(album_id, "GalleryStillAlbum")
        still = conn.get(still_id, "GalleryStill")
        result = album.SetLabel(still, label)
        if result:
            return _ok(f"Label set to '{label}'")
        return _err("Failed to set label")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_still_album_import_stills(album_id: str, file_paths: list[str]) -> str:
    """Import stills into an album from file paths.

    Args:
        album_id: GalleryStillAlbum ID
        file_paths: List of image file paths to import
    """
    try:
        conn = get_connection()
        album = conn.get(album_id, "GalleryStillAlbum")
        result = album.ImportStills(file_paths)
        if result:
            return _ok(f"Imported stills from {len(file_paths)} file(s)")
        return _err("Failed to import stills")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_still_album_export_stills(
    album_id: str, still_ids: list[str], folder_path: str, file_prefix: str, format: str,
) -> str:
    """Export stills from an album to files.

    Args:
        album_id: GalleryStillAlbum ID
        still_ids: List of GalleryStill IDs to export
        folder_path: Output directory
        file_prefix: Filename prefix
        format: File format (dpx, cin, tif, jpg, png, ppm, bmp, xpm, drx)
    """
    try:
        conn = get_connection()
        album = conn.get(album_id, "GalleryStillAlbum")
        stills = [conn.get(sid, "GalleryStill") for sid in still_ids]
        result = album.ExportStills(stills, folder_path, file_prefix, format)
        if result:
            return _ok(f"Exported {len(stills)} still(s) to '{folder_path}'")
        return _err("Failed to export stills")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def gallery_still_album_delete_stills(album_id: str, still_ids: list[str]) -> str:
    """Delete stills from an album.

    Args:
        album_id: GalleryStillAlbum ID
        still_ids: List of GalleryStill IDs to delete
    """
    try:
        conn = get_connection()
        album = conn.get(album_id, "GalleryStillAlbum")
        stills = [conn.get(sid, "GalleryStill") for sid in still_ids]
        result = album.DeleteStills(stills)
        if result:
            for sid in still_ids:
                conn.remove(sid)
            return _ok(f"Deleted {len(stills)} still(s)")
        return _err("Failed to delete stills")
    except Exception as e:
        return _err(str(e))
