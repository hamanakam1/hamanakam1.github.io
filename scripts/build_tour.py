#!/usr/bin/env python3
"""Encode the reviewed seven-frame browser capture; requires FFmpeg on PATH."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
frames = ROOT / 'docs/tour/frames'
assert sorted(p.name for p in frames.glob('*.png')) == [f'{n:02d}.png' for n in range(1, 8)]
subprocess.run([
    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-framerate', '1/2',
    '-i', str(frames / '%02d.png'), '-filter_complex',
    '[0:v]split[a][b];[a]palettegen=stats_mode=diff[p];'
    '[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle',
    '-loop', '0', str(ROOT / 'assets/factory-tour.gif'),
], check=True)
shutil.copyfile(frames / '01.png', ROOT / 'assets/factory-tour-still.png')
print('Built a 14-second, seven-stop tour and its still preview.')
