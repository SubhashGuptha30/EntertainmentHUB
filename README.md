# Entertainment Hub — README

## Project Overview

Entertainment Hub is a full-stack OTT (Over-The-Top) streaming platform built as a college project using:

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask
- **Database**: SQLite (via Python's built-in `sqlite3`)
- **Self-hosted**: runs entirely on your local machine — no cloud required

---

## Project Structure

```
sorted websit/
├── app.py               # Flask server — all API routes & page serving
├── database.py          # SQLite schema, data migration, helper functions
├── requirements.txt     # Python dependencies (just Flask)
├── entertainmenthub.db  # SQLite database (auto-created on first run)
│
├── static/              # All static web assets (served at root /)
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   ├── images/          # Images (posters, banners, cast photos)
│   ├── data/            # JSON backup files (original source data)
│   └── admin/           # Admin portal CSS & JS
│       ├── admin.css
│       └── admin.js
│
└── templates/           # All HTML pages
    ├── index.html       # Landing page
    ├── home.html        # Main user dashboard
    ├── movies.html      # Movies section
    ├── anime.html       # Anime section
    ├── web-series.html  # Web Series section
    ├── play.html        # Content detail & player page
    ├── profile.html     # User profile
    ├── franchises.html  # Franchises page
    ├── aboutus.html     # About page
    ├── redirect.html    # Watch platform redirect page
    ├── login/
    │   ├── login.html
    │   ├── register.html
    │   └── success.html
    ├── contact/
    │   └── contactus.html
    └── admin/           # Admin portal pages
        ├── index.html   # Admin login
        ├── dashboard.html
        ├── content.html # Add / Edit / Delete content
        └── users.html   # View registered users
```

---

## Setup & Running

### 1. Install Python (if not already)
Download from https://python.org (Python 3.8+ recommended)

### 2. Install Flask
```bash
pip install flask
```

### 3. Start the server
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

### 5. Admin Panel
```
http://localhost:5000/admin/index.html
Username: admin
Password: admin123
```

---

## Access from Another Device (LAN)

The server binds to `0.0.0.0`, so it's accessible from any device on the same WiFi:

```bash
# Find your local IP on Windows:
ipconfig

# Then share this URL with your professor:
http://<your-local-IP>:5000
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/auth/me` | Get logged-in user info |
| PUT | `/api/auth/me` | Update profile / password |
| GET | `/api/content` | Get all content (movies + anime + series) |
| GET | `/api/content/<type>` | Get by type: `movies`, `animes`, `webSeries` |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/admin/stats` | Dashboard stats |
| GET | `/api/admin/users` | List all users |
| DELETE | `/api/admin/users/<id>` | Delete a user |
| GET | `/api/admin/content` | List all content |
| POST | `/api/admin/content` | Add new content item |
| PUT | `/api/admin/content/<id>` | Edit content item |
| DELETE | `/api/admin/content/<id>` | Delete content item |

---

## Notes

- The SQLite database (`entertainmenthub.db`) is auto-created and populated from the JSON files in `static/data/` on first run.
- The admin user (`admin` / `admin123`) is seeded automatically.
- Change the Flask `secret_key` in `app.py` before sharing the project publicly.
