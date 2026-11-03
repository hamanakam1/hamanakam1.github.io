(() => {
  'use strict';
  const cards = Array.from(document.querySelectorAll('[data-story-card]'));
  const sections = Array.from(document.querySelectorAll('.story-section[data-story-section]'));
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
    const visibleSections = new Set();
    cards.forEach(card => {
      card.hidden = !card.textContent.toLocaleLowerCase().includes(query);
      if (!card.hidden) {
        visible++;
        visibleSections.add(card.dataset.section);
      }
      else {
        const button = card.querySelector('[data-animate]');
        if (button && button.getAttribute('aria-pressed') === 'true') setCardMotion(button, false);
      }
    });
    sections.forEach(section => {
      section.hidden = !visibleSections.has(section.dataset.storySection);
    });
    count.textContent = `${visible} of ${cards.length} projects`;
    document.getElementById('story-empty').hidden = visible !== 0;
  };
  document.getElementById('search-controls').hidden = false;
  search.addEventListener('input', applySearch);
  document.getElementById('story-clear').addEventListener('click', () => {
    search.value = ''; applySearch(); search.focus();
  });
  applySearch();
  const pauseCards = () => cardMotion.forEach(button => {
    if (button.getAttribute('aria-pressed') === 'true') setCardMotion(button, false);
  });
  reduced.addEventListener('change', event => {
    if (event.matches) pauseCards();
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) pauseCards();
  });
  fetch('assets/factory-stories/stories.json').then(response => {
    if (!response.ok) throw new Error('Story data unavailable');
    return response.json();
  }).then(data => {
    const stories = data.repositories;
    if (!Array.isArray(stories) || stories.length === 0) throw new Error('No stories available');
    let selected = 0;
    let timer = null;
    let playing = false;
    let imageGeneration = 0;
    let stopWaitingForImage = () => {};
    const play = document.getElementById('story-play');
    const position = document.getElementById('story-position');
    const image = document.getElementById('viewer-image');
    const cancelPendingAdvance = () => {
      imageGeneration++;
      stopWaitingForImage();
      stopWaitingForImage = () => {};
      if (timer !== null) window.clearTimeout(timer);
      timer = null;
    };
    const show = index => {
      cancelPendingAdvance();
      selected = (index + stories.length) % stories.length;
      const story = stories[selected];
      document.getElementById('walkthrough-title').textContent = story.name;
      document.getElementById('viewer-maturity').textContent = story.maturity_label;
      document.getElementById('viewer-purpose').textContent = story.buyer_problem;
      document.getElementById('viewer-source').href = story.source.url;
      document.getElementById('viewer-source').textContent = story.source_access === 'private' ? 'Read the public description ↗' : 'Inspect project source ↗';
      image.alt = `${story.name}: ${story.input} → ${story.transform} → ${story.output}. Generated illustration.`;
      position.textContent = `${selected + 1} / ${stories.length} — ${story.name}`;
      if (!playing) {
        image.src = `assets/factory-stories/${encodeURIComponent(story.name)}.webp`;
        return;
      }
      const generation = imageGeneration;
      let settled = false;
      const loaded = () => {
        if (settled || generation !== imageGeneration || !playing) return;
        settled = true;
        stopWaitingForImage();
        scheduleNext();
      };
      const failed = () => {
        if (settled || generation !== imageGeneration || !playing) return;
        settled = true;
        pause();
        position.textContent += ' — Animation unavailable; still image shown. Play to retry.';
      };
      stopWaitingForImage = () => {
        image.removeEventListener('load', loaded);
        image.removeEventListener('error', failed);
      };
      image.addEventListener('load', loaded);
      image.addEventListener('error', failed);
      image.src = `assets/factory-stories/${encodeURIComponent(story.name)}.gif`;
      // Cached images may already be ready before a load listener can run.
      if (image.complete) {
        if (image.naturalWidth > 0) loaded();
        else failed();
      }
    };
    const scheduleNext = () => {
      if (timer !== null) window.clearTimeout(timer);
      timer = null;
      if (!playing) return;
      const duration = Number(stories[selected].motion?.duration_ms);
      const delay = (Number.isFinite(duration) && duration > 0 ? duration : 6000) + 500;
      timer = window.setTimeout(() => {
        timer = null;
        if (!playing) return;
        show(selected + 1);
      }, delay);
    };
    const pause = () => {
      playing = false;
      cancelPendingAdvance();
      image.src = `assets/factory-stories/${encodeURIComponent(stories[selected].name)}.webp`;
      play.textContent = 'Play walkthrough';
      play.setAttribute('aria-pressed', 'false');
      position.setAttribute('aria-live', 'polite');
    };
    play.addEventListener('click', () => {
      if (playing) { pause(); return; }
      playing = true;
      play.textContent = 'Pause walkthrough';
      play.setAttribute('aria-pressed', 'true');
      position.setAttribute('aria-live', 'off');
      show(selected);
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
      if (event.matches) pause();
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) pause();
    });
    document.getElementById('viewer-controls').hidden = false;
    show(0);
  }).catch(() => {
    // Every project, source link and full image remains available without JS.
  });
})();
