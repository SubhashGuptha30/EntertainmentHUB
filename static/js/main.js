
// Escape DB strings before putting them into innerHTML templates
function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// "2h 12m" / "54h" from minutes; '' when unknown
function fmtRuntime(min) {
  if (!min) return '';
  const h = Math.floor(min / 60), m = min % 60;
  if (h >= 10) return `${Math.round(min / 60)}h`;
  return h ? (m ? `${h}h ${m}m` : `${h}h`) : `${m}m`;
}

// Stable gradient for titles without artwork, so cards never show a broken/grey box
function artStyle(title) {
  let hash = 0;
  for (const ch of String(title)) hash = (hash * 31 + ch.charCodeAt(0)) | 0;
  const hue = Math.abs(hash) % 360;
  return `background:linear-gradient(135deg,hsl(${hue} 55% 28%),hsl(${(hue + 50) % 360} 60% 12%))`;
}

// "Marvel Cinematic Universe" -> "MCU"; skips small words, max 3 letters
function monogram(title) {
  const words = String(title).replace(/[^\p{L}\p{N} ]/gu, ' ').split(/\s+/)
    .filter(w => w && !/^(the|of|a|and|in|to)$/i.test(w));
  return (words.length > 1 ? words.slice(0, 3).map(w => w[0]).join('') : (words[0] || '?').slice(0, 2)).toUpperCase();
}

// Poster-style card shared by home rows, One & Done and Anime pages.
// opts: { href, title, image, badge, meta (HTML, caller escapes), progress (0..1) }
function titleCard(o) {
  const art = o.image
    ? `<img src="${esc(o.image)}" alt="" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'tcard-art'}))">`
    : `<div class="tcard-art" style="${artStyle(o.title)}" aria-hidden="true"><span>${esc(monogram(o.title))}</span></div>`;
  return `
    <a class="tcard" href="${esc(o.href)}" aria-label="${esc(o.title)}">
      ${art}
      ${o.badge ? `<span class="tcard-badge">${esc(o.badge)}</span>` : ''}
      <div class="tcard-info">
        <div class="tcard-title">${esc(o.title)}</div>
        ${o.meta ? `<div class="tcard-meta">${o.meta}</div>` : ''}
        ${o.progress != null ? `<div class="tcard-progress"><div style="width:${Math.round(o.progress * 100)}%"></div></div>` : ''}
      </div>
    </a>`;
}

// --- Main Data Manager ---
/* global Swiper */

const DataManager = {
  data: {},
  isLoaded: false,

  async init() {
    if (this.isLoaded) return;
    try {
      // Fetch all content from the Flask API (returns { movies:{}, animes:{}, webSeries:{} })
      const res = await fetch('/api/content');
      if (!res.ok) throw new Error('API fetch failed: ' + res.status);
      const allData = await res.json();
      this.data = {
        movies:   allData.movies   || {},
        animes:   allData.animes   || {},
        webSeries: allData.webSeries || {}
      };
      this.isLoaded = true;
      // Dispatch event for other scripts
      window.dispatchEvent(new Event('dataLoaded'));
    } catch (error) {
      console.error('Failed to load content from API:', error);
    }
  },

  getAllItems(category) {
    let all = [];
    if (category) {
      // Only return items from the specified category
      const catData = this.data[category];
      if (catData) {
        for (const slug in catData) {
          all.push({ ...catData[slug], slug, type: category });
        }
      }
    } else {
      // Return items from all categories
      for (const cat in this.data) {
        for (const slug in this.data[cat]) {
          all.push({ ...this.data[cat][slug], slug, type: cat });
        }
      }
    }
    return all;
  },

  getItemsBySection(sectionName, category) {
    const items = this.getAllItems(category).filter(item =>
      item.sections && item.sections.includes(sectionName)
    );
    return items;
  },

  /**
   * Returns a random shuffle of items that have a horizontal image.
   * Used for the hero banner so it feels fresh on every page load.
   * @param {number} max - max items to return (default 12)
   */
  getHeroItems(max = 12, category = null) {
    const all = this.getAllItems(category).filter(item => item['h-image']);
    // Fisher-Yates shuffle
    for (let i = all.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [all[i], all[j]] = [all[j], all[i]];
    }
    return all.slice(0, max);
  },

  // Detect which data category the current page should show
  // Returns null for home (show all), or the category key for dedicated pages
  getPageCategory() {
    const path = window.location.pathname.toLowerCase();
    if (path.includes('movies')) return 'movies';
    if (path.includes('anime')) return 'animes';
    if (path.includes('web-series')) return 'webSeries';
    // home.html or any other page → show all categories
    return null;
  },

  // Convenience: get items filtered by section AND current page's category
  getPageFilteredItems(sectionName) {
    return this.getItemsBySection(sectionName, this.getPageCategory());
  },

  // Helper to generate correct Path
  getItemPath(item) {
    if (item.path) return item.path;
    return `/play?type=${item.type}&slug=${item.slug}`;
  }
};

