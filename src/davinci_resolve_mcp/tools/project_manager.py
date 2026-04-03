"""Tools for the ProjectManager object.

Covers: project CRUD, database management, folder navigation,
project import/export/archive, cloud projects.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection
from davinci_resolve_mcp.models import CloudSettings
from davinci_resolve_mcp.constants import (
    CLOUD_SETTING_KEYS,
    CLOUD_SYNC_MODES,
    resolve_enum,
)

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_pm():
    """Get the ProjectManager from the current connection."""
    conn = get_connection()
    return conn, conn.get_project_manager()


def _cloud_settings_to_resolve_dict(conn, settings: CloudSettings) -> dict:
    """Convert a CloudSettings model to a resolve-native dict with resolve.CLOUD_SETTING_* keys."""
    result = {}
    resolve_obj = conn.resolve

    if settings.project_name is not None:
        key = getattr(resolve_obj, CLOUD_SETTING_KEYS["PROJECT_NAME"])
        result[key] = settings.project_name

    if settings.project_media_path is not None:
        key = getattr(resolve_obj, CLOUD_SETTING_KEYS["PROJECT_MEDIA_PATH"])
        result[key] = settings.project_media_path

    if settings.is_collab is not None:
        key = getattr(resolve_obj, CLOUD_SETTING_KEYS["IS_COLLAB"])
        result[key] = settings.is_collab

    if settings.sync_mode is not None:
        key = getattr(resolve_obj, CLOUD_SETTING_KEYS["SYNC_MODE"])
        result[key] = resolve_enum(resolve_obj, CLOUD_SYNC_MODES, settings.sync_mode)

    if settings.is_camera_access is not None:
        key = getattr(resolve_obj, CLOUD_SETTING_KEYS["IS_CAMERA_ACCESS"])
        result[key] = settings.is_camera_access

    return result


# ── Project CRUD ──────────────────────────────────────────────────

@mcp.tool()
def project_manager_create_project(project_name: str, media_location_path: str | None = None) -> str:
    """Create a new project.

    Args:
        project_name: Unique name for the new project
        media_location_path: Optional path for project media location (Resolve 20.2.2+)

    Returns the new Project ID on success.
    """
    try:
        conn, pm = _get_pm()
        if media_location_path:
            project = pm.CreateProject(project_name, media_location_path)
        else:
            project = pm.CreateProject(project_name)
        if project is None:
            return _err(f"Failed to create project '{project_name}'. Name may already exist.")
        conn.clear()
        pid = conn.register(project, "Project")
        return _ok({"id": pid, "type": "Project", "name": project_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_delete_project(project_name: str) -> str:
    """Delete a project from the current folder. Cannot delete the currently loaded project.

    Args:
        project_name: Name of the project to delete
    """
    try:
        _, pm = _get_pm()
        result = pm.DeleteProject(project_name)
        if result:
            return _ok(f"Project '{project_name}' deleted")
        return _err(f"Failed to delete '{project_name}'. It may be currently loaded or not found.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_load_project(project_name: str) -> str:
    """Load an existing project by name.

    This switches to a different project. All cached object handles from the
    previous project become invalid and will be cleared.

    Args:
        project_name: Name of the project to load
    """
    try:
        conn, pm = _get_pm()
        project = pm.LoadProject(project_name)
        if project is None:
            return _err(f"Failed to load project '{project_name}'. Check the name is correct.")
        conn.clear()
        pid = conn.register(project, "Project")
        return _ok({"id": pid, "type": "Project", "name": project_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_get_current_project() -> str:
    """Get the currently loaded project.

    Returns the Project ID and name.
    """
    try:
        conn, pm = _get_pm()
        project = pm.GetCurrentProject()
        if project is None:
            return _err("No project is currently loaded")
        pid = conn.register(project, "Project")
        name = project.GetName()
        return _ok({"id": pid, "type": "Project", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_save_project() -> str:
    """Save the currently loaded project."""
    try:
        _, pm = _get_pm()
        result = pm.SaveProject()
        if result:
            return _ok("Project saved")
        return _err("Failed to save project")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_close_project(project_id: str) -> str:
    """Close a project without saving.

    Args:
        project_id: ID of the project to close (from project tools)
    """
    try:
        conn, pm = _get_pm()
        project = conn.get(project_id, "Project")
        result = pm.CloseProject(project)
        if result:
            conn.clear()
            return _ok("Project closed without saving")
        return _err("Failed to close project")
    except Exception as e:
        return _err(str(e))


# ── Folder Navigation (Database folders, not Media Pool) ──────────

@mcp.tool()
def project_manager_get_project_list_in_current_folder() -> str:
    """List all project names in the current database folder."""
    try:
        _, pm = _get_pm()
        projects = pm.GetProjectListInCurrentFolder()
        return _ok(projects)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_get_folder_list_in_current_folder() -> str:
    """List all folder names in the current database folder."""
    try:
        _, pm = _get_pm()
        folders = pm.GetFolderListInCurrentFolder()
        return _ok(folders)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_get_current_folder() -> str:
    """Get the name of the current database folder."""
    try:
        _, pm = _get_pm()
        return _ok(pm.GetCurrentFolder())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_goto_root_folder() -> str:
    """Navigate to the root folder in the database."""
    try:
        _, pm = _get_pm()
        result = pm.GotoRootFolder()
        if result:
            return _ok("Navigated to root folder")
        return _err("Failed to navigate to root folder")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_goto_parent_folder() -> str:
    """Navigate to the parent folder of the current database folder."""
    try:
        _, pm = _get_pm()
        result = pm.GotoParentFolder()
        if result:
            return _ok("Navigated to parent folder")
        return _err("Failed to navigate to parent folder (may already be at root)")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_open_folder(folder_name: str) -> str:
    """Open a subfolder in the current database folder.

    Args:
        folder_name: Name of the folder to open
    """
    try:
        _, pm = _get_pm()
        result = pm.OpenFolder(folder_name)
        if result:
            return _ok(f"Opened folder '{folder_name}'")
        return _err(f"Failed to open folder '{folder_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_create_folder(folder_name: str) -> str:
    """Create a new folder in the current database folder.

    Args:
        folder_name: Unique name for the new folder
    """
    try:
        _, pm = _get_pm()
        result = pm.CreateFolder(folder_name)
        if result:
            return _ok(f"Folder '{folder_name}' created")
        return _err(f"Failed to create folder '{folder_name}'. Name may already exist.")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_delete_folder(folder_name: str) -> str:
    """Delete a folder from the current database folder.

    Args:
        folder_name: Name of the folder to delete
    """
    try:
        _, pm = _get_pm()
        result = pm.DeleteFolder(folder_name)
        if result:
            return _ok(f"Folder '{folder_name}' deleted")
        return _err(f"Failed to delete folder '{folder_name}'")
    except Exception as e:
        return _err(str(e))


# ── Import/Export/Archive ─────────────────────────────────────────

@mcp.tool()
def project_manager_import_project(file_path: str, project_name: str | None = None) -> str:
    """Import a project from a file.

    Args:
        file_path: Path to the project file (.drp)
        project_name: Optional name for the imported project
    """
    try:
        _, pm = _get_pm()
        if project_name:
            result = pm.ImportProject(file_path, project_name)
        else:
            result = pm.ImportProject(file_path)
        if result:
            return _ok(f"Project imported from '{file_path}'")
        return _err(f"Failed to import project from '{file_path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_export_project(
    project_name: str,
    file_path: str,
    with_stills_and_luts: bool = True
) -> str:
    """Export a project to a file.

    Args:
        project_name: Name of the project to export
        file_path: Destination file path
        with_stills_and_luts: Include stills and LUTs in export (default True)
    """
    try:
        _, pm = _get_pm()
        result = pm.ExportProject(project_name, file_path, with_stills_and_luts)
        if result:
            return _ok(f"Project '{project_name}' exported to '{file_path}'")
        return _err(f"Failed to export project '{project_name}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_restore_project(file_path: str, project_name: str | None = None) -> str:
    """Restore a project from an archive file.

    Args:
        file_path: Path to the project archive
        project_name: Optional name for the restored project
    """
    try:
        _, pm = _get_pm()
        if project_name:
            result = pm.RestoreProject(file_path, project_name)
        else:
            result = pm.RestoreProject(file_path)
        if result:
            return _ok(f"Project restored from '{file_path}'")
        return _err(f"Failed to restore project from '{file_path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_archive_project(
    project_name: str,
    file_path: str,
    archive_src_media: bool = True,
    archive_render_cache: bool = True,
    archive_proxy_media: bool = False,
) -> str:
    """Archive a project to a file with optional media inclusion.

    Args:
        project_name: Name of the project to archive
        file_path: Destination file path for the archive
        archive_src_media: Include source media (default True)
        archive_render_cache: Include render cache (default True)
        archive_proxy_media: Include proxy media (default False)
    """
    try:
        _, pm = _get_pm()
        result = pm.ArchiveProject(
            project_name, file_path,
            archive_src_media, archive_render_cache, archive_proxy_media
        )
        if result:
            return _ok(f"Project '{project_name}' archived to '{file_path}'")
        return _err(f"Failed to archive project '{project_name}'")
    except Exception as e:
        return _err(str(e))


# ── Database Management ───────────────────────────────────────────

@mcp.tool()
def project_manager_get_current_database() -> str:
    """Get info about the currently connected database.

    Returns a dict with keys: DbType ('Disk' or 'PostgreSQL'), DbName, and optional IpAddress.
    """
    try:
        _, pm = _get_pm()
        return _ok(pm.GetCurrentDatabase())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_get_database_list() -> str:
    """List all databases configured in DaVinci Resolve.

    Returns a list of dicts with keys: DbType, DbName, and optional IpAddress.
    """
    try:
        _, pm = _get_pm()
        return _ok(pm.GetDatabaseList())
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_set_current_database(
    db_type: str,
    db_name: str,
    ip_address: str | None = None
) -> str:
    """Switch to a different database. Closes any open project.

    Args:
        db_type: 'Disk' or 'PostgreSQL'
        db_name: Database name
        ip_address: PostgreSQL server IP (optional, defaults to '127.0.0.1')
    """
    try:
        conn, pm = _get_pm()
        db_info = {"DbType": db_type, "DbName": db_name}
        if ip_address:
            db_info["IpAddress"] = ip_address
        result = pm.SetCurrentDatabase(db_info)
        if result:
            conn.clear()
            return _ok(f"Switched to database '{db_name}' ({db_type})")
        return _err(f"Failed to switch to database '{db_name}'")
    except Exception as e:
        return _err(str(e))


# ── Cloud Projects ────────────────────────────────────────────────

@mcp.tool()
def project_manager_create_cloud_project(
    project_name: str,
    project_media_path: str,
    is_collab: bool = False,
    sync_mode: str = "PROXY_ONLY",
    is_camera_access: bool = False,
) -> str:
    """Create a new cloud project.

    Args:
        project_name: Name for the cloud project
        project_media_path: Media location path (required)
        is_collab: Enable collaboration mode (default False)
        sync_mode: One of 'NONE', 'PROXY_ONLY', 'PROXY_AND_ORIG' (default 'PROXY_ONLY')
        is_camera_access: Enable camera access (default False)
    """
    try:
        conn, pm = _get_pm()
        settings = CloudSettings(
            project_name=project_name,
            project_media_path=project_media_path,
            is_collab=is_collab,
            sync_mode=sync_mode,
            is_camera_access=is_camera_access,
        )
        resolve_dict = _cloud_settings_to_resolve_dict(conn, settings)
        project = pm.CreateCloudProject(resolve_dict)
        if project is None:
            return _err(f"Failed to create cloud project '{project_name}'")
        conn.clear()
        pid = conn.register(project, "Project")
        return _ok({"id": pid, "type": "Project", "name": project_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_load_cloud_project(
    project_name: str,
    project_media_path: str | None = None,
    sync_mode: str | None = None,
) -> str:
    """Load an existing cloud project.

    On first load, project_media_path and sync_mode are used.
    On subsequent loads, only project_name is honored.

    Args:
        project_name: Name of the cloud project
        project_media_path: Media location path (used on first load only)
        sync_mode: One of 'NONE', 'PROXY_ONLY', 'PROXY_AND_ORIG' (first load only)
    """
    try:
        conn, pm = _get_pm()
        settings = CloudSettings(
            project_name=project_name,
            project_media_path=project_media_path,
            sync_mode=sync_mode,
        )
        resolve_dict = _cloud_settings_to_resolve_dict(conn, settings)
        project = pm.LoadCloudProject(resolve_dict)
        if project is None:
            return _err(f"Failed to load cloud project '{project_name}'")
        conn.clear()
        pid = conn.register(project, "Project")
        return _ok({"id": pid, "type": "Project", "name": project_name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_import_cloud_project(
    file_path: str,
    project_name: str,
    project_media_path: str,
    is_collab: bool = False,
    sync_mode: str = "PROXY_ONLY",
    is_camera_access: bool = False,
) -> str:
    """Import a cloud project from a file.

    Args:
        file_path: Path to the file to import
        project_name: Name for the imported project
        project_media_path: Media location path
        is_collab: Enable collaboration mode
        sync_mode: One of 'NONE', 'PROXY_ONLY', 'PROXY_AND_ORIG'
        is_camera_access: Enable camera access
    """
    try:
        conn, pm = _get_pm()
        settings = CloudSettings(
            project_name=project_name,
            project_media_path=project_media_path,
            is_collab=is_collab,
            sync_mode=sync_mode,
            is_camera_access=is_camera_access,
        )
        resolve_dict = _cloud_settings_to_resolve_dict(conn, settings)
        result = pm.ImportCloudProject(file_path, resolve_dict)
        if result:
            return _ok(f"Cloud project imported from '{file_path}'")
        return _err(f"Failed to import cloud project from '{file_path}'")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def project_manager_restore_cloud_project(
    folder_path: str,
    project_name: str,
    project_media_path: str,
    is_collab: bool = False,
    sync_mode: str = "PROXY_ONLY",
    is_camera_access: bool = False,
) -> str:
    """Restore a cloud project from a folder.

    Args:
        folder_path: Path to the folder to restore from
        project_name: Name for the restored project
        project_media_path: Media location path
        is_collab: Enable collaboration mode
        sync_mode: One of 'NONE', 'PROXY_ONLY', 'PROXY_AND_ORIG'
        is_camera_access: Enable camera access
    """
    try:
        conn, pm = _get_pm()
        settings = CloudSettings(
            project_name=project_name,
            project_media_path=project_media_path,
            is_collab=is_collab,
            sync_mode=sync_mode,
            is_camera_access=is_camera_access,
        )
        resolve_dict = _cloud_settings_to_resolve_dict(conn, settings)
        result = pm.RestoreCloudProject(folder_path, resolve_dict)
        if result:
            return _ok(f"Cloud project restored from '{folder_path}'")
        return _err(f"Failed to restore cloud project from '{folder_path}'")
    except Exception as e:
        return _err(str(e))
