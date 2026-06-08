// Function to shuffle array and select n random elements
function getRandomSlides(arr, n) {
  const shuffled = arr.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

// Function to generate slide HTML (forcing vertical poster only)
function generateVerticalSlideHTML(slide) {
  return `
  <div class="swiper-slide">
    <div class="movie-box">
      <img src="${slide['v-image'] || '/static/images/default-poster.jpg'}" alt="${slide.title}" class="movie-box-img" onerror="this.src='/static/images/default-poster.jpg'" />
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

// Function to render dynamic sections dynamically
function renderSections() {
  if (!DataManager.isLoaded) {
    window.addEventListener('dataLoaded', renderSections);
    return;
  }

  const sections = [
    { sectionKey: 'popular', wrapperId: 'popular-slides', seeAllLink: '/see-all?section=popular', max: 8, sliderSelector: '.popular-content' },
    { sectionKey: 'new-releases', wrapperId: 'new-slides', seeAllLink: '/see-all?section=new-releases', max: 9, sliderSelector: '#new .new-content' },
    { sectionKey: 'most-watched', wrapperId: 'most-watched-slides', seeAllLink: '/see-all?section=most-watched', max: 8, sliderSelector: '#most-watched .new-content' },
    { sectionKey: 'top-rated', wrapperId: 'top-rated-slides', seeAllLink: '/see-all?section=top-rated', max: 8, sliderSelector: '#top-rated .new-content' },
    { sectionKey: 'coming-soon', wrapperId: 'coming-soon-slides', seeAllLink: '/see-all?section=coming-soon', max: 8, sliderSelector: '#coming-soon .new-content' }
  ];

  // Detect page type for appending to see-all links
  const pageCategory = DataManager.getPageCategory();
  const typeSuffix = pageCategory ? `&type=${pageCategory}` : '';

  sections.forEach(config => {
    const swiperWrapper = document.getElementById(config.wrapperId);
    if (!swiperWrapper) return; // If section not on page, skip

    // get items filtered by section key AND current page category
    let items = DataManager.getPageFilteredItems(config.sectionKey);
    const selectedSlides = getRandomSlides(items, config.max);

    swiperWrapper.innerHTML = selectedSlides.map(generateVerticalSlideHTML).join("");

    const viewMoreSlide = `
    <div class="swiper-slide">
      <div class="view-more-box" title="View More">
        <a href="${config.seeAllLink}${typeSuffix}" class="view-more-btn">
          <span class="view-more-btn-box">
            <i class="bx bx-chevron-right-circle"></i>
            <span class="view-more">View More</span>
          </span>
        </a>
      </div>
    </div>
    `;
    swiperWrapper.innerHTML += viewMoreSlide;

    if (window.setupSwiper) window.setupSwiper(config.sliderSelector);
  });
}

// Initialize the sections
document.addEventListener("DOMContentLoaded", () => {
    renderSections();
});
