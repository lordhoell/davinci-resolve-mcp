"""
Enum mappings for DaVinci Resolve constants.

The Resolve API uses constants like resolve.EXPORT_AAF, resolve.KEYFRAME_MODE_ALL, etc.
These are only available at runtime on the resolve object instance.

This module maps human-readable string keys to the attribute names on the resolve object.
Use resolve_enum() to get the actual value at runtime.
"""

# ── Timeline Export Types ─────────────────────────────────────────
# Used by Timeline.Export(fileName, exportType, exportSubtype)

EXPORT_TYPES = {
    "AAF": "EXPORT_AAF",
    "DRT": "EXPORT_DRT",
    "EDL": "EXPORT_EDL",
    "FCP_7_XML": "EXPORT_FCP_7_XML",
    "FCPXML_1_8": "EXPORT_FCPXML_1_8",
    "FCPXML_1_9": "EXPORT_FCPXML_1_9",
    "FCPXML_1_10": "EXPORT_FCPXML_1_10",
    "HDR_10_PROFILE_A": "EXPORT_HDR_10_PROFILE_A",
    "HDR_10_PROFILE_B": "EXPORT_HDR_10_PROFILE_B",
    "TEXT_CSV": "EXPORT_TEXT_CSV",
    "TEXT_TAB": "EXPORT_TEXT_TAB",
    "DOLBY_VISION_VER_2_9": "EXPORT_DOLBY_VISION_VER_2_9",
    "DOLBY_VISION_VER_4_0": "EXPORT_DOLBY_VISION_VER_4_0",
    "DOLBY_VISION_VER_5_1": "EXPORT_DOLBY_VISION_VER_5_1",
    "OTIO": "EXPORT_OTIO",
    "ALE": "EXPORT_ALE",
    "ALE_CDL": "EXPORT_ALE_CDL",
}

EXPORT_SUBTYPES = {
    "NONE": "EXPORT_NONE",
    "AAF_NEW": "EXPORT_AAF_NEW",
    "AAF_EXISTING": "EXPORT_AAF_EXISTING",
    "CDL": "EXPORT_CDL",
    "SDL": "EXPORT_SDL",
    "MISSING_CLIPS": "EXPORT_MISSING_CLIPS",
}

# ── Keyframe Modes ────────────────────────────────────────────────
# Used by Resolve.GetKeyframeMode() / SetKeyframeMode()

KEYFRAME_MODES = {
    "ALL": "KEYFRAME_MODE_ALL",        # 0
    "COLOR": "KEYFRAME_MODE_COLOR",    # 1
    "SIZING": "KEYFRAME_MODE_SIZING",  # 2
}

# ── Cache Modes ───────────────────────────────────────────────────
# Used by Graph.GetNodeCacheMode() / SetNodeCacheMode()

CACHE_MODES = {
    "AUTO": "CACHE_AUTO_ENABLED",      # -1
    "DISABLED": "CACHE_DISABLED",      # 0
    "ENABLED": "CACHE_ENABLED",        # 1
}

# ── Cloud Project Settings ────────────────────────────────────────
# Keys used in {cloudSettings} dict for ProjectManager cloud methods

CLOUD_SETTING_KEYS = {
    "PROJECT_NAME": "CLOUD_SETTING_PROJECT_NAME",
    "PROJECT_MEDIA_PATH": "CLOUD_SETTING_PROJECT_MEDIA_PATH",
    "IS_COLLAB": "CLOUD_SETTING_IS_COLLAB",
    "SYNC_MODE": "CLOUD_SETTING_SYNC_MODE",
    "IS_CAMERA_ACCESS": "CLOUD_SETTING_IS_CAMERA_ACCESS",
}

CLOUD_SYNC_MODES = {
    "NONE": "CLOUD_SYNC_NONE",
    "PROXY_ONLY": "CLOUD_SYNC_PROXY_ONLY",
    "PROXY_AND_ORIG": "CLOUD_SYNC_PROXY_AND_ORIG",
}

# ── Audio Sync Settings ──────────────────────────────────────────
# Used by MediaPool.AutoSyncAudio()

AUDIO_SYNC_SETTING_KEYS = {
    "MODE": "AUDIO_SYNC_MODE",
    "CHANNEL_NUMBER": "AUDIO_SYNC_CHANNEL_NUMBER",
    "RETAIN_EMBEDDED_AUDIO": "AUDIO_SYNC_RETAIN_EMBEDDED_AUDIO",
    "RETAIN_VIDEO_METADATA": "AUDIO_SYNC_RETAIN_VIDEO_METADATA",
}

AUDIO_SYNC_MODES = {
    "WAVEFORM": "AUDIO_SYNC_WAVEFORM",
    "TIMECODE": "AUDIO_SYNC_TIMECODE",
}

AUDIO_SYNC_CHANNELS = {
    "AUTOMATIC": -1,
    "MIX": -2,
}

