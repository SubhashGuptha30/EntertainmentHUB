document.addEventListener("DOMContentLoaded", function () {
  // Show the preloader
  document.getElementById("preloader").style.display = "block";

  // Simulate content loading (replace this with your actual content loading logic)
  setTimeout(function () {
    // Hide the preloader
    document.getElementById("preloader").style.display = "none";
    // Show the main content
    document.getElementById("main-content").style.display = "block";
  }, 1000);
});

//search
const searchKeywords = [
  {
    name: "Avengers: Endgame",
    path: "/movies/avengers-endgame.html"
  },
  {
    name: "One Piece",
    path: "/anime/one-piece.html"
  },
  {
    name: "The Boys",
    path: "/web-series/the-boys.html"
  },
  {
    name: "Godzilla x Kong: The New Empire",
    path: "/movies/godzilla-x-kong-the-new-empire.html"
  },
  {
    name: "Your Lie in April",
    path: "/anime/your-lie-in-april.html"
  },
  {
    name: "Squid Game",
    path: "/web-series/squid-game.html"
  },
  {
    name: "Zack Snyder Justice League",
    path: "/movies/zack-snyder-justice-league.html"
  },
  {
    name: "Weathering With You",
    path: "/anime/weathering-with-you.html"
  },
  {
    name: "Your Name",
    path: "/anime/your-name.html"
  },
  {
    name: "Bheemla Nayak",
    path: "/movies/bheemla-nayak.html"
  },
  {
    name: "Vikram Hitlist",
    path: "/movies/vikram-hitlist.html"
  },
  {
    name: "The Marvels",
    path: "/movies/the-marvels.html"
  },
  {
    name: "Oppenheimer",
    path: "/movies/oppenheimer.html"
  },
  {
    name: "Avatar: The Last Airbender",
    path: "/web-series/avatar-the-last-airbender.html"
  },
  {
    name: "Dhootha",
    path: "/movies/dhootha.html"
  },
  {
    name: "Attack On Titan",
    path: "/movies/attack-on-titan.html"
  },
  {
    name: "Avengers: Infinity War",
    path: "/movies/avengers-infinity-war.html"
  },
  {
    name: "Baahubali 2: The Conclusion",
    path: "/movies/baahubali-2-the-conclusion.html"
  },
  {
    name: "One Punch Man",
    path: "/anime/one-punch-man.html"
  },
  {
    name: "Stranger Things",
    path: "/web-series/stranger-things.html"
  },
  {
    name: "A Silent Voice",
    path: "/anime/a-silent-voice.html"
  },
  {
    name: "Salaar: Part 1 - Ceasefire",
    path: "/movies/salaar-part-1-ceasefire.html"
  },
  {
    name: "RRR",
    path: "/movies/rrr.html"
  },
  {
    name: "Mirzapur",
    path: "/web-series/mirzapur.html"
  },
  {
    name: "Mirzapur",
    path: "/web-series/mirzapur.html"
  },
  {
    name: "Secret Invasion",
    path: "/web-series/secret-invasion.html"
  },
  {
    name: "Vikram Vedha",
    path: "/movies/vikram-vedha.html"
  },
  {
    name: "Gangubhai Kathiawadi",
    path: "/movies/gangubhai-khathiawadi.html"
  },
  {
    name: "Death Note",
    path: "/anime/death-note.html"
  },
  {
    name: "Animal",
    path: "/movies/animal.html"
  },
  {
    name: "Leo",
    path: "/movies/leo.html"
  },
  {
    name: "Karthikeya 2",
    path: "/movies/karthikeya-2.html"
  },
  {
    name: "Peacemaker",
    path: "/web-series/peacemaker.html"
  },
  {
    name: "My Hero Academia: Season 2",
    path: "/anime/my-hero-academia-s4.html"
  },
  {
    name: "Black Clover",
    path: "/anime/black-clover.html"
  },
  {
    name: "Guntur Karam",
    path: "/movies/guntur-karam.html"
  },
  {
    name: "Wednesday",
    path: "/web-series/wednesday.html"
  },
  {
    name: "Hanu-man",
    path: "/movies/hanu-man.html"
  },
  {
    name: "Kung Fu Panda 4",
    path: "/movies/kung-fu-panda-4.html"
  },
  {
    name: "Wind Breaker",
    path: "/anime/wind-breaker.html"
  },
  {
    name: "3 Body Problem",
    path: "/web-series/3-body-problem.html"
  },
  {
    name: "Solo Leveling",
    path: "/anime/solo-leveling.html"
  },
  {
    name: "Tillu Square",
    path: "/movies/tillu-square.html"
  },
  {
    name: "Ninja Kamui",
    path: "/anime/ninja-kamui.html"
  },
  {
    name: "The GOAT Life",
    path: "/movies/the-goat-life.html"
  },
  {
    name: "Fast X",
    path: "/movies/fast-x.html"
  },
  {
    name: "Rocky Aur Rani Kii Prem Kahaani",
    path: "/movies/rocky-aur-rani-kii-prem-kahani.html"
  },
  {
    name: "Demon Slayer",
    path: "/anime/demon-slayer.html"
  },
  {
    name: "Kaiju No.8",
    path: "/anime/kaiju-no-8.html"
  },
  {
    name: "Fighter",
    path: "/movies/fighter.html"
  },
  {
    name: "Captain Miller",
    path: "/movies/captain-miller.html"
  },
  {
    name: "Bhagavanth Kesari",
    path: "/movies/bhagavanth-kesari.html"
  },
  {
    name: "Eagle",
    path: "/movies/eagle.html"
  },
  {
    name: "Samajavaragamana",
    path: "/movies/samajavaragamana.html"
  },
  {
    name: "Om Bheem Bush",
    path: "/movies/om-bheem-bush.html"
  },
  {
    name: "The Last of Us",
    path: "/web-series/the-last-of-us.html"
  },
  {
    name: "Avatar: The Last Airbender",
    path: "/web-series/avatar-the-last-airbender.html"
  },
  {
    name: "Extraction 2",
    path: "/movies/extraction-2.html"
  },
  {
    name: "Shogun",
    path: "/anime/shogun.html"
  },
  {
    name: "Classroom of the Elite",
    path: "/anime/classroom-of-the-elite.html"
  },
  {
    name: "Dune Part Two",
    path: "/movies/dune-part-two.html"
  },
  {
    name: "Game of Thrones: House of the Dragon",
    path: "/web-series/house-of-the-dragon.html"
  },
  {
    name: "Fifty Shades of Grey",
    path: "/movies/fifty-shades-of-grey.html"
  },
  {
    name: "Kantara",
    path: "/movies/kantara.html"
  },
  {
    name: "Spirited Away",
    path: "/anime/spirited-away.html"
  },
  {
    name: "The Shawshank Redemption",
    path: "/movies/the-shawshank-redemption.html"
  },
  {
    name: "Fullmetal Alchemist: Brotherhood",
    path: "/anime/fullmetal-alchemist-brotherhood.html"
  },
  {
    name: "Breaking Bad",
    path: "/web-series/breaking-bad.html"
  },
  {
    name: "The Godfather",
    path: "/movies/the-godfather.html"
  },
  {
    name: "Naruto: Shippuden",
    path: "/anime/naruto-shippuden.html"
  },
  {
    name: "Gangs of Wasseypur",
    path: "/movies/gangs-of-wasseypur.html"
  },
  {
    name: "I Want to Eat Your Pancreas",
    path: "/anime/i-want-to-eat-your-pancreas.html"
  },
  {
    name: "Brahmastra Part One: Shiva",
    path: "/movies/brahmastra-part-one-shiva.html"
  },
  {
    name: "Spider-man: No Way Home",
    path: "/movies/spider-man-no-way-home.html"
  },
  {
    name: "Jujutsu Kaisen 0",
    path: "/anime/jujutsu-kaisen-0.html"
  },
  {
    name: "The Witcher: Season 3",
    path: "/web-series/the-witcher-season-3.html"
  },
  {
    name: "Pushpa 2",
    path: "/movies/pushpa-2.html"
  },
  {
    name: "Kingdom of the Planet of the Apes",
    path: "/movies/kingdom-of-the-planet-of-the-apes.html"
  },
  {
    name: "Deadpool and Wolverine",
    path: "/movies/deadpool-and-wolverine.html"
  },
  {
    name: "Furiosa: A Mad Max Saga",
    path: "/movies/furiosa-a-mad-max-saga.html"
  },
  {
    name: "Madame Web",
    path: "/movies/madame-web.html"
  }
];

