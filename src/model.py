# SPDX-License-Identifier: BSD-2-Clause
import mutagen
import util
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4Tags
from mutagen.id3 import ID3
from mutagen.mp4 import MP4Tags

TRACK_EXTS = set([".mp3", ".m4a"])


class Artist(object):
    def __init__(self, name):
        self.name = name
        self.albums = []

    def add(self, album):
        self.albums.append(album)


class Album(object):
    def __init__(self, path, name, tracks):
        self.name = name
        self.tracks = tracks

        # TODO:
        # - load target state

    @property
    def year(self):
        return self.tracks[0].year

    @property
    def staging_name(self):
        artist = self.tracks[0].artist
        return util.fs_safe(f"{artist} - {self.name}")


class Track(object):
    def __init__(self, path):
        self.path = path
        self.skip = False

        self._loaded = False
        self._artist = None
        self._album = None
        self._title = None
        self._duration_s = None
        self._year = None

    def _metadata(self):
        if self._loaded:
            return

        mf = mutagen.File(self.path, easy=True)
        if not mf:
            raise Exception(f"Unrecognized file {path}")

        if type(mf.tags) not in [EasyID3, EasyMP4Tags]:
            raise Exception(f"Don't know how to handle {type(mf.tags)}")

        self._artist = mf.tags["artist"][0]
        self._album = mf.tags["album"][0]
        self._title = mf.tags["title"][0]
        try:
            self._year = int(mf.tags["date"][0])
        except (KeyError, ValueError):
            print(f"track {self.path} is missing date information")

        self.duration_s = int(mf.info.length)

    def cover(self):
        tags = mutagen.File(self.path, easy=True).tags

        if type(tags) == ID3:
            for candidate in ["APIC:", "APIC:cover"]:
                art = tags.get(candidate)
                if art:
                    art = art.data
                    break
        elif type(tags) == MP4Tags:
            art = mf.tags.get("aART")
            if not art:
                art = mf.tags.get("covr")
            if isinstance(art, list):
                art = art[0]

        return art

    @property
    def artist(self):
        self._metadata()
        return self._artist

    @property
    def album(self):
        self._metadata()
        return self._album

    @property
    def year(self):
        self._metadata()
        return self._year


class Config(util.ConfigObj):
    source_path = ""
    target_path = ""

    def __init__(self):
        pass


class Metadata(object):
    def __init__(self, src):
        # TODO:
        # - load metadata from file
        pass
