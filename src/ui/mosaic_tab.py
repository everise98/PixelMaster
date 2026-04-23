import os
import math
import numpy as np
import cv2
from PIL import Image as PilImage

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QComboBox, QSlider, QFileDialog, QSizePolicy,
)
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import (
    QPainter, QColor, QImage, QPixmap,
    QPen, QKeySequence, QShortcut,
)


class MosaicCanvas(QWidget):
    """Paintable canvas — supports Brush / Box / Circle selection modes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._orig_bgr:    np.ndarray | None = None
        self._result_bgr:  np.ndarray | None = None
        self._mask:        np.ndarray | None = None   # float32 H×W, 0-1
        self._undo_stack:  list[tuple]        = []

        # brush
        self._brush_px   = 30
        self._painting   = False
        self._last_pos:  QPoint | None = None

        # box / circle drag
        self._mode       = "brush"   # "brush" | "box" | "circle"
        self._drag_start: QPoint | None = None
        self._drag_cur:   QPoint | None = None

        self._source_path = ""

        self.setAcceptDrops(True)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.CrossCursor)

    # ── public API ────────────────────────────────────────────────────────────

    def load_image(self, path: str):
        try:
            pil = PilImage.open(path).convert("RGB")
            arr = np.array(pil)
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            self._orig_bgr   = bgr
            self._result_bgr = bgr.copy()
            h, w             = bgr.shape[:2]
            self._mask       = np.zeros((h, w), dtype=np.float32)
            self._undo_stack.clear()
            self._drag_start = self._drag_cur = None
            self.update()
        except Exception as e:
            print(f"MosaicCanvas.load_image error: {e}")

    def set_mode(self, mode: str):
        self._mode       = mode
        self._drag_start = None
        self._drag_cur   = None
        self._painting   = False
        self.update()

    def set_brush_size(self, px: int):
        self._brush_px = px

    def clear_mask(self):
        if self._mask is not None:
            self._push_undo(mask_only=True)
            self._mask[:] = 0
            self.update()

    def undo(self):
        if self._undo_stack:
            self._result_bgr, self._mask = self._undo_stack.pop()
            self.update()

    def apply_effect(self, effect: str, strength: int):
        if self._result_bgr is None or self._mask is None:
            return
        if self._mask.max() == 0:
            return
        self._push_undo()

        src   = self._result_bgr
        mask3 = np.stack([self._mask] * 3, axis=-1)

        if effect == "pixelate":
            block = max(4, strength)
            h, w  = src.shape[:2]
            small = cv2.resize(src, (max(1, w // block), max(1, h // block)),
                               interpolation=cv2.INTER_LINEAR)
            tiled = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
            out   = src * (1 - mask3) + tiled * mask3
        else:  # blur
            k   = strength * 2 + 1
            blr = cv2.GaussianBlur(src, (k, k), 0)
            out = src * (1 - mask3) + blr * mask3

        self._result_bgr = np.clip(out, 0, 255).astype(np.uint8)
        self._mask[:]    = 0
        self.update()

    def save_result(self, path: str, jpeg_quality: int = 95) -> tuple[bool, str]:
        if self._result_bgr is None:
            return False, "No image loaded"
        try:
            rgb = cv2.cvtColor(self._result_bgr, cv2.COLOR_BGR2RGB)
            pil = PilImage.fromarray(rgb)
            ext = os.path.splitext(path)[1].lower()
            if ext in (".jpg", ".jpeg"):
                pil.save(path, "JPEG", quality=jpeg_quality, optimize=True)
            else:
                pil.save(path, "PNG", optimize=True)
            return True, path
        except Exception as e:
            return False, str(e)

    def has_image(self) -> bool:
        return self._result_bgr is not None

    # ── coordinate helpers ────────────────────────────────────────────────────

    def _img_rect(self) -> tuple[int, int, int, int, float]:
        if self._orig_bgr is None:
            return 0, 0, 0, 0, 1.0
        h, w   = self._orig_bgr.shape[:2]
        ww, wh = self.width(), self.height()
        scale  = min(ww / w, wh / h)
        dw, dh = int(w * scale), int(h * scale)
        ox     = (ww - dw) // 2
        oy     = (wh - dh) // 2
        return ox, oy, dw, dh, scale

    def _to_img(self, wx: float, wy: float) -> tuple[int, int]:
        ox, oy, _, _, scale = self._img_rect()
        return int((wx - ox) / scale), int((wy - oy) / scale)

    def _clamp_img(self, ix: int, iy: int) -> tuple[int, int]:
        if self._mask is None:
            return ix, iy
        h, w = self._mask.shape
        return max(0, min(ix, w - 1)), max(0, min(iy, h - 1))

    # ── brush painting ────────────────────────────────────────────────────────

    def _draw_brush_circle(self, ix: int, iy: int):
        if self._mask is None:
            return
        h, w = self._mask.shape
        if not (0 <= ix < w and 0 <= iy < h):
            return
        _, _, _, _, scale = self._img_rect()
        r = max(1, int(self._brush_px / scale))
        cv2.circle(self._mask, (ix, iy), r, 1.0, -1)

    def _stroke_to(self, p2: QPoint):
        if self._mask is None or self._last_pos is None:
            return
        ix1, iy1 = self._to_img(self._last_pos.x(), self._last_pos.y())
        ix2, iy2 = self._to_img(p2.x(), p2.y())
        steps    = max(1, max(abs(ix2 - ix1), abs(iy2 - iy1)))
        for i in range(steps + 1):
            t  = i / steps
            self._draw_brush_circle(
                int(ix1 + (ix2 - ix1) * t),
                int(iy1 + (iy2 - iy1) * t),
            )
        self.update()

    # ── shape commit (box / circle) ───────────────────────────────────────────

    def _commit_shape(self):
        if self._mask is None or self._drag_start is None or self._drag_cur is None:
            return
        ix1, iy1 = self._clamp_img(*self._to_img(self._drag_start.x(), self._drag_start.y()))
        ix2, iy2 = self._clamp_img(*self._to_img(self._drag_cur.x(),   self._drag_cur.y()))

        if self._mode == "box":
            cv2.rectangle(
                self._mask,
                (min(ix1, ix2), min(iy1, iy2)),
                (max(ix1, ix2), max(iy1, iy2)),
                1.0, -1,
            )
        elif self._mode == "circle":
            r = int(math.sqrt((ix2 - ix1) ** 2 + (iy2 - iy1) ** 2))
            cv2.circle(self._mask, (ix1, iy1), r, 1.0, -1)

        self.update()

    # ── mouse events ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self._orig_bgr is None:
            return
        if self._mode == "brush":
            self._painting = True
            self._last_pos = event.position().toPoint()
            ix, iy = self._to_img(event.position().x(), event.position().y())
            self._draw_brush_circle(ix, iy)
            self.update()
        else:
            self._drag_start = event.position().toPoint()
            self._drag_cur   = event.position().toPoint()
            self.update()

    def mouseMoveEvent(self, event):
        if self._mode == "brush":
            if self._painting and self._last_pos is not None:
                cur = event.position().toPoint()
                self._stroke_to(cur)
                self._last_pos = cur
        else:
            if self._drag_start is not None:
                self._drag_cur = event.position().toPoint()
                self.update()

    def mouseReleaseEvent(self, _event):
        if self._mode == "brush":
            self._painting = False
            self._last_pos = None
        else:
            if self._drag_start is not None:
                self._commit_shape()
            self._drag_start = None
            self._drag_cur   = None
            self.update()

    # ── drag & drop ───────────────────────────────────────────────────────────

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.splitext(path)[1].lower() in (".jpg", ".jpeg", ".png"):
                self._source_path = path
                self.load_image(path)
                if hasattr(self.parent(), "_on_canvas_image_loaded"):
                    self.parent()._on_canvas_image_loaded(path)
                break

    # ── rendering ─────────────────────────────────────────────────────────────

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(8, 12, 20))

        if self._result_bgr is None:
            painter.setPen(QColor(74, 120, 53))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter,
                "Drop image here  or  click  Open Image",
            )
            painter.end()
            return

        ox, oy, dw, dh, _ = self._img_rect()
        h, w = self._result_bgr.shape[:2]

        # Image
        rgb  = cv2.cvtColor(self._result_bgr, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.tobytes(), w, h, w * 3, QImage.Format.Format_RGB888)
        pix  = QPixmap.fromImage(qimg).scaled(
            dw, dh,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(ox, oy, pix)

        # Committed mask overlay
        if self._mask is not None and self._mask.max() > 0:
            alpha = (self._mask * 150).astype(np.uint8)
            rgba  = np.zeros((h, w, 4), dtype=np.uint8)
            rgba[:, :, 0] = 180
            rgba[:, :, 1] = 255
            rgba[:, :, 2] = 46
            rgba[:, :, 3] = alpha
            oi = QImage(rgba.tobytes(), w, h, w * 4, QImage.Format.Format_RGBA8888)
            op = QPixmap.fromImage(oi).scaled(
                dw, dh,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(ox, oy, op)

        # Live drag preview
        if self._drag_start is not None and self._drag_cur is not None:
            pen = QPen(QColor(180, 255, 46), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(180, 255, 46, 45))

            sx, sy = self._drag_start.x(), self._drag_start.y()
            cx, cy = self._drag_cur.x(),   self._drag_cur.y()

            if self._mode == "box":
                painter.drawRect(
                    min(sx, cx), min(sy, cy),
                    abs(cx - sx), abs(cy - sy),
                )
            elif self._mode == "circle":
                r = int(math.sqrt((cx - sx) ** 2 + (cy - sy) ** 2))
                painter.drawEllipse(sx - r, sy - r, r * 2, r * 2)

        painter.end()

    # ── undo helpers ──────────────────────────────────────────────────────────

    def _push_undo(self, mask_only: bool = False):
        entry = (
            self._result_bgr.copy() if not mask_only else self._result_bgr,
            self._mask.copy(),
        )
        self._undo_stack.append(entry)
        if len(self._undo_stack) > 30:
            self._undo_stack.pop(0)


# ── Mosaic Tab ────────────────────────────────────────────────────────────────

class MosaicTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_path = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_canvas_area(), stretch=1)

        undo_sc = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_sc.activated.connect(self._undo)
        self._set_mode("brush")

    # ── controls panel ────────────────────────────────────────────────────────

    def _build_controls(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("settingsPanel")
        panel.setFixedWidth(244)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(0)

        title = QLabel("◈  Mosaic Tool")
        title.setObjectName("appTitle")
        sub   = QLabel("Select areas & apply effect")
        sub.setObjectName("appSub")
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(28)

        # Open Image
        open_btn = QPushButton("Open Image")
        open_btn.setObjectName("primaryBtn")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setFixedHeight(38)
        open_btn.clicked.connect(self._open_image)
        layout.addWidget(open_btn)
        layout.addSpacing(24)

        # ── Selection Mode ────────────────────────────────────────────────────
        layout.addWidget(self._section_label("SELECTION MODE"))
        layout.addSpacing(8)
        mode_row = QHBoxLayout()
        mode_row.setSpacing(5)
        self._mode_btns: dict[str, QPushButton] = {}
        for key, label in [("brush", "Brush"), ("box", "Box"), ("circle", "Circle")]:
            btn = QPushButton(label)
            btn.setObjectName("scaleBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda _, m=key: self._set_mode(m))
            self._mode_btns[key] = btn
            mode_row.addWidget(btn)
        layout.addLayout(mode_row)
        layout.addSpacing(6)

        self._mode_hint = QLabel("Freehand circle brush")
        self._mode_hint.setStyleSheet(
            "font-size: 10px; color: #4a6a35; background: transparent;"
        )
        layout.addWidget(self._mode_hint)
        layout.addSpacing(18)

        # Brush size (only for brush mode)
        self._brush_section_lbl = self._section_label("BRUSH SIZE")
        layout.addWidget(self._brush_section_lbl)
        layout.addSpacing(8)
        self._brush_val_lbl = QLabel("30 px")
        self._brush_val_lbl.setStyleSheet(
            "font-size: 11px; color: #b4ff2e; background: transparent;"
        )
        self._brush_slider = QSlider(Qt.Orientation.Horizontal)
        self._brush_slider.setRange(5, 200)
        self._brush_slider.setValue(30)
        self._brush_slider.valueChanged.connect(self._on_brush_changed)
        layout.addWidget(self._brush_slider)
        layout.addSpacing(4)
        layout.addWidget(self._brush_val_lbl)
        layout.addSpacing(22)

        # Effect
        layout.addWidget(self._section_label("EFFECT"))
        layout.addSpacing(8)
        self._effect_combo = QComboBox()
        self._effect_combo.addItem("Pixelate (Mosaic)", "pixelate")
        self._effect_combo.addItem("Gaussian Blur",     "blur")
        layout.addWidget(self._effect_combo)
        layout.addSpacing(22)

        # Strength
        layout.addWidget(self._section_label("STRENGTH"))
        layout.addSpacing(8)
        self._strength_val_lbl = QLabel("Medium (15)")
        self._strength_val_lbl.setStyleSheet(
            "font-size: 11px; color: #b4ff2e; background: transparent;"
        )
        self._strength_slider = QSlider(Qt.Orientation.Horizontal)
        self._strength_slider.setRange(1, 50)
        self._strength_slider.setValue(15)
        self._strength_slider.valueChanged.connect(self._on_strength_changed)
        layout.addWidget(self._strength_slider)
        layout.addSpacing(4)
        layout.addWidget(self._strength_val_lbl)
        layout.addSpacing(24)

        # Apply
        apply_btn = QPushButton("▶  Apply Effect")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setFixedHeight(40)
        apply_btn.clicked.connect(self._apply_effect)
        layout.addWidget(apply_btn)
        layout.addSpacing(8)

        # Undo / Clear
        row = QHBoxLayout()
        row.setSpacing(6)
        undo_btn  = QPushButton("↩  Undo")
        clear_btn = QPushButton("✕  Clear")
        for btn in (undo_btn, clear_btn):
            btn.setObjectName("secondaryBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(34)
            row.addWidget(btn)
        undo_btn.clicked.connect(self._undo)
        clear_btn.clicked.connect(self._clear_mask)
        layout.addLayout(row)

        layout.addStretch()

        # Save
        save_btn = QPushButton("Save As New File")
        save_btn.setObjectName("primaryBtn")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(44)
        save_btn.clicked.connect(self._save_file)
        layout.addWidget(save_btn)

        return panel

    def _build_canvas_area(self) -> QWidget:
        container = QWidget()
        layout    = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._canvas = MosaicCanvas(self)
        layout.addWidget(self._canvas, stretch=1)

        self._status_lbl = QLabel("Open or drag an image to get started")
        self._status_lbl.setFixedHeight(30)
        self._status_lbl.setStyleSheet(
            "font-size: 11px; color: #4a6a35; background: #080c14;"
            "border-top: 1px solid #1a2535; padding: 0 16px;"
        )
        layout.addWidget(self._status_lbl)
        return container

    @staticmethod
    def _section_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionTitle")
        return lbl

    # ── slots ─────────────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        self._canvas.set_mode(mode)
        hints = {
            "brush":  "Freehand circle brush",
            "box":    "Drag to draw a rectangle",
            "circle": "Drag from center outward",
        }
        self._mode_hint.setText(hints[mode])

        # show/hide brush size based on mode
        visible = mode == "brush"
        self._brush_section_lbl.setVisible(visible)
        self._brush_slider.setVisible(visible)
        self._brush_val_lbl.setVisible(visible)

        # update button active state
        for key, btn in self._mode_btns.items():
            btn.setProperty("active", "true" if key == mode else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Images (*.jpg *.jpeg *.png)"
        )
        if path:
            self._load(path)

    def _on_canvas_image_loaded(self, path: str):
        self._source_path = path
        self._status_lbl.setText(
            f"Loaded: {os.path.basename(path)}  ·  Select areas, then Apply Effect"
        )

    def _load(self, path: str):
        self._source_path         = path
        self._canvas._source_path = path
        self._canvas.load_image(path)
        self._status_lbl.setText(
            f"Loaded: {os.path.basename(path)}  ·  Select areas, then Apply Effect"
        )

    def _on_brush_changed(self, v: int):
        self._brush_val_lbl.setText(f"{v} px")
        self._canvas.set_brush_size(v)

    def _on_strength_changed(self, v: int):
        level = "Light" if v < 10 else "Strong" if v > 30 else "Medium"
        self._strength_val_lbl.setText(f"{level} ({v})")

    def _apply_effect(self):
        self._canvas.apply_effect(
            self._effect_combo.currentData(),
            self._strength_slider.value(),
        )
        self._status_lbl.setText("Effect applied  ·  Continue selecting or Save As New File")

    def _undo(self):
        self._canvas.undo()
        self._status_lbl.setText("Undo")

    def _clear_mask(self):
        self._canvas.clear_mask()
        self._status_lbl.setText("Mask cleared")

    def _save_file(self):
        if not self._canvas.has_image():
            return
        src  = self._source_path or self._canvas._source_path
        base, ext = os.path.splitext(src) if src else ("output", ".png")
        default   = base + "_mosaic" + ext

        path, _ = QFileDialog.getSaveFileName(
            self, "Save As New File", default,
            "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if path:
            ok, msg = self._canvas.save_result(path)
            self._status_lbl.setText(
                f"Saved: {os.path.basename(path)}" if ok else f"Error: {msg}"
            )
