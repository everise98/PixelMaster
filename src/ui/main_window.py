import os
import sys
import ctypes
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QLineEdit, QComboBox,
    QScrollArea, QFileDialog, QProgressBar, QDialog, QTabWidget,
)
from PyQt6.QtCore import Qt

from src.ui.styles import APP_STYLE
from src.ui.drop_zone import DropZone
from src.ui.image_card import ImageCard
from src.core.upscaler import get_image_info, METHODS
from src.core.worker import UpscaleWorker

APP_NAME    = "Pixel Master"
APP_VERSION = "1.0.0"
AUTHOR      = "Youngkee Kim"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  v{APP_VERSION}")
        self.setMinimumSize(920, 640)
        self.resize(1080, 720)
        self.setStyleSheet(APP_STYLE)

        self._queue: dict[str, ImageCard] = {}
        self._worker: UpscaleWorker | None = None
        self._output_folder = ""
        self._scale = 4
        self._scale_btns: dict[int, QPushButton] = {}

        self._setup_ui()
        self._enable_dark_titlebar()

    # ── UI construction ───────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Tab bar ──────────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setObjectName("mainTabs")

        # Tab 1 — Upscaler
        upscaler_page = QWidget()
        up_layout = QHBoxLayout(upscaler_page)
        up_layout.setContentsMargins(0, 0, 0, 0)
        up_layout.setSpacing(0)
        up_layout.addWidget(self._build_settings_panel())
        up_layout.addWidget(self._build_content_panel(), stretch=1)
        self._tabs.addTab(upscaler_page, "✦  Upscaler")

        # Tab 2 — Mosaic
        from src.ui.mosaic_tab import MosaicTab
        self._tabs.addTab(MosaicTab(), "◈  Mosaic")

        # Tab 3 — Background Remover
        from src.ui.bg_remover_tab import BgRemoverTab
        self._tabs.addTab(BgRemoverTab(), "✂  BG Remover")

        root_layout.addWidget(self._tabs, stretch=1)
        root_layout.addWidget(self._build_footer())

    # ── Settings panel ────────────────────────────────────────────────────────

    def _build_settings_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("settingsPanel")
        panel.setFixedWidth(244)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(0)

        logo = QLabel(f"✦  {APP_NAME}")
        logo.setObjectName("appTitle")
        sub = QLabel(f"Image Upscaler  ·  v{APP_VERSION}")
        sub.setObjectName("appSub")

        layout.addWidget(logo)
        layout.addWidget(sub)
        layout.addSpacing(28)

        # Scale factor
        layout.addWidget(self._section_label("SCALE FACTOR"))
        layout.addSpacing(8)
        scale_row = QHBoxLayout()
        scale_row.setSpacing(6)
        for s in (4, 8, 16):
            btn = QPushButton(f"{s}×")
            btn.setObjectName("scaleBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.clicked.connect(lambda _, v=s: self._set_scale(v))
            self._scale_btns[s] = btn
            scale_row.addWidget(btn)
        layout.addLayout(scale_row)
        self._set_scale(4)
        layout.addSpacing(22)

        # Upscale method
        layout.addWidget(self._section_label("UPSCALE METHOD"))
        layout.addSpacing(8)
        self._method_combo = QComboBox()
        for key, label in METHODS.items():
            self._method_combo.addItem(label, key)
        self._method_combo.setCurrentIndex(5)   # default: Real-ESRGAN General
        layout.addWidget(self._method_combo)
        layout.addSpacing(4)

        method_hint = QLabel("Real-ESRGAN General: recommended · fast AI\nReal-ESRGAN Plus: best quality · slower\nMulti-scale: no AI · fastest")
        method_hint.setStyleSheet(
            "font-size: 10px; color: #4a6a35; background: transparent; line-height: 1.4;"
        )
        layout.addWidget(method_hint)
        layout.addSpacing(22)

        # Output suffix
        layout.addWidget(self._section_label("OUTPUT FILENAME SUFFIX"))
        layout.addSpacing(8)
        self._suffix_edit = QLineEdit("_upscaling")
        self._suffix_edit.setPlaceholderText("e.g.  _upscaling")
        layout.addWidget(self._suffix_edit)
        layout.addSpacing(22)

        # Output folder
        layout.addWidget(self._section_label("OUTPUT FOLDER"))
        layout.addSpacing(8)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("browseBtn")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setFixedHeight(34)
        browse_btn.clicked.connect(self._browse_folder)
        layout.addWidget(browse_btn)

        self._folder_label = QLabel("Same as source file")
        self._folder_label.setStyleSheet(
            "font-size: 10px; color: #4a6a35; background: transparent;"
        )
        self._folder_label.setWordWrap(True)
        layout.addSpacing(4)
        layout.addWidget(self._folder_label)

        layout.addStretch()

        reset_btn = QPushButton("↺  Reset to source folder")
        reset_btn.setObjectName("secondaryBtn")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setFixedHeight(34)
        reset_btn.clicked.connect(self._reset_folder)
        layout.addWidget(reset_btn)

        return panel

    # ── Content panel ─────────────────────────────────────────────────────────

    def _build_content_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        self._drop_zone = DropZone()
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        layout.addWidget(self._drop_zone)

        # Queue header
        queue_header = QHBoxLayout()
        self._queue_title = QLabel("QUEUE  ·  0 images")
        self._queue_title.setObjectName("sectionTitle")
        clear_btn = QPushButton("Clear All")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setFixedHeight(30)
        clear_btn.clicked.connect(self._clear_queue)
        queue_header.addWidget(self._queue_title)
        queue_header.addStretch()
        queue_header.addWidget(clear_btn)
        layout.addLayout(queue_header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        self._queue_widget = QWidget()
        self._queue_widget.setStyleSheet("background: transparent;")
        self._queue_layout = QVBoxLayout(self._queue_widget)
        self._queue_layout.setContentsMargins(0, 0, 0, 0)
        self._queue_layout.setSpacing(6)

        self._empty_label = QLabel("Add images above to get started")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(
            "font-size: 12px; color: #4a6a35; background: transparent; padding: 20px;"
        )
        self._queue_layout.addWidget(self._empty_label)
        self._queue_layout.addStretch()

        scroll.setWidget(self._queue_widget)
        layout.addWidget(scroll, stretch=1)

        # Action buttons
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self._count_label = QLabel("")
        self._count_label.setStyleSheet(
            "font-size: 12px; color: #4a6a35; background: transparent;"
        )
        action_row.addWidget(self._count_label)
        action_row.addStretch()

        self._open_folder_btn = QPushButton("Open Output Folder")
        self._open_folder_btn.setObjectName("secondaryBtn")
        self._open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_folder_btn.setFixedHeight(44)
        self._open_folder_btn.setVisible(False)
        self._open_folder_btn.clicked.connect(self._open_output_folder)
        action_row.addWidget(self._open_folder_btn)

        self._start_btn = QPushButton("▶  Start Processing")
        self._start_btn.setObjectName("primaryBtn")
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.setFixedHeight(44)
        self._start_btn.setEnabled(False)
        self._start_btn.clicked.connect(self._start_processing)
        action_row.addWidget(self._start_btn)

        layout.addLayout(action_row)
        return container

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet("background-color: #060a10; border-top: 1px solid #b4ff2e;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet(
            "font-size: 10px; color: #b4ff2e; background: transparent;"
        )
        self._status_text = QLabel("Ready")
        self._status_text.setStyleSheet(
            "font-size: 11px; color: #4a6a35; background: transparent;"
        )

        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedWidth(160)
        self._progress_bar.setFixedHeight(5)
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)

        author_label = QLabel(AUTHOR)
        author_label.setStyleSheet(
            "font-size: 10px; color: #3a5a30; background: transparent; letter-spacing: 0.5px;"
        )

        layout.addWidget(self._status_dot)
        layout.addWidget(self._status_text)
        layout.addStretch()
        layout.addWidget(self._progress_bar)
        layout.addSpacing(16)
        layout.addWidget(author_label)

        return bar

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _section_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionTitle")
        return lbl

    def _set_scale(self, value: int):
        self._scale = value
        for s, btn in self._scale_btns.items():
            btn.setProperty("active", "true" if s == value else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _update_queue_ui(self):
        count = len(self._queue)
        self._queue_title.setText(
            f"QUEUE  ·  {count} image{'s' if count != 1 else ''}"
        )
        self._count_label.setText(
            f"{count} image{'s' if count != 1 else ''} ready" if count else ""
        )
        self._start_btn.setEnabled(count > 0 and self._worker is None)
        self._empty_label.setVisible(count == 0)
        if count:
            self._start_btn.setText(
                f"▶  Process {count} Image{'s' if count != 1 else ''}"
            )

    def _set_status(self, text: str, color: str = "#64748b"):
        self._status_text.setText(text)
        self._status_dot.setStyleSheet(
            f"font-size: 10px; color: {color}; background: transparent;"
        )

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_files_dropped(self, paths: list[str]):
        added = 0
        for p in paths:
            if p in self._queue:
                continue
            try:
                w, h, _ = get_image_info(p)
            except Exception:
                continue
            card = ImageCard(p, w, h)
            card.remove_requested.connect(self._remove_image)
            card.preview_requested.connect(self._open_preview)
            self._queue[p] = card
            self._queue_layout.insertWidget(self._queue_layout.count() - 1, card)
            added += 1

        if added:
            self._update_queue_ui()
            self._set_status(f"Added {added} image{'s' if added != 1 else ''}", "#16a34a")

    def _remove_image(self, path: str):
        if path in self._queue:
            card = self._queue.pop(path)
            card.setParent(None)
            card.deleteLater()
            self._update_queue_ui()

    def _clear_queue(self):
        for card in list(self._queue.values()):
            card.setParent(None)
            card.deleteLater()
        self._queue.clear()
        self._update_queue_ui()
        self._progress_bar.setValue(0)
        self._set_status("Queue cleared", "#64748b")
        self._open_folder_btn.setVisible(False)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self._output_folder or ""
        )
        if folder:
            self._output_folder = folder
            short = folder if len(folder) <= 32 else "…" + folder[-29:]
            self._folder_label.setText(short)
            self._folder_label.setToolTip(folder)
            self._folder_label.setStyleSheet(
                "font-size: 10px; color: #b4ff2e; background: transparent;"
            )

    def _reset_folder(self):
        self._output_folder = ""
        self._folder_label.setText("Same as source file")
        self._folder_label.setToolTip("")
        self._folder_label.setStyleSheet(
            "font-size: 10px; color: #4a6a35; background: transparent;"
        )

    def _start_processing(self):
        if not self._queue:
            return
        suffix = self._suffix_edit.text().strip() or "_upscaling"
        method_key = self._method_combo.currentData()

        self._worker = UpscaleWorker(
            tasks=list(self._queue.keys()),
            scale=self._scale,
            method=method_key,
            output_suffix=suffix,
            output_folder=self._output_folder,
        )
        self._worker.image_started.connect(self._on_image_started)
        self._worker.preview_ready.connect(self._on_preview_ready)
        self._worker.image_done.connect(self._on_image_done)
        self._worker.progress.connect(self._progress_bar.setValue)
        self._worker.all_done.connect(self._on_all_done)
        self._worker.finished.connect(self._worker.deleteLater)

        self._start_btn.setEnabled(False)
        self._start_btn.setText("Processing…")
        self._set_status("Processing images…", "#f59e0b")
        self._open_folder_btn.setVisible(False)
        self._worker.start()

    def _on_image_started(self, path: str):
        if path in self._queue:
            self._queue[path].set_status("processing")

    def _on_image_done(self, path: str, success: bool, msg: str):
        if path in self._queue:
            if success:
                status = "done"
            elif msg == "Skipped":
                status = "skipped"
            else:
                status = "error"
            self._queue[path].set_status(status, msg)

    def _on_all_done(self, saved: int, errored: int, skipped: int):
        self._worker = None
        self._start_btn.setEnabled(False)
        self._start_btn.setText("✓  Done")
        self._open_folder_btn.setVisible(saved > 0)

        parts = []
        if saved:    parts.append(f"✓ {saved} saved")
        if skipped:  parts.append(f"{skipped} skipped")
        if errored:  parts.append(f"{errored} failed")
        color = "#22c55e" if errored == 0 else "#f59e0b"
        self._set_status("  ·  ".join(parts) or "Done", color)

    def _on_preview_ready(self, input_path: str, temp_path: str, uid: str):
        """Called from worker (via signal) — runs on main thread."""
        from src.ui.preview_dialog import PreviewDialog
        method_label = self._method_combo.currentText()
        dlg = PreviewDialog(
            input_path, temp_path, self._scale, method_label,
            mode="confirm", parent=self,
        )
        save = dlg.exec() == QDialog.DialogCode.Accepted
        self._worker.confirm(uid, save)

    def _open_preview(self, input_path: str, output_path: str):
        """Called when user clicks Preview on a completed card."""
        from src.ui.preview_dialog import PreviewDialog
        method_label = self._method_combo.currentText()
        dlg = PreviewDialog(
            input_path, output_path, self._scale, method_label,
            mode="preview", parent=self,
        )
        dlg.exec()

    def _open_output_folder(self):
        folder = self._output_folder
        if not folder:
            paths = list(self._queue.keys())
            folder = os.path.dirname(paths[0]) if paths else os.path.expanduser("~")
        os.startfile(folder)

    # ── Windows dark titlebar ─────────────────────────────────────────────────

    def _enable_dark_titlebar(self):
        if sys.platform != "win32":
            return
        try:
            hwnd = int(self.winId())
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
            )
        except Exception:
            pass
