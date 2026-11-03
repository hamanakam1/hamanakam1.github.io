"""Assemble conceptual project motion over the unchanged, reviewed illustrations.

Native vector overlays show input, transformation, and reviewable output. They
are explanatory animation, not execution footage or live telemetry. All source
PNGs remain unchanged; FFmpeg encodes and Pillow independently decodes each GIF.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/factory-stories'
WIDTH, ART_HEIGHT, HEIGHT = 720, 405, 459
FPS, FRAMES, DURATION_MS = 30, 180, 6000
SIZE_LIMIT, DASHBOARD_LIMIT = 1_000_000, 3_000_000
RECIPE = 'project-objects-v2-three-active-regions-30fps-six-seconds-four-dashboard-chapters'
INK, IVORY, LIME = '#173F40', '#FAF6ED', '#D9F252'
CHAPTERS = ('work', 'inference', 'resources', 'review')


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


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def rgba(color: str, alpha: int = 255) -> tuple:
    return (*tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)), alpha)


def sprite(kind: str, phase: float, color: str, size: int = 42) -> Image.Image:
    """Distinct native objects, rather than reusing a moving paper rectangle."""
    scale = 2
    image = Image.new('RGBA', (64 * scale, 64 * scale))
    draw = ImageDraw.Draw(image)
    def line(points, fill=INK, width=2):
        draw.line([(round(x*scale), round(y*scale)) for x,y in points], fill=fill, width=width*scale, joint='curve')
    def box(coords, fill=IVORY, outline=INK, radius=3):
        draw.rounded_rectangle(tuple(round(v*scale) for v in coords), radius=radius*scale, fill=fill, outline=outline, width=2*scale)
    def circle(coords, fill=IVORY, outline=INK, width=2):
        draw.ellipse(tuple(round(v*scale) for v in coords), fill=fill, outline=outline, width=width*scale)
    def poly(points, fill=LIME):
        draw.polygon([(round(x*scale),round(y*scale)) for x,y in points], fill=fill, outline=INK, width=2*scale)
    window = {'terminal','browser','dashboard','web-shell','gallery','plugin','explanation'}
    graph = {'node','topology','telemetry','event-state','scan','vector','trajectory','state','clearance'}
    papers = {'evidence','receipt','ledger','records','record','observation','lesson','article','verdict','trace','proposal','handoff','result','checkpoint','claim','code','rules','planning','change','project','contact','failure'}
    if kind in window:
        box((5,10,59,51), fill=INK if kind=='terminal' else IVORY)
        line([(6,20),(58,20)], fill=color)
        for x in (12,18,24): circle((x-1,14,x+1,16),fill=LIME,outline=None)
        if kind=='terminal':
            line([(13,28),(18,32),(13,36)],fill=LIME)
            length = 8 + round(17*(phase%1))
            line([(23,33),(23+length,33)],fill=LIME)
            if phase%1 < .7: box((18+length,30,21+length,37),fill=LIME,outline=None,radius=0)
            line([(12,43),(37,43)],fill='#78BDB8',width=1)
        elif kind=='browser':
            box((12,27,49,43),fill='#D8ECE6',outline=color,radius=1)
            box((15,30,27+int(14*(phase%1)),39),fill=LIME,outline=None,radius=0)
            poly([(44,36),(45,49),(49,45),(54,46)],fill=IVORY)
        elif kind in {'dashboard','gallery'}:
            for j in range(3): box((12+j*14,27,22+j*14,44),fill=LIME if j==int(phase*3)%3 else '#D8ECE6',outline=color,radius=1)
        elif kind=='plugin':
            box((21,27,43,45),fill=LIME); circle((28,23,36,31),fill=LIME)
        else:
            for y in (28,35,42): line([(13,y),(46-(y%3)*5,y)],fill=color)
    elif kind in graph:
        nodes=[(13,35),(31,14),(52,28),(42,51)]
        for a,b in [(0,1),(1,2),(2,3),(3,0),(0,2)]: line([nodes[a],nodes[b]],fill=color,width=2)
        for j,(x,y) in enumerate(nodes): circle((x-5,y-5,x+5,y+5),fill=LIME if j==int(phase*4)%4 else IVORY)
        u=phase%1; x=13+39*u; y=35-7*u; circle((x-3,y-3,x+3,y+3),fill=LIME,outline=INK,width=1)
    elif kind in {'gauge','usage','hardware'}:
        box((8,8,56,54),fill=IVORY)
        draw.arc((15*scale,17*scale,49*scale,51*scale),180,360,fill=color,width=4*scale)
        angle=math.pi + math.pi*(.5+.36*math.sin(phase*math.tau))
        line([(32,35),(32+18*math.cos(angle),35+18*math.sin(angle))],fill=INK,width=3)
        circle((29,32,35,38),fill=LIME)
        line([(18,46),(45,46)],fill=color)
    elif kind in {'ingredient','meal'}:
        if kind=='ingredient':
            box((7,35,57,49),fill=IVORY)
            circle((12,22,27,39),fill='#E7A858'); circle((31,20,48,38),fill=LIME)
            line([(20,23),(22,15),(28,12)],fill=color)
            line([(39,22),(35,13)],fill=color)
        else:
            draw.pieslice((8*scale,21*scale,56*scale,57*scale),0,180,fill=IVORY,outline=INK,width=2*scale)
            draw.ellipse((8*scale,25*scale,56*scale,35*scale),fill='#E7A858',outline=INK,width=2*scale)
            for x in (21,32,43): line([(x,22),(x-2+4*math.sin(phase*math.tau),17),(x,10)],fill=color,width=2)
    elif kind in {'seed','organism'}:
        if kind=='seed':
            circle((21,25,39,44),fill=LIME); line([(30,29),(31,12)],fill=color)
            draw.ellipse((30*scale,8*scale,47*scale,19*scale),fill=color)
        else:
            for j in range(5):
                a=phase*math.tau+j*2.4; x=32+15*math.cos(a);y=32+12*math.sin(a)
                poly([(x-7,y+3),(x,y-4),(x+7,y+3),(x,y)],fill=LIME)
    elif kind in {'conversation','bookmark','idea'}:
        box((7,10,55,43),fill=LIME)
        poly([(17,42),(17,52),(29,43)],fill=LIME)
        for x in (20,31,42):circle((x-2,25,x+2,29),fill=color,outline=None)
    elif kind in {'folder','packet','bundle','envelope'}:
        box((7,15,31,27),fill=LIME)
        box((6,24,57,51),fill=IVORY)
        line([(11,31),(52,31)],fill=color)
        if kind=='envelope':line([(8,26),(31,43),(55,26)],fill=color)
        else:line([(17,39),(45,39)],fill=color)
    elif kind in {'ticket','job','scenario'}:
        box((8,15,56,48),fill=LIME,radius=5)
        circle((3,27,13,37),fill=IVORY);circle((51,27,61,37),fill=IVORY)
        for y in (25,33,40):line([(19,y),(42 if y!=40 else 34,y)],fill=INK)
    elif kind in papers:
        box((14,12,51,56),fill='#B9DAD2')
        box((9,7,46,50),fill=IVORY)
        for j,y in enumerate((20,30,40)):
            circle((16,y-2,20,y+2),fill=LIME if j<=int(phase*3)%3 else color,outline=INK,width=1)
            line([(25,y),(38,y)],fill=color)
        # Output remains an inspectable document, never an automatic Done badge.
        if kind in {'verdict','observation','evidence','claim'}:
            circle((33,32,50,49),fill=IVORY,outline=color)
            line([(47,46),(56,55)],fill=INK,width=3)
    else:
        raise ValueError(f'Unrecognized reviewed motion symbol: {kind}')
    return image.resize((size,size),Image.Resampling.LANCZOS)


def put(canvas: Image.Image, kind: str, x: float, y: float, phase: float, color: str,
        size: int = 42, alpha: float = 1.0, angle: float = 0) -> None:
    icon=sprite(kind,phase,color,size)
    if angle: icon=icon.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    if alpha<1: icon.putalpha(icon.getchannel('A').point(lambda a:int(a*alpha)))
    canvas.alpha_composite(icon,(round(x-icon.width/2),round(y-icon.height/2)))


def motion_overlay(story: dict, time: float, duration: float = 6, chapter: int | None = None) -> Image.Image:
    layer=Image.new('RGBA',(WIDTH,HEIGHT)); d=ImageDraw.Draw(layer)
    color=story.get('color','#0F9D92'); phase=time/6; cyc=math.tau
    before,after=story['motion_symbols']['input'],story['motion_symbols']['output']
    if chapter is not None:
        before,after=[('ticket','terminal'),('node','result'),('usage','gauge'),('evidence','ledger')][chapter]
    # Input objects converge from separate origins; outputs fan out for inspection.
    for j in range(3):
        u=((time+j*(2/3))%2)/2; p=ease(u)
        x=70+142*p; y=220+(j-1)*24-17*math.sin(math.pi*p)
        alpha=min(1,u*7,(1-u)*7)
        put(layer,before,x,y,time*.5+j,color,36,alpha,angle=(1-p)*(-9+j*9))
    for j in range(3):
        u=((time+j*.63)%3.0)/3; p=ease(u)
        x=482+135*p; y=225+(j-1)*35*p-10*math.sin(math.pi*p)
        alpha=min(1,u*8,(1-u)*6)
        put(layer,after,x,y,time*.5+j,color,37,alpha,angle=(j-1)*8*p)
    # Processing focus: two rotating arcs, moving scan, changing cursor/objects.
    cx,cy=355,225
    if chapter==0:cx=430
    elif chapter==3:cx=435
    for radius,offset in [(40,0),(48,145)]:
        a=(time*60+offset)%360
        d.arc((cx-radius,cy-radius,cx+radius,cy+radius),a,a+110,fill=rgba(color,210),width=3)
        px=cx+radius*math.cos(math.radians(a+110));py=cy+radius*math.sin(math.radians(a+110))
        d.ellipse((px-3,py-3,px+3,py+3),fill=rgba(LIME),outline=rgba(INK))
    scan=cy-30+60*((time*.5)%1)
    d.line((cx-34,scan,cx+34,scan),fill=rgba(LIME,175),width=2)
    core=before if before in {'terminal','browser','node','telemetry','ingredient','seed','hardware'} else after
    put(layer,core,cx,cy,time,color,56)
    if story['name']=='taskrivet' or chapter==0:
        # Persistent terminal session panes run independently.
        put(layer,'terminal',cx-40,cy+33,time*.5,color,35)
        put(layer,'terminal',cx+40,cy+33,time*.5+.4,color,35)
    if story['name']=='murmuration':
        for j in range(9):
            a=time*(cyc/6)+j*2.4; x=360+170*math.sin(a+.6*math.cos(a)); y=225+36*math.cos(a)
            wing=3+3*math.sin(time*cyc+j)
            d.line((x-7,y+wing,x,y-2,x+7,y+wing),fill=rgba(color,220),width=2)
            d.ellipse((x-2,y-3,x+2,y+1),fill=rgba(LIME))
    # Along the upper body, short trails join the three animated regions.
    for j in range(7):
        u=((time/6+j/7)%1); x=165+390*u; y=177+17*math.sin(u*cyc)
        for tail in range(3):
            tx=x-tail*5; d.ellipse((tx-2,y-2,tx+2,y+2),fill=rgba(color,170-tail*45))
    # Stage captions occur above OR below different illustrations. These stable
    # bands protect both layouts; all body activity is confined to the middle.
    layer.paste((0,0,0,0),(0,0,WIDTH,145))
    layer.paste((0,0,0,0),(0,280,WIDTH,405))
    # Appended conveyor carries project-specific input, processing, then output.
    d.rectangle((0,405,720,459),fill=rgba(IVORY))
    d.line((0,405,720,405),fill=rgba(INK,70),width=1)
    d.line((72,442,650,442),fill=rgba(color,120),width=2)
    for x in (105,355,605):
        d.rounded_rectangle((x-22,448,x+22,451),radius=1,fill=rgba(color,160))
    for j in range(15):
        x=77+((j*38+time*19)%570)
        d.line((x-3,438,x,442,x-3,446),fill=rgba(color,90),width=1)
    t=time%6
    if t<.6:x=-32+137*ease(t/.6)
    elif t<1.4:x=105
    elif t<2.4:x=105+250*ease(t-1.4)
    elif t<3.2:x=355
    elif t<4.2:x=355+250*ease(t-3.2)
    elif t<5:x=605
    else:x=605+149*ease(t-5)
    kind=before if t<2.35 else core if t<3.7 else after
    put(layer,kind,x,427,time,color,36)
    station=105 if t<1.5 else 355 if t<3.5 else 605
    d.rounded_rectangle((station-22,448,station+22,451),radius=1,fill=rgba(LIME))
    # Dashboard's chapter progress is symbolic, not fabricated numeric telemetry.
    if chapter is not None:
        for j in range(4):
            d.rounded_rectangle((326+j*18,453,338+j*18,456),radius=1,fill=rgba(color if j==chapter else '#CBD9D3'))
    return layer


def load_art(path: Path) -> Image.Image:
    with Image.open(path) as im:
        art=ImageOps.contain(im.convert('RGB'),(WIDTH,ART_HEIGHT),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(WIDTH,HEIGHT),IVORY)
    canvas.paste(art,((WIDTH-art.width)//2,(ART_HEIGHT-art.height)//2))
    return canvas


def rendered_frame(story: dict, index: int, sources: list[Image.Image]) -> Image.Image:
    t=index/FPS
    if len(sources)==1:
        frame=sources[0].copy(); frame.alpha_composite(motion_overlay(story,t)); return frame.convert('RGB')
    chapter=int(t//4)%4; local=t%4
    frame=sources[chapter].copy()
    frame.alpha_composite(motion_overlay(story,local,4,chapter))
    if local>=3.6:
        # A crisp, quick wipe reveals the next chapter; all titles return whole.
        nextchapter=(chapter+1)%4; nextframe=sources[nextchapter].copy()
        nextframe.alpha_composite(motion_overlay(story,0,4,nextchapter))
        cut=round(WIDTH*ease((local-3.6)/.4))
        frame.paste(nextframe.crop((0,0,cut,HEIGHT)),(0,0))
        d=ImageDraw.Draw(frame)
        d.rectangle((max(0,cut-3),0,cut+2,HEIGHT),fill=INK)
        d.rectangle((cut+3,0,cut+7,HEIGHT),fill=LIME)
    return frame.convert('RGB')


def inspect_motion(path: Path, dashboard: bool = False) -> dict:
    unique=set();duration=0;moving=0;changed=0;prior=None
    regions={'input':(60,190,235,330),'processing':(290,180,420,335),'output':(470,175,650,340),'conveyor':(0,405,720,459)}
    region_changed={key:0 for key in regions}; headers=set();footers=set()
    with Image.open(path) as im:
        assert im.format=='GIF' and im.size==(WIDTH,HEIGHT),path
        frames=im.n_frames;loop=im.info.get('loop')
        for i in range(frames):
            im.seek(i);frame=im.convert('RGB');delay=im.info.get('duration',0)
            assert delay in (30,40),(path.name,delay)
            duration+=delay;unique.add(hashlib.sha256(frame.tobytes()).digest())
            headers.add(hashlib.sha256(frame.crop((0,0,WIDTH,145)).tobytes()).digest())
            footers.add(hashlib.sha256(frame.crop((0,280,WIDTH,405)).tobytes()).digest())
            if prior is not None:
                diff=ImageChops.difference(frame,prior)
                r,g,b=diff.split();mask=ImageChops.lighter(ImageChops.lighter(r,g),b)
                count=sum(mask.histogram()[1:]);changed+=count;moving+=count>0
                for key,bounds in regions.items():region_changed[key]+=sum(mask.crop(bounds).histogram()[1:])
            prior=frame
    expected=480 if dashboard else FRAMES;expected_duration=16000 if dashboard else DURATION_MS
    assert frames==expected and duration==expected_duration,(frames,duration)
    assert loop==0 and len(unique)>=expected*.9 and moving>=expected*.9
    assert all(v>10000 for v in region_changed.values()),region_changed
    if not dashboard: assert len(headers)==len(footers)==1,'Protected artwork labels changed'
    limit=DASHBOARD_LIMIT if dashboard else SIZE_LIMIT
    assert path.stat().st_size<limit,(path.name,path.stat().st_size,limit)
    return {'frames':frames,'duration_ms':duration,'loop':loop,'unique_decoded_frames':len(unique),
            'moving_frame_transitions':moving,'changed_motion_pixels':changed,
            'motion_region_changed_pixels':region_changed,'protected_labels_static':not dashboard,
            'protected_artwork_bands':[[0,0,720,145],[0,280,720,405]] if not dashboard else [],
            'artwork_region_static':False,'source_artwork_files_unchanged':True}


def source_records(story: dict) -> list[dict]:
    name=story['name']
    paths=[ASSETS/'details'/f'ai-dashboard-{c}.png' for c in CHAPTERS] if name=='ai-dashboard' else [ASSETS/f'{name}.png']
    return [{'file':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in paths]


def recipe_signature(story: dict, sources: list[dict]) -> str:
    config={'recipe':RECIPE,'script_sha256':digest(Path(__file__)),'symbols':story['motion_symbols'],
            'color':story.get('color'),'chapters':sources if story['name']=='ai-dashboard' else [],'fps':FPS}
    return hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()


def build_one(story: dict, previous: dict | None) -> dict:
    name=story['name'];source=ASSETS/f'{name}.png';output=ASSETS/f'{name}.gif'
    dashboard=name=='ai-dashboard'
    paths=[ASSETS/'details'/f'ai-dashboard-{c}.png' for c in CHAPTERS] if dashboard else [source]
    for p in paths:
        if not p.is_file():raise FileNotFoundError(f'Required scene unavailable: {p}')
    sources_sha=[{'file':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in paths]
    source_sha=digest(source)
    recipe_sha=recipe_signature(story,sources_sha)
    if previous and output.exists() and previous.get('source_sha256')==source_sha \
            and previous.get('recipe_sha256')==recipe_sha and previous.get('sha256')==digest(output):
        return {**previous,**inspect_motion(output,dashboard)}
    frames=480 if dashboard else FRAMES;limit=DASHBOARD_LIMIT if dashboard else SIZE_LIMIT
    sources=[load_art(p) for p in paths]
    with tempfile.TemporaryDirectory(prefix='.project-motion-',dir=ASSETS) as temporary:
        raw=Path(temporary)/'frames.rgb';candidate=Path(temporary)/f'{name}.gif'
        with raw.open('wb') as stream:
            for i in range(frames):stream.write(rendered_frame(story,i,sources).tobytes())
        palette=Path(temporary)/'palette.png'
        for colors in (80,64,48):
            # Two passes avoid retaining hundreds of full RGB frames in the
            # palette split graph, especially for the 480-frame dashboard.
            raw_input=['-f','rawvideo','-pixel_format','rgb24','-video_size',f'{WIDTH}x{HEIGHT}',
                       '-framerate',str(FPS),'-i',str(raw)]
            base=['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-filter_complex_threads','1']
            palette_command=base+raw_input+['-vf',f'palettegen=max_colors={colors}:stats_mode=full',
                                           '-frames:v','1','-threads','1',str(palette)]
            result=subprocess.run(palette_command,capture_output=True,text=True)
            if result.returncode or not palette.is_file():
                raise RuntimeError(f'{name}: palette failed: {result.stderr[-2000:]}')
            command=base+raw_input+['-i',str(palette),'-lavfi','paletteuse=dither=none:diff_mode=rectangle',
                                    '-frames:v',str(frames),'-r',str(FPS),'-loop','0','-final_delay','3',str(candidate)]
            result=subprocess.run(command,capture_output=True,text=True)
            if result.returncode or not candidate.exists() or candidate.stat().st_size<1000:
                raise RuntimeError(f'{name}: FFmpeg failed or returned empty output: {result.stderr[-2000:]}')
            if candidate.stat().st_size<limit:break
        else:raise RuntimeError(f'{name}: cannot meet {limit}-byte delivery limit; last size {candidate.stat().st_size}')
        inspected=inspect_motion(candidate,dashboard)
        assert digest(source)==source_sha and all(digest(ROOT/p['file'])==p['sha256'] for p in sources_sha)
        result={'name':name,'file':f'assets/factory-stories/{name}.gif','source_file':f'assets/factory-stories/{name}.png',
                'source_sha256':source_sha,'scene_sources':sources_sha,'sha256':digest(candidate),'bytes':candidate.stat().st_size,
                'width':WIDTH,'height':HEIGHT,'fps':FPS,'palette_colors':colors,'size_limit_bytes':limit,
                'recipe':RECIPE,'recipe_sha256':recipe_sha,'motion_symbols':story['motion_symbols'],
                'motion_motif':story['motion_motif'],'chapters':list(CHAPTERS) if dashboard else [],**inspected}
        os.replace(candidate,output)
        return result


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    selection=parser.add_mutually_exclusive_group()
    selection.add_argument('--name',help='Build one reviewed project')
    selection.add_argument('--available',action='store_true',help='Explicitly skip missing PNGs')
    args=parser.parse_args()
    stories=json.loads((ASSETS/'stories.json').read_text())['repositories']
    names=[s['name'] for s in stories]
    assert len(names)==len(set(names)) and all(re.fullmatch(r'[A-Za-z0-9_.-]+',n) for n in names)
    assert not any(s.get('fork') for s in stories)
    assert all(s.get('motion_symbols') and s.get('motion_motif') for s in stories),'Reviewed motion map required'
    if args.name and args.name not in names:parser.error('Requested project is outside the reviewed portfolio')
    missing=[n for n in names if not (ASSETS/f'{n}.png').is_file()]
    if args.name in missing:parser.error(f'Missing source PNG: {args.name}')
    if missing and not(args.available or args.name):parser.error('Final build requires all PNGs: '+', '.join(missing))
    chosen=[s for s in stories if s['name']==args.name] if args.name else [s for s in stories if s['name'] not in missing]
    manifest_path=ASSETS/'motion.json'
    old=json.loads(manifest_path.read_text()) if manifest_path.exists() else {'projects':[]}
    # Preserve valid in-progress records. Completion is explicitly tied to this recipe.
    by_name={s['name']:s for s in stories}
    built={}
    for record in old['projects']:
        name=record['name']
        if name not in by_name or name in missing or not (ASSETS/f'{name}.gif').exists():continue
        if record.get('source_sha256')!=digest(ASSETS/f'{name}.png'):continue
        if record.get('sha256')!=digest(ASSETS/f'{name}.gif'):continue
        if record.get('recipe_sha256')!=recipe_signature(by_name[name],source_records(by_name[name])):continue
        built[name]=record
    for story in chosen:
        name=story['name'];result=build_one(story,built.get(name));built[name]=result
        manifest={'schema':'project-motion.v2','generated_at':datetime.now(timezone.utc).isoformat(),
                  'boundary':'Conceptual project-specific motion over generated illustrations; not software execution footage or live telemetry.',
                  'expected_projects':len(names),'complete':len(built)==len(names),'missing_source_images':missing,
                  'projects':[built[n] for n in names if n in built]}
        atomic_json(manifest_path,manifest)
        print(f'{name}: {result["frames"]} frames, {result["duration_ms"]} ms, {result["bytes"]:,} bytes, {result["unique_decoded_frames"]} distinct frames',flush=True)
    print(json.dumps({'complete':len(built)==len(names),'built':len(built),'expected':len(names),'missing':missing}))


if __name__=='__main__':
    main()
