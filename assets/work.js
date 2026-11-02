(() => {
  'use strict';
  const gallery = document.querySelector('[data-gallery]');
  const slides = Array.from(document.querySelectorAll('[data-slide]'));
  let selected = 0;
  const show = i => {
    selected = (i + slides.length) % slides.length;
    slides.forEach((el, n) => { el.hidden = n !== selected; });
    document.getElementById('slide-count').textContent = `${selected + 1} / ${slides.length}`;
  };
  if (gallery && slides.length) {
    document.getElementById('gallery-prev').addEventListener('click', () => show(selected - 1));
    document.getElementById('gallery-next').addEventListener('click', () => show(selected + 1));
    gallery.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft') { event.preventDefault(); show(selected - 1); }
      if (event.key === 'ArrowRight') { event.preventDefault(); show(selected + 1); }
    });
    show(0);
  }
  const reel = document.getElementById('work-reel');
  const toggle = document.getElementById('reel-toggle');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let playing = false;
  const setPlaying = on => {
    playing = on;
    reel.src = on ? reel.dataset.animation : reel.dataset.still;
    toggle.textContent = on ? 'Pause screenshot reel' : 'Play screenshot reel';
    toggle.setAttribute('aria-pressed', String(on));
  };
  if (reel && toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', () => setPlaying(!playing));
    reduced.addEventListener('change', event => { if (event.matches) setPlaying(false); });
    // Leave the still visible until the visitor chooses motion.
  }
  const search = document.getElementById('repo-search');
  const filter = document.getElementById('repo-filter');
  const repos = Array.from(document.querySelectorAll('[data-repo]'));
  const apply = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const repo of repos) {
      const matches = repo.textContent.toLocaleLowerCase().includes(query) &&
        (filter.value === 'all' || repo.dataset.kind === filter.value);
      repo.hidden = !matches;
      if (matches) count++;
    }
    document.getElementById('repo-count').textContent = `${count} of ${repos.length} public repositories`;
    document.getElementById('no-results').hidden = count !== 0;
  };
  if (search && filter) {
    search.addEventListener('input', apply);
    filter.addEventListener('change', apply);
    document.getElementById('clear-search').addEventListener('click', () => {
      search.value = ''; filter.value = 'all'; apply(); search.focus();
    });
    apply();
  }
})();
