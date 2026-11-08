import sys
import numpy as np
import librosa

y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
hop = 64                                   # 2.9 ms resolution
S = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop)) ** 2
f = librosa.fft_frequencies(sr=sr, n_fft=1024)
def flux(band):
    m = S[band]
    d = np.maximum(0, np.diff(np.log1p(m), axis=1)).sum(axis=0)
    d = np.concatenate([[0], d]); return d / (d.std() + 1e-9)
bands = {"kick <120Hz": f < 120, "snare 150-2.5k": (f > 150) & (f < 2500), "hats >6k": f > 6000, "full": f > 0}
env = {k: flux(v) for k, v in bands.items()}
fr = sr / hop
t0, t1 = 12.0, min(200.0, len(y) / sr - 6)   # steady part of the song
a, b = int(t0 * fr), int(t1 * fr)

def comb(e, bpm, nphase=96):
    per = 60.0 / bpm * fr
    n = int((b - a) / per) - 1
    best = (-1, 0)
    for ph in np.linspace(0, per, nphase, endpoint=False):
        idx = (a + ph + per * np.arange(n)).astype(int)
        # max within +-1 frame to tolerate rounding
        v = np.maximum(np.maximum(e[idx], e[idx - 1]), e[idx + 1]).mean()
        if v > best[0]: best = (v, ph)
    return best

bpms = np.arange(60, 180.01, 0.05)
for name in ["kick <120Hz", "snare 150-2.5k", "hats >6k", "full"]:
    sc = np.array([comb(env[name], x, 48)[0] for x in bpms])
    top = np.argsort(sc)[::-1]
    picks = []
    for i in top:
        if all(abs(bpms[i] - p) > 1.5 for p, _ in picks): picks.append((bpms[i], sc[i]))
        if len(picks) == 5: break
    print(f"{name:15} best BPMs:", ", ".join(f"{p:.2f} ({s:.2f})" for p, s in picks))
