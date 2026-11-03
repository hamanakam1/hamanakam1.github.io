# Software in practice — screenshot film

The current reel is an editorial film with seven projects, a collage opening, fourteen product/detail views, a contact closing and short crossfades. It replaces the older map animation and the initial six-still slideshow.

The 1280×820 GIF runs for 37.58 seconds. Original screenshot bytes are hash-checked before composition. `assets/work/sources.json` pins each source and `assets/work/reel.json` records timing, hash and output size. The film includes Murmuration, Panther Intent Capture, Taskrivet, MeterMouseGarden, El Verificador, fluxrecord and LineasFlows. CLI panels use detail crops from their original output. Scene motion is editorial; it does not simulate a live integrated run. Demo, fixture and experimental boundaries remain visible.

`assets/factory-tour-still.png` is the reduced-motion collage. The homepage starts on the still and provides explicit play/pause. The GitHub profile offers a reduced-motion picture source and separate still link. `assets/work/reel-storyboard.jpg` shows all sixteen keyframes.

Rebuild: `python3 scripts/build_screenshot_reel.py` (Pillow). Uses Arial on macOS or DejaVu Sans on Linux. Font changes can change the resulting image hash.

Historical 28 October frames are retained in this folder. `scripts/build_tour.py` rebuilds that archived format, not the current screenshot film.
