import os
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap
from src.ui.styles import STATUS_COLORS, STATUS_ICONS

_SPINNER = ["◐", "◓", "◑", "◒"]


class ImageCard(QFrame):
    remove_requested  = pyqtSignal(str)   # input_path
    preview_requested = pyqtSignal(str, str)  # input_path, output_path

    def __init__(self, path: str, width: int, height: int, parent=None):
        super().__init__(parent)
        self.path = path
        self.orig_w = width
        self.orig_h = height
        self._status = "pending"
        self._output_path = ""
        self._spinner_idx = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._tick_spinner)

        self.setObjectName("imageCard")
        self.setFixedHeight(68)
        self._build_ui()
        self._set_status_display()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(10, 8, 10, 8)
        outer.setSpacing(10)

        # thumbnail
        self._thumb = QLabel(self)
        self._thumb.setFixedSize(48, 48)
        self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb.setStyleSheet(
            "border-radius: 6px; background-color: #eaffd0; color: #5a7a40; font-size: 10px;"
        )
        pix = QPixmap(self.path)
        if not pix.isNull():
            self._thumb.setPixmap(
                pix.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._thumb.setText("?")
        outer.addWidget(self._thumb)

        # info column
        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)

        self._name_label = QLabel(self._short_name(), self)
        self._name_label.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #0f1a08; background: transparent;"
        )
        self._name_label.setToolTip(self.path)

        self._size_label = QLabel(f"{self.orig_w} × {self.orig_h}", self)
        self._size_label.setStyleSheet(
            "font-size: 10px; color: #5a7a40; background: transparent;"
        )

        info.addWidget(self._name_label)
        info.addWidget(self._size_label)
        outer.addLayout(info, stretch=1)

        # preview button (hidden until done)
        self._preview_btn = QPushButton("Preview", self)
        self._preview_btn.setFixedHeight(26)
        self._preview_btn.setFixedWidth(62)
        self._preview_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._preview_btn.setVisible(False)
        self._preview_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #3a8a00;
                border: 1px solid #80cc00;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #b4ff2e;
                color: #0a1e00;
            }
        """)
        self._preview_btn.clicked.connect(
            lambda: self.preview_requested.emit(self.path, self._output_path)
        )
        outer.addWidget(self._preview_btn)

        # status label
        self._status_label = QLabel(self)
        self._status_label.setFixedWidth(80)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._status_label.setStyleSheet("font-size: 11px; background: transparent;")
        outer.addWidget(self._status_label)

        # remove button
        remove_btn = QPushButton("✕", self)
        remove_btn.setObjectName("removeBtn")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setToolTip("Remove")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.path))
        outer.addWidget(remove_btn)

    def set_status(self, status: str, detail: str = ""):
        self._status = status
        if status == "processing":
            self._spinner_timer.start(180)
            self._preview_btn.setVisible(False)
        else:
            self._spinner_timer.stop()

        if status == "done" and detail:
            self._output_path = detail
            self._preview_btn.setVisible(True)
            try:
                from PIL import Image
                with Image.open(detail) as img:
                    self._size_label.setText(
                        f"{self.orig_w}×{self.orig_h}  →  {img.width}×{img.height}"
                    )
            except Exception:
                pass

        self._set_status_display(detail)

    def _set_status_display(self, detail: str = ""):
        icon  = STATUS_ICONS.get(self._status, "○")
        color = STATUS_COLORS.get(self._status, "#64748b")
        text  = self._status.capitalize()
        if self._status == "error" and detail:
            self._status_label.setToolTip(detail)
        self._status_label.setText(f'<span style="color:{color}">{icon} {text}</span>')

    def _tick_spinner(self):
        self._spinner_idx = (self._spinner_idx + 1) % len(_SPINNER)
        icon  = _SPINNER[self._spinner_idx]
        color = STATUS_COLORS["processing"]
        self._status_label.setText(f'<span style="color:{color}">{icon} Processing</span>')

    def _short_name(self, max_len: int = 26) -> str:
        name = os.path.basename(self.path)
        return name if len(name) <= max_len else name[:max_len - 3] + "..."
