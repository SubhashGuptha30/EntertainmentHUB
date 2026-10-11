"""
database.py — MongoDB backend for Entertainment Hub (MongoDB Atlas free tier)

Collections:
  - users      : {username, email, password, gender, age, profile_pic, is_admin, created_at}
  - content    : {slug, type, title, h_image, v_image, rating, status, description,
                  tags, cast, watchOptions, video_url, genreDisplay, sections, franchise}
                  _id = "{type}_{slug}" (natural composite key)
  - selectors  : {category, value}

All _id values are strings (kept from the original Firestore document IDs),
so routes that pass IDs around are unchanged.
"""

import json
import os
import secrets
import hashlib
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient
import bcrypt

_db = None


def get_db():
    """Return the MongoDB database (lazily initialised, reused)."""
    global _db
    if _db is None:
        client = MongoClient(os.environ['MONGODB_URI'])
        _db = client[os.environ.get('MONGODB_DB', 'entertainmenthub')]
    return _db


def _new_id():
    return str(ObjectId())


def _now():
    return datetime.now(timezone.utc)


def _out(doc):
    """Mongo document -> dict with string 'id' (and no '_id')."""
    if doc is None:
        return None
    d = dict(doc)
    d['id'] = d.pop('_id')
    if isinstance(d.get('created_at'), datetime):
        d['created_at'] = d['created_at'].isoformat()
    return d


