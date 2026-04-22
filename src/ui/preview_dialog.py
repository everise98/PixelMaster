import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QFont, QBrush


class SplitView(QWidget):
    """Draggable before/after split-view widget."""

    def __init__(self, before_path: str, after_path: str, parent=None):
        super().__init__(parent)
        self._before = QPixmap(before_path)
        self._after  = QPixmap(after_path)
        self._split  = 0.50
        self._dragging = False
        self.setMouseTracking(True)
        self.setMinimumSize(640, 420)

    # ── paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _):
        if self._before.isNull() or self._after.isNull():
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        sx = int(W * self._split)

        # scale both to same display rect
        disp  = self._after.scaled(W, H, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        bef_d = self._before.scaled(disp.width(), disp.height(),
                                    Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
        ox = (W - disp.width()) // 2
        oy = (H - disp.height()) // 2

        p.fillRect(0, 0, W, H, QColor("#0d0d1a"))

        # BEFORE — left half
        p.setClipRect(ox, oy, max(0, sx - ox), disp.height())
        p.drawPixmap(ox, oy, bef_d)

        # AFTER — right half
        cx = max(ox, sx)
        p.setClipRect(cx, oy, ox + disp.width() - cx, disp.height())
        p.drawPixmap(ox, oy, disp)

        p.setClipping(False)

        # divider line
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.drawLine(sx, oy, sx, oy + disp.height())

        # handle
        cy, r = H // 2, 18
        p.setBrush(QBrush(QColor("#7c3aed")))
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.drawEllipse(QPoint(sx, cy), r, r)
        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p.setPen(QColor("#ffffff"))
        p.drawText(sx - r + 1, cy + 5, "‹")
        p.drawText(sx + r - 9, cy + 5, "›")

        # labels
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        label_y = oy + 26
        if sx - ox > 70:
            self._shadow_text(p, ox + 12, label_y, "BEFORE", QColor("#ffffff"))
        if ox + disp.width() - sx > 70:
            self._shadow_text(p, sx + 12, label_y, "AFTER", QColor("#a78bfa"))

        p.end()

    @staticmethod
    def _shadow_text(painter, x, y, text, color):
        painter.setPen(QColor(0, 0, 0, 130))
        painter.drawText(x + 1, y + 1, text)
        painter.setPen(color)
        painter.drawText(x, y, text)

    # ── mouse ─────────────────────────────────────────────────────────────────

    def _near(self, x):
        return abs(x - int(self.width() * self._split)) < 22

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self._near(e.pos().x()):
            self._dragging = True

    def mouseMoveEvent(self, e):
        self.setCursor(Qt.CursorShape.SizeHorCursor if self._near(e.pos().x())
                       else Qt.CursorShape.ArrowCursor)
        if self._dragging:
            self._split = max(0.04, min(0.96, e.pos().x() / self.width()))
            self.update()

    def mouseReleaseEvent(self, _):
        self._dragging = False


class PreviewDialog(QDialog):
    """
    mode="confirm" → shows Save / Skip buttons (used before writing to disk)
    mode="preview" → shows Close button (used after processing is done)
    """

    def __init__(
        self,
        before_path: str,
        after_path: str,
        scale: int,
        method_label: str,
        mode: str = "confirm",
        parent=None,
    ):
        super().__init__(parent)
        self._after_path = after_path
        self._mode = mode
        self.setWindowTitle("Preview — Before / After")
        self.setModal(True)
        self.resize(940, 640)
        self.setStyleSheet("QDialog { background: #0d0d1a; color: #f1f5f9; }"
                           "QLabel  { background: transparent; }")
        self._build_ui(before_path, after_path, scale, method_label)

    def _build_ui(self, before_path, after_path, scale, method_label):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # header
        hdr = QWidget()
        hdr.setFixedHeight(52)
        hdr.setStyleSheet("background:#12121f; border-bottom:1px solid #1e1e38;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(20, 0, 20, 0)
        title = QLabel(f"Before / After  ·  {scale}×  ·  {method_label}")
        title.setStyleSheet("font-size:13px; font-weight:600; color:#e2e8f0;")
        fname = QLabel(os.path.basename(before_path))
        fname.setStyleSheet("font-size:11px; color:#475569;")
        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(fname)
        root.addWidget(hdr)

        # split view
        self._sv = SplitView(before_path, after_path)
        root.addWidget(self._sv, stretch=1)

        # info / action bar
        bar = QWidget()
        bar.setFixedHeight(56)
        bar.setStyleSheet("background:#12121f; border-top:1px solid #1e1e38;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(20, 0, 20, 0)
        bl.setSpacing(16)

        try:
            from PIL import Image
            with Image.open(before_path) as b: bw, bh = b.size
            with Image.open(after_path)  as a: aw, ah = a.size
            lbl_b = QLabel(f"Original:  {bw} × {bh} px")
            lbl_a = QLabel(f"Upscaled:  {aw} × {ah} px")
        except Exception:
            lbl_b, lbl_a = QLabel("Original"), QLabel("Upscaled")

        lbl_b.setStyleSheet("font-size:11px; color:#64748b;")
        lbl_a.setStyleSheet("font-size:11px; color:#a78bfa; font-weight:600;")
        hint = QLabel("Drag divider to compare")
        hint.setStyleSheet("font-size:10px; color:#334155;")

        bl.addWidget(lbl_b)
        bl.addWidget(lbl_a)
        bl.addStretch()
        bl.addWidget(hint)
        bl.addSpacing(8)

        if self._mode == "confirm":
            skip_btn = QPushButton("✕  Skip")
            skip_btn.setStyleSheet(self._btn_style(secondary=True))
            skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            skip_btn.clicked.connect(self.reject)

            save_btn = QPushButton("✓  Save Image")
            save_btn.setStyleSheet(self._btn_style(secondary=False))
            save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            save_btn.clicked.connect(self.accept)

            bl.addWidget(skip_btn)
            bl.addWidget(save_btn)
        else:
            open_btn = QPushButton("Open File")
            open_btn.setStyleSheet(self._btn_style(secondary=True))
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.clicked.connect(self._open_file)

            close_btn = QPushButton("Close")
            close_btn.setStyleSheet(self._btn_style(secondary=False))
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.clicked.connect(self.accept)

            bl.addWidget(open_btn)
            bl.addWidget(close_btn)

        root.addWidget(bar)

    @staticmethod
    def _btn_style(secondary: bool) -> str:
        if secondary:
            return """QPushButton {
                background:#1e1e35; color:#94a3b8;
                border:1px solid #2a2a4a; border-radius:8px;
                padding:8px 18px; font-size:12px; font-weight:600;
            } QPushButton:hover { background:#252545; color:#f1f5f9; border-color:#7c3aed; }"""
        return """QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #7c3aed, stop:1 #3b82f6);
            color:#fff; border:none; border-radius:8px;
            padding:8px 22px; font-size:12px; font-weight:700;
        } QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #6d28d9, stop:1 #2563eb);
        }"""

    def _open_file(self):
        import subprocess
        subprocess.Popen(["explorer", "/select,", os.path.normpath(self._after_path)])
