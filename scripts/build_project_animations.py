"""Animate reviewed project illustrations without changing the source artwork.

Each six-second loop adds a conceptual input/process/output conveyor below the
original illustration. These are explanatory animations, not software telemetry.
FFmpeg encodes delivery assets; Pillow independently checks their decoded motion.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/factory-stories'
WIDTH, ART_HEIGHT, STRIP_HEIGHT = 720, 405, 54
HEIGHT = ART_HEIGHT + STRIP_HEIGHT
FPS, FRAMES, DURATION_MS = 10, 60, 6000
SIZE_LIMIT = 1_000_000
RECIPE = 'conveyor-v1-enter-hold-input-process-output-exit-720x459-10fps-6s'
RECIPE_SHA = hashlib.sha256(RECIPE.encode()).hexdigest()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix='.motion-', suffix='.json', delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, indent=2)
        stream.write('\n')
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def motion_filter(colors: int) -> str:
    # At every loop boundary the packet is outside the frame. It pauses at all
    # three stations; all movement is confined to the appended conveyor strip.
    ease = lambda u: f'({u})*({u})*(3-2*({u}))'
    packet_x = (
        f"if(lt(t,0.6),-26+119*{ease('t/0.6')},"
        f"if(lt(t,1.4),93,if(lt(t,2.4),93+250*{ease('t-1.4')},"
        f"if(lt(t,3.2),343,if(lt(t,4.2),343+250*{ease('t-3.2')},"
        f"if(lt(t,5),593,593+153*{ease('t-5')}))))))"
    )
    base = (
        f'[0:v]format=rgba,scale={WIDTH}:{ART_HEIGHT}:'
        'force_original_aspect_ratio=decrease:flags=lanczos,'
        f'pad={WIDTH}:{ART_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0xfaf6ed,'
        f'pad={WIDTH}:{HEIGHT}:0:0:color=0xfaf6ed,'
        'drawbox=x=0:y=405:w=720:h=1:color=0x172e2d@0.25:t=fill,'
        'drawbox=x=70:y=444:w=580:h=2:color=0x205c58@0.45:t=fill,'
        'drawbox=x=95:y=444:w=20:h=4:color=0x205c58:t=fill,'
        'drawbox=x=345:y=444:w=20:h=4:color=0x205c58:t=fill,'
        'drawbox=x=595:y=444:w=20:h=4:color=0x205c58:t=fill,'
        "drawbox=x=85:y=451:w=40:h=3:color=0xb8d929:t=fill:enable='between(t,0.5,1.5)',"
        "drawbox=x=335:y=451:w=40:h=3:color=0xb8d929:t=fill:enable='between(t,2.3,3.3)',"
        "drawbox=x=585:y=451:w=40:h=3:color=0xb8d929:t=fill:enable='between(t,4.1,5.1)'[base];"
    )
    sprite = (
        '[1:v]format=rgba,'
        'drawbox=x=0:y=0:w=24:h=30:color=0x172e2d:t=2,'
        'drawbox=x=5:y=8:w=14:h=2:color=0x205c58:t=fill,'
        'drawbox=x=5:y=14:w=14:h=2:color=0x205c58:t=fill,'
        'drawbox=x=5:y=20:w=9:h=2:color=0x205c58:t=fill[sprite];'
    )
    return (
        base + sprite + f"[base][sprite]overlay=x='{packet_x}':y=411:"
        'eval=frame:shortest=1:format=auto,format=rgb24,split[scene][palette_source];'
        f'[palette_source]palettegen=max_colors={colors}:stats_mode=full[palette];'
        '[scene][palette]paletteuse=dither=none:diff_mode=rectangle[out]'
    )


def inspect_motion(path: Path) -> dict:
    """Decode every frame, prove motion, and ensure the artwork stays static."""
    unique_frames, artwork_hashes = set(), set()
    duration, changed_pixels, moving_transitions = 0, 0, 0
    prior_strip = None
    with Image.open(path) as image:
        assert image.format == 'GIF' and image.size == (WIDTH, HEIGHT), path
        loop = image.info.get('loop')
        frame_count = image.n_frames
        for index in range(frame_count):
            image.seek(index)
            frame = image.convert('RGB')
            delay = image.info.get('duration', 0)
            assert delay == 100, f'{path.name}: unexpected frame delay {delay}'
            duration += delay
            unique_frames.add(hashlib.sha256(frame.tobytes()).digest())
            artwork = frame.crop((0, 0, WIDTH, ART_HEIGHT))
            artwork_hashes.add(hashlib.sha256(artwork.tobytes()).digest())
            strip = frame.crop((0, ART_HEIGHT, WIDTH, HEIGHT))
            if prior_strip is not None:
                difference = ImageChops.difference(strip, prior_strip)
                channels = difference.split()
                mask = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
                changed = sum(mask.histogram()[1:])
                changed_pixels += changed
                moving_transitions += int(changed > 0)
            prior_strip = strip
    assert frame_count == FRAMES and duration == DURATION_MS, (frame_count, duration)
    assert loop == 0, f'{path.name}: does not loop'
    assert len(unique_frames) >= 20 and moving_transitions >= 20 and changed_pixels > 1000
    assert len(artwork_hashes) == 1, f'{path.name}: original artwork region changed'
    assert path.stat().st_size < SIZE_LIMIT, f'{path.name}: exceeds size limit'
    return {'frames': frame_count, 'duration_ms': duration, 'loop': loop,
            'unique_decoded_frames': len(unique_frames),
            'moving_frame_transitions': moving_transitions,
            'changed_motion_pixels': changed_pixels, 'artwork_region_static': True}


def build_one(name: str, previous: dict | None) -> dict:
    source, output = ASSETS / f'{name}.png', ASSETS / f'{name}.gif'
    source_sha = digest(source)
    if previous and output.exists() and previous.get('source_sha256') == source_sha \
            and previous.get('recipe_sha256') == RECIPE_SHA \
            and previous.get('sha256') == digest(output):
        inspected = inspect_motion(output)
        return {**previous, **inspected}
    with tempfile.TemporaryDirectory(prefix='.project-motion-', dir=ASSETS) as temporary:
        candidate = Path(temporary) / f'{name}.gif'
        for colors in (96, 80, 64):
            command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                       '-threads', '1', '-filter_threads', '1', '-filter_complex_threads', '1',
                       '-loop', '1', '-framerate', str(FPS), '-i', str(source),
                       '-f', 'lavfi', '-i', f'color=c=0xdaf278:s=24x30:r={FPS}:d=6',
                       '-filter_complex', motion_filter(colors), '-map', '[out]',
                       '-frames:v', str(FRAMES), '-r', str(FPS), '-loop', '0',
                       '-final_delay', '10', str(candidate)]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(f'{name}: FFmpeg failed: {result.stderr[-4000:]}')
            if candidate.stat().st_size < SIZE_LIMIT:
                break
        else:
            raise RuntimeError(f'{name}: cannot meet {SIZE_LIMIT}-byte delivery limit')
        inspected = inspect_motion(candidate)
        assert digest(source) == source_sha, f'{name}: source changed during encoding'
        result = {'name': name, 'file': f'assets/factory-stories/{name}.gif',
                  'source_file': f'assets/factory-stories/{name}.png',
                  'source_sha256': source_sha, 'sha256': digest(candidate),
                  'bytes': candidate.stat().st_size, 'width': WIDTH, 'height': HEIGHT,
                  'fps': FPS, 'palette_colors': colors, 'size_limit_bytes': SIZE_LIMIT,
                  'recipe': RECIPE, 'recipe_sha256': RECIPE_SHA, **inspected}
        os.replace(candidate, output)
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--name', help='Build one project from the reviewed story manifest')
    selection.add_argument('--available', action='store_true', help='Explicitly skip missing source PNGs')
    args = parser.parse_args()
    data = json.loads((ASSETS / 'stories.json').read_text())
    names = [story['name'] for story in data['repositories']]
    assert len(names) == len(set(names)) and all(re.fullmatch(r'[A-Za-z0-9_.-]+', n) for n in names)
    assert not any(story.get('fork') for story in data['repositories']), 'Forks are outside this portfolio'
    if args.name and args.name not in names:
        parser.error('Requested project is outside the reviewed story manifest')
    missing = [name for name in names if not (ASSETS / f'{name}.png').is_file()]
    if args.name and args.name in missing:
        parser.error(f'Missing source PNG: {args.name}')
    if missing and not (args.available or args.name):
        parser.error('Missing source PNGs; final build requires all projects: ' + ', '.join(missing))
    chosen = [args.name] if args.name else [n for n in names if n not in missing]
    manifest_path = ASSETS / 'motion.json'
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'projects': []}
    existing = {item['name']: item for item in old['projects'] if item['name'] in names}
    built = {name: record for name, record in existing.items()
             if (ASSETS / f'{name}.png').is_file() and (ASSETS / f'{name}.gif').is_file()
             and record.get('source_sha256') == digest(ASSETS / f'{name}.png')
             and record.get('recipe_sha256') == RECIPE_SHA
             and record.get('sha256') == digest(ASSETS / f'{name}.gif')}
    for name in chosen:
        result = build_one(name, built.get(name))
        built[name] = result
        manifest = {'schema': 'project-motion.v1',
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'boundary': 'Conceptual input/process/output conveyor; not software execution footage.',
                    'expected_projects': len(names), 'complete': len(built) == len(names),
                    'missing_source_images': missing,
                    'projects': [built[n] for n in names if n in built]}
        atomic_json(manifest_path, manifest)
        print(f'{name}: {result["frames"]} frames, {result["duration_ms"]} ms, '
              f'{result["bytes"]:,} bytes, {result["unique_decoded_frames"]} distinct frames', flush=True)
    print(json.dumps({'complete': len(built) == len(names), 'built': len(built),
                      'expected': len(names), 'missing': missing}, sort_keys=True))


if __name__ == '__main__':
    main()
