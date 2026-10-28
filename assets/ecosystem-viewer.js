'use strict';
(async function () {
  const $ = id => document.getElementById(id);
  const groups = [
    {id:'hub', title:'Factory core', code:'CONTROL', icon:'⌘', color:'#91f2cd', featured:'ai-dashboard', story:'Meet the command center', description:'AI Dashboard brings the workshop into one operator surface. Cofoundry and the local AI workspace sit alongside it in the factory core.'},
    {id:'work', title:'Intent & delivery', code:'BUILD', icon:'↗', color:'#9dbdff', featured:'taskrivet', story:'Give an idea a place to work', description:'Capture intent with Panther, keep agent sessions in Taskrivet, and explore bounded preparation and supervision tools.'},
    {id:'proof', title:'Evidence & memory', code:'VERIFY', icon:'◇', color:'#baa6ff', featured:'el-verificador', story:'Make the result reviewable', description:'Explore independent checks, shared evidence formats and retained lessons. Each project has its own maturity and contribution surface.'},
    {id:'edge', title:'Machines & inference', code:'COMPUTE', icon:'⌁', color:'#7ddde6', featured:'the-surveyor', story:'Know the machines', description:'Discover hardware, inspect resource constraints and explore inference queues. Prototypes and unfinished adapters stay labelled.'},
    {id:'lab', title:'Simulation lab', code:'EXPERIMENT', icon:'⚗', color:'#ffd28c', featured:'mockmill', story:'Try something safely fictional', description:'Mockmill and the private simulations provide fictional fixtures and experiments for rehearsing product and platform ideas.'},
    {id:'surface', title:'Publishing & portals', code:'SHARE', icon:'▤', color:'#f5a8be', featured:'hamanakam1.github.io', story:'Give the workshop a front door', description:'Explore the atlas, profile, publishing adapters and client surfaces. Private source still requires access.'},
    {id:'upstream', title:'Upstream connections', code:'COLLABORATE', icon:'⑂', color:'#b9c9f3', featured:'archify', story:'Build with other communities', description:'Archify and the sandbox workshop connect this ecosystem to upstream projects. Check their contribution guidance before starting.'}
  ];
  const groupById = new Map(groups.map(g => [g.id, g]));
  const search = $('project-search'), access = $('access-filter'), dialog = $('project-dialog');
  let projects = [], activeGroup = 'hub', selected = '', tourIndex = -1;
  document.querySelectorAll('.toolbar button,.toolbar input,.toolbar select').forEach(control => { control.disabled = true; });
  const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');
  let motion = !motionQuery.matches;
  function setMotion(value) {
    motion = value; document.body.classList.toggle('motion-off', !motion);
    $('motion').setAttribute('aria-pressed', String(motion)); $('motion').textContent = `Motion ${motion ? 'on' : 'off'}`;
  }
  setMotion(motion);
  motionQuery.addEventListener('change', e => setMotion(!e.matches));
  $('motion').addEventListener('click', () => setMotion(!motion));
  function el(tag, text, className) { const node = document.createElement(tag); if (text) node.textContent = text; if (className) node.className = className; return node; }
  function matches(project) {
    const q = search.value.trim().toLowerCase();
    return (access.value === 'all' || project.access === access.value) && (!q || project.search.includes(q));
  }
  function visibleProjects() { return projects.filter(p => matches(p) && (!activeGroup || p.group === activeGroup)); }
  function endTour() { tourIndex = -1; $('tour').hidden = true; $('tour-start').textContent = 'Take a tour →'; }
  function renderStations() {
    const focusedGroup = document.activeElement.dataset.group;
    $('stations').replaceChildren(...groups.map(group => {
      const all = projects.filter(p => p.group === group.id), count = all.filter(matches).length;
      const button = el('button', null, 'station'); button.type = 'button'; button.dataset.group = group.id;
      button.style.setProperty('--accent', group.color); button.setAttribute('aria-pressed', String(activeGroup === group.id));
      button.setAttribute('aria-label', `${group.title}, ${count} matching projects`);
      const icon = el('span', group.icon, 'station-icon'); icon.setAttribute('aria-hidden', 'true');
      const label = el('span'); label.append(el('strong', group.title), el('small', `${count} ${count === 1 ? 'project' : 'projects'}${group.id === 'hub' ? ' · the integration hub' : ''}`));
      button.append(el('span', group.code, 'station-code'), icon, label);
      button.addEventListener('click', () => { endTour(); activeGroup = group.id; render(); });
      return button;
    }));
    if (focusedGroup) document.querySelector(`[data-group="${focusedGroup}"]`)?.focus({preventScroll:true});
  }
  function render() {
    renderStations();
    const visible = visibleProjects();
    $('list-title').textContent = activeGroup ? groupById.get(activeGroup).title : 'All projects';
    $('results-status').textContent = `${visible.length} of ${projects.length} projects${search.value.trim() ? ` matching “${search.value.trim()}”` : ''} · select one to open the hood`;
    $('project-list').replaceChildren(...visible.map(project => {
      const button = el('button', null, 'project-button'); button.type = 'button'; button.dataset.project = project.id;
      button.setAttribute('aria-pressed', String(selected === project.id));
      button.append(el('strong', project.id), el('small', `${project.access === 'public' ? 'Public' : 'Private'} · ${project.maturity}`));
      const arrow = el('span', '↗', 'project-arrow'); arrow.setAttribute('aria-hidden', 'true'); button.append(arrow);
      button.addEventListener('click', () => { endTour(); select(project.id, true); }); return button;
    }));
    $('empty-state').hidden = visible.length > 0;
    $('surprise').disabled = visible.length === 0;
    if (visible.length) select(visible.find(p => p.id === selected)?.id || visible[0].id);
    else {
      selected = '';
      $('project-detail').replaceChildren(el('p', 'No matching project. Clear the filters to keep exploring.', 'detail-description'));
      $('mobile-detail').replaceChildren();
      history.replaceState(null, '', location.pathname + location.search);
    }
  }
  function detail(project) {
    const fragment = document.createDocumentFragment();
    fragment.append(el('p', groupById.get(project.group).title, 'detail-area'), el('h2', project.id, 'detail-title'));
    const badges = el('div', null, 'badges'); badges.append(el('span', project.access === 'public' ? 'Public source' : 'Private source', `badge ${project.access}`), el('span', project.maturity, 'badge'));
    fragment.append(badges, el('p', project.description, 'detail-description'));
    const help = el('div', null, 'contribute-card'); help.append(el('h3', 'YOUR WAY IN'), el('p', project.contribution)); fragment.append(help);
    const links = el('div', null, 'detail-links');
    for (const source of project.links) { const a = el('a', source.textContent.trim() + ' ↗'); a.href = source.href; links.append(a); }
    fragment.append(links);
    const extra = el('div', null, 'detail-tools'), atlasLink = el('a', 'Read in the atlas'); atlasLink.href = `index.html#project-${project.id}`;
    const copy = el('button', 'Copy project link', 'quiet'); copy.type = 'button';
    copy.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(new URL(`#project=${encodeURIComponent(project.id)}`, location.href).href); copy.textContent = 'Link copied ✓'; }
      catch { copy.textContent = 'Copy from address bar'; }
    }); extra.append(atlasLink, copy); fragment.append(extra); return fragment;
  }
  function select(id, openMobile = false, updateUrl = true) {
    const project = projects.find(p => p.id === id); if (!project) return;
    selected = id;
    $('selection-status').textContent = `Selected ${id}. ${project.maturity}. ${project.access} source.`;
    $('project-detail').replaceChildren(detail(project)); $('mobile-detail').replaceChildren(detail(project));
    document.querySelectorAll('[data-project]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.project === selected)));
    if (updateUrl) history.replaceState(null, '', `#project=${encodeURIComponent(id)}`);
    if (openMobile && matchMedia('(max-width:850px)').matches && !dialog.open) dialog.showModal();
  }
  function resetFilters() { search.value = ''; access.value = 'all'; activeGroup = null; endTour(); render(); }
  function tourStep(index) {
    tourIndex = index; const group = groups[index]; search.value = ''; access.value = 'all'; activeGroup = group.id; selected = group.featured;
    render(); select(group.featured, false); if (dialog.open) dialog.close();
    $('tour').hidden = false; $('tour-step').textContent = `FACTORY TOUR / ${index + 1} OF ${groups.length}`;
    $('tour-title').textContent = group.story; $('tour-description').textContent = group.description;
    $('tour-prev').disabled = index === 0; $('tour-next').textContent = index === groups.length - 1 ? 'Finish tour ✓' : 'Next stop →';
    $('tour-start').textContent = 'Restart tour ↻';
    if (matchMedia('(max-width:850px)').matches) $('tour').scrollIntoView({block:'nearest'});
  }
  $('tour-start').addEventListener('click', () => tourStep(0));
  $('tour-prev').addEventListener('click', () => { if (tourIndex > 0) tourStep(tourIndex - 1); });
  $('tour-next').addEventListener('click', () => { if (tourIndex === groups.length - 1) { endTour(); $('tour-start').focus(); } else tourStep(tourIndex + 1); });
  $('tour-inspect').addEventListener('click', () => { if (tourIndex >= 0 && !dialog.open) dialog.showModal(); });
  $('tour-close').addEventListener('click', () => { endTour(); $('tour-start').focus(); });
  $('show-all').addEventListener('click', () => { activeGroup = null; endTour(); render(); });
  $('clear-filters').addEventListener('click', resetFilters);
  search.addEventListener('input', () => { activeGroup = null; endTour(); render(); });
  access.addEventListener('change', () => { activeGroup = null; endTour(); render(); });
  $('surprise').addEventListener('click', () => { const pool = visibleProjects().filter(p => p.id !== selected); const choice = pool.length ? pool[Math.floor(Math.random() * pool.length)] : visibleProjects()[0]; if (choice) { endTour(); select(choice.id, true); document.querySelector(`[data-project="${CSS.escape(choice.id)}"]`)?.scrollIntoView({block:'nearest'}); } });
  $('close-dialog').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
  addEventListener('keydown', e => { if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !dialog.open) { e.preventDefault(); search.focus(); } });
  function fromHash(openMobile = false) {
    const id = new URLSearchParams(location.hash.slice(1)).get('project'), project = projects.find(p => p.id === id);
    if (project) { activeGroup = project.group; selected = project.id; search.value = ''; access.value = 'all'; endTour(); render(); select(project.id, openMobile, false); return true; } return false;
  }
  addEventListener('hashchange', () => fromHash(true));
  try {
    const response = await fetch('index.html'); if (!response.ok) throw new Error('Atlas unavailable');
    const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
    projects = [...doc.querySelectorAll('.repo-card[id^="project-"]')].map(card => {
      const group = card.closest('section').id;
      const project = {id:card.id.slice(8), group, access:card.querySelector('.repo-badge').textContent.trim().toLowerCase(), maturity:card.querySelector('.maturity').textContent.trim(), description:card.querySelector('.repo-description').textContent.trim(), contribution:card.querySelector('.contribution').textContent.replace(/^Where you could help:\s*/, '').trim(), links:[...card.querySelectorAll('.repo-links a')].filter(a => /^https:\/\//.test(a.getAttribute('href')))};
      if (!groupById.has(group)) throw new Error('Unknown area');
      project.search = [project.id, groupById.get(group).title, project.maturity, project.description, project.contribution].join(' ').toLowerCase(); return project;
    });
    if (!projects.length) throw new Error('Empty atlas');
    $('total-count').textContent = projects.length; const publicCount = projects.filter(p => p.access === 'public').length;
    $('access-count').textContent = `${publicCount} public · ${projects.length - publicCount} private`;
    document.querySelectorAll('.toolbar button,.toolbar input,.toolbar select').forEach(control => { control.disabled = false; });
    $('load-status').hidden = true; $('factory').hidden = false;
    if (!fromHash(true)) { render(); select('ai-dashboard', false, false); }
  } catch (error) {
    $('load-status').replaceChildren(el('span', 'The interactive floor could not load. '));
    const fallback = el('a', 'Browse the complete text atlas →'); fallback.href = 'index.html#repos'; $('load-status').append(fallback);
    document.querySelectorAll('.toolbar button,.toolbar input,.toolbar select').forEach(control => { control.disabled = true; });
  }
}());
