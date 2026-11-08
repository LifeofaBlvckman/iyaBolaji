import sys, numpy as np, soundfile as sf
from scipy import signal
ref, sr = sf.read(sys.argv[1], always_2d=True); song, _ = sf.read(sys.argv[2], always_2d=True)
coarse = float(sys.argv[3]); r = ref.mean(1); s = song.mean(1)
def bp(x, lo, hi):
    sos = signal.butter(4, [lo, hi], btype="band", fs=sr, output="sos"); return signal.sosfiltfilt(sos, x)
for name, (lo, hi) in {"low": (40, 250), "mid": (250, 3000), "high": (3000, 12000)}.items():
    rb, sb = bp(r, lo, hi), bp(s, lo, hi)
    out = []
    for t in np.arange(0.25, len(r)/sr - 1.25, 0.5):
        a = rb[int(t*sr): int((t+1)*sr)]
        c0 = int((t + coarse - 0.1) * sr); b = sb[c0: c0 + len(a) + int(0.2*sr)]
        cc = signal.correlate(b, a, mode="valid", method="fft"); k = int(np.argmax(np.abs(cc)))
        bb = b[k:k+len(a)]; q = cc[k] / (np.sqrt((a**2).sum()*(bb**2).sum()) + 1e-12)
        out.append(f"{t:5.2f}:{((c0+k)/sr - t - coarse)*1000:+6.1f}ms/{q:.2f}")
    print(name); print("  ".join(out))
