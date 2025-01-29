const topRatedSlidesData = [
  {
    title: "The Shawahank Redemption",
    genre: "Drama",
    imgSrc: "/images/vertical/the-shawshank-redemption.jpg",
    path: "/movies/the-shawshank-redemption.html"
  },
  {
    title: "Fullmetal Alchemist: Brotherhood",
    genre: "Action &centerdot; Animation &centerdot; Adventure",
    imgSrc: "/images/vertical/fullmetal-alchemist-brotherhood.jpeg",
    path: "/anime/fullmetal-alchemist-brotherhood.html"
  },
  {
    title: "Breaking Bad",
    genre: "Crime &centerdot; Drama &centerdot; Thriller",
    imgSrc: "/images/vertical/breaking-bad.jpg",
    path: "/web-series/breaking-bad.html"
  },
  {
    title: "The Godfather",
    genre: "Drama &centerdot; Crime",
    imgSrc: "/images/vertical/the-godfather.jpg",
    path: "/movies/the-godfather.html"
  },
  {
    title: "Naruto: Shippuden",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/naruto-shippuden.jpg",
    path: "/anime/naruto-shippuden.html"
  },
  {
    title: "Gangs of Wasseypur",
    genre: "Action &centerdot; Crime &centerdot; Drama &centerdot; Comedy &CenterDot; Thriller",
    imgSrc: "/images/vertical/gangs-of-wasseypur.jpg",
    path: "/movies/gangs-of-wasseypur.html"
  },
  {
    title: "I Want to Eat Your Pancreas",
    genre: "Animation &centerdot; Drama &centerdot; Family",
    imgSrc: "/images/vertical/i-want-to-eat-your-pancreas.jpg",
    path: "/movies/i-want-to-eat-your-pancreas.html"
  },
  {
    title: "Brahmāstra Part One: Shiva",
    genre: "Adventure &centerdot; Action &centerdot; Fantasy",
    imgSrc: "/images/vertical/brahmastra-part-one-shiva.jpg",
    path: "/movies/brahmastra-part-one-shiva.html"
  },
  {
    title: "Secret Invasion",
    genre: "Action &centerdot; Sci-fi &centerdot; Drama &centerdot; Mystery",
    imgSrc: "/images/vertical/tr-9.jpeg",
    path: "/web-series/secret-invasion.html"
  },
  {
    title: "Vikram Vedha",
    genre: "Action &centerdot; Drama &centerdot; Crime",
    imgSrc: "/images/vertical/tr-10.jpeg",
    path: "/movies/vikram-vedha.html"
  },
  {
    title: "Gangubhai Kathiawadi",
    genre: "Biography &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/tr-11.jpeg",
    path: "/movies/gangubhai-khathiawadi.html"
  },
  {
    title: "Death Note",
    genre: "Animation &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/tr-12.jpeg",
    path: "/anime/death-note.html"
  },
  {
    title: "Animal",
    genre: "Action &centerdot; Crime &centerdot; Drama",
    imgSrc: "/images/vertical/tr-13.jpg",
    path: "/movies/animal.html"
  },
  {
    title: "Leo",
    genre: "Biography &centerdot; History &centerdot; Drama",
    imgSrc: "/images/vertical/tr-14.jpeg",
    path: "/movies/Leo.html"
  },
  {
    title: "Karthikeya 2",
    genre: "Action &centerdot; Adventure &centerdot; Fantasy",
    imgSrc: "/images/vertical/tr-15.jpg",
    path: "/movies/Karthikeya-2.html"
  },
  {
    title: "Peacemaker",
    genre: "Action &centerdot; Adventure &centerdot; Comedy",
    imgSrc: "/images/vertical/tr-16.jpeg",
    path: "/web-series/peacemaker.html"
  },
  {
    title: "My Hero Academia: Season 2",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/tr-17.jpeg",
    path: "/anime/my-hero-academia-s4.html"
  },
  {
    title: "Black Clover",
    genre: "Animation &centerdot; Action &centerdot; Adventure",
    imgSrc: "/images/vertical/tr-18.jpeg",
    path: "/anime/black-clover.html"
  },
  {
    title: "Guntur Karam",
    genre: "Action &centerdot; Drama",
    imgSrc: "/images/vertical/tr-19.jpg",
    path: "/movies/guntur-karam.html"
  },
  {
    title: "Wednesday",
    genre: "Comedy &centerdot; Crime &centerdot; Fantasy",
    imgSrc: "/images/vertical/tr-20.jpg",
    path: "/web-series/wednesday.html"
  }
];

// Function to shuffle array and select n random elements
function getRandomTopRatedSlides(arr, n) {
  const shuffled = arr.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

// Function to generate slide HTML
function generateTopRatedSlideHTML(slide) {
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
function renderTopRatedSlides() {
  const selectedSlides = getRandomTopRatedSlides(topRatedSlidesData, 8);
  const swiperWrapper = document.getElementById("top-rated-slides");
  swiperWrapper.innerHTML = selectedSlides.map(generateTopRatedSlideHTML).join("");
  const viewMoreSlide = `
  <div class="swiper-slide">
    <div class="view-more-box" title="View More">
      <a href="all-top-rated.html" class="view-more-btn">
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
  renderTopRatedSlides();
});
