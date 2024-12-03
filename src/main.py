# SPDX-License-Identifier: BSD-2-Clause
import app
import config
import util


class MainWindow(util.compile_ui("main.ui")):
    def __init__(self, cfg):
        super().__init__()
        self.bQuit.clicked.connect(self.handle_quit)
        self.bConfig.clicked.connect(self.handle_config)

        self.cfg = cfg

    def handle_quit(self):
        self.cfg.save()
        app.get().exit()

    def handle_config(self):
        cfg_wnd = config.ConfigWindow(self, self.cfg)
        cfg_wnd.show()
