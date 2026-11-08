import sys, numpy as np, soundfile as sf
from scipy import signal
res, sr = sf.read(sys.argv[1], always_2d=True); mus, _ = sf.read(sys.argv[2], always_2d=True); ref, _ = sf.read(sys.argv[3], always_2d=True)
f, t, R = signal.stft(res.mean(1), sr, nperseg=2048, noverlap=2048 - 441)
_, _, M = signal.stft(mus.mean(1), sr, nperseg=2048, noverlap=2048 - 441)
_, _, F = signal.stft(ref.mean(1), sr, nperseg=2048, noverlap=2048 - 441)
# stereo width of the reference: side/mid per frame in 6-16 kHz
_, _, Mi = signal.stft(ref.mean(1), sr, nperseg=2048, noverlap=2048 - 441)
_, _, Si = signal.stft((ref[:, 0] - ref[:, 1]) / 2, sr, nperseg=2048, noverlap=2048 - 441)
b = (f > 6000) & (f < 16000); bm = (f > 9500) & (f < 13000)
er = 10*np.log10((np.abs(R[b])**2).sum(0)+1e-12); em = 10*np.log10((np.abs(M[b])**2).sum(0)+1e-12)
ef = 10*np.log10((np.abs(F[b])**2).sum(0)+1e-12)
side = 10*np.log10((np.abs(Si[b])**2).sum(0)+1e-12) - 10*np.log10((np.abs(Mi[b])**2).sum(0)+1e-12)
notch = 10*np.log10((np.abs(R[bm])**2).mean(0)+1e-12) - 10*np.log10((np.abs(R[b])**2).mean(0)+1e-12)
d = er - em
line = []
for i in range(0, len(t), 2):
    line.append(f"{t[i]:5.2f} {d[i]:+5.1f} ref{ef[i]:5.1f} side{side[i]:+5.1f}")
for k in range(0, len(line), 4): print("   ".join(line[k:k+4]))
