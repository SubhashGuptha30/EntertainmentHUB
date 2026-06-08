"""
app.py — Entertainment Hub | Flask Backend (GCP Cloud Run version)
Runs on Cloud Run with Firestore + Cloud Storage.

Local dev:  python app.py
Cloud Run:  gunicorn --bind :$PORT app:app
"""

import os
from datetime import timedelta
import uuid
from functools import wraps
from flask import (Flask, request, jsonify, session, send_from_directory)

# Database layer (Firestore)
import database as db

# Cloud Storage for file uploads
from google.cloud import storage as gcs

# App Setup
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR     = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR  = os.path.join(BASE_DIR, 'templates')

# Cloud Storage bucket name for uploaded images (set via env var)
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET', '')

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
# SECRET_KEY from environment (set via Secret Manager on Cloud Run)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=15)

# Initialise DB on startup
with app.app_context():
    db.init_db()


# ── Cloud Storage helper ────────────────────────────────────────────────

def _upload_to_gcs(file_obj, folder, filename):
    """Upload a file to Cloud Storage and return its public URL."""
    client = gcs.Client()
    bucket = client.bucket(UPLOAD_BUCKET)
    blob_path = f"images/{folder}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_file(file_obj, content_type=file_obj.content_type)
    return blob.public_url


# ── Auth Decorators ─────────────────────────────────────────────────────

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


# ── HTML Page Serving (from templates/) ─────────────────────────────────

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


# ── FILE UPLOAD API ─────────────────────────────────────────────────────

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
    # Each upload type has its own directory under images/
    allowed_folders = {'cast', 'vertical', 'horizontal', 'watch', 'franchise'}
    folder = request.args.get('folder', '').strip()
    if folder not in allowed_folders:
        return jsonify({'error': f'Unknown folder "{folder}". Use one of: {sorted(allowed_folders)}'}), 400

    filename = str(uuid.uuid4()) + ext

    # Upload to Cloud Storage if bucket is configured, otherwise fall back to local
    if UPLOAD_BUCKET:
        public_url = _upload_to_gcs(file, folder, filename)
        return jsonify({'path': public_url})
    else:
        # Local fallback (for development without GCS)
        save_dir = os.path.join(BASE_DIR, 'static', 'images', folder)
        os.makedirs(save_dir, exist_ok=True)
        file.save(os.path.join(save_dir, filename))
        return jsonify({'path': f'/static/images/{folder}/{filename}'})


# ── SELECTORS API (manages dropdown options) ────────────────────────────

@app.route('/api/admin/selectors', methods=['GET'])
@admin_required
def get_all_selectors():
    return jsonify(db.get_all_selectors())


@app.route('/api/admin/selectors/<category>', methods=['GET'])
@admin_required
def get_selectors_by_category(category):
    return jsonify(db.get_selectors_by_category(category))


@app.route('/api/admin/selectors/cast/search', methods=['GET'])
@admin_required
def search_cast():
    q = request.args.get('q', '')
    return jsonify(db.search_cast_selectors(q))


@app.route('/api/admin/selectors', methods=['POST'])
@admin_required
def add_selector():
    data = request.get_json(silent=True) or {}
    category = (data.get('category') or '').strip()
    value    = (data.get('value') or '').strip()
    if not category or not value:
        return jsonify({'error': 'category and value are required'}), 400

    doc_id, created = db.add_selector(category, value)
    if created:
        return jsonify({'id': doc_id, 'message': 'Selector added'}), 201
    return jsonify({'id': doc_id, 'message': 'Selector already exists'}), 200


@app.route('/api/admin/selectors/<selector_id>', methods=['DELETE'])
@admin_required
def delete_selector(selector_id):
    db.delete_selector(selector_id)
    return jsonify({'message': 'Selector deleted'})


@app.route('/api/admin/selectors/<selector_id>', methods=['PUT'])
@admin_required
def update_selector(selector_id):
    data  = request.get_json(silent=True) or {}
    value = (data.get('value') or '').strip()
    if not value:
        return jsonify({'error': 'value is required'}), 400
    db.update_selector(selector_id, value)
    return jsonify({'message': 'Selector updated'})


