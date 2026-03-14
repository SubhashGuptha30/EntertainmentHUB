"""
app.py — Entertainment Hub | Flask Backend
Run: python app.py
Access: http://localhost:5000
"""

import os
import json
import uuid
from functools import wraps
from flask import (Flask, request, jsonify, session,
                   send_from_directory)
from database import init_db, get_db, hash_password, row_to_dict

# ── App Setup ─────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR     = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR  = os.path.join(BASE_DIR, 'templates')

# Status → sections mapping (admin no longer needs to set sections manually)
STATUS_SECTIONS = {
    'Released':    ['new-releases', 'popular', 'most-watched'],
    'New Release': ['new-releases', 'popular'],
    'Top Rated':   ['top-rated', 'popular'],
    'Coming Soon': ['coming-soon'],
    'Ongoing':     ['popular', 'most-watched'],
}

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    static_url_path='/static',   # Serve assets at /static/css/, /static/js/ etc.
)
app.secret_key = 'eh-secret-key-change-in-production-2024'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialise DB on startup
with app.app_context():
    init_db()


# ── Auth Decorators ───────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


# ── HTML Page Serving (from templates/) ──────────────────────────────────────

@app.route('/images/<path:filename>')
def legacy_images(filename):
    """Backward-compat: serve old /images/ paths from the new static/images/ dir."""
    return send_from_directory(os.path.join(STATIC_DIR, 'images'), filename)


