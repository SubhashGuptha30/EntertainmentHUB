"""Seed script + HTTP API tests (in-memory MongoDB). Run: python -m pytest -q"""
import os
import sys

import mongomock
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db  # noqa: E402

# app.py calls init_db() at import time, so point it at an in-memory DB first
db._db = mongomock.MongoClient()['import-time']
os.environ.setdefault('ADMIN_PASSWORD', 'admin-pw')
import app as appmod  # noqa: E402
from scripts import seed_franchises, seed_data  # noqa: E402

QUIET = dict(log=lambda *_: None)


@pytest.fixture(autouse=True)
def fresh_db(monkeypatch):
    monkeypatch.setattr(db, '_db', mongomock.MongoClient()['test'])
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin-pw')
    db.init_db()


@pytest.fixture
def client():
    appmod.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    appmod.limiter.enabled = False
    return appmod.app.test_client()


def _register_login(client, username='alice', email='alice@example.test', password='Passw0rd!'):
    r = client.post('/api/auth/register', json={'username': username, 'email': email,
                                                  'password': password, 'gender': 'F', 'age': 20})
    assert r.status_code == 201, r.json
    assert client.post('/api/auth/login', json={'username': username, 'password': password}).status_code == 200


# ── seed data ────────────────────────────────────────────────────────────

def test_seed_data_is_consistent():
    assert seed_franchises.validate() == []
    slugs = {f['slug'] for f in seed_data.FRANCHISES}
    assert {'marvel-cinematic-universe', 'middle-earth', 'despicable-me', 'hotel-transylvania',
            'fate', 'demon-slayer'} <= slugs


def test_seed_dry_run_writes_nothing():
    seed_franchises.seed(apply=False, **QUIET)
    assert db.list_franchises() == [] and db.get_content_stats()['total_content'] == 0


def test_seed_apply_is_idempotent_and_keeps_admin_data():
    # an admin already added Iron Man with a poster under a different slug, and an MCU card image
    db.add_content({'type': 'movies', 'slug': 'iron-man-2008', 'title': 'Iron Man', 'v-image': '/p.jpg'})
    db.create_franchise({'title': 'MCU', 'image': '/mcu.jpg'}, slug='marvel-cinematic-universe')

    seed_franchises.seed(apply=True, **QUIET)
    total = db.get_content_stats()['total_content']
    seed_franchises.seed(apply=True, **QUIET)                     # second run: no duplicates
    assert db.get_content_stats()['total_content'] == total

    mcu = db.get_franchise('marvel-cinematic-universe')
    assert mcu['image'] == '/mcu.jpg' and mcu['kind'] == 'universe'
    first = mcu['entries'][0]
    assert first['content_id'] == 'movies_iron-man-2008'          # reused, not duplicated
    assert first['content']['v-image'] == '/p.jpg' and first['content']['year'] == 2008  # gap filled

    chrono = sorted(mcu['entries'], key=lambda e: e['chrono'])
    assert chrono[0]['content']['title'] == 'Captain America: The First Avenger'

    ds = db.get_franchise('demon-slayer')
    assert [e['label'] for e in ds['entries'] if e['content']['title'].endswith('Yaiba')][0] == 'Season 1'
    assert len(db.compact_items('trilogy')) >= 3 and db.compact_items('limited')


def test_seed_prune_removes_false_franchises_only():
    db.create_franchise({'title': 'One Punch Man'})
    seed_franchises.seed(apply=True, prune=True, **QUIET)
    assert db.get_franchise('one-punch-man') is None and db.get_franchise('fate')


def test_seed_rejects_bad_chrono():
    bad = [seed_data.F('x', 'X', 'saga', 'complete', '', [seed_data.E('movies', 'A', 2000, 90)], chrono=['B'])]
    with pytest.raises(ValueError):
        seed_franchises.seed(franchises=bad, singles=[], **QUIET)


# ── API: behaviour ───────────────────────────────────────────────────────

