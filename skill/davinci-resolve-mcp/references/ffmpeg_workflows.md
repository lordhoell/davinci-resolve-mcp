# FFmpeg + DaVinci Resolve Workflows

## 1. Silence Removal (Auto Jump-Cut)

Remove silent sections from a timeline, keeping only speech/audio segments.

### Steps
1. Get clip file path and source time range from Resolve
2. Check audio streams: `ffmpeg -i <file> 2>&1 | grep Stream.*Audio`
3. Run silence detection on the target audio stream:
   ```bash
   ffmpeg -t <clip_duration_seconds> -i <file> -map 0:<stream_index> -af silencedetect=noise=-30dB:d=1.0 -vn -f null -
   ```
4. Parse output for `silence_start` and `silence_end` pairs
5. Merge overlapping/adjacent silence periods (within 0.05s gap)
6. Compute speech segments as the complement (gaps between silences)
7. Filter out segments shorter than 0.3s
8. Convert timestamps to source frames: `frame = int(seconds * fps)`
9. Create new timeline and append speech segments via `media_pool_append_to_timeline`

### Parameters
- `noise=-30dB` — threshold below which audio is considered silent
- `d=1.0` — minimum silence duration in seconds to detect
- Adjust noise threshold: `-25dB` (stricter, keeps more), `-35dB` (looser, removes more)

## 2. Audio Fingerprint Matching

Find specific sounds (jingles, sound effects, game audio cues) in a long recording.

### Steps
1. Extract game/target audio as mono 16kHz WAV:
   ```bash
   ffmpeg -i <source> -map 0:<stream_index> -ac 1 -ar 16000 game_audio.wav
   ```
2. Convert reference samples to same format:
   ```bash
   ffmpeg -i sample.wav -ac 1 -ar 16000 sample_mono.wav
   ```
3. Run FFT cross-correlation in Python (see find_sounds_fast.py):
   - Load both as numpy arrays via wave module
   - FFT-based normalized cross-correlation
   - Peak detection above threshold
   - Group nearby peaks (within 2 seconds)
4. Filter by confidence score
5. Build ±30s windows around each match
6. Merge overlapping windows
7. Create timeline with segments in chronological order

### Confidence Thresholds
- `0.7+` — high confidence, fewer false positives (recommended start)
- `0.6` — moderate, good balance
- `0.45` — catches more but many false positives with game music
- Short/common sounds (pipes, clicks) produce more false positives than distinctive sounds (level clear jingles)

### Performance
- 16kHz mono extraction: ~6 seconds for 2.5 hours
- Cross-correlation: ~20 seconds per sample against 2.5 hours
- Total for 4 samples: ~78 seconds

### Python Pattern (find_sounds_fast.py)
```python
from numpy.fft import fft, ifft
# FFT cross-correlation
fft_size = next_power_of_2(len(game) + len(sample) - 1)
corr_raw = real(ifft(fft(game, fft_size) * fft(sample_norm[::-1], fft_size)))
# Vectorized normalization using cumsum trick for local energy
# Peak detection and grouping
```

## 3. Volume Spike Detection

Find moments where audio exceeds a threshold (e.g., streamer yelling = hype moments).

### Steps
1. Extract voice audio stream as WAV
2. Use ffmpeg loudness detection or compute RMS in numpy
3. Find timestamps where volume exceeds threshold
4. Build windows around spikes
5. Create review timeline

### FFmpeg approach
```bash
ffmpeg -i <file> -map 0:<voice_stream> -af astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level -f null -
```

## Common Patterns

### Multi-stream MKV files
Stream recordings often have 5+ audio tracks:
- Stream 0:1 = microphone/voice
- Stream 0:2 = game audio
- Stream 0:3 = Discord/comms
- Stream 0:4-5 = other sources

Always check streams first and map to the correct one.

### Source vs Timeline frames
- Source files may be much longer than the timeline clip
- Use `timeline_item_get_source_start_time` / `timeline_item_get_source_end_time` to get the used range
- FFmpeg timestamps are source-relative (0-based from file start)
- `startFrame` in clip_infos = source frame, not timeline frame

### Batch appending
- `media_pool_append_to_timeline` works best with up to 50 clip_infos per call
- For large segment counts, batch into groups of 50
- All segments append sequentially to the current timeline
