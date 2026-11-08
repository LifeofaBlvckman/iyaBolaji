import sys, json, numpy as np, soundfile as sf
from scipy import signal
res, sr = sf.read(sys.argv[1], always_2d=True); mus, _ = sf.read(sys.argv[2], always_2d=True)
resm = res.mean(1); musm = mus.mean(1)
hp = signal.butter(4, 1500, btype="high", fs=sr, output="sos")
rh = signal.sosfiltfilt(hp, resm); mh = signal.sosfiltfilt(hp, musm)
def env(x, ms=1.0):
    n = int(sr * ms / 1000); e = np.sqrt(np.convolve(x ** 2, np.ones(n) / n, mode="same")); return e
er = env(rh); em = env(mh)
db = lambda v: 20 * np.log10(v + 1e-12)
def one(t, search=0.03, win=0.25):
    a = int((t - search) * sr); b = int((t + search) * sr)
    p = a + int(np.argmax(er[a:b])); pk = er[p]
    # onset = first point before peak within 10 ms above -20 dB of the peak
    pre = er[p - int(0.01 * sr): p]; on = p - len(pre) + int(np.argmax(pre > pk * 0.1))
    post = er[p: p + int(win * sr)]
    d10 = np.argmax(post < pk * 10 ** (-10 / 20)) / sr * 1000
    d20 = np.argmax(post < pk * 10 ** (-20 / 20)) / sr * 1000
    seg = resm[on: on + max(int(0.004 * sr), int(d20 / 1000 * sr))] * np.hanning(max(int(0.004 * sr), int(d20 / 1000 * sr)))
    F = np.abs(np.fft.rfft(seg, 8192)); f = np.fft.rfftfreq(8192, 1 / sr)
    m = f > 300; cen = (f[m] * F[m] ** 2).sum() / (F[m] ** 2).sum()
    pkf = f[m][np.argmax(F[m])]
    # band split of energy
    bands = {}
    for lo, hi in [(300, 1500), (1500, 4000), (4000, 8000), (8000, 16000)]:
        mm = (f >= lo) & (f < hi); bands[f"{lo//1000 if lo>=1000 else lo/1000}-{hi//1000}k"] = round(10 * np.log10((F[mm] ** 2).sum() + 1e-12), 1)
    mloc = em[p - int(0.05 * sr): p + int(0.05 * sr)].mean()
    return dict(t=round(on / sr, 4), peak_dbfs=round(db(np.abs(rh[p - 40:p + 40]).max()), 1), over_music_hf_db=round(db(pk) - db(mloc), 1),
                d10_ms=round(d10, 1), d20_ms=round(d20, 1), centroid=int(cen) if cen == cen else 0, peak_hz=int(pkf), bands=bands)
groups = {
 "click": [1.840, 1.927, 3.170, 3.257, 4.722, 4.812, 8.217, 8.304, 8.998, 9.085, 10.478, 10.565],
 "type": [3.991, 4.122, 4.255, 4.386, 4.519],
 "star": [12.873, 13.087, 13.296, 13.505, 13.717],
 "late": [15.192, 17.662, 18.019, 18.262],
}
out = {}
for g, ts in groups.items():
    print("==", g)
    out[g] = []
    for t in ts:
        r = one(t); out[g].append(r); print(r)
json.dump(out, open(sys.argv[3], "w"), indent=1)
# also report the music's own HF level & typical full-band peak for scale
print("music full-band peak dBFS", round(db(np.abs(musm).max()), 1), " ref-mix hf env median", round(db(np.median(env(signal.sosfiltfilt(hp, musm), 10))), 1))
