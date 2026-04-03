"""Connection manager and object registry for DaVinci Resolve."""

import sys
import os
import logging

logger = logging.getLogger(__name__)


def _load_dynamic(module_name: str, file_path: str):
    """Load a native extension module from a specific file path."""
    import importlib.machinery
    import importlib.util

    loader = importlib.machinery.ExtensionFileLoader(module_name, file_path)
    spec = importlib.util.spec_from_loader(module_name, loader)
    if spec is None:
        raise ImportError(f"Could not create spec for {module_name} at {file_path}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def _get_resolve_script_module():
    """
    Locate and load DaVinciResolveScript / fusionscript.

    Search order:
    1. Try importing fusionscript directly (works if PYTHONPATH is set)
    2. Check RESOLVE_SCRIPT_LIB environment variable
    3. Fall back to default platform-specific install paths
    """
    # 1. Direct import
    try:
        import fusionscript
        return fusionscript
    except ImportError:
        pass

    # 2. Environment variable
    lib_path = os.getenv("RESOLVE_SCRIPT_LIB")
    if lib_path:
        try:
            return _load_dynamic("fusionscript", lib_path)
        except ImportError:
            logger.warning(f"RESOLVE_SCRIPT_LIB set to '{lib_path}' but failed to load")

    # 3. Default paths per platform
    if sys.platform.startswith("darwin"):
        path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        path = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
    elif sys.platform.startswith("linux"):
        path = "/opt/resolve/libs/Fusion/fusionscript.so"
    else:
        raise ImportError(f"Unsupported platform: {sys.platform}")

    try:
        return _load_dynamic("fusionscript", path)
    except ImportError:
        raise ImportError(
            f"Could not load fusionscript from '{path}'. "
            f"Ensure DaVinci Resolve is installed, or set RESOLVE_SCRIPT_LIB to the correct path."
        )


class ResolveConnection:
    """
    Manages connection to DaVinci Resolve and an object registry.

    The Resolve scripting API returns opaque native objects (Timeline, MediaPoolItem, etc.)
    that cannot be serialized to JSON. The registry maps string IDs to live objects so
    MCP tools can reference them across calls.

    Objects with GetUniqueId(): Project, MediaPool, Timeline, TimelineItem,
                                MediaPoolItem, Folder
    Objects WITHOUT GetUniqueId(): Gallery, GalleryStillAlbum, GalleryStill,
                                   Graph, ColorGroup — use composite keys
    """

    def __init__(self):
        self.resolve = None
        self._script_module = None
        self._registry: dict[str, object] = {}
        self._type_map: dict[str, str] = {}  # id -> type name for debugging

    def connect(self):
        """Connect to a running DaVinci Resolve instance. Raises if not available."""
        self._script_module = _get_resolve_script_module()
        self.resolve = self._script_module.scriptapp("Resolve")
        if self.resolve is None:
            raise ConnectionError(
                "Could not connect to DaVinci Resolve. "
                "Make sure DaVinci Resolve is running before starting the MCP server."
            )
        logger.info(f"Connected to DaVinci Resolve {self.resolve.GetVersionString()}")

    def disconnect(self):
        """Clean up connection state."""
        self._registry.clear()
        self._type_map.clear()
        self.resolve = None
        self._script_module = None

    def ensure_connected(self):
        """Raise if not connected to Resolve."""
        if self.resolve is None:
            raise ConnectionError("Not connected to DaVinci Resolve")

    # ── Object Registry ──────────────────────────────────────────────

    def register(self, obj, type_name: str, composite_key: str | None = None) -> str:
        """
        Register a Resolve API object and return its unique ID.

        For objects with GetUniqueId() (Project, MediaPool, Timeline, TimelineItem,
        MediaPoolItem, Folder), the native ID is used.

        For objects without GetUniqueId() (Gallery, GalleryStillAlbum, GalleryStill,
        Graph, ColorGroup), a composite_key must be provided.

        Args:
            obj: The native Resolve API object
            type_name: Human-readable type (e.g., "Timeline", "MediaPoolItem")
            composite_key: Required for objects that lack GetUniqueId()

        Returns:
            String ID that can be used in subsequent tool calls
        """
        if obj is None:
            raise ValueError(f"Cannot register None as {type_name}")

        if composite_key:
            obj_id = composite_key
        else:
            try:
                obj_id = obj.GetUniqueId()
            except AttributeError:
                raise ValueError(
                    f"{type_name} does not have GetUniqueId() — provide a composite_key"
                )

        self._registry[obj_id] = obj
        self._type_map[obj_id] = type_name
        return obj_id

    def get(self, obj_id: str, expected_type: str | None = None) -> object:
        """
        Look up a registered object by ID.

        Args:
            obj_id: The string ID returned by register()
            expected_type: If provided, validates the stored type matches

        Returns:
            The live Resolve API object

        Raises:
            KeyError: If the ID is not in the registry
            TypeError: If expected_type doesn't match
        """
        if obj_id not in self._registry:
            stored_types = ", ".join(sorted(set(self._type_map.values())))
            raise KeyError(
                f"Object '{obj_id}' not found in cache. "
                f"Currently cached types: [{stored_types}]. "
                f"Use the appropriate 'get' tool to fetch and cache the object first."
            )

        if expected_type and self._type_map.get(obj_id) != expected_type:
            actual = self._type_map.get(obj_id, "unknown")
            raise TypeError(
                f"Expected {expected_type} but '{obj_id}' is a {actual}"
            )

        return self._registry[obj_id]

    def remove(self, obj_id: str):
        """Remove an object from the registry."""
        self._registry.pop(obj_id, None)
        self._type_map.pop(obj_id, None)

    def clear(self):
        """Flush all cached objects. Call when switching projects or reconnecting."""
        count = len(self._registry)
        self._registry.clear()
        self._type_map.clear()
        logger.info(f"Cleared {count} objects from registry")

    def get_cache_info(self) -> dict:
        """Return summary of cached objects for debugging."""
        type_counts: dict[str, int] = {}
        for type_name in self._type_map.values():
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        return {
            "total": len(self._registry),
            "by_type": type_counts,
        }

    # ── Convenience: get commonly needed top-level objects ────────

    def get_project_manager(self):
        """Get the ProjectManager (not cached — always live from resolve)."""
        self.ensure_connected()
        pm = self.resolve.GetProjectManager()
        if pm is None:
            raise RuntimeError("Failed to get ProjectManager from Resolve")
        return pm

    def get_current_project(self):
        """Get the current project (fetched live, then cached)."""
        pm = self.get_project_manager()
        project = pm.GetCurrentProject()
        if project is None:
            raise RuntimeError("No project is currently open in Resolve")
        self.register(project, "Project")
        return project

    def get_media_storage(self):
        """Get the MediaStorage object (not cached — always live)."""
        self.ensure_connected()
        ms = self.resolve.GetMediaStorage()
        if ms is None:
            raise RuntimeError("Failed to get MediaStorage from Resolve")
        return ms
