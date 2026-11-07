"""
Curated franchise / watch-order data for scripts/seed_franchises.py.

Sources cross-checked (Nov 2026): official release dates (IMDb), franchisefever.com
timelines, r/fatestaynight "Official Viewing Order Guide v2", r/araragi wiki (Monogatari
novel order), r/anime watch-order threads, MyAnimeList watch-order stacks.

Format
  F(slug, title, kind, status, description, entries, chrono=[...])
  E(type, title, year, minutes, **opts)
    type     movies | animes | webSeries
    minutes  runtime of THIS entry (a season, a film)
    opts     label, phase, canon, essential, note, format ('film' for anime films),
             seasons, tags, desc, language, ongoing (title still airing)
  chrono     in-universe order as a list of "Title" or "Title|Label"; omitted = release order.
Entry order inside `entries` is release order.
"""


def E(type, title, year, minutes, **opts):
    return {'type': type, 'title': title, 'year': year, 'minutes': minutes, **opts}


def F(slug, title, kind, status, description, entries, chrono=None):
    return {'slug': slug, 'title': title, 'kind': kind, 'status': status,
            'description': description, 'entries': entries, 'chrono': chrono}


M, A, S = 'movies', 'animes', 'webSeries'

FRANCHISES = [
    # ── Universes ─────────────────────────────────────────────────────────
    F('marvel-cinematic-universe', 'Marvel Cinematic Universe', 'universe', 'ongoing',
      'Since Iron Man in 2008, Marvel Studios has built one connected story across films and '
      'Disney+ series: the Infinity Saga (Phases 1–3) and the Multiverse Saga (Phases 4–6).', [
        E(M, 'Iron Man', 2008, 126, phase='Phase One', tags=['Action', 'Sci-Fi']),
        E(M, 'The Incredible Hulk', 2008, 112, phase='Phase One', essential=False,
          note='Skippable: only General Ross carries forward.'),
        E(M, 'Iron Man 2', 2010, 124, phase='Phase One'),
        E(M, 'Thor', 2011, 115, phase='Phase One'),
        E(M, 'Captain America: The First Avenger', 2011, 124, phase='Phase One'),
        E(M, 'The Avengers', 2012, 143, phase='Phase One'),
        E(M, 'Iron Man 3', 2013, 130, phase='Phase Two'),
        E(M, 'Thor: The Dark World', 2013, 112, phase='Phase Two', essential=False,
          note='Introduces the Aether (Reality Stone); the rest is skippable.'),
        E(M, 'Captain America: The Winter Soldier', 2014, 136, phase='Phase Two'),
        E(M, 'Guardians of the Galaxy', 2014, 121, phase='Phase Two'),
        E(M, 'Avengers: Age of Ultron', 2015, 141, phase='Phase Two'),
        E(M, 'Ant-Man', 2015, 117, phase='Phase Two'),
        E(M, 'Captain America: Civil War', 2016, 147, phase='Phase Three'),
        E(M, 'Doctor Strange', 2016, 115, phase='Phase Three'),
        E(M, 'Guardians of the Galaxy Vol. 2', 2017, 136, phase='Phase Three'),
        E(M, 'Spider-Man: Homecoming', 2017, 133, phase='Phase Three'),
        E(M, 'Thor: Ragnarok', 2017, 130, phase='Phase Three'),
        E(M, 'Black Panther', 2018, 134, phase='Phase Three'),
        E(M, 'Avengers: Infinity War', 2018, 149, phase='Phase Three'),
        E(M, 'Ant-Man and the Wasp', 2018, 118, phase='Phase Three'),
        E(M, 'Captain Marvel', 2019, 123, phase='Phase Three'),
        E(M, 'Avengers: Endgame', 2019, 181, phase='Phase Three'),
        E(M, 'Spider-Man: Far From Home', 2019, 129, phase='Phase Three'),
        E(S, 'WandaVision', 2021, 350, phase='Phase Four', seasons=1),
        E(S, 'The Falcon and the Winter Soldier', 2021, 300, phase='Phase Four', seasons=1),
        E(S, 'Loki', 2021, 300, label='Season 1', phase='Phase Four'),
        E(M, 'Black Widow', 2021, 134, phase='Phase Four',
          note='Set between Civil War and Infinity War.'),
        E(M, 'Shang-Chi and the Legend of the Ten Rings', 2021, 132, phase='Phase Four'),
        E(M, 'Eternals', 2021, 156, phase='Phase Four', essential=False),
        E(S, 'Hawkeye', 2021, 300, phase='Phase Four', seasons=1),
        E(M, 'Spider-Man: No Way Home', 2021, 148, phase='Phase Four'),
        E(S, 'Moon Knight', 2022, 290, phase='Phase Four', seasons=1, essential=False),
        E(M, 'Doctor Strange in the Multiverse of Madness', 2022, 126, phase='Phase Four',
          note='Watch WandaVision first.'),
        E(S, 'Ms. Marvel', 2022, 280, phase='Phase Four', seasons=1, essential=False,
          note='Sets up The Marvels.'),
        E(M, 'Thor: Love and Thunder', 2022, 119, phase='Phase Four', essential=False),
        E(M, 'Black Panther: Wakanda Forever', 2022, 161, phase='Phase Four'),
        E(M, 'Ant-Man and the Wasp: Quantumania', 2023, 125, phase='Phase Five'),
        E(M, 'Guardians of the Galaxy Vol. 3', 2023, 150, phase='Phase Five'),
        E(S, 'Loki', 2023, 320, label='Season 2', phase='Phase Five'),
        E(M, 'The Marvels', 2023, 105, phase='Phase Five', essential=False),
        E(M, 'Deadpool & Wolverine', 2024, 128, phase='Phase Five'),
        E(S, 'Agatha All Along', 2024, 330, phase='Phase Five', seasons=1, essential=False),
        E(M, 'Captain America: Brave New World', 2025, 118, phase='Phase Five'),
        E(M, 'Thunderbolts*', 2025, 127, phase='Phase Five'),
        E(M, 'The Fantastic Four: First Steps', 2025, 115, phase='Phase Six',
          note='Set on Earth-828, a separate universe.'),
      ], chrono=[
        'Captain America: The First Avenger', 'Captain Marvel', 'Iron Man', 'Iron Man 2',
        'The Incredible Hulk', 'Thor', 'The Avengers', 'Thor: The Dark World', 'Iron Man 3',
        'Captain America: The Winter Soldier', 'Guardians of the Galaxy',
        'Guardians of the Galaxy Vol. 2', 'Avengers: Age of Ultron', 'Ant-Man',
        'Captain America: Civil War', 'Black Widow', 'Black Panther', 'Spider-Man: Homecoming',
        'Doctor Strange', 'Thor: Ragnarok', 'Ant-Man and the Wasp', 'Avengers: Infinity War',
        'Avengers: Endgame', 'Loki|Season 1', 'WandaVision', 'The Falcon and the Winter Soldier',
        'Spider-Man: Far From Home', 'Shang-Chi and the Legend of the Ten Rings', 'Eternals',
        'Hawkeye', 'Spider-Man: No Way Home', 'Doctor Strange in the Multiverse of Madness',
        'Moon Knight', 'Thor: Love and Thunder', 'Black Panther: Wakanda Forever', 'Ms. Marvel',
        'Ant-Man and the Wasp: Quantumania', 'Guardians of the Galaxy Vol. 3', 'The Marvels',
        'Loki|Season 2', 'Deadpool & Wolverine', 'Agatha All Along',
        'Captain America: Brave New World', 'Thunderbolts*', 'The Fantastic Four: First Steps',
      ]),

    F('star-wars', 'Star Wars', 'universe', 'ongoing',
      'A long time ago in a galaxy far, far away: the nine-episode Skywalker saga plus the '
      'anthology films and live-action and animated series that fill the gaps between them.', [
        E(M, 'Star Wars: Episode IV – A New Hope', 1977, 121, phase='Original Trilogy', tags=['Sci-Fi', 'Adventure']),
        E(M, 'Star Wars: Episode V – The Empire Strikes Back', 1980, 124, phase='Original Trilogy'),
        E(M, 'Star Wars: Episode VI – Return of the Jedi', 1983, 131, phase='Original Trilogy'),
        E(M, 'Star Wars: Episode I – The Phantom Menace', 1999, 136, phase='Prequel Trilogy'),
        E(M, 'Star Wars: Episode II – Attack of the Clones', 2002, 142, phase='Prequel Trilogy'),
        E(M, 'Star Wars: Episode III – Revenge of the Sith', 2005, 140, phase='Prequel Trilogy'),
        E(A, 'Star Wars: The Clone Wars', 2008, 2930, phase='Prequel Trilogy', seasons=7,
          tags=['Animation', 'Sci-Fi'], note='Animated; set between Episodes II and III. Fans rate it essential.'),
        E(M, 'Star Wars: Episode VII – The Force Awakens', 2015, 138, phase='Sequel Trilogy'),
        E(M, 'Rogue One: A Star Wars Story', 2016, 133, phase='Sequel Trilogy',
          note='Leads directly into A New Hope.'),
        E(M, 'Star Wars: Episode VIII – The Last Jedi', 2017, 152, phase='Sequel Trilogy'),
        E(M, 'Solo: A Star Wars Story', 2018, 135, phase='Sequel Trilogy', essential=False),
        E(S, 'The Mandalorian', 2019, 300, label='Season 1', phase='Disney+ era'),
        E(M, 'Star Wars: Episode IX – The Rise of Skywalker', 2019, 142, phase='Sequel Trilogy'),
        E(S, 'The Mandalorian', 2020, 320, label='Season 2', phase='Disney+ era'),
        E(S, 'The Book of Boba Fett', 2021, 290, phase='Disney+ era', seasons=1,
          note='Episodes 5–6 continue The Mandalorian; watch before its Season 3.'),
        E(S, 'Obi-Wan Kenobi', 2022, 270, phase='Disney+ era', seasons=1),
        E(S, 'Andor', 2022, 560, label='Season 1', phase='Disney+ era'),
        E(S, 'The Mandalorian', 2023, 340, label='Season 3', phase='Disney+ era'),
        E(S, 'Ahsoka', 2023, 360, label='Season 1', phase='Disney+ era',
          note='Continues the animated Star Wars Rebels.'),
        E(S, 'Andor', 2025, 560, label='Season 2', phase='Disney+ era'),
      ], chrono=[
        'Star Wars: Episode I – The Phantom Menace', 'Star Wars: Episode II – Attack of the Clones',
        'Star Wars: The Clone Wars', 'Star Wars: Episode III – Revenge of the Sith',
        'Solo: A Star Wars Story', 'Obi-Wan Kenobi', 'Andor|Season 1', 'Andor|Season 2',
        'Rogue One: A Star Wars Story', 'Star Wars: Episode IV – A New Hope',
        'Star Wars: Episode V – The Empire Strikes Back', 'Star Wars: Episode VI – Return of the Jedi',
        'The Mandalorian|Season 1', 'The Mandalorian|Season 2', 'The Book of Boba Fett',
        'The Mandalorian|Season 3', 'Ahsoka|Season 1',
        'Star Wars: Episode VII – The Force Awakens', 'Star Wars: Episode VIII – The Last Jedi',
        'Star Wars: Episode IX – The Rise of Skywalker',
      ]),

    F('middle-earth', 'Middle-earth', 'universe', 'ongoing',
      "J.R.R. Tolkien's world on screen: Peter Jackson's two trilogies, the anime prequel "
      'The War of the Rohirrim, and the Second Age series The Rings of Power.', [
        E(M, 'The Lord of the Rings: The Fellowship of the Ring', 2001, 178, phase='The Lord of the Rings',
          tags=['Fantasy', 'Adventure'], note='Extended edition: 228 min.'),
        E(M, 'The Lord of the Rings: The Two Towers', 2002, 179, phase='The Lord of the Rings'),
        E(M, 'The Lord of the Rings: The Return of the King', 2003, 201, phase='The Lord of the Rings'),
        E(M, 'The Hobbit: An Unexpected Journey', 2012, 169, phase='The Hobbit'),
        E(M, 'The Hobbit: The Desolation of Smaug', 2013, 161, phase='The Hobbit'),
        E(M, 'The Hobbit: The Battle of the Five Armies', 2014, 144, phase='The Hobbit'),
        E(S, 'The Lord of the Rings: The Rings of Power', 2022, 560, label='Season 1', phase='Second Age',
          essential=False, note='Thousands of years before The Hobbit; no knowledge needed.'),
        E(S, 'The Lord of the Rings: The Rings of Power', 2024, 520, label='Season 2', phase='Second Age',
          essential=False),
        E(A, 'The Lord of the Rings: The War of the Rohirrim', 2024, 134, phase='Third Age', format='film',
          essential=False, note='Anime film set 183 years before The Hobbit.'),
      ], chrono=[
        'The Lord of the Rings: The Rings of Power|Season 1', 'The Lord of the Rings: The Rings of Power|Season 2',
        'The Lord of the Rings: The War of the Rohirrim', 'The Hobbit: An Unexpected Journey',
        'The Hobbit: The Desolation of Smaug', 'The Hobbit: The Battle of the Five Armies',
        'The Lord of the Rings: The Fellowship of the Ring', 'The Lord of the Rings: The Two Towers',
        'The Lord of the Rings: The Return of the King',
      ]),

    F('wizarding-world', 'Wizarding World', 'universe', 'ongoing',
      "Harry Potter's eight films and the Fantastic Beasts prequels, set seventy years earlier.", [
        E(M, "Harry Potter and the Philosopher's Stone", 2001, 152, phase='Harry Potter', tags=['Fantasy']),
        E(M, 'Harry Potter and the Chamber of Secrets', 2002, 161, phase='Harry Potter'),
        E(M, 'Harry Potter and the Prisoner of Azkaban', 2004, 142, phase='Harry Potter'),
        E(M, 'Harry Potter and the Goblet of Fire', 2005, 157, phase='Harry Potter'),
        E(M, 'Harry Potter and the Order of the Phoenix', 2007, 138, phase='Harry Potter'),
        E(M, 'Harry Potter and the Half-Blood Prince', 2009, 153, phase='Harry Potter'),
        E(M, 'Harry Potter and the Deathly Hallows – Part 1', 2010, 146, phase='Harry Potter'),
        E(M, 'Harry Potter and the Deathly Hallows – Part 2', 2011, 130, phase='Harry Potter'),
        E(M, 'Fantastic Beasts and Where to Find Them', 2016, 133, phase='Fantastic Beasts', essential=False),
        E(M, 'Fantastic Beasts: The Crimes of Grindelwald', 2018, 134, phase='Fantastic Beasts', essential=False),
        E(M, 'Fantastic Beasts: The Secrets of Dumbledore', 2022, 142, phase='Fantastic Beasts', essential=False),
      ], chrono=[
        'Fantastic Beasts and Where to Find Them', 'Fantastic Beasts: The Crimes of Grindelwald',
        'Fantastic Beasts: The Secrets of Dumbledore', "Harry Potter and the Philosopher's Stone",
        'Harry Potter and the Chamber of Secrets', 'Harry Potter and the Prisoner of Azkaban',
        'Harry Potter and the Goblet of Fire', 'Harry Potter and the Order of the Phoenix',
        'Harry Potter and the Half-Blood Prince', 'Harry Potter and the Deathly Hallows – Part 1',
        'Harry Potter and the Deathly Hallows – Part 2',
      ]),

    F('the-conjuring-universe', 'The Conjuring Universe', 'universe', 'complete',
      "Horror universe built around Ed and Lorraine Warren's case files, with spin-offs about "
      'Annabelle and the demon nun Valak.', [
        E(M, 'The Conjuring', 2013, 112, tags=['Horror']),
        E(M, 'Annabelle', 2014, 99, essential=False),
        E(M, 'The Conjuring 2', 2016, 134),
        E(M, 'Annabelle: Creation', 2017, 109),
        E(M, 'The Nun', 2018, 96),
        E(M, 'The Curse of La Llorona', 2019, 93, canon='optional', essential=False,
          note='Only loosely connected (one cameo).'),
        E(M, 'Annabelle Comes Home', 2019, 106, essential=False),
        E(M, 'The Conjuring: The Devil Made Me Do It', 2021, 112),
        E(M, 'The Nun II', 2023, 110),
        E(M, 'The Conjuring: Last Rites', 2025, 135, note='Final Warrens film.'),
      ], chrono=[
        'The Nun', 'Annabelle: Creation', 'The Nun II', 'Annabelle', 'The Conjuring',
        'Annabelle Comes Home', 'The Curse of La Llorona', 'The Conjuring 2',
        'The Conjuring: The Devil Made Me Do It', 'The Conjuring: Last Rites',
      ]),

    F('breaking-bad-universe', 'Breaking Bad Universe', 'universe', 'complete',
      "Vince Gilligan's Albuquerque: Walter White's story, its sequel film, and the Saul Goodman "
      'prequel series.', [
        E(S, 'Breaking Bad', 2008, 2900, seasons=5, tags=['Crime', 'Drama']),
        E(S, 'Better Call Saul', 2015, 3200, seasons=6,
          note='Mostly a prequel, but its final season continues after Breaking Bad. Watch in release order.'),
        E(M, 'El Camino: A Breaking Bad Movie', 2019, 122, note="Jesse's story right after the finale."),
      ], chrono=['Better Call Saul', 'Breaking Bad', 'El Camino: A Breaking Bad Movie']),

    F('a-song-of-ice-and-fire', 'Game of Thrones Universe', 'universe', 'ongoing',
      "HBO's Westeros: Game of Thrones and its prequels House of the Dragon (172 years earlier) "
      'and A Knight of the Seven Kingdoms (about 90 years earlier).', [
        E(S, 'Game of Thrones', 2011, 4100, seasons=8, tags=['Fantasy', 'Drama']),
        E(S, 'House of the Dragon', 2022, 620, label='Season 1', ongoing=True),
        E(S, 'House of the Dragon', 2024, 520, label='Season 2', ongoing=True),
        E(S, 'A Knight of the Seven Kingdoms', 2026, 190, label='Season 1', ongoing=True),
      ], chrono=['House of the Dragon|Season 1', 'House of the Dragon|Season 2',
                 'A Knight of the Seven Kingdoms|Season 1', 'Game of Thrones']),

    # ── Sagas ─────────────────────────────────────────────────────────────
    F('fast-and-furious', 'Fast & Furious', 'saga', 'ongoing',
      'From street racing to globe-trotting heists: Dom Toretto and family across eleven films.', [
        E(M, 'The Fast and the Furious', 2001, 106, tags=['Action']),
        E(M, '2 Fast 2 Furious', 2003, 107),
        E(M, 'The Fast and the Furious: Tokyo Drift', 2006, 104,
          note='Takes place after Fast & Furious 6 — that is why Han is back.'),
        E(M, 'Fast & Furious', 2009, 107),
        E(M, 'Fast Five', 2011, 130),
        E(M, 'Fast & Furious 6', 2013, 130),
        E(M, 'Furious 7', 2015, 137),
        E(M, 'The Fate of the Furious', 2017, 136),
        E(M, 'Fast & Furious Presents: Hobbs & Shaw', 2019, 137, canon='optional', essential=False,
          note='Spin-off.'),
        E(M, 'F9', 2021, 143),
        E(M, 'Fast X', 2023, 141),
      ], chrono=[
        'The Fast and the Furious', '2 Fast 2 Furious', 'Fast & Furious', 'Fast Five',
        'Fast & Furious 6', 'The Fast and the Furious: Tokyo Drift', 'Furious 7',
        'The Fate of the Furious', 'Fast & Furious Presents: Hobbs & Shaw', 'F9', 'Fast X',
      ]),

    F('mission-impossible', 'Mission: Impossible', 'saga', 'complete',
      "Ethan Hunt and the IMF across eight films, ending with The Final Reckoning.", [
        E(M, 'Mission: Impossible', 1996, 110, tags=['Action', 'Thriller']),
        E(M, 'Mission: Impossible 2', 2000, 123, essential=False),
        E(M, 'Mission: Impossible III', 2006, 126),
        E(M, 'Mission: Impossible – Ghost Protocol', 2011, 133),
        E(M, 'Mission: Impossible – Rogue Nation', 2015, 131),
        E(M, 'Mission: Impossible – Fallout', 2018, 147),
        E(M, 'Mission: Impossible – Dead Reckoning', 2023, 163),
        E(M, 'Mission: Impossible – The Final Reckoning', 2025, 169),
      ]),

    F('despicable-me', 'Despicable Me & Minions', 'saga', 'ongoing',
      "Gru goes from supervillain to dad; the Minions get two prequels of their own.", [
        E(M, 'Despicable Me', 2010, 95, tags=['Animation', 'Comedy']),
        E(M, 'Despicable Me 2', 2013, 98),
        E(M, 'Minions', 2015, 91, note='Prequel set in 1968.'),
        E(M, 'Despicable Me 3', 2017, 89),
        E(M, 'Minions: The Rise of Gru', 2022, 87, note='Prequel: 11-year-old Gru.'),
        E(M, 'Despicable Me 4', 2024, 94),
      ], chrono=['Minions', 'Minions: The Rise of Gru', 'Despicable Me', 'Despicable Me 2',
                 'Despicable Me 3', 'Despicable Me 4']),

    F('hotel-transylvania', 'Hotel Transylvania', 'saga', 'complete',
      "Dracula's monsters-only hotel, his daughter Mavis and her very human husband Johnny.", [
        E(M, 'Hotel Transylvania', 2012, 91, tags=['Animation', 'Comedy']),
        E(M, 'Hotel Transylvania 2', 2015, 89),
        E(M, 'Hotel Transylvania 3: Summer Vacation', 2018, 97),
        E(M, 'Hotel Transylvania: Transformania', 2022, 87),
      ]),

    F('toy-story', 'Toy Story', 'saga', 'ongoing',
      "Pixar's first feature and its sequels: Woody, Buzz and the toys who come alive when nobody "
      'is watching.', [
        E(M, 'Toy Story', 1995, 81, tags=['Animation', 'Comedy']),
        E(M, 'Toy Story 2', 1999, 92),
        E(M, 'Toy Story 3', 2010, 103),
        E(M, 'Toy Story 4', 2019, 100),
        E(M, 'Lightyear', 2022, 105, canon='optional', essential=False,
          note='The in-universe movie that made Andy want a Buzz toy.'),
      ]),

    # ── Anime ─────────────────────────────────────────────────────────────
    F('dragon-ball', 'Dragon Ball', 'anime', 'ongoing',
      "Goku's journey from kid martial artist to universe-saving Saiyan. Battle of Gods and "
      "Resurrection 'F' are retold in Dragon Ball Super; GT is not canon.", [
        E(A, 'Dragon Ball', 1986, 3520, seasons=1, tags=['Action', 'Shonen']),
        E(A, 'Dragon Ball Z', 1989, 6690, seasons=1, note='Or watch Dragon Ball Z Kai instead.'),
        E(A, 'Dragon Ball GT', 1996, 1470, seasons=1, canon='noncanon', essential=False),
        E(A, 'Dragon Ball Z Kai', 2009, 3840, seasons=1, canon='optional', essential=False,
          note='Remastered Z with the filler cut: alternative to Dragon Ball Z.'),
        E(A, 'Dragon Ball Z: Battle of Gods', 2013, 85, format='film', essential=False,
          note='Retold in Dragon Ball Super episodes 1–14.'),
        E(A, "Dragon Ball Z: Resurrection 'F'", 2015, 93, format='film', essential=False,
          note='Retold in Dragon Ball Super episodes 15–27.'),
        E(A, 'Dragon Ball Super', 2015, 3010, seasons=1),
        E(A, 'Dragon Ball Super: Broly', 2018, 100, format='film'),
        E(A, 'Dragon Ball Super: Super Hero', 2022, 99, format='film'),
        E(A, 'Dragon Ball Daima', 2024, 460, seasons=1, note='Set between the Buu saga and Super.'),
      ], chrono=[
        'Dragon Ball', 'Dragon Ball Z', 'Dragon Ball Z Kai', 'Dragon Ball Daima',
        'Dragon Ball Z: Battle of Gods', "Dragon Ball Z: Resurrection 'F'", 'Dragon Ball Super',
        'Dragon Ball Super: Broly', 'Dragon Ball Super: Super Hero', 'Dragon Ball GT',
      ]),

    F('naruto', 'Naruto', 'anime', 'ongoing',
      'Naruto Uzumaki from outcast ninja to Hokage, then his son Boruto. About 40% of the original '
      'and Shippuden episodes are filler — check a filler list.', [
        E(A, 'Naruto', 2002, 5060, seasons=1, tags=['Action', 'Shonen'],
          note='220 episodes; about 90 are filler (most of 136–220).'),
        E(A, 'Naruto: Shippuden', 2007, 11500, seasons=1, note='500 episodes; about 200 are filler.'),
        E(A, 'The Last: Naruto the Movie', 2014, 112, format='film',
          note='Canon. Set between Shippuden episodes 493 and 494.'),
        E(A, 'Boruto: Naruto the Movie', 2015, 95, format='film', essential=False,
          note='Retold in Boruto episodes 54–66.'),
        E(A, 'Boruto: Naruto Next Generations', 2017, 6740, seasons=1),
      ], chrono=['Naruto', 'The Last: Naruto the Movie', 'Naruto: Shippuden',
                 'Boruto: Naruto the Movie', 'Boruto: Naruto Next Generations']),

    F('fate', 'Fate', 'anime', 'complete',
      'Mages and legendary heroes fight the Holy Grail War. Three routes of the Fate/stay night '
      'visual novel plus the Fate/Zero prequel. Common recommendation: Fate/Zero → Unlimited Blade '
      "Works → Heaven's Feel.", [
        E(A, 'Fate/stay night (2006)', 2006, 550, seasons=1, phase='Fifth Holy Grail War',
          canon='optional', essential=False,
          note='Older adaptation of the "Fate" route. Most fans skip it.', tags=['Action', 'Fantasy']),
        E(A, 'Fate/Zero', 2011, 575, seasons=1, phase='Fourth Holy Grail War',
          note='Prequel. Some fans watch it after Unlimited Blade Works to avoid spoilers.'),
        E(A, 'Fate/stay night: Unlimited Blade Works', 2014, 650, seasons=1, phase='Fifth Holy Grail War'),
        E(A, "Fate/stay night: Heaven's Feel", 2017, 120, label='I. Presage Flower', format='film',
          phase='Fifth Holy Grail War', note='Darkest route — watch last.'),
        E(A, "Fate/stay night: Heaven's Feel", 2019, 117, label='II. Lost Butterfly', format='film',
          phase='Fifth Holy Grail War'),
        E(A, "Fate/stay night: Heaven's Feel", 2020, 122, label='III. Spring Song', format='film',
          phase='Fifth Holy Grail War'),
      ], chrono=[
        'Fate/Zero', 'Fate/stay night (2006)', 'Fate/stay night: Unlimited Blade Works',
        "Fate/stay night: Heaven's Feel|I. Presage Flower", "Fate/stay night: Heaven's Feel|II. Lost Butterfly",
        "Fate/stay night: Heaven's Feel|III. Spring Song",
      ]),

    F('demon-slayer', 'Demon Slayer', 'anime', 'ongoing',
      'Tanjiro hunts demons to cure his sister Nezuko. The Mugen Train movie sits between Season 1 '
      'and the Entertainment District Arc; the Infinity Castle trilogy finishes the story.', [
        E(A, 'Demon Slayer: Kimetsu no Yaiba', 2019, 600, label='Season 1', tags=['Action', 'Shonen']),
        E(A, 'Demon Slayer: Mugen Train', 2020, 117, format='film'),
        E(A, 'Demon Slayer: Kimetsu no Yaiba', 2021, 160, label='Mugen Train Arc (TV)', essential=False,
          canon='optional', note='TV version of the Mugen Train movie — watch one or the other.'),
        E(A, 'Demon Slayer: Kimetsu no Yaiba', 2021, 280, label='Entertainment District Arc'),
        E(A, 'Demon Slayer: Kimetsu no Yaiba', 2023, 270, label='Swordsmith Village Arc'),
        E(A, 'Demon Slayer: Kimetsu no Yaiba', 2024, 200, label='Hashira Training Arc'),
        E(A, 'Demon Slayer: Infinity Castle', 2025, 155, format='film', ongoing=True,
          note='Part 1 of a film trilogy.'),
      ]),

    F('attack-on-titan', 'Attack on Titan', 'anime', 'complete',
      "Humanity's last city behind giant walls, and what lies beyond them. One story told across "
      'four seasons and a multi-part finale.', [
        E(A, 'Attack on Titan', 2013, 575, label='Season 1', tags=['Action', 'Drama']),
        E(A, 'Attack on Titan', 2017, 276, label='Season 2'),
        E(A, 'Attack on Titan', 2018, 506, label='Season 3'),
        E(A, 'Attack on Titan', 2020, 860, label='The Final Season',
          note='Parts 1–2 on TV, then the two-part finale "The Final Chapters".'),
      ]),

    F('jujutsu-kaisen', 'Jujutsu Kaisen', 'anime', 'ongoing',
      'Yuji Itadori swallows a cursed finger and joins Tokyo Jujutsu High. The movie JJK 0 is a '
      'prequel best watched after Season 1.', [
        E(A, 'Jujutsu Kaisen', 2020, 550, label='Season 1', tags=['Action', 'Shonen', 'Supernatural']),
        E(A, 'Jujutsu Kaisen 0', 2021, 105, format='film',
          note='Prequel starring Yuta Okkotsu. Season 2 assumes you have seen it.'),
        E(A, 'Jujutsu Kaisen', 2023, 530, label='Season 2',
          note='Opens with the Hidden Inventory arc (Gojo and Geto as students).'),
      ], chrono=['Jujutsu Kaisen 0', 'Jujutsu Kaisen|Season 1', 'Jujutsu Kaisen|Season 2']),

    F('monogatari', 'Monogatari', 'anime', 'complete',
      "Koyomi Araragi and the girls touched by apparitions. The r/araragi wiki recommends novel "
      '(roughly release) order; chronological order is for rewatches.', [
        E(A, 'Bakemonogatari', 2009, 345, seasons=1, tags=['Mystery', 'Supernatural']),
        E(A, 'Nisemonogatari', 2012, 253, seasons=1),
        E(A, 'Nekomonogatari: Black', 2012, 92, seasons=1),
        E(A, 'Monogatari Series: Second Season', 2013, 598, seasons=1),
        E(A, 'Hanamonogatari', 2014, 115, seasons=1, note='Novel order puts it after Owarimonogatari.'),
        E(A, 'Tsukimonogatari', 2014, 92, seasons=1),
        E(A, 'Owarimonogatari', 2015, 276, label='Season 1'),
        E(A, 'Kizumonogatari', 2016, 64, label='Part 1: Tekketsu', format='film',
          note='Prequel trilogy; the r/araragi wiki places it right after Bakemonogatari.'),
        E(A, 'Kizumonogatari', 2016, 69, label='Part 2: Nekketsu', format='film'),
        E(A, 'Koyomimonogatari', 2016, 144, seasons=1, essential=False, note='12 short episodes.'),
        E(A, 'Kizumonogatari', 2017, 83, label='Part 3: Reiketsu', format='film'),
        E(A, 'Owarimonogatari', 2017, 161, label='Season 2'),
        E(A, 'Zoku Owarimonogatari', 2018, 138, seasons=1),
        E(A, 'Monogatari Series: Off & Monster Season', 2024, 322, seasons=1),
      ], chrono=[
        'Kizumonogatari|Part 1: Tekketsu', 'Kizumonogatari|Part 2: Nekketsu',
        'Kizumonogatari|Part 3: Reiketsu', 'Nekomonogatari: Black', 'Bakemonogatari',
        'Nisemonogatari', 'Monogatari Series: Second Season', 'Tsukimonogatari', 'Koyomimonogatari',
        'Owarimonogatari|Season 1', 'Owarimonogatari|Season 2', 'Zoku Owarimonogatari', 'Hanamonogatari',
        'Monogatari Series: Off & Monster Season',
      ]),

    # ── Duologies & trilogies (One & Done) ─────────────────────────────────
    F('the-incredibles', 'The Incredibles', 'duology', 'complete',
      'A family of undercover superheroes, back in action.', [
        E(M, 'The Incredibles', 2004, 115, tags=['Animation', 'Action']),
        E(M, 'Incredibles 2', 2018, 118, note='Picks up seconds after the first film ends.'),
      ]),
    F('monsters-inc', 'Monsters, Inc.', 'duology', 'complete',
      'Sulley and Mike: scarers, best friends, and one very small human.', [
        E(M, 'Monsters, Inc.', 2001, 92, tags=['Animation', 'Comedy']),
        E(M, 'Monsters University', 2013, 104, note='Prequel: Mike and Sulley at college.'),
      ], chrono=['Monsters University', 'Monsters, Inc.']),
    F('dune', 'Dune', 'duology', 'ongoing',
      "Denis Villeneuve's adaptation of Frank Herbert's novel. Part Three is coming.", [
        E(M, 'Dune', 2021, 155, tags=['Sci-Fi', 'Adventure']),
        E(M, 'Dune: Part Two', 2024, 166),
      ]),
    F('before-trilogy', 'The Before Trilogy', 'trilogy', 'complete',
      'Jesse and Céline meet on a train, then again every nine years.', [
        E(M, 'Before Sunrise', 1995, 101, tags=['Romance', 'Drama']),
        E(M, 'Before Sunset', 2004, 80),
        E(M, 'Before Midnight', 2013, 109),
      ]),
    F('back-to-the-future', 'Back to the Future', 'trilogy', 'complete',
      'Marty McFly and Doc Brown, a DeLorean, and 1.21 gigawatts.', [
        E(M, 'Back to the Future', 1985, 116, tags=['Sci-Fi', 'Comedy']),
        E(M, 'Back to the Future Part II', 1989, 108),
        E(M, 'Back to the Future Part III', 1990, 118),
      ]),
    F('the-dark-knight-trilogy', 'The Dark Knight Trilogy', 'trilogy', 'complete',
      "Christopher Nolan's Batman, from origin to the Dark Knight's last stand.", [
        E(M, 'Batman Begins', 2005, 140, tags=['Action', 'Crime']),
        E(M, 'The Dark Knight', 2008, 152),
        E(M, 'The Dark Knight Rises', 2012, 164),
      ]),
]