def test_franchise_and_compact_endpoints(client):
    seed_franchises.seed(apply=True, **QUIET)
    assert client.get('/api/franchises?kind=anime').status_code == 200
    assert client.get('/api/franchises?kind=bogus').status_code == 400
    assert client.get('/api/franchises/fate').json['total_minutes'] > 0
    assert client.get('/api/franchises/nope').status_code == 404
    short = client.get('/api/compact?max_minutes=150').json
    assert short and all(i['runtime_min'] <= 150 for i in short)
    assert client.get('/api/compact?kind=nope').status_code == 400


def test_pages_require_login_and_legacy_redirect(client):
    assert client.get('/franchise/fate').status_code == 302
    assert client.get('/one-and-done').status_code == 302
    r = client.get('/franchise-explore?franchise=Middle Earth')
    assert r.status_code == 301 and r.headers['Location'].endswith('/franchise/middle-earth')
    _register_login(client)
    assert client.get('/franchise/fate').status_code == 200
    assert client.get('/one-and-done').status_code == 200


def test_progress_and_continue(client):
    seed_franchises.seed(apply=True, **QUIET)
    assert client.put('/api/me/progress', json={'key': 'movies_dune#', 'watched': True}).status_code == 401
    _register_login(client)
    assert client.put('/api/me/progress', json={'key': 'movies_dune#', 'watched': True}).status_code == 200
    assert client.get('/api/me/continue').json[0]['next']['title'] == 'Dune: Part Two'
    # unknown titles and malformed keys are rejected (no arbitrary rows per user)
    assert client.put('/api/me/progress', json={'key': 'movies_nope#', 'watched': True}).status_code == 400
    assert client.put('/api/me/progress', json={'key': ['x'], 'watched': True}).status_code == 400


def test_admin_edit_content_keeps_type_and_validates_meta(client):
    db.add_content({'type': 'movies', 'slug': 'dune', 'title': 'Dune'})
    assert client.post('/api/admin/login', json={'username': 'admin', 'password': 'admin-pw'}).status_code == 200
    r = client.put('/api/admin/content/movies_dune',
                   json={'title': 'Dune (2021)', 'type': 'animes', 'year': '2021', 'runtime_min': -5})
    assert r.status_code == 200
    c = db.get_content_by_id('movies_dune')
    assert (c['title'], c['type'], c['year'], c['runtime_min']) == ('Dune (2021)', 'movies', 2021, None)
    r = client.post('/api/admin/content', json={'slug': '"><script>', 'type': 'movies', 'title': 'x'})
    assert r.status_code == 201 and db.get_content_by_id('movies_script')


# ── API: security ────────────────────────────────────────────────────────

def test_register_validates_input(client):
    base = {'username': 'bob', 'email': 'bob@example.test', 'password': 'Passw0rd!'}
    for bad in ({'username': 'a b'}, {'email': 'nope'}, {'password': 'short'}, {'username': {'$ne': None}}):
        assert client.post('/api/auth/register', json={**base, **bad}).status_code == 400, bad
    assert client.post('/api/auth/register', json=['not', 'a', 'dict']).status_code == 400
    r = client.post('/api/auth/register', json={**base, 'age': 'x' * 100})   # junk age → stored as 0
    assert r.status_code == 201 and db.find_user_by_username('bob')[1]['age'] == 0


def test_user_cannot_take_another_username(client):
    _register_login(client, 'mallory', 'm@example.test')
    client.post('/api/auth/logout', json={})
    _register_login(client, 'alice', 'alice@example.test')
    assert client.put('/api/auth/me', json={'username': 'mallory'}).status_code == 409
    assert client.put('/api/auth/me', json={'profile_pic': 'javascript:alert(1)'}).status_code == 400
    assert client.put('/api/auth/me', json={'profile_pic': '/static/images/user.png'}).status_code == 200


def test_login_rejects_non_string_credentials(client):
    r = client.post('/api/auth/login', json={'username': {'$gt': ''}, 'password': {'$gt': ''}})
    assert r.status_code == 400


def test_admin_routes_need_admin(client):
    _register_login(client)
    assert client.post('/api/admin/franchises', json={'title': 'X'}).status_code == 403
    assert client.post('/api/admin/franchises', json=[1]).status_code == 403


def test_csrf_content_type_guard(client):
    r = client.post('/api/auth/login', data='username=a&password=b',
                    content_type='application/x-www-form-urlencoded')
    assert r.status_code == 415
