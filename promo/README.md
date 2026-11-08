# IyaBolaji promo video (source)

A 1080×1080 one-take promo in the style of the reference app-ordering ad, cut to Don Toliver's "Body" (146 BPM). The songs are not in this repo (copyright): put your copy at `promo/music/body.wav` before mixing.

- `promo.html`: the whole animation. `render(t)` draws the frame at time `t`, so every frame can be captured exactly. Storyboard landings are in beats (`k`); the video starts 2 beats before the drop at 8.24 s into the song.
- `timeline.json`: tempo 146.000 BPM, beat 410.96 ms, song start 8.2373 s, 58 beats (23.8 s).
- `tempo_scan.py`, `beat_grid.py`: how the tempo, beat phase and drop were measured (librosa).
- `mix.py`: the 7 short airy effects (5 taps, 1 swipe whoosh, 1 logo shimmer) in the song's quiet 3–5 kHz and 12–16 kHz bands, with brief dips in that band of the music only under each effect.
- `render.js`: captures the frames with Playwright.

Rebuild:

```bash
node promo/render.js promo/promo.html promo/frames 30 23.8356
```

```bash
python promo/mix.py promo/music/body.wav promo/timeline.json promo/mix.wav promo/sfx.wav promo/sfx.json
```

Then normalise to -14 LUFS (two-pass `loudnorm`, linear) and encode with ffmpeg (`-c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k`).

Photos: the spaghetti side dish still uses the drawing. Put the real photo at `assets/img/stir-fry-spaghetti.jpg` and set `SPAG` / `SPAG_ART` at the top of the script in `promo.html`.
