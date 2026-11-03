"""Compose an editorial film from pinned, unmodified software captures.

Requires Pillow. No live software activity is synthesized. Original image bytes
are hash-checked before composition; framing/transition motion is editorial.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
W, H = 1280, 820
BG = '#091b20'
PAPER = '#f1eee4'
MUTED = '#9fb5b5'
LIME = '#d6eea8'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
# Linux development/CI can use the same installed alternative family.
if not Path(FONT).exists():
    FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

sources = {s['repo']: s for s in json.loads((ASSETS / 'work/sources.json').read_text())}
images = {}
for name, s in sources.items():
    path = ASSETS / 'work' / s['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != s['sha256']:
        raise ValueError(f'Capture provenance mismatch: {name}')
    images[name] = Image.open(path).convert('RGB')

scenes = [
    ('murmuration', 'EXPLORE', ['Make the', 'interface', 'feel alive.'], 'Browser graphics / artificial life', 'Published browser toy preview.'),
    ('panther-intent-capture', 'CAPTURE', ['Turn friction', 'into a clear', 'request.'], 'Browser extension / intent capture', 'Actual options page; synthetic capture.'),
    ('taskrivet', 'WORK', ['Keep context', 'with the', 'work.'], 'Desktop app / agent workspaces', 'Desktop alpha; synthetic task data.'),
    ('meter-mouse-garden', 'OBSERVE', ['Make AI', 'usage easy', 'to read.'], 'Interface design / usage visibility', 'Static prototype; fixture data.'),
    ('el-verificador', 'VERIFY', ['Turn a failed', 'check into', 'a next step.'], 'Developer tools / verification', 'Actual CLI demo; detail crop.'),
    ('fluxrecord', 'RECORD', ['Keep the', 'decision', 'with its proof.'], 'Developer tools / work records', 'Actual CLI demo; synthetic task; detail crop.'),
    ('lineasflow', 'CONNECT', ['Explore the', 'systems', 'boundary.'], 'Go / edge synchronization experiment', 'Test capture; not fleet deployment evidence.'),
]

def base(chapter, title):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((34, 25), 'MIKE HAMANAKA', font=font(18, True), fill=PAPER)
    d.text((256, 27), 'SOFTWARE FACTORY', font=font(15), fill=MUTED)
    d.text((960, 27), title, font=font(14, True), fill=LIME)
    d.line((34, 64, 1246, 64), fill='#365052', width=1)
    d.text((34, 783), 'CONSULTING  /  CONTRACT ENGINEERING', font=font(15, True), fill=LIME)
    d.text((848, 783), 'hamanakam1.github.io', font=font(18, True), fill=PAPER)
    d.text((1193, 783), chapter, font=font(14), fill=MUTED)
    return im

def paste_screen(im, name, box, crop=None):
    x, y, w, h = box
    pic = images[name]
    if crop:
        a, b, c, e = crop
        pic = pic.crop((int(a*pic.width), int(b*pic.height), int(c*pic.width), int(e*pic.height)))
    pic = ImageOps.contain(pic, (w, h), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x-3,y-3,x+w+3,y+h+3), radius=11, fill='#223b40', outline='#4c6261', width=1)
    im.paste(pic, (x+(w-pic.width)//2, y+(h-pic.height)//2))


def strip(im, active):
    d=ImageDraw.Draw(im)
    for i,(name,label,*_) in enumerate(scenes):
        x=34+i*174
        color=LIME if i==active else '#274146'
        d.rounded_rectangle((x,701,x+159,751),radius=8,fill=color)
        d.text((x+12,710),f'{i+1:02d}',font=font(12,True),fill=BG if i==active else MUTED)
        d.text((x+12,729),label,font=font(12,True),fill=BG if i==active else MUTED)


def project_scene(i, detail=False):
    name,label,lines,sub,boundary=scenes[i]
    im=base(f'{i+1}/7','SELECTED SOFTWARE')
    d=ImageDraw.Draw(im)
    d.text((34,95),f'{i+1:02d}  /  {label}',font=font(17,True),fill=LIME)
    for j,line in enumerate(lines):
        d.text((34,154+j*59),line,font=font(45,True),fill=PAPER)
    # A deliberate short caption keeps a project intelligible at README size.
    short={'panther-intent-capture':'Panther Intent Capture','meter-mouse-garden':'MeterMouseGarden','el-verificador':'El Verificador','lineasflow':'LineasFlows','taskrivet':'Taskrivet','murmuration':'Murmuration','fluxrecord':'fluxrecord'}[name]
    d.text((34,380),short,font=font(23,True),fill=LIME)
    # Wrap editorial explanatory line, leaving source screenshots intact.
    words=sub.split(); line=''; yy=421
    for word in words:
        nextline=(line+' '+word).strip()
        if d.textlength(nextline,font=font(18))>300:
            d.text((34,yy),line,font=font(18),fill=MUTED);yy+=28;line=word
        else: line=nextline
    d.text((34,yy),line,font=font(18),fill=MUTED)
    d.text((34,584),'REAL CAPTURE',font=font(13,True),fill=PAPER)
    d.text((34,610),'Editorial sequence.',font=font(16),fill=MUTED)
    d.text((34,635),'Not a live integrated run.',font=font(16),fill=MUTED)
    crop=None
    if name in ('el-verificador','fluxrecord'):
        # Two readable regions of tall terminal capture; no output is rewritten.
        crop=(0,0.06,1,0.51) if not detail else (0,0.48,1,0.93)
    elif detail:
        crop={'murmuration':(.23,.15,.83,.86),'panther-intent-capture':(.02,.23,.99,.63),'taskrivet':(.15,.10,.98,.89),'meter-mouse-garden':(.15,.12,.99,.91),'lineasflow':(0,0,1,1)}[name]
    paste_screen(im,name,(380,105,864,525),crop)
    label_extra='  /  CLOSE-UP' if detail and name not in ('lineasflow','el-verificador','fluxrecord') else ''
    d.text((380,650),boundary+label_extra,font=font(15),fill=PAPER)
    strip(im,i)
    return im


def cover(end=False):
    im=base('REEL','REAL SOFTWARE / 7 PROJECTS')
    d=ImageDraw.Draw(im)
    if not end:
        for j,line in enumerate(['Ideas into','interfaces.','Work into proof.']):
            d.text((34,113+j*67),line,font=font(53,True),fill=PAPER if j<2 else LIME)
        d.text((36,341),'Explore the software I build.',font=font(23),fill=MUTED)
    else:
        for j,line in enumerate(['Bring one','bottleneck.','Build a next step.']):
            d.text((34,113+j*67),line,font=font(51,True),fill=PAPER if j<2 else LIME)
        d.text((36,341),'AI workflows / tools / local systems',font=font(20),fill=MUTED)
    paste_screen(im,'murmuration',(631,105,610,449),(.10,.08,.94,.94))
    paste_screen(im,'taskrivet',(34,403,555,276))
    paste_screen(im,'meter-mouse-garden',(756,426,455,257),(.13,.07,1,.89))
    d.text((34,706),'Actual repository captures. Demo and fixture data are identified in each chapter.',font=font(17),fill=MUTED)
    d.text((34,739),'SEE THE WORK.  DISCUSS A PAID PROJECT.',font=font(16,True),fill=LIME)
    return im

# Holds keep each chapter readable. Brief crossfades and a cut to detail create
# motion without pretending that captured applications are running live.
keyframes=[(cover(),3000,'cover')]
for i,(name,*_) in enumerate(scenes):
    keyframes.append((project_scene(i),2100,name+'-overview'))
    keyframes.append((project_scene(i,True),1700,name+'-detail'))
keyframes.append((cover(True),3500,'contact'))
frames=[]; durations=[]
for i,(frame,duration,label) in enumerate(keyframes):
    if i:
        previous=keyframes[i-1][0]
        # A short five-step dissolve, then a long readable hold.
        for step in range(1,5):
            frames.append(Image.blend(previous,frame,step/5));durations.append(70)
    frames.append(frame);durations.append(duration)
for step in range(1,5):
    frames.append(Image.blend(keyframes[-1][0],keyframes[0][0],step/5));durations.append(70)

out=ASSETS/'work'
for i in range(6):
    # Update the existing tracked frame names with representative new chapters.
    keyframes[1+i*2][0].save(out/f'frame-{i+1:02d}.png')
keyframes[0][0].save(ASSETS/'factory-tour-still.png')
# Consistent palette limits flicker and allows delta compression.
palette_source=Image.new('RGB',(320*4,205*4))
for i,(frame,_,_) in enumerate(keyframes):
    palette_source.paste(frame.resize((320,205)),((i%4)*320,(i//4)*205))
palette=palette_source.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
quantized=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
quantized[0].save(ASSETS/'factory-tour.gif',save_all=True,append_images=quantized[1:],duration=durations,loop=0,optimize=True,disposal=1)
# Compact human-review storyboard and machine-readable timing/provenance receipt.
board=Image.new('RGB',(1280,820),PAPER)
for i,(frame,_,_) in enumerate(keyframes):
    board.paste(frame.resize((320,205)),((i%4)*320,(i//4)*205))
board.save(out/'reel-storyboard.jpg',quality=94)
receipt={'version':2,'size':[W,H],'frames':len(frames),'duration_ms':sum(durations),'chapters':[s[0] for s in scenes],'transitions':'Editorial crossfades and source detail crops; not live application behavior','gif_bytes':(ASSETS/'factory-tour.gif').stat().st_size,'gif_sha256':hashlib.sha256((ASSETS/'factory-tour.gif').read_bytes()).hexdigest(),'keyframes':[{'label':label,'hold_ms':ms} for _,ms,label in keyframes]}
(out/'reel.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
