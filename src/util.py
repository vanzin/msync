import os
from PySide6.QtUiTools import loadUiType

def compile_ui(src):
    path = os.path.join(os.path.dirname(__file__), "ui", src)
    form, qtclass = loadUiType(path)

    class _WidgetBase(form, qtclass):
        def __init__(self, parent=None):
            qtclass.__init__(self, parent)
            form.__init__(self)
            self.setupUi(self)

    return _WidgetBase