@app.route('/')
def index():
    return send_from_directory(TEMPLATES_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_page(filename):
    """
    Serve HTML pages from templates/ and static assets from static/.
    Flask automatically handles /css/, /js/, /images/ etc. via static_folder.
    This route only handles HTML page requests.
    """
    # Only intercept .html files (or clean URL paths)
    if '.' not in filename or filename.endswith('.html'):
        # Try exact match in templates/
        tmpl_path = os.path.join(TEMPLATES_DIR, filename)
        if os.path.isfile(tmpl_path):
            directory = os.path.dirname(tmpl_path)
            file_only = os.path.basename(tmpl_path)
            return send_from_directory(directory, file_only)

        # Try with .html extension appended
        if not filename.endswith('.html'):
            html_path = os.path.join(TEMPLATES_DIR, filename + '.html')
            if os.path.isfile(html_path):
                directory = os.path.dirname(html_path)
                file_only = os.path.basename(html_path)
                return send_from_directory(directory, file_only)

    # Note: We must check if 404.html exists first, to avoid sending error if missing.
    if os.path.isfile(os.path.join(TEMPLATES_DIR, '404.html')):
        return send_from_directory(TEMPLATES_DIR, '404.html'), 404
    return "404 Not Found", 404


# ══════════════════════════════════════════════════════════════════════════════
#  FILE UPLOAD API
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/admin/upload', methods=['POST'])
@admin_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
        return jsonify({'error': 'Unsupported file type. Use JPG, PNG, WebP, or GIF.'}), 400
    # Each upload type has its own directory under static/images/
    allowed_folders = {'cast', 'vertical', 'horizontal', 'watch', 'franchise'}
    folder = request.args.get('folder', '').strip()
    if folder not in allowed_folders:
        return jsonify({'error': f'Unknown folder "{folder}". Use one of: {sorted(allowed_folders)}'}), 400
    save_dir = os.path.join(BASE_DIR, 'static', 'images', folder)
    os.makedirs(save_dir, exist_ok=True)
    filename = str(uuid.uuid4()) + ext
    file.save(os.path.join(save_dir, filename))
    return jsonify({'path': f'/static/images/{folder}/{filename}'})


# ══════════════════════════════════════════════════════════════════════════════
#  SELECTORS API (manages dropdown options)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/admin/selectors', methods=['GET'])
@admin_required
def get_all_selectors():
    db = get_db()
    try:
        rows = db.execute(
            'SELECT id, category, value FROM selectors ORDER BY category, value'
        ).fetchall()
        result = {}
        for r in rows:
            cat = r['category']
            if cat not in result:
                result[cat] = []
            result[cat].append({'id': r['id'], 'value': r['value']})
        return jsonify(result)
    finally:
        db.close()


@app.route('/api/admin/selectors/<category>', methods=['GET'])
@admin_required
def get_selectors_by_category(category):
    db = get_db()
    try:
        rows = db.execute(
            'SELECT id, value FROM selectors WHERE category=? ORDER BY value',
            (category,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()


@app.route('/api/admin/selectors/cast/search', methods=['GET'])
@admin_required
def search_cast():
    q = (request.args.get('q') or '').lower().strip()
    db = get_db()
    try:
        rows = db.execute(
            'SELECT id, value FROM selectors WHERE category=?', ('cast',)
        ).fetchall()
        results = []
        for r in rows:
            try:
                m = json.loads(r['value'])
                if not q or q in m.get('name', '').lower():
                    results.append({
                        'id': r['id'],
                        'name': m.get('name', ''),
                        'image': m.get('image', '')
                    })
            except Exception:
                pass
        results.sort(key=lambda x: x['name'])
        return jsonify(results[:20])
    finally:
        db.close()


@app.route('/api/admin/selectors', methods=['POST'])
@admin_required
def add_selector():
    data = request.get_json(silent=True) or {}
    category = (data.get('category') or '').strip()
    value    = (data.get('value') or '').strip()
    if not category or not value:
        return jsonify({'error': 'category and value are required'}), 400
    db = get_db()
    try:
        db.execute(
            'INSERT OR IGNORE INTO selectors (category, value) VALUES (?, ?)',
            (category, value)
        )
        db.commit()
        row = db.execute(
            'SELECT id FROM selectors WHERE category=? AND value=?', (category, value)
        ).fetchone()
        return jsonify({'id': row['id'], 'message': 'Selector added'}), 201
    finally:
        db.close()


@app.route('/api/admin/selectors/<int:selector_id>', methods=['DELETE'])
@admin_required
def delete_selector(selector_id):
    db = get_db()
    try:
        db.execute('DELETE FROM selectors WHERE id=?', (selector_id,))
        db.commit()
        return jsonify({'message': 'Selector deleted'})
    finally:
        db.close()


@app.route('/api/admin/selectors/<int:selector_id>', methods=['PUT'])
@admin_required
def update_selector(selector_id):
    import sqlite3 as _sqlite3  # local import to catch IntegrityError
    data  = request.get_json(silent=True) or {}
    value = (data.get('value') or '').strip()
    if not value:
        return jsonify({'error': 'value is required'}), 400
    db = get_db()
    try:
        db.execute('UPDATE selectors SET value=? WHERE id=?', (value, selector_id))
        db.commit()
        return jsonify({'message': 'Selector updated'})
    except _sqlite3.IntegrityError:
        # New value already exists in this category → no-op, treat as success
        return jsonify({'message': 'Value already exists — no change needed'}), 200
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  USER AUTH API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email    = (data.get('email') or '').strip()
    password = data.get('password') or ''
    gender   = data.get('gender') or ''
    age      = data.get('age') or 0

    if not username or not email or not password:
        return jsonify({'error': 'Username, email and password are required'}), 400

    db = get_db()
    try:
        existing = db.execute(
            'SELECT id FROM users WHERE username=? OR email=?',
            (username, email)
        ).fetchone()
        if existing:
            return jsonify({'error': 'Username or email already exists'}), 409

        db.execute(
            '''INSERT INTO users (username, email, password, gender, age)
               VALUES (?, ?, ?, ?, ?)''',
            (username, email, hash_password(password), gender, age)
        )
        db.commit()
        return jsonify({'message': 'Registration successful'}), 201
    finally:
        db.close()


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    db = get_db()
    try:
        user = db.execute(
            'SELECT * FROM users WHERE username=? AND is_admin=0',
            (username,)
        ).fetchone()
        if not user or user['password'] != hash_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401

        session['user_id']  = user['id']
        session['username'] = user['username']
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'gender': user['gender'],
                'age': user['age'],
                'profile_pic': user['profile_pic'],
            }
        })
    finally:
        db.close()


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': 'Logged out'})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_me():
    db = get_db()
    try:
        user = db.execute(
            'SELECT id, username, email, gender, age, profile_pic, created_at FROM users WHERE id=?',
            (session['user_id'],)
        ).fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(dict(user))
    finally:
        db.close()


