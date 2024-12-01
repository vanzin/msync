import sys

from PySide6.QtWidgets import QApplication

_APP = None


def get():
    global _APP
    if not _APP:
        _APP = QApplication(sys.argv)
    return _APP
