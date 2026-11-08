import sys
import numpy as np
import librosa
ref, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
song, _ = librosa.load(sys.argv[2], sr=22050, mono=True)
hop = 512
def feat(y):
    c = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    o = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    return c, o
cr, orf = feat(ref); cs, osg = feat(song)
# Slide the reference's chroma over the song and score the similarity at each offset
n = cr.shape[1]
crn = cr / (np.linalg.norm(cr, axis=0) + 1e-9); csn = cs / (np.linalg.norm(cs, axis=0) + 1e-9)
scores = np.array([(crn * csn[:, i:i + n]).sum(0).mean() for i in range(cs.shape[1] - n)])
best = int(scores.argmax())
print(f"best chroma match: song offset {best * hop / sr:.2f}s, score {scores[best]:.3f} (median {np.median(scores):.3f}, 99th pct {np.percentile(scores, 99):.3f})")
# Onset-envelope correlation as a second opinion
oc = np.correlate((osg - osg.mean()) / osg.std(), (orf - orf.mean()) / orf.std(), mode="valid") / len(orf)
bo = int(oc.argmax())
print(f"best onset match: song offset {bo * hop / sr:.2f}s, corr {oc[bo]:.3f} (median {np.median(oc):.3f})")
# Tempo of the reference itself
t, beats = librosa.beat.beat_track(y=ref, sr=sr, hop_length=256, units="time")
print("reference tempo estimate:", np.round(np.atleast_1d(t), 2), "beats:", len(beats))
print("reference loudness proxy (rms):", float(np.sqrt((ref ** 2).mean())))