def hash_password(password):
    """Hash a password using bcrypt (salted + key-stretched)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, hashed):
    """Verify a password against a hash. Supports both bcrypt and legacy SHA-256."""
    if _is_legacy_hash(hashed):
        return hashed == hashlib.sha256(password.encode()).hexdigest()
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _is_legacy_hash(hashed):
    """Detect old SHA-256 hex hashes (64 hex chars) vs bcrypt ($2b$ prefix)."""
    return len(hashed) == 64 and not hashed.startswith('$2')


def migrate_password_if_needed(user_id, password, current_hash):
    """If the stored hash is legacy SHA-256, re-hash with bcrypt and update."""
    if _is_legacy_hash(current_hash):
        new_hash = hash_password(password)
        _users_col().update_one({'_id': user_id}, {'$set': {'password': new_hash}})
        return new_hash
    return current_hash


# ── Collection references ────────────────────────────────────────────────

def _users_col():
    return get_db()['users']

def _content_col():
    return get_db()['content']

def _selectors_col():
    return get_db()['selectors']


# ── Content helpers ──────────────────────────────────────────────────────

def content_doc_id(ctype, slug):
    """Generate a deterministic document ID for content: '{type}_{slug}'."""
    return f"{ctype}_{slug}"


def content_to_dict(doc):
    return _out(doc)


def user_to_dict(doc):
    return _out(doc)


# ── Init / Seed ──────────────────────────────────────────────────────────

def init_db():
    """Seed default data if collections are empty. Idempotent."""
    _users_col().create_index('username')
    _content_col().create_index('type')
    _selectors_col().create_index('category')

    if not _users_col().find_one({'username': 'admin'}):
        admin_pw = os.environ.get('ADMIN_PASSWORD', '')
        if not admin_pw:
            admin_pw = secrets.token_urlsafe(16)
            print(f'[DB] Generated admin password (save this!): {admin_pw}')
        _users_col().insert_one({
            '_id':         _new_id(),
            'username':    'admin',
            'email':       'admin@entertainmenthub.com',
            'password':    hash_password(admin_pw),
            'gender':      'Other',
            'age':         0,
            'profile_pic': '/static/images/user.png',
            'is_admin':    True,
            'created_at':  _now(),
        })
        print('[DB] Admin user created')

    if not _selectors_col().find_one():
        _seed_selectors()
        print('[DB] Selectors seeded with defaults')


def _seed_selectors():
    """Seed default dropdown options into the selectors collection."""
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
    docs = []
    for category, values in defaults.items():
        for val in values:
            if category == 'watch_options':
                val = json.dumps({'name': val, 'logo': ''}, ensure_ascii=False)
            docs.append({'_id': _new_id(), 'category': category, 'value': val})
    _selectors_col().insert_many(docs)


# ── User queries ─────────────────────────────────────────────────────────

def find_user_by_username(username, admin_only=False):
    """Find a user by username. Returns (doc_id, user_dict) or (None, None)."""
    doc = _users_col().find_one({'username': username, 'is_admin': bool(admin_only)})
    if doc:
        d = _out(doc)
        return d['id'], d
    return None, None


def find_user_by_username_or_email(username, email):
    """Check if username or email already exists (for registration)."""
    return _users_col().find_one({'$or': [{'username': username}, {'email': email}]}) is not None


def create_user(username, email, password, gender, age):
    """Create a new regular user. Returns the doc ID."""
    user_id = _new_id()
    _users_col().insert_one({
        '_id':         user_id,
        'username':    username,
        'email':       email,
        'password':    hash_password(password),
        'gender':      gender,
        'age':         age,
        'profile_pic': '/images/user.png',
        'is_admin':    False,
        'created_at':  _now(),
    })
    return user_id


def get_user_by_id(user_id):
    """Fetch a single user by ID."""
    return _out(_users_col().find_one({'_id': user_id}))


def update_user(user_id, data):
    """Update user fields. `data` is a dict of fields to update."""
    _users_col().update_one({'_id': user_id}, {'$set': data})


def list_users(admin=False):
    """List users (non-admin by default) for the admin dashboard, newest first."""
    users = [_out(d) for d in _users_col().find({'is_admin': admin}, {'password': 0})]
    users.sort(key=lambda u: u.get('created_at') or '', reverse=True)
    return users


def delete_user(user_id):
    """Delete a non-admin user."""
    return _users_col().delete_one({'_id': user_id, 'is_admin': False}).deleted_count > 0


# ── Content queries ──────────────────────────────────────────────────────

def get_all_content():
    """Fetch all content, grouped by type."""
    result = {'movies': {}, 'animes': {}, 'webSeries': {}}
    for doc in _content_col().find():
        d = _out(doc)
        ctype, slug = d.get('type'), d.get('slug')
        if ctype in result and slug:
            result[ctype][slug] = d
    return result


def get_content_by_type(ctype):
    """Fetch all content of a specific type."""
    return {d['slug']: d for d in map(_out, _content_col().find({'type': ctype}))}


def get_single_content(ctype, slug):
    """Fetch a single content item by type + slug."""
    return _out(_content_col().find_one({'_id': content_doc_id(ctype, slug)}))


def add_content(data):
    """Add a new content item. Returns slug or raises ValueError on duplicate."""
    doc_id = content_doc_id(data['type'], data['slug'])
    if _content_col().find_one({'_id': doc_id}, {'_id': 1}):
        raise ValueError('Slug already exists for this type')
    _content_col().insert_one({**data, '_id': doc_id})
    return data['slug']


def update_content(content_id, data):
    """Update a content item by its document ID. Returns the old document or None."""
    old = _content_col().find_one_and_update({'_id': content_id}, {'$set': data})
    if old is None:
        return None
    old.pop('_id', None)
    return old


def delete_content(content_id):
    """Delete a content item by its document ID."""
    _content_col().delete_one({'_id': content_id})


def get_content_list(ctype=None):
    """List content for admin panel. Optional type filter."""
    items = [_out(d) for d in _content_col().find({'type': ctype} if ctype else {})]
    items.sort(key=lambda x: (x.get('type', ''), x.get('title', '')))
    return items


def get_content_stats():
    """Get content counts for admin dashboard."""
    count = _content_col().count_documents
    movies = count({'type': 'movies'})
    animes = count({'type': 'animes'})
    series = count({'type': 'webSeries'})
    users = _users_col().count_documents({'is_admin': False})
    return {
        'movies': movies,
        'animes': animes,
        'series': series,
        'users':  users,
        'total_content': movies + animes + series,
    }


# ── Selector queries ─────────────────────────────────────────────────────

def get_all_selectors():
    """Get all selectors grouped by category."""
    result = {}
    for d in _selectors_col().find():
        result.setdefault(d['category'], []).append({'id': d['_id'], 'value': d['value']})
    for cat in result:
        result[cat].sort(key=lambda x: x['value'])
    return result


def get_selectors_by_category(category):
    """Get selectors for a specific category."""
    items = [{'id': d['_id'], 'value': d['value']} for d in _selectors_col().find({'category': category})]
    items.sort(key=lambda x: x['value'])
    return items


def search_cast_selectors(query_str):
    """Search cast selectors by name (case-insensitive substring match)."""
    results = []
    q = query_str.lower().strip()
    for d in _selectors_col().find({'category': 'cast'}):
        try:
            m = json.loads(d['value'])
            if not q or q in m.get('name', '').lower():
                results.append({'id': d['_id'], 'name': m.get('name', ''), 'image': m.get('image', '')})
        except Exception:
            pass
    results.sort(key=lambda x: x['name'])
    return results[:20]


def add_selector(category, value):
    """Add a new selector. Returns (doc_id, created)."""
    existing = _selectors_col().find_one({'category': category, 'value': value}, {'_id': 1})
    if existing:
        return existing['_id'], False
    sel_id = _new_id()
    _selectors_col().insert_one({'_id': sel_id, 'category': category, 'value': value})
    return sel_id, True


def update_selector(selector_id, value):
    """Update a selector's value."""
    _selectors_col().update_one({'_id': selector_id}, {'$set': {'value': value}})


def delete_selector(selector_id):
    """Delete a selector."""
    _selectors_col().delete_one({'_id': selector_id})


if __name__ == '__main__':
    print("[DB] Initializing MongoDB...")
    init_db()
    print("[DB] Done.")
