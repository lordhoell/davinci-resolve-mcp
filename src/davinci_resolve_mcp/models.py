"""Pydantic models for complex Resolve API parameters."""

from pydantic import BaseModel, Field


# ── Render Settings ───────────────────────────────────────────────
# Used by Project.SetRenderSettings()

class RenderSettings(BaseModel):
    """Render settings for Project.SetRenderSettings(). All fields optional — only set fields are applied."""

    SelectAllFrames: bool | None = Field(None, description="When True, MarkIn and MarkOut are ignored")
    MarkIn: int | None = Field(None, description="Start frame for render range")
    MarkOut: int | None = Field(None, description="End frame for render range")
    TargetDir: str | None = Field(None, description="Output directory path")
    CustomName: str | None = Field(None, description="Custom output filename")
    UniqueFilenameStyle: int | None = Field(None, description="0=Prefix, 1=Suffix")
    ExportVideo: bool | None = None
    ExportAudio: bool | None = None
    FormatWidth: int | None = None
    FormatHeight: int | None = None
    FrameRate: float | None = Field(None, description="e.g., 23.976, 24, 29.97")
    PixelAspectRatio: str | None = Field(None, description="SD: '16_9' or '4_3'. Other: 'square' or 'cinemascope'")
    VideoQuality: int | str | None = Field(None, description="0=auto, 1-MAX=bitrate, or 'Least'/'Low'/'Medium'/'High'/'Best'")
    AudioCodec: str | None = Field(None, description="e.g., 'aac'")
    AudioBitDepth: int | None = None
    AudioSampleRate: int | None = None
    ColorSpaceTag: str | None = Field(None, description="e.g., 'Same as Project', 'AstroDesign'")
    GammaTag: str | None = Field(None, description="e.g., 'Same as Project', 'ACEScct'")
    ExportAlpha: bool | None = None
    EncodingProfile: str | None = Field(None, description="e.g., 'Main10'. H.264/H.265 only")
    MultiPassEncode: bool | None = Field(None, description="H.264 only")
    AlphaMode: int | None = Field(None, description="0=Premultiplied, 1=Straight. Only if ExportAlpha=True")
    NetworkOptimization: bool | None = Field(None, description="QuickTime and MP4 only")
    ClipStartFrame: int | None = None
    TimelineStartTimecode: str | None = Field(None, description="e.g., '01:00:00:00'")
    ReplaceExistingFilesInPlace: bool | None = None
    ExportSubtitle: bool | None = None
    SubtitleFormat: str | None = Field(None, description="'BurnIn', 'EmbeddedCaptions', or 'SeparateFile'")

    def to_resolve_dict(self) -> dict:
        """Convert to dict suitable for Resolve API, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


# ── Clip Info for AppendToTimeline ────────────────────────────────

class ClipInfo(BaseModel):
    """Clip info for MediaPool.AppendToTimeline([{clipInfo}])."""

    media_pool_item_id: str = Field(description="Registry ID of the MediaPoolItem")
    startFrame: float | int | None = Field(None, description="Start frame in source clip")
    endFrame: float | int | None = Field(None, description="End frame in source clip")
    mediaType: int | None = Field(None, description="1=Video only, 2=Audio only")
    trackIndex: int | None = Field(None, description="Target track index (1-based)")
    recordFrame: float | int | None = Field(None, description="Frame position on timeline")


# ── Import Options ────────────────────────────────────────────────

class TimelineImportOptions(BaseModel):
    """Options for MediaPool.ImportTimelineFromFile()."""

    timelineName: str | None = Field(None, description="Name for the created timeline. Not valid for DRT import")
    importSourceClips: bool | None = Field(None, description="Import source clips. Default True. Not valid for DRT")
    sourceClipsPath: str | None = Field(None, description="Filesystem path to search for source clips")
    sourceClipsFolderIds: list[str] | None = Field(None, description="Media Pool folder IDs to search for clips")
    interlaceProcessing: bool | None = Field(None, description="Enable interlace processing. AAF import only")


class AAFImportOptions(BaseModel):
    """Options for Timeline.ImportIntoTimeline()."""

    autoImportSourceClipsIntoMediaPool: bool | None = Field(True)
    ignoreFileExtensionsWhenMatching: bool | None = Field(False)
    linkToSourceCameraFiles: bool | None = Field(False)
    useSizingInfo: bool | None = Field(False)
    importMultiChannelAudioTracksAsLinkedGroups: bool | None = Field(False)
    insertAdditionalTracks: bool | None = Field(True)
    insertWithOffset: str | None = Field(None, description="Timecode format, e.g., '00:00:00:00'")
    sourceClipsPath: str | None = None
    sourceClipsFolders: str | None = None

    def to_resolve_dict(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}


# ── Auto Caption Settings ────────────────────────────────────────

class AutoCaptionSettings(BaseModel):
    """Settings for Timeline.CreateSubtitlesFromAudio(). All fields optional."""

    language: str | None = Field(None, description="Language ID: AUTO, ENGLISH, FRENCH, GERMAN, SPANISH, etc.")
    caption_preset: str | None = Field(None, description="DEFAULT, TELETEXT, or NETFLIX")
    chars_per_line: int | None = Field(None, ge=1, le=60, description="Characters per line, 1-60")
    line_break: str | None = Field(None, description="SINGLE or DOUBLE")
    gap: int | None = Field(None, ge=0, le=10, description="Gap between subtitles, 0-10")


# ── Voice Isolation State ─────────────────────────────────────────

class VoiceIsolationState(BaseModel):
    """Voice isolation settings for Timeline/TimelineItem."""

    isEnabled: bool
    amount: int = Field(ge=0, le=100, description="Isolation amount, 0-100")


# ── CDL Map ───────────────────────────────────────────────────────

class CDLMap(BaseModel):
    """CDL settings for TimelineItem.SetCDL()."""

    NodeIndex: str = Field(description="1-based node index")
    Slope: str = Field(description="RGB values as 'R G B', e.g., '0.5 0.4 0.2'")
    Offset: str = Field(description="RGB values as 'R G B', e.g., '0.4 0.3 0.2'")
    Power: str = Field(description="RGB values as 'R G B', e.g., '0.6 0.7 0.8'")
    Saturation: str = Field(description="Saturation value, e.g., '0.65'")


# ── Media Import Info ─────────────────────────────────────────────

class MediaStorageItemInfo(BaseModel):
    """Item info for MediaStorage.AddItemListToMediaPool([{itemInfo}])."""

    media: str = Field(description="File path")
    startFrame: int | None = None
    endFrame: int | None = None


class MediaImportInfo(BaseModel):
    """Clip info for MediaPool.ImportMedia([{clipInfo}])."""

    FilePath: str = Field(description="File path pattern, e.g., 'file_%03d.dpx'")
    StartIndex: int | None = None
    EndIndex: int | None = None


# ── Audio Sync Settings ──────────────────────────────────────────

class AudioSyncSettings(BaseModel):
    """Settings for MediaPool.AutoSyncAudio()."""

    mode: str | None = Field(None, description="WAVEFORM or TIMECODE")
    channel_number: int | None = Field(None, description="Channel offset. -1=automatic, -2=mix, or 1-N")
    retain_embedded_audio: bool | None = None
    retain_video_metadata: bool | None = None


# ── Cloud Settings ────────────────────────────────────────────────

class CloudSettings(BaseModel):
    """Settings for ProjectManager cloud project methods."""

    project_name: str | None = None
    project_media_path: str | None = None
    is_collab: bool | None = None
    sync_mode: str | None = Field(None, description="NONE, PROXY_ONLY, or PROXY_AND_ORIG")
    is_camera_access: bool | None = None


# ── Track Options ─────────────────────────────────────────────────

class NewTrackOptions(BaseModel):
    """Options for Timeline.AddTrack() with options dict."""

    audioType: str | None = Field(None, description="Audio format: mono, stereo, 5.1, 7.1, adaptive1-36, etc.")
    index: int | None = Field(None, description="Insert position. 1 <= index <= GetTrackCount(trackType)")


# ── Quick Export Settings ─────────────────────────────────────────

class QuickExportSettings(BaseModel):
    """Settings for Project.RenderWithQuickExport()."""

    TargetDir: str | None = None
    CustomName: str | None = None
    VideoQuality: int | str | None = None
    EnableUpload: bool | None = Field(None, description="Enable direct upload for supported web presets")

    def to_resolve_dict(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}
