import os
import numpy as np
from PIL import Image as PilImage

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QFileDialog, QSizePolicy, QScrollArea,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap


# ── Worker ────────────────────────────────────────────────────────────────────

class BgRemoveWorker(QThread):
    done  = pyqtSignal(object)   # PIL RGBA Image
    error = pyqtSignal(str)

    def __init__(self, path: str):
        super().__init__()
        self._path = path

    def run(self):
        try:
            import rembg
            img    = PilImage.open(self._path).convert("RGBA")
            result = rembg.remove(img)
            self.done.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ── Preview widget with checkerboard ─────────────────────────────────────────

class ImagePreview(QWidget):
    """Displays a PIL image; RGBA images shown over a checkerboard."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self._pil:   PilImage.Image | None = None
        self._label  = label
        self._pixmap: QPixmap | None = None
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_image(self, img: PilImage.Image | None):
        self._pil = img
        if img is None:
            self._pixmap = None
        else:
            self._pixmap = self._to_pixmap(img)
        self.update()

    @staticmethod
    def _to_pixmap(img: PilImage.Image) -> QPixmap:
        if img.mode == "RGBA":
            arr  = np.array(img)
            qimg = QImage(arr.tobytes(), arr.shape[1], arr.shape[0],
                          arr.shape[1] * 4, QImage.Format.Format_RGBA8888)
        else:
            rgb  = img.convert("RGB")
            arr  = np.array(rgb)
            qimg = QImage(arr.tobytes(), arr.shape[1], arr.shape[0],
                          arr.shape[1] * 3, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qimg)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # background
        painter.fillRect(self.rect(), QColor(18, 18, 30))

        if self._pixmap is None:
            painter.setPen(QColor(60, 55, 100))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._label)
            painter.end()
            return

        # fit image
        pw, ph = self._pixmap.width(), self._pixmap.height()
        ww, wh = self.width(), self.height() - 24   # reserve space for label
        scale  = min(ww / pw, wh / ph, 1.0)
        dw, dh = int(pw * scale), int(ph * scale)
        ox     = (ww - dw) // 2
        oy     = (wh - dh) // 2

        # checkerboard for RGBA images
        if self._pil and self._pil.mode == "RGBA":
            cell = max(6, dw // 30)
            for row in range(0, dh, cell):
                for col in range(0, dw, cell):
                    if (row // cell + col // cell) % 2 == 0:
                        painter.fillRect(ox + col, oy + row, cell, cell, QColor(200, 200, 200))
                    else:
                        painter.fillRect(ox + col, oy + row, cell, cell, QColor(155, 155, 155))

        painter.drawPixmap(ox, oy,
            self._pixmap.scaled(dw, dh,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))

        # label below
        painter.setPen(QColor(100, 90, 140))
        lbl_rect = self.rect().adjusted(0, self.height() - 24, 0, 0)
        painter.drawText(lbl_rect, Qt.AlignmentFlag.AlignCenter, self._label)

        painter.end()


# ── Background Remover Tab ────────────────────────────────────────────────────

class BgRemoverTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_path = ""
        self._orig_pil:   PilImage.Image | None = None
        self._result_pil: PilImage.Image | None = None
        self._worker: BgRemoveWorker | None = None
        self._setup_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_canvas_area(), stretch=1)

    def _build_controls(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("settingsPanel")
        panel.setFixedWidth(244)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(0)

        title = QLabel("✂  BG Remover")
        title.setObjectName("appTitle")
        sub   = QLabel("AI-powered background removal")
        sub.setObjectName("appSub")
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(28)

        open_btn = QPushButton("Open Image")
        open_btn.setObjectName("primaryBtn")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setFixedHeight(38)
        open_btn.clicked.connect(self._open_image)
        layout.addWidget(open_btn)
        layout.addSpacing(16)

        self._remove_btn = QPushButton("✂  Remove Background")
        self._remove_btn.setObjectName("primaryBtn")
        self._remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._remove_btn.setFixedHeight(44)
        self._remove_btn.setEnabled(False)
        self._remove_btn.clicked.connect(self._run)
        layout.addWidget(self._remove_btn)
        layout.addSpacing(20)

        # Info box
        info = QLabel(
            "Output: transparent PNG\n\n"
            "Model: u2net (~176 MB)\n"
            "Downloaded once to:\n~/.u2net/\n\n"
            "Processing time:\n~3–10 sec (CPU)"
        )
        info.setStyleSheet(
            "font-size: 10px; color: #334155; background: #12121f;"
            "border: 1px solid #1e1e38; border-radius: 8px;"
            "padding: 10px; line-height: 1.6;"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()

        self._save_btn = QPushButton("Save as PNG")
        self._save_btn.setObjectName("primaryBtn")
        self._save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_btn.setFixedHeight(44)
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._save)
        layout.addWidget(self._save_btn)

        return panel

    def _build_canvas_area(self) -> QWidget:
        container = QWidget()
        layout    = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(12)

        # Before / After side by side
        previews = QHBoxLayout()
        previews.setSpacing(12)

        self._before = ImagePreview("Original\n\nOpen an image to get started")
        self._after  = ImagePreview("Result\n\nClick  ✂ Remove Background")
        self._before.setAcceptDrops(True)
        self._before.dragEnterEvent = self._drag_enter
        self._before.dropEvent      = self._drop

        previews.addWidget(self._before, stretch=1)

        # divider
        div = QFrame()
        div.setFixedWidth(1)
        div.setStyleSheet("background: #1e1e38;")
        previews.addWidget(div)

        previews.addWidget(self._after, stretch=1)
        layout.addLayout(previews, stretch=1)

        self._status_lbl = QLabel("Open or drag an image to get started")
        self._status_lbl.setFixedHeight(30)
        self._status_lbl.setStyleSheet(
            "font-size: 11px; color: #475569; background: #0a0a14;"
            "border-top: 1px solid #1e1e38; padding: 0 16px;"
        )
        layout.addWidget(self._status_lbl)
        return container

    # ── drag & drop ───────────────────────────────────────────────────────────

    def _drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.splitext(path)[1].lower() in (".jpg", ".jpeg", ".png"):
                self._load(path)
                break

    # ── logic ─────────────────────────────────────────────────────────────────

    def _open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Images (*.jpg *.jpeg *.png)"
        )
        if path:
            self._load(path)

    def _load(self, path: str):
        try:
            self._source_path = path
            self._result_pil  = None
            self._orig_pil    = PilImage.open(path).convert("RGBA")
            self._before.set_image(self._orig_pil)
            self._after.set_image(None)
            self._remove_btn.setEnabled(True)
            self._save_btn.setEnabled(False)
            name = os.path.basename(path)
            w, h = self._orig_pil.size
            self._status_lbl.setText(
                f"Loaded: {name}  ·  {w}×{h}  ·  Click  ✂ Remove Background"
            )
        except Exception as e:
            self._status_lbl.setText(f"Error loading image: {e}")

    def _run(self):
        if not self._source_path or self._worker is not None:
            return
        self._remove_btn.setEnabled(False)
        self._remove_btn.setText("Processing…")
        self._status_lbl.setText("Removing background — this may take a few seconds…")
        self._after.set_image(None)

        self._worker = BgRemoveWorker(self._source_path)
        self._worker.done.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_done(self, result: PilImage.Image):
        self._worker      = None
        self._result_pil  = result
        self._after.set_image(result)
        self._remove_btn.setEnabled(True)
        self._remove_btn.setText("✂  Remove Background")
        self._save_btn.setEnabled(True)
        self._status_lbl.setText(
            "Background removed  ·  Click  Save as PNG  to export"
        )

    def _on_error(self, msg: str):
        self._worker = None
        self._remove_btn.setEnabled(True)
        self._remove_btn.setText("✂  Remove Background")
        self._status_lbl.setText(f"Error: {msg}")

    def _save(self):
        if self._result_pil is None:
            return
        base, _ = os.path.splitext(self._source_path) if self._source_path else ("output", "")
        default = base + "_nobg.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save as PNG", default, "PNG (*.png)"
        )
        if path:
            try:
                self._result_pil.save(path, "PNG")
                self._status_lbl.setText(f"Saved: {os.path.basename(path)}")
            except Exception as e:
                self._status_lbl.setText(f"Error: {e}")
