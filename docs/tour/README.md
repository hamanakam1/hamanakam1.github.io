# Software screenshot reel

Prepared 2 November 2026. The current `assets/factory-tour.gif` is a 30-second reel of six published software captures. It replaces the older seven-area explorer animation. Source URLs, source commits, original file hashes and evidence boundaries are in `assets/work/sources.json`.

Taskrivet, Panther, MeterMouseGarden, El Verificador, fluxrecord and LineasFlows appear for five seconds each. Actual published screenshot bytes are retained unchanged in `assets/work/`. The reel scales images to fit; tall CLI images use a labelled top detail crop. These are software demonstrations, fixtures or experiments, not customer case studies.

The reduced-motion still is `assets/factory-tour-still.png`. The portfolio starts on the still and offers explicit play/pause. The profile offers a picture-based reduced-motion fallback and a separate still link.

The historical explorer frames in this folder were captured on 28 October and are retained as historical assets. `scripts/build_tour.py` builds that historical format, not the new screenshot reel. Regenerate the current reel with `python3 scripts/build_screenshot_reel.py` from the site root (requires Pillow).
