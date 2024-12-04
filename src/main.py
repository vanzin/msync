# SPDX-License-Identifier: BSD-2-Clause
import os

import app
import config
import model
import util
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem


class MainWindow(util.compile_ui("main.ui")):
    def __init__(self, cfg):
        super().__init__()
        self.bQuit.clicked.connect(self.handle_quit)
        self.bConfig.clicked.connect(self.handle_config)

        self.cfg = cfg
        self.pixmaps = util.PixmapCache()
        self.artists = self._load_sources()

        items = []
        for a in self.artists:
            items.append(self._to_tree_item(a))
        self.source.insertTopLevelItems(0, items)
        self.source.itemDoubleClicked.connect(self.toggle_track_state)

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
            album = tracks[0].album
            martist = artists_by_name.get(artist)
            if not martist:
                martist = model.Artist(artist)
                artists.append(martist)
                artists_by_name[artist] = martist

            martist.add(model.Album(path, album, tracks))

        artists.sort(key=lambda a: a.name)
        for a in artists:
            a.albums.sort(key=lambda a: -a.year)

        return artists

    def _to_tree_item(self, artist):
        top = QTreeWidgetItem(self.source)
        top.setIcon(0, self.pixmaps.get_icon("artist.png"))
        top.setText(0, artist.name)
        top.setFlags(Qt.ItemIsEnabled)

        for album in artist.albums:
            a = QTreeWidgetItem(top)
            a.setIcon(0, self.pixmaps.get_icon("album.png"))
            a.setText(0, album.name)
            a.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            a.setCheckState(0, Qt.Unchecked)
            a.setData(0, Qt.UserRole, album)
            top.addChild(a)

            for track in album.tracks:
                t = QTreeWidgetItem(a)
                t.setText(0, os.path.basename(track.path))
                t.setFlags(Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
                t.setData(0, Qt.UserRole, track)
                a.addChild(t)

        return top

    def toggle_track_state(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not isinstance(data, model.Track):
            return

        flags = item.flags()
        flags ^= Qt.ItemIsEnabled
        item.setFlags(flags)
