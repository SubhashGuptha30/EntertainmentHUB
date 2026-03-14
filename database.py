"""
database.py — SQLite setup and JSON migration for Entertainment Hub
Run this file once to create and populate the database.
Also imported by app.py for the get_db() helper.
"""

import sqlite3
import json
import os
import hashlib

DB_PATH  = os.path.join(os.path.dirname(__file__), 'entertainmenthub.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'static', 'data')


def get_db():
    """Open a new database connection. Used by Flask request context."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Create all tables if they don't exist, then seed data."""
    conn = get_db()
    c = conn.cursor()

    # ── Users table ──────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            gender      TEXT,
            age         INTEGER,
            profile_pic TEXT    DEFAULT '/images/user.png',
            is_admin    INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ── Content table (movies, anime, web-series all in one) ─────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            slug         TEXT    NOT NULL,
            type         TEXT    NOT NULL,          -- 'movies' | 'animes' | 'webSeries'
            title        TEXT    NOT NULL,
            h_image      TEXT    DEFAULT '',
            v_image      TEXT    DEFAULT '',
            rating       TEXT    DEFAULT '4.5',
            status       TEXT    DEFAULT 'Released',
            description  TEXT    DEFAULT '',
            tags         TEXT    DEFAULT '[]',      -- JSON array stored as text
            cast_data    TEXT    DEFAULT '[]',      -- JSON array stored as text
            watch_options TEXT   DEFAULT '[]',      -- JSON array stored as text
            video_url    TEXT    DEFAULT '',
            genre_display TEXT   DEFAULT '',
            sections     TEXT    DEFAULT '[]',      -- JSON array stored as text
            franchise    TEXT    DEFAULT '',
            UNIQUE(slug, type)
        )
    '''
    )

    # ── Selectors table (manages dropdown options for the admin form) ──────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS selectors (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT    NOT NULL,
            value    TEXT    NOT NULL,
            UNIQUE(category, value)
        )
    ''')

    conn.commit()

    # ── Seed default selectors (only on first run) ────────────────────────────
    if c.execute('SELECT COUNT(*) FROM selectors').fetchone()[0] == 0:
        _seed_selectors(c)
        conn.commit()
        print('[DB] Selectors seeded with defaults')

    # ── Seed admin user ───────────────────────────────────────────────────────
    existing_admin = c.execute(
        "SELECT id FROM users WHERE username = 'admin'"
    ).fetchone()
    if not existing_admin:
        c.execute('''
            INSERT INTO users (username, email, password, gender, age, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@entertainmenthub.com', hash_password('admin123'),
              'Other', 0, 1))
        conn.commit()
        print("[DB] Admin user created  ->  username: admin | password: admin123")

    # ── Migrate JSON data ─────────────────────────────────────────────────────
    existing_content = c.execute('SELECT COUNT(*) FROM content').fetchone()[0]
    if existing_content == 0:
        _migrate_json(c, conn)
    else:
        print(f'[DB] Content already present ({existing_content} rows), skipping migration.')

    # ── Migrate existing cast members into selectors (idempotent) ─────────────
    if c.execute("SELECT COUNT(*) FROM selectors WHERE category='cast'").fetchone()[0] == 0:
        _migrate_cast_to_selectors(c, conn)

    # ── Ensure watch_options selectors use JSON format (idempotent) ────────────
    _migrate_watch_options_to_json(c, conn)

    conn.close()


def _migrate_json(cursor, conn):
    """Read the three JSON files and INSERT them into the content table."""
    file_map = {
        'movies':    'movies.json',
        'animes':    'anime.json',
        'webSeries': 'series.json',
    }
    total = 0
    for content_type, filename in file_map.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[DB] WARNING: {filepath} not found, skipping.")
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for slug, item in data.items():
            cursor.execute('''
                INSERT OR IGNORE INTO content
                    (slug, type, title, h_image, v_image, rating, status,
                     description, tags, cast_data, watch_options, video_url,
                     genre_display, sections)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                slug,
                content_type,
                item.get('title', slug),
                item.get('h-image', ''),
                item.get('v-image', ''),
                str(item.get('rating', '4.5')),
                item.get('Status', 'Released'),
                item.get('description', ''),
                json.dumps(item.get('tags', []), ensure_ascii=False),
                json.dumps(item.get('cast', []), ensure_ascii=False),
                json.dumps(item.get('watchOptions', []), ensure_ascii=False),
                item.get('videoUrl', ''),
                item.get('genreDisplay', ''),
                json.dumps(item.get('sections', []), ensure_ascii=False),
            ))
            total += 1
        conn.commit()
        print(f"[DB] Migrated {len(data)} items from {filename} ({content_type})")
    print(f'[DB] Total content migrated: {total} items')


