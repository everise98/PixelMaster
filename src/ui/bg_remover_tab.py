import os
import math
import urllib.request
import numpy as np
from PIL import Image as PilImage

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QFileDialog, QSizePolicy, QDialog,
    QProgressBar, QVBoxLayout as QVBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap


MODEL_URL  = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
MODEL_PATH = os.path.join(os.path.expanduser("~"), ".u2net", "u2net.onnx")
MODEL_SIZE = 176_000_000   # ~176 MB


# ── Download worker ───────────────────────────────────────────────────────────

class DownloadWorker(QThread):
    progress = pyqtSignal(int)    # 0-100
    done     = pyqtSignal()
    error    = pyqtSignal(str)

    def run(self):
        try:
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            downloaded = [0]

            def hook(count, block, total):
                downloaded[0] = min(count * block, MODEL_SIZE)
                pct = min(100, int(downloaded[0] / MODEL_SIZE * 100))
                self.progress.emit(pct)

            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, hook)
            self.progress.emit(100)
            self.done.emit()
        except Exception as e:
            self.error.emit(str(e))


# ── Download dialog ───────────────────────────────────────────────────────────

class DownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading AI Model")
        self.setFixedSize(400, 160)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.CustomizeWindowHint
        )
        self.setStyleSheet("""
            QDialog { background: #f0f4f0; }
            QLabel  { color: #0f1a08; background: transparent; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel("Downloading u2net model")
        title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1a4a00;")
        layout.addWidget(title)

        self._sub = QLabel("First-time setup — ~176 MB, downloaded once")
        self._sub.setStyleSheet("font-size: 11px; color: #5a7a40;")
        layout.addWidget(self._sub)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(8)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet("""
            QProgressBar {
                background: #1a2535; border: none; border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #80cc00, stop:1 #b4ff2e);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self._bar)

        self._pct_lbl = QLabel("0%")
        self._pct_lbl.setStyleSheet("font-size: 11px; color: #3a8a00; font-weight: 600;")
        layout.addWidget(self._pct_lbl)

        self._worker = DownloadWorker()
        self._worker.progress.connect(self._on_progress)
        self._worker.done.connect(self.accept)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, pct: int):
        self._bar.setValue(pct)
        mb = pct * 176 // 100
        self._pct_lbl.setText(f"{pct}%  ·  {mb} / 176 MB")

    def _on_error(self, msg: str):
        self._sub.setText(f"Error: {msg}")
        self.reject()


# ── BG Remove worker ──────────────────────────────────────────────────────────

class BgRemoveWorker(QThread):
    done  = pyqtSignal(object)
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


# ── Preview widget ────────────────────────────────────────────────────────────

class ImagePreview(QWidget):
    def __init__(self, placeholder: str, parent=None):
        super().__init__(parent)
        self._pil:        PilImage.Image | None = None
        self._pixmap:     QPixmap | None        = None
        self._placeholder = placeholder
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_image(self, img: PilImage.Image | None):
        self._pil = img
        if img is None:
            self._pixmap = None
        else:
            if img.mode == "RGBA":
                arr  = np.array(img)
                qimg = QImage(arr.tobytes(), arr.shape[1], arr.shape[0],
                              arr.shape[1] * 4, QImage.Format.Format_RGBA8888)
            else:
                arr  = np.array(img.convert("RGB"))
                qimg = QImage(arr.tobytes(), arr.shape[1], arr.shape[0],
                              arr.shape[1] * 3, QImage.Format.Format_RGB888)
            self._pixmap = QPixmap.fromImage(qimg)
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor(240, 248, 234))

        if self._pixmap is None:
            painter.setPen(QColor(100, 150, 70))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             self._placeholder)
            painter.end()
            return

        pw, ph = self._pixmap.width(), self._pixmap.height()
        ww, wh = self.width(), self.height() - 26
        scale  = min(ww / pw, wh / ph, 1.0)
        dw, dh = int(pw * scale), int(ph * scale)
        ox, oy = (ww - dw) // 2, (wh - dh) // 2

        # checkerboard for transparent RGBA
        if self._pil and self._pil.mode == "RGBA":
            cell = max(6, dw // 32)
            for r in range(0, dh, cell):
                for c in range(0, dw, cell):
                    col = QColor(210, 225, 200) if (r // cell + c // cell) % 2 == 0 \
                          else QColor(240, 248, 234)
                    painter.fillRect(ox + c, oy + r, cell, cell, col)

        painter.drawPixmap(ox, oy,
            self._pixmap.scaled(dw, dh,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))

        # bottom caption
        painter.setPen(QColor(100, 150, 70))
        cap_rect = self.rect().adjusted(0, self.height() - 22, 0, 0)
        painter.drawText(cap_rect, Qt.AlignmentFlag.AlignCenter,
                         "Original" if "Original" in self._placeholder else "Result")
        painter.end()


# ── Background Remover Tab ────────────────────────────────────────────────────

class BgRemoverTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_path = ""
        self._result_pil: PilImage.Image | None = None
        self._worker: BgRemoveWorker | None = None
        self._setup_ui()

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
        layout.addSpacing(14)

        self._remove_btn = QPushButton("✂  Remove Background")
        self._remove_btn.setObjectName("primaryBtn")
        self._remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._remove_btn.setFixedHeight(44)
        self._remove_btn.setEnabled(False)
        self._remove_btn.clicked.connect(self._run)
        layout.addWidget(self._remove_btn)
        layout.addSpacing(20)

        info = QLabel(
            "Output: transparent PNG\n\n"
            "Model: u2net (~176 MB)\n"
            "Downloaded once on first use\n\n"
            "Processing time:\n~3–10 sec (CPU)"
        )
        info.setStyleSheet(
            "font-size: 10px; color: #5a7a40; background: #eaffd0;"
            "border: 1px solid #b4ff2e; border-radius: 8px;"
            "padding: 10px;"
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

        previews = QHBoxLayout()
        previews.setSpacing(12)

        self._before = ImagePreview("Original\n\nOpen or drag an image")
        self._after  = ImagePreview("Result\n\nClick  ✂ Remove Background")
        self._before.setAcceptDrops(True)
        self._before.dragEnterEvent = self._drag_enter
        self._before.dropEvent      = self._drop

        previews.addWidget(self._before, stretch=1)

        div = QFrame()
        div.setFixedWidth(1)
        div.setStyleSheet("background: #e2e8f0;")
        previews.addWidget(div)

        previews.addWidget(self._after, stretch=1)
        layout.addLayout(previews, stretch=1)

        self._status_lbl = QLabel("Open or drag an image to get started")
        self._status_lbl.setFixedHeight(30)
        self._status_lbl.setStyleSheet(
            "font-size: 11px; color: #5a7a40; background: #e8f0e0;"
            "border-top: 1px solid #c8ddb0; padding: 0 16px;"
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
            self, "Open Image", "", "Images (*.jpg *.jpeg *.png)"
        )
        if path:
            self._load(path)

    def _load(self, path: str):
        try:
            self._source_path = path
            self._result_pil  = None
            pil = PilImage.open(path).convert("RGBA")
            self._before.set_image(pil)
            self._after.set_image(None)
            self._remove_btn.setEnabled(True)
            self._save_btn.setEnabled(False)
            w, h = pil.size
            self._status_lbl.setText(
                f"Loaded: {os.path.basename(path)}  ·  {w}×{h}  ·  Click  ✂ Remove Background"
            )
        except Exception as e:
            self._status_lbl.setText(f"Error loading: {e}")

    def _run(self):
        if not self._source_path or self._worker is not None:
            return

        # Show download dialog if model not present
        if not os.path.exists(MODEL_PATH):
            dlg = DownloadDialog(self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                self._status_lbl.setText("Model download failed or cancelled.")
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
        self._worker     = None
        self._result_pil = result
        self._after.set_image(result)
        self._remove_btn.setEnabled(True)
        self._remove_btn.setText("✂  Remove Background")
        self._save_btn.setEnabled(True)
        self._status_lbl.setText("Done  ·  Click  Save as PNG  to export")

    def _on_error(self, msg: str):
        self._worker = None
        self._remove_btn.setEnabled(True)
        self._remove_btn.setText("✂  Remove Background")
        self._status_lbl.setText(f"Error: {msg}")

    def _save(self):
        if self._result_pil is None:
            return
        base, _ = os.path.splitext(self._source_path) if self._source_path else ("output", "")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save as PNG", base + "_nobg.png", "PNG (*.png)"
        )
        if path:
            try:
                self._result_pil.save(path, "PNG")
                self._status_lbl.setText(f"Saved: {os.path.basename(path)}")
            except Exception as e:
                self._status_lbl.setText(f"Error: {e}")
