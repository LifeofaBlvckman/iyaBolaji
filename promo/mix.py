"""Music + sound effects for the replica, matched to what was measured in the reference.

usage: mix_replica.py song.wav out_premaster.wav out_sfx.wav report.json

The reference uses the same song from 26.335 s, so the music section is the same and every
effect sits at the time it sits in the reference. Levels are set the way they were measured:
clicks/taps/ticks/pops by their sample peak above 1.5 kHz, swooshes by their 6-16 kHz band
level, both in a mix whose music is as loud as the reference's.
"""
import sys, json
import numpy as np
import soundfile as sf
from scipy import signal

song_path, out_path, sfx_path, rep_path = sys.argv[1:5]
OFFSET, DUR = 26.33483, 20.0
song, sr = sf.read(song_path, always_2d=True)
a = int(round(OFFSET * sr)); n = int(round(DUR * sr))
music = song[a:a + n].copy()
fi = int(0.01 * sr); music[:fi] *= np.linspace(0, 1, fi)[:, None]
# The reference's music drops away under the final fade (19.45 -> 19.9 s)
tt = np.arange(n) / sr
music *= (0.5 + 0.5 * np.cos(np.pi * np.clip((tt - 19.45) / 0.45, 0, 1)))[:, None]

rng = np.random.default_rng(11)
def bp(x, lo, hi, order=4): return signal.sosfilt(signal.butter(order, [lo, hi], btype="band", fs=sr, output="sos"), x)
def hp(x, f): return signal.sosfiltfilt(signal.butter(4, f, btype="high", fs=sr, output="sos"), x)
def ring(f, decay, L, phase=0.0):
    t = np.arange(L) / sr; return np.sin(2 * np.pi * f * t + phase) * np.exp(-t / decay)
def env_exp(L, tau, attack=0.0004):
    t = np.arange(L) / sr; return np.minimum(t / attack, 1) * np.exp(-t / tau)

# --- the effects -----------------------------------------------------------
def click_press():      # broadband, flat 0.3-8 kHz, ~12 ms to -10 dB, ~28 ms to -20 dB, centroid ~4.3 kHz
    L = int(0.08 * sr)
    x = bp(rng.standard_normal(L), 1000, 9500) * env_exp(L, 0.0135)
    x += 0.5 * ring(2380, 0.015, L) + 0.5 * ring(4480, 0.014, L, 1.0) + 0.25 * ring(1080, 0.016, L, 2.0) + 0.3 * ring(6700, 0.011, L, .5)
    return x / np.abs(x).max()
def click_release():    # brighter (centroid ~7.7 kHz), fast first drop (~4 ms to -10 dB) then a short tail
    L = int(0.07 * sr)
    x = bp(rng.standard_normal(L), 3500, 11000) * env_exp(L, 0.005)
    x += 0.5 * bp(rng.standard_normal(L), 3000, 9000) * env_exp(L, 0.016)
    x += 0.35 * ring(10400, 0.004, L) + 0.3 * ring(7600, 0.006, L, 1.3)
    return x / np.abs(x).max()
def key_tap():          # keyboard tap: body 0.4-0.7 kHz plus a 2-3 kHz click, ~5.5 ms to -10 dB, short tail
    L = int(0.09 * sr)
    x = 0.35 * ring(400, 0.016, L) + 0.3 * ring(690, 0.012, L, .7) + 0.6 * ring(2745, 0.006, L, 1.9)
    x += 0.8 * bp(rng.standard_normal(L), 1500, 8000) * env_exp(L, 0.0055)
    x += 0.3 * bp(rng.standard_normal(L), 1500, 6000) * env_exp(L, 0.025)
    return x / np.abs(x).max()
def star_tick():        # bright tick, centroid 7-12 kHz, 11-34 ms long
    L = int(0.045 * sr)
    x = bp(rng.standard_normal(L), 5500, 13000) * env_exp(L, 0.0035)
    x += 0.7 * ring(9000 + rng.uniform(-600, 600), 0.006, L) + 0.35 * ring(8500, 0.005, L, 1.1)
    return x / np.abs(x).max()
def soft_pop(f0=1300, f1=700, dur=0.24, decay=0.085):   # low "bloop" when the closing line lands
    L = int(dur * sr); t = np.arange(L) / sr
    f = f1 + (f0 - f1) * np.exp(-t / 0.02); ph = 2 * np.pi * np.cumsum(f) / sr
    x = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * env_exp(L, decay, 0.002)
    return x / np.abs(x).max()
def tonal_pop(f=656, dur=0.16, decay=0.055):           # rounded pop with partials near 2 and 2.6 kHz
    L = int(dur * sr)
    x = ring(f, decay, L) + 1.0 * ring(f * 3.0, decay * .7, L, .4) + 0.6 * ring(f * 4.0, decay * .5, L, 1.2)
    x *= np.minimum(np.arange(L) / (0.0015 * sr), 1)
    return x / np.abs(x).max()
def swoosh(L, peak=0.55):   # airy, stereo-wide: independent noise per side, 5-15 kHz, rises then falls
    N = int(L * sr); t = np.arange(N) / sr; u = t / L
    env = np.where(u < peak, (u / peak) ** 1.6, ((1 - u) / (1 - peak)) ** 1.3)
    out = []
    for ch in range(2):
        lo = bp(rng.standard_normal(N), 4500, 9000); hi = bp(rng.standard_normal(N), 8500, 15500)
        w = np.clip(u / peak, 0, 1)
        out.append((lo * (1 - 0.6 * w) + hi * (0.4 + 0.6 * w)) * env)
    x = np.stack(out, 1)
    return x / np.abs(x).max()