def _seed_selectors(cursor):
    """Seed default dropdown options into selectors table."""
    defaults = {
        'rating': [
            'G', 'PG', 'PG-13', 'R', 'NC-17',
            'TV-G', 'TV-PG', 'TV-14', 'TV-MA', 'Not Rated', '18+'
        ],
        'tags': [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
            'Drama', 'Fantasy', 'History', 'Horror', 'Mystery', 'Romance',
            'Sci-Fi', 'Slice of Life', 'Sports', 'Supernatural', 'Thriller',
            'Mecha', 'Isekai', 'Shonen', 'Seinen', 'Shoujo', 'Psychological', 'Music'
        ],
        'watch_options': [
            'Netflix', 'Amazon Prime Video', 'Disney+ Hotstar', 'Apple TV+',
            'Hulu', 'HBO Max', 'Crunchyroll', 'Funimation', 'Peacock',
            'Sony LIV', 'Zee5', 'MX Player', 'YouTube Premium', 'Paramount+'
        ],
    }
    for category, values in defaults.items():
        for val in values:
            # watch_options: seed as JSON {name, logo} from start
            if category == 'watch_options':
                db_val = json.dumps({'name': val, 'logo': ''}, ensure_ascii=False)
            else:
                db_val = val
            cursor.execute(
                'INSERT OR IGNORE INTO selectors (category, value) VALUES (?, ?)',
                (category, db_val)
            )


def _migrate_cast_to_selectors(cursor, conn):
    """Extract unique cast members from content.cast_data into selectors."""
    rows = cursor.execute(
        "SELECT cast_data FROM content WHERE cast_data != '[]' AND cast_data != ''"
    ).fetchall()
    seen = set()
    for row in rows:
        try:
            members = json.loads(row[0])
            for m in members:
                name = (m.get('name') or '').strip()
                if name and name not in seen:
                    seen.add(name)
                    val = json.dumps(
                        {'name': name, 'image': m.get('image', '')},
                        ensure_ascii=False
                    )
                    cursor.execute(
                        'INSERT OR IGNORE INTO selectors (category, value) VALUES (?, ?)',
                        ('cast', val)
                    )
        except Exception:
            pass
    conn.commit()
    print(f'[DB] Migrated {len(seen)} cast members into selectors')


def _migrate_watch_options_to_json(cursor, conn):
    """Convert any watch_options selector still stored as plain string to
    JSON {name, logo} format. Idempotent - already-JSON rows are skipped."""
    rows = cursor.execute(
        "SELECT id, value FROM selectors WHERE category='watch_options'"
    ).fetchall()
    migrated = 0
    for row in rows:
        try:
            json.loads(row[1])  # already JSON — skip
        except (ValueError, TypeError):
            new_val = json.dumps({'name': row[1], 'logo': ''}, ensure_ascii=False)
            cursor.execute('UPDATE selectors SET value=? WHERE id=?', (new_val, row[0]))
            migrated += 1
    if migrated:
        conn.commit()
        print(f'[DB] Migrated {migrated} watch_options selectors to JSON format')

def row_to_dict(row):
    """Convert a sqlite3.Row to a regular dict, parsing JSON fields."""
    d = dict(row)
    for field in ('tags', 'cast_data', 'watch_options', 'sections'):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
    # Rename cast_data → cast for frontend compatibility
    if 'cast_data' in d:
        d['cast'] = d.pop('cast_data')
    if 'watch_options' in d:
        d['watchOptions'] = d.pop('watch_options')
    if 'h_image' in d:
        d['h-image'] = d.pop('h_image')
    if 'v_image' in d:
        d['v-image'] = d.pop('v_image')
    if 'genre_display' in d:
        d['genreDisplay'] = d.pop('genre_display')
    if 'status' in d:
        d['Status'] = d.pop('status')
    return d


if __name__ == '__main__':
    print("[DB] Initializing database...")
    init_db()
    print("[DB] Done.")
