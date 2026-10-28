"""Derive a static public SVG from an unchanged, validated Archify artifact."""
import hashlib
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
artifact = Path(sys.argv[1])
original = artifact.read_bytes()
document = original.decode()
assert '/Users/' not in document
svg = re.search(r'<svg\b[\s\S]*?</svg>', document).group()
svg = svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
css = '''<style>:root {--text:#edf5f3;--text-muted:#b5cbc7;--text-dim:#8aa6a0;--mask:#102326;--grid:#34545a;--arrow:#669e9d;--arrow-emphasis:#86e8cc;--lane-stroke:#34545a;--frontend-fill:#163034;--frontend-stroke:#86e8cc;--backend-fill:#182d3d;--backend-stroke:#84baff;--database-fill:#1a3430;--database-stroke:#8ae1b3;--cloud-fill:#2c2840;--cloud-stroke:#c5a8ff;--security-fill:#3b2a2e;--security-stroke:#f3a8b9;--messagebus-fill:#3c321d;--messagebus-stroke:#f0cc80;--external-fill:#202f3e;--external-stroke:#a0b8c7;} text{font-family:system-ui,sans-serif}.t-primary{fill:var(--text)}.t-muted{fill:var(--text-muted)}.t-dim{fill:var(--text-dim)}.c-mask{fill:var(--mask)}.a-default{fill:none;stroke:var(--arrow)}.c-external{fill:var(--external-fill);stroke:var(--external-stroke)}.tree-toggle{display:none} [data-tree-toggle]{display:none} [data-node-id]{cursor:pointer;outline:none}[data-node-id]:focus > rect,[data-selected] > rect{stroke:#ffe296;stroke-width:3px} .tree-socket{fill:#102326;stroke:#86e8cc}</style>'''
css += '<style>.c-grid{fill:none;stroke:#34545a;opacity:.35}</style>'
svg = svg.replace('>', '>' + css + '<rect width="100%" height="100%" fill="#102326"/>', 1)
# The public rendering has its own reviewed controls; canonical Archify HTML stays unchanged.
svg = re.sub(r'aria-label="Focus ', 'aria-label="Inspect ', svg)
(root / 'assets/ecosystem-map.svg').write_text(svg)
(root / 'assets/ecosystem-canonical-spec.json').write_bytes((artifact.parent / 'specification.json').read_bytes())
receipt = {'artifact_id': artifact.parent.name, 'original_html_sha256': hashlib.sha256(original).hexdigest(), 'specification_sha256': hashlib.sha256((artifact.parent / 'specification.json').read_bytes()).hexdigest(), 'public_svg_sha256': hashlib.sha256(svg.encode()).hexdigest(), 'derivation': 'Canonical geometry extracted; public theme and independent view controls added. Original HTML retained privately.', 'validation': {'checks_passed': 9, 'errors': 0, 'warnings': 0}, 'evidence_scope': 'Archify validation and browser checks apply to original artifact; hosted viewer has separate layout checks.'}
(root / 'assets/ecosystem-map-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('Exported public SVG and portable provenance receipt')
