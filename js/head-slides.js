const headSlidesData = [
  {
    title: "Avengers: Endgame",
    category: "Movie",
    rating: "PG-13",
    genre: "Action &centerdot; Adventure &centerdot; Drama &centerdot; Sci-Fi",
    imgSrc: "/images/horizontal/avengers-endgame.jpg",
    path: "/movies/avengers-endgame.html"
  },
  {
    title: "One Piece",
    category: "Anime",
    rating: "PG-14",
    genre: "Animation &centerdot; Action &centerdot; Adventure &centerdot; Comedy &centerdot; Drama &centerdot; Fantasy",
    imgSrc: "/images/horizontal/one-piece.jpg",
    path: "/anime/one-piece.html"
  },
  {
    title: "The Boys",
    category: "Series",
    rating: "18+",
    genre: "Action &centerdot; Comedy &centerdot; Crime",
    imgSrc: "/images/horizontal/the-boys.jpg",
    path: "/web-series/the-boys.html"
  },
  {
    title: "Godzilla x Kong: The New Empire",
    category: "Movie",
    rating: "PG-13",
    genre: "Action &centerdot; Adventure &centerdot; Thriller &centerdot; Sci-Fi",
    imgSrc: "/images/horizontal/godzilla-x-kong-the-new-empire.jpg",
    path: "/movies/godzilla-x-kong-the-new-empire.html"
  },
  {
    title: "Your Lie in April",
    category: "Anime",
    rating: "PG-13",
    genre: "Animation &centerdot; Drama &centerdot; Romance &centerdot; Music &centerdot; Comedy",
    imgSrc: "/images/horizontal/your-lie-in-april.jpg",
    path: "/anime/your-lie-in-april.html"
  },
  {
    title: "Squid Game",
    category: "Series",
    rating: "18+",
    genre: "Action &centerdot; Mystery &centerdot; Drama &centerdot; Thriller",
    imgSrc: "/images/horizontal/squid-game.jpg",
    path: "/web-series/squid-game.html"
  },
  {
    title: "Zack Snyder's Justice League",
    category: "Movie",
    rating: "R",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy &centerdot; Sci-fi",
    imgSrc: "/images/horizontal/zack-snyder-justice-league.jpg",
    path: "/movies/zack-snyder-justice-league.html"
  },
  {
    title: "Weathering With You",
    category: "Anime",
    rating: "PG-13",
    genre: "Action &centerdot; Fantasy &centerdot; Drama",
    imgSrc: "/images/horizontal/weathering-with-you.jpg",
    path: "/anime/weathering-with-you.html"
  },
  {
    title: "Your Name",
    category: "Anime",
    rating: "PG-12",
    genre: "Animation &centerdot; Fantasy &centerdot; Drama",
    imgSrc: "/images/horizontal/your-name.jpg",
    path: "/anime/your-name.html"
  },
  {
    title: "Bheemla Nayak",
    category: "Movie",
    rating: "PG-15",
    genre: "Action &centerdot; Drama &centerdot; Thriller",
    imgSrc: "/images/horizontal/bheemla-nayak.jpg",
    path: "/movies/bheemla-nayak.html"
  },
  {
    title: "Vikram Hitlist",
    category: "Movie",
    rating: "NR",
    genre: "Action &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/horizontal/vikram-hitlist.jpg",
    path: "/movies/vikram-hitlist.html"
  },
  {
    title: "The Marvels",
    category: "Movie",
    rating: "PG-13",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy",
    imgSrc: "/images/horizontal/the-marvels.jpg",
    path: "/movies/the-marvels.html"
  },
  {
    title: "Oppenheimer",
    category: "Movie",
    rating: "R",
    genre: "Biography &centerdot; History &centerdot; Drama",
    imgSrc: "/images/horizontal/oppenheimer.jpg",
    path: "/movies/oppenheimer.html"
  },
  {
    title: "Avatar: The Last Airbender",
    category: "Series",
    rating: "PG-12",
    genre: "Action &centerdot; Adventure &centerdot; Comedy",
    imgSrc: "/images/horizontal/avatar-the-last-airbender.jpg",
    path: "/web-series/avatar-the-last-airbender.html"
  },
  {
    title: "Dhootha",
    category: "Series",
    rating: "PG-13",
    genre: "Drama &centerdot; Horror &centerdot; Thriller",
    imgSrc: "/images/horizontal/dhootha.jpg",
    path: "/movies/dhootha.html"
  },
  {
    title: "Attack On Titan",
    category: "Anime",
    rating: "PG-15",
    genre: "Animation &centerdot; Action &centerdot; Drama &centerdot; Horror &centerdot; Thriller",
    imgSrc: "/images/horizontal/attack-on-titan.jpeg",
    path: "/movies/attack-on-titan.html"
  }
];

// Function to shuffle array and select n random elements
function getRandomheadSlides(arr, n) {
  const shuffled = arr.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

// Function to generate slide HTML
function generateheadSlideHTML(slide) {
  return `
      <div class="swiper-slide">
        <div class="head-box">
          <img src="${slide.imgSrc}" alt="${slide.title}" class="head-img" />
          <div class="head-text">
            <div class="head-text-info">
              <h1 class="head-title">${slide.title}</h1>
              <p>
              ${slide.category}<br />
              ${slide.rating}<br />
              ${slide.genre}<br />
              </p>
            </div>
            <div class="watch">
              <span class="tooltip">Watch Now</span>
              <span class="text">
                <div class="borde-back">
                  <div class="watch-btn-box" title="Watch Now">
                    <a href="${slide.path}" class="watch-btn">
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
  const selectedSlides = getRandomheadSlides(headSlidesData, 6);
  const swiperWrapper = document.getElementById("head-slides");
  swiperWrapper.innerHTML = selectedSlides.map(generateheadSlideHTML).join("");
}

// Initialize the slider
document.addEventListener("DOMContentLoaded", () => {
  renderheadSlides();
});
