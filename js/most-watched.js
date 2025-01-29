const mostWatchedSlidesData = [
  {
    title: "Extraction 2",
    genre: "Action &centerdot; Crime &centerdot; Thriller",
    imgSrc: "/images/vertical/extraction-2.jpg",
    path: "/movies/extraction-2.html"
  },
  {
    title: "Shōgun",
    genre: "Adventure &centerdot; Drama &centerdot; History &centerdot; War",
    imgSrc: "/images/vertical/shogun.jpg",
    path: "/web-series/shogun.html"
  },
  {
    title: "Classroom of the Elite",
    genre: "Animation &centerdot; Drama &centerdot; Thriller &centerdot; Psychological",
    imgSrc: "/images/vertical/classroom-of-the-elite.jpeg",
    path: "/anime/classroom-of-the-elite.html"
  },
  {
    title: "Dune Part Two",
    genre: "Drama &centerdot; Adventure &centerdot; Sci-fi &centerdot; Action",
    imgSrc: "/images/vertical/dune-part-two.jpeg",
    path: "/web-series/dune-part-two.html"
  },
  {
    title: "Game of Thrones: House of The Dragon",
    genre: "Fantasy &centerdot; Action &centerdot; Adventure &centerdot; Drama",
    imgSrc: "/images/vertical/game-of-thrones-house-of-the-dragon.jpeg",
    path: "/web-series/game-of-thrones-house-of-the-dragon.html"
  },
  {
    title: "Fifty Shades of Grey",
    genre: "Romance &centerdot; Thriller &centerdot; Drama",
    imgSrc: "/images/vertical/fifty-shades-of-gray.jpeg",
    path: "/movies/fifty-shades-of-gray.html"
  },
  {
    title: "Kantara",
    genre: "Action &centerdot; Drama &centerdot; Adventure &centerdot; Thriller",
    imgSrc: "/images/vertical/kantara.jpeg",
    path: "/movies/kantara.html"
  },
  {
    title: "Spirited Away",
    genre: "Adventure &centerdot; Drama &centerdot; Animation &centerdot; Fantasy",
    imgSrc: "/images/vertical/spirited-away.jpg",
    path: "/anime/spirited-away.html"
  },
  {
    title: "Secret Invasion",
    genre: "Action &centerdot; Sci-fi &centerdot; Drama &centerdot; Mystery",
    imgSrc: "/images/vertical/mw-9.jpeg",
    path: "/web-series/secret-invasion.html"
  },
  {
    title: "Vikram Vedha",
    genre: "Action &centerdot; Drama &centerdot; Crime",
    imgSrc: "/images/vertical/mw-10.jpeg",
    path: "/movies/vikram-vedha.html"
  },
  {
    title: "Gangubhai Kathiawadi",
    genre: "Biography &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/mw-11.jpeg",
    path: "/movies/gangubhai-khathiawadi.html"
  },
  {
    title: "Death Note",
    genre: "Animation &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/mw-12.jpeg",
    path: "/anime/death-note.html"
  },
  {
    title: "Animal",
    genre: "Action &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/mw-13.jpg",
    path: "/movies/animal.html"
  },
  {
    title: "Leo",
    genre: "Biography &centerdot; History &centerdot; Drama",
    imgSrc: "/images/vertical/mw-14.jpeg",
    path: "/movies/Leo.html"
  },
  {
    title: "Karthikeya 2",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy",
    imgSrc: "/images/vertical/mw-15.jpg",
    path: "/movies/Karthikeya-2.html"
  },
  {
    title: "Peacemaker",
    genre: "Action &centerdot; Adventure &centerdot; Comedy",
    imgSrc: "/images/vertical/mw-16.jpeg",
    path: "/web-series/peacemaker.html"
  },
  {
    title: "My Hero Academia: Season 2",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/mw-17.jpeg",
    path: "/anime/my-hero-academia-s4.html"
  },
  {
    title: "Black Clover",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/mw-18.jpeg",
    path: "/anime/black-clover.html"
  },
  {
    title: "Guntur Karam",
    genre: "Action &centerdot; Drama",
    imgSrc: "/images/vertical/mw-19.jpg",
    path: "/movies/guntur-karam.html"
  },
  {
    title: "Wednesday",
    genre: "Comedy &centerdot; Crime &centerdot; Fantasy",
    imgSrc: "/images/vertical/mw-20.jpg",
    path: "/web-series/wednesday.html"
  }
];

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
      <img src="${slide.imgSrc}" alt="${slide.title}" class="movie-box-img" />
      <div class="box-text">
        <div class="movie-info">
          <h2 class="movie-title">${slide.title}</h2>
          <span class="movie-type">
            ${slide.genre}
          </span>
        </div>
        <div class="play-btn-box" title="Play Now">
          <a href="${slide.path}" class="watch-btn play-btn">
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
  const swiperWrapper = document.getElementById("most-watched-slides");
  const selectedSlides = getRandomMostWatchedSlides(mostWatchedSlidesData, 8);
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
}

// Initialize the slider
document.addEventListener("DOMContentLoaded", () => {
  renderMostWatchedSlides();
});
