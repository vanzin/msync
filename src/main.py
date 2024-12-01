import app
import util


class MainWindow(util.compile_ui("main.ui")):
    def __init__(self, cfg):
        super().__init__()
        self.bQuit.clicked.connect(self.handle_quit)

    def handle_quit(self):
        app.get().exit()
