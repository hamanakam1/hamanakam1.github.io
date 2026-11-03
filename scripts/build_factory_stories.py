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
DETAILS = [
    ('work', 'Work and agents', 'Keep the task beside the activity.',
     'Task tickets and agent work are shown together, giving the operator a place to inspect what is being worked on.'),
    ('inference', 'Inference activity', 'See requests moving through the work.',
     'This concept follows inference requests and responses through an activity view, without presenting invented provider routes or live throughput.'),
    ('resources', 'Spend and machine health', 'Bring costs and constraints into view.',
     'Spending signals and machine-health categories sit beside the work, so the operator can inspect the resources involved.'),
    ('review', 'Evidence and human inspection', 'Make the result inspectable.',
     'Results arrive with evidence for a person to examine. The scene illustrates review, not automatic acceptance or a production-readiness claim.'),
]


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-threads', '1', '-filter_threads', '1', *map(str, args)], check=True)


def render(stories):
    first = stories[0]
    public_count = sum(s['source_access'] == 'public' for s in stories)
    private_count = len(stories) - public_count
    cards = []
    current_section = None
    for i, story in enumerate(stories):
        name = story['name']
        private = story['source_access'] == 'private'
        source_label = 'Read the published description' if private else 'Read the source at this revision'
        destination = story['source']['url'] if private else story['repository_url']
        destination_label = 'Public description' if private else 'Open repository'
        if story['section'] != current_section:
            current_section = story['section']
            cards.append(f'<div class="story-section" id="section-{E(current_section)}" data-story-section="{E(current_section)}"><p class="eyebrow">{i+1:02d} / NEXT PART OF THE WORKSHOP</p><h3>{E(story["section_label"])}</h3></div>')
        steps = ''.join(f'<li><strong>{E(s["stage"])}</strong> {E(s["label"])}</li>'
                        for s in story['factory_checkpoints'])
        attribution = (f'<p class="attribution">Fork of <a href="https://github.com/{E(story["upstream"])}">'
                       f'{E(story["upstream"])}</a></p>') if story['fork'] else ''
        cards.append(f'''<article class="story-card" id="repo-{E(name)}" data-story-card data-name="{E(name)}" data-section="{E(story['section'])}">
<a class="art" href="assets/factory-stories/{E(name)}.gif" aria-label="Open animated {E(name)} illustration"><img data-project-image="{E(name)}" src="assets/factory-stories/{E(name)}.webp" width="1120" height="630" loading="lazy" alt="{E(name)}: {E(story['input'])} → {E(story['transform'])} → {E(story['output'])}. Generated illustration."></a>
<div class="card-copy"><div class="eyebrow">{i+1:02d} / {E(story['category'])}</div><h3>{E(name)}</h3><p class="badge">{E(story['maturity_label'])}</p>{attribution}<p>{E(story['buyer_problem'])}</p>
<ol class="io"><li><span>INPUT</span>{E(story['input'])}</li><li><span>OPERATION</span>{E(story['transform'])}</li><li><span>OUTPUT</span>{E(story['output'])}</li></ol>
<details><summary>Factory checkpoints &amp; source</summary><p>Proposed checkpoints for discussing this project:</p><ol>{steps}</ol><p>{E(story['limitations'])}</p><a href="{E(story['source']['url'])}">{source_label} ↗</a></details>
<div class="card-actions"><button hidden data-animate="{E(name)}" type="button" aria-pressed="false">Play this flow</button><button hidden data-select="{i}" type="button">Show above ↑</button><a href="{E(destination)}">{destination_label} ↗</a><a href="assets/factory-stories/{E(name)}.png">Still image</a></div></div></article>''')
    chapter_cards = ''.join(f'<article><a href="assets/factory-stories/details/ai-dashboard-{slug}.png"><img src="assets/factory-stories/details/ai-dashboard-{slug}.webp" width="1120" height="630" loading="lazy" alt="AI Dashboard concept: {E(title)}"></a><p class="chapter-number">CHAPTER {number:02d} / {E(title.upper())}</p><h3>{E(headline)}</h3><p>{E(description)}</p></article>' for number,(slug,title,headline,description) in enumerate(DETAILS,1))
    dashboard_panel = f'<section id="dashboard-detail" class="dashboard-detail" aria-labelledby="dashboard-detail-title"><p class="eyebrow">AI DASHBOARD / A CLOSER LOOK</p><h2 id="dashboard-detail-title">One command center.<br>Four perspectives.</h2><p class="lead">Work, inference, resources and evidence—brought into an operator’s view.</p><p class="scope">These richer concept scenes expand the categories already described in the public atlas. They are illustrations of a private project, not its actual interface or live data.</p><div class="detail-grid">{chapter_cards}</div></section>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Inside the Software Factory — Mike Hamanaka</title><meta name="description" content="Follow {len(stories)} selected software projects from input to result, with illustrated workflows and source links."><link rel="canonical" href="https://hamanakam1.github.io/factory.html"><meta property="og:image" content="https://hamanakam1.github.io/assets/factory-stories/factory-cover.webp"><link rel="stylesheet" href="assets/factory-stories.css"></head>
