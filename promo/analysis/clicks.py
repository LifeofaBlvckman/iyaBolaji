"""Find short transients (clicks/pops) in the residual left after subtracting the music.
usage: clicks.py resid.wav music_est.wav ref.wav out.json"""
import sys, json, numpy as np, soundfile as sf
from scipy import signal
res, sr = sf.read(sys.argv[1], always_2d=True); mus, _ = sf.read(sys.argv[2], always_2d=True); ref, _ = sf.read(sys.argv[3], always_2d=True)
res = res.mean(1); mus = mus.mean(1); ref = ref.mean(1)
n = 1024; hop = 128
def spec(x):
    f, t, Z = signal.stft(x, sr, nperseg=n, noverlap=n - hop, window="hann"); return f, t, np.abs(Z)
f, t, R = spec(res); _, _, M = spec(mus); _, _, F = spec(ref)
band = (f > 1500) & (f < 16000)
def flux(X):
    L = np.log1p(1e3 * X[band]); d = np.diff(L, axis=1, prepend=L[:, :1]); return np.maximum(d, 0).sum(0)
fr, fm = flux(R), flux(M)
# adaptive threshold: local median over 0.5 s + k * MAD
w = int(0.5 * sr / hop) | 1
med = signal.medfilt(fr, w); mad = signal.medfilt(np.abs(fr - med), w) + 1e-9
z = (fr - med) / (1.4826 * mad)
pk, _ = signal.find_peaks(z, height=5, distance=int(0.04 * sr / hop))
ev = []
env_r = R[band].sum(0); env_m = M[band].sum(0)
for p in pk:
    t0 = t[p]
    # duration: time until the residual band energy falls 20 dB below the peak (within 400 ms)
    seg = env_r[p: p + int(0.4 * sr / hop)]; pkv = seg[:4].max()
    below = np.where(seg < pkv * 0.1)[0]; dur = (below[0] if len(below) else len(seg)) * hop / sr
    sl = slice(p, p + max(2, int(dur * sr / hop)))
    spec_sum = R[:, sl].sum(1)
    cen = float((f * spec_sum).sum() / spec_sum.sum())
    # how much of this frame's high band is residual vs the music estimate
    ratio = 20 * np.log10(env_r[p:p+3].mean() / (env_m[p:p+3].mean() + 1e-12))
    ev.append(dict(t=round(float(t0), 3), z=round(float(z[p]), 1), dur_ms=round(dur * 1000), centroid=round(cen), res_vs_music_db=round(float(ratio), 1), music_flux=round(float(fm[p] / (np.median(fm) + 1e-9)), 1)))
json.dump(ev, open(sys.argv[4], "w"), indent=0)
for e in ev: print(e)
print(len(ev), "events")
