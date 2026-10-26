#!/usr/bin/env python3
"""Check local site navigation and assets without network or package installs."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys


ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids: Counter[str] = Counter()
        self.links: list[str] = []
        self.references: list[str] = []
        self.errors: list[str] = []
        self.headings = 0
        self.feed(path.read_text(encoding="utf-8"))
        self.close()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1
        if tag == "h1":
            self.headings += 1
        for attribute in ("aria-labelledby", "aria-describedby"):
            self.references.extend((attrs.get(attribute) or "").split())
        if tag == "img" and "alt" not in attrs:
            self.errors.append("image is missing alt text (use alt='' for decoration)")
        if tag == "script":
            self.errors.append("this static site does not use scripts")
        for attribute in ("href", "src"):
            value = attrs.get(attribute)
            if value is None:
                continue
            url = urlsplit(value)
            is_asset = attribute == "src" or (
                tag == "link" and bool(set((attrs.get("rel") or "").split()) & {"stylesheet", "icon"})
            )
            if is_asset and (url.netloc or url.scheme not in ("", "data")):
                self.errors.append(f"asset must be local: {value}")
            if not url.scheme and not url.netloc:
                self.links.append(value)


def check(root: Path) -> list[str]:
    root = root.resolve()
    pages = {path: Page(path) for path in root.rglob("*.html") if ".git" not in path.parts}
    errors = []
    if root / "index.html" not in pages:
        errors.append("index.html: homepage is missing")
    for path, page in pages.items():
        problems = list(page.errors)
        if page.headings != 1:
            problems.append(f"expected one h1, found {page.headings}")
        problems.extend(f"duplicate id: {key}" for key, count in page.ids.items() if count > 1)
        problems.extend(f"missing ARIA target: {key}" for key in page.references if key not in page.ids)
        for value in page.links:
            url = urlsplit(value)
            relative = unquote(url.path)
            target = root / relative.lstrip("/") if relative.startswith("/") else path.parent / relative
            if not relative:
                target = path
            target = target.resolve()
            if not target.is_relative_to(root):
                problems.append(f"link leaves site directory: {value}")
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                problems.append(f"missing local destination: {value}")
            elif url.fragment and target.suffix == ".html":
                destination = pages.get(target)
                if destination is None or unquote(url.fragment) not in destination.ids:
                    problems.append(f"missing fragment: {value}")
        errors.extend(f"{path.relative_to(root)}: {problem}" for problem in problems)
    return errors


if __name__ == "__main__":
    failures = check(ROOT)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print("Site checks passed: href/src destinations, labelled/described ARIA targets, headings, and image alt attributes.")
