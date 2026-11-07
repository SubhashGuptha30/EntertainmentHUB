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
import re
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

def _franchises_col():
    return get_db()['franchises']

def _progress_col():
    return get_db()['progress']


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

    _progress_col().create_index('user_id')
    if not _franchises_col().find_one():
        n = migrate_selector_franchises()
        if n:
            print(f'[DB] Migrated {n} franchises from selectors')


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


def username_or_email_taken(username, email, exclude_id=None):
    """True if another user already has this username or email."""
    q = {'$or': [{'username': username}, {'email': email}]}
    if exclude_id:
        q['_id'] = {'$ne': exclude_id}
    return _users_col().find_one(q, {'_id': 1}) is not None


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


def get_content_by_id(content_id):
    """Fetch a single content item by its document ID."""
    return _out(_content_col().find_one({'_id': content_id}))


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


# ── Franchise queries ────────────────────────────────────────────────────
# A franchise owns an ordered list of entries. List order = release order;
# `chrono` gives the in-universe position. One content item can appear in
# several entries (e.g. a series split into seasons) or several franchises.

FRANCHISE_KINDS = ('universe', 'saga', 'anime', 'trilogy', 'duology')
CANON_VALUES    = ('canon', 'filler', 'optional', 'noncanon')


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')


def entry_key(entry):
    """Stable progress key: same title+label counts as watched in every franchise."""
    return f"{entry['content_id']}#{entry.get('label', '')}"


