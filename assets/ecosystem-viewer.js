'use strict';
(async function () {
  const viewport = document.getElementById('map-viewport');
  const stage = document.getElementById('map-stage');
  const finder = document.getElementById('project-finder');
  const output = document.getElementById('zoom-level');
  const details = document.getElementById('project-detail');
  try {
    const [drawing, atlas] = await Promise.all([fetch('assets/ecosystem-map.svg'), fetch('index.html')]);
    if (!drawing.ok || !atlas.ok) throw new Error('Map unavailable');
    const parsed = new DOMParser().parseFromString(await drawing.text(), 'image/svg+xml');
    if (parsed.querySelector('parsererror')) throw new Error('Map format unavailable');
    const svg = document.importNode(parsed.documentElement, true);
    // Static checked local SVG only; no external resources or scripts are accepted.
    if (svg.querySelector('script,foreignObject,image,iframe')) throw new Error('Unexpected map content');
    const atlasDoc = new DOMParser().parseFromString(await atlas.text(), 'text/html');
    const cards = new Map([...atlasDoc.querySelectorAll('.repo-card[id^="project-"]')].map(card => [card.id.slice(8), card]));
    for (const name of [...cards.keys()].sort((a,b) => a.localeCompare(b))) {
      const option = document.createElement('option'); option.value = name; option.textContent = name; finder.append(option);
    }
    stage.append(svg);
    const {width, height} = svg.viewBox.baseVal;
    let steps = -2;
    let selected;
    function render() {
      const scale = Math.min(1, (viewport.clientWidth - 32) / width) * Math.pow(0.9, -steps);
      svg.style.width = `${width * scale}px`;
      svg.style.height = `${height * scale}px`;
      output.value = `${Math.round(Math.pow(0.9, -steps) * 100)}%`;
      viewport.dataset.zoomSteps = String(steps);
    }
    function reset() { steps = -2; render(); viewport.scrollTo(0, 0); }
    function select(name, jump = false) {
      const card = cards.get(name);
      if (!card) return;
      if (selected) selected.removeAttribute('data-selected');
      selected = [...svg.querySelectorAll('[data-node-id]')].find(n => n.dataset.nodeLabel === name);
      selected?.setAttribute('data-selected', '');
      finder.value = name;
      const clone = card.cloneNode(true);
      clone.removeAttribute('id'); clone.removeAttribute('aria-labelledby');
      clone.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
      clone.querySelectorAll('a').forEach(a => { if (a.getAttribute('href').startsWith('#')) a.href = 'index.html' + a.getAttribute('href'); });
      details.replaceChildren(clone);
      if (jump && selected) {
        const node = selected.getBoundingClientRect(); const view = viewport.getBoundingClientRect();
        viewport.scrollTo({left: Math.max(0, viewport.scrollLeft + node.left - view.left - 24), top: Math.max(0, viewport.scrollTop + node.top - view.top - 80), behavior: 'auto'});
      }
    }
    svg.querySelectorAll('[data-node-id]').forEach(node => {
      const name = node.dataset.nodeLabel;
      if (!cards.has(name)) { node.removeAttribute('tabindex'); node.removeAttribute('role'); return; }
      node.setAttribute('role', 'button');
      node.setAttribute('aria-label', `Inspect ${name}`);
      node.addEventListener('click', () => select(name));
      node.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(name); } });
    });
    finder.addEventListener('change', () => select(finder.value, true));
    document.getElementById('zoom-in').addEventListener('click', () => { steps = Math.min(8, steps + 1); render(); });
    document.getElementById('zoom-out').addEventListener('click', () => { steps = Math.max(-8, steps - 1); render(); });
    document.getElementById('reset-map').addEventListener('click', reset);
    new ResizeObserver(render).observe(viewport);
    reset();
  } catch (error) {
    const fallback = document.createElement('a'); fallback.href = 'assets/ecosystem-map.svg'; fallback.textContent = 'Open the static diagram (interactive map unavailable)'; stage.replaceChildren(fallback);
  }
}());
