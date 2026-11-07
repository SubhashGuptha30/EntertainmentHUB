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


def _add(ctype, slug, title):
    db.add_content({'type': ctype, 'slug': slug, 'title': title})
    return f'{ctype}_{slug}'


def test_franchise_orders_resolution_and_counts():
    hobbit = _add('movies', 'hobbit', 'The Hobbit')
    fotr = _add('movies', 'fotr', 'Fellowship')
    rop = _add('webSeries', 'rop', 'Rings of Power')
    slug = db.create_franchise({'title': 'Middle-earth!', 'kind': 'universe', 'entries': [
        {'content_id': fotr, 'chrono': '3'},
        {'content_id': hobbit, 'chrono': 2},
        {'content_id': rop, 'label': 'Season 1', 'chrono': 1, 'canon': 'bogus', 'essential': False},
        {'content_id': 'movies_deleted'},     # dangling → dropped on read
        {'content_id': ''},                   # blank → dropped on save
    ]})
    assert slug == 'middle-earth'
    with pytest.raises(ValueError):
        db.create_franchise({'title': 'Middle Earth'})          # same slug
    with pytest.raises(ValueError):
        db.create_franchise({'title': 'X', 'kind': 'nope'})

    f = db.get_franchise(slug)
    assert [e['release'] for e in f['entries']] == [1, 2, 3]
    assert [e['content']['title'] for e in sorted(f['entries'], key=lambda e: e['chrono'])] == \
        ['Rings of Power', 'The Hobbit', 'Fellowship']
    rop_entry = f['entries'][2]
    assert rop_entry['canon'] == 'canon' and rop_entry['essential'] is False
    assert rop_entry['key'] == f'{rop}#Season 1'

    summary = db.list_franchises()[0]
    assert summary['counts'] == {'movies': 2, 'webSeries': 1, 'animes': 0} and 'entries' not in summary
    assert db.list_franchises('anime') == []
    [link] = db.franchises_for_content(hobbit)          # dangling entry not counted
    assert (link['position'], link['total']) == (2, 3)
    assert link['prev']['title'] == 'Fellowship' and link['next']['label'] == 'Season 1'

    assert db.update_franchise(slug, {'title': 'Middle-earth', 'kind': 'universe', 'entries': []})
    assert db.get_franchise(slug)['entries'] == []
    assert not db.update_franchise('missing', {'title': 'x'})
    db.delete_franchise(slug)
    assert db.get_franchise(slug) is None


def test_migrate_selector_franchises():
    db.add_selector('franchises', '{"title": "Naruto", "image": "/n.jpg", "description": "ninja"}')
    db.add_content({'type': 'animes', 'slug': 'naruto', 'title': 'Naruto', 'franchise': 'naruto'})
    assert db.migrate_selector_franchises() == 1
    assert db.migrate_selector_franchises() == 0          # idempotent
    f = db.get_franchise('naruto')
    assert f['kind'] == 'anime' and f['image'] == '/n.jpg'
    assert [e['content_id'] for e in f['entries']] == ['animes_naruto']


def test_runtime_totals_and_season_entries():
    db.add_content({'type': 'webSeries', 'slug': 'loki', 'title': 'Loki', 'runtime_min': 620})
    db.add_content({'type': 'movies', 'slug': 'thor', 'title': 'Thor', 'runtime_min': 115})
    db.create_franchise({'title': 'Mini MCU', 'entries': [
        {'content_id': 'movies_thor'},
        {'content_id': 'webSeries_loki', 'label': 'Season 1', 'runtime_min': 300},
        {'content_id': 'webSeries_loki', 'label': 'Season 2'},   # unknown: title is split
    ]})
    f = db.get_franchise('mini-mcu')
    assert [e['runtime_min'] for e in f['entries']] == [115, 300, None]
    assert (f['total_minutes'], f['runtime_complete']) == (415, False)
    s = db.list_franchises()[0]
    assert (s['total_minutes'], s['runtime_complete']) == (415, False)


