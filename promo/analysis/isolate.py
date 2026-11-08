"""Line the reference up with the song it uses, subtract the music, and keep what is left (the sound effects).

usage: isolate.py ref.wav song.wav coarse_offset_s out_residual.wav out_music_est.wav
"""
import sys, json
import numpy as np
import soundfile as sf
from scipy import signal

ref, sr = sf.read(sys.argv[1], always_2d=True)
song, sr2 = sf.read(sys.argv[2], always_2d=True)
assert sr == sr2
coarse = float(sys.argv[3])
r = ref.mean(1); s = song.mean(1)

# 1. offsets found by offscan.py: constant until ~13.8 s, then 1.0 ms earlier (an edit in the reference)
off0 = coarse; drift = 0.0
tt = np.arange(len(r)) / sr
shift = np.where(tt < 13.8, 0.0, -0.0010)
src = (tt + off0 + shift) * sr
music = np.stack([np.interp(src, np.arange(len(song)), song[:, ch]) for ch in range(song.shape[1])], 1)

# 3. per-band, slowly varying gain: STFT, then fit H(f, t) = <R S*> / <|S|^2> smoothed over ~1.5 s
nper = 2048; hop = 512
f, t, R = signal.stft(ref.T, sr, nperseg=nper, noverlap=nper - hop)
_, _, S = signal.stft(music.T, sr, nperseg=nper, noverlap=nper - hop)
win = int(1.5 * sr / hop) | 1
k = np.hanning(win); k /= k.sum()
num = signal.fftconvolve(R * np.conj(S), k[None, None, :], mode="same", axes=2)
den = signal.fftconvolve(np.abs(S) ** 2, k[None, None, :], mode="same", axes=2) + 1e-10
H = num / den
# also smooth across frequency (1/6 octave-ish, use 9 bins) so H cannot fit the effects themselves
kf = np.hanning(9); kf /= kf.sum()
H = signal.fftconvolve(H, kf[None, :, None], mode="same", axes=1)
E = R - H * S
_, resid = signal.istft(E, sr, nperseg=nper, noverlap=nper - hop)
_, mest = signal.istft(H * S, sr, nperseg=nper, noverlap=nper - hop)
resid = resid.T[: len(r)]; mest = mest.T[: len(r)]
sf.write(sys.argv[4], resid.astype(np.float32), sr)
sf.write(sys.argv[5], mest.astype(np.float32), sr)

rd = lambda x: 10 * np.log10((x ** 2).mean() + 1e-20)
print(f"ref {rd(ref):.1f} dB, music estimate {rd(mest):.1f} dB, residual {rd(resid):.1f} dB  (music cancelled by {rd(ref)-rd(resid):.1f} dB)")
gain = np.abs(H).mean(axis=(0, 2))
bands = [(60, 250), (250, 1000), (1000, 4000), (4000, 10000), (10000, 18000)]
for lo, hi in bands:
    m = (f >= lo) & (f < hi)
    print(f"  mean |H| {lo}-{hi} Hz: {20*np.log10(gain[m].mean()):.1f} dB")
json.dump({"offset": off0, "drift": drift, "sr": sr}, open(sys.argv[4] + ".json", "w"))
