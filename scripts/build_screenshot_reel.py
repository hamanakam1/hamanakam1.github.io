import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
W,H=1280,820
BG='#102b2b'; FG='#f5f0e5'; ACCENT='#d6eea8'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(size,bold=False): return ImageFont.truetype(BOLD if bold else FONT,size)
sources=json.loads((ASSETS/'work/sources.json').read_text())
frames=[]
for i,s in enumerate(sources):
    frame=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(frame)
    d.text((40,24),'MIKE HAMANAKA  /  SOFTWARE IN PRACTICE',font=font(17,True),fill=ACCENT)
    d.text((40,60),s['title'],font=font(34,True),fill=FG)
    d.text((40,108),s['repo'],font=font(20),fill=FG)
    img=Image.open(ASSETS/'work'/s['file']).convert('RGB')
    if img.height > img.width * 0.95:
        img=img.crop((0,0,img.width,int(img.width/1.8)))
        d.text((1000,110),'DETAIL CROP',font=font(14,True),fill=ACCENT)
    img=ImageOps.contain(img,(1200,570),Image.Resampling.LANCZOS)
    frame.paste(img,((W-img.width)//2,155+(570-img.height)//2))
    d.text((40,747),s['boundary'],font=font(18),fill=FG)
    d.text((40,779),'AI workflow tooling  /  Developer tools  /  Local systems',font=font(16),fill=ACCENT)
    d.text((1150,779),f'{i+1:02d} / 06',font=font(16,True),fill=ACCENT)
    frame.save(ASSETS/'work'/f'frame-{i+1:02d}.png')
    frames.append(frame)
frames[0].save(ASSETS/'factory-tour-still.png')
frames[0].save(ASSETS/'factory-tour.gif',save_all=True,append_images=frames[1:],duration=[5000]*6,loop=0,optimize=True,disposal=2)
print('Built 6 screenshot frames, a 30-second GIF, and a reduced-motion still.')