<body><a class="skip" href="#main">Skip to content</a><header class="top wrap"><a class="brand" href="index.html">HAMANAKA / SOFTWARE FACTORY</a><nav aria-label="Main"><a href="index.html#contact">Work with Mike</a><a href="#dashboard-detail">AI Dashboard</a><a href="#projects">All {len(stories)} projects</a><a href="diagrams/factory-flow.html">Factory workflow</a></nav></header>
<main id="main" class="wrap"><section class="intro"><p class="eyebrow">IDEAS / TOOLS / REVIEWABLE RESULTS</p><h1>Inside the<br>Software Factory.</h1><p class="lead">One project at a time: what goes in, what the software does, and what comes out.</p><p class="scope">Generated illustrations and moving work packets explain project roles. The factory path is conceptual; each project retains its own maturity and limits.</p><ol class="factory-path" aria-label="Conceptual software factory process"><li>01 <strong>Define</strong></li><li>02 <strong>Build with AI</strong></li><li>03 <strong>Check</strong></li><li>04 <strong>Human review</strong></li><li>05 <strong>Share / demo</strong></li></ol><p class="small"><a href="diagrams/factory-flow.html">Explore the workflow and revision loop ↗</a></p></section>
<section id="walkthrough" class="walkthrough" aria-labelledby="walkthrough-title"><div class="viewer-heading"><div><p class="eyebrow">ANIMATED PROJECT WALKTHROUGH</p><h2 id="walkthrough-title">{E(first['name'])}</h2></div><p id="viewer-maturity" class="badge">{E(first['maturity_label'])}</p></div><img id="viewer-image" src="assets/factory-stories/{E(first['name'])}.webp" width="1120" height="630" alt="{E(first['name'])} illustrated input, operation and output"><div class="viewer-bottom"><p id="viewer-purpose">{E(first['buyer_problem'])}</p><a id="viewer-source" href="{E(first['source']['url'])}">Inspect the published description ↗</a></div><div class="controls" id="viewer-controls" hidden><button id="story-prev" type="button" aria-label="Previous project">← Previous</button><button id="story-play" type="button" aria-pressed="false">Play walkthrough</button><button id="story-next" type="button" aria-label="Next project">Next →</button><span id="story-position" role="status" aria-live="polite">1 / {len(stories)}</span></div><p class="small">Illustrations, not application screenshots or recorded executions. <a href="index.html#selected-work">See actual software captures</a>.</p></section>
{dashboard_panel}<section id="projects" aria-labelledby="projects-title"><div class="section-heading"><div><p class="eyebrow">THE SELECTED WORKSHOP</p><h2 id="projects-title">{len(stories)} projects.<br>Each with a purpose.</h2></div><p>{public_count} public projects and {private_count} private concepts, based on their already-public descriptions. Selection reviewed on 3 November 2026. Factory tools come first; independent product and creative experiments finish the tour. Each project has its own animated loop.</p></div><div class="search-controls" hidden id="search-controls"><label for="story-search">Find a project or workflow</label><div><input id="story-search" type="search" placeholder="Try Taskrivet, browser, kitchen, or evidence"><button id="story-clear" type="button">Clear</button></div><p id="story-count" role="status" aria-live="polite">{len(stories)} projects</p></div><p id="story-empty" hidden>No matching projects. Clear the search to see all projects.</p><div class="story-grid">{''.join(cards)}</div></section>
<section class="contact"><p class="eyebrow">START WITH A REAL PROBLEM</p><h2>What needs to work<br>better in your day?</h2><p>I build prototypes and workflow tools with AI. Bring one recurring task or an idea you want to test, and we can discuss a small paid project with a result we can review together.</p><a class="cta" href="https://www.linkedin.com/in/hamanaka/">Discuss a project with Mike ↗</a></section></main><footer class="wrap"><span>Mike Hamanaka / Hamanaka Software Factory</span><a href="assets/factory-stories/stories.json">Source notes &amp; image provenance</a><a href="assets/factory-process-v3.gif">Open the animation</a></footer><script src="assets/factory-stories.js" defer></script></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--encode', action='store_true', help='Encode images and the size-limited GIF')
    args = parser.parse_args()
    data = json.loads((ASSETS / 'stories.json').read_text())
    stories = data['repositories']
    stories.sort(key=lambda s: s['display_order'])
    data['motion_revision'] = 2
    if args.encode:
        for name in ['factory-cover'] + [s['name'] for s in stories] + [f'details/ai-dashboard-{s[0]}' for s in DETAILS]:
            original = ASSETS / f'{name}.png'
            if not original.exists():
                raise SystemExit(f'Missing generated image: {name}')
            subprocess.run(['cwebp', '-quiet', '-q', '88', '-resize', '1120', '630',
                            str(original), '-o', str(ASSETS / f'{name}.webp')], check=True)
        with tempfile.TemporaryDirectory(prefix='factory-gif-') as temporary:
            temp = Path(temporary)
            featured = ['ai-dashboard', 'panther-intent-capture', 'el-hidratador',
                        'taskrivet', 'el-verificador', 'the-chronicler', 'murmuration', 'scratch-kitchen']
            motion = json.loads((ASSETS / 'motion.json').read_text())
            if not motion.get('complete') or len(motion['projects']) != len(stories) or {item['name'] for item in motion['projects']} != {s['name'] for s in stories}:
                raise SystemExit('Every selected project must have a verified animation before building the overview')
            for item in motion['projects']:
                if hashlib.sha256((ROOT / item['file']).read_bytes()).hexdigest() != item['sha256']:
                    raise SystemExit(f'Animation changed after validation: {item["name"]}')
            motion_by_name = {item['name']: item for item in motion['projects']}
            inputs = []
            graph = []
            fps = 15
            overview_speed = 2
            for i, name in enumerate(featured):
                inputs.extend(['-ignore_loop', '1', '-i', ASSETS / f'{name}.gif'])
                graph.append(f'[{i}:v]settb=AVTB,setpts=(PTS-STARTPTS)/{overview_speed},fps={fps},scale=720:459,format=yuv444p,settb=AVTB[v{i}]')
            duration = motion_by_name[featured[0]]['duration_ms'] / 1000 / overview_speed
            prior = 'v0'
            transition = 0.3
            for i, name in enumerate(featured[1:], 1):
                effect = 'wipeup' if name == 'murmuration' else 'slideleft'
                graph.append(f'[{prior}][v{i}]xfade=transition={effect}:duration={transition}:offset={duration-transition:.3f}[x{i}]')
                prior = f'x{i}'
                duration += motion_by_name[name]['duration_ms'] / 1000 / overview_speed - transition
            ffmpeg(*inputs, '-filter_complex_threads', '1', '-filter_complex', ';'.join(graph),
                   '-map', f'[{prior}]', '-c:v', 'ffv1', '-an', temp / 'overview.mkv')
            gif = temp / 'candidate.gif'
            for width, colors, frame_rate in [(720, 96, 15), (680, 80, 15), (640, 64, 12), (600, 64, 10)]:
                scale = f'fps={frame_rate},scale={width}:-2:flags=lanczos'
                ffmpeg('-i', temp / 'overview.mkv', '-vf', f'{scale},palettegen=max_colors={colors}:stats_mode=full', '-frames:v', '1', temp / 'palette.png')
                ffmpeg('-i', temp / 'overview.mkv', '-i', temp / 'palette.png', '-filter_complex_threads', '1', '-lavfi', f'[0:v]{scale}[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle', '-fps_mode', 'vfr', '-loop', '0', gif)
                print(f'Overview candidate: {width}px, {colors} colors, {frame_rate}fps, {gif.stat().st_size:,} bytes', flush=True)
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
                if len(delays) < 150 or abs(sum(delays) - duration * 1000) > 500:
                    raise SystemExit(f'Unexpected GIF timing: {len(delays)} frames / {sum(delays)} ms')
            (ROOT / 'assets/factory-process-v3.gif').write_bytes(gif.read_bytes())
            # The versioned still describes the conceptual factory, not a software screenshot.
            ffmpeg('-i', ASSETS / 'factory-cover.png', '-vf', 'scale=1120:630', '-frames:v', '1', ROOT / 'assets/factory-process-v3-still.png')
            data['animation'] = {'file': 'assets/factory-process-v3.gif', 'bytes': gif.stat().st_size,
                'sha256': hashlib.sha256(gif.read_bytes()).hexdigest(), 'size_budget_bytes': 4_000_000,
                'featured_projects': featured, 'gallery_projects': len(stories), 'width': width,
                'delivery_fps': frame_rate,
                'overview_speed': overview_speed,
                'palette_colors': colors, 'encoded_frames': len(delays), 'duration_ms': sum(delays),
                'transitions': 'Slide between related workflows; wipe into independent experiments at the end',
                'frame_delays_ms': delays, 'mode': 'Illustrated project sequences; not recordings of software execution'}
        for story in stories:
            original = ASSETS / f"{story['name']}.png"
            story['image'] = {'file': f"assets/factory-stories/{story['name']}.png",
                'preview': f"assets/factory-stories/{story['name']}.webp", 'kind': 'AI-generated illustration',
                'sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
                'preview_sha256': hashlib.sha256((ASSETS / f"{story['name']}.webp").read_bytes()).hexdigest()}
            story['motion'] = motion_by_name[story['name']]
        data['dashboard_details'] = [
            {'slug': slug, 'title': title, 'file': f'assets/factory-stories/details/ai-dashboard-{slug}.png',
             'sha256': hashlib.sha256((ASSETS/f'details/ai-dashboard-{slug}.png').read_bytes()).hexdigest(),
             'preview': f'assets/factory-stories/details/ai-dashboard-{slug}.webp',
             'preview_sha256': hashlib.sha256((ASSETS/f'details/ai-dashboard-{slug}.webp').read_bytes()).hexdigest(),
             'source': stories[0]['source'], 'kind': 'Private project concept from published categories'}
            for slug,title,_,_ in DETAILS]
        data['cover'] = {'file': 'assets/factory-stories/factory-cover.png',
            'sha256': hashlib.sha256((ASSETS/'factory-cover.png').read_bytes()).hexdigest(),
            'preview': 'assets/factory-stories/factory-cover.webp',
            'preview_sha256': hashlib.sha256((ASSETS/'factory-cover.webp').read_bytes()).hexdigest(),
            'kind': 'AI-generated conceptual factory illustration'}
    (ASSETS / 'stories.json').write_text(json.dumps(data, indent=2) + '\n')
    (ROOT / 'factory.html').write_text(render(stories))
    print(f'Built illustrated workflow page for {len(stories)} selected projects.')
    if 'animation' in data:
        print(json.dumps({k:v for k,v in data['animation'].items() if k != 'frame_delays_ms'}, indent=2))


if __name__ == '__main__':
    main()