document.addEventListener("DOMContentLoaded", function () {
  // 1. Preloader Logic
  const preloader = document.getElementById("preloader");
  const mainContent = document.getElementById("main-content");

  // Start Data Loading immediately
  DataManager.init();

  if (preloader) {
    setTimeout(function () {
      preloader.style.opacity = '0';
      setTimeout(() => {
        preloader.style.display = "none";
      }, 500);
    }, 1000);
  }

  // Initialize Header & Footer (if containers exist)
  if (document.getElementById("global-header")) {
    loadHeader();
  }
  if (document.getElementById("global-footer")) {
    loadFooter();
  }
});



// Helper: Load Header
function loadHeader() {
  const headerHTML = `
    <header>
      <div class="nav container">
        <a href="/home" class="logo" title="Entertainment Hub">
          Entertainment<span>Hub</span>
        </a>
        <div class="navbar">
          <a href="/home" class="nav-link" data-page="/home" title="Home">
            <i class="bx bx-home-alt-2"></i>
            <span class="nav-link-title">Home</span>
          </a>
          <a href="/franchises" class="nav-link" data-page="/franchises" title="Franchises">
            <i class="bx bx-git-branch"></i>
            <span class="nav-link-title">Franchises</span>
          </a>
          <a href="/anime" class="nav-link" data-page="/anime" title="Anime">
            <i class="bx bx-child"></i>
            <span class="nav-link-title">Anime</span>
          </a>
          <a href="/one-and-done" class="nav-link" data-page="/one-and-done" title="One &amp; Done: stories that end">
            <i class="bx bx-check-double"></i>
            <span class="nav-link-title">One &amp; Done</span>
          </a>
          <a href="/see-all?section=popular" class="nav-link" data-page="/see-all" title="Browse all titles">
            <i class="bx bx-grid-alt"></i>
            <span class="nav-link-title">Browse</span>
          </a>
        </div>
        <div class="search">
          <div class="search-box">
            <input type="search" title="Search" id="search-input" placeholder="Search here..." />
            <i class="bx bx-search"></i>
          </div>
          <div class="search-result"></div>
        </div>
        <a href="/profile" class="user">
          <img src="/images/user.png" alt="user profile" title="User Profile" class="user-img" />
        </a>
      </div>
    </header>
    `;

  document.getElementById("global-header").innerHTML = headerHTML;
  setActiveLink();
  initializeSearch(); // Re-bind search listeners to new DOM
}

// Helper: Load Footer
function loadFooter() {
  const footerHTML = `
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <h2>Entertainment<span>Hub</span></h2>
          <p>Every franchise and anime saga in the right watch order, plus stories you can finish this weekend.</p>
        </div>
        <div class="footer-links">
          <h3>Quick Links</h3>
          <ul>
            <li><a href="/franchises">Franchises</a></li>
            <li><a href="/one-and-done">One &amp; Done</a></li>
            <li><a href="/movies">Movies</a></li>
            <li><a href="/web-series">Series</a></li>
            <li><a href="/contact/contactus">Help & Support</a></li>
          </ul>
        </div>
        <div class="footer-social">
          <h3>Connect with Us</h3>
          <div class="social-icons">
            <a href="#" class="social-icon"><i class='bx bxl-facebook'></i></a>
            <a href="#" class="social-icon"><i class='bx bxl-twitter'></i></a>
            <a href="#" class="social-icon"><i class='bx bxl-instagram'></i></a>
            <a href="#" class="social-icon"><i class='bx bxl-youtube'></i></a>
          </div>
        </div>
      </div>
      <div class="copyright">
        <p>&copy; ${new Date().getFullYear()} Entertainment Hub. All Rights Reserved.</p>
      </div>
    </footer>
    `;

  document.getElementById("global-footer").innerHTML = footerHTML;
}


