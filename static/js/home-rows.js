// Franchise-first rows for Home and Anime pages.
// Usage: <section id="franchise-rows" data-rows="continue,universe,anime,compact"></section>
document.addEventListener('DOMContentLoaded', async () => {
  const host = document.getElementById('franchise-rows');
  if (!host) return;
  const wanted = (host.dataset.rows || '').split(',').map(s => s.trim()).filter(Boolean);

  const getJSON = url => fetch(url).then(r => (r.ok ? r.json() : [])).catch(() => []);
  const kindLabel = { universe: 'Universe', saga: 'Saga', anime: 'Anime', duology: 'Duology', trilogy: 'Trilogy',
                      standalone: 'Film', limited: 'Short series' };

  const franchiseCard = f => titleCard({
    href: `/franchise/${encodeURIComponent(f.slug)}`, title: f.title, image: f.image || f.cover,
    badge: kindLabel[f.kind],
    meta: [`${f.entry_count} entries`, f.total_minutes ? `<b>${f.runtime_complete ? '' : '~'}${fmtRuntime(f.total_minutes)}</b>` : '']
      .filter(Boolean).join(' · '),
  });

  const compactCard = i => titleCard({
    href: i.href, title: i.title, image: i.image, badge: kindLabel[i.kind],
    meta: [i.year ? esc(i.year) : '', i.runtime_min ? `<b>${fmtRuntime(i.runtime_min)}</b>` : ''].filter(Boolean).join(' · '),
  });

  const row = (title, sub, link, cards, wide) => cards.length ? `
    <div class="hrow">
      <div class="hrow-head">
        <div><h2>${title}</h2>${sub ? `<p>${sub}</p>` : ''}</div>
        ${link ? `<a href="${link}">See all <i class="bx bx-chevron-right"></i></a>` : ''}
      </div>
      <div class="hrow-track ${wide ? 'wide' : ''}">${cards.join('')}</div>
    </div>` : '';

  const builders = {
    async continue() {
      const list = await getJSON('/api/me/continue');
      return row('Continue your franchises', 'Pick up where you left off', '', list.map(c => titleCard({
        href: `/franchise/${encodeURIComponent(c.slug)}`, title: c.title, image: c.image,
        badge: `${c.done}/${c.total}`, progress: c.done / c.total,
        meta: c.next ? `Next: ${esc(c.next.title)}${c.next.label ? ' · ' + esc(c.next.label) : ''}` : '',
      })), true);
    },
    async universe() {
      const list = await getJSON('/api/franchises?kind=universe');
      return row('Start a universe', 'Shared worlds with a watch order', '/franchises', list.map(franchiseCard), true);
    },
    async saga() {
      const list = await getJSON('/api/franchises?kind=saga');
      return row('Sagas', 'Sequels, prequels and spin-offs in order', '/franchises', list.map(franchiseCard), true);
    },
    async anime() {
      const list = await getJSON('/api/franchises?kind=anime');
      return row('Anime sagas', 'Seasons, movies, filler and canon — sorted', '/franchises', list.map(franchiseCard), true);
    },
    async compact() {
      const list = await getJSON('/api/compact?max_minutes=720');
      return row('Finish this weekend', 'Complete stories under 12 hours', '/one-and-done', list.slice(0, 20).map(compactCard));
    },
    async 'anime-compact'() {
      const list = (await getJSON('/api/compact')).filter(i => i.type === 'animes');
      return row('Anime you can finish', 'Films and short series', '/one-and-done', list.map(compactCard));
    },
  };

  const html = await Promise.all(wanted.filter(k => builders[k]).map(k => builders[k]()));
  host.innerHTML = html.join('');
});
