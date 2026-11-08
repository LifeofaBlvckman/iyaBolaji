import json, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sosfiltfilt

song_path, tl_path, out_mix, out_sfx, out_json = sys.argv[1:6]
tl = json.load(open(tl_path)); B = tl["beat"]; dur = tl["duration"]
sr, song = wavfile.read(song_path); song = song.astype(np.float32) / 32768.0
a = int(round(tl["song_start"] * sr)); n = int(round(dur * sr))
music = song[a:a + n].copy()
# 15 ms fade in; fade out over the last two beats
fi = int(0.015 * sr); music[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(2 * B * sr); music[-fo:] *= (np.cos(np.linspace(0, np.pi, fo)) * 0.5 + 0.5)[:, None]
rng = np.random.default_rng(7)
def band(x, lo, hi): return sosfilt(butter(4, [lo, hi], btype="band", fs=sr, output="sos"), x)
def hp(x, f): return sosfilt(butter(4, f, btype="high", fs=sr, output="sos"), x)
# Effects live where the song is quiet: 3-5 kHz (presence) and 12-16 kHz (air).
def tap():
    L = int(0.045 * sr); t = np.arange(L) / sr
    x = band(rng.standard_normal(L), 3000, 5200) * np.exp(-t / 0.008)
    x += 0.35 * np.sin(2 * np.pi * 3900 * t) * np.exp(-t / 0.012)
    x += 0.6 * band(rng.standard_normal(L), 12000, 16000) * np.exp(-t / 0.014)
    return x / np.abs(x).max()
def whoosh(peak=0.2, L=0.26):
    N = int(L * sr); t = np.arange(N) / sr
    lo = band(rng.standard_normal(N), 2800, 4000); hi = band(rng.standard_normal(N), 3800, 5200)
    air = band(rng.standard_normal(N), 12000, 16000)
    w = np.clip(t / peak, 0, 1)                         # rises in pitch and gets airier
    x = lo * (1 - w) + hi * w + air * (0.3 + 0.7 * w)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / 0.025))
    x *= env; return x / np.abs(x).max()
def shimmer(L=0.34):
    N = int(L * sr); t = np.arange(N) / sr
    x = band(rng.standard_normal(N), 12000, 16000) * np.minimum(t / 0.01, 1) * np.exp(-t / 0.11)
    for f, d in [(3900, 0.0), (4400, 0.035), (4950, 0.07)]:
        tt = np.clip(t - d, 0, None); x += 0.5 * np.sin(2 * np.pi * f * tt) * (t >= d) * np.exp(-tt / 0.06)
    return x / np.abs(x).max()
def pan(x, p):                                          # p: 0 = left, 1 = right (equal power)
    return np.stack([x * np.cos(p * np.pi / 2), x * np.sin(p * np.pi / 2)], axis=1)
def pan_sweep(x, p0, p1):
    p = np.linspace(p0, p1, len(x)); return np.stack([x * np.cos(p * np.pi / 2), x * np.sin(p * np.pi / 2)], axis=1)

# Moves that matter, on the beat grid (beat numbers from the storyboard)
cursor_x = {10: 700, 15: 880, 23: 820, 28: 770, 41: 680}
events = [{"kind": "tap", "beat": k, "x": x} for k, x in cursor_x.items()]
events += [{"kind": "whoosh", "beat": 18.0, "peak_at": 0.20}, {"kind": "shimmer", "beat": 51.0}]
sfx = np.zeros_like(music)
F = np.fft.rfftfreq(4096, 1 / sr)
def pocket_db(x, s0, s1):                               # energy in the 3-5 kHz pocket
    seg = x[s0:s1].mean(axis=1) if x.ndim > 1 else x[s0:s1]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 4096)) ** 2
    return 10 * np.log10(spec[(F > 3000) & (F < 5000)].sum() + 1e-12)
report = []
for e in events:
    if e["kind"] == "tap": x = pan(tap(), e["x"] / 1080); onset = e["beat"] * B - 0.005
    elif e["kind"] == "whoosh": x = pan_sweep(whoosh(e["peak_at"]), 0.75, 0.25); onset = e["beat"] * B - e["peak_at"]
    else: x = pan(shimmer(), 0.5); onset = e["beat"] * B - 0.005
    s0 = int(round(onset * sr)); s1 = s0 + len(x)
    # Level: at its peak, 6 dB above the music inside the 3-5 kHz pocket (30 ms window)
    pk = int(np.argmax(np.abs(x).sum(axis=1)))
    w0 = max(0, pk - int(0.015 * sr)); w1 = w0 + int(0.03 * sr)
    m = pocket_db(music, s0 + w0, s0 + w1); g = 0.02
    while pocket_db(x * g, w0, w1) < m + 6 and g < 0.5: g *= 1.06
    # Still short? Dip only the music's 2.5-6 kHz slice, only for this effect's length (max 8 dB).
    short = (m + 6) - pocket_db(x * g, w0, w1)
    duck_db = float(np.clip(short, 0, 8))
    if duck_db > 0.1:
        a0, a1 = max(0, s0 - int(0.03 * sr)), min(len(music), s1 + int(0.04 * sr))
        seg = music[a0:a1]
        zsos = butter(4, [2500, 6000], btype="band", fs=sr, output="sos")   # zero-phase, so subtraction cancels cleanly
        slice_ = np.stack([sosfiltfilt(zsos, seg[:, c]) for c in range(2)], axis=1)
        ramp = np.clip(np.sin(np.linspace(0, np.pi, a1 - a0)) * 1.6, 0, 1)
        music[a0:a1] = seg - (1 - 10 ** (-duck_db / 20)) * slice_ * ramp[:, None]
        m = pocket_db(music, s0 + w0, s0 + w1)
    sfx[s0:s1] += x * g
    # Measured character: length to -20 dB, brightness (spectral centroid)
    mono = x.mean(axis=1); envd = 20 * np.log10(np.abs(mono) / np.abs(mono).max() + 1e-9)
    above = np.where(envd > -20)[0]; length = (above[-1] - above[0]) / sr
    spec = np.abs(np.fft.rfft(mono, 8192)) ** 2; f = np.fft.rfftfreq(8192, 1 / sr)
    report.append({**e, "time_s": round(onset, 3), "length_ms": round(length * 1000), "centroid_hz": round(float((f * spec).sum() / spec.sum())), "gain": round(g, 3), "music_dip_db": round(duck_db, 1), "peak_dbfs": round(20 * np.log10(np.abs(x * g).max()), 1), "above_music_pocket_db": round(pocket_db(x * g, w0, w1) - m, 1)})
mixed = music + sfx
wavfile.write(out_mix, sr, mixed.astype(np.float32))
wavfile.write(out_sfx, sr, sfx.astype(np.float32))
json.dump(report, open(out_json, "w"), indent=1)
L = np.array([r["length_ms"] for r in report]); C = np.array([r["centroid_hz"] for r in report])
print(f"{len(report)} effects in {dur:.1f}s = {len(report)/dur:.2f}/s; length ms median {np.median(L):.0f} ({L.min()}-{L.max()}); brightness median {np.median(C):.0f} Hz ({C.min()}-{C.max()})")
for r in report: print(r)
print("mix peak dBFS before loudness:", round(20 * np.log10(np.abs(mixed).max()), 2))