# ── USER AUTH API ───────────────────────────────────────────────────────

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

    if db.find_user_by_username_or_email(username, email):
        return jsonify({'error': 'Username or email already exists'}), 409

    doc_id = db.create_user(username, email, password, gender, age)
    return jsonify({'message': 'Registration successful'}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user_id, user = db.find_user_by_username(username, admin_only=False)
    if not user or user['password'] != db.hash_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Remember Me: set session.permanent so cookie survives browser close
    remember = data.get('remember_me', False)
    session.permanent = bool(remember)

    session['user_id']  = user_id
    session['username'] = user['username']
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id':          user_id,
            'username':    user['username'],
            'email':       user['email'],
            'gender':      user.get('gender', ''),
            'age':         user.get('age', 0),
            'profile_pic': user.get('profile_pic', ''),
        }
    })


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': 'Logged out'})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_me():
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    # Strip sensitive fields
    user.pop('password', None)
    user.pop('is_admin', None)
    return jsonify(user)


@app.route('/api/auth/me', methods=['PUT'])
@login_required
def update_me():
    data = request.get_json(silent=True) or {}
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    username    = (data.get('username') or user['username'] or '').strip()
    email       = (data.get('email') or user['email'] or '').strip()
    gender      = data.get('gender', user.get('gender', ''))
    age         = data.get('age', user.get('age', 0))
    profile_pic = data.get('profile_pic', user.get('profile_pic', ''))

    new_password     = data.get('new_password')
    current_password = data.get('current_password')
    if new_password:
        if not current_password or user['password'] != db.hash_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        hashed = db.hash_password(new_password)
    else:
        hashed = user['password']

    db.update_user(session['user_id'], {
        'username':    username,
        'email':       email,
        'gender':      gender,
        'age':         age,
        'profile_pic': profile_pic,
        'password':    hashed,
    })
    session['username'] = username
    return jsonify({'message': 'Profile updated'})


# ── PUBLIC SELECTORS (franchise list, watch logos for frontend) ─────────

@app.route('/api/selectors/franchises', methods=['GET'])
def public_franchises():
    """Return franchise selectors for the public franchises page."""
    items = db.get_selectors_by_category('franchises')
    result = []
    for item in items:
        try:
            m = __import__('json').loads(item['value'])
        except Exception:
            m = {'title': item['value']}
        result.append({
            'title': m.get('title', item['value']),
            'image': m.get('image', ''),
            'description': m.get('description', ''),
        })
    result.sort(key=lambda x: x['title'])
    return jsonify(result)


@app.route('/api/selectors/watch_options', methods=['GET'])
def public_watch_options():
    """Return watch option selectors (name + logo) for the play page."""
    items = db.get_selectors_by_category('watch_options')
    result = {}
    for item in items:
        try:
            m = __import__('json').loads(item['value'])
        except Exception:
            m = {'name': item['value']}
        name = m.get('name', item['value'])
        result[name.lower().replace(' ', '')] = {
            'name': name,
            'logo': m.get('logo', ''),
        }
    return jsonify(result)


# ── CONTENT API (User-facing) ──────────────────────────────────────────

@app.route('/api/content', methods=['GET'])
def get_all_content():
    return jsonify(db.get_all_content())


@app.route('/api/content/<ctype>', methods=['GET'])
def get_content_by_type(ctype):
    valid = ('movies', 'animes', 'webSeries')
    if ctype not in valid:
        return jsonify({'error': 'Invalid type'}), 400
    return jsonify(db.get_content_by_type(ctype))


@app.route('/api/content/<ctype>/<slug>', methods=['GET'])
def get_single_item(ctype, slug):
    item = db.get_single_content(ctype, slug)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(item)


