const popularSlidesData = [
  {
    title: "Avengers: Infinity War",
    genre: "Action &centerdot; Adventure &centerdot; Sci-Fi",
    imgSrc: "/images/vertical/avengers-infinity-war.jpeg",
    path: "/movies/avengers-infinity-war.html"
  },
  {
    title: "Baahubali 2: The Conclusion",
    genre: "Action &centerdot; Drama",
    imgSrc: "/images/vertical/baahubali-2-the-conclusion.jpg",
    path: "/movies/baahubali-2-the-conclusion.html"
  },
  {
    title: "One Punch Man",
    genre: "Animation &centerdot Action &centerdot; Comedy",
    imgSrc: "/images/vertical/one-punch-man.jpg",
    path: "/anime/one-punch-man.html"
  },
  {
    title: "Stranger Things",
    genre: "Drama &centerdot; Fantasy &centerdot; Horror",
    imgSrc: "/images/vertical/stranger-things.jpeg",
    path: "/web-series/stranger-things.html"
  },
  {
    title: "A Silent Voice",
    genre: "Animation &centerdot; Drama",
    imgSrc: "/images/vertical/a-silent-voice.jpg",
    path: "/anime/a-silent-voice.html"
  },
  {
    title: "Salaar: Part 1 - Ceasefire",
    genre: "Action &centerdot; Drama &centerdot; Crime",
    imgSrc: "/images/vertical/salaar-part-1-ceasefire.jpg",
    path: "/movies/salaar-part-1-ceasefire.html"
  },
  {
    title: "RRR",
    genre: "Action &centerdot; Adventure &centerdot; Drama",
    imgSrc: "/images/vertical/rrr.jpeg",
    path: "/movies/rrr.html"
  },
  {
    title: "Mirzapur",
    genre: "Action &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/mirzapur.jpg",
    path: "/web-series/mirzapur.html"
  },
  {
    title: "Secret Invasion",
    genre: "Action &centerdot; Sci-fi &centerdot; Drama &centerdot; Mystery",
    imgSrc: "/images/vertical/secret-invasion.jpeg",
    path: "/web-series/secret-invasion.html"
  },
  {
    title: "Vikram Vedha",
    genre: "Action &centerdot; Drama &centerdot; Crime",
    imgSrc: "/images/vertical/vikram-vedha.jpeg",
    path: "/movies/vikram-vedha.html"
  },
  {
    title: "Gangubhai Kathiawadi",
    genre: "Biography &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/gangubhai-khathiawadi.jpeg",
    path: "/movies/gangubhai-khathiawadi.html"
  },
  {
    title: "Death Note",
    genre: "Animation &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/death-note.jpeg",
    path: "/anime/death-note.html"
  },
  {
    title: "Animal",
    genre: "Action &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/animal.jpg",
    path: "/movies/animal.html"
  },
  {
    title: "Leo",
    genre: "Biography &centerdot; History &centerdot; Drama",
    imgSrc: "/images/vertical/leo.jpeg",
    path: "/movies/leo.html"
  },
  {
    title: "Karthikeya 2",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy",
    imgSrc: "/images/vertical/karthikeya-2.jpg",
    path: "/movies/karthikeya-2.html"
  },
  {
    title: "Peacemaker",
    genre: "Action &centerdot; Adventure &centerdot; Comedy",
    imgSrc: "/images/vertical/peacemaker.jpeg",
    path: "/web-series/peacemaker.html"
  },
  {
    title: "My Hero Academia: Season 2",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/my-hero-academia-s4.jpeg",
    path: "/anime/my-hero-academia-s4.html"
  },
  {
    title: "Black Clover",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/black-clover.jpeg",
    path: "/anime/black-clover.html"
  },
  {
    title: "Guntur Karam",
    genre: "Action &centerdot; Drama",
    imgSrc: "/images/vertical/guntur-karam.jpg",
    path: "/movies/guntur-karam.html"
  },
  {
    title: "Wednesday",
    genre: "Comedy &centerdot; Crime &centerdot; Fantasy",
    imgSrc: "/images/vertical/wednesday.jpg",
    path: "/web-series/wednesday.html"
  }
];

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
function renderPopularSlides() {
  const selectedSlides = getRandomPopularSlides(popularSlidesData, 8);
  const swiperWrapper = document.getElementById("popular-slides");
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
}

// Initialize the slider
document.addEventListener("DOMContentLoaded", () => {
  renderPopularSlides();
});
