# Hamanaka Software Factory — the ecosystem atlas

[Explore the atlas](https://hamanakam1.github.io/) · [Interactive repository map](https://hamanakam1.github.io/ecosystem.html) · [Suggest a contribution](https://github.com/hamanakam1/hamanakam1.github.io/issues/new?template=ecosystem-idea.yml)

One software factory, many entry points. Most systems work comes together in the private [ai-dashboard](https://github.com/hamanakam1/ai-dashboard). Public tools, private components, upstream forks and experiments all belong on the same map. Describing a private repository does not distribute its source; GitHub permissions still govern access.

The atlas covers the owner's 2026-10-28 GitHub inventory: 32 repositories in seven areas. Each has a role, source-access label, maturity description and suggested contribution surface. These are editorial assessments and invitations, not claims that every adapter is deployed or every contribution is pre-approved.

## Contribute a useful piece

Try a public tool and report a reproducible problem. Improve accessibility, recovery, documentation or failure explanations. Propose a small adapter, portable evidence contract, hardware fixture or synthetic scenario. Public projects can evolve independently; later integration into the private factory is a separate decision. Check each repository's license and contribution guide.

For a private component, discuss a generic interface through this repository's public issue tracker. No private access is needed to contribute a useful idea.

## The interactive factory floor

`ecosystem.html` is a compact, responsive explorer of the same reviewed inventory as the text atlas. Seven station buttons filter projects by responsibility. Search matches names, roles, maturity and contribution ideas; public/private filters describe source access. The details panel always follows the visible results and clears when no projects match.

On desktop, the floor and project details sit side by side. Short laptop screens use a compact layout. Phones use a swipeable area strip and a native modal for project details. Keyboard selection, `/` to focus search, Escape to close details, a motion toggle, reduced-motion preferences, copyable project links (`#project=taskrivet`), surprise selection and a seven-stop guided tour are supported. The tour explains roles, not observed runtime jobs. No analytics, external fonts, provider requests or live telemetry are used.

The browser reads project descriptions directly from `index.html`; it does not keep a second editorial inventory. Loading and failed requests disable controls, and a text-atlas fallback remains available without JavaScript. Private links remain access-controlled.

The original 40-node Archify map remains available as the full vector diagram. A compact seven-area overview is generated through the Dashboard Archify integration, with the authored and canonical specifications and portable receipt in `assets/factory-overview-*`. Its nine validation gates and canonical browser evidence are separate from the public explorer checks. Both diagram versions group roles; they do not certify integrations.

`assets/factory-tour.gif` is the 14-second, seven-stop browser preview used on the homepage and GitHub profile. It links to the interactive page. The homepage has play/pause controls and initially shows the still image when reduced motion is requested; without JavaScript it remains a linked still. Turning on reduced motion while it plays also stops the preview. An explicit Play action can start it afterward. The profile uses a `<picture>` still fallback for reduced-motion preferences and provides a separate still-image link. GitHub README rendering does not run the explorer JavaScript.

The [capture notes and seven reviewed frames](docs/tour/README.md) retain provenance and reproduction instructions. Run `python3 scripts/build_tour.py` with FFmpeg installed to rebuild the GIF and still. This is a dated UI tour, not live telemetry. `assets/factory-preview.svg` remains an alternative static card.

## Preview and maintain

```sh
python3 -m http.server 8000 --bind 127.0.0.1
python3 scripts/check_site.py
node --check assets/ecosystem-viewer.js
```

Open `/` and `/ecosystem.html`. Assets are local; serving needs no build service, package install, analytics, remote fonts or inference.

The reviewed inventory is `assets/repositories.json`. Editorial roles and contribution ideas are in `scripts/build_atlas.py`. Review additions/removals in that mapping, then run `python3 scripts/build_atlas.py --refresh` to read GitHub metadata with gh and rebuild the static page and typed diagram specification. Without `--refresh`, it uses the retained snapshot. Regenerate through the local Archify integration when the specification changes, then run `scripts/export_map.py` against the canonical HTML. Retain the original delivery receipt and inspect the hosted viewer.

The offline checker verifies local links, fragments, duplicate IDs, ARIA targets, headings and image alt attributes. Only the named local viewer and preview scripts are allowed. Inspect desktop/mobile widths, zero horizontal page overflow, all project selections, search/access filters, empty recovery, tour completion, keyboard focus, mobile modal dismissal, deep links, clipboard behavior, motion preferences and fetch-failure fallback. The 404 page keeps root-relative recovery links.

Pages currently publishes from `codex/f07-site-quality` at the repository root. A push and an actual Pages deployment need separate remote readback.
