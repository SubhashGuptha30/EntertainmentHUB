
// Removed hardcoded data
// const mostWatchedSlidesData = ...

// Function to shuffle array and select n random elements
function getRandomMostWatchedSlides(arr, n) {
  const shuffled = arr.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

// Function to generate slide HTML
function generateMostWatchedSlideHTML(slide) {
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
function renderMostWatchedSlides() {
  let items = [];
  if (DataManager.isLoaded) {
    items = DataManager.getPageFilteredItems('most-watched');
  } else {
    window.addEventListener('dataLoaded', renderMostWatchedSlides);
    return;
  }

  const swiperWrapper = document.getElementById("most-watched-slides");
  // Clean first
  if (!swiperWrapper) return;

  const selectedSlides = getRandomMostWatchedSlides(items, 8);
  swiperWrapper.innerHTML = selectedSlides.map(generateMostWatchedSlideHTML).join("");
  const viewMoreSlide = `
  <div class="swiper-slide">
    <div class="view-more-box" title="View More">
      <a href="all-most-watched.html" class="view-more-btn">
        <span class="view-more-btn-box">
          <i class="bx bx-chevron-right-circle"></i>
          <span class="view-more">View More</span>
        </span>
      </a>
    </div>
  </div>
  `;
  swiperWrapper.innerHTML += viewMoreSlide;
  if (window.setupSwiper) window.setupSwiper('#most-watched .new-content');
}

// Initialize the slider
document.addEventListener("DOMContentLoaded", () => {
  renderMostWatchedSlides();
});

