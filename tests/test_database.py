"""Data-layer tests against an in-memory MongoDB (mongomock). Run: python -m pytest -q"""
import os
import sys

import mongomock
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db  # noqa: E402
from scripts.migrate_from_firestore import rewrite  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db(monkeypatch):
    monkeypatch.setattr(db, '_db', mongomock.MongoClient()['test'])
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin-pw')
    db.init_db()


def test_init_seeds_admin_and_selectors_once():
    db.init_db()  # idempotent
    _, admin = db.find_user_by_username('admin', admin_only=True)
    assert admin and db.check_password('admin-pw', admin['password'])
    assert len(db.get_selectors_by_category('rating')) == 11


def test_user_lifecycle():
    uid = db.create_user('alice', 'a@x.com', 'pw', 'F', 21)
    assert db.find_user_by_username_or_email('alice', 'other@x.com')
    _, u = db.find_user_by_username('alice')
    assert u['id'] == uid and db.check_password('pw', u['password'])
    db.update_user(uid, {'age': 22})
    assert db.get_user_by_id(uid)['age'] == 22
    assert [x['username'] for x in db.list_users()] == ['alice']
    assert 'password' not in db.list_users()[0]
    assert db.delete_user(uid) and db.get_user_by_id(uid) is None


def test_admin_cannot_be_deleted():
    admin_id, _ = db.find_user_by_username('admin', admin_only=True)
    assert not db.delete_user(admin_id)


def test_content_crud_and_stats():
    db.add_content({'type': 'movies', 'slug': 'inception', 'title': 'Inception'})
    with pytest.raises(ValueError):
        db.add_content({'type': 'movies', 'slug': 'inception', 'title': 'dup'})
    assert db.get_single_content('movies', 'inception')['id'] == 'movies_inception'
    assert db.update_content('movies_inception', {'title': 'Inception (2010)'})['title'] == 'Inception'
    assert db.get_all_content()['movies']['inception']['title'] == 'Inception (2010)'
    assert db.update_content('missing', {'title': 'x'}) is None
    assert db.get_content_stats()['movies'] == 1
    db.delete_content('movies_inception')
    assert db.get_content_by_type('movies') == {}


def test_selectors():
    sid, created = db.add_selector('cast', '{"name": "Aaron Paul", "image": ""}')
    assert created and db.add_selector('cast', '{"name": "Aaron Paul", "image": ""}') == (sid, False)
    assert db.search_cast_selectors('aaron')[0]['name'] == 'Aaron Paul'
    db.update_selector(sid, '{"name": "A. Paul", "image": ""}')
    assert db.search_cast_selectors('a. paul')
    db.delete_selector(sid)
    assert db.search_cast_selectors('paul') == []


def test_rewrite_replaces_nested_and_json_encoded_urls():
    old = 'https://storage.googleapis.com/e-hub-uploads/images/cast/a.jpg'
    urls = {'images/cast/a.jpg': 'https://res.cloudinary.com/x/a.jpg'}
    missing = set()
    doc = {'v': old, 'cast': ['{"image": "%s"}' % old], 'n': 1,
           'gone': 'https://storage.googleapis.com/e-hub-uploads/images/cast/b.jpg'}
    out = rewrite(doc, urls, missing)
    assert out['v'] == urls['images/cast/a.jpg'] and urls['images/cast/a.jpg'] in out['cast'][0]
    assert missing == {'images/cast/b.jpg'} and out['n'] == 1
