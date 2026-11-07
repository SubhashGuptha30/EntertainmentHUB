# Entertainment Hub — README

## Project Overview

Entertainment Hub is a franchise- and anime-first discovery site: a Netflix-style take on a
franchise watch-order guide. For each franchise it shows release order vs chronological order,
canon/filler flags, skippable entries, where each part streams, and the user's watch progress.
See [docs/FRANCHISE_PLAN.md](docs/FRANCHISE_PLAN.md) for the product plan and roadmap.

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (pages in `templates/` fetch JSON from the API)
- **Backend**: Python Flask (gunicorn), containerized with Docker
- **Database**: MongoDB Atlas (free M0 cluster)
- **Media storage**: Cloudinary (free plan)
- **Hosting**: Render (free web service) at https://ehub.subhashguptha.online

Environment variables: `MONGODB_URI`, `CLOUDINARY_URL`, `SECRET_KEY`, `ADMIN_PASSWORD`.
Tests: `python -m pytest -q` (runs against an in-memory MongoDB).

---

## Project Structure

```
sorted websit/
├── app.py               # Flask server — all API routes & page serving
├── database.py          # MongoDB data layer (users, content, selectors, franchises, progress)
├── requirements.txt
├── scripts/             # One-off migration scripts
├── tests/               # pytest + mongomock
├── docs/                # Product plan
├── static/              # css/, js/, images/, admin/
└── templates/
    ├── index.html       # Landing page
    ├── home.html        # Main user dashboard
    ├── franchises.html  # All franchises (filter: universe / saga / anime)
    ├── franchise.html   # One franchise: watch-order timeline  (/franchise/<slug>)
    ├── movies.html, anime.html, web-series.html, see-all.html
    ├── play.html        # Title detail page
    ├── profile.html, aboutus.html, redirect.html, login/, contact/
    └── admin/           # dashboard, content, franchises, users, selectors
```

---

## Running locally

```bash
pip install -r requirements.txt
```

```bash
MONGODB_URI="mongodb+srv://..." ADMIN_PASSWORD="choose-one" python app.py
```

Open http://localhost:5000 — admin panel at http://localhost:5000/admin/index (user `admin`,
password from `ADMIN_PASSWORD`; if unset, a random one is printed on first start).

On first start against a database without a `franchises` collection, the old selector-based
franchises (and each title's `franchise` field) are migrated automatically.

### Seeding curated watch orders

`scripts/seed_data.py` holds 25 researched franchises (MCU, Star Wars, Middle-earth, Wizarding
World, Conjuring, Breaking Bad, Game of Thrones, Fast & Furious, Mission: Impossible, Despicable
Me & Minions, Hotel Transylvania, Toy Story, Dragon Ball, Naruto, Fate, Demon Slayer, Attack on
Titan, Jujutsu Kaisen, Monogatari, plus duologies/trilogies) and 20 standalone films / short series.

```bash
python -m scripts.seed_franchises
```

```bash
python -m scripts.seed_franchises --apply --prune
```

The first command is a dry run. `--apply` writes; `--prune` deletes franchise records for single
works (One Punch Man, The Simpsons). Re-running is safe: existing titles are matched by type and
title and only their empty fields are filled; existing franchise images are kept.
Seeded titles have no artwork — upload posters/banners in the admin panel (cards show a
generated gradient until then).

### Pages

| URL | What it shows |
|-----|---------------|
| `/home` | Continue your franchises, universes, anime sagas, sagas, "finish this weekend" |
| `/franchises` | Universes, sagas, anime (filterable) |
| `/franchise/<slug>` | Timeline: release / chronological / essentials, canon flags, runtimes, watched ticks |
| `/one-and-done` | Standalone films, duologies, trilogies, ≤3-season series; filter by time budget |
| `/anime` | Anime franchises first, then finishable anime |
| `/admin/franchises` | Franchise + watch-order editor |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET / PUT | `/api/auth/me` | Get / update logged-in user |
| GET | `/api/content` | All content (movies + anime + series) |
| GET | `/api/content/<type>` | By type: `movies`, `animes`, `webSeries` |
| GET | `/api/franchises?kind=universe,saga` | Franchise summaries with counts and runtime |
| GET | `/api/franchises/<slug>` | Franchise with ordered entries |
| GET | `/api/franchises/of/<content_id>` | Franchises a title belongs to, with previous/next entry |
| GET | `/api/compact?kind=&max_minutes=` | One & Done titles, shortest first |
| GET / PUT | `/api/me/progress` | Watched entries (PUT body: `{key, watched}`) |
| GET | `/api/me/continue` | Started-but-unfinished franchises with the next entry |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/admin/stats` | Dashboard stats |
| GET / DELETE | `/api/admin/users[/<id>]` | List / delete users |
| GET / POST | `/api/admin/content` | List / add content |
| PUT / DELETE | `/api/admin/content/<id>` | Edit / delete content |
| GET / PUT / DELETE | `/api/admin/franchises/<slug>` | Get / save / delete franchise |
| POST | `/api/admin/franchises` | Create franchise |
