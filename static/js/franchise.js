// Franchise page — dynamically loads franchise data from API
document.addEventListener('DOMContentLoaded', async () => {
  const franchiseSection = document.querySelector('.franchises-section');
  if (!franchiseSection) return;

  try {
    const res = await fetch('/api/selectors/franchises');
    if (!res.ok) throw new Error('Failed to load franchises');
    const franchises = await res.json();

    if (!franchises.length) {
      franchiseSection.innerHTML = `
        <div style="text-align:center; padding:4rem 1rem; color:var(--text-muted);">
          <i class='bx bx-film' style="font-size:3rem;"></i>
          <p style="margin-top:1rem;">No franchises have been added yet.</p>
        </div>`;
      return;
    }

    franchiseSection.innerHTML = franchises.map(franchise => `
      <div class="franchise-card" title="${franchise.title}">
        <img src="${franchise.image || '/static/images/default-banner.jpg'}" alt="${franchise.title}" class="franchise-img"
             onerror="this.src='/static/images/default-banner.jpg'" />
        <div class="franchise-content">
          <h3 class="franchise-title">${franchise.title}</h3>
          <p class="franchise-desc">${franchise.description || ''}</p>
          <a href="/franchise-explore?franchise=${encodeURIComponent(franchise.title)}" class="view-btn"
             style="text-decoration:none; display:inline-block; text-align:center; padding-top: 5px;">Explore</a>
        </div>
      </div>
    `).join('');

  } catch (err) {
    console.error('Error loading franchises:', err);
    franchiseSection.innerHTML = `
      <div style="text-align:center; padding:4rem 1rem; color:var(--text-muted);">
        <p>Failed to load franchises. Please try again later.</p>
      </div>`;
  }
});
