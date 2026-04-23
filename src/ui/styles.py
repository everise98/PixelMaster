APP_STYLE = """
/* ── Base ── */
QMainWindow, QWidget {
    background-color: #f0f4f0;
    color: #0f1a08;
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    font-size: 13px;
}

QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* ── Scrollbar ── */
QScrollBar:vertical {
    background: #e4ede4;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #c0d4b0;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #80cc00; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Frame / Card ── */
QFrame#card {
    background-color: #eaffd0;
    border: 1px solid #b4ff2e;
    border-radius: 14px;
}
QFrame#settingsPanel {
    background-color: #e8f0e0;
    border-right: 1px solid #c8ddb0;
}

/* ── Labels ── */
QLabel#sectionTitle {
    color: #4a7a1a;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
}
QLabel#appTitle {
    color: #1a4a00;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
QLabel#appSub {
    color: #5a7a40;
    font-size: 11px;
}

/* ── Scale Buttons ── */
QPushButton#scaleBtn {
    background-color: #ffffff;
    color: #5a7a40;
    border: 1px solid #c0d4a0;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#scaleBtn:hover {
    background-color: #eaffd0;
    color: #1a4a00;
    border-color: #80cc00;
}
QPushButton#scaleBtn[active="true"] {
    background-color: #b4ff2e;
    color: #0a1e00;
    border-color: #80cc00;
}

/* ── Method Combo ── */
QComboBox {
    background-color: #ffffff;
    color: #0f1a08;
    border: 1px solid #c0d4a0;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QComboBox:hover { border-color: #80cc00; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7a9a60;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #c0d4a0;
    border-radius: 8px;
    color: #0f1a08;
    selection-background-color: #b4ff2e;
    selection-color: #0a1e00;
    outline: none;
    padding: 4px;
}

/* ── Line Edit ── */
QLineEdit {
    background-color: #ffffff;
    color: #0f1a08;
    border: 1px solid #c0d4a0;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #80cc00; }
QLineEdit:hover { border-color: #a0c070; }

/* ── Browse Button ── */
QPushButton#browseBtn {
    background-color: #ffffff;
    color: #5a7a40;
    border: 1px solid #c0d4a0;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12px;
}
QPushButton#browseBtn:hover {
    background-color: #eaffd0;
    color: #1a4a00;
    border-color: #80cc00;
}

/* ── Primary Action Button ── */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #80cc00, stop:1 #b4ff2e);
    color: #0a1e00;
    border: none;
    border-radius: 10px;
    padding: 11px 28px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #b4ff2e, stop:1 #d4ff6e);
}
QPushButton#primaryBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5a9900, stop:1 #80cc00);
}
QPushButton#primaryBtn:disabled {
    background: #d0ddc0;
    color: #8aaa70;
}

/* ── Secondary Button ── */
QPushButton#secondaryBtn {
    background-color: transparent;
    color: #5a7a40;
    border: 1px solid #c0d4a0;
    border-radius: 10px;
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#secondaryBtn:hover {
    background-color: #eaffd0;
    color: #1a4a00;
    border-color: #80cc00;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #d0ddc0;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #80cc00, stop:1 #b4ff2e);
    border-radius: 4px;
}

/* ── Drop Zone ── */
QFrame#dropZone {
    background-color: #f8fff0;
    border: 2px dashed #c0d4a0;
    border-radius: 16px;
}
QFrame#dropZone[drag="true"] {
    background-color: #eaffd0;
    border-color: #b4ff2e;
}

/* ── Image Card ── */
QFrame#imageCard {
    background-color: #ffffff;
    border: 1px solid #d0ddc0;
    border-radius: 10px;
}
QFrame#imageCard:hover {
    border-color: #b4ff2e;
    background-color: #f4ffe8;
}

/* ── Remove Button ── */
QPushButton#removeBtn {
    background: transparent;
    color: #a0b890;
    border: none;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    padding: 0px;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#removeBtn:hover {
    background: #ffe0e0;
    color: #ef4444;
}

/* ── Status Indicator ── */
QLabel#statusDot { font-size: 11px; }
QLabel#statusText { font-size: 11px; color: #5a7a40; }

/* ── Tooltip ── */
QToolTip {
    background-color: #0f1a08;
    color: #edffd0;
    border: 1px solid #b4ff2e;
    border-radius: 6px;
    padding: 4px 8px;
}

/* ── Tab Bar ── */
QTabWidget#mainTabs::pane {
    border: none;
    background: #f0f4f0;
}
QTabWidget#mainTabs > QTabBar {
    background: #e8f0e0;
    border-bottom: 1px solid #c8ddb0;
}
QTabBar::tab {
    background: transparent;
    color: #6a9050;
    padding: 10px 28px;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}
QTabBar::tab:selected {
    color: #1a4a00;
    border-bottom: 2px solid #80cc00;
}
QTabBar::tab:hover:!selected {
    color: #1a4a00;
    background: #eaffd0;
}

/* ── Slider ── */
QSlider::groove:horizontal {
    background: #d0ddc0;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #80cc00;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #b4ff2e;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #80cc00, stop:1 #b4ff2e);
    height: 4px;
    border-radius: 2px;
}

/* ── Dialog ── */
QDialog {
    background: #f0f4f0;
    color: #0f1a08;
}
"""

STATUS_COLORS = {
    "pending":    "#8aaa70",
    "processing": "#e09000",
    "done":       "#3a8a00",
    "error":      "#e03040",
    "skipped":    "#8aaa70",
}

STATUS_ICONS = {
    "pending":    "○",
    "processing": "◐",
    "done":       "●",
    "error":      "✕",
    "skipped":    "–",
}