// Helper: Set Active Link
function setActiveLink() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link');

  // Default active state removal
  navLinks.forEach(link => link.classList.remove('link-active'));

  navLinks.forEach(link => {
    let linkPath = link.getAttribute('data-page');
    if (!linkPath) return;
    
    // Normalize both paths for comparison
    let currentNorm = currentPath.toLowerCase().replace('.html', '');
    let linkNorm = linkPath.toLowerCase().replace('.html', '');
    
    if (currentNorm === '/' || currentNorm === '') {
        currentNorm = '/home';
    }

    if (currentNorm.endsWith(linkNorm)) {
      link.classList.add('link-active');
    }
  });
}

// 3. Search Logic — searches by Title, Cast, and Genre/Tags
function initializeSearch() {
  const inputBox = document.getElementById("search-input");
  const searchResult = document.querySelector(".search-result");

  if (!inputBox || !searchResult) return;

  let allItems = [];
  const categoryLabels = { movies: 'Movie', animes: 'Anime', webSeries: 'Series' };

  // If DataManager already loaded, populate. Else wait.
  if (DataManager.isLoaded) {
    populateSearch();
  } else {
    window.addEventListener('dataLoaded', populateSearch);
  }

  let allFranchises = [];
  fetch('/api/franchises').then(r => (r.ok ? r.json() : [])).then(list => { allFranchises = list; }).catch(() => {});

  function populateSearch() {
    allItems = DataManager.getAllItems();
  }

  // Core search: returns results with match reason
  function performSearch(query) {
    if (!query || (!allItems.length && !allFranchises.length)) return [];
    const q = query.toLowerCase();
    const resultMap = new Map(); // slug -> result object (dedup)

    // Franchises first: they are what this site is about
    allFranchises.forEach(f => {
      if (f.title.toLowerCase().includes(q)) {
        resultMap.set('franchise_' + f.slug, {
          title: f.title, path: `/franchise/${encodeURIComponent(f.slug)}`,
          image: f.image || f.cover || '/static/images/default-poster.jpg',
          category: 'Franchise', matchType: 'title', matchLabel: f.title,
        });
      }
    });

    allItems.forEach(item => {
      const path = DataManager.getItemPath(item);
      const key = item.slug + '_' + item.type;
      const image = item['v-image'] || item['h-image'] || '/static/images/default-poster.jpg';
      const category = categoryLabels[item.type] || 'Content';

      // 1. Match by title
      if (item.title && item.title.toLowerCase().includes(q)) {
        if (!resultMap.has(key)) {
          resultMap.set(key, { title: item.title, path, image, category, matchType: 'title', matchLabel: item.title });
        }
      }

      // 2. Match by cast/actor name
      if (item.cast && Array.isArray(item.cast)) {
        item.cast.forEach(member => {
          if (member.name && member.name.toLowerCase().includes(q)) {
            if (!resultMap.has(key)) {
              resultMap.set(key, { title: item.title, path, image, category, matchType: 'cast', matchLabel: 'Cast: ' + member.name });
            } else {
              // Already matched by title, add cast as secondary info
              const existing = resultMap.get(key);
              if (existing.matchType === 'title') {
                existing.matchLabel2 = 'Cast: ' + member.name;
              }
            }
          }
        });
      }

      // 3. Match by genre/tag
      if (item.tags && Array.isArray(item.tags)) {
        item.tags.forEach(tag => {
          if (tag.toLowerCase().includes(q)) {
            if (!resultMap.has(key)) {
              resultMap.set(key, { title: item.title, path, image, category, matchType: 'genre', matchLabel: 'Genre: ' + tag });
            }
          }
        });
      }

      // 4. Match by language
      if (item.language && item.language.toLowerCase().includes(q)) {
        if (!resultMap.has(key)) {
          resultMap.set(key, { title: item.title, path, image, category, matchType: 'language', matchLabel: 'Language: ' + item.language });
        }
      }
    });

    // Convert map to array, limit results
    return Array.from(resultMap.values()).slice(0, 15);
  }

  let debounceTimeout;

  // Input handler
  inputBox.addEventListener("input", () => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      const query = inputBox.value.trim();
      if (query.length < 2) {
        searchResult.innerHTML = "";
        searchResult.classList.remove('active');
        return;
      }
      const results = performSearch(query);
      displayResults(results, searchResult, query);
    }, 250);
  });

  // Keyboard navigation
  inputBox.addEventListener("keydown", (e) => {
    const items = searchResult.querySelectorAll(".search-item");
    if (items.length === 0) return;

    let index = Array.from(items).indexOf(document.querySelector('.search-item.highlighted'));

    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (index >= 0) items[index].classList.remove('highlighted');
      index = (index + 1) % items.length;
      items[index].classList.add('highlighted');
      items[index].scrollIntoView({ block: 'nearest' });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (index >= 0) items[index].classList.remove('highlighted');
      index = (index - 1 + items.length) % items.length;
      items[index].classList.add('highlighted');
      items[index].scrollIntoView({ block: 'nearest' });
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (index >= 0) {
        items[index].click();
      } else if (items.length > 0) {
        items[0].click();
      }
    } else if (e.key === "Escape") {
      searchResult.innerHTML = "";
      searchResult.classList.remove('active');
      inputBox.blur();
    }
  });

  // Click outside to close
  document.addEventListener("click", (e) => {
    if (!e.target.closest('.search')) {
      searchResult.innerHTML = "";
      searchResult.classList.remove('active');
    }
  });
}

