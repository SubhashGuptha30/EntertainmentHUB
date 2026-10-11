"""
One-time migration: Firestore JSON export + recovered images -> MongoDB Atlas + Cloudinary.

Usage (env vars MONGODB_URI and CLOUDINARY_URL must be set):
    python scripts/migrate_from_firestore.py <backup_dir>

<backup_dir> contains users.json, content.json, selectors.json (each a list of
documents with an "_id" field) and images-recovered/images/<folder>/<file>.
Safe to re-run: documents are upserted and images are uploaded with fixed public IDs.
"""

import json
import os
import re
import sys
from datetime import datetime

import cloudinary.uploader
from pymongo import MongoClient, ReplaceOne

OLD_PREFIX = 'https://storage.googleapis.com/e-hub-uploads/'
OLD_URL = re.compile(re.escape(OLD_PREFIX) + r'(images/[A-Za-z0-9_./-]+)')


def upload_images(image_root):
    """Upload every recovered image; return {'images/x/y.jpg': cloudinary_url}."""
    urls = {}
    for dirpath, _, files in os.walk(image_root):
        for name in files:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, os.path.dirname(image_root)).replace(os.sep, '/')
            public_id = 'ehub/' + os.path.splitext(rel)[0]
            res = cloudinary.uploader.upload(full, public_id=public_id, overwrite=False, unique_filename=False)
            urls[rel] = res['secure_url']
    return urls


def rewrite(value, urls, missing):
    """Replace old GCS URLs inside any (nested / JSON-encoded) string value."""
    if isinstance(value, str):
        def sub(m):
            path = m.group(1)
            if path in urls:
                return urls[path]
            missing.add(path)
            return m.group(0)
        return OLD_URL.sub(sub, value)
    if isinstance(value, list):
        return [rewrite(v, urls, missing) for v in value]
    if isinstance(value, dict):
        return {k: rewrite(v, urls, missing) for k, v in value.items()}
    return value


def main(backup_dir):
    db = MongoClient(os.environ['MONGODB_URI'])[os.environ.get('MONGODB_DB', 'entertainmenthub')]
    urls = upload_images(os.path.join(backup_dir, 'images-recovered', 'images'))
    print(f'uploaded {len(urls)} images')

    missing = set()
    for name in ('users', 'content', 'selectors'):
        docs = json.load(open(os.path.join(backup_dir, f'{name}.json'), encoding='utf-8'))
        ops = []
        for d in docs:
            d = rewrite(d, urls, missing)
            if isinstance(d.get('created_at'), str):
                d['created_at'] = datetime.fromisoformat(d['created_at'])
            ops.append(ReplaceOne({'_id': d['_id']}, d, upsert=True))
        if ops:
            db[name].bulk_write(ops)
        print(f'{name}: {len(ops)} documents')

    if missing:
        print(f'{len(missing)} image paths had no recovered file (re-upload via admin panel):')
        for p in sorted(missing):
            print('  ', p)


if __name__ == '__main__':
    main(sys.argv[1])
