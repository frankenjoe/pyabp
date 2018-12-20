import os
import json
import pprint
import random
import tools


class Meta:
    path = None
    root = ''
    artist = ''
    album = ''
    track = 0
    ntracks = 0
    position = 0
    duration = 0.0
    volume = 50
    modified = None
    known = False

    def print(self, logger=None):
        tools.info('root=' + self.root, logger)
        tools.info('artist=' + self.artist, logger)
        tools.info('album=' + self.album, logger)
        tools.info('track=' + str(self.track + 1) + '/' + str(self.ntracks), logger)
        tools.info('position=' + str(tools.friendlytime(self.position)), logger)
        tools.info('total=' + str(tools.friendlytime(self.duration)), logger)
        tools.info('volume=' + str(self.volume), logger)
        tools.info('modified=' + str(self.modified), logger)
        tools.info('known=' + str(self.known), logger)


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
    meta.known = False

    meta.print()
