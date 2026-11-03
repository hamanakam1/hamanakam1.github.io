(() => {
  'use strict';
  const cards = Array.from(document.querySelectorAll('[data-story-card]'));
  const search = document.getElementById('story-search');
  const count = document.getElementById('story-count');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const cardMotion = Array.from(document.querySelectorAll('[data-animate]'));
  const setCardMotion = (button, playing) => {
    const name = button.dataset.animate;
    const image = button.closest('[data-story-card]').querySelector('[data-project-image]');
    image.src = `assets/factory-stories/${encodeURIComponent(name)}.${playing ? 'gif' : 'webp'}`;
    button.setAttribute('aria-pressed', String(playing));
    button.textContent = playing ? 'Pause this flow' : 'Play this flow';
  };
  cardMotion.forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => setCardMotion(button, button.getAttribute('aria-pressed') !== 'true'));
  });
  const applySearch = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      card.hidden = !card.textContent.toLocaleLowerCase().includes(query);
      if (!card.hidden) visible++;
      else {
        const button = card.querySelector('[data-animate]');
        if (button && button.getAttribute('aria-pressed') === 'true') setCardMotion(button, false);
      }
    });
    count.textContent = `${visible} of ${cards.length} projects`;
    document.getElementById('story-empty').hidden = visible !== 0;
  };
  document.getElementById('search-controls').hidden = false;
  search.addEventListener('input', applySearch);
  document.getElementById('story-clear').addEventListener('click', () => {
    search.value = ''; applySearch(); search.focus();
  });
  fetch('assets/factory-stories/stories.json').then(response => {
    if (!response.ok) throw new Error('Story data unavailable');
    return response.json();
  }).then(data => {
    const stories = data.repositories;
    let selected = 0;
    let timer = null;
    const play = document.getElementById('story-play');
    const position = document.getElementById('story-position');
    const show = index => {
      selected = (index + stories.length) % stories.length;
      const story = stories[selected];
      const image = document.getElementById('viewer-image');
      document.getElementById('walkthrough-title').textContent = story.name;
      document.getElementById('viewer-maturity').textContent = story.maturity_label;
      document.getElementById('viewer-purpose').textContent = story.buyer_problem;
      document.getElementById('viewer-source').href = story.source.url;
      document.getElementById('viewer-source').textContent = story.source_access === 'private' ? 'Read the public description ↗' : 'Inspect project source ↗';
      image.src = `assets/factory-stories/${encodeURIComponent(story.name)}.${timer ? 'gif' : 'webp'}`;
      image.alt = `${story.name}: ${story.input} → ${story.transform} → ${story.output}. Generated illustration.`;
      position.textContent = `${selected + 1} / ${stories.length} — ${story.name}`;
    };
    const pause = () => {
      if (timer) window.clearInterval(timer);
      timer = null;
      document.getElementById('viewer-image').src = `assets/factory-stories/${encodeURIComponent(stories[selected].name)}.webp`;
      play.textContent = 'Play walkthrough';
      play.setAttribute('aria-pressed', 'false');
      position.setAttribute('aria-live', 'polite');
    };
    play.addEventListener('click', () => {
      if (timer) { pause(); return; }
      timer = window.setInterval(() => show(selected + 1), 6500);
      show(selected);
      play.textContent = 'Pause walkthrough';
      play.setAttribute('aria-pressed', 'true');
      position.setAttribute('aria-live', 'off');
    });
    document.getElementById('story-prev').addEventListener('click', () => { pause(); show(selected - 1); });
    document.getElementById('story-next').addEventListener('click', () => { pause(); show(selected + 1); });
    document.querySelectorAll('[data-select]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => {
        pause(); show(Number(button.dataset.select));
        const title = document.getElementById('walkthrough-title');
        title.setAttribute('tabindex', '-1'); title.focus({preventScroll: true});
        document.getElementById('walkthrough').scrollIntoView({behavior: reduced.matches ? 'instant' : 'smooth'});
      });
    });
    reduced.addEventListener('change', event => {
      if (event.matches) { pause(); cardMotion.forEach(button => setCardMotion(button, false)); }
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) { pause(); cardMotion.forEach(button => setCardMotion(button, false)); }
    });
    document.getElementById('viewer-controls').hidden = false;
    show(0);
  }).catch(() => {
    // Every project, source link and full image remains available without JS.
  });
})();