def test_compact_items_classification_and_budget():
    db.add_content({'type': 'movies', 'slug': 'parasite', 'title': 'Parasite', 'runtime_min': 132})
    db.add_content({'type': 'webSeries', 'slug': 'dark', 'title': 'Dark', 'seasons': 3,
                    'Status': 'Released', 'runtime_min': 1550})
    db.add_content({'type': 'webSeries', 'slug': 'long', 'title': 'Long', 'seasons': 9, 'Status': 'Released'})
    db.add_content({'type': 'webSeries', 'slug': 'airing', 'title': 'Airing', 'seasons': 1, 'Status': 'Ongoing'})
    db.add_content({'type': 'animes', 'slug': 'your-name', 'title': 'Your Name', 'format': 'film',
                    'runtime_min': 106})
    db.add_content({'type': 'movies', 'slug': 'bttf', 'title': 'BTTF', 'runtime_min': 116})
    db.create_franchise({'title': 'Back to the Future', 'kind': 'trilogy',
                         'entries': [{'content_id': 'movies_bttf'}]})

    kinds = {i['title']: i['kind'] for i in db.compact_items()}
    assert kinds == {'Parasite': 'standalone', 'Dark': 'limited', 'Your Name': 'standalone',
                     'Back to the Future': 'trilogy'}             # Long/Airing excluded; BTTF via collection
    assert [i['title'] for i in db.compact_items(max_minutes=120)] == ['Your Name', 'Back to the Future']
    assert [i['title'] for i in db.compact_items('limited')] == ['Dark']


def test_continue_watching_next_entry():
    for s in ('a', 'b', 'c'):
        db.add_content({'type': 'movies', 'slug': s, 'title': s.upper()})
    db.create_franchise({'title': 'Saga', 'entries': [{'content_id': f'movies_{s}'} for s in 'abc']})
    assert db.continue_watching('u1') == []
    db.set_progress('u1', 'movies_a#', True)
    [c] = db.continue_watching('u1')
    assert (c['done'], c['total'], c['next']['title']) == (1, 3, 'B')
    for s in 'bc':
        db.set_progress('u1', f'movies_{s}#', True)
    assert db.continue_watching('u1') == []                      # finished → gone


def test_clean_franchise_rejects_bad_shapes():
    for bad in ([], {'title': 'x', 'entries': 'nope'}):
        with pytest.raises(ValueError):
            db.clean_franchise(bad)
    assert db.clean_franchise({'title': 'x', 'entries': ['junk', {'content_id': 'm_a'}]})['entries'][0][
        'content_id'] == 'm_a'


def test_username_or_email_taken():
    uid = db.create_user('alice', 'a@x.com', 'pw', '', 0)
    assert db.username_or_email_taken('alice', 'new@x.com')
    assert not db.username_or_email_taken('alice', 'a@x.com', exclude_id=uid)


def test_progress():
    db.set_progress('u1', 'movies_a#', True)
    db.set_progress('u1', 'movies_a#', True)              # upsert, no duplicate
    db.set_progress('u2', 'movies_b#', True)
    assert db.get_progress('u1') == ['movies_a#']
    db.set_progress('u1', 'movies_a#', False)
    assert db.get_progress('u1') == []


def test_rewrite_replaces_nested_and_json_encoded_urls():
    old = 'https://storage.googleapis.com/e-hub-uploads/images/cast/a.jpg'
    urls = {'images/cast/a.jpg': 'https://res.cloudinary.com/x/a.jpg'}
    missing = set()
    doc = {'v': old, 'cast': ['{"image": "%s"}' % old], 'n': 1,
           'gone': 'https://storage.googleapis.com/e-hub-uploads/images/cast/b.jpg'}
    out = rewrite(doc, urls, missing)
    assert out['v'] == urls['images/cast/a.jpg'] and urls['images/cast/a.jpg'] in out['cast'][0]
    assert missing == {'images/cast/b.jpg'} and out['n'] == 1