// DOM elements
const searchResult = document.querySelector(".search-result");
const inputBox = document.getElementById("search-input");

let debounceTimeout;

// Event listener for the input box
inputBox.addEventListener("keyup", () => {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    let result = [];
    let input = inputBox.value.trim();
    if (input.length) {
      result = searchKeywords.filter(keyword => keyword.name.toLowerCase().includes(input.toLowerCase()));
      console.log(result);
    }
    display(result);
    if (!result.length) {
      searchResult.innerHTML = "";
    }
  }, 300); // Delay for debounce
});

// Function to display the search results
function display(result) {
  if (result.length) {
    const content = result.map(keyword => `<li tabindex="0" onclick='selectInput("${keyword.path}", "${keyword.name}")'>${keyword.name}</li>`).join("");
    searchResult.innerHTML = `<ul>${content}</ul>`;
  } else {
    searchResult.innerHTML = "";
  }
}

// Function to handle the selection of a search result
function selectInput(path, name) {
  inputBox.value = name;
  searchResult.innerHTML = "";
  window.location.href = path;
}

// Event listener for keyboard navigation
inputBox.addEventListener("keydown", (e) => {
  const items = searchResult.querySelectorAll("li");
  let index = Array.prototype.indexOf.call(items, document.activeElement);

  if (e.key === "ArrowDown") {
    index = (index + 1) % items.length;
    items[index].focus();
  } else if (e.key === "ArrowUp") {
    index = (index - 1 + items.length) % items.length;
    items[index].focus();
  } else if (e.key === "Enter" && index >= 0) {
    items[index].click();
  }
});


//swiper
var swiper = new Swiper(".popular-content, .new-content", {
  slidesPerView: 1,
  spaceBetween: 10,
  autoplay: {
    delay: 775500,
    disableOnInteraction: false,
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
  breakpoints: {
    280: {
      slidesPerView: 1,
      spaceBetween: 10,
    },
    320: {
      slidesPerView: 2,
      spaceBetween: 10,
    },
    510: {
      slidesPerView: 2,
      spaceBetween: 10,
    },
    758: {
      slidesPerView: 3,
      spaceBetween: 15,
    },
    900: {
      slidesPerView: 4,
      spaceBetween: 20,
    },
  },
});

//hswiper
var swiper = new Swiper(".head-content", {
  spaceBetween: 30,
  centeredSlides: true,
  slidesPerView: 1,
  spaceBetween: 10,
  autoplay: {
    delay: 10000,
    disableOnInteraction: false,
  },
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  rewind: true,
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
});