@app.route('/api/auth/me', methods=['PUT'])
@login_required
def update_me():
    data = request.get_json(silent=True) or {}
    db = get_db()
    try:
        user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        username    = (data.get('username') or user['username'] or '').strip()
        email       = (data.get('email') or user['email'] or '').strip()
        gender      = data.get('gender', user['gender'])
        age         = data.get('age', user['age'])
        profile_pic = data.get('profile_pic', user['profile_pic'])

        new_password     = data.get('new_password')
        current_password = data.get('current_password')
        if new_password:
            if not current_password or user['password'] != hash_password(current_password):
                return jsonify({'error': 'Current password is incorrect'}), 400
            hashed = hash_password(new_password)
        else:
            hashed = user['password']

        db.execute(
            '''UPDATE users SET username=?, email=?, gender=?, age=?,
               profile_pic=?, password=? WHERE id=?''',
            (username, email, gender, age, profile_pic, hashed, session['user_id'])
        )
        db.commit()
        session['username'] = username
        return jsonify({'message': 'Profile updated'})
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTENT API (User-facing)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/content', methods=['GET'])
def get_all_content():
    db = get_db()
    try:
        rows = db.execute('SELECT * FROM content').fetchall()
        result = {'movies': {}, 'animes': {}, 'webSeries': {}}
        for row in rows:
            d = row_to_dict(row)
            ctype = d.get('type')
            slug  = d.get('slug')
            if ctype in result and slug:
                result[ctype][slug] = d
        return jsonify(result)
    finally:
        db.close()


@app.route('/api/content/<ctype>', methods=['GET'])
def get_content_by_type(ctype):
    valid = ('movies', 'animes', 'webSeries')
    if ctype not in valid:
        return jsonify({'error': 'Invalid type'}), 400
    db = get_db()
    try:
        rows = db.execute('SELECT * FROM content WHERE type=?', (ctype,)).fetchall()
        result = {}
        for r in rows:
            d = row_to_dict(r)
            result[d['slug']] = d
        return jsonify(result)
    finally:
        db.close()


@app.route('/api/content/<ctype>/<slug>', methods=['GET'])
def get_single_item(ctype, slug):
    db = get_db()
    try:
        row = db.execute(
            'SELECT * FROM content WHERE type=? AND slug=?', (ctype, slug)
        ).fetchone()
        if not row:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(row_to_dict(row))
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN AUTH API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    db = get_db()
    try:
        admin = db.execute(
            'SELECT * FROM users WHERE username=? AND is_admin=1', (username,)
        ).fetchone()
        if not admin or admin['password'] != hash_password(password):
            return jsonify({'error': 'Invalid admin credentials'}), 401

        session['admin_id']       = admin['id']
        session['admin_username'] = admin['username']
        return jsonify({'message': 'Admin login successful', 'admin': admin['username']})
    finally:
        db.close()


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return jsonify({'message': 'Admin logged out'})


