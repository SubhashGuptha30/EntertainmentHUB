"""
database.py — Firestore backend for Entertainment Hub (GCP deployment)
Replaces the SQLite backend with Google Cloud Firestore (NoSQL).

Collections:
  - users      : {username, email, password, gender, age, profile_pic, is_admin, created_at}
  - content    : {slug, type, title, h_image, v_image, rating, status, description,
                  tags, cast, watchOptions, video_url, genreDisplay, sections, franchise}
                  Document ID = "{type}_{slug}" (natural composite key)
  - selectors  : {category, value}
"""

import json
import os
import secrets
import hashlib
from datetime import datetime
from google.cloud import firestore
import bcrypt

# Firestore client — auto-authenticates on Cloud Run via service account
_db_client = None


def get_db():
    """Return a Firestore client (lazily initialised, reused)."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client()
    return _db_client


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
        _users_col().document(user_id).update({'password': new_hash})
        return new_hash
    return current_hash


# ── Collection references ────────────────────────────────────────────────

def _users_col():
    return get_db().collection('users')

def _content_col():
    return get_db().collection('content')

def _selectors_col():
    return get_db().collection('selectors')


# ── Content helpers ──────────────────────────────────────────────────────

def content_doc_id(ctype, slug):
    """Generate a deterministic document ID for content: '{type}_{slug}'."""
    return f"{ctype}_{slug}"


def content_to_dict(doc):
    """Convert a Firestore content document to the frontend-expected dict."""
    if not doc.exists:
        return None
    d = doc.to_dict()
    d['id'] = doc.id  # preserve the Firestore doc ID for admin operations
    return d


def user_to_dict(doc):
    """Convert a Firestore user document to dict."""
    if not doc.exists:
        return None
    d = doc.to_dict()
    d['id'] = doc.id
    # Convert Firestore Timestamp to ISO string for JSON serialisation
    if isinstance(d.get('created_at'), datetime):
        d['created_at'] = d['created_at'].isoformat()
    return d


# ── Init / Seed ──────────────────────────────────────────────────────────

def init_db():
    """Seed default data into Firestore if collections are empty.
    Safe to call on every startup — idempotent."""
    db = get_db()

    # ── Seed admin user ──────────────────────────────────────────────────
    admin_query = _users_col().where('username', '==', 'admin').limit(1).get()
    if not list(admin_query):
        admin_pw = os.environ.get('ADMIN_PASSWORD', '')
        if not admin_pw:
            admin_pw = secrets.token_urlsafe(16)
            print(f'[DB] Generated admin password (save this!): {admin_pw}')
        _users_col().add({
            'username':    'admin',
            'email':       'admin@entertainmenthub.com',
            'password':    hash_password(admin_pw),
            'gender':      'Other',
            'age':         0,
            'profile_pic': '/static/images/user.png',
            'is_admin':    True,
            'created_at':  firestore.SERVER_TIMESTAMP,
        })
        print('[DB] Admin user created')

    # ── Seed default selectors ───────────────────────────────────────────
    existing_selectors = list(_selectors_col().limit(1).get())
    if not existing_selectors:
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
    batch = get_db().batch()
    for category, values in defaults.items():
        for val in values:
            if category == 'watch_options':
                db_val = json.dumps({'name': val, 'logo': ''}, ensure_ascii=False)
            else:
                db_val = val
            doc_ref = _selectors_col().document()  # auto-ID
            batch.set(doc_ref, {'category': category, 'value': db_val})
    batch.commit()


# ── User queries ─────────────────────────────────────────────────────────

def find_user_by_username(username, admin_only=False):
    """Find a user by username. Returns (doc_id, user_dict) or (None, None)."""
    query = _users_col().where('username', '==', username)
    if admin_only:
        query = query.where('is_admin', '==', True)
    else:
        query = query.where('is_admin', '==', False)
    results = list(query.limit(1).get())
    if results:
        doc = results[0]
        d = doc.to_dict()
        d['id'] = doc.id
        return doc.id, d
    return None, None


def find_user_by_username_or_email(username, email):
    """Check if username or email already exists (for registration)."""
    q1 = list(_users_col().where('username', '==', username).limit(1).get())
    if q1:
        return True
    q2 = list(_users_col().where('email', '==', email).limit(1).get())
    if q2:
        return True
    return False


def create_user(username, email, password, gender, age):
    """Create a new regular user. Returns the doc ID."""
    _, doc_ref = _users_col().add({
        'username':    username,
        'email':       email,
        'password':    hash_password(password),
        'gender':      gender,
        'age':         age,
        'profile_pic': '/images/user.png',
        'is_admin':    False,
        'created_at':  firestore.SERVER_TIMESTAMP,
    })
    return doc_ref.id


def get_user_by_id(user_id):
    """Fetch a single user by Firestore doc ID."""
    doc = _users_col().document(user_id).get()
    return user_to_dict(doc)


def update_user(user_id, data):
    """Update user fields. `data` is a dict of fields to update."""
    _users_col().document(user_id).update(data)


def list_users(admin=False):
    """List all non-admin users (for admin dashboard)."""
    query = _users_col().where('is_admin', '==', admin)
    docs = query.get()
    users = []
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        if isinstance(d.get('created_at'), datetime):
            d['created_at'] = d['created_at'].isoformat()
        # Strip password from listing
        d.pop('password', None)
        users.append(d)
    # Sort by created_at descending in Python (avoids needing a composite index)
    users.sort(key=lambda u: u.get('created_at', ''), reverse=True)
    return users


def delete_user(user_id):
    """Delete a non-admin user."""
    doc = _users_col().document(user_id).get()
    if doc.exists and not doc.to_dict().get('is_admin', False):
        _users_col().document(user_id).delete()
        return True
    return False


# ── Content queries ──────────────────────────────────────────────────────

def get_all_content():
    """Fetch all content, grouped by type."""
    result = {'movies': {}, 'animes': {}, 'webSeries': {}}
    for doc in _content_col().stream():
        d = doc.to_dict()
        d['id'] = doc.id
        ctype = d.get('type')
        slug  = d.get('slug')
        if ctype in result and slug:
            result[ctype][slug] = d
    return result


def get_content_by_type(ctype):
    """Fetch all content of a specific type."""
    result = {}
    docs = _content_col().where('type', '==', ctype).get()
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        result[d['slug']] = d
    return result


def get_single_content(ctype, slug):
    """Fetch a single content item by type + slug."""
    doc_id = content_doc_id(ctype, slug)
    doc = _content_col().document(doc_id).get()
    return content_to_dict(doc)


def add_content(data):
    """Add a new content item. Returns slug or raises ValueError on duplicate."""
    slug = data['slug']
    ctype = data['type']
    doc_id = content_doc_id(ctype, slug)

    # Check for duplicate
    existing = _content_col().document(doc_id).get()
    if existing.exists:
        raise ValueError('Slug already exists for this type')

    _content_col().document(doc_id).set(data)
    return slug


def update_content(content_id, data):
    """Update a content item by its Firestore document ID."""
    doc = _content_col().document(content_id).get()
    if not doc.exists:
        return None
    _content_col().document(content_id).update(data)
    return doc.to_dict()


def delete_content(content_id):
    """Delete a content item by its Firestore document ID."""
    _content_col().document(content_id).delete()


def get_content_list(ctype=None):
    """List content for admin panel. Optional type filter."""
    if ctype:
        docs = _content_col().where('type', '==', ctype).get()
    else:
        docs = _content_col().get()
    items = []
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        items.append(d)
    # Sort: by type, then newest-first (no created_at on content, so sort by title)
    items.sort(key=lambda x: (x.get('type', ''), x.get('title', '')))
    return items


def get_content_stats():
    """Get content counts for admin dashboard."""
    from google.cloud.firestore_v1.aggregation import AggregationQuery

    db = get_db()
    col = _content_col()

    def _count(query):
        agg = AggregationQuery(query)
        agg.count(alias='total')
        results = agg.get()
        for r in results:
            for ar in r:
                return ar.value
        return 0

    movies = _count(col.where('type', '==', 'movies'))
    animes = _count(col.where('type', '==', 'animes'))
    series = _count(col.where('type', '==', 'webSeries'))
    users  = _count(_users_col().where('is_admin', '==', False))

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
    for doc in _selectors_col().stream():
        d = doc.to_dict()
        cat = d['category']
        if cat not in result:
            result[cat] = []
        result[cat].append({'id': doc.id, 'value': d['value']})
    # Sort values within each category
    for cat in result:
        result[cat].sort(key=lambda x: x['value'])
    return result


def get_selectors_by_category(category):
    """Get selectors for a specific category."""
    docs = _selectors_col().where('category', '==', category).get()
    items = [{'id': doc.id, 'value': doc.to_dict()['value']} for doc in docs]
    items.sort(key=lambda x: x['value'])
    return items


def search_cast_selectors(query_str):
    """Search cast selectors by name (case-insensitive substring match)."""
    docs = _selectors_col().where('category', '==', 'cast').get()
    results = []
    q = query_str.lower().strip()
    for doc in docs:
        try:
            m = json.loads(doc.to_dict()['value'])
            if not q or q in m.get('name', '').lower():
                results.append({
                    'id':    doc.id,
                    'name':  m.get('name', ''),
                    'image': m.get('image', ''),
                })
        except Exception:
            pass
    results.sort(key=lambda x: x['name'])
    return results[:20]


def add_selector(category, value):
    """Add a new selector. Returns (doc_id, created)."""
    # Check for duplicate
    existing = list(
        _selectors_col()
        .where('category', '==', category)
        .where('value', '==', value)
        .limit(1).get()
    )
    if existing:
        return existing[0].id, False
    _, doc_ref = _selectors_col().add({'category': category, 'value': value})
    return doc_ref.id, True


def update_selector(selector_id, value):
    """Update a selector's value."""
    _selectors_col().document(selector_id).update({'value': value})


def delete_selector(selector_id):
    """Delete a selector."""
    _selectors_col().document(selector_id).delete()


if __name__ == '__main__':
    print("[DB] Initializing Firestore...")
    init_db()
    print("[DB] Done.")
