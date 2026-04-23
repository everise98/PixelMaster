APP_STYLE = """
/* ── Base ── */
QMainWindow, QWidget {
    background-color: #080c14;
    color: #edffd0;
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
    background: #0c1020;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #1e3010;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #b4ff2e; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Frame / Card ── */
QFrame#card {
    background-color: #0f1a08;
    border: 1px solid #2e4a0a;
    border-radius: 14px;
}
QFrame#settingsPanel {
    background-color: #0c1020;
    border-right: 1px solid #1a2535;
}

/* ── Labels ── */
QLabel#sectionTitle {
    color: #4a7a35;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
}
QLabel#appTitle {
    color: #b4ff2e;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
QLabel#appSub {
    color: #5c7a4a;
    font-size: 11px;
}

/* ── Scale Buttons ── */
QPushButton#scaleBtn {
    background-color: #0f1a0a;
    color: #5c7a4a;
    border: 1px solid #1e3010;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#scaleBtn:hover {
    background-color: #162008;
    color: #b4ff2e;
    border-color: #b4ff2e;
}
QPushButton#scaleBtn[active="true"] {
    background-color: #b4ff2e;
    color: #080c14;
    border-color: #b4ff2e;
}

/* ── Method Combo ── */
QComboBox {
    background-color: #0f1a0a;
    color: #edffd0;
    border: 1px solid #1e3010;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QComboBox:hover { border-color: #b4ff2e; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #5c7a4a;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background: #0c1020;
    border: 1px solid #1e3010;
    border-radius: 8px;
    color: #edffd0;
    selection-background-color: #b4ff2e;
    selection-color: #080c14;
    outline: none;
    padding: 4px;
}

/* ── Line Edit ── */
QLineEdit {
    background-color: #0f1a0a;
    color: #edffd0;
    border: 1px solid #1e3010;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #b4ff2e; }
QLineEdit:hover { border-color: #3a5a20; }

/* ── Browse Button ── */
QPushButton#browseBtn {
    background-color: #0f1a0a;
    color: #5c7a4a;
    border: 1px solid #1e3010;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12px;
}
QPushButton#browseBtn:hover {
    background-color: #162008;
    color: #b4ff2e;
    border-color: #b4ff2e;
}

/* ── Primary Action Button ── */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #80cc00, stop:1 #b4ff2e);
    color: #080c14;
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
    background: #1a2535;
    color: #3a5030;
}

/* ── Secondary Button ── */
QPushButton#secondaryBtn {
    background-color: transparent;
    color: #5c7a4a;
    border: 1px solid #1e3010;
    border-radius: 10px;
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#secondaryBtn:hover {
    background-color: #0f1a08;
    color: #b4ff2e;
    border-color: #b4ff2e;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #1a2535;
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
    background-color: #0c1020;
    border: 2px dashed #1e3010;
    border-radius: 16px;
}
QFrame#dropZone[drag="true"] {
    background-color: #0f1a08;
    border-color: #b4ff2e;
}

/* ── Image Card ── */
QFrame#imageCard {
    background-color: #0d1828;
    border: 1px solid #1a2535;
    border-radius: 10px;
}
QFrame#imageCard:hover {
    border-color: #2e4a0a;
    background-color: #0f1a08;
}

/* ── Remove Button ── */
QPushButton#removeBtn {
    background: transparent;
    color: #3a5030;
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
    background: #2a0a0a;
    color: #ff3355;
}

/* ── Status Indicator ── */
QLabel#statusDot { font-size: 11px; }
QLabel#statusText { font-size: 11px; color: #5c7a4a; }

/* ── Tooltip ── */
QToolTip {
    background-color: #0c1020;
    color: #edffd0;
    border: 1px solid #b4ff2e;
    border-radius: 6px;
    padding: 4px 8px;
}

/* ── Tab Bar ── */
QTabWidget#mainTabs::pane {
    border: none;
    background: #080c14;
}
QTabWidget#mainTabs > QTabBar {
    background: #0c1020;
    border-bottom: 1px solid #1a2535;
}
QTabBar::tab {
    background: transparent;
    color: #4a6a35;
    padding: 10px 28px;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}
QTabBar::tab:selected {
    color: #b4ff2e;
    border-bottom: 2px solid #b4ff2e;
}
QTabBar::tab:hover:!selected {
    color: #d4ff6e;
    background: #0f1a08;
}

/* ── Slider ── */
QSlider::groove:horizontal {
    background: #1a2535;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #b4ff2e;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #d4ff6e;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #80cc00, stop:1 #b4ff2e);
    height: 4px;
    border-radius: 2px;
}

/* ── Dialog ── */
QDialog {
    background: #0a0f1a;
    color: #edffd0;
}
"""

STATUS_COLORS = {
    "pending":    "#4a6a35",
    "processing": "#ffaa00",
    "done":       "#b4ff2e",
    "error":      "#ff3355",
    "skipped":    "#4a6a35",
}

STATUS_ICONS = {
    "pending":    "○",
    "processing": "◐",
    "done":       "●",
    "error":      "✕",
    "skipped":    "–",
}
