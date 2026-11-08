import json, sys
import numpy as np
import librosa

y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
hop = 32
S = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop)) ** 2
f = librosa.fft_frequencies(sr=sr, n_fft=1024)
fr = sr / hop
def flux(band):
    d = np.maximum(0, np.diff(np.log1p(S[band]), axis=1)).sum(axis=0)
    d = np.concatenate([[0], d]); return d / (d.std() + 1e-9)
kick, snare, full = flux(f < 120), flux((f > 150) & (f < 2500)), flux(f > 0)
a, b = int(12 * fr), int(min(200, len(y) / sr - 6) * fr)

def score(e, bpm, ph):
    per = 60 / bpm * fr
    n = int((b - a) / per) - 1
    idx = np.round(a + ph * fr + per * np.arange(n)).astype(int)
    win = np.stack([e[idx + k] for k in range(-3, 4)])
    return win.max(axis=0).mean()

# Fine tempo + phase search on the full-band onsets
best = (0, 0, 0)
CENTER = float(sys.argv[3]) if len(sys.argv) > 3 else 110.0
for bpm in np.arange(CENTER - 0.1, CENTER + 0.101, 0.005):
    per = 60 / bpm
    for ph in np.arange(0, per, 0.002):
        s = score(full, bpm, ph)
        if s > best[0]: best = (s, bpm, ph)
_, bpm, ph = best
period = 60 / bpm
# Express the phase as the first beat after t=0 in the absolute timeline
first = (a / fr + ph) % period
print(f"tempo {bpm:.3f} BPM, beat period {period*1000:.2f} ms, first beat at {first:.4f}s")

# Downbeat: which beat (mod 4) has the most kick and the least snare
nb = int((len(y) / sr - first) / period)
beats = first + period * np.arange(nb)
def at(e, t):
    i = int(round(t * fr)); return e[max(0, i - 4): i + 5].max()
k4 = [np.mean([at(kick, t) for t in beats[p::4] if 12 < t < len(y) / sr - 6]) for p in range(4)]
s4 = [np.mean([at(snare, t) for t in beats[p::4] if 12 < t < len(y) / sr - 6]) for p in range(4)]
print("kick by beat mod 4:", [round(x, 2) for x in k4], " snare by beat mod 4:", [round(x, 2) for x in s4])
down = int(np.argmax(np.array(k4) - np.array(s4)))
print("bar starts at beat index phase", down)

# Section novelty per bar (MFCC + chroma), to find phrase boundaries
bars = beats[down::4]
mf = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20, hop_length=512)
ch = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=512)
rms = librosa.feature.rms(y=y, hop_length=512)[0]
fb = librosa.time_to_frames(bars, sr=sr, hop_length=512)
feat = np.array([np.concatenate([mf[:, fb[i]:fb[i+1]].mean(1), 3 * ch[:, fb[i]:fb[i+1]].mean(1)]) for i in range(len(fb) - 1)])
feat = (feat - feat.mean(0)) / (feat.std(0) + 1e-9)
nov = np.r_[0, np.linalg.norm(np.diff(feat, axis=0), axis=1)]
loud = np.array([rms[fb[i]:fb[i+1]].mean() for i in range(len(fb) - 1)])
print("\nbar  start   rms    novelty")
for i in range(min(48, len(nov))):
    mark = " <-- change" if nov[i] > np.percentile(nov, 85) else ""
    print(f"{i:3d} {bars[i]:7.3f}  {loud[i]:.3f}  {nov[i]:5.2f}{mark}")
json.dump({"bpm": bpm, "period": period, "first_beat": first, "down_phase": down, "bars": [float(x) for x in bars]}, open(sys.argv[2], "w"))
