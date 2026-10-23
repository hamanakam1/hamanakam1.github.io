# Hamanaka Software Factory project atlas

A small, static directory of Mike Hamanaka's public projects. The page introduces
tools for intent capture, AI session coordination, verification, memory, and edge
infrastructure, and links directly to their repositories.

The project directory comes first. Task shortcuts jump to intent capture,
session coordination, and the ticket standard. Each project has separate,
descriptive links to its source and documentation; the conceptual workflow
follows the directory.

## Preview locally

Python 3 is the only tool needed for a local preview. From this directory, run:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/>. Use another unused port if 8000 is busy, and stop the
preview with `Ctrl+C` when finished. There is no build step or package installation.

You can also open `index.html` directly in a browser. All page assets are local;
following a project link navigates to that project's external website.

Open <http://127.0.0.1:8000/404.html> to preview the missing-page design. Python's
standard preview server does not substitute that file for missing URLs; its
default error response is expected. The recovery page uses root-relative links
and `/style.css`, so preview it over HTTP at the site root. These paths also let
the page recover from nested missing URLs on the intended root-level site.

## Files and content

| File | Purpose |
| --- | --- |
| `index.html` | Page content, navigation, metadata, project links, and the existing workflow illustration |
| `404.html` | Missing-page explanation, project-directory recovery link, and indexing exclusion |
| `style.css` | Responsive layout, system fonts, focus indicators, and print styles |

The architecture illustration is conceptual. It is not evidence that the tools
are deployed together or that a particular integration is implemented. Keep this
distinction visible when updating the page, and use each project's README and
release notes to establish its supported capabilities.

The page needs no JavaScript, analytics, web fonts, or third-party asset requests.
Keep those properties intact unless a future change explicitly calls for them.

## Check a change

1. Preview the page and confirm the browser reports no missing assets.
2. Use `Tab` from the top of the page. The first link should reveal **Skip to main
   content**; `Enter` should move focus to the main content. Continue through the
   source and documentation links and check that focus stays visible. Each link
   should announce its project and destination without reading the entire card.
   On Safari for Mac, use `Option+Tab` if `Tab` skips links; see Apple's
   [keyboard navigation guide](https://support.apple.com/guide/safari/cpsh003/mac).
3. Activate each navigation link and confirm it reaches the matching section.
4. Inspect widths of 320, 390, 768, and 1440 CSS pixels, then test 200% zoom. Text,
   cards, and navigation should remain readable without horizontal page scrolling.
   Increase the default text size to 200% as a separate check; headings should
   enlarge with the body text.
5. Test user text-spacing overrides together: line height of 1.5 times the font
   size, paragraph spacing of 2 times the font size, letter spacing of 0.12 times
   the font size, and word spacing of 0.16 times the font size. Content and links
   should remain available without clipping. These are the override values in
   [WCAG's text-spacing guidance](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html),
   not required default styles.
6. Review A4 and Letter print previews. Source and documentation URLs should be
   visible, cards should remain intact, and the numbered workflow should stay
   together. Also review reduced-motion preferences and forced-colors mode.
7. Open `404.html` and follow **Browse public projects**. Check its skip link and
   narrow-screen layout. When hosting is separately authorized, verify that both
   a missing root URL and a nested missing URL return HTTP 404, display this page,
   and load `/style.css`. [GitHub Pages supports a root-level `404.html`](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-custom-404-page-for-your-github-pages-site);
   a local preview does not establish hosted routing.
8. Check project destinations when changing links. A successful response confirms
   reachability, not the accuracy of a project's feature claims.
9. Run `git diff --check` for tracked changes. Review new files separately because
   Git does not include untracked files in that check.

Automated checks complement keyboard, visual, and screen-reader testing; they do
not establish complete accessibility conformance.

## Maintaining the directory

Use descriptive link text, a single page heading, and ordered section headings.
Keep the skip target, section IDs, and navigation fragments in sync. Treat emoji
and arrows as decorative, and preserve the text alternative for the workflow SVG.
Keep each project card as an article with a named heading and two independent
links. Avoid making the entire card a link, nesting links, or adding click
handlers to the article. Keep the SVG's short title as its accessible name and
its longer explanation as its description.

Use synthetic examples and omit credentials, private logs, machine paths, and
identifying operational screenshots. The project list describes public roles;
each repository defines its own license and contribution process.

Local source changes and preview checks do not publish the site. Hosting setup,
publication, and verification of the public destination are separate steps.
