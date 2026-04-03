"""Tools for the Fusion Composition object.

Covers: tool creation, finding tools, undo/redo, rendering,
comp settings, path mapping, script execution, save/load.

Composition objects are obtained from:
- TimelineItem.GetFusionCompByIndex(idx)
- TimelineItem.GetFusionCompByName(name)
- Fusion.GetCurrentComp()
- Fusion.NewComp()
- Fusion.LoadComp(filename)

Important: Most Fusion comp operations should be wrapped in
StartUndo()/EndUndo() pairs so the user can undo them in the UI.
"""

import json
import logging

from davinci_resolve_mcp.server import mcp, get_connection

logger = logging.getLogger(__name__)


def _ok(result=None) -> str:
    return json.dumps({"success": True, "result": result})


def _err(message: str) -> str:
    return json.dumps({"success": False, "error": message})


def _get_comp(comp_id: str):
    conn = get_connection()
    return conn, conn.get(comp_id, "FusionComp")


# ── Getting a Composition ────────────────────────────────────────

@mcp.tool()
def fusion_get_current_comp() -> str:
    """Get the currently active Fusion composition.

    This works when the Fusion page is active, or when a Fusion comp
    is loaded on a timeline item.

    Returns a FusionComp reference.
    """
    try:
        conn = get_connection()
        fusion = conn.resolve.Fusion()
        if fusion is None:
            return _err("Fusion is not available")
        comp = fusion.GetCurrentComp()
        if comp is None:
            return _err("No active Fusion composition")
        cid = conn.register(comp, "FusionComp", composite_key="fusion:current_comp")
        name = comp.GetAttrs().get("COMPS_Name", "Untitled")
        return _ok({"id": cid, "type": "FusionComp", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def fusion_get_comp_from_timeline_item(
    timeline_item_id: str,
    comp_index: int = 1,
) -> str:
    """Get a Fusion composition from a timeline item by index.

    Args:
        timeline_item_id: TimelineItem ID
        comp_index: 1-based composition index (default 1)

    Returns a FusionComp reference.
    """
    try:
        conn = get_connection()
        item = conn.get(timeline_item_id, "TimelineItem")
        comp = item.GetFusionCompByIndex(comp_index)
        if comp is None:
            return _err(f"No Fusion comp at index {comp_index}")
        cid = conn.register(
            comp, "FusionComp",
            composite_key=f"fusion:comp:{timeline_item_id}:{comp_index}"
        )
        name = comp.GetAttrs().get("COMPS_Name", f"Comp {comp_index}")
        return _ok({"id": cid, "type": "FusionComp", "name": name})
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def fusion_get_comp_by_name(
    timeline_item_id: str,
    comp_name: str,
) -> str:
    """Get a Fusion composition from a timeline item by name.

    Args:
        timeline_item_id: TimelineItem ID
        comp_name: Name of the Fusion composition
    """
    try:
        conn = get_connection()
        item = conn.get(timeline_item_id, "TimelineItem")
        comp = item.GetFusionCompByName(comp_name)
        if comp is None:
            return _err(f"No Fusion comp named '{comp_name}'")
        cid = conn.register(
            comp, "FusionComp",
            composite_key=f"fusion:comp:{timeline_item_id}:{comp_name}"
        )
        return _ok({"id": cid, "type": "FusionComp", "name": comp_name})
    except Exception as e:
        return _err(str(e))


# ── Tool Creation & Discovery ────────────────────────────────────

@mcp.tool()
def comp_add_tool(comp_id: str, tool_id: str, x: int = -32768, y: int = -32768) -> str:
    """Add a tool (node) to the composition.

    This is the primary way to create nodes in Fusion.

    Args:
        comp_id: FusionComp ID
        tool_id: Tool registry ID (e.g., "TextPlus", "Merge", "Background",
                 "Blur", "Transform", "ColorCorrector", "MediaIn", "MediaOut",
                 "BrightnessContrast", "ChannelBooleans", "Resize", etc.)
        x: X position on the flow (default: auto-place)
        y: Y position on the flow (default: auto-place)

    Returns a FusionTool reference.
    """
    try:
        conn, comp = _get_comp(comp_id)
        tool = comp.AddTool(tool_id, -32768 if x == -32768 else x, -32768 if y == -32768 else y)
        if tool is None:
            return _err(f"Failed to add tool '{tool_id}'. Check the registry ID is valid.")
        tid = conn.register(tool, "FusionTool", composite_key=f"ftool:{comp_id}:{tool.Name}")
        return _ok({
            "id": tid,
            "type": "FusionTool",
            "name": tool.Name,
            "tool_type": tool.ID,
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_find_tool(comp_id: str, name: str) -> str:
    """Find a tool in the composition by its unique name.

    Args:
        comp_id: FusionComp ID
        name: Tool name (e.g., "TextPlus1", "Merge1", "Background1")

    Returns a FusionTool reference.
    """
    try:
        conn, comp = _get_comp(comp_id)
        tool = comp.FindTool(name)
        if tool is None:
            return _err(f"No tool named '{name}' in composition")
        tid = conn.register(tool, "FusionTool", composite_key=f"ftool:{comp_id}:{name}")
        return _ok({
            "id": tid,
            "type": "FusionTool",
            "name": tool.Name,
            "tool_type": tool.ID,
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_find_tool_by_type(comp_id: str, tool_type: str, after_tool_id: str | None = None) -> str:
    """Find the first (or next) tool of a given type.

    Args:
        comp_id: FusionComp ID
        tool_type: Tool type ID (e.g., "TextPlus", "Merge", "Blur")
        after_tool_id: Optional FusionTool ID — find the next tool after this one

    Use this to iterate tools of a given type by passing the previously found tool.
    """
    try:
        conn, comp = _get_comp(comp_id)
        prev = None
        if after_tool_id:
            prev = conn.get(after_tool_id, "FusionTool")
        tool = comp.FindToolByID(tool_type, prev)
        if tool is None:
            return _err(f"No more tools of type '{tool_type}'")
        tid = conn.register(tool, "FusionTool", composite_key=f"ftool:{comp_id}:{tool.Name}")
        return _ok({
            "id": tid,
            "type": "FusionTool",
            "name": tool.Name,
            "tool_type": tool.ID,
        })
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_get_tool_list(comp_id: str, selected_only: bool = False, tool_type: str | None = None) -> str:
    """Get a list of tools in the composition.

    Args:
        comp_id: FusionComp ID
        selected_only: If True, only return selected tools
        tool_type: Optional tool type filter (e.g., "TextPlus", "Merge")

    Returns list of FusionTool references.
    """
    try:
        conn, comp = _get_comp(comp_id)
        tools = comp.GetToolList(selected_only, tool_type)
        if tools is None:
            return _ok([])
        result = []
        for key, tool in tools.items():
            tid = conn.register(tool, "FusionTool", composite_key=f"ftool:{comp_id}:{tool.Name}")
            result.append({
                "id": tid,
                "type": "FusionTool",
                "name": tool.Name,
                "tool_type": tool.ID,
            })
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Undo System ──────────────────────────────────────────────────

@mcp.tool()
def comp_start_undo(comp_id: str, name: str) -> str:
    """Begin an undo block. All subsequent changes until EndUndo will be
    grouped as a single undoable action in Fusion's Edit menu.

    Args:
        comp_id: FusionComp ID
        name: Name for the undo action (shown in Edit > Undo menu)

    Always pair with comp_end_undo(). Failing to call EndUndo will
    leave the undo system in a broken state.
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.StartUndo(name)
        return _ok(f"Undo block '{name}' started")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_end_undo(comp_id: str, keep: bool = True) -> str:
    """End an undo block.

    Args:
        comp_id: FusionComp ID
        keep: If True, keeps the changes. If False, undoes everything
              since StartUndo (useful for cancellation).
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.EndUndo(keep)
        return _ok("Undo block ended" + (" (kept)" if keep else " (discarded)"))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_undo(comp_id: str, count: int = 1) -> str:
    """Undo the last action(s).

    Args:
        comp_id: FusionComp ID
        count: Number of undo steps
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Undo(count)
        return _ok(f"Undid {count} action(s)")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_redo(comp_id: str, count: int = 1) -> str:
    """Redo previously undone action(s).

    Args:
        comp_id: FusionComp ID
        count: Number of redo steps
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Redo(count)
        return _ok(f"Redid {count} action(s)")
    except Exception as e:
        return _err(str(e))


# ── Composition State ────────────────────────────────────────────

@mcp.tool()
def comp_get_attrs(comp_id: str) -> str:
    """Get composition attributes (name, frame range, render state, etc.).

    Args:
        comp_id: FusionComp ID

    Returns dict of attributes including:
    - COMPS_Name: composition name
    - COMPN_CurrentTime: current frame
    - COMPN_GlobalStart / COMPN_GlobalEnd: global frame range
    - COMPN_RenderStart / COMPN_RenderEnd: render range
    - COMPB_HiQ: high quality mode
    - COMPB_Proxy: proxy mode
    - COMPB_Rendering: is rendering
    """
    try:
        _, comp = _get_comp(comp_id)
        attrs = comp.GetAttrs()
        return _ok(attrs)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_set_active_tool(comp_id: str, tool_id: str | None = None) -> str:
    """Set the active (selected) tool in the composition.

    Args:
        comp_id: FusionComp ID
        tool_id: FusionTool ID to make active, or None to deselect all
    """
    try:
        conn, comp = _get_comp(comp_id)
        if tool_id:
            tool = conn.get(tool_id, "FusionTool")
            comp.SetActiveTool(tool)
        else:
            comp.SetActiveTool()
        return _ok("Active tool set")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_get_current_time(comp_id: str) -> str:
    """Get the current time (frame number) of the composition.

    Args:
        comp_id: FusionComp ID
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.CurrentTime)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_set_current_time(comp_id: str, time: int) -> str:
    """Set the current time (frame number) of the composition.

    Args:
        comp_id: FusionComp ID
        time: Frame number to jump to
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.CurrentTime = time
        return _ok(f"Current time set to {time}")
    except Exception as e:
        return _err(str(e))


# ── Rendering ────────────────────────────────────────────────────

@mcp.tool()
def comp_render(
    comp_id: str,
    start: int | None = None,
    end: int | None = None,
    wait: bool = True,
    high_quality: bool = True,
    proxy: bool = False,
) -> str:
    """Render the composition.

    Args:
        comp_id: FusionComp ID
        start: Start frame (default: render start)
        end: End frame (default: render end)
        wait: If True, blocks until render completes
        high_quality: Render in high quality mode
        proxy: Render in proxy mode
    """
    try:
        _, comp = _get_comp(comp_id)
        kwargs = {"Wait": wait, "HiQ": high_quality, "Proxy": proxy}
        if start is not None:
            kwargs["Start"] = start
        if end is not None:
            kwargs["End"] = end
        result = comp.Render(kwargs)
        if result:
            return _ok("Render complete" if wait else "Render started")
        return _err("Render failed or was aborted")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_abort_render(comp_id: str) -> str:
    """Abort any in-progress render.

    Args:
        comp_id: FusionComp ID
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.AbortRender()
        return _ok("Render aborted")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_is_rendering(comp_id: str) -> str:
    """Check if the composition is currently rendering.

    Args:
        comp_id: FusionComp ID
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.IsRendering())
    except Exception as e:
        return _err(str(e))


# ── Playback Control ─────────────────────────────────────────────

@mcp.tool()
def comp_play(comp_id: str, reverse: bool = False) -> str:
    """Start playback of the composition.

    Args:
        comp_id: FusionComp ID
        reverse: If True, play in reverse
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Play(reverse)
        return _ok("Playing" + (" (reverse)" if reverse else ""))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_stop(comp_id: str) -> str:
    """Stop playback of the composition.

    Args:
        comp_id: FusionComp ID
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Stop()
        return _ok("Stopped")
    except Exception as e:
        return _err(str(e))


# ── Lock/Unlock ──────────────────────────────────────────────────

@mcp.tool()
def comp_lock(comp_id: str) -> str:
    """Lock the composition to prevent UI updates during batch operations.

    Locking prevents Fusion from updating the display after every change,
    which significantly speeds up batch operations (adding many tools,
    setting many values, etc.).

    Always pair with comp_unlock(). Failing to unlock will freeze the UI.

    Args:
        comp_id: FusionComp ID
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Lock()
        return _ok("Composition locked (UI updates paused)")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_unlock(comp_id: str) -> str:
    """Unlock the composition and resume UI updates.

    Args:
        comp_id: FusionComp ID
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Unlock()
        return _ok("Composition unlocked")
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_is_locked(comp_id: str) -> str:
    """Check if the composition is locked.

    Args:
        comp_id: FusionComp ID
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.IsLocked())
    except Exception as e:
        return _err(str(e))


# ── Copy/Paste & Settings ───────────────────────────────────────

@mcp.tool()
def comp_copy_settings(comp_id: str, tool_ids: list[str] | None = None) -> str:
    """Copy tool settings to the clipboard as a serializable dict.

    Args:
        comp_id: FusionComp ID
        tool_ids: Optional list of FusionTool IDs. If omitted, copies selected tools.

    Returns the settings dict which can be used with comp_paste().
    Useful for duplicating tools or saving tool configurations.
    """
    try:
        conn, comp = _get_comp(comp_id)
        if tool_ids:
            if len(tool_ids) == 1:
                tool = conn.get(tool_ids[0], "FusionTool")
                settings = comp.CopySettings(tool)
            else:
                tools = {i: conn.get(tid, "FusionTool") for i, tid in enumerate(tool_ids)}
                settings = comp.CopySettings(tools)
        else:
            settings = comp.CopySettings()
        if settings is None:
            return _err("No settings to copy")
        return _ok(settings)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_paste(comp_id: str, settings: dict | None = None) -> str:
    """Paste tools from clipboard or from a settings dict.

    Args:
        comp_id: FusionComp ID
        settings: Optional settings dict (from comp_copy_settings).
                  If omitted, pastes from system clipboard.
    """
    try:
        _, comp = _get_comp(comp_id)
        result = comp.Paste(settings) if settings else comp.Paste()
        if result:
            return _ok("Pasted successfully")
        return _err("Paste failed")
    except Exception as e:
        return _err(str(e))


# ── Save/Load ────────────────────────────────────────────────────

@mcp.tool()
def comp_save(comp_id: str, filename: str | None = None) -> str:
    """Save the composition.

    Args:
        comp_id: FusionComp ID
        filename: Optional file path. If omitted, saves to current path.
    """
    try:
        _, comp = _get_comp(comp_id)
        if filename:
            result = comp.Save(filename)
        else:
            result = comp.Save()
        if result:
            return _ok("Composition saved")
        return _err("Failed to save composition")
    except Exception as e:
        return _err(str(e))


# ── Data Storage ─────────────────────────────────────────────────

@mcp.tool()
def comp_get_data(comp_id: str, name: str | None = None) -> str:
    """Get custom persistent data stored on the composition.

    Args:
        comp_id: FusionComp ID
        name: Data key name. If omitted, returns all stored data.
    """
    try:
        _, comp = _get_comp(comp_id)
        result = comp.GetData(name) if name else comp.GetData()
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_set_data(comp_id: str, name: str, value: str | int | float | bool | None) -> str:
    """Set custom persistent data on the composition.

    Data persists with the comp file. Useful for storing metadata
    or state that tools need across sessions.

    Args:
        comp_id: FusionComp ID
        name: Data key name
        value: Data value (string, number, boolean, or None to delete)
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.SetData(name, value)
        return _ok(f"Data '{name}' set")
    except Exception as e:
        return _err(str(e))


# ── Preferences ──────────────────────────────────────────────────

@mcp.tool()
def comp_get_prefs(comp_id: str, pref_name: str | None = None) -> str:
    """Get composition preferences.

    Args:
        comp_id: FusionComp ID
        pref_name: Optional specific preference key. If omitted, returns all prefs.
    """
    try:
        _, comp = _get_comp(comp_id)
        result = comp.GetPrefs(pref_name) if pref_name else comp.GetPrefs()
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_set_prefs(comp_id: str, pref_name: str, value: str | int | float | bool) -> str:
    """Set a composition preference.

    Args:
        comp_id: FusionComp ID
        pref_name: Preference key
        value: Preference value
    """
    try:
        _, comp = _get_comp(comp_id)
        result = comp.SetPrefs(pref_name, value)
        if result:
            return _ok(f"Preference '{pref_name}' set")
        return _err(f"Failed to set preference '{pref_name}'")
    except Exception as e:
        return _err(str(e))


# ── Keyframe Navigation ─────────────────────────────────────────

@mcp.tool()
def comp_get_next_key_time(comp_id: str, time: int | None = None, tool_id: str | None = None) -> str:
    """Get the next keyframe time after the given time.

    Args:
        comp_id: FusionComp ID
        time: Frame to search from (default: current time)
        tool_id: Optional FusionTool ID to limit search to one tool
    """
    try:
        conn, comp = _get_comp(comp_id)
        tool = conn.get(tool_id, "FusionTool") if tool_id else None
        result = comp.GetNextKeyTime(time, tool) if tool else comp.GetNextKeyTime(time)
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_get_prev_key_time(comp_id: str, time: int | None = None, tool_id: str | None = None) -> str:
    """Get the previous keyframe time before the given time.

    Args:
        comp_id: FusionComp ID
        time: Frame to search from (default: current time)
        tool_id: Optional FusionTool ID to limit search to one tool
    """
    try:
        conn, comp = _get_comp(comp_id)
        tool = conn.get(tool_id, "FusionTool") if tool_id else None
        result = comp.GetPrevKeyTime(time, tool) if tool else comp.GetPrevKeyTime(time)
        return _ok(result)
    except Exception as e:
        return _err(str(e))


# ── Frame List ───────────────────────────────────────────────────

@mcp.tool()
def comp_get_frame_list(comp_id: str) -> str:
    """Get the list of frames that are available for rendering.

    Args:
        comp_id: FusionComp ID

    Returns list of frame numbers.
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.GetFrameList())
    except Exception as e:
        return _err(str(e))


# ── Console History ──────────────────────────────────────────────

@mcp.tool()
def comp_get_console_history(comp_id: str) -> str:
    """Get the console output history for the composition.

    Args:
        comp_id: FusionComp ID

    Useful for debugging scripts and checking for errors.
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.GetConsoleHistory())
    except Exception as e:
        return _err(str(e))


# ── Script Execution ─────────────────────────────────────────────

@mcp.tool()
def comp_execute(comp_id: str, script: str) -> str:
    """Execute a script string in the composition's context.

    This runs arbitrary Lua (default) or Python code inside Fusion.
    Prefix with "!Py:" for Python, "!Py3:" for Python 3 specifically.

    Args:
        comp_id: FusionComp ID
        script: Script string to execute

    Example scripts:
    - "print('Hello from Fusion')"
    - "!Py3: comp.AddTool('Background')"
    - "comp:AddTool('Merge')"

    Warning: This executes arbitrary code in Fusion's scripting environment.
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Execute(script)
        return _ok("Script executed")
    except Exception as e:
        return _err(str(e))


# ── Path Mapping ─────────────────────────────────────────────────

@mcp.tool()
def comp_map_path(comp_id: str, path: str) -> str:
    """Resolve a Fusion path map to an absolute filesystem path.

    Fusion uses path maps like "Comp:", "Scripts:", "Temp:" etc.
    This resolves them to real paths.

    Args:
        comp_id: FusionComp ID
        path: Path with Fusion path map prefix (e.g., "Comp:output.png")
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.MapPath(path))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_reverse_map_path(comp_id: str, path: str) -> str:
    """Convert an absolute filesystem path to a Fusion path map string.

    Args:
        comp_id: FusionComp ID
        path: Absolute filesystem path
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.ReverseMapPath(path))
    except Exception as e:
        return _err(str(e))


@mcp.tool()
def comp_get_comp_path_map(comp_id: str) -> str:
    """Get all path maps defined for the composition.

    Args:
        comp_id: FusionComp ID

    Returns dict of path map name -> resolved path.
    """
    try:
        _, comp = _get_comp(comp_id)
        return _ok(comp.GetCompPathMap())
    except Exception as e:
        return _err(str(e))


# ── Loop Mode ────────────────────────────────────────────────────

@mcp.tool()
def comp_set_loop(comp_id: str, enabled: bool) -> str:
    """Enable or disable looped playback.

    Args:
        comp_id: FusionComp ID
        enabled: True to enable loop, False to disable
    """
    try:
        _, comp = _get_comp(comp_id)
        comp.Loop(enabled)
        return _ok(f"Loop {'enabled' if enabled else 'disabled'}")
    except Exception as e:
        return _err(str(e))


# ── Flow View Access ─────────────────────────────────────────────

@mcp.tool()
def comp_get_flow_view(comp_id: str) -> str:
    """Get the FlowView (node graph layout) for the composition.

    Args:
        comp_id: FusionComp ID

    Returns a FusionFlow reference for positioning tools on the canvas.
    """
    try:
        conn, comp = _get_comp(comp_id)
        # FlowView is accessed through the current frame
        frame = comp.CurrentFrame
        if frame is None:
            return _err("No active frame")
        flow = frame.FlowView
        if flow is None:
            return _err("No flow view available")
        fid = conn.register(flow, "FusionFlow", composite_key=f"flow:{comp_id}")
        return _ok({"id": fid, "type": "FusionFlow"})
    except Exception as e:
        return _err(str(e))
