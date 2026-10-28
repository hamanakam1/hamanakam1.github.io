# A quick tour of the factory

[Open the interactive explorer](https://hamanakam1.github.io/ecosystem.html) · [Play the GIF](../../assets/factory-tour.gif) · [View the still](../../assets/factory-tour-still.png)

Seven actual browser captures, two seconds per stop. The preview follows the explorer's built-in tour through Factory core, Intent & delivery, Evidence & memory, Machines & inference, Simulation lab, Publishing & portals, and Upstream connections. Select the preview to explore at your own pace.

## Capture provenance

- Captured from the public explorer on 28 October 2026 in Safari.
- Explorer source at capture: `f51b9f53b3a432a75fd28156fe717add88538e59`.
- The tour selects AI Dashboard, Taskrivet, El Verificador, The Surveyor, Mockmill, this atlas, and Archify in that order.
- Each capture was checked against the visible `FACTORY TOUR / n OF 7` label before advancing.
- Browser chrome was removed and each frame resized to 1120 × 756 pixels. The seven reviewed PNG frames are retained in `frames/`.
- Only the public atlas is depicted. Source-access and maturity labels describe the inventory; the preview does not establish live integrations or access to private repositories.

## Rebuild the assets

From the repository root, with Python 3 and FFmpeg on PATH:

```sh
python3 scripts/build_tour.py
python3 scripts/check_site.py
node --check assets/tour-preview.js
```

The encoder uses a shared palette and two seconds per frame, loops the GIF, and copies frame 1 as the still preview. FFmpeg versions can produce different encoded bytes; the reviewed frames preserve the visual source. The page generator retains the preview when rebuilding the atlas.

The homepage starts with a still when JavaScript is unavailable or reduced motion is requested. Its toggle starts or stops the preview, and a new reduced-motion preference stops playback. The GitHub profile links the same animation to the explorer and provides both a reduced-motion still source and a direct still-image link. The animation is a dated preview; project exploration happens on the linked page.
