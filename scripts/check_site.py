#!/usr/bin/env python3
"""Check local site navigation and assets without network or package installs."""

from collections import Counter
import json
import re
import hashlib
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
        allowed_scripts = {"ecosystem.html": "assets/ecosystem-viewer.js", "atlas.html": "assets/tour-preview.js", "index.html": "assets/work.js", "work.html": "assets/work.js", "factory.html": "assets/factory-stories.js"}
        if tag == "script" and (not attrs.get("src") or attrs.get("src") != allowed_scripts.get(self.path.name)):
            self.errors.append("only the named local viewer and preview scripts are allowed")
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
    generated = root / "diagrams"
    manifest_path = generated / "manifest.json"
    approved = {}
    if manifest_path.exists():
        approved = {entry["file"]: entry["sha256"] for entry in json.loads(manifest_path.read_text())}
    generated_errors = []
    for path in generated.glob("*.html"):
        expected = approved.get(path.name)
        if expected is None or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            generated_errors.append(f"Unverified generated diagram: {path.name}")
    for name in approved:
        if not (generated / name).is_file():
            generated_errors.append(f"Missing generated diagram: {name}")
    pages = {path: Page(path) for path in root.rglob("*.html") if ".git" not in path.parts and path.parent != generated}
    errors = generated_errors[:]
    if root / "index.html" not in pages:
        errors.append("index.html: homepage is missing")
    homepage = root / "index.html"
    source = root / "work.html"
    if homepage.is_file() and source.is_file() and homepage.read_bytes() != source.read_bytes():
        errors.append("index.html differs from work.html: run python3 scripts/sync_homepage.py")
    if source.is_file() and '<link rel="canonical" href="https://hamanakam1.github.io/">' not in source.read_text():
        errors.append("work.html: canonical homepage URL is missing")
    inventory = root / "assets/repositories.json"
    if inventory.is_file() and root / "atlas.html" not in pages:
        errors.append("atlas.html: repository atlas is missing")
    if inventory.is_file() and root / "atlas.html" in pages:
        names = {r["name"] for r in json.loads(inventory.read_text())["repositories"]}
        actual = {key[8:] for key in pages[root / "atlas.html"].ids if key.startswith("project-")}
        if names != actual:
            errors.append("Repository inventory and public atlas cards differ")
        spec = json.loads((root / "assets/ecosystem-spec.json").read_text())
        mapped = {n["label"] for n in spec["nodes"] if n["id"].startswith("repo-")}
        if mapped != names:
            errors.append("Diagram specification does not cover the complete repository inventory")
    public_path = root / "assets/work/public-repositories.json"
    if public_path.is_file() and source.is_file():
        public = json.loads(public_path.read_text())["repositories"]
        public_names = {r["name"] for r in public}
        expected_public = {r["name"] for r in json.loads(inventory.read_text())["repositories"] if not r["isPrivate"]}
        card_names = set(re.findall(r'data-repo-name="([^"]+)"', source.read_text()))
        if public_names != expected_public or card_names != public_names or any(r["private"] for r in public):
            errors.append("Public catalogue coverage or source-access boundary differs from reviewed inventory")
        for r in public:
            if r["fork"] and not (r.get("parent") or {}).get("html_url", "").startswith("https://github.com/"):
                errors.append(f"Fork lacks upstream attribution: {r['name']}")
    captures_path = root / "assets/work/sources.json"
    stories_path = root / "assets/factory-stories/stories.json"
    if stories_path.is_file():
        stories = json.loads(stories_path.read_text())
        expected = {r["name"] for r in json.loads(inventory.read_text())["repositories"]}
        actual = [r["name"] for r in stories["repositories"]]
        if set(actual) != expected or len(actual) != len(set(actual)):
            errors.append("Factory illustrations must cover each selected project exactly once")
        excluded = {"archify", "cwinvoicer", "node-pty", "wad-sbx-workshop", "portal"}
        if excluded.intersection(actual):
            errors.append("Excluded projects appear in the factory gallery")
        if sum(bool(r["fork"]) for r in stories["repositories"]) != sum(bool(r["fork"]) for r in json.loads(public_path.read_text())["repositories"]):
            errors.append("Factory fork attribution count differs from the public inventory")
        for story in stories["repositories"]:
            image = root / story.get("image", {}).get("file", "MISSING")
            if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != story.get("image", {}).get("sha256"):
                errors.append(f"Generated image provenance mismatch: {story['name']}")
            preview = root / story.get("image", {}).get("preview", "MISSING")
            if not preview.is_file() or hashlib.sha256(preview.read_bytes()).hexdigest() != story.get("image", {}).get("preview_sha256"):
                errors.append(f"Image preview provenance mismatch: {story['name']}")
            if story["fork"] and not story.get("upstream"):
                errors.append(f"Illustrated fork lacks upstream attribution: {story['name']}")
        cover = stories.get("cover", {})
        for path_key, hash_key in (("file", "sha256"), ("preview", "preview_sha256")):
            image = root / cover.get(path_key, "MISSING")
            if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != cover.get(hash_key):
                errors.append(f"Factory cover provenance mismatch: {path_key}")
        animation = stories.get("animation", {})
        motion_path = root / "assets/factory-stories/motion.json"
        if not motion_path.is_file():
            errors.append("Per-project animation manifest is missing")
        else:
            motion = json.loads(motion_path.read_text())
            if {m["name"] for m in motion["projects"]} != expected:
                errors.append("Every selected project must have its own animated loop")
            for item in motion["projects"]:
                asset = root / item["file"]
                if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != item["sha256"]:
                    errors.append(f"Project animation provenance mismatch: {item['name']}")
                elif asset.stat().st_size >= 1_000_000 or item["frames"] < 10 or item["duration_ms"] < 3000:
                    errors.append(f"Project animation exceeds size budget or lacks motion frames: {item['name']}")
        gif = root / animation.get("file", "MISSING")
        if not gif.is_file() or gif.stat().st_size >= 4_000_000:
            errors.append("Factory GIF is missing or exceeds the 4 MB GitHub delivery budget")
        elif hashlib.sha256(gif.read_bytes()).hexdigest() != animation.get("sha256"):
            errors.append("Factory GIF hash differs from its delivery manifest")
        for name in ("factory-tour.gif", "factory-process-v3.gif"):
            candidate = root / "assets" / name
            if not candidate.is_file() or candidate.stat().st_size >= 4_000_000:
                errors.append(f"Referenced GIF exceeds delivery budget or is missing: {name}")
    if captures_path.is_file():
        for capture in json.loads(captures_path.read_text()):
            image = root / "assets/work" / capture["file"]
            if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != capture["sha256"]:
                errors.append(f"Screenshot provenance mismatch: {capture['file']}")
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
