"""Refresh the public catalogue and gallery from reviewed local manifests."""
import collections
import html
import json
import re
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=html.escape
public_snapshot=json.loads((ROOT/'assets/work/public-repositories.json').read_text())
public=public_snapshot['repositories']
story_order=json.loads((ROOT/'assets/factory-stories/story-order.json').read_text())
order_by_name={item['name']:item['order'] for item in story_order['repositories']}
public.sort(key=lambda item:order_by_name[item['name']])
captured=date.fromisoformat(public_snapshot['observed_on'])
captured_label=f'{captured.day} {captured:%B %Y}'
selected=json.loads((ROOT/'assets/repositories.json').read_text())['repositories']
assert all(not r['private'] for r in public)
assert all(not r['fork'] for r in public)
assert {r['name'] for r in public}=={r['name'] for r in selected if not r['isPrivate']}
page=(ROOT/'work.html').read_text()
cards=[]
for r in public:
    kind=r['category'];maturity=r['maturity']
    demo=''
    if r['name']=='murmuration':demo='<p><a href="https://hamanakam1.github.io/murmuration/">Play the browser demo ↗</a></p>'
    cards.append(f'<article class="repo" data-repo data-repo-name="{E(r["name"])}" data-kind="{E(kind)}"><span class="pill">{E(kind)}</span><span class="pill">{E(r["language"] or "Not reported")}</span><h3><a href="{E(r["html_url"])}">{E(r["name"])}</a></h3><p>{E(r["description"] or "Documentation and software workspace.")}</p><p><strong>{E(maturity)}</strong></p>{demo}</article>')
lang=collections.Counter(r['language'] or 'Not reported' for r in public)
colors=['#153b39','#49756c','#99ab6c','#bd843a','#684f71','#577e95','#9e5b4d','#71824c','#a5a198','#384f6c']
bars=''.join(f'<span style="width:{n/len(public)*100:.4f}%;background:{colors[i%len(colors)]}" title="{E(k)}: {n}"></span>' for i,(k,n) in enumerate(lang.most_common()))
legend=''.join(f'<span><i style="background:{colors[i%len(colors)]}"></i>{E(k)} {n}</span>' for i,(k,n) in enumerate(lang.most_common()))
section=f'''<section class="rule" id="inventory"><div class="intro"><div><p class="kicker">DEEPER TECHNICAL REVIEW</p><h2>The public workshop.</h2></div><p>{len(public)} public repositories in a curated {len(selected)}-project portfolio, alongside {len(selected)-len(public)} private summaries. Forks and client-specific workspaces are excluded. Counts describe this selection and source access, not the whole GitHub account or customer deployments.</p></div><p class="note">Primary repository languages from GitHub metadata, captured {captured_label}. This chart counts repositories, not lines of code or proficiency.</p><div class="bar" role="img" aria-label="Primary language counts: {E(', '.join(f'{k} {n}' for k,n in lang.most_common()))}">{bars}</div><div class="legend">{legend}</div><div class="inventory-controls"><label>Search projects<input id="repo-search" type="search" placeholder="Try workflow, Python, or Taskrivet"></label><label>Area<select id="repo-filter"><option value="all">All public projects</option><option value="workflow">Workflows</option><option value="evidence">Evidence</option><option value="edge">Edge systems</option><option value="data">Data and product experiments</option><option value="interface">Interfaces and publishing</option></select></label><button type="button" id="clear-search" class="button secondary">Clear filters</button></div><p id="repo-count" class="inventory-count" role="status" aria-live="polite">{len(public)} public repositories</p><p hidden id="no-results">No matching projects. Clear the filters to see the workshop again.</p><div class="repo-grid">{''.join(cards)}</div></section>'''
page,n=re.subn(r'<section class="rule" id="inventory">.*?</section>',lambda m:section,page,flags=re.S);assert n==1
page=re.sub(r'(?:complete|curated) \d+-repository role map',f'curated {len(selected)}-repository role map',page)
sources=json.loads((ROOT/'assets/work/sources.json').read_text());slides=[]
for i,s in enumerate(sources):
    slides.append(f'<div data-slide><div class="gallery"><a class="screen-box" href="assets/work/{E(s["file"])}" aria-label="Open the full {E(s["repo"])} screenshot"><img src="assets/work/{E(s["file"])}" alt="{E(s["title"]+" — "+s["boundary"])}" loading="lazy" width="1200" height="750"></a><div><p class="kicker">SOFTWARE CAPTURE / {i+1:02d}</p><h3>{E(s["title"])}</h3><p>{E(s["repo"])}</p><p class="caption">{E(s["boundary"])}</p><a href="{E(s["source_page"])}">Inspect the project and its limits ↗</a></div></div></div>')
start='<div data-gallery tabindex="0" role="region" aria-label="Software screenshot gallery">'
left,rest=page.split(start,1);_,right=rest.split('<div class="controls">',1)
page=left+start+''.join(slides)+'<div class="controls">'+right
page=page.replace('1 / 6</span>','1 / 7</span>').replace('All six captures','All seven captures').replace('Six published captures.','Seven published captures.').replace('Taskrivet desktop workspace, one of six published software captures in the reel','Collage of Taskrivet, Murmuration and MeterMouseGarden; seven real software captures in the reel')
(ROOT/'work.html').write_text(page)
(ROOT/'index.html').write_text(page)
print(f'Built {len(public)} public cards, {len(sources)} gallery captures, language chart and synchronized homepage.')
