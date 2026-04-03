# Render Settings Reference

## Table of Contents
- [Render Settings Keys](#render-settings-keys)
- [Export Types](#export-types)
- [Export Subtypes](#export-subtypes)
- [Auto Caption Settings](#auto-caption-settings)
- [Timeline Item Properties](#timeline-item-properties)
- [Cloud Project Settings](#cloud-project-settings)

---

## Render Settings Keys

Pass to `project_set_render_settings(project_id, settings={...})`:

| Key | Type | Description |
|-----|------|-------------|
| `SelectAllFrames` | bool | When True, MarkIn/MarkOut are ignored |
| `MarkIn` | int | Start frame |
| `MarkOut` | int | End frame |
| `TargetDir` | string | Output directory path |
| `CustomName` | string | Output filename |
| `UniqueFilenameStyle` | int | 0=Prefix, 1=Suffix |
| `ExportVideo` | bool | Include video |
| `ExportAudio` | bool | Include audio |
| `FormatWidth` | int | Output width |
| `FormatHeight` | int | Output height |
| `FrameRate` | float | e.g., 23.976, 24, 29.97, 30, 60 |
| `PixelAspectRatio` | string | "16_9", "4_3" (SD) or "square", "cinemascope" |
| `VideoQuality` | int/string | 0=auto, 1-MAX=bitrate, or "Least"/"Low"/"Medium"/"High"/"Best" |
| `AudioCodec` | string | e.g., "aac" |
| `AudioBitDepth` | int | Audio bit depth |
| `AudioSampleRate` | int | Audio sample rate |
| `ColorSpaceTag` | string | e.g., "Same as Project", "AstroDesign" |
| `GammaTag` | string | e.g., "Same as Project", "ACEScct" |
| `ExportAlpha` | bool | Include alpha channel |
| `EncodingProfile` | string | e.g., "Main10" (H.264/H.265 only) |
| `MultiPassEncode` | bool | Multi-pass (H.264 only) |
| `AlphaMode` | int | 0=Premultiplied, 1=Straight (if ExportAlpha) |
| `NetworkOptimization` | bool | QuickTime/MP4 only |
| `ClipStartFrame` | int | Custom clip start frame number |
| `TimelineStartTimecode` | string | e.g., "01:00:00:00" |
| `ReplaceExistingFilesInPlace` | bool | Overwrite existing files |
| `ExportSubtitle` | bool | Include subtitles |
| `SubtitleFormat` | string | "BurnIn", "EmbeddedCaptions", "SeparateFile" |

---

## Export Types

For `timeline_export(timeline_id, filename, export_type, export_subtype)`:

| Type | Constant |
|------|----------|
| AAF | `AAF` |
| DRT (Resolve timeline) | `DRT` |
| EDL | `EDL` |
| FCP 7 XML | `FCP_7_XML` |
| FCPXML 1.8 | `FCPXML_1_8` |
| FCPXML 1.9 | `FCPXML_1_9` |
| FCPXML 1.10 | `FCPXML_1_10` |
| HDR10 Profile A | `HDR_10_PROFILE_A` |
| HDR10 Profile B | `HDR_10_PROFILE_B` |
| CSV | `TEXT_CSV` |
| Tab-delimited | `TEXT_TAB` |
| Dolby Vision 2.9 | `DOLBY_VISION_VER_2_9` |
| Dolby Vision 4.0 | `DOLBY_VISION_VER_4_0` |
| Dolby Vision 5.1 | `DOLBY_VISION_VER_5_1` |
| OTIO | `OTIO` |
| ALE | `ALE` |
| ALE CDL | `ALE_CDL` |

## Export Subtypes

Required for AAF and EDL exports:

| Subtype | When to use |
|---------|-------------|
| `NONE` | Default for most export types |
| `AAF_NEW` | AAF export - new composition |
| `AAF_EXISTING` | AAF export - existing composition |
| `CDL` | EDL export with CDL data |
| `SDL` | EDL export with SDL data |
| `MISSING_CLIPS` | EDL export - missing clips list |

---

## Auto Caption Settings

For `timeline_create_subtitles_from_audio(timeline_id, ...)`:

**Languages:** AUTO, DANISH, DUTCH, ENGLISH, FRENCH, GERMAN, ITALIAN, JAPANESE, KOREAN, MANDARIN_SIMPLIFIED, MANDARIN_TRADITIONAL, NORWEGIAN, PORTUGUESE, RUSSIAN, SPANISH, SWEDISH

**Caption presets:** DEFAULT, TELETEXT, NETFLIX

**Line break:** SINGLE, DOUBLE

**Chars per line:** 1-60 (default varies by language/preset)

**Gap:** 0-10 frames between subtitles

---

## Timeline Item Properties

For `timeline_item_set_property(item_id, key, value)`:

**Transform:**
- `Pan`, `Tilt`: -4x width/height to 4x
- `ZoomX`, `ZoomY`: 0.0 to 100.0
- `ZoomGang`: bool
- `RotationAngle`: -360.0 to 360.0
- `AnchorPointX`, `AnchorPointY`: -4x to 4x
- `Pitch`, `Yaw`: -1.5 to 1.5
- `FlipX`, `FlipY`: bool

**Crop:**
- `CropLeft`, `CropRight`, `CropTop`, `CropBottom`: 0.0 to width/height
- `CropSoftness`: -100.0 to 100.0
- `CropRetain`: bool

**Compositing:**
- `Opacity`: 0.0 to 100.0
- `CompositeMode`: NORMAL(0), ADD(1), SUBTRACT(2), MULTIPLY(4), SCREEN(5), OVERLAY(6), SOFTLIGHT(8), etc.

**Retime:**
- `RetimeProcess`: USE_PROJECT(0), NEAREST(1), FRAME_BLEND(2), OPTICAL_FLOW(3)
- `MotionEstimation`: USE_PROJECT(0), STANDARD_FASTER(1), STANDARD_BETTER(2), ENHANCED_FASTER(3), ENHANCED_BETTER(4), SPEED_WARP_BETTER(5), SPEED_WARP_FASTER(6)

**Scaling:**
- `Scaling`: USE_PROJECT(0), CROP(1), FIT(2), FILL(3), STRETCH(4)
- `ResizeFilter`: USE_PROJECT(0), SHARPER(1), SMOOTHER(2), BICUBIC(3), BILINEAR(4), LANCZOS(10), etc.

**Other:**
- `Distortion`: -1.0 to 1.0
- `DynamicZoomEase`: LINEAR(0), IN(1), OUT(2), IN_AND_OUT(3)

---

## Cloud Project Settings

For `project_manager_create_cloud_project`, `load_cloud_project`, etc.:

| Key | Type | Default |
|-----|------|---------|
| `project_name` | string | "" |
| `project_media_path` | string | "" |
| `is_collab` | bool | False |
| `sync_mode` | string | "PROXY_ONLY" |
| `is_camera_access` | bool | False |

Sync modes: NONE, PROXY_ONLY, PROXY_AND_ORIG

## LUT Export Types

For `timeline_item_export_lut(item_id, export_type, path)`:

| Type | Description |
|------|-------------|
| `17PT_CUBE` | 17-point 3D CUBE LUT |
| `33PT_CUBE` | 33-point 3D CUBE LUT |
| `65PT_CUBE` | 65-point 3D CUBE LUT |
| `PANASONIC_VLUT` | Panasonic V-LUT format |