# ── ADMIN AUTH API ──────────────────────────────────────────────────────

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    user_id, admin = db.find_user_by_username(username, admin_only=True)
    if not admin or admin['password'] != db.hash_password(password):
        return jsonify({'error': 'Invalid admin credentials'}), 401

    session['admin_id']       = user_id
    session['admin_username'] = admin['username']
    return jsonify({'message': 'Admin login successful', 'admin': admin['username']})


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


# ── ADMIN DASHBOARD API ────────────────────────────────────────────────

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    return jsonify(db.get_content_stats())


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    return jsonify(db.list_users(admin=False))


@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    db.delete_user(user_id)
    return jsonify({'message': 'User deleted'})


@app.route('/api/admin/content', methods=['GET'])
@admin_required
def admin_get_content():
    ctype = request.args.get('type')
    return jsonify(db.get_content_list(ctype))


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

    content_data = {
        'slug':         slug,
        'type':         data['type'],
        'title':        data.get('title', ''),
        'h-image':      data.get('h_image', data.get('h-image', '')),
        'v-image':      data.get('v_image', data.get('v-image', '')),
        'rating':       str(data.get('rating', 'Not Rated')),
        'Status':       status,
        'description':  data.get('description', ''),
        'tags':         data.get('tags', []),
        'cast':         data.get('cast', []),
        'watchOptions': data.get('watchOptions', []),
        'videoUrl':     data.get('video_url', data.get('videoUrl', '')),
        'genreDisplay': data.get('genre_display', data.get('genreDisplay', '')),
        'sections':     sections,
        'franchise':    data.get('franchise', ''),
        'language':     data.get('language', ''),
    }

    try:
        slug = db.add_content(content_data)
        return jsonify({'message': 'Content added', 'slug': slug}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 409


@app.route('/api/admin/content/<content_id>', methods=['PUT'])
@admin_required
def admin_update_content(content_id):
    data = request.get_json(silent=True) or {}

    # Fetch existing document
    doc = db._content_col().document(content_id).get()
    if not doc.exists:
        return jsonify({'error': 'Not found'}), 404
    existing = doc.to_dict()

    # Re-derive sections from the (possibly new) status
    new_status = data.get('status', data.get('Status', existing.get('Status', 'Released')))
    new_sections = list(STATUS_SECTIONS.get(new_status, ['popular', 'most-watched']))
    if data.get('feature_hero') or 'head' in existing.get('sections', []):
        if 'head' not in new_sections:
            new_sections = ['head'] + new_sections

    update_data = {
        'title':        data.get('title', existing.get('title', '')),
        'h-image':      data.get('h_image', data.get('h-image', existing.get('h-image', ''))),
        'v-image':      data.get('v_image', data.get('v-image', existing.get('v-image', ''))),
        'rating':       str(data.get('rating', existing.get('rating', 'Not Rated'))),
        'Status':       new_status,
        'description':  data.get('description', existing.get('description', '')),
        'tags':         data.get('tags', existing.get('tags', [])),
        'cast':         data.get('cast', existing.get('cast', [])),
        'watchOptions': data.get('watchOptions', existing.get('watchOptions', [])),
        'videoUrl':     data.get('video_url', data.get('videoUrl', existing.get('videoUrl', ''))),
        'genreDisplay': data.get('genre_display', data.get('genreDisplay', existing.get('genreDisplay', ''))),
        'sections':     new_sections,
        'type':         data.get('type', existing.get('type', 'movies')),
        'franchise':    data.get('franchise', existing.get('franchise', '')),
        'language':     data.get('language', existing.get('language', '')),
    }

    db._content_col().document(content_id).update(update_data)
    return jsonify({'message': 'Content updated'})


@app.route('/api/admin/content/<content_id>', methods=['DELETE'])
@admin_required
def admin_delete_content(content_id):
    db.delete_content(content_id)
    return jsonify({'message': 'Content deleted'})

if __name__ == '__main__':
    print("=" * 60)
    print("  Entertainment Hub -- Full Stack Server")
    print("  http://localhost:5000")
    print("  Admin Panel: http://localhost:5000/admin/index.html")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