# Finite stories with no franchise — shown on One & Done.
STANDALONES = [
    E(M, 'Parasite', 2019, 132, tags=['Thriller', 'Drama'], language='Korean',
      desc='A poor family schemes its way into a rich household, until it all goes wrong.'),
    E(M, 'Whiplash', 2014, 106, tags=['Drama', 'Music'],
      desc='A young jazz drummer and the teacher who will stop at nothing to push him.'),
    E(M, 'Arrival', 2016, 116, tags=['Sci-Fi', 'Drama'],
      desc='A linguist races to understand the aliens who have just landed.'),
    E(M, 'Everything Everywhere All at Once', 2022, 139, tags=['Sci-Fi', 'Comedy'],
      desc='A laundromat owner must connect with her multiverse selves to save everything.'),
    E(M, 'Interstellar', 2014, 169, tags=['Sci-Fi', 'Adventure'],
      desc='Astronauts travel through a wormhole to find humanity a new home.'),
    E(M, 'Coco', 2017, 105, tags=['Animation', 'Music'],
      desc='A boy who dreams of music crosses into the Land of the Dead.'),
    E(A, 'Your Name', 2016, 106, format='film', tags=['Romance', 'Supernatural'], language='Japanese',
      desc="Two teenagers who have never met start waking up in each other's bodies."),
    E(A, 'Spirited Away', 2001, 125, format='film', tags=['Fantasy', 'Adventure'], language='Japanese',
      desc='Chihiro must work in a bathhouse for spirits to free her parents.'),
    E(A, 'A Silent Voice', 2016, 130, format='film', tags=['Drama', 'Romance'], language='Japanese',
      desc='A former bully tries to make amends with the deaf girl he tormented.'),
    E(A, 'Perfect Blue', 1997, 81, format='film', tags=['Psychological', 'Thriller'], language='Japanese',
      desc='A pop idol turned actress loses her grip on what is real.'),
]

