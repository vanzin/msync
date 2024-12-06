# SPDX-License-Identifier: BSD-2-Clause
import os

import jsonpickle
from PySide6.QtCore import QSettings
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QPixmapCache
from PySide6.QtUiTools import loadUiType

APP_NAME = "msync"
SETTINGS = QSettings("vanzin.org", APP_NAME)

_FS_SAFE_TABLE = str.maketrans("/*$^&%|[{}]\n\t:;'?!\"´", "--____-(())--__---.'")


def config_dir(create=False):
    path = os.path.join(os.path.dirname(SETTINGS.fileName()), APP_NAME)
    if create and not os.path.isdir(path):
        os.mkdir(path)
    return path


def compile_ui(src):
    path = os.path.join(os.path.dirname(__file__), "ui", src)
    form, qtclass = loadUiType(path)

    class _WidgetBase(form, qtclass):
        def __init__(self, parent=None):
            qtclass.__init__(self, parent)
            form.__init__(self)
            self.setupUi(self)

    return _WidgetBase


def fs_safe(s):
    return s.translate(_FS_SAFE_TABLE)


def icon(name):
    return os.path.join(os.path.dirname(__file__), "icons", name)


def restore_ui(widget):
    name = widget.__class__.__name__
    data = SETTINGS.value(f"{name}/geometry")
    if data:
        widget.restoreGeometry(data)

    data = SETTINGS.value(f"{name}/windowState")
    if data:
        widget.restoreState(data)


def save_ui(widget):
    name = widget.__class__.__name__
    SETTINGS.setValue(f"{name}/geometry", widget.saveGeometry())
    if hasattr(widget, "saveState"):
        SETTINGS.setValue(f"{name}/windowState", widget.saveState())


def set_pixmap(label, pixmap):
    h = label.height()
    w = label.width()
    scaled = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    label.setPixmap(scaled)


class ConfigObj:
    """
    Base class for config objects that disables serialization of "private" fields.
    """

    SAVE_ENABLED = True

    @classmethod
    def load(cls):
        path = os.path.join(config_dir(), cls.config_file_name())
        if os.path.isfile(path):
            return jsonpickle.decode(open(path).read())
        return cls()

    @classmethod
    def config_file_name(cls):
        return "{}.{}".format(cls.__module__, cls.__name__)

    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __setstate__(self, data):
        self.__init__()
        for k, v in data.items():
            setattr(self, k, v)

    def save(self):
        if self.SAVE_ENABLED:
            jsonpickle.set_preferred_backend("json")
            jsonpickle.set_encoder_options("json", indent=2)
            path = os.path.join(config_dir(create=True), self.config_file_name())
            data = jsonpickle.encode(self)
            with open(path, "wt", encoding="utf-8") as out:
                out.write(data)


class PixmapCache:
    def __init__(self):
        self._cache = QPixmapCache()
        self._cache.setCacheLimit(64 * 1024 * 1024)

    def get_icon(self, name):
        pixmap = self._cache.find(name)
        if not pixmap:
            pixmap = QPixmap()
            pixmap.load(icon(name))
            self._cache.insert(name, pixmap)
        return pixmap
