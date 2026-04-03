---
name: davinci-resolve-mcp
description: >
  Control DaVinci Resolve via the davinci-resolve MCP server. Use this skill whenever the user asks
  to work with DaVinci Resolve, video editing, color grading, timelines, media pools, rendering,
  Fusion compositions, or any Resolve-related task. Triggers include: mentions of "Resolve",
  "DaVinci", "timeline", "color grade", "render", "media pool", "Fusion comp", "captions",
  "subtitles", or any video post-production workflow. Covers 440+ MCP tools spanning the full
  Resolve scripting API and Fusion composition API.
---

# DaVinci Resolve MCP Server

Control DaVinci Resolve programmatically through 440+ MCP tools.

```
AI Assistant  <-->  MCP Protocol  <-->  davinci-resolve-mcp  <-->  fusionscript  <-->  DaVinci Resolve
```

## Critical Concepts

### Object Registry

Resolve API objects cannot be serialized. The server maps string IDs to live objects.

**Always follow this chain:**
1. Get a parent object (returns an ID)
2. Pass that ID to child tools
3. If objects go stale, call `clear_object_cache` and re-fetch

```
resolve_get_project_manager  -->  project_manager_id
  --> project_manager_get_current_project  -->  project_id
    --> project_get_current_timeline  -->  timeline_id
      --> timeline_get_item_list_in_track  -->  [timeline_item_ids]
```

### Response Format

All tools return JSON: `{"success": true, "result": ...}` or `{"success": false, "error": "..."}`.

### Page Requirements

Some tools require specific Resolve pages:
- Thumbnails: Color page
- Fairlight audio: Fairlight page
- Fusion comps: Fusion page (or via timeline item bridge)
- Stills/Gallery: Color page

Use `resolve_open_page("color")` etc. to switch first.

## Tool Categories

| Category | Count | Key Tools |
|----------|-------|-----------|
| Resolve | 22 | `resolve_open_page`, `resolve_get_version`, layout/render presets |
| ProjectManager | 25 | `project_manager_get_current_project`, `project_manager_load_project`, database/cloud |
| Project | 43 | `project_get_current_timeline`, `project_set_render_settings`, `project_start_rendering` |
| MediaStorage | 7 | `media_storage_get_file_list`, `media_storage_add_item_list_to_media_pool` |
| MediaPool | 27 | `media_pool_import_media`, `media_pool_create_empty_timeline`, `media_pool_append_to_timeline` |
| Folder | 8 | `folder_get_clip_list`, `folder_get_sub_folder_list` |
| MediaPoolItem | 36 | metadata, markers, flags, clip properties, proxy, transcription |
| Timeline | 59 | tracks, markers, titles, `timeline_create_subtitles_from_audio`, export, scene detection |
| TimelineItem | 80 | properties, Fusion comps, color versions, takes, CDL, grades, stabilization |
| Gallery | 14 | still/PowerGrade albums, import/export stills |
| Graph | 11 | node LUTs, cache modes, grade application |
| ColorGroup | 5 | naming, pre/post clip node graphs |
| Utility | 3 | `clear_object_cache`, `initialize` |
| Fusion Comp | 40 | `comp_add_tool`, `comp_find_tool`, undo/redo, render, lock/unlock |
| Fusion Tool | 20 | `tool_set_input`, `tool_connect_input`, modifiers, settings |
| Fusion Input | 12 | expressions, connections, keyframes |
| Fusion Output | 8 | values, connections, disk cache |
| Fusion Flow | 8 | node positioning, selection, zoom |
| Fusion Spline | 5 | keyframe animation (BezierSpline) |
| Fusion Misc | 11 | `fusion_get_font_list`, `fusion_get_reg_list`, image cache |

## Common Workflows

See [references/workflows.md](references/workflows.md) for step-by-step recipes covering:
- Getting started (project/timeline chain)
- Importing media and building timelines
- Setting up and running renders
- Color grading with node graphs
- Batch operations on clips

See [references/ffmpeg_workflows.md](references/ffmpeg_workflows.md) for audio-driven editing:
- Silence removal (auto jump-cut)
- Audio fingerprint matching (detect game sounds, jingles, effects)
- Volume spike detection (find hype moments)

## Fusion Reference

See [references/fusion_tools.md](references/fusion_tools.md) for Fusion node types, common inputs (TextPlus, Merge, Background), and connection patterns.

## FFmpeg + Resolve Integration

FFmpeg is used for audio analysis BEFORE building timelines in Resolve. The pattern is:
1. Get the source file path via `media_pool_item_get_clip_property(clip_id, "File Path")`
2. Run ffmpeg analysis (silence detection, audio fingerprinting) on the source file
3. Parse results into frame-based segments
4. Build timelines using `media_pool_create_empty_timeline` + `media_pool_append_to_timeline` with `clip_infos`

### Silence Removal
```bash
ffmpeg -t <duration> -i <file> -map 0:<audio_stream> -af silencedetect=noise=-30dB:d=1.0 -vn -f null -
```
- Use `-map 0:<N>` to target a specific audio stream (MKV files often have multiple)
- Use `-t <seconds>` to limit to clip duration (source files may be longer than timeline clips)
- Parse silence_start/silence_end pairs, compute speech segments as complement
- Filter speech segments by minimum duration (0.3s) to avoid micro-clips

### Audio Fingerprint Matching
Use FFT-based normalized cross-correlation (see find_sounds_fast.py pattern):
1. Extract target audio stream as mono 16kHz WAV: `ffmpeg -i <file> -map 0:<N> -ac 1 -ar 16000 <output.wav>`
2. Convert reference samples to same format
3. Run numpy FFT cross-correlation with normalized scoring
4. Filter by confidence threshold (0.7+ recommended for game sounds with background music)
5. Merge overlapping ±padding windows
6. Build timeline from merged segments chronologically

**Performance:** ~78 seconds to scan 2.5 hours of audio against 4 sound samples at 16kHz mono.

### Timeline Assembly from Segments
`media_pool_append_to_timeline` with `clip_infos` is the workhorse:
```json
{"media_pool_item_id": "<id>", "startFrame": 1000, "endFrame": 2000}
```
- Batch up to 50 clip_infos per call for reliability
- Source frames are 0-based from the media file start
- After MCP reconnection, re-fetch media pool items via `media_pool_get_root_folder` → `folder_get_clip_list`

## Important Notes

- Get the project/timeline chain before operating on items
- Use `clear_object_cache` when switching projects via the Resolve UI
- Use `initialize` if Resolve was restarted after the MCP server started
- MKV files often have multiple audio streams; check with `ffmpeg -i <file>` and use `-map 0:<N>` to target the right one
- Get source time ranges via `timeline_item_get_source_start_time` / `timeline_item_get_source_end_time`
- After MCP server reconnection, object cache is cleared — re-fetch objects before using them
- Wrap batch Fusion operations in `comp_lock`/`comp_unlock`
- Wrap undoable Fusion changes in `comp_start_undo`/`comp_end_undo`
- Many Resolve methods return False/None on failure - always check the success field
