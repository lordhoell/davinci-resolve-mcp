import numpy as np
import wave
import json
import time

def load_wav(path):
    with wave.open(path, 'rb') as w:
        frames = w.readframes(w.getnframes())
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        return data, w.getframerate()

def fast_match(game, sample, sr, threshold=0.4):
    """FFT-based normalized cross-correlation - vectorized, no Python loops"""
    from numpy.fft import fft, ifft

    n = len(game)
    m = len(sample)

    # Normalize sample
    sample = sample - np.mean(sample)
    sample_std = np.std(sample)
    if sample_std < 1e-10:
        return []
    sample_norm = sample / sample_std

    # Pad for FFT correlation
    fft_size = 1
    while fft_size < n + m - 1:
        fft_size *= 2

    # FFT cross-correlation
    game_fft = fft(game, fft_size)
    sample_fft = fft(sample_norm[::-1], fft_size)
    corr_raw = np.real(ifft(game_fft * sample_fft))[:n - m + 1]

    # Vectorized local energy computation using cumsum trick
    game_sq_cumsum = np.cumsum(game ** 2)
    game_cumsum = np.cumsum(game)

    # Local sum and sum-of-squares for each window of length m
    local_sq = np.empty(n - m + 1)
    local_sum = np.empty(n - m + 1)
    local_sq[0] = game_sq_cumsum[m - 1]
    local_sum[0] = game_cumsum[m - 1]
    local_sq[1:] = game_sq_cumsum[m:] - game_sq_cumsum[:n - m]
    local_sum[1:] = game_cumsum[m:] - game_cumsum[:n - m]

    # Local std
    local_var = local_sq / m - (local_sum / m) ** 2
    local_var = np.maximum(local_var, 0)
    local_std = np.sqrt(local_var) * m

    # Normalize correlation
    valid = local_std > 1e-10
    ncc = np.zeros(n - m + 1)
    ncc[valid] = corr_raw[valid] / local_std[valid]

    # Find peaks above threshold
    above = np.where(ncc > threshold)[0]
    if len(above) == 0:
        return []

    # Group nearby peaks (within 2 seconds)
    min_gap = sr * 2
    matches = []
    last = -min_gap * 2
    for idx in above:
        if idx - last > min_gap:
            matches.append({
                "time": round(idx / sr, 2),
                "score": round(float(ncc[idx]), 3)
            })
            last = idx

    return matches

base = "C:/Users/patrick/Desktop/DavincciResolveMCP"

print("Loading game audio...")
t0 = time.time()
game, sr = load_wav(f"{base}/game_audio.wav")
print(f"Game audio: {len(game)/sr:.1f}s at {sr}Hz, loaded in {time.time()-t0:.1f}s")

samples = ["GOALTAPE", "checkpoint", "door", "pipe"]
all_matches = {}

for name in samples:
    print(f"\nProcessing {name}...")
    t1 = time.time()
    sample, _ = load_wav(f"{base}/audio/{name}_mono.wav")
    print(f"  Sample: {len(sample)/sr:.2f}s")

    matches = fast_match(game, sample, sr, threshold=0.35)
    elapsed = time.time() - t1

    all_matches[name] = matches
    print(f"  Found {len(matches)} matches in {elapsed:.1f}s")
    for m in matches[:15]:
        mins = int(m['time'] // 60)
        secs = m['time'] % 60
        print(f"    {mins}:{secs:05.2f} (score: {m['score']:.3f})")
    if len(matches) > 15:
        print(f"    ... and {len(matches)-15} more")

total = time.time() - t0
print(f"\nTotal time: {total:.1f}s")

with open(f"{base}/audio_matches.json", "w") as f:
    json.dump(all_matches, f, indent=2)

print(f"Saved to audio_matches.json")

# Summary
total_matches = sum(len(v) for v in all_matches.values())
print(f"\nTotal: {total_matches} sound events found across all 4 samples")
