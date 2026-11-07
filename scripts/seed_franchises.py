"""
Seed curated franchises, watch orders and One & Done titles (data in scripts/seed_data.py).

    python -m scripts.seed_franchises            # dry run: print what would change
    python -m scripts.seed_franchises --apply    # write to MONGODB_URI
    python -m scripts.seed_franchises --apply --prune   # also delete FALSE_FRANCHISES records

Safe to re-run:
  * Titles are matched to existing content by type + title (case-insensitive), so titles you
    already added keep their id, images, cast and description; only empty fields are filled.
  * Existing franchises keep their image, banner and featured flag; kind, status, description
    and the entry list are replaced with the curated watch order.
"""
import argparse
import os
import sys

import database as db
from scripts.seed_data import FALSE_FRANCHISES, FRANCHISES, LIMITED, STANDALONES


def _norm(title):
    return ' '.join(title.lower().split())


def _key(title, label=''):
    return f'{title}|{label}' if label else title


def _content_fields(group):
    """Build content fields from every seed entry that refers to the same title."""
    first = group[0]
    labels = [e.get('label') for e in group if e.get('label')]
    seasons = first.get('seasons')
    if seasons is None and labels and first['type'] != 'movies' and first.get('format') != 'film':
        seasons = len(labels)
    year = min(e['year'] for e in group)
    status = 'Ongoing' if any(e.get('ongoing') for e in group) else 'Released'
    sections = ['popular', 'most-watched'] + (['new-releases'] if year >= 2024 else [])
    return {
        'title': first['title'],
        'type': first['type'],
        'year': year,
        'runtime_min': sum(e['minutes'] for e in group),
        'seasons': seasons,
        'format': first.get('format') or ('film' if first['type'] == 'movies' else 'series'),
        'Status': status,
        'tags': next((e['tags'] for e in group if e.get('tags')), []),
        'description': next((e['desc'] for e in group if e.get('desc')), ''),
        'language': next((e['language'] for e in group if e.get('language')), ''),
        'rating': 'Not Rated', 'h-image': '', 'v-image': '', 'cast': [], 'watchOptions': [],
        'videoUrl': '', 'genreDisplay': '', 'franchise': '', 'sections': sections,
    }


def validate(franchises=FRANCHISES):
    """Catch data typos (chrono names, duplicate slugs) before touching the database."""
    errors, slugs = [], set()
    for f in franchises:
        if f['slug'] in slugs:
            errors.append(f"duplicate slug {f['slug']}")
        slugs.add(f['slug'])
        if f['kind'] not in db.FRANCHISE_KINDS:
            errors.append(f"{f['slug']}: bad kind {f['kind']}")
        keys = [_key(e['title'], e.get('label', '')) for e in f['entries']]
        if len(keys) != len(set(keys)):
            errors.append(f"{f['slug']}: duplicate entry")
        if f.get('chrono') and sorted(f['chrono']) != sorted(keys):
            errors.append(f"{f['slug']}: chrono list mismatch {sorted(set(keys) ^ set(f['chrono']))}")
    return errors


def seed(apply=False, prune=False, franchises=FRANCHISES, singles=STANDALONES + LIMITED, log=print):
    errors = validate(franchises)
    if errors:
        raise ValueError('; '.join(errors))

    col = db._content_col()
    existing = {(d.get('type'), _norm(d.get('title', ''))): d for d in col.find()}
    taken_ids = {d['_id'] for d in existing.values()}

    # Group every seed entry by title so a series split into seasons becomes one content doc.
    groups = {}
    for f in franchises:
        for e in f['entries']:
            groups.setdefault((e['type'], _norm(e['title'])), []).append(e)
    for e in singles:
        groups.setdefault((e['type'], _norm(e['title'])), []).append(e)

    ids, created, filled = {}, 0, 0
    for key, group in groups.items():
        fields = _content_fields(group)
        doc = existing.get(key)
        if doc:
            ids[key] = doc['_id']
            # only fill gaps; never overwrite what an admin entered
            patch = {k: v for k, v in fields.items()
                     if k in ('year', 'runtime_min', 'seasons', 'format', 'description', 'tags', 'language')
                     and v not in (None, '', []) and doc.get(k) in (None, '', [])}
            if patch:
                filled += 1
                if apply:
                    col.update_one({'_id': doc['_id']}, {'$set': patch})
            continue
        slug = db.slugify(fields['title'])
        cid = db.content_doc_id(fields['type'], slug)
        if cid in taken_ids:   # same slug, different title → disambiguate with the year
            slug = f"{slug}-{fields['year']}"
            cid = db.content_doc_id(fields['type'], slug)
        taken_ids.add(cid)
        ids[key] = cid
        created += 1
        if apply:
            db.add_content({**fields, 'slug': slug})
    log(f'content: {created} new, {filled} existing titles get missing fields filled')

    for f in franchises:
        order = {k: i for i, k in enumerate(f.get('chrono') or [], start=1)}
        entries = [{
            'content_id': ids[(e['type'], _norm(e['title']))],
            'label': e.get('label', ''), 'year': e['year'], 'phase': e.get('phase', ''),
            'chrono': order.get(_key(e['title'], e.get('label', ''))),
            'canon': e.get('canon', 'canon'), 'essential': e.get('essential', True),
            'note': e.get('note', ''), 'runtime_min': e['minutes'],
        } for e in f['entries']]
        data = {'title': f['title'], 'kind': f['kind'], 'status': f['status'],
                'description': f['description'], 'entries': entries}
        current = db.get_franchise_raw(f['slug'])
        if current:
            data.update(image=current.get('image', ''), banner=current.get('banner', ''),
                        featured=current.get('featured', False))
            log(f"update  {f['slug']} ({len(entries)} entries)")
            if apply:
                db.update_franchise(f['slug'], data)
        else:
            log(f"create  {f['slug']} ({len(entries)} entries)")
            if apply:
                db.create_franchise(data, slug=f['slug'])

    if prune:
        for slug in FALSE_FRANCHISES:
            if db.get_franchise_raw(slug):
                log(f'delete  {slug} (single work, not a franchise)')
                if apply:
                    db.delete_franchise(slug)

    if not apply:
        log('dry run — nothing written. Re-run with --apply.')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--apply', action='store_true', help='write changes (default: dry run)')
    p.add_argument('--prune', action='store_true', help='delete franchise records for single works')
    args = p.parse_args(argv)
    if not os.environ.get('MONGODB_URI'):
        print('MONGODB_URI is not set. In PowerShell run:\n'
              '  $env:MONGODB_URI = "mongodb+srv://<user>:<password>@<cluster>/"\n'
              'then run this command again.', file=sys.stderr)
        return 1
    try:
        seed(apply=args.apply, prune=args.prune)
    except ValueError as e:
        print(f'seed data invalid: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
