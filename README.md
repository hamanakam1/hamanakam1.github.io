# Mike Hamanaka — AI-assisted prototypes and workflow tools

[Work with Mike](https://hamanakam1.github.io/) · [Repository atlas](https://hamanakam1.github.io/atlas.html) · [Interactive repository map](https://hamanakam1.github.io/ecosystem.html)

The homepage presents paid project options, illustrated project workflows, original software captures and a direct contact route. Hamanaka Software Factory is Mike's independent workshop for AI workflows, developer tools and local systems. The repository catalogue supplies technical evidence for a project or hiring conversation.

`index.html` is the canonical homepage. `work.html` remains an identical compatibility address for existing profile and campaign links. Edit `work.html`, then run `python3 scripts/sync_homepage.py`; the site checker rejects differences between the two files. Both declare the root canonical URL.

## Find the right level of detail

- **Homepage:** engagement options, screenshots, project evidence and a searchable public catalogue.
- **Text atlas (`atlas.html`):** the curated 39-project selection grouped into six areas, with source access, maturity and contribution ideas.
- **Interactive explorer (`ecosystem.html`):** search and filter the same atlas by project responsibility and access.
- **Technical diagrams (`diagrams/`):** documented project responsibilities, proposed handoffs, a local systems pattern and an engagement workflow.

Source access and maturity are separate labels. Private repository links require the appropriate GitHub permissions. Forked repositories and the client-specific workspace are excluded from the selected portfolio. Demonstrations, fixtures and learning projects are identified so readers can judge the evidence behind each example.

## Animated Software Factory

`factory.html` contains 39 individually animated project illustrations: 23 public repositories and 16 private projects described only from their already-public atlas summaries. The gallery offers search, stage explanations, source references, still images and explicit playback controls. The original generated PNGs are retained; WebP previews and GIFs are delivery formats. These are conceptual workflows, not application screenshots or recordings of deployed automation.

`assets/factory-process-v3.gif` combines eight featured six-second loops into the compact profile overview. Each project GIF shows a moving work packet and stage pauses while preserving the generated illustration. `assets/factory-stories/stories.json` records reviewed project descriptions and original/preview hashes; `motion.json` records frame counts, decoded duration, source hashes, animation hashes and distinct-frame checks. `prompts.json` retains the image-generation prompts without local paths.

Rebuild after reviewing the selected source data and generated PNGs:

```sh
python3 scripts/build_project_animations.py
python3 scripts/build_factory_stories.py --encode
```

The tools are FFmpeg, cwebp and Pillow (validation). The build enforces a 4 MB maximum for the overview and a 1 MB maximum for each project loop; the current loops are much smaller. The page starts on still previews and stops playback when reduced motion is requested or the page becomes hidden.

The seven actual software captures remain in the homepage gallery. `assets/work/sources.json` pins their original hashes. `assets/factory-tour.gif` is a compressed legacy screenshot reel retained for the existing profile URL during migration; it has its own provenance receipt and must also remain below 4 MB. `scripts/build_screenshot_reel.py` is a legacy authoring script, not the factory animation builder. See [tour maintenance notes](docs/tour/README.md).

## Interactive explorer

The browser reads project descriptions from `atlas.html`, keeping one editorial source for the atlas and explorer. Six station buttons filter by responsibility. Search matches names, roles, maturity and contribution ideas; public/private filters describe source access. The details panel follows the visible results and clears when none match.

The explorer supports keyboard selection, `/` to focus search, Escape to close details, copyable project links, a motion toggle and a guided tour. The tour describes roles. Its motion is illustrative and does not show live jobs or qualify deployments. No analytics, external fonts, provider requests or live telemetry are used. Loading and failed requests disable controls, and a text-atlas fallback remains available without JavaScript.

The interactive explorer uses the curated atlas. Earlier map assets containing excluded projects are retained outside the published site. Regenerate a current technical diagram through the Dashboard Archify integration when its specification changes, retain the authored and canonical specifications and delivery receipt, and inspect the result separately from the portfolio.

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
node --check assets/factory-stories.js
node --check assets/ecosystem-viewer.js

python3 -m http.server 8000 --bind 127.0.0.1
```

Open `/`, `/factory.html`, `/atlas.html` and `/ecosystem.html`. Assets are local; serving needs no build service, external fonts or inference.

The reviewed snapshot is `assets/repositories.json`. Editorial roles and contribution ideas are in `scripts/build_atlas.py`. Review additions and removals in that mapping before running the refresh; the generator rejects an unexplained inventory change. Without `--refresh`, it uses the retained snapshot. The generator writes `atlas.html` and the typed `assets/ecosystem-spec.json`; it never overwrites the homepage.

The offline checker verifies local links and fragments, duplicate IDs, ARIA targets, headings, image alt attributes, homepage parity, atlas inventory coverage and registered diagram hashes. It allows only the named local scripts on each page. Browser review should cover desktop and phone widths, overflow, screenshot navigation, search and empty-result recovery, keyboard focus, the explorer modal, deep links, motion preferences and failed-fetch fallback.

Publishing requires checking the repository's configured Pages source, completing the required repository checks and reading back the deployed revision and assets. A local preview or push alone does not establish that Pages is current.

## Contribute

Try a public tool and report a reproducible problem, or propose a small adapter, portable evidence contract or synthetic scenario. Follow each repository's license and contribution guide. Contribution ideas in the atlas are invitations to discuss scope; integration into private components remains a separate decision. For a private component, discuss a generic interface through this repository's public issue tracker.

The public catalogue in `assets/work/public-repositories.json` retains reviewed category and maturity labels for the 23 selected public repositories. Refresh it from public GitHub metadata, review additions, and run `scripts/build_work_catalogue.py` to update gallery, chart, catalogue and homepage. Never copy the private owner inventory into that public manifest.
