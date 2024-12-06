# SPDX-License-Identifier: BSD-2-Clause
import os
import shutil

import app
import config
import model
import util
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QTreeWidgetItem


class MainWindow(util.compile_ui("main.ui")):
    def __init__(self, cfg):
        super().__init__()
        self.bQuit.clicked.connect(self.handle_quit)
        self.bConfig.clicked.connect(self.handle_config)
        self.bSync.clicked.connect(self.handle_sync)

        self.cfg = cfg
        self.pixmaps = util.PixmapCache()
        self.staged_albums = {}
        self.target_size = 0
        self.album_cover = None

        artists = self._load_sources()

        items = []
        for a in artists:
            items.append(self._to_tree_item(a))

            for aa in a.albums:
                if aa.path in self.cfg.staged_albums:
                    self._add_target(aa)

        self.source.insertTopLevelItems(0, items)
        self.source.itemDoubleClicked.connect(self.toggle_track_state)
        self.source.itemChanged.connect(self.sync_album_state)
        self.target.itemChanged.connect(self.sync_target_state)
        self.source.itemSelectionChanged.connect(self.handle_selection)
        self._update_target_size()
        util.restore_ui(self)

    def closeEvent(self, e):
        util.save_ui(self)
        super().closeEvent(e)

    def handle_quit(self):
        self.cfg.save()
        util.save_ui(self)
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

            malbum = model.Album(path, album, tracks)
            martist.add(malbum)

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
            a.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
            a.setData(0, Qt.UserRole, album)

            state = Qt.Unchecked
            if album.path in self.cfg.staged_albums:
                state = Qt.Checked
            a.setCheckState(0, state)

            top.addChild(a)

            for track in album.tracks:
                t = QTreeWidgetItem(a)
                t.setText(0, os.path.basename(track.path))
                t.setData(0, Qt.UserRole, track)

                flags = Qt.ItemNeverHasChildren | Qt.ItemIsSelectable
                if track.path in self.cfg.skipped_tracks:
                    track.set_skip(True)
                else:
                    flags |= Qt.ItemIsEnabled
                t.setFlags(flags)

                a.addChild(t)

        return top

    def _add_target(self, album):
        item_name = album.staging_name

        list_item = QListWidgetItem(self.target)
        list_item.setData(Qt.UserRole, album)
        list_item.setText(item_name)
        list_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        list_item.setCheckState(Qt.Checked)
        self.target.addItem(list_item)
        self.target.sortItems()
        self.staged_albums[item_name] = album

        for t in album.tracks:
            if not t.skip:
                self.target_size += t.size

        self._update_target_size()

    def _remove_target(self, album):
        del self.staged_albums[album.staging_name]

        for i in range(0, self.target.count()):
            tgt_item = self.target.item(i)
            tgt_data = tgt_item.data(Qt.UserRole)
            if tgt_data == album:
                self.target.takeItem(i)
                break

        for t in album.tracks:
            if not t.skip:
                self.target_size -= t.size

        self._update_target_size()

    def _update_target_size(self):
        SIZES = ["B", "kB", "MB", "GB"]

        total = self.target_size
        unit = 0
        rem = 0
        while total > 1024 and unit < len(SIZES) - 1:
            unit += 1
            rem = total % 1024
            total //= 1024

        total = 1.0 * total + 1.0 * rem / 1024.0
        size = f"Total: {total:.1f} {SIZES[unit]}"
        self.lTargetSize.setText(size)

    def toggle_track_state(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not isinstance(data, model.Track):
            return

        flags = item.flags()
        flags ^= Qt.ItemIsEnabled
        item.setFlags(flags)
        data.set_skip(not bool(flags & Qt.ItemIsEnabled))

        album = item.parent().data(0, Qt.UserRole)
        if album.staging_name in self.staged_albums:
            if data.skip:
                self.target_size -= data.size
            else:
                self.target_size += data.size

            self._update_target_size()

    def sync_album_state(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not isinstance(data, model.Album):
            return

        staged = data.staging_name
        state = item.checkState(col)

        if staged in self.staged_albums and state == Qt.Unchecked:
            self._remove_target(data)
            return

        if not staged in self.staged_albums and state == Qt.Checked:
            self._add_target(data)
            return

    def sync_target_state(self, item):
        album = item.data(Qt.UserRole)
        if (
            album.staging_name in self.staged_albums
            and item.checkState() == Qt.Unchecked
        ):
            self._remove_target(album)

    def handle_sync(self):
        # Clean up all existing staged data
        for e in os.listdir(self.cfg.target_path):
            shutil.rmtree(os.path.join(self.cfg.target_path, e))

        # Symlink all selected albums, skipping disabled tracks.
        albums = set()
        skipped_tracks = set()

        for _, album in self.staged_albums.items():
            albums.add(album.path)
            tgt_path = os.path.join(self.cfg.target_path, album.staging_name)
            os.mkdir(tgt_path)

            for t in album.tracks:
                if t.skip:
                    skipped_tracks.add(t.path)
                    continue

                tgt_lnk = os.path.join(tgt_path, util.fs_safe(os.path.basename(t.path)))
                os.symlink(t.path, tgt_lnk)

        self.cfg.staged_albums = albums
        self.cfg.skipped_tracks = skipped_tracks
        self.cfg.save()

        QMessageBox.information(self, "msync", "Done!")

    def handle_selection(self):
        selected = self.source.selectedItems()
        if not selected:
            return

        selected = selected[0]
        data = selected.data(0, Qt.UserRole)
        src = data

        is_track = True
        if isinstance(data, model.Album):
            src = data.tracks[0]
            is_track = False

        self.artist.setText(src.artist)
        self.album.setText(src.album)
        self.year.setText(f"{src.year}")
        if is_track:
            duration = src.duration_s
            self.track.setText(src.title)
            self.trackno.setText(f"{src.trackno}")
        else:
            self.track.setText("")
            self.trackno.setText("")
            duration = 0
            for t in data.tracks:
                duration += t.duration_s

        dur_m = duration // 60
        dur_s = duration % 60
        self.duration.setText(f"{dur_m}:{dur_s:0d}")

        if src.album != self.album_cover:
            cover = src.cover()
            if cover:
                pm = QPixmap()
                pm.loadFromData(src.cover())
                util.set_pixmap(self.cover, pm)
                self.album_cover = src.album
            else:
                self.album_cover = None
