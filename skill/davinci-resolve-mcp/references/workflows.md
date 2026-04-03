# DaVinci Resolve MCP Workflows

## Table of Contents
- [Getting Started](#getting-started)
- [Import Media and Build Timeline](#import-media-and-build-timeline)
- [Generate Captions from Audio](#generate-captions-from-audio)
- [Set Up and Run a Render](#set-up-and-run-a-render)
- [Build a Fusion Title from Scratch](#build-a-fusion-title-from-scratch)
- [Style Text in a Fusion Comp](#style-text-in-a-fusion-comp)
- [Batch Add Markers to Timeline](#batch-add-markers-to-timeline)
- [Color Grading with Node Graphs](#color-grading-with-node-graphs)
- [Export Timeline as EDL/XML/AAF](#export-timeline)
- [Manage Gallery Stills](#manage-gallery-stills)

---

## Getting Started

Every session starts by walking the object hierarchy:

```
1. resolve_get_project_manager()              --> pm_id
2. project_manager_get_current_project()      --> project_id
3. project_get_current_timeline(project_id)   --> timeline_id
```

Now use `timeline_id` for all timeline operations.

To get the media pool:
```
4. project_get_media_pool(project_id)         --> media_pool_id
5. media_pool_get_root_folder(media_pool_id)  --> root_folder_id
6. folder_get_clip_list(root_folder_id)       --> [clip_ids...]
```

---

## Import Media and Build Timeline

```
1. resolve_get_media_storage()                               --> ms_id
2. media_storage_get_file_list(ms_id, "/path/to/footage")    --> [file paths]
3. media_storage_add_item_list_to_media_pool(ms_id, paths)   --> [clip_ids]
4. media_pool_create_empty_timeline(mp_id, "My Timeline")    --> timeline_id
5. media_pool_append_to_timeline(mp_id, clip_ids)            --> [item_ids]
```

Or import from a project file:
```
media_pool_import_timeline_from_file(mp_id, "/path/to/file.xml", options)
```

---

## Generate Captions from Audio

```
1. project_get_current_timeline(project_id)   --> timeline_id
2. timeline_create_subtitles_from_audio(
     timeline_id,
     language="ENGLISH",
     caption_preset="DEFAULT",
     chars_per_line=42,
     gap=0
   )
```

Language options: AUTO, ENGLISH, FRENCH, GERMAN, SPANISH, ITALIAN, JAPANESE, KOREAN, MANDARIN_SIMPLIFIED, MANDARIN_TRADITIONAL, PORTUGUESE, RUSSIAN, DANISH, DUTCH, NORWEGIAN, SWEDISH

Caption presets: DEFAULT, TELETEXT, NETFLIX

---

## Set Up and Run a Render

```
1. project_set_render_settings(project_id, settings={
     "TargetDir": "C:/Renders",
     "CustomName": "MyProject_v1",
     "FormatWidth": 1920,
     "FormatHeight": 1080,
     "FrameRate": 24.0,
     "ExportVideo": true,
     "ExportAudio": true,
     "SelectAllFrames": true
   })
2. project_set_current_render_format_and_codec(project_id, "mp4", "H265_NVIDIA")
3. project_add_render_job(project_id)           --> job_id
4. project_start_rendering(project_id)
5. project_get_render_job_status(project_id, job_id)  --> {status, percentage}
```

To render with subtitles burned in, add to settings:
```
"ExportSubtitle": true,
"SubtitleFormat": "BurnIn"
```

Discover available formats/codecs:
```
project_get_render_formats(project_id)  --> {format: extension}
project_get_render_codecs(project_id, "mp4")  --> {description: codec_name}
```

---

## Build a Fusion Title from Scratch

```
 1. timeline_insert_fusion_title_into_timeline(timeline_id, "Text+")  --> item_id
    -- OR create a Fusion comp on an existing clip:
    timeline_item_add_fusion_comp(item_id)

 2. fusion_get_comp_from_timeline_item(item_id, 1)    --> comp_id

 3. comp_lock(comp_id)              -- Pause UI for batch performance
 4. comp_start_undo(comp_id, "Create Lower Third")

 5. comp_add_tool(comp_id, "Background")    --> bg_id
 6. comp_add_tool(comp_id, "TextPlus")      --> text_id
 7. comp_add_tool(comp_id, "Merge")         --> merge_id

 8. tool_connect_input(merge_id, "Background", bg_id)
 9. tool_connect_input(merge_id, "Foreground", text_id)

10. tool_set_input(text_id, "StyledText", "JOHN DOE")
11. tool_set_input(text_id, "Font", "Open Sans")
12. tool_set_input(text_id, "Size", 0.08)
13. tool_set_input(text_id, "Red1", 1.0)
14. tool_set_input(text_id, "Green1", 1.0)
15. tool_set_input(text_id, "Blue1", 1.0)

16. tool_set_input(bg_id, "TopLeftRed", 0.0)
17. tool_set_input(bg_id, "TopLeftGreen", 0.0)
18. tool_set_input(bg_id, "TopLeftBlue", 0.0)
19. tool_set_input(bg_id, "TopLeftAlpha", 0.7)

20. comp_end_undo(comp_id, true)
21. comp_unlock(comp_id)
```

---

## Style Text in a Fusion Comp

Discover what inputs a tool has:
```
tool_get_input_list(text_id)  --> {index: {id, name, data_type}}
```

Common TextPlus inputs:
```
tool_set_input(id, "StyledText", "Hello World")   -- Text content
tool_set_input(id, "Font", "Arial")                -- Font name
tool_set_input(id, "Size", 0.06)                   -- Size (0.0-1.0)
tool_set_input(id, "Red1", 1.0)                    -- Text color R
tool_set_input(id, "Green1", 0.8)                  -- Text color G
tool_set_input(id, "Blue1", 0.2)                   -- Text color B
tool_set_input(id, "Center", {0.5, 0.5})           -- Position (x, y)
tool_set_input(id, "Tracking", 20)                 -- Letter spacing
tool_set_input(id, "LineSpacing", 1.2)             -- Line spacing
```

Animate with keyframes:
```
1. tool_add_modifier(text_id, "Size", "BezierSpline")
2. spline_get_spline_from_input(size_input_id)   --> spline_id
3. spline_set_keyframes(spline_id, {"0": 0.0, "15": 0.06, "90": 0.06, "100": 0.0})
```

---

## Batch Add Markers to Timeline

```
timeline_add_marker(timeline_id, 100, "Red", "Review", "Check this shot", 1)
timeline_add_marker(timeline_id, 250, "Blue", "VFX", "Add explosion", 1)
timeline_add_marker(timeline_id, 500, "Green", "Approved", "", 1)
```

Query markers:
```
timeline_get_markers(timeline_id)  --> {frameId: {color, duration, note, name, customData}}
```

---

## Color Grading with Node Graphs

```
1. timeline_item_get_node_graph(item_id)         --> graph_id
2. graph_get_num_nodes(graph_id)                 --> count
3. graph_set_lut(graph_id, 1, "path/to/lut.cube")
4. graph_set_node_enabled(graph_id, 2, false)    -- Disable node 2
5. graph_get_node_label(graph_id, 1)
6. graph_reset_all_grades(graph_id)
```

Apply a grade from DRX file:
```
graph_apply_grade_from_drx(graph_id, "/path/to/still.drx", 0)
  -- gradeMode: 0=No keyframes, 1=Source Timecode, 2=Start Frames
```

---

## Export Timeline

```
timeline_export(timeline_id, "/path/to/output.xml", "FCP_7_XML", "NONE")
```

Export types: AAF, DRT, EDL, FCP_7_XML, FCPXML_1_8, FCPXML_1_9, FCPXML_1_10, HDR_10_PROFILE_A, HDR_10_PROFILE_B, TEXT_CSV, TEXT_TAB, DOLBY_VISION_VER_2_9, DOLBY_VISION_VER_4_0, DOLBY_VISION_VER_5_1, OTIO, ALE, ALE_CDL

Export subtypes (required for AAF/EDL): NONE, AAF_NEW, AAF_EXISTING, CDL, SDL, MISSING_CLIPS

---

## Manage Gallery Stills

```
1. project_get_gallery(project_id)                    --> gallery_id
2. gallery_get_gallery_still_albums(gallery_id)       --> [album_ids]
3. gallery_get_current_still_album(gallery_id)        --> album_id
4. gallery_still_album_get_stills(album_id)           --> [still_ids]
5. gallery_still_album_export_stills(album_id, still_ids, "/path", "prefix", "png")
```

Grab stills from timeline:
```
timeline_grab_still(timeline_id)       --> still from current frame
timeline_grab_all_stills(timeline_id, 1)  --> stills from first frame of each clip
```
