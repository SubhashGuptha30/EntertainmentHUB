// Franchises list page — cards with stats, filtered by kind
document.addEventListener('DOMContentLoaded', () => {
  const grid = document.querySelector('.franchises-section');
  if (!grid) return;

  const statLabels = { movies: 'Movies', webSeries: 'Series', animes: 'Anime' };

  const card = f => {
    const stats = Object.entries(f.counts || {})
      .filter(([, n]) => n > 0)
      .map(([t, n]) => `<div class="franchise-stat"><b>${n}</b><span>${statLabels[t]}</span></div>`)
      .join('');
    return `
      <a class="franchise-card" href="/franchise/${encodeURIComponent(f.slug)}" title="${esc(f.title)}">
        <span class="franchise-kind">${esc(f.kind)}</span>
        ${(f.image || f.cover)
          ? `<img src="${esc(f.image || f.cover)}" alt="" class="franchise-img" loading="lazy"
                 onerror="this.src='/static/images/default-banner.jpg'" />`
          : `<div class="franchise-img" style="${artStyle(f.title)}" aria-hidden="true"></div>`}
        <div class="franchise-content">
          <h3 class="franchise-title">${esc(f.title)}</h3>
          <div class="franchise-stats">${stats}${f.total_minutes
            ? `<div class="franchise-stat"><b>${f.runtime_complete ? '' : '~'}${fmtRuntime(f.total_minutes)}</b><span>To watch</span></div>` : ''}</div>
          <p class="franchise-desc">${esc(f.description)}</p>
          <span class="view-btn">Watch order</span>
        </div>
      </a>`;
  };

  const empty = msg => `
    <div style="grid-column:1/-1; text-align:center; padding:4rem 1rem; color:var(--text-muted);">
      <i class='bx bx-film' style="font-size:3rem;"></i><p style="margin-top:1rem;">${msg}</p>
    </div>`;

  async function load(kind) {
    try {
      const res = await fetch('/api/franchises' + (kind ? `?kind=${kind}` : ''));
      if (!res.ok) throw new Error(res.status);
      const list = await res.json();
      grid.innerHTML = list.length ? list.map(card).join('') : empty('No franchises here yet.');
    } catch (err) {
      console.error('Error loading franchises:', err);
      grid.innerHTML = empty('Failed to load franchises. Please try again later.');
    }
  }

  document.querySelectorAll('button.franchise-chip').forEach(btn => btn.addEventListener('click', () => {
    document.querySelectorAll('button.franchise-chip').forEach(b => b.classList.toggle('active', b === btn));
    load(btn.dataset.kind);
  }));

  load('universe,saga,anime');   // duologies/trilogies live on One & Done
});
