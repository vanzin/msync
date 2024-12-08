# SPDX-License-Identifier: BSD-2-Clause
import util
from PySide6.QtWidgets import QFileDialog


class ConfigWindow(util.compile_ui("config.ui")):
    def __init__(self, parent, cfg):
        super().__init__(parent)
        self.bPickSource.clicked.connect(self.pick_source)
        self.bPickTarget.clicked.connect(self.pick_target)
        self.controls.accepted.connect(self.handle_ok)
        self.controls.rejected.connect(self.close)

        self.source.setText(cfg.source_path)
        self.target.setText(cfg.target_path)

        self.cfg = cfg

    def pick_source(self):
        self.cfg.source_path = QFileDialog.getExistingDirectory(self)
        self.source.setText(self.cfg.source_path)

    def pick_target(self):
        self.cfg.target_path = QFileDialog.getExistingDirectory(self)
        self.target.setText(self.cfg.target_path)

    def handle_ok(self):
        self.cfg.source_path = self.source.text()
        self.cfg.target_path = self.target.text()

        self.cfg.save()
        self.close()
