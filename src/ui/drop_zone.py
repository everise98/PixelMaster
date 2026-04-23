import os
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent

ACCEPTED = {".jpg", ".jpeg", ".png"}


def _filter_images(paths: list[str]) -> list[str]:
    return [p for p in paths if os.path.splitext(p)[1].lower() in ACCEPTED]


class DropZone(QFrame):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(160)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        self._icon = QLabel("⬆", self)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet("font-size: 32px; color: #4a6a35; background: transparent;")

        self._title = QLabel("Drop images here", self)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            "font-size: 15px; font-weight: 600; color: #5c7a4a; background: transparent;"
        )

        self._sub = QLabel("JPG · PNG  —  multiple files supported", self)
        self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub.setStyleSheet(
            "font-size: 11px; color: #5c7a4a; background: transparent;"
        )

        browse_btn = QPushButton("Browse Files", self)
        browse_btn.setObjectName("browseBtn")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setFixedWidth(120)
        browse_btn.clicked.connect(self._open_dialog)

        layout.addWidget(self._icon)
        layout.addWidget(self._title)
        layout.addWidget(self._sub)
        layout.addSpacing(4)
        layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    # ── drag events ──────────────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls()]
            if _filter_images(paths):
                event.acceptProposedAction()
                self._set_drag_state(True)
                return
        event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._set_drag_state(False)

    def dropEvent(self, event: QDropEvent):
        self._set_drag_state(False)
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        valid = _filter_images(paths)
        if valid:
            self.files_dropped.emit(valid)
        event.acceptProposedAction()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _set_drag_state(self, active: bool):
        self.setProperty("drag", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if active:
            self._icon.setStyleSheet("font-size: 36px; color: #b4ff2e; background: transparent;")
            self._title.setStyleSheet(
                "font-size: 15px; font-weight: 600; color: #b4ff2e; background: transparent;"
            )
        else:
            self._icon.setStyleSheet("font-size: 32px; color: #4a6a35; background: transparent;")
            self._title.setStyleSheet(
                "font-size: 15px; font-weight: 600; color: #5c7a4a; background: transparent;"
            )

    def _open_dialog(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.jpg *.jpeg *.png)",
        )
        if paths:
            self.files_dropped.emit(paths)
