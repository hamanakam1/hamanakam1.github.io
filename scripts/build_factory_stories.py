"""Publish reviewed project stories and encode a Camo-safe animation.

The PNGs are original image-generation outputs. cwebp makes delivery-format
copies and FFmpeg assembles the GIF; neither invents screenshots or product state.
"""
from pathlib import Path
from html import escape as E
import argparse
import hashlib
import json
import subprocess
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/factory-stories'
PRIORITY = ['ai-dashboard', 'taskrivet', 'panther-intent-capture', 'el-hidratador', 'fluxrecord',
            'el-verificador', 'the-chronicler', 'meter-mouse-garden', 'mockmill']


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-threads', '1', '-filter_threads', '1', *map(str, args)], check=True)


def render(stories):
    first = stories[0]
    public_count = sum(s['source_access'] == 'public' for s in stories)
    private_count = len(stories) - public_count
    cards = []
    for i, story in enumerate(stories):
        name = story['name']
        private = story['source_access'] == 'private'
        source_label = 'Read the published description' if private else 'Read the source at this revision'
        destination = story['source']['url'] if private else story['repository_url']
        destination_label = 'Public description' if private else 'Open repository'
        steps = ''.join(f'<li><strong>{E(s["stage"])}</strong> {E(s["label"])}</li>'
                        for s in story['factory_checkpoints'])
        attribution = (f'<p class="attribution">Fork of <a href="https://github.com/{E(story["upstream"])}">'
                       f'{E(story["upstream"])}</a></p>') if story['fork'] else ''
        cards.append(f'''<article class="story-card" id="repo-{E(name)}" data-story-card data-name="{E(name)}">
<a class="art" href="assets/factory-stories/{E(name)}.gif" aria-label="Open animated {E(name)} illustration"><img data-project-image="{E(name)}" src="assets/factory-stories/{E(name)}.webp" width="1120" height="630" loading="lazy" alt="{E(name)}: {E(story['input'])} → {E(story['transform'])} → {E(story['output'])}. Generated illustration."></a>
<div class="card-copy"><div class="eyebrow">{i+1:02d} / {E(story['category'])}</div><h3>{E(name)}</h3><p class="badge">{E(story['maturity_label'])}</p>{attribution}<p>{E(story['buyer_problem'])}</p>
<ol class="io"><li><span>INPUT</span>{E(story['input'])}</li><li><span>OPERATION</span>{E(story['transform'])}</li><li><span>OUTPUT</span>{E(story['output'])}</li></ol>
<details><summary>Factory checkpoints &amp; source</summary><p>Proposed checkpoints for discussing this project:</p><ol>{steps}</ol><p>{E(story['limitations'])}</p><a href="{E(story['source']['url'])}">{source_label} ↗</a></details>
<div class="card-actions"><button hidden data-animate="{E(name)}" type="button" aria-pressed="false">Play this flow</button><button hidden data-select="{i}" type="button">Show above ↑</button><a href="{E(destination)}">{destination_label} ↗</a><a href="assets/factory-stories/{E(name)}.png">Still image</a></div></div></article>''')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Inside the Software Factory — Mike Hamanaka</title><meta name="description" content="Follow {len(stories)} selected software projects from input to result, with illustrated workflows and source links."><link rel="canonical" href="https://hamanakam1.github.io/factory.html"><meta property="og:image" content="https://hamanakam1.github.io/assets/factory-stories/factory-cover.webp"><link rel="stylesheet" href="assets/factory-stories.css"></head>
<body><a class="skip" href="#main">Skip to content</a><header class="top wrap"><a class="brand" href="index.html">HAMANAKA / SOFTWARE FACTORY</a><nav aria-label="Main"><a href="index.html#contact">Work with Mike</a><a href="#projects">All {len(stories)} projects</a><a href="diagrams/factory-flow.html">Factory workflow</a></nav></header>
<main id="main" class="wrap"><section class="intro"><p class="eyebrow">IDEAS / TOOLS / REVIEWABLE RESULTS</p><h1>Inside the<br>Software Factory.</h1><p class="lead">One project at a time: what goes in, what the software does, and what comes out.</p><p class="scope">Generated illustrations and moving work packets explain project roles. The factory path is conceptual; each project retains its own maturity and limits.</p><ol class="factory-path" aria-label="Conceptual software factory process"><li>01 <strong>Define</strong></li><li>02 <strong>Build with AI</strong></li><li>03 <strong>Check</strong></li><li>04 <strong>Human review</strong></li><li>05 <strong>Share / demo</strong></li></ol><p class="small"><a href="diagrams/factory-flow.html">Explore the workflow and revision loop ↗</a></p></section>
<section id="walkthrough" class="walkthrough" aria-labelledby="walkthrough-title"><div class="viewer-heading"><div><p class="eyebrow">ANIMATED PROJECT WALKTHROUGH</p><h2 id="walkthrough-title">{E(first['name'])}</h2></div><p id="viewer-maturity" class="badge">{E(first['maturity_label'])}</p></div><img id="viewer-image" src="assets/factory-stories/{E(first['name'])}.webp" width="1120" height="630" alt="{E(first['name'])} illustrated input, operation and output"><div class="viewer-bottom"><p id="viewer-purpose">{E(first['buyer_problem'])}</p><a id="viewer-source" href="{E(first['source']['url'])}">Inspect the published description ↗</a></div><div class="controls" id="viewer-controls" hidden><button id="story-prev" type="button" aria-label="Previous project">← Previous</button><button id="story-play" type="button" aria-pressed="false">Play walkthrough</button><button id="story-next" type="button" aria-label="Next project">Next →</button><span id="story-position" role="status" aria-live="polite">1 / {len(stories)}</span></div><p class="small">Illustrations, not application screenshots or recorded executions. <a href="index.html#selected-work">See actual software captures</a>.</p></section>
<section id="projects" aria-labelledby="projects-title"><div class="section-heading"><div><p class="eyebrow">THE SELECTED WORKSHOP</p><h2 id="projects-title">{len(stories)} projects.<br>Each with a purpose.</h2></div><p>{public_count} public projects and {private_count} private concepts, based on their already-public descriptions. Selection reviewed on 3 November 2026. Each project has its own animated loop.</p></div><div class="search-controls" hidden id="search-controls"><label for="story-search">Find a project or workflow</label><div><input id="story-search" type="search" placeholder="Try Taskrivet, browser, invoice, or evidence"><button id="story-clear" type="button">Clear</button></div><p id="story-count" role="status" aria-live="polite">{len(stories)} projects</p></div><p id="story-empty" hidden>No matching projects. Clear the search to see all projects.</p><div class="story-grid">{''.join(cards)}</div></section>
<section class="contact"><p class="eyebrow">START WITH A REAL PROBLEM</p><h2>What needs to work<br>better in your day?</h2><p>I build prototypes and workflow tools with AI. Bring one recurring task or an idea you want to test, and we can discuss a small paid project with a result we can review together.</p><a class="cta" href="https://www.linkedin.com/in/hamanaka/">Discuss a project with Mike ↗</a></section></main><footer class="wrap"><span>Mike Hamanaka / Hamanaka Software Factory</span><a href="assets/factory-stories/stories.json">Source notes &amp; image provenance</a><a href="assets/factory-process-v3.gif">Open the animation</a></footer><script src="assets/factory-stories.js" defer></script></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--encode', action='store_true', help='Encode images and the size-limited GIF')
    args = parser.parse_args()
    data = json.loads((ASSETS / 'stories.json').read_text())
    stories = data['repositories']
    stories.sort(key=lambda s: (PRIORITY.index(s['name']) if s['name'] in PRIORITY else len(PRIORITY), s['name'].casefold()))
    if args.encode:
        for name in ['factory-cover'] + [s['name'] for s in stories]:
            original = ASSETS / f'{name}.png'
            if not original.exists():
                raise SystemExit(f'Missing generated image: {name}')
            subprocess.run(['cwebp', '-quiet', '-q', '88', '-resize', '1120', '630',
                            str(original), '-o', str(ASSETS / f'{name}.webp')], check=True)
        with tempfile.TemporaryDirectory(prefix='factory-gif-') as temporary:
            temp = Path(temporary)
            sequence = temp / 'scenes.ffconcat'
            featured = ['ai-dashboard', 'panther-intent-capture', 'el-hidratador', 'taskrivet',
                        'fluxrecord', 'el-verificador', 'the-chronicler', 'edgerecord-publisher']
            motion = json.loads((ASSETS / 'motion.json').read_text())
            if {item['name'] for item in motion['projects']} != {s['name'] for s in stories}:
                raise SystemExit('Every selected project must have a verified animation before building the overview')
            # All names come from the reviewed owned-repository list; quote paths for ffconcat.
            sequence.write_text('ffconcat version 1.0\n' + ''.join(f"file '{(ASSETS / (name+'.gif')).as_posix()}'\n" for name in featured))
            gif = temp / 'candidate.gif'
            for width, colors in [(720, 96), (680, 80), (640, 64)]:
                scale = f'scale={width}:-2:flags=lanczos'
                ffmpeg('-f', 'concat', '-safe', '0', '-i', sequence, '-vf', f'{scale},palettegen=max_colors={colors}:stats_mode=full', '-frames:v', '1', temp / 'palette.png')
                ffmpeg('-f', 'concat', '-safe', '0', '-i', sequence, '-i', temp / 'palette.png', '-filter_complex_threads', '1', '-lavfi', f'[0:v]{scale}[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle', '-fps_mode', 'vfr', '-loop', '0', gif)
                if gif.stat().st_size < 4_000_000:
                    break
            else:
                raise SystemExit('GIF exceeds the 4 MB delivery budget')
            with Image.open(gif) as decoded:
                delays = []
                for frame in range(decoded.n_frames):
                    decoded.seek(frame)
                    decoded.load()
                    delays.append(decoded.info.get('duration', 0))
                if len(delays) < 80 or not 40_000 <= sum(delays) <= 55_000:
                    raise SystemExit(f'Unexpected GIF timing: {len(delays)} frames / {sum(delays)} ms')
            (ROOT / 'assets/factory-process-v3.gif').write_bytes(gif.read_bytes())
            # The versioned still describes the conceptual factory, not a software screenshot.
            ffmpeg('-i', ASSETS / 'factory-cover.png', '-vf', 'scale=1120:630', '-frames:v', '1', ROOT / 'assets/factory-process-v3-still.png')
            data['animation'] = {'file': 'assets/factory-process-v3.gif', 'bytes': gif.stat().st_size,
                'sha256': hashlib.sha256(gif.read_bytes()).hexdigest(), 'size_budget_bytes': 4_000_000,
                'featured_projects': featured, 'gallery_projects': len(stories), 'width': width,
                'palette_colors': colors, 'encoded_frames': len(delays), 'duration_ms': sum(delays),
                'frame_delays_ms': delays, 'mode': 'Illustrated project sequences; not recordings of software execution'}
        for story in stories:
            original = ASSETS / f"{story['name']}.png"
            story['image'] = {'file': f"assets/factory-stories/{story['name']}.png",
                'preview': f"assets/factory-stories/{story['name']}.webp", 'kind': 'AI-generated illustration',
                'sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
                'preview_sha256': hashlib.sha256((ASSETS / f"{story['name']}.webp").read_bytes()).hexdigest()}
        data['cover'] = {'file': 'assets/factory-stories/factory-cover.png',
            'sha256': hashlib.sha256((ASSETS/'factory-cover.png').read_bytes()).hexdigest(),
            'preview': 'assets/factory-stories/factory-cover.webp',
            'preview_sha256': hashlib.sha256((ASSETS/'factory-cover.webp').read_bytes()).hexdigest(),
            'kind': 'AI-generated conceptual factory illustration'}
    (ASSETS / 'stories.json').write_text(json.dumps(data, indent=2) + '\n')
    (ROOT / 'factory.html').write_text(render(stories))
    print(f'Built illustrated workflow page for {len(stories)} selected projects.')
    if 'animation' in data:
        print(json.dumps(data['animation'], indent=2))


if __name__ == '__main__':
    main()
