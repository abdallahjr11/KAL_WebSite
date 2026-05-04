import subprocess
from pathlib import Path

src = Path('KAL_promo_video.mp4')
tmp = Path('KAL_promo_with_voice.mp4')
filter_complex = (
    '[1:a]adelay=450|450,volume=1.55,'
    'acompressor=threshold=-18dB:ratio=2.2:attack=12:release=180[vo];'
    '[2:a]volume=0.55[bed];'
    '[bed][vo]amix=inputs=2:duration=first:dropout_transition=0,'
    'alimiter=limit=0.9[a]'
)
cmd = [
    'ffmpeg', '-y',
    '-i', str(src),
    '-i', 'KAL_voiceover.wav',
    '-i', 'KAL_ambient_bed.wav',
    '-filter_complex', filter_complex,
    '-map', '0:v',
    '-map', '[a]',
    '-c:v', 'copy',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    str(tmp),
]
subprocess.run(cmd, check=True)
tmp.replace(src)
print('updated', src)