# ── Auto Caption / Subtitle Settings ─────────────────────────────
# Used by Timeline.CreateSubtitlesFromAudio()

SUBTITLE_SETTING_KEYS = {
    "LANGUAGE": "SUBTITLE_LANGUAGE",
    "CAPTION_PRESET": "SUBTITLE_CAPTION_PRESET",
    "CHARS_PER_LINE": "SUBTITLE_CHARS_PER_LINE",
    "LINE_BREAK": "SUBTITLE_LINE_BREAK",
    "GAP": "SUBTITLE_GAP",
}

AUTO_CAPTION_LANGUAGES = {
    "AUTO": "AUTO_CAPTION_AUTO",
    "DANISH": "AUTO_CAPTION_DANISH",
    "DUTCH": "AUTO_CAPTION_DUTCH",
    "ENGLISH": "AUTO_CAPTION_ENGLISH",
    "FRENCH": "AUTO_CAPTION_FRENCH",
    "GERMAN": "AUTO_CAPTION_GERMAN",
    "ITALIAN": "AUTO_CAPTION_ITALIAN",
    "JAPANESE": "AUTO_CAPTION_JAPANESE",
    "KOREAN": "AUTO_CAPTION_KOREAN",
    "MANDARIN_SIMPLIFIED": "AUTO_CAPTION_MANDARIN_SIMPLIFIED",
    "MANDARIN_TRADITIONAL": "AUTO_CAPTION_MANDARIN_TRADITIONAL",
    "NORWEGIAN": "AUTO_CAPTION_NORWEGIAN",
    "PORTUGUESE": "AUTO_CAPTION_PORTUGUESE",
    "RUSSIAN": "AUTO_CAPTION_RUSSIAN",
    "SPANISH": "AUTO_CAPTION_SPANISH",
    "SWEDISH": "AUTO_CAPTION_SWEDISH",
}

AUTO_CAPTION_PRESETS = {
    "DEFAULT": "AUTO_CAPTION_SUBTITLE_DEFAULT",
    "TELETEXT": "AUTO_CAPTION_TELETEXT",
    "NETFLIX": "AUTO_CAPTION_NETFLIX",
}

AUTO_CAPTION_LINE_BREAKS = {
    "SINGLE": "AUTO_CAPTION_LINE_SINGLE",
    "DOUBLE": "AUTO_CAPTION_LINE_DOUBLE",
}

# ── LUT Export Types ──────────────────────────────────────────────
# Used by TimelineItem.ExportLUT()

EXPORT_LUT_TYPES = {
    "17PT_CUBE": "EXPORT_LUT_17PTCUBE",
    "33PT_CUBE": "EXPORT_LUT_33PTCUBE",
    "65PT_CUBE": "EXPORT_LUT_65PTCUBE",
    "PANASONIC_VLUT": "EXPORT_LUT_PANASONICVLUT",
}

# ── Dolby Vision Analysis Types ──────────────────────────────────
# Used by Timeline.AnalyzeDolbyVision()

DOLBY_VISION_ANALYSIS_TYPES = {
    "BLEND_SHOTS": "DLB_BLEND_SHOTS",
}

# ── TimelineItem Property Enums ───────────────────────────────────
# Used by TimelineItem.SetProperty() / GetProperty()
# These are integer constants, NOT resolve.* attributes

COMPOSITE_MODES = {
    "NORMAL": 0,
    "ADD": 1,
    "SUBTRACT": 2,
    "DIFF": 3,
    "MULTIPLY": 4,
    "SCREEN": 5,
    "OVERLAY": 6,
    "HARDLIGHT": 7,
    "SOFTLIGHT": 8,
    "DARKEN": 9,
    "LIGHTEN": 10,
    "COLOR_DODGE": 11,
    "COLOR_BURN": 12,
    "EXCLUSION": 13,
    "HUE": 14,
    "SATURATE": 15,
    "COLORIZE": 16,
    "LUMA_MASK": 17,
    "DIVIDE": 18,
    "LINEAR_DODGE": 19,
    "LINEAR_BURN": 20,
    "LINEAR_LIGHT": 21,
    "VIVID_LIGHT": 22,
    "PIN_LIGHT": 23,
    "HARD_MIX": 24,
    "LIGHTER_COLOR": 25,
    "DARKER_COLOR": 26,
    "FOREGROUND": 27,
    "ALPHA": 28,
    "INVERTED_ALPHA": 29,
    "LUM": 30,
    "INVERTED_LUM": 31,
}

DYNAMIC_ZOOM_EASE = {
    "LINEAR": 0,
    "IN": 1,
    "OUT": 2,
    "IN_AND_OUT": 3,
}

RETIME_PROCESSES = {
    "USE_PROJECT": 0,
    "NEAREST": 1,
    "FRAME_BLEND": 2,
    "OPTICAL_FLOW": 3,
}

