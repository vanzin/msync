# SPDX-License-Identifier: BSD-2-Clause
import os

import app
import config
import model
import util


class MainWindow(util.compile_ui("main.ui")):
    def __init__(self, cfg):
        super().__init__()
        self.bQuit.clicked.connect(self.handle_quit)
        self.bConfig.clicked.connect(self.handle_config)

        self.cfg = cfg
        self.artists = self._load_sources()

    def handle_quit(self):
        self.cfg.save()
        app.get().exit()

    def handle_config(self):
        cfg_wnd = config.ConfigWindow(self, self.cfg)
        cfg_wnd.show()

    def _load_sources(self):
        artists = []
        artists_by_name = {}

        for path, dirs, files in os.walk(self.cfg.source_path):
            tracks = [
                model.Track(os.path.join(path, t))
                for t in files
                if os.path.splitext(t)[1] in model.TRACK_EXTS
            ]
            if not tracks:
                continue

            artist = tracks[0].artist
            martist = artists_by_name.get(artist)
            if not martist:
                martist = model.Artist(artist)
                artists.append(martist)
                artists_by_name[artist] = martist

            martist.add(model.Album(path, tracks))

        artists.sort(key=lambda a: a.name)
        return artists
