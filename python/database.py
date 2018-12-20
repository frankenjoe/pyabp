import os
import random

from tinydb import TinyDB, Query
from meta import Meta
import tools


class Database:
    logger = None
    db = None

    def __init__(self, logger=None):
        self.logger = logger

    def open(self, path: str):

        if self.db is not None:
            self.db.close()

        tools.info('open database ' + path, self.logger)

        self.db = TinyDB(path)

    def close(self):

        if self.db is None:
            return

        tools.info('close database', self.logger)

        self.db.close()

    def contains(self, root: str):

        if self.db is None:
            return False

        query = Query()

        return self.db.contains(query.root == root)

    def write(self, meta: Meta):

        if self.db is None:
            return

        query = Query()

        self.db.upsert({'root': meta.root,
                        'artist': meta.artist,
                        'album': meta.album,
                        'track': meta.track,
                        'ntracks': meta.ntracks,
                        'position': meta.position,
                        'duration': meta.duration,
                        'volume': meta.volume,
                        'modified': meta.modified,
                        'known': meta.known},
                       query.root == meta.root)

    def read(self, root):

        if self.db is None:
            return None

        query = Query()

        result = self.db.search(query.root == root)

        if len(result) == 0:
            return None

        meta = Meta()
        meta.root = result[0]['root']
        meta.artist = result[0]['artist']
        meta.album = result[0]['album']
        meta.track = result[0]['track']
        meta.ntracks = result[0]['ntracks']
        meta.position = result[0]['position']
        meta.duration = result[0]['duration']
        meta.volume = result[0]['volume']
        meta.modified = result[0]['modified']
        meta.known = result[0]['known']

        return meta

    def isnotdir(self, path: str):
        return not os.path.isdir(path)

    def clean(self):

        if self.db is None:
            return None

        query = Query()

        condition = query.root.test(self.isnotdir)
        result = self.db.remove(condition)

        tools.info('clean database (' + str(len(result)) + ' entries removed)', self.logger)

    def print(self):

        if not self.db:
            return

        tools.info(self.db.all(), self.logger)


if __name__ == '__main__':
    meta = Meta()
    meta.root = '.'
    meta.album = tools.randstr()
    meta.artist = tools.randstr()
    meta.ntracks = 100
    meta.track = random.randint(0, meta.ntracks - 1)
    meta.position = round(random.uniform(0.0, 60.0), 1)
    meta.volume = random.randint(0, 100)
    meta.modified = 0

    database = Database()
    database.open('db.json')
    database.write(meta)
    meta.root = tools.randstr()
    database.write(meta)
    database.print()

    meta2 = database.read(meta.root)
    meta2.print()

    database.clean()
    database.print()

    database.close()
