const ComingSoonSlidesData = [
  {
    title: "Spider-Man: No Way Home",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy &CenterDot; Sci-fi",
    imgSrc: "/images/vertical/spiderman-no-way-home.jpg",
    path: "/movies/spiderman-no-way-home.html"
  },
  {
    title: "Jujutsu Kaisen 0",
    genre: "Action &centerdot; Fantasy &centerdot; Animation &centerdot; Comedy",
    imgSrc: "/images/vertical/jujutsu-kaisen-0.jpg",
    path: "/anime/jujutsu-kaisen-0.html"
  },
  {
    title: "The Witcher: Season 3",
    genre: "Drama &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/the-witcher-season-3.jpeg",
    path: "/web-series/the-witcher-season-3.html"
  },
  {
    title: "Pushpa 2",
    genre: "Drama &centerdot; Action &centerdot; Crime",
    imgSrc: "/images/vertical/pushpa-2.jpeg",
    path: "/movies/pushpa-2.html"
  },
  {
    title: "Kingdom of the Planet of the Apes",
    genre: "Action &centerdot; Sci-fi &centerdot; Adventure",
    imgSrc: "/images/vertical/kingdom-of-the-planet-of-the-apes.jpg",
    path: "/movies/kingdom-of-the-planet-of-the-apes.html"
  },
  {
    title: "Deadpool & Wolverine",
    genre: "Action &centerdot; Comedy &centerdot; Sci-fi",
    imgSrc: "/images/vertical/deadpool-and-wolverine.jpg",
    path: "/movies/deadpool-and-wolverine.html"
  },
  {
    title: "Furiosa: A Mad Max Saga",
    genre: "Adventure &centerdot; Action &centerdot; Sci-fi",
    imgSrc: "/images/vertical/furiosa-a-mad-max-saga.jpeg",
    path: "/movies/furiosa-a-mad-max-saga.html"
  },
  {
    title: "Madame Web",
    genre: "Adventure &centerdot; Action &centerdot; Sci-fi",
    imgSrc: "/images/vertical/madame-web.jpg",
    path: "/movies/madame-web.html"
  },
  {
    title: "Secret Invasion",
    genre: "Action &centerdot; Sci-fi &centerdot; Drama &centerdot; Mystery",
    imgSrc: "/images/vertical/cs-9.jpeg",
    path: "/web-series/secret-invasion.html"
  },
  {
    title: "Vikram Vedha",
    genre: "Action &centerdot; Drama &centerdot; Crime",
    imgSrc: "/images/vertical/cs-10.jpeg",
    path: "/movies/vikram-vedha.html"
  },
  {
    title: "Gangubhai Kathiawadi",
    genre: "Biography &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/cs-11.jpeg",
    path: "/movies/gangubhai-khathiawadi.html"
  },
  {
    title: "Death Note",
    genre: "Animation &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/cs-12.jpeg",
    path: "/anime/death-note.html"
  },
  {
    title: "Animal",
    genre: "Action &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/cs-13.jpg",
    path: "/movies/animal.html"
  },
  {
    title: "Leo",
    genre: "Biography &centerdot; History &centerdot; Drama",
    imgSrc: "/images/vertical/cs-14.jpeg",
    path: "/movies/Leo.html"
  },
  {
    title: "Karthikeya 2",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy",
    imgSrc: "/images/vertical/cs-15.jpg",
    path: "/movies/Karthikeya-2.html"
  },
  {
    title: "Peacemaker",
    genre: "Action &centerdot; Adventure &centerdot; Comedy",
    imgSrc: "/images/vertical/cs-16.jpeg",
    path: "/web-series/peacemaker.html"
  },
  {
    title: "My Hero Academia: Season 2",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/cs-17.jpeg",
    path: "/anime/my-hero-academia-s4.html"
  },
  {
    title: "Black Clover",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/cs-18.jpeg",
    path: "/anime/black-clover.html"
  },
  {
    title: "Guntur Karam",
    genre: "Action &centerdot; Drama",
    imgSrc: "/images/vertical/cs-19.jpg",
    path: "/movies/guntur-karam.html"
  },
  {
    title: "Wednesday",
    genre: "Comedy &centerdot; Crime &centerdot; Fantasy",
    imgSrc: "/images/vertical/cs-20.jpg",
    path: "/web-series/wednesday.html"
  }
];

// Function to shuffle array and select n random elements
function getRandomComingSoonSlides(arr, n) {
  const shuffled = arr.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

// Function to generate slide HTML
function generateComingSoonSlideHTML(slide) {
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
function renderComingSoonSlides() {
  const selectedSlides = getRandomComingSoonSlides(ComingSoonSlidesData, 8);
  const swiperWrapper = document.getElementById("coming-soon-slides");
  swiperWrapper.innerHTML = selectedSlides.map(generateComingSoonSlideHTML).join("");
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
  renderComingSoonSlides();
});