LIMITED = [
    E(S, 'Chernobyl', 2019, 330, seasons=1, tags=['History', 'Drama'],
      desc='The 1986 nuclear disaster and the people who paid to contain it. Five episodes.'),
    E(S, "The Queen's Gambit", 2020, 395, seasons=1, tags=['Drama'],
      desc='An orphaned chess prodigy fights her way to the top, and against her addictions.'),
    E(S, 'Dark', 2017, 1550, seasons=3, tags=['Sci-Fi', 'Mystery'], language='German',
      desc='Four families, one small town, and a time loop spanning 33-year cycles.'),
    E(S, 'Arcane', 2021, 720, seasons=2, tags=['Animation', 'Action'],
      desc='Two sisters on opposite sides of the war between Piltover and Zaun.'),
    E(S, 'Fleabag', 2016, 330, seasons=2, tags=['Comedy', 'Drama'],
      desc='A grieving, chaotic Londoner talks straight to the camera.'),
    E(S, 'Band of Brothers', 2001, 594, seasons=1, tags=['History', 'Drama'],
      desc='Easy Company from D-Day to the end of World War II.'),
    E(A, 'Death Note', 2006, 850, seasons=1, tags=['Psychological', 'Thriller'], language='Japanese',
      desc='A student finds a notebook that kills anyone whose name is written in it.'),
    E(A, 'Cyberpunk: Edgerunners', 2022, 250, seasons=1, tags=['Sci-Fi', 'Action'],
      desc='A street kid becomes an edgerunner in Night City. Ten episodes.'),
    E(A, 'Erased', 2016, 280, seasons=1, tags=['Mystery', 'Thriller'], language='Japanese',
      desc='A man sent back 18 years tries to stop a string of kidnappings.'),
    E(A, 'Devilman Crybaby', 2018, 250, seasons=1, tags=['Horror', 'Action'], language='Japanese',
      desc='A shy boy merges with a demon to fight demons. Ten episodes.'),
]

# Single works that the old site listed as franchises. --prune removes these franchise
# records (the titles themselves are kept).
FALSE_FRANCHISES = ['one-punch-man', 'the-simpsons']
