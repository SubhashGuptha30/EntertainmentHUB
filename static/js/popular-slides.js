
// Removed hardcoded data
// const popularSlidesData = ...

// Function to shuffle array and select n random elements
function getRandomPopularSlides(arr, n) {
  const shuffled = arr.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

// Function to generate slide HTML
function generatePopularSlideHTML(slide) {
  return `
  <div class="swiper-slide">
    <div class="movie-box">
      <img src="${slide['v-image'] || slide.posterVertical || slide.imgSrc}" alt="${slide.title}" class="movie-box-img" onerror="this.src='/images/default-poster.jpg'" />
      <div class="box-text">
        <div class="movie-info">
          <h2 class="movie-title">${slide.title}</h2>
          <span class="movie-type">
            ${slide.genreDisplay || slide.genre || (slide.tags ? slide.tags.join(' • ') : '')}
          </span>
        </div>
        <div class="play-btn-box" title="Play Now">
          <a href="${DataManager.getItemPath(slide)}" class="play-btn">
            <i class="bx bx-right-arrow"></i>
          </a>
        </div>
      </div>
    </div>
  </div>
  `;
}

// Function to render slides
function renderPopularSlides() {
  // Use DataManager
  let items = [];
  if (DataManager.isLoaded) {
    items = DataManager.getPageFilteredItems('popular');
  } else {
    // Wait for data
    window.addEventListener('dataLoaded', renderPopularSlides);
    return;
  }

  const selectedSlides = getRandomPopularSlides(items, 8);
  const swiperWrapper = document.getElementById("popular-slides");
  // Clean first
  if (!swiperWrapper) return;

  swiperWrapper.innerHTML = selectedSlides.map(generatePopularSlideHTML).join("");

  const viewMoreSlide = `
  <div class="swiper-slide">
    <div class="view-more-box" title="View More">
      <a href="all-pop.html" class="view-more-btn">
        <span class="view-more-btn-box">
          <i class="bx bx-chevron-right-circle"></i>
          <span class="view-more">View More</span>
        </span>
      </a>
    </div>
  </div>
  `;
  swiperWrapper.innerHTML += viewMoreSlide;

  // Initialize Swiper
  if (window.setupSwiper) window.setupSwiper('.popular-content');
}

// Initialize the slider
document.addEventListener("DOMContentLoaded", () => {
  renderPopularSlides();
});

