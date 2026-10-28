# Hamanaka Software Factory — the ecosystem atlas

[Explore the atlas](https://hamanakam1.github.io/) · [Interactive repository map](https://hamanakam1.github.io/ecosystem.html) · [Suggest a contribution](https://github.com/hamanakam1/hamanakam1.github.io/issues/new?template=ecosystem-idea.yml)

One software factory, many entry points. Most systems work comes together in the private [ai-dashboard](https://github.com/hamanakam1/ai-dashboard). Public tools, private components, upstream forks and experiments all belong on the same map. Describing a private repository does not distribute its source; GitHub permissions still govern access.

The atlas covers the owner's 2026-10-28 GitHub inventory: 32 repositories in seven areas. Each has a role, source-access label, maturity description and suggested contribution surface. These are editorial assessments and invitations, not claims that every adapter is deployed or every contribution is pre-approved.

## Contribute a useful piece

Try a public tool and report a reproducible problem. Improve accessibility, recovery, documentation or failure explanations. Propose a small adapter, portable evidence contract, hardware fixture or synthetic scenario. Public projects can evolve independently; later integration into the private factory is a separate decision. Check each repository's license and contribution guide.

For a private component, discuss a generic interface through this repository's public issue tracker. No private access is needed to contribute a useful idea.

## The map

The 40-node map groups repositories by responsibility. Branches show membership, not runtime calls or deployment qualification. AI Dashboard's role as integration hub is supplied by the owner.

The viewer starts two zoom steps out (81%), aligned left. Controls occupy a separate column; below 800px they stack below the drawing. Zoom, reset, keyboard selection and a project chooser are supported. Reset restores the initial view. The text directory and static SVG remain available without JavaScript.

Archify generated the canonical geometry through the Dashboard integration, passing all nine validation checks and its original browser gate. The original HTML is retained outside this public repository. The SVG has a public theme and independent controls; its portable receipt records source and derived hashes. Hosted viewer tests and visual review are separate checks.

## Preview and maintain

```sh
python3 -m http.server 8000 --bind 127.0.0.1
python3 scripts/check_site.py
node --check assets/ecosystem-viewer.js
```

Open `/` and `/ecosystem.html`. Assets are local; serving needs no build service, package install, analytics, remote fonts or inference.

The reviewed inventory is `assets/repositories.json`. Editorial roles and contribution ideas are in `scripts/build_atlas.py`. Review additions/removals in that mapping, then run `python3 scripts/build_atlas.py --refresh` to read GitHub metadata with gh and rebuild the static page and typed diagram specification. Without `--refresh`, it uses the retained snapshot. Regenerate through the local Archify integration when the specification changes, then run `scripts/export_map.py` against the canonical HTML. Retain the original delivery receipt and inspect the hosted viewer.

The offline checker verifies local links, fragments, duplicate IDs, ARIA targets, headings and image alt attributes. Only the named local viewer script is allowed. Inspect desktop/mobile widths, zero horizontal page overflow, project selection, zoom/reset, keyboard focus and control clearance. The 404 page keeps root-relative recovery links.

Pages currently publishes from `codex/f07-site-quality` at the repository root. A push and an actual Pages deployment need separate remote readback.
