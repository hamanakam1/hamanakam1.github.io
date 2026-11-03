#!/usr/bin/env python3
"""Keep the canonical homepage and the existing work.html address identical.

Edit work.html, then run this script. Both URLs use the root canonical URL.
The site checker rejects drift so profile links to either address remain valid.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / "work.html"
    content = source.read_bytes()
    canonical = b'<link rel="canonical" href="https://hamanakam1.github.io/">'
    if canonical not in content:
        raise SystemExit("work.html must declare the root canonical URL before syncing")
    (ROOT / "index.html").write_bytes(content)
    print("Synchronized index.html from work.html; root is the canonical homepage.")


if __name__ == "__main__":
    main()
