# DaVinci Resolve MCP

[![PyPI](https://img.shields.io/pypi/v/davinci-resolve-mcp)](https://pypi.org/project/davinci-resolve-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

An [MCP](https://modelcontextprotocol.io/) server and Claude Code skill that expose the **complete** DaVinci Resolve scripting API — letting any MCP-compatible AI assistant control DaVinci Resolve programmatically.

```
AI Assistant  <-->  MCP Protocol  <-->  This Server  <-->  fusionscript  <-->  DaVinci Resolve
```

## What It Can Do

**440+ tools** covering every aspect of DaVinci Resolve:

| Category | Tools | Examples |
|----------|-------|---------|
| **Project Management** | 25 | Create/load/export projects, manage databases, cloud projects |
| **Timeline Editing** | 59 | Add/remove tracks, insert titles & generators, manage markers, export timelines |
| **Media Pool** | 27 | Import media, create timelines from clips, organize folders, sync audio |
| **Clip Operations** | 80 | Set clip properties, manage Fusion comps, color versions, takes, CDL, stabilize, smart reframe |
| **Color Grading** | 16 | Node graph control, LUT management, grade application, color groups |
| **Rendering** | 15 | Configure render settings, formats/codecs, add render jobs, start/stop renders |
| **Fusion Compositing** | 95 | Add/connect nodes, set inputs, keyframe animation, expressions, render comps |
| **Gallery & Stills** | 14 | Manage still albums, PowerGrade albums, import/export stills |
| **Media Storage** | 7 | Browse volumes, import from disk, manage clip/timeline mattes |
| **Captions & Audio** | 5+ | Generate subtitles from audio, voice isolation, Fairlight presets, transcription |
| **App Control** | 22 | Page navigation, layout presets, version info, keyframe modes |

### Example Prompts

- *"List all my projects"*
- *"Import all .mov files from my Desktop into the media pool"*
- *"Create a new timeline called 'Assembly' and add all clips from the media pool"*
- *"Add a Text+ title to video track 2 at the start of the timeline"*
- *"Set up a render job as ProRes 422 HQ at 4K to my Renders folder"*
- *"Apply the LUT 'Rec709' to node 1 of the current clip"*
- *"Generate subtitles from the audio on the current timeline"*
- *"Build a Fusion comp with a Background, Text, and Merge node"*

## Quick Start

### Prerequisites

- **DaVinci Resolve** or **DaVinci Resolve Studio** (v19.0+) installed and running
- **Python 3.10+**
- The MCP server must run on the **same machine** as DaVinci Resolve

### Install

```bash
pip install davinci-resolve-mcp
```

### Configure Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "davinci-resolve-mcp"
    }
  }
}
```

Or with `uvx` (no install needed):

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "uvx",
      "args": ["davinci-resolve-mcp"]
    }
  }
}
```

### Configure Claude Code

```bash
claude mcp add davinci-resolve -- davinci-resolve-mcp
```

## Claude Code Skill

This repo also includes a **Claude Code skill** that teaches Claude how to effectively use the 440+ MCP tools — including the object registry pattern, correct tool chaining, Fusion node wiring, and common workflow recipes.

### Install the Skill

```bash
claude skill install davinci-resolve-mcp.skill
```

Or copy the `skill/davinci-resolve-mcp/` directory into your Claude Code skills folder.

The skill provides:
- **Object registry guidance** — how to chain parent/child object IDs correctly
- **Workflow recipes** — step-by-step patterns for importing, editing, grading, rendering
- **Fusion reference** — node types, common inputs, connection patterns
- **Render settings reference** — format/codec options and configuration keys

## Architecture

### Object Registry

The Resolve API returns native objects that can't be serialized over MCP. The server maintains an in-memory registry mapping string IDs to live objects:

```
resolve_get_project_manager  -->  project_manager_id
  --> project_manager_get_current_project  -->  project_id
    --> project_get_current_timeline  -->  timeline_id
      --> timeline_get_item_list_in_track  -->  [timeline_item_ids]
```

1. Tools that return Resolve objects register them and return a JSON-safe ID
2. Subsequent tools accept that ID to look up the live object
3. Use `clear_object_cache` if objects become stale (e.g., after switching projects in the Resolve UI)
4. Use `initialize` to reconnect if Resolve was restarted

### Server Structure

```
src/davinci_resolve_mcp/
  server.py              # FastMCP server with lifespan management
  resolve_connection.py  # fusionscript bridge & object registry
  models.py              # Pydantic response models
  constants.py           # Enums and API constants
  tools/
    resolve.py           # App-level tools (22)
    project_manager.py   # Project CRUD & databases (25)
    project.py           # Timeline & render management (43)
    timeline.py          # Track, marker, generator tools (59)
    timeline_item.py     # Clip properties, Fusion, grades (80)
    media_pool.py        # Import, organize, create (27)
    media_pool_item.py   # Metadata, markers, proxy (36)
    media_storage.py     # Volume browsing, import (7)
    gallery.py           # Stills & PowerGrades (14)
    graph.py             # Node graph & LUTs (11)
    color_group.py       # Color group management (5)
    fusion_comp.py       # Fusion composition tools (40)
    fusion_tool.py       # Fusion node tools (20)
    fusion_input.py      # Input connections & expressions (12)
    fusion_output.py     # Output values & cache (8)
    fusion_flow.py       # Node layout & selection (8)
    fusion_spline.py     # Keyframe animation (5)
    fusion_misc.py       # Fonts, registry, image cache (11)
    folder.py            # Folder browsing (8)
    utility.py           # Cache & init (3)
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `RESOLVE_SCRIPT_LIB` | Path to `fusionscript.dll`/`.so` | Auto-detected |
| `RESOLVE_SCRIPT_API` | Path to Resolve scripting modules | Auto-detected |

### Default paths by platform

| Platform | `fusionscript` location |
|----------|------------------------|
| Windows | `C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll` |
| macOS | `/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so` |
| Linux | `/opt/resolve/libs/Fusion/fusionscript.so` |

## API Coverage

Based on the DaVinci Resolve 20.2.2 Scripting API. Works with Resolve 19.0+, but some tools require newer versions:

| Feature | Min Version |
|---------|-------------|
| Voice isolation APIs | 20.1 |
| SetName for clips/items | 20.2 |
| Fairlight presets | 20.2.2 |
| MonitorGrowingFile | 20.0 |
| Graph/ColorGroup objects | 19.0 |

## Limitations

- Must run on the same machine as DaVinci Resolve
- DaVinci Resolve must be running before the server starts
- Some operations require specific pages (e.g., thumbnails need the Color page)
- Some features are Studio-only (scripting access may be limited in the free version)
- Wraps the Scripting API only — no GPU plugin control

## Development

```bash
git clone https://github.com/lordhoell/davinci-resolve-mcp.git
cd davinci-resolve-mcp
pip install -e ".[dev]"
```

### Adding Tools for New API Versions

1. Check `Scripting/CHANGELOG.txt` in the Resolve SDK for new methods
2. Add the tool to the appropriate file in `src/davinci_resolve_mcp/tools/`
3. Add any new enum constants to `constants.py`
4. Add any new models to `models.py`

## License

MIT
