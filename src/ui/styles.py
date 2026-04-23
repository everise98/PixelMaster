APP_STYLE = """
/* ── Base ── */
QMainWindow, QWidget {
    background-color: #ffffff;
    color: #1a2e1f;
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
    background: #f0f7f2;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #c8e8d0;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #93F1A5; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Frame / Card ── */
QFrame#card {
    background-color: #f0fdf4;
    border: 1px solid #93F1A5;
    border-radius: 14px;
}
QFrame#settingsPanel {
    background-color: #f8fafb;
    border-right: 1px solid #ddeee2;
}

/* ── Labels ── */
QLabel#sectionTitle {
    color: #6b8a72;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
}
QLabel#appTitle {
    color: #1a2e1f;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
QLabel#appSub {
    color: #6b8a72;
    font-size: 11px;
}

/* ── Scale Buttons ── */
QPushButton#scaleBtn {
    background-color: #ffffff;
    color: #6b8a72;
    border: 1px solid #ddeee2;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#scaleBtn:hover {
    background-color: #f0fdf4;
    color: #1a2e1f;
    border-color: #93F1A5;
}
QPushButton#scaleBtn[active="true"] {
    background-color: #93F1A5;
    color: #0d1f10;
    border-color: #5ed47a;
}

/* ── Method Combo ── */
QComboBox {
    background-color: #ffffff;
    color: #1a2e1f;
    border: 1px solid #ddeee2;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QComboBox:hover { border-color: #93F1A5; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #93a09a;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #ddeee2;
    border-radius: 8px;
    color: #1a2e1f;
    selection-background-color: #93F1A5;
    selection-color: #0d1f10;
    outline: none;
    padding: 4px;
}

/* ── Line Edit ── */
QLineEdit {
    background-color: #ffffff;
    color: #1a2e1f;
    border: 1px solid #ddeee2;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #93F1A5; }
QLineEdit:hover { border-color: #b8dfc0; }

/* ── Browse Button ── */
QPushButton#browseBtn {
    background-color: #ffffff;
    color: #6b8a72;
    border: 1px solid #ddeee2;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12px;
}
QPushButton#browseBtn:hover {
    background-color: #f0fdf4;
    color: #1a2e1f;
    border-color: #93F1A5;
}

/* ── Primary Action Button ── */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5ed47a, stop:1 #93F1A5);
    color: #0d1f10;
    border: none;
    border-radius: 10px;
    padding: 11px 28px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #93F1A5, stop:1 #b8f5c4);
}
QPushButton#primaryBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3abf58, stop:1 #5ed47a);
}
QPushButton#primaryBtn:disabled {
    background: #e8f0ea;
    color: #a0b8a8;
}

/* ── Secondary Button ── */
QPushButton#secondaryBtn {
    background-color: transparent;
    color: #6b8a72;
    border: 1px solid #ddeee2;
    border-radius: 10px;
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#secondaryBtn:hover {
    background-color: #f0fdf4;
    color: #1a2e1f;
    border-color: #93F1A5;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #e8f0ea;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5ed47a, stop:1 #93F1A5);
    border-radius: 4px;
}

/* ── Drop Zone ── */
QFrame#dropZone {
    background-color: #f8fafb;
    border: 2px dashed #c8e8d0;
    border-radius: 16px;
}
QFrame#dropZone[drag="true"] {
    background-color: #f0fdf4;
    border-color: #93F1A5;
}

/* ── Image Card ── */
QFrame#imageCard {
    background-color: #ffffff;
    border: 1px solid #e2ebe4;
    border-radius: 10px;
}
QFrame#imageCard:hover {
    border-color: #93F1A5;
    background-color: #f0fdf4;
}

/* ── Remove Button ── */
QPushButton#removeBtn {
    background: transparent;
    color: #b0c8b8;
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
    background: #fee2e2;
    color: #ef4444;
}

/* ── Status Indicator ── */
QLabel#statusDot { font-size: 11px; }
QLabel#statusText { font-size: 11px; color: #6b8a72; }

/* ── Tooltip ── */
QToolTip {
    background-color: #1a2e1f;
    color: #f0fdf4;
    border: 1px solid #93F1A5;
    border-radius: 6px;
    padding: 4px 8px;
}

/* ── Tab Bar ── */
QTabWidget#mainTabs::pane {
    border: none;
    background: #ffffff;
}
QTabWidget#mainTabs > QTabBar {
    background: #f8fafb;
    border-bottom: 1px solid #ddeee2;
}
QTabBar::tab {
    background: transparent;
    color: #6b8a72;
    padding: 10px 28px;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}
QTabBar::tab:selected {
    color: #1a2e1f;
    border-bottom: 2px solid #93F1A5;
}
QTabBar::tab:hover:!selected {
    color: #1a2e1f;
    background: #f0fdf4;
}

/* ── Slider ── */
QSlider::groove:horizontal {
    background: #e2ebe4;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #93F1A5;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #5ed47a;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5ed47a, stop:1 #93F1A5);
    height: 4px;
    border-radius: 2px;
}

/* ── Dialog ── */
QDialog {
    background: #ffffff;
    color: #1a2e1f;
}
"""

STATUS_COLORS = {
    "pending":    "#93a09a",
    "processing": "#f59e0b",
    "done":       "#2db558",
    "error":      "#ef4444",
    "skipped":    "#93a09a",
}

STATUS_ICONS = {
    "pending":    "○",
    "processing": "◐",
    "done":       "●",
    "error":      "✕",
    "skipped":    "–",
}
