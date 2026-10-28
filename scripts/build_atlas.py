"""Build the static atlas from a reviewed snapshot; --refresh reads GitHub metadata."""
import argparse
import html
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    'hub': ('The factory core', 'The private workshop where most integration happens.'),
    'work': ('Intent, sessions & delivery', 'Public tools for turning an idea into reviewable work.'),
    'proof': ('Evidence & institutional memory', 'Contracts, independent checks, retained records and lessons.'),
    'edge': ('Machines, inference & the edge', 'Discover resources, understand constraints and explore distributed work.'),
    'lab': ('Simulation & product experiments', 'Fictional fixtures and experimental product surfaces.'),
    'surface': ('Publishing & public entry points', 'The front doors, documentation and communication layers.'),
    'upstream': ('Upstream collaborations', 'Forks that connect the workshop to other communities.'),
}
# Role, maturity and contribution ideas are editorial assessments, not integration certification.
PROJECTS = {
 'ai-dashboard': ('hub', 'Integration hub', 'The local command center where I bring agents, inference, tickets, spend, evidence and machine health together.', 'Discuss operator experience, adapter contracts, observability and useful experiments through the public atlas.'),
 'cofoundry': ('hub', 'Private engine', 'Packaged supervisor, job dispatch, local execution, readiness and audited controls.', 'Discuss portable supervisor contracts and reproducible integration examples.'),
 'panther-intent-capture': ('work', 'Browser extension', 'Capture browser intent into reviewed proposals and portable context.', 'Try browser compatibility, accessible capture controls and export/import edge cases.'),
 'panther-companion': ('work', 'Desktop companion', 'Explain selected evidence in the context of a current goal.', 'Improve evidence explanations, keyboard workflows and intent-bundle handoffs.'),
 'taskrivet': ('work', 'Desktop alpha', 'Persistent agent terminals, bounded task context and reviewable results.', 'Test terminal recovery, session continuity, accessibility and bounded context adapters.'),
 'osprey': ('work', 'Prerelease', 'A Mac supervisor for selected Taskrivet output and reviewed work records.', 'Exercise output redaction, checkpoint capture and macOS build/recovery flows.'),
 'el-hidratador': ('work', 'Staging experiment', 'Expand a ticket into bounded context and reviewable execution preparation.', 'Build synthetic context fixtures and test dependency ordering and cancellation.'),
 'fluxrecord': ('proof', 'Ticket standard', 'A shared language for bounded context, evidence and visible failures.', 'Contribute small interoperable examples, schema edge cases and adapter fixtures.'),
 'el-verificador': ('proof', 'Verification tooling', 'Independent intent checks and proof records for reviewable coding work.', 'Add falsifiable checks, adversarial examples and understandable failure reports.'),
 'the-chronicler': ('proof', 'Memory tooling', 'Turn local failure evidence into reviewed lessons and reusable heuristics.', 'Improve provenance, retrieval evaluation and reviewable memory updates.'),
 'edgerecord-core': ('proof', 'Private verifier', 'Deterministic append-only state verification for edge nodes.', 'Discuss portable verification formats using synthetic examples.'),
 'edgerecord': ('proof', 'Private workspace', 'Local verification and evidence workspace.', 'Discuss evidence exchange and review ergonomics in the public atlas.'),
 'edgerecord-era': ('proof', 'Private ledger', 'Autonomy evidence and records ledger.', 'Propose interoperable receipts without requiring ledger access.'),
 'edgerecord-ai': ('hub', 'Private workspace', 'Local AI stack workspace and durable agent handoffs.', 'Discuss source-bound handoffs and recovery contracts.'),
 'the-surveyor': ('edge', 'Read-only discovery', 'Hardware discovery, topology snapshots and change reports.', 'Add hardware fixtures, discovery adapters and topology-diff examples.'),
 'the-tower': ('edge', 'Prototype', 'Thermal, power and memory observations with advisory dispatch planning.', 'Improve sensor fixtures, stale-data handling and resource-limit explanations.'),
 'horizon-broker': ('edge', 'Alpha', 'Asynchronous inference queues with retries and failover; the real ledger adapter remains unfinished.', 'Explore idempotency, cancellation, failover and the unfinished ledger seam.'),
 'VortexMesh': ('edge', 'Learning experiment', 'Go event envelopes and an in-process concurrent pub/sub mesh.', 'Explore transport, offline durability, discovery and partition tests as proposed next slices.'),
 'mockmill': ('lab', 'Synthetic fixtures', 'Reproducible fictional business stories and offline CRM adapters.', 'Add generic fixture scenarios, adapter validation and deterministic examples.'),
 'onramp-synthetic-company': ('lab', 'Private simulation', 'A fictional company dataset for local business-workflow rehearsals.', 'Use generic public Mockmill fixtures to explore similar workflows.'),
 'vs-platform-synthetic-fleet': ('lab', 'Private simulation', 'Synthetic hardware nodes and protocol fixtures for platform testing.', 'Discuss generic protocol fixtures through the public atlas.'),
 'cloudteams-extension-studio': ('lab', 'Private prototype', 'Standalone extension concepts and a proposed browser-local SDK.', 'Discuss generic extension lifecycles, permissions and fictional fixtures.'),
 'cloudteams-lunch-break': ('lab', 'Private experiment', 'A fictional client/talent gesture-planning demo derived from Extension Studio.', 'Discuss accessible planning and consent models with synthetic examples.'),
 'cloudteams-plot-twist': ('lab', 'Private experiment', 'A fictional demo for rehearsing changed project circumstances.', 'Discuss context continuity and human-reviewed next-step proposals.'),
 'blessed-edge-deployment': ('lab', 'Private local demo', 'A fictional hardware-to-handoff rehearsal with local permissions and reproducible bundles.', 'Discuss reproducible demo bundles and tamper/failure fixtures.'),
 'portal': ('surface', 'Private client workspace', 'A private personal clone used for client-platform work.', 'Discuss portable client interfaces without copying client-specific source or data.'),
 'edgerecord-com': ('surface', 'Private web shell', 'A multi-tenant web shell for the evidence workspace.', 'Discuss accessible operator/client surfaces using generic examples.'),
 'edgerecord-publisher': ('surface', 'Private publishing adapter', 'Publish reviewed ledger receipts through Joomla Web Services.', 'Discuss portable receipt-to-article formats and preview behavior.'),
 'hamanakam1': ('surface', 'Public profile', 'The short introduction to the entire software-factory ecosystem.', 'Improve orientation, project explanations and contributor entry points.'),
 'hamanakam1.github.io': ('surface', 'Public atlas', 'This public map of the workshop, its experiments and ways to contribute.', 'Improve the map, accessible navigation and project/contribution descriptions.'),
 'archify': ('upstream', 'Upstream fork', 'An agent skill for interactive technical diagrams.', 'Check upstream guidance and contribute diagram usability or schema examples to the right project.'),
 'wad-sbx-workshop': ('upstream', 'Workshop fork', 'Docker Sandboxes learning material and host-side testing connectors.', 'Improve workshop reproduction, platform notes and synthetic sandbox examples.'),
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    inventory = ROOT / 'assets/repositories.json'
    if args.refresh:
        repos = json.loads(subprocess.check_output(['gh', 'repo', 'list', 'hamanakam1', '--limit', '200', '--json', 'name,url,isPrivate,isFork,homepageUrl'], text=True))
        assert {r['name'] for r in repos} == set(PROJECTS), 'Review inventory additions/removals before regenerating'
        inventory.write_text(json.dumps({'observed_on': '2026-10-28', 'repositories': sorted(repos, key=lambda r: r['name'].lower())}, indent=2) + '\n')
    repos = json.loads(inventory.read_text())['repositories']
    by_name = {r['name']: r for r in repos}
    esc = html.escape
    nodes = [{'id': 'factory', 'label': 'Hamanaka Software Factory', 'sublabel': 'One ecosystem · AI Dashboard at its core'}]
    sections = []
    for key, (title, intro) in GROUPS.items():
        nodes.append({'id': key, 'parent': 'factory', 'label': title, 'sublabel': 'Repository roles · not runtime call paths'})
        cards = []
        for name, (group, status, role, help_text) in PROJECTS.items():
            if group != key:
                continue
            repo = by_name[name]
            visibility = 'Private' if repo['isPrivate'] else 'Public'
            nodes.append({'id': 'repo-' + name.replace('.', '-'), 'parent': key, 'label': name, 'sublabel': f'{visibility} · {status}'})
            source_label = 'Access-controlled repository' if repo['isPrivate'] else 'Source & contribution guidance'
            issue_repo = 'hamanakam1.github.io' if repo['isPrivate'] else name
            docs = f'<a href="{esc(repo["homepageUrl"])}">Project guide / site</a>' if repo['homepageUrl'].startswith('https://') else ''
            cards.append(f'''<article id="project-{esc(name)}" class="repo-card" aria-labelledby="title-{esc(name)}">
<div class="repo-header"><h3 id="title-{esc(name)}">{esc(name)}</h3><span class="repo-badge">{visibility}</span></div>
<p class="repo-description">{esc(role)}</p><p class="maturity">{esc(status)}</p>
<p class="contribution"><strong>Where you could help:</strong> {esc(help_text)}</p>
<div class="repo-links"><a href="{esc(repo['url'])}">{source_label}</a>{docs}<a href="https://github.com/hamanakam1/{issue_repo}/issues">{'Public discussion' if repo['isPrivate'] else 'Issues & ideas'}</a></div></article>''')
        sections.append(f'<section class="section" id="{key}"><div class="container"><h2 class="section-title">{title}</h2><p class="section-description">{intro}</p><div class="repos-grid">' + '\n'.join(cards) + '</div></div></section>')
    public = sum(not r['isPrivate'] for r in repos)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hamanaka Software Factory — the whole ecosystem</title>
<meta name="description" content="One software factory, many entry points. Explore all 32 public and private projects, experimental systems, and opportunities to contribute."><meta name="color-scheme" content="dark light"><link rel="canonical" href="https://hamanakam1.github.io/"><meta property="og:url" content="https://hamanakam1.github.io/"><meta property="og:title" content="Hamanaka Software Factory — ecosystem atlas"><link rel="stylesheet" href="style.css"><link rel="icon" href="assets/favicon.svg"></head><body>
<a class="skip-link" href="#main">Skip to main content</a><header class="header"><div class="container"><p class="eyebrow">Mike Hamanaka · An open invitation into the workshop</p><h1 class="logo">One factory.<br>Many ways in.</h1><p class="subtitle">A living ecosystem of tools, experiments and a private integration hub.</p><p class="tagline">Most of my systems work comes together in <a href="https://github.com/hamanakam1/ai-dashboard">ai-dashboard</a>. These repositories are the entry points: some useful on their own, some experimental, some private. This atlas connects the dots and shows where other people can help the system grow.</p><div class="hero-links"><a class="hero-link" href="ecosystem.html">Explore the full interactive map ↗</a><a class="hero-link" href="#contribute">Find a way to contribute</a></div><p class="inventory-count">{len(repos)} repositories · {public} public · {len(repos)-public} private · inventory checked 28 October 2026</p></div></header>
<nav class="nav" aria-label="Ecosystem areas"><div class="container"><a class="nav-link" href="#hub">Factory core</a><a class="nav-link" href="#work">Workflows</a><a class="nav-link" href="#proof">Evidence</a><a class="nav-link" href="#edge">Edge systems</a><a class="nav-link" href="#lab">Experiments</a><a class="nav-link" href="#surface">Front doors</a><a class="nav-link" href="#upstream">Upstream</a><a class="nav-link" href="#contribute">Contribute</a></div></nav>
<main id="main" tabindex="-1"><section id="repos" class="section section-dark"><div class="container"><h2 class="section-title">The whole workshop, in view.</h2><p class="section-description">Public and private describe source access. They do not decide whether a project belongs in the ecosystem. Private links require permission; their names and roles can still be discussed here. Experiments get a place on the map, with their maturity visible.</p><div class="hub-callout"><p class="eyebrow">The integration hub</p><h3>ai-dashboard</h3><p>Agents, inference, work boards, spend, machine health, evidence and review come together in one local operator surface. The surrounding repositories expose focused tools and seams that can evolve independently, then be considered for integration.</p><a class="text-link" href="ecosystem.html">Explore all repository roles →</a></div><p class="section-description">The map groups responsibilities and contribution opportunities. The owner identifies AI Dashboard as the integrated hub; individual cross-repository adapters and deployments still need their own evidence. A place on the map is not a claim that every experiment is already connected.</p></div></section>
{''.join(sections)}
<section id="contribute" class="section section-dark"><div class="container"><p class="eyebrow">Build a useful piece of the bigger system</p><h2 class="section-title">Pick a seam. Make it better.</h2><p class="section-description">You do not need the private factory to help. Start with a public tool, a reproducible problem or a small synthetic example. Improvements can stand on their own; I can evaluate how they fit the larger system later.</p><div class="repos-grid"><article class="repo-card"><h3>Try a real workflow</h3><p>Run a public project using its own setup guide. Report your platform, the steps, what you expected and what happened. Accessibility, recovery and confusing first-run experiences are valuable starting points.</p></article><article class="repo-card"><h3>Build an adapter or fixture</h3><p>Suggest a small contract first: inputs, outputs, failure behavior and an offline example. Good places include ticket formats, evidence interchange, hardware discovery, inference queues and synthetic CRM data.</p></article><article class="repo-card"><h3>Explore an experiment</h3><p>Prototype ideas in a bounded branch. Label simulations and proposals, keep the example reproducible, and show what would be needed before integration. Learning projects are welcome here too.</p></article></div><p class="section-description">Contribution ideas are invitations to discuss scope, not pre-approved implementation requests. Check each repository’s license and contribution guidance. For private components, use the public atlas issue tracker to propose a generic interface or ask about collaboration.</p><a class="hero-link" href="https://github.com/hamanakam1/hamanakam1.github.io/issues/new?template=ecosystem-idea.yml">Propose an ecosystem contribution ↗</a></div></section></main>
<footer class="footer"><div class="container"><p>© 2026 Mike Hamanaka · Hamanaka Software Factory</p><p><a href="https://github.com/hamanakam1">GitHub</a> · <a href="ecosystem.html">Interactive map</a> · <a href="assets/repositories.json">Repository inventory</a> · <a href="#repos">Back to the workshop</a></p></div></footer></body></html>'''
    (ROOT / 'index.html').write_text(page)
    spec = {'schema_version': 1, 'diagram_type': 'tree', 'meta': {'title': 'Hamanaka Software Factory — all repository roles', 'subtitle': 'Owner-described ecosystem. Branches group repositories by role; they do not assert deployed integrations.', 'output': 'ecosystem-map.html', 'quality_profile': 'showcase', 'locale': 'en'}, 'layout': {'direction': 'right', 'nodeW': 230, 'nodeMaxW': 290, 'gapX': 80, 'gapY': 28}, 'nodes': nodes, 'cards': [{'dot': 'cyan', 'title': 'The integration hub', 'items': ['Most systems work comes together in the private ai-dashboard, according to its owner.', 'Public tools offer independent contribution surfaces; integration is evaluated separately.']}, {'dot': 'amber', 'title': 'Read the map honestly', 'items': ['Public/private describes repository access. Experiments remain part of the ecosystem.', 'Membership links are taxonomy, not execution, data flow or runtime qualification.']}]}
    (ROOT / 'assets/ecosystem-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    print(f'Built {len(repos)} project cards and {len(nodes)} map nodes')

if __name__ == '__main__':
    main()