// Display rich search results
function displayResults(results, container, query) {
  if (!results.length) {
    container.innerHTML = `<div class="search-empty"><i class='bx bx-search-alt'></i><span>No results for "${esc(query)}"</span></div>`;
    container.classList.add('active');
    return;
  }

  // Escape first, then highlight the (escaped) query, so DB text and typed input can't inject HTML
  const highlight = (text) => {
    const regex = new RegExp(`(${esc(query).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return esc(text).replace(regex, '<mark>$1</mark>');
  };

  const html = results.map(r => `
    <div class="search-item" tabindex="0" data-href="${esc(r.path)}" role="link">
      <img class="search-item-img" src="${esc(r.image)}" alt="" onerror="this.src='/static/images/default-poster.jpg'">
      <div class="search-item-info">
        <div class="search-item-title">${highlight(r.title)}</div>
        <div class="search-item-meta">
          <span class="search-badge search-badge--${esc(r.matchType)}">${r.matchType === 'title' ? esc(r.category) : highlight(r.matchLabel)}</span>
          ${r.matchLabel2 ? `<span class="search-badge search-badge--cast">${esc(r.matchLabel2)}</span>` : ''}
          ${r.matchType !== 'title' ? `<span class="search-badge search-badge--category">${esc(r.category)}</span>` : ''}
        </div>
      </div>
      <i class='bx bx-chevron-right search-item-arrow'></i>
    </div>
  `).join('');

  container.innerHTML = html;
  container.querySelectorAll('.search-item').forEach(el =>
    el.addEventListener('click', () => { window.location.href = el.dataset.href; }));
  container.classList.add('active');
}



// Swiper Initialization Helper
/* global Swiper */
window.setupSwiper = function (selector) {
  // Common config
  const commonConfig = {
    slidesPerView: 1,
    spaceBetween: 10,
    autoplay: {
      delay: 7500, // Slightly faster than original huge number
      disableOnInteraction: false,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    breakpoints: {
      280: { slidesPerView: 1, spaceBetween: 10 },
      320: { slidesPerView: 2, spaceBetween: 10 },
      510: { slidesPerView: 2, spaceBetween: 10 },
      758: { slidesPerView: 3, spaceBetween: 15 },
      900: { slidesPerView: 4, spaceBetween: 20 },
    },
  };

  const headConfig = {
    centeredSlides: true,
    slidesPerView: 1,
    spaceBetween: 10,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    rewind: true,
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
  };

  // Select elements safely
  const elements = document.querySelectorAll(selector);
  elements.forEach(el => {
    // Check if already initialized to avoid double init (optional, but good practice)
    if (el.swiper) el.swiper.destroy(true, true);

    if (selector.includes('head-content') || el.classList.contains('head-content')) {
      new Swiper(el, headConfig);
    } else {
      new Swiper(el, commonConfig);
    }
  });
};