# --- when, as measured in the reference -----------------------------------
CLICKS = [1.8416, 3.1725, 4.7263, 8.2201, 9.0015, 10.4804]
PRESS_DB = [-3.8, -4.2, -5.4, -3.3, -3.3, -4.9]            # sample peak above 1.5 kHz
RELEASE_GAP, RELEASE_DB = 0.081, [-8.6, -9.3, -7.6, -9.1, -8.7, -6.8]
TAPS = [3.9886, 4.1183, 4.2503, 4.3824, 4.5143]; TAP_DB = [-11.6, -11.1, -12.3, -11.3, -11.5]
STARS = [12.8696, 13.0827, 13.3005, 13.5105, 13.7127]; STAR_DB = [-7.6, -8.1, -10.0, -8.7, -9.7]
POPS = [(15.1965, "soft", -16.6), (18.016, "tonal", -10.5), (18.2579, "tonal2", -16.5)]
SWOOSH = [(0.06, .16), (0.78, .2), (2.28, .18), (3.52, .12), (4.76, .18), (5.92, .12), (6.26, .12), (6.6, .1), (6.82, .14),
          (7.08, .1), (7.34, .2), (9.06, .2), (10.54, .2), (11.54, .1), (12.38, .16), (13.78, .18), (14.62, .2), (14.84, .12),
          (16.0, .2), (16.96, .22)]
SWOOSH_BAND_DB = -27.5      # 6-16 kHz band level at the swoosh's loudest frame (reference median)

# --- level the music like the reference's -----------------------------------
def lufs(x):
    # BS.1770 integrated loudness (K-weighting + gating), compact version
    # K-weighting coefficients for any sample rate (pyloudnorm formulation)
    def shelf(G=3.999843853973347, Q=0.7071752369554196, fc=1681.974450955533):
        A = 10 ** (G / 40); w0 = 2 * np.pi * fc / sr; al = np.sin(w0) / (2 * Q)
        b = [A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * np.cos(w0)), A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * al)]
        a = [(A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * np.cos(w0)), (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * al]
        return np.array(b) / a[0], np.array(a) / a[0]
    def hpf(Q=0.5003270373238773, fc=38.13547087602444):
        w0 = 2 * np.pi * fc / sr; al = np.sin(w0) / (2 * Q)
        b = [(1 + np.cos(w0)) / 2, -(1 + np.cos(w0)), (1 + np.cos(w0)) / 2]; a = [1 + al, -2 * np.cos(w0), 1 - al]
        return np.array(b) / a[0], np.array(a) / a[0]
    (bs, as_), (bh, ah) = shelf(), hpf()
    y = signal.lfilter(bh, ah, signal.lfilter(bs, as_, x, axis=0), axis=0)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    z = np.array([(y[i:i + blk] ** 2).mean(0).sum() for i in range(0, len(y) - blk, hop)])
    l = -0.691 + 10 * np.log10(z + 1e-12)
    g = z[l > -70]; th = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = z[(l > -70) & (l > th)]
    return -0.691 + 10 * np.log10(g2.mean())

music_l = lufs(music[: int(19.4 * sr)])
music *= 10 ** ((-14.8 - music_l) / 20)        # reference is -14.5 LUFS with the effects in

sfx = np.zeros_like(music)
def put(x, t, peak_db=None):
    if x.ndim == 1: x = np.stack([x, x], 1)
    if peak_db is not None:
        x = x * 10 ** (peak_db / 20) / np.abs(hp(x.mean(1), 1500)).max()
    i = int(round(t * sr)); j = min(len(sfx), i + len(x))
    sfx[i:j] += x[: j - i]
    return x
for t, pdb, rdb in zip(CLICKS, PRESS_DB, RELEASE_DB):
    put(click_press(), t, pdb); put(click_release(), t + RELEASE_GAP, rdb)
for t, d in zip(TAPS, TAP_DB): put(key_tap(), t, d)
for t, d in zip(STARS, STAR_DB): put(star_tick(), t, d)
for t, kind, d in POPS:
    put({"soft": soft_pop(), "tonal": tonal_pop(), "tonal2": tonal_pop(586, 0.12, 0.04)}[kind], t, d)

def band_peak_db(x):   # same measure as the analysis: mono, STFT 2048, hop 10 ms, 6-16 kHz summed power
    f, _, Z = signal.stft(x.mean(1), sr, nperseg=2048, noverlap=2048 - 441)
    m = (f > 6000) & (f < 16000)
    return 10 * np.log10((np.abs(Z[m]) ** 2).sum(0).max() + 1e-12)
for t, L in SWOOSH:
    w = swoosh(L)
    pad = np.zeros((int(0.1 * sr), 2)); probe = np.concatenate([pad, w, pad])
    w *= 10 ** ((SWOOSH_BAND_DB - band_peak_db(probe)) / 20)
    put(w, t)

mixd = music + sfx
sf.write(out_path, mixd.astype(np.float32), sr, subtype="FLOAT")
sf.write(sfx_path, sfx.astype(np.float32), sr, subtype="FLOAT")
json.dump({"music_lufs_before": music_l, "events": len(CLICKS) * 2 + len(TAPS) + len(STARS) + len(POPS) + len(SWOOSH),
           "premaster_lufs": lufs(mixd[: int(19.4 * sr)]), "sfx_peak": float(np.abs(sfx).max()), "mix_peak": float(np.abs(mixd).max())},
          open(rep_path, "w"), indent=1)
print(open(rep_path).read())
