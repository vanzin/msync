import util


class Directory(object):
    def __init__(self, path):
        self.tracks = []

        # TODO:
        # - load track list
        # - load target state
        # - method for loading metadata based on first track


class Track(object):
    def __init__(self, path):
        self.path = path
        self.skip = False

        # TODO:
        # - method for loading track data

        pass


class Config(util.ConfigObj):
    def __init__(self):
        # TODO:
        # - track selected source dirs
        # - track ignored tracks
        pass


class Metadata(object):
    def __init__(self, src):
        # TODO:
        # - load metadata from file
        pass
