import sys, numpy as np
import librosa
from faster_whisper import WhisperModel

if len(sys.argv) < 2:
    print("Usage: python scripts/ct2_smoketest.py <ABS_PATH_TO_AUDIO>")
    sys.exit(1)

audio_path = sys.argv[1]
print("[CT2-SMOKE] loading model 'small' (device=auto, compute_type=float16)")
model = WhisperModel("small", device="auto", compute_type="float16")

print(f"[CT2-SMOKE] reading (librosa): {audio_path}")
# librosa MP3/WAV/FLAC hepsini okur; 16k tek kanal float32'e dönüştürelim
audio, sr = librosa.load(audio_path, sr=16000, mono=True)
audio = audio.astype(np.float32)

print("[CT2-SMOKE] transcribe...")
segments, info = model.transcribe(audio, language=None, task="transcribe", beam_size=1)
text = "".join([s.text for s in segments]).strip()
print("[CT2-SMOKE] TEXT:", text)
