import math
import wave
from pathlib import Path

sr = 48000
duration = 16.0
samples = int(sr * duration)
out = Path('KAL_ambient_bed.wav')

with wave.open(str(out), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    frames = bytearray()
    for n in range(samples):
        t = n / sr
        fade_in = min(1.0, t / 1.2)
        fade_out = min(1.0, max(0.0, (duration - t) / 1.5))
        env = fade_in * fade_out
        # Soft low warm tone, intentionally very quiet.
        val = (
            0.045 * math.sin(2 * math.pi * 110 * t) +
            0.025 * math.sin(2 * math.pi * 220 * t) +
            0.012 * math.sin(2 * math.pi * 55 * t)
        ) * env
        s = int(max(-1, min(1, val)) * 32767)
        frames += int(s).to_bytes(2, 'little', signed=True)
    w.writeframes(frames)
print(out)
