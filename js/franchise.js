const franchiseCards = [
  {
    title: "MCU",
    imgSrc: "mcu.jpeg",
    description: "The Marvel Cinematic Universe is a media franchise and shared universe centered on a series of superhero films.",
  },
  {
    title: "DCEU",
    imgSrc: "dceu.jpeg",
    description: "The DC Extended Universe is an American media franchise and shared universe centered on superhero films.",
  },
  {
    title: "Pokemon",
    imgSrc: "pokemon.png",
    description: "Pokemon is a Japanese media franchise managed by The Pokemon Company, centered on fictional creatures called 'Pokemon'.",
  },
  {
    title: "One Piece",
    imgSrc: "onepiece.jpeg",
    description: "One Piece is a Japanese manga series written and illustrated by Eiichiro Oda, featuring the adventures of Monkey D. Luffy.",
  },
  {
    title: "Arrowverse",
    imgSrc: "arrowverse.png",
    description: "The Arrowverse is an American media franchise and shared universe centered on various interconnected television series.",
  },
  {
    title: "Breaking Bad",
    imgSrc: "breakingbad.jpg",
    description: "Breaking Bad is an American neo-Western crime drama television series created and produced by Vince Gilligan.",
  },
  {
    title: "Star Wars",
    imgSrc: "starwars.jpeg",
    description: "Star Wars is a space opera media franchise created by George Lucas, centered on a series of films and extended universe.",
  },
  {
    title: "Harry Potter",
    imgSrc: "harrypotter.jpeg",
    description: "Harry Potter is a British-American film series based on the eponymous novels by J.K. Rowling.",
  },
  {
    title: "Lord of the Rings",
    imgSrc: "lotr.png",
    description: "The Lord of the Rings is an epic high-fantasy novel series by J.R.R. Tolkien, adapted into an award-winning film series.",
  },
  {
    title: "Star Trek",
    imgSrc: "startrek.jpeg",
    description: "Star Trek is a science fiction media franchise that began with the 1960s TV series, followed by films, series, and more.",
  },
  {
    title: "Jurassic Park",
    imgSrc: "jurassicpark.jpg",
    description: "Jurassic Park is a media franchise centered on a disastrous attempt to create a theme park of cloned dinosaurs.",
  },
  {
    title: "Transformers",
    imgSrc: "transformers.jpeg",
    description: "Transformers is a media franchise produced by Hasbro, featuring giant robots that can transform into vehicles and other objects.",
  },
  {
    title: "Game of Thrones",
    imgSrc: "got.jpg",
    description: "Game of Thrones is a fantasy drama television series based on 'A Song of Ice and Fire' novels by George R.R. Martin.",
  },
  {
    title: "Fast & Furious",
    imgSrc: "fastandfurious.jpeg",
    description: "Fast & Furious is an American media franchise centered on a series of action films involving street racing and heists.",
  },
  {
    title: "The Simpsons",
    imgSrc: "simpsons.jpeg",
    description: "The Simpsons is an American animated sitcom created by Matt Groening, depicting the lives of the Simpson family.",
  },
  {
    title: "James Bond",
    imgSrc: "jamesbond.jpeg",
    description: "James Bond is a British spy film series based on the character created by writer Ian Fleming in 1953.",
  },
  {
    title: "Mission Impossible",
    imgSrc: "missionimpossible.jpg",
    description: "Mission Impossible is an American media franchise based on a series of action spy films starring Tom Cruise as Ethan Hunt.",
  },
  {
    title: "Indiana Jones",
    imgSrc: "indianajones.jpeg",
    description: "Indiana Jones is an American media franchise based on the adventures of Dr. Henry 'Indiana' Jones, an archaeologist.",
  },
  {
    title: "Doctor Who",
    imgSrc: "doctorwho.jpg",
    description: "Doctor Who is a British science fiction television series about the adventures of the Doctor, a Time Lord.",
  },
  {
    title: "The Witcher",
    imgSrc: "witcher.jpg",
    description: "The Witcher is a Polish-American fantasy drama series based on the book series by Andrzej Sapkowski.",
  },
  {
    title: "Naruto",
    imgSrc: "naruto.jpeg",
    description: "Naruto is a Japanese manga series written and illustrated by Masashi Kishimoto, centered on a young ninja, Naruto Uzumaki.",
  },
  {
    title: "Dragon Ball",
    imgSrc: "dragonball.jpg",
    description: "Dragon Ball is a Japanese media franchise created by Akira Toriyama, featuring the adventures of Goku and his friends.",
  },
  {
    title: "Attack on Titan",
    imgSrc: "attackontitan.png",
    description: "Attack on Titan is a Japanese manga series written and illustrated by Hajime Isayama, set in a world where humanity lives inside cities surrounded by enormous walls due to the sudden appearance of the Titans.",
  },
  {
    title: "My Hero Academia",
    imgSrc: "myheroacademia.png",
    description: "My Hero Academia is a Japanese superhero manga series written and illustrated by Kohei Horikoshi, following the adventures of Izuku Midoriya in a world where people with superpowers are commonplace.",
  },
  {
    title: "Demon Slayer",
    imgSrc: "demonslayer.jpg",
    description: "Demon Slayer is a Japanese manga series written and illustrated by Koyoharu Gotouge, following Tanjiro Kamado and his quest to avenge his family and cure his sister.",
  },
  {
    title: "Fullmetal Alchemist",
    imgSrc: "fullmetalalchemist.jpg",
    description: "Fullmetal Alchemist is a Japanese manga series written and illustrated by Hiromu Arakawa, set in a world where alchemy is one of the most advanced scientific techniques.",
  },
  {
    title: "One Punch Man",
    imgSrc: "onepunchman.jpg",
    description: "One Punch Man is a Japanese superhero franchise created by the artist ONE, following the story of Saitama, a hero who can defeat any opponent with a single punch.",
  },
  {
    title: "Bleach",
    imgSrc: "bleach.jpg",
    description: "Bleach is a Japanese manga series written and illustrated by Tite Kubo, following the adventures of Ichigo Kurosaki after he obtains the powers of a Soul Reaper.",
  },
  {
    title: "Toy Story",
    imgSrc: "toystory.jpeg",
    description: "Toy Story is a CGI animated film series produced by Pixar Animation Studios, centered on the lives of toys that come to life when humans are not around.",
  },
  {
    title: "The Incredibles",
    imgSrc: "theincredibles.jpg",
    description: "The Incredibles is a CGI animated film series produced by Pixar Animation Studios, focusing on a family of superheroes living a suburban life.",
  },
  {
    title: "Monsters, Inc.",
    imgSrc: "monstersinc.jpeg",
    description: "Monsters, Inc. is a CGI animated film series produced by Pixar Animation Studios, set in a world where monsters generate energy by scaring children.",
  },
  {
    title: "Cars",
    imgSrc: "cars.jpeg",
    description: "Cars is a CGI animated film series produced by Pixar Animation Studios, centered on anthropomorphic cars and their adventures.",
  },
  {
    title: "Kung Fu Panda",
    imgSrc: "kungfupanda.jpg",
    description: "Kung Fu Panda is a CGI animated film series produced by DreamWorks Animation, following the adventures of Po, a clumsy panda who becomes a kung fu master.",
  },
  {
    title: "Shrek",
    imgSrc: "shrek.jpeg",
    description: "Shrek is a CGI animated film series produced by DreamWorks Animation, featuring the adventures of Shrek, an ogre, and his friends.",
  },
  {
    title: "Despicable Me",
    imgSrc: "despicableme.jpeg",
    description: "Despicable Me is a CGI animated film series produced by Illumination Entertainment, centered on Gru, a supervillain, and his Minions.",
  },
  {
    title: "How to Train Your Dragon",
    imgSrc: "howtotrainyourdragon.jpeg",
    description: "How to Train Your Dragon is a CGI animated film series produced by DreamWorks Animation, focusing on the adventures of a young Viking named Hiccup and his dragon Toothless.",
  },
  {
    title: "Ice Age",
    imgSrc: "iceage.jpeg",
    description: "Ice Age is a CGI animated film series produced by Blue Sky Studios, focusing on a group of prehistoric animals surviving the Ice Age.",
  }
];

const franchiseSection = document.querySelector(".franchises-section");

franchiseCards.forEach(franchise => {
  const franchiseCard = `
    <div class="franchise-card" >
      <img src="/images/franchise/${franchise.imgSrc}" alt="${franchise.title}" class="franchise-img" />
      <h3>${franchise.title}</h3>
      <p>${franchise.description}</p>
      <button class="view-btn">View</button>
    </div >
    `;
  franchiseSection.innerHTML += franchiseCard;
});
