# IyaBolaji promo video (source)

A 20-second 1080×1080 promo at 60 fps: a shot-for-shot replica of the reference app-ordering ad, with IyaBolaji's dishes and photos. The reference uses Don Toliver's "Body" from 26.33 s into the track, so this video uses the same 20 seconds. That makes every move and sound effect fall in the same place on the beat (146 BPM) as in the reference. The song is not in this repo (copyright): put your copy at `promo/music/body.wav` before mixing.

## Files

| File | What it is |
|------|------------|
| `promo.html` | The whole animation. `render(t)` draws the frame at `t` seconds, so every frame can be captured exactly. Shot timings, container keyframes (`K`), carousel swipes and the cursor path are at the top of the script. |
| `timeline.json` | Song start, tempo, and the time of every sound effect. |
| `mix.py` | Builds the effects and the mix: the music section, mouse clicks (press, then release 81 ms later), key taps, star ticks, swooshes and the end pops, each set to the level measured in the reference. |
| `render.js` | Captures the frames with Playwright. |
| `assets/` | Spaghetti and fried yam photos, the cropped logo, and [Fluent](https://github.com/microsoft/fluentui-emoji) 3D emoji (MIT licence, see `assets/emoji/LICENSE`). Turkey and fish photos come from the site's `assets/img/`. |
| `analysis/` | How the reference was measured (see below). |

## How the reference was measured

- `analysis/match.py` found the reference's music inside "Body" (chroma match 0.94, onset correlation 0.79, at 26.33 s).
- `analysis/offscan.py` checked the alignment band by band: the offset stays constant, with no drift.
- `analysis/isolate.py` subtracts the aligned song to leave the effects. The cancellation is only partial because the reference uses a different mix of the song, but it is enough to expose the transients.
- `analysis/clicks.py`, `analysis/measure.py` and `analysis/whoosh.py` find each effect and measure its level, length and brightness:

| Effect | Count | Level (sample peak above 1.5 kHz) | Length (to −10 / −20 dB) | Brightness (centroid) |
|---|---|---|---|---|
| Mouse click press | 6 | −3 to −5 dBFS | 12 / 28 ms | 4.3 kHz |
| Mouse click release (81 ms after) | 6 | −7 to −9 dBFS | 8 / 34 ms | 7 kHz |
| Key tap (every 133 ms) | 5 | −11 to −12 dBFS | 6 ms | 2.7 kHz |
| Star tick (every half beat) | 5 | −8 to −10 dBFS | 5 / 12 ms | 7–11 kHz |
| Swoosh (on morphs and swipes) | 20 | 6–16 kHz band at about hi-hat level | 100–200 ms | wide stereo |

Altogether there are 45 effects in 20 s, about 2 per second.

## Rebuild

```bash
node promo/render.js promo/promo.html promo/frames 60 20
```

```bash
python promo/mix.py promo/music/body.wav promo/premaster.wav promo/sfx.wav promo/mix.json
```

```bash
ffmpeg -i promo/premaster.wav -af "volume=0.55dB,alimiter=limit=0.86:attack=0.3:release=30:level=disabled:asc=1" -ar 48000 promo/master.wav
```

```bash
ffmpeg -framerate 60 -i promo/frames/%05d.png -i promo/master.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart -shortest promo/iyabolaji-promo.mp4
```

The result is −14.0 LUFS integrated with a true peak of −1.0 dBTP (the reference is −14.5 LUFS).