@app.route('/api/admin/check', methods=['GET'])
def admin_check():
    if 'admin_id' in session:
        return jsonify({'logged_in': True, 'admin': session.get('admin_username')})
    return jsonify({'logged_in': False}), 401


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    db = get_db()
    try:
        movies = db.execute("SELECT COUNT(*) FROM content WHERE type='movies'").fetchone()[0]
        animes = db.execute("SELECT COUNT(*) FROM content WHERE type='animes'").fetchone()[0]
        series = db.execute("SELECT COUNT(*) FROM content WHERE type='webSeries'").fetchone()[0]
        users  = db.execute("SELECT COUNT(*) FROM users WHERE is_admin=0").fetchone()[0]
        return jsonify({'movies': movies, 'animes': animes,
                        'series': series, 'users': users,
                        'total_content': movies + animes + series})
    finally:
        db.close()


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    db = get_db()
    try:
        rows = db.execute(
            'SELECT id, username, email, gender, age, profile_pic, created_at '
            'FROM users WHERE is_admin=0 ORDER BY created_at DESC'
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    db = get_db()
    try:
        db.execute('DELETE FROM users WHERE id=? AND is_admin=0', (user_id,))
        db.commit()
        return jsonify({'message': 'User deleted'})
    finally:
        db.close()


@app.route('/api/admin/content', methods=['GET'])
@admin_required
def admin_get_content():
    db = get_db()
    try:
        ctype = request.args.get('type')
        if ctype:
            rows = db.execute('SELECT * FROM content WHERE type=? ORDER BY id DESC', (ctype,)).fetchall()
        else:
            rows = db.execute('SELECT * FROM content ORDER BY type, id DESC').fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        db.close()


@app.route('/api/admin/content', methods=['POST'])
@admin_required
def admin_add_content():
    data = request.get_json(silent=True) or {}
    for field in ('slug', 'type', 'title'):
        if not data.get(field):
            return jsonify({'error': f'Field "{field}" is required'}), 400

    if data['type'] not in ('movies', 'animes', 'webSeries'):
        return jsonify({'error': 'type must be movies, animes, or webSeries'}), 400

    slug = data['slug'].strip().lower().replace(' ', '-')

    # Auto-derive sections from status; honour optional hero flag
    status   = data.get('status', 'Released')
    sections = list(STATUS_SECTIONS.get(status, ['popular', 'most-watched']))
    if data.get('feature_hero'):
        sections = ['head'] + sections

    db = get_db()
    try:
        if db.execute('SELECT id FROM content WHERE slug=? AND type=?',
                      (slug, data['type'])).fetchone():
            return jsonify({'error': 'Slug already exists for this type'}), 409

        db.execute('''
            INSERT INTO content
                (slug, type, title, h_image, v_image, rating, status, description,
                 tags, cast_data, watch_options, video_url, genre_display, sections, franchise)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            slug, data['type'],
            data.get('title', ''),
            data.get('h_image', data.get('h-image', '')),
            data.get('v_image', data.get('v-image', '')),
            str(data.get('rating', 'Not Rated')),
            status,
            data.get('description', ''),
            json.dumps(data.get('tags', []), ensure_ascii=False),
            json.dumps(data.get('cast', []), ensure_ascii=False),
            json.dumps(data.get('watchOptions', []), ensure_ascii=False),
            data.get('video_url', data.get('videoUrl', '')),
            data.get('genre_display', data.get('genreDisplay', '')),
            json.dumps(sections, ensure_ascii=False),
            data.get('franchise', ''),
        ))
        db.commit()
        return jsonify({'message': 'Content added', 'slug': slug}), 201
    finally:
        db.close()


@app.route('/api/admin/content/<int:content_id>', methods=['PUT'])
@admin_required
def admin_update_content(content_id):
    data = request.get_json(silent=True) or {}
    db = get_db()
    try:
        row = db.execute('SELECT * FROM content WHERE id=?', (content_id,)).fetchone()
        if not row:
            return jsonify({'error': 'Not found'}), 404
        existing = row_to_dict(row)

        def _j(key):
            """Return JSON string for a list field, preferring new data over existing."""
            val = data.get(key)
            if val is None:
                val = existing.get(key, [])
            return json.dumps(val, ensure_ascii=False)

        # Re-derive sections from the (possibly new) status
        new_status = data.get('status', data.get('Status', existing.get('Status', 'Released')))
        new_sections = list(STATUS_SECTIONS.get(new_status, ['popular', 'most-watched']))
        if data.get('feature_hero') or 'head' in existing.get('sections', []):
            if 'head' not in new_sections:
                new_sections = ['head'] + new_sections

        db.execute('''
            UPDATE content SET
                title=?, h_image=?, v_image=?, rating=?, status=?,
                description=?, tags=?, cast_data=?, watch_options=?,
                video_url=?, genre_display=?, sections=?, type=?, franchise=?
            WHERE id=?
        ''', (
            data.get('title', existing['title']),
            data.get('h_image', data.get('h-image', existing.get('h-image', ''))),
            data.get('v_image', data.get('v-image', existing.get('v-image', ''))),
            str(data.get('rating', existing.get('rating', 'Not Rated'))),
            new_status,
            data.get('description', existing.get('description', '')),
            _j('tags'),
            json.dumps(data.get('cast', existing.get('cast', [])), ensure_ascii=False),
            json.dumps(data.get('watchOptions', existing.get('watchOptions', [])), ensure_ascii=False),
            data.get('video_url', data.get('videoUrl', existing.get('videoUrl', ''))),
            data.get('genre_display', data.get('genreDisplay', existing.get('genreDisplay', ''))),
            json.dumps(new_sections, ensure_ascii=False),
            data.get('type', existing.get('type', 'movies')),
            data.get('franchise', existing.get('franchise', '')),
            content_id
        ))
        db.commit()
        return jsonify({'message': 'Content updated'})
    finally:
        db.close()


@app.route('/api/admin/content/<int:content_id>', methods=['DELETE'])
@admin_required
def admin_delete_content(content_id):
    db = get_db()
    try:
        db.execute('DELETE FROM content WHERE id=?', (content_id,))
        db.commit()
        return jsonify({'message': 'Content deleted'})
    finally:
        db.close()


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  Entertainment Hub -- Full Stack Server")
    print("  http://localhost:5000")
    print("  Admin Panel: http://localhost:5000/admin/index.html")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