MOTION_ESTIMATION = {
    "USE_PROJECT": 0,
    "STANDARD_FASTER": 1,
    "STANDARD_BETTER": 2,
    "ENHANCED_FASTER": 3,
    "ENHANCED_BETTER": 4,
    "SPEED_WARP_BETTER": 5,
    "SPEED_WARP_FASTER": 6,
}

SCALING_MODES = {
    "USE_PROJECT": 0,
    "CROP": 1,
    "FIT": 2,
    "FILL": 3,
    "STRETCH": 4,
}

RESIZE_FILTERS = {
    "USE_PROJECT": 0,
    "SHARPER": 1,
    "SMOOTHER": 2,
    "BICUBIC": 3,
    "BILINEAR": 4,
    "BESSEL": 5,
    "BOX": 6,
    "CATMULL_ROM": 7,
    "CUBIC": 8,
    "GAUSSIAN": 9,
    "LANCZOS": 10,
    "MITCHELL": 11,
    "NEAREST_NEIGHBOR": 12,
    "QUADRATIC": 13,
    "SINC": 14,
    "LINEAR": 15,
}

CLOUD_SYNC_STATUS = {
    "DEFAULT": -1,
    "DOWNLOAD_IN_QUEUE": 0,
    "DOWNLOAD_IN_PROGRESS": 1,
    "DOWNLOAD_SUCCESS": 2,
    "DOWNLOAD_FAIL": 3,
    "DOWNLOAD_NOT_FOUND": 4,
    "UPLOAD_IN_QUEUE": 5,
    "UPLOAD_IN_PROGRESS": 6,
    "UPLOAD_SUCCESS": 7,
    "UPLOAD_FAIL": 8,
    "UPLOAD_NOT_FOUND": 9,
    "SUCCESS": 10,
}


# ── Runtime Resolution ────────────────────────────────────────────

def resolve_enum(resolve_obj, mapping: dict[str, str], key: str):
    """
    Look up a human-readable enum key and return the actual resolve constant value.

    Args:
        resolve_obj: The live Resolve instance (has attributes like EXPORT_AAF)
        mapping: One of the mappings above (e.g., EXPORT_TYPES)
        key: Human-readable key (e.g., "AAF")

    Returns:
        The integer/constant value from the resolve object

    Raises:
        ValueError: If the key is not found in the mapping
        AttributeError: If the resolve object doesn't have the expected attribute
            (usually means the Resolve version is too old)
    """
    upper_key = key.upper()
    attr_name = mapping.get(upper_key)
    if attr_name is None:
        valid = ", ".join(sorted(mapping.keys()))
        raise ValueError(f"Unknown value '{key}'. Valid options: {valid}")

    try:
        return getattr(resolve_obj, attr_name)
    except AttributeError:
        raise AttributeError(
            f"Resolve does not have attribute '{attr_name}'. "
            f"This may require a newer version of DaVinci Resolve."
        )


def resolve_int_enum(mapping: dict[str, int], key: str | int) -> int:
    """
    Look up an integer enum value. Accepts either a string key or direct int.

    Used for TimelineItem property enums (CompositeMode, RetimeProcess, etc.)
    which are plain integers, not resolve.* attributes.

    Args:
        mapping: One of the int mappings above (e.g., COMPOSITE_MODES)
        key: Human-readable string (e.g., "OVERLAY") or integer value

    Returns:
        The integer constant value
    """
    if isinstance(key, int):
        return key

    upper_key = key.upper()
    value = mapping.get(upper_key)
    if value is None:
        valid = ", ".join(sorted(mapping.keys()))
        raise ValueError(f"Unknown value '{key}'. Valid options: {valid}")
    return value


# ── Fusion Registry Type Masks ──────────────────────────────────
# Used by Fusion.GetRegList(typemask)

FUSION_REG_TYPES = {
    "CT_Tool": 0x01,               # Regular tools
    "CT_Filter": 0x02,             # Filter tools (process input)
    "CT_FilterSource": 0x04,       # Source tools (generate output)
    "CT_ParticleTool": 0x08,       # Particle tools
    "CT_ImageFormat": 0x10,        # Image format handlers
    "CT_Mask": 0x20,               # Mask tools
    "CT_Modifier": 0x40,           # Modifiers (animation, expressions)
    "CT_LUT": 0x80,                # LUTs
    "CT_Event": 0x0200,            # Event scripts
    "CT_View": 0x00100000,         # View types
    "CT_PreviewControl": 0x00200000,
    "CT_GLViewer": 0x01000000,     # GL viewer types
    "CT_3D": 0x10000000,           # 3D tools
}

# ── Fusion Image Depth Constants ────────────────────────────────

FUSION_IMAGE_DEPTHS = {
    1: "uint8",
    2: "uint16",
    3: "float16",
    4: "float32",
}
