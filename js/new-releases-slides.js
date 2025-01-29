const newSlidesData = [
  {
    title: "Hanu-man",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy",
    imgSrc: "/images/vertical/hanu-man.jpeg",
    path: "/movies/hanu-man.html"
  },
  {
    title: "Kung Fu Panda 4",
    genre: "Action &centerdot; Drama Animation &centerdot; Comedy",
    imgSrc: "/images/vertical/kung-fu-panda-4.jpeg",
    path: "/movies/kung-fu-panda-4.html"
  },
  {
    title: "Wind Breaker",
    genre: "Animation &centerdot Action &centerdot; Adventure",
    imgSrc: "/images/vertical/wind-breaker.jpeg",
    path: "/anime/wind-breaker.html"
  },
  {
    title: "3 Body Problem",
    genre: "Drama &centerdot; Fantasy &centerdot; Sci-fi &centerdot; Thriller",
    imgSrc: "/images/vertical/3-body-problem.jpg",
    path: "/web-series/3-body-problem.html"
  },
  {
    title: "Solo Leveling",
    genre: "Animation &centerdot; Action &centerdot Fantasy",
    imgSrc: "/images/vertical/solo-leveling.jpg",
    path: "/anime/solo-leveling.html"
  },
  {
    title: "Tillu Square",
    genre: "Comedy &centerdot; Drama &centerdot; Crime",
    imgSrc: "/images/vertical/tillu-square.jpeg",
    path: "/movies/tillu-square.html"
  },
  {
    title: "Ninja Kamui",
    genre: "Animation &centerdot; Action &centerdot; Drama",
    imgSrc: "/images/vertical/ninja-kamui.jpg",
    path: "/anime/ninja-kamui.html"
  },
  {
    title: "The GOAT Life",
    genre: "Adventure &centerdot; Drama",
    imgSrc: "/images/vertical/the-goat-life.jpg",
    path: "/movies/the-goat-life.html"
  },
  {
    title: "Fast X",
    genre: "Action &centerdot; Adventure &centerdot; Crime",
    imgSrc: "/images/vertical/fast-x.jpg",
    path: "/movies/fast-x.html"
  },
  {
    title: "Rocky Aur Rani Kii Prem Kahaani",
    genre: "Comedy &centerdot; Drama &centerdot; Family &centerdot Romance",
    imgSrc: "/images/vertical/rocky-aur-rani-kii-prem-kahani.jpg",
    path: "/movies/rocky-aur-rani-kii-prem-kahani.html"
  },
  {
    title: "Demon Slayer",
    genre: "Animation &centerdot Action &centerdot; Adventure &centerdot; Fantasy",
    imgSrc: "/images/vertical/demon-slayer.jpg",
    path: "/anime/demon-slayer.html"
  },
  {
    title: "Kaiju No.8",
    genre: "Animation &centerdot; Action &centerdot; Horror &centerdot; Fantasy",
    imgSrc: "/images/vertical/kaiju-no-8.jpeg",
    path: "/anime/kaiju-no-8.html"
  },
  {
    title: "Fighter",
    genre: "Action &centerdot; Thriller",
    imgSrc: "/images/vertical/fighter.jpg",
    path: "/movies/fighter.html"
  },
  {
    title: "Captain Miller",
    genre: "Action &centerdot; Adventure &centerdot; Drama",
    imgSrc: "/images/vertical/captain-miller.jpeg",
    path: "/movies/captain-miller.html"
  },
  {
    title: "Bhagavanth Kesari",
    genre: "Action &centerdot; Thriller &centerdot; Drama",
    imgSrc: "/images/vertical/bhagavanth-kesari.jpg",
    path: "/movies/bhagavanth-kesari.html"
  },
  {
    title: "Eagle",
    genre: "Action &centerdot; Thriller",
    imgSrc: "/images/vertical/eagle.jpg",
    path: "/movies/eagle.html"
  },
  {
    title: "Samajavaragamana",
    genre: "Comedy &centerdot; Family &centerdot; Drama",
    imgSrc: "/images/vertical/samajavaragamana.jpg",
    path: "/movies/samajavaragamana.html"
  },
  {
    title: "Om Bheem Bush",
    genre: "Comedy",
    imgSrc: "/images/vertical/om-bheem-bush.jpg",
    path: "/movies/om-bheem-bush.html"
  },
  {
    title: "The Last of Us",
    genre: "Action &centerdot; Adventure &centerdot; Drama",
    imgSrc: "/images/vertical/the-last-of-us.jpg",
    path: "/web-series/the-last-of-us.html"
  },
  {
    title: "Avatar: The Last Airbender",
    genre: "Action &centerdot; Adventure &centerdot; Comedy",
    imgSrc: "/images/vertical/avatar-the-last-airbender.jpeg",
    path: "/web-series/avatar-the-last-airbender.html"
  }
];

// Function to shuffle array and select n random elements
function getRandomnewSlides(arr, n) {
  const shuffled = arr.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

// Function to generate slide HTML
function generatenewSlideHTML(slide) {
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
function rendernewSlides() {
  const selectedSlides = getRandomnewSlides(newSlidesData, 9);
  const swiperWrapper = document.getElementById("new-slides");
  swiperWrapper.innerHTML = selectedSlides.map(generatenewSlideHTML).join("");
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
  rendernewSlides();
});
