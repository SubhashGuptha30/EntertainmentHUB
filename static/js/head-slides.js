
// Function to generate slide HTML
function generateheadSlideHTML(slide) {
  // Use category or derive from type
  let categoryDisplay = slide.category || "";
  if (!categoryDisplay) {
    if (slide.type === 'animes') categoryDisplay = "Anime";
    else if (slide.type === 'webSeries') categoryDisplay = "Series";
    else categoryDisplay = "Movie";
  }

  return `
      <div class="swiper-slide">
        <div class="head-box">
          <img src="${slide['h-image'] || slide.posterHorizontal || slide.imgSrc}" alt="${slide.title}" class="head-img" onerror="this.src='/images/default-banner.jpg'" />
          <div class="head-text">
            <div class="head-text-info">
              <h1 class="head-title">${slide.title}</h1>
              <p>
              ${categoryDisplay}<br />
              ${slide.rating || "UA"}<br />
              ${slide.genreDisplay || slide.genre || (slide.tags ? slide.tags.join(' • ') : '')}<br />
              </p>
            </div>
            <div class="watch">
              <span class="tooltip">Watch Now</span>
              <span class="text">
                <div class="borde-back">
                  <div class="watch-btn-box" title="Watch Now">
                    <a href="${DataManager.getItemPath(slide)}" class="watch-btn">
                      <i class="bx bx-right-arrow"></i>
                    </a>
                  </div>
                </div>
              </span>
            </div>
          </div>
        </div>
      </div>
    `;
}

// Function to render slides
function renderheadSlides() {
  if (!DataManager.isLoaded) {
    window.addEventListener('dataLoaded', renderheadSlides);
    return;
  }

  // Randomly sample items with horizontal posters — filter by page category
  const selectedSlides = DataManager.getHeroItems(8, DataManager.getPageCategory());
  const swiperWrapper = document.getElementById('head-slides');
  if (!swiperWrapper) return;

  swiperWrapper.innerHTML = selectedSlides.map(generateheadSlideHTML).join('');
  if (window.setupSwiper) window.setupSwiper('.head-content');
}

// Initialize the slider
document.addEventListener("DOMContentLoaded", () => {
  renderheadSlides();
});