def _int_or_none(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def clean_franchise(data):
    """Validate/normalise franchise input from the admin API. Raises ValueError."""
    if not isinstance(data, dict):
        raise ValueError('expected a JSON object')
    if not isinstance(data.get('entries') or [], list):
        raise ValueError('entries must be a list')
    title = str(data.get('title') or '').strip()[:200]
    if not title:
        raise ValueError('title is required')
    kind = data.get('kind') or 'saga'
    if kind not in FRANCHISE_KINDS:
        raise ValueError(f'kind must be one of {FRANCHISE_KINDS}')
    entries = []
    for e in data.get('entries') or []:
        if not isinstance(e, dict):
            continue
        cid = str(e.get('content_id') or '').strip()
        if not cid:
            continue
        canon = e.get('canon') or 'canon'
        entries.append({
            'content_id': cid,
            'label':      str(e.get('label') or '').strip(),
            'year':       _int_or_none(e.get('year')),
            'phase':      str(e.get('phase') or '').strip(),
            'chrono':     _int_or_none(e.get('chrono')),
            'canon':      canon if canon in CANON_VALUES else 'canon',
            'essential':  bool(e.get('essential', True)),
            'note':       str(e.get('note') or '').strip(),
            'runtime_min': _int_or_none(e.get('runtime_min')),
        })
    return {
        'title':       title,
        'kind':        kind,
        'status':      'complete' if data.get('status') == 'complete' else 'ongoing',
        'description': str(data.get('description') or '').strip(),
        'image':       str(data.get('image') or '').strip(),
        'banner':      str(data.get('banner') or '').strip(),
        'featured':    bool(data.get('featured')),
        'entries':     entries,
    }


def _content_map(ids):
    return {d['_id']: _out(d) for d in _content_col().find({'_id': {'$in': list(set(ids))}})}


def _entry_minutes(entry, content, entries):
    """Entry runtime: its own value, else the title's total if the title appears once."""
    if entry.get('runtime_min'):
        return entry['runtime_min']
    if content and sum(e['content_id'] == entry['content_id'] for e in entries) == 1:
        return _int_or_none(content.get('runtime_min'))
    return None


def _runtime_totals(entries, contents):
    mins = [_entry_minutes(e, contents.get(e['content_id']), entries) for e in entries]
    known = [m for m in mins if m]
    return sum(known), bool(entries) and len(known) == len(mins)


def list_franchises(kind=None):
    """Franchise summaries (no entries) with per-type counts for cards."""
    if isinstance(kind, (list, tuple)):
        query = {'kind': {'$in': list(kind)}}
    else:
        query = {'kind': kind} if kind else {}
    docs = list(_franchises_col().find(query))
    contents = _content_map(e['content_id'] for d in docs for e in d.get('entries', []))
    result = []
    for d in docs:
        entries = [e for e in d.get('entries', []) if e['content_id'] in contents]
        counts = {'movies': 0, 'webSeries': 0, 'animes': 0}
        for e in entries:
            ctype = contents[e['content_id']].get('type')
            if ctype in counts:
                counts[ctype] += 1
        f = _out(d)
        f.pop('entries', None)
        f['slug'] = f['id']
        f['entry_count'] = len(entries)
        f['counts'] = counts
        f['total_minutes'], f['runtime_complete'] = _runtime_totals(entries, contents)
        years = [e.get('year') or contents[e['content_id']].get('year') for e in entries]
        years = [y for y in years if y]
        f['years'] = [min(years), max(years)] if years else None
        f['cover'] = next((contents[e['content_id']].get('h-image') for e in entries
                           if contents[e['content_id']].get('h-image')), '')
        result.append(f)
    result.sort(key=lambda f: (not f.get('featured'), f['title'].lower()))
    return result


def get_franchise(slug):
    """Franchise with entries resolved to content (dangling entries dropped)."""
    d = _franchises_col().find_one({'_id': slug})
    if not d:
        return None
    f = _out(d)
    f['slug'] = f['id']
    contents = _content_map(e['content_id'] for e in f.get('entries', []))
    raw = [e for e in f.get('entries', []) if e['content_id'] in contents]
    f['entries'] = [
        {**e, 'release': i, 'chrono': e.get('chrono') or i, 'key': entry_key(e),
         'runtime_min': _entry_minutes(e, contents[e['content_id']], raw),
         'year': e.get('year') or contents[e['content_id']].get('year'),
         'content': contents[e['content_id']]}
        for i, e in enumerate(raw, start=1)
    ]
    f['total_minutes'], f['runtime_complete'] = _runtime_totals(raw, contents)
    return f


def get_franchise_raw(slug):
    """Franchise as stored (for the admin editor)."""
    d = _out(_franchises_col().find_one({'_id': slug}))
    if d:
        d['slug'] = d['id']
    return d


def _entry_link(entry, contents):
    c = contents.get(entry['content_id']) if entry else None
    if not c:
        return None
    return {'title': c.get('title', ''), 'label': entry.get('label', ''),
            'type': c.get('type'), 'slug': c.get('slug')}


def franchises_for_content(content_id):
    """Franchises containing a title, with its position and the previous/next entries."""
    docs = list(_franchises_col().find({'entries.content_id': content_id}, {'title': 1, 'entries': 1}))
    contents = _content_map(e['content_id'] for d in docs for e in d['entries'])
    out = []
    for d in docs:
        entries = [e for e in d['entries'] if e['content_id'] in contents]
        idxs = [i for i, e in enumerate(entries) if e['content_id'] == content_id]
        if not idxs:
            continue
        first, last = idxs[0], idxs[-1]   # a series may span several season entries
        out.append({
            'slug': d['_id'], 'title': d['title'],
            'position': first + 1, 'total': len(entries),
            'prev': _entry_link(entries[first - 1] if first > 0 else None, contents),
            'next': _entry_link(entries[last + 1] if last + 1 < len(entries) else None, contents),
        })
    return out


def create_franchise(data, slug=None):
    doc = clean_franchise(data)
    slug = slugify(slug or doc['title'])
    if not slug:
        raise ValueError('title must contain letters or digits')
    if _franchises_col().find_one({'_id': slug}, {'_id': 1}):
        raise ValueError('A franchise with this slug already exists')
    _franchises_col().insert_one({**doc, '_id': slug})
    return slug


def update_franchise(slug, data):
    """Replace a franchise's fields. Returns False if it doesn't exist."""
    doc = clean_franchise(data)
    return _franchises_col().update_one({'_id': slug}, {'$set': doc}).matched_count > 0


def delete_franchise(slug):
    _franchises_col().delete_one({'_id': slug})


def migrate_selector_franchises():
    """One-time: build `franchises` from the old selector entries + content.franchise strings."""
    by_name = {}
    for c in _content_col().find({'franchise': {'$nin': [None, '']}}):
        by_name.setdefault(c['franchise'].strip().lower(), []).append(c)
    count = 0
    for sel in _selectors_col().find({'category': 'franchises'}):
        try:
            m = json.loads(sel['value'])
        except (ValueError, TypeError):
            m = {'title': sel['value']}
        title = (m.get('title') or '').strip()
        slug = slugify(title)
        if not slug or _franchises_col().find_one({'_id': slug}, {'_id': 1}):
            continue
        items = sorted(by_name.get(title.lower(), []), key=lambda c: c.get('title', ''))
        kind = 'anime' if items and all(c.get('type') == 'animes' for c in items) else 'saga'
        create_franchise({
            'title': title, 'kind': kind,
            'description': m.get('description', ''), 'image': m.get('image', ''),
            'entries': [{'content_id': c['_id']} for c in items],
        }, slug=slug)
        count += 1
    return count


# ── One & Done (finite stories) ──────────────────────────────────────────

COMPACT_KINDS = ('standalone', 'limited', 'duology', 'trilogy')
_FINISHED = ('Released', 'Top Rated', 'New Release', 'Completed')


def content_format(c):
    """'film' or 'series' — explicit field wins; legacy docs fall back to type."""
    return c.get('format') or ('film' if c.get('type') == 'movies' else 'series')


def compact_items(kind=None, max_minutes=None):
    """Standalone films, short finished series (≤3 seasons), duologies and trilogies."""
    items = []
    if kind in (None, 'duology', 'trilogy'):
        for f in list_franchises([kind] if kind else ['duology', 'trilogy']):
            items.append({'kind': f['kind'], 'title': f['title'], 'slug': f['slug'],
                          'href': f"/franchise/{f['slug']}", 'image': f.get('image') or f.get('cover'),
                          'runtime_min': f['total_minutes'] if f['runtime_complete'] else None,
                          'year': (f.get('years') or [None])[0], 'count': f['entry_count'],
                          'description': f.get('description', '')})
    if kind in (None, 'standalone', 'limited'):
        in_franchise = set(_franchises_col().distinct('entries.content_id'))
        for d in _content_col().find({'_id': {'$nin': list(in_franchise)}}):
            c = _out(d)
            if content_format(c) == 'film':
                k = 'standalone'
            elif 1 <= (_int_or_none(c.get('seasons')) or 0) <= 3 and c.get('Status') in _FINISHED:
                k = 'limited'
            else:
                continue
            if kind and k != kind:
                continue
            items.append({'kind': k, 'title': c.get('title', ''), 'type': c.get('type'),
                          'href': f"/play?type={c.get('type')}&slug={c.get('slug')}",
                          'image': c.get('v-image') or c.get('h-image') or '',
                          'runtime_min': _int_or_none(c.get('runtime_min')),
                          'year': _int_or_none(c.get('year')), 'seasons': _int_or_none(c.get('seasons')),
                          'tags': c.get('tags', []), 'description': c.get('description', '')})
    if max_minutes:
        items = [i for i in items if i['runtime_min'] and i['runtime_min'] <= max_minutes]
    items.sort(key=lambda i: (i['runtime_min'] is None, i['runtime_min'] or 0, i['title'].lower()))
    return items


# ── Watch progress ───────────────────────────────────────────────────────

def get_progress(user_id):
    return [d['key'] for d in _progress_col().find({'user_id': user_id}, {'key': 1})]


def continue_watching(user_id, limit=12):
    """Franchises the user has started but not finished, most recently active first."""
    watched = {d['key']: d['watched_at'] for d in _progress_col().find({'user_id': user_id})}
    if not watched:
        return []
    cids = {k.split('#', 1)[0] for k in watched}
    docs = list(_franchises_col().find({'entries.content_id': {'$in': list(cids)}}))
    contents = _content_map(e['content_id'] for d in docs for e in d['entries'])
    out = []
    for d in docs:
        entries = [e for e in d['entries'] if e['content_id'] in contents]
        done = [watched[entry_key(e)] for e in entries if entry_key(e) in watched]
        if not done or len(done) == len(entries):
            continue
        nxt = next(e for e in entries if entry_key(e) not in watched)
        c = contents[nxt['content_id']]
        out.append({'slug': d['_id'], 'title': d['title'], 'kind': d.get('kind'),
                    'done': len(done), 'total': len(entries), 'last': max(done),
                    'image': c.get('h-image') or d.get('image') or '',
                    'next': _entry_link(nxt, contents)})
    out.sort(key=lambda x: x['last'], reverse=True)
    for x in out:
        x.pop('last')
    return out[:limit]


def set_progress(user_id, key, watched):
    _id = f'{user_id}|{key}'
    if watched:
        _progress_col().update_one({'_id': _id},
                                   {'$set': {'user_id': user_id, 'key': key, 'watched_at': _now()}},
                                   upsert=True)
    else:
        _progress_col().delete_one({'_id': _id})


if __name__ == '__main__':
    print("[DB] Initializing MongoDB...")
    init_db()
    print("[DB] Done.")
