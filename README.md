# Mike Hamanaka — software engineering portfolio

[Work with Mike](https://hamanakam1.github.io/) · [Repository atlas](https://hamanakam1.github.io/atlas.html) · [Interactive repository map](https://hamanakam1.github.io/ecosystem.html)

The homepage presents paid engineering services, selected software, original software captures and a direct contact route. Hamanaka Software Factory is Mike's independent workshop for AI workflows, developer tools and local systems. The repository catalogue supplies technical evidence for a project or hiring conversation.

`index.html` is the canonical homepage. `work.html` remains an identical compatibility address for existing profile and campaign links. Edit `work.html`, then run `python3 scripts/sync_homepage.py`; the site checker rejects differences between the two files. Both declare the root canonical URL.

## Find the right level of detail

- **Homepage:** engagement options, screenshots, project evidence and a searchable public catalogue.
- **Text atlas (`atlas.html`):** the complete reviewed owner inventory grouped into seven areas, with source access, maturity and contribution ideas.
- **Interactive explorer (`ecosystem.html`):** search and filter the same atlas by project responsibility and access.
- **Technical diagrams (`diagrams/`):** documented project responsibilities, proposed handoffs, a local systems pattern and an engagement workflow.

Source access and maturity are separate labels. Private repository links require the appropriate GitHub permissions. Forks credit their upstream authors. Demonstrations, fixtures and learning projects are identified so readers can judge the evidence behind each example.

## Software screenshot reel

`assets/factory-tour.gif` uses published captures of Mike's software. `assets/work/sources.json` records the source URLs, revisions and original file hashes. Original captures remain available alongside the reel; detail crops are labelled. The capture notes and reproduction instructions are in [docs/tour/README.md](docs/tour/README.md).

Rebuild the current reel with `python3 scripts/build_screenshot_reel.py` (requires Pillow). The older `scripts/build_tour.py` produces the historical seven-area explorer tour; it must not be used to rebuild the current screenshot reel.

The homepage initially shows the still image and offers explicit play/pause. A change to reduced-motion preferences stops playback. The GitHub profile has a picture-based reduced-motion fallback and a separate still-image link; GitHub Markdown does not run the portfolio's JavaScript.

## Interactive explorer

The browser reads project descriptions from `atlas.html`, keeping one editorial source for the atlas and explorer. Seven station buttons filter by responsibility. Search matches names, roles, maturity and contribution ideas; public/private filters describe source access. The details panel follows the visible results and clears when none match.

The explorer supports keyboard selection, `/` to focus search, Escape to close details, copyable project links, a motion toggle and a guided tour. The tour describes roles. Its motion is illustrative and does not show live jobs or qualify deployments. No analytics, external fonts, provider requests or live telemetry are used. Loading and failed requests disable controls, and a text-atlas fallback remains available without JavaScript.

The original 28 October Archify SVG map remains explicitly archived. The interactive explorer uses the current reviewed atlas. Regenerate a current technical diagram through the Dashboard Archify integration when its specification changes, retain the authored and canonical specifications and delivery receipt, and inspect the result separately from the portfolio.

New diagram HTML in `diagrams/` is unchanged registered Archify output. `diagrams/manifest.json` binds each file to its registered hash; the site checker verifies that hash and the local destination. Archify's schema and browser checks are separate from checks of the surrounding website.

## Maintain and preview

```sh
# Review the inventory and editorial roles before refreshing GitHub metadata.
python3 scripts/build_atlas.py --refresh

# After editing work.html, keep both public entry addresses identical.
python3 scripts/build_work_catalogue.py
python3 scripts/sync_homepage.py

# Verify static navigation, inventory coverage and JavaScript syntax.
python3 scripts/check_site.py
node --check assets/work.js
node --check assets/ecosystem-viewer.js

python3 -m http.server 8000 --bind 127.0.0.1
```

Open `/`, `/atlas.html` and `/ecosystem.html`. Assets are local; serving needs no build service, external fonts or inference.

The reviewed snapshot is `assets/repositories.json`. Editorial roles and contribution ideas are in `scripts/build_atlas.py`. Review additions and removals in that mapping before running the refresh; the generator rejects an unexplained inventory change. Without `--refresh`, it uses the retained snapshot. The generator writes `atlas.html` and the typed `assets/ecosystem-spec.json`; it never overwrites the homepage.

The offline checker verifies local links and fragments, duplicate IDs, ARIA targets, headings, image alt attributes, homepage parity, atlas inventory coverage and registered diagram hashes. It allows only the named local scripts on each page. Browser review should cover desktop and phone widths, overflow, screenshot navigation, search and empty-result recovery, keyboard focus, the explorer modal, deep links, motion preferences and failed-fetch fallback.

Publishing requires checking the repository's configured Pages source, completing the required repository checks and reading back the deployed revision and assets. A local preview or push alone does not establish that Pages is current.

## Contribute

Try a public tool and report a reproducible problem, or propose a small adapter, portable evidence contract or synthetic scenario. Follow each repository's license and contribution guide. Contribution ideas in the atlas are invitations to discuss scope; integration into private components remains a separate decision. For a private component, discuss a generic interface through this repository's public issue tracker.

The public catalogue in `assets/work/public-repositories.json` retains reviewed category and maturity labels plus upstream links. Refresh it from public GitHub metadata, review additions, and run `scripts/build_work_catalogue.py` to update gallery, chart, catalogue and homepage. Never copy the private owner inventory into that public manifest.
