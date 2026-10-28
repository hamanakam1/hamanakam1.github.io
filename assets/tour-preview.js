'use strict';
(() => {
  const image = document.getElementById('tour-preview-image');
  const toggle = document.getElementById('tour-preview-toggle');
  if (!image || !toggle) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const still = image.getAttribute('src');
  let playing = false;
  function setPlaying(value) {
    playing = value;
    image.src = value ? image.dataset.animation : still;
    toggle.textContent = value ? 'Pause preview' : 'Play preview';
    toggle.setAttribute('aria-pressed', String(value));
  }
  toggle.hidden = false;
  toggle.addEventListener('click', () => setPlaying(!playing));
  motion.addEventListener('change', event => {
    if (event.matches) setPlaying(false);
  });
  setPlaying(!motion.matches);
})();
