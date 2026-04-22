APP_STYLE = """
/* ── Base ── */
QMainWindow, QWidget {
    background-color: #0d0d1a;
    color: #f1f5f9;
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
    background: #161629;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #2a2a4a;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #7c3aed; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Frame / Card ── */
QFrame#card {
    background-color: #161629;
    border: 1px solid #1e1e38;
    border-radius: 14px;
}
QFrame#settingsPanel {
    background-color: #12121f;
    border-right: 1px solid #1e1e38;
}

/* ── Labels ── */
QLabel#sectionTitle {
    color: #94a3b8;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
}
QLabel#appTitle {
    color: #f1f5f9;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
QLabel#appSub {
    color: #64748b;
    font-size: 11px;
}

/* ── Scale Buttons ── */
QPushButton#scaleBtn {
    background-color: #1e1e35;
    color: #94a3b8;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#scaleBtn:hover {
    background-color: #252545;
    color: #f1f5f9;
    border-color: #7c3aed;
}
QPushButton#scaleBtn[active="true"] {
    background-color: #7c3aed;
    color: #ffffff;
    border-color: #7c3aed;
}

/* ── Method Combo ── */
QComboBox {
    background-color: #1e1e35;
    color: #f1f5f9;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QComboBox:hover { border-color: #7c3aed; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94a3b8;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background: #1e1e35;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    color: #f1f5f9;
    selection-background-color: #7c3aed;
    outline: none;
    padding: 4px;
}

/* ── Line Edit ── */
QLineEdit {
    background-color: #1e1e35;
    color: #f1f5f9;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #7c3aed; }
QLineEdit:hover { border-color: #3b3b5e; }

/* ── Browse Button ── */
QPushButton#browseBtn {
    background-color: #1e1e35;
    color: #94a3b8;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12px;
}
QPushButton#browseBtn:hover {
    background-color: #252545;
    color: #f1f5f9;
    border-color: #7c3aed;
}

/* ── Primary Action Button ── */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #3b82f6);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 11px 28px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6d28d9, stop:1 #2563eb);
}
QPushButton#primaryBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5b21b6, stop:1 #1d4ed8);
}
QPushButton#primaryBtn:disabled {
    background: #2a2a4a;
    color: #4b5563;
}

/* ── Secondary Button ── */
QPushButton#secondaryBtn {
    background-color: transparent;
    color: #64748b;
    border: 1px solid #1e1e38;
    border-radius: 10px;
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#secondaryBtn:hover {
    background-color: #1e1e35;
    color: #f1f5f9;
    border-color: #2a2a4a;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #1e1e35;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #3b82f6);
    border-radius: 4px;
}

/* ── Drop Zone ── */
QFrame#dropZone {
    background-color: #12121f;
    border: 2px dashed #2a2a4a;
    border-radius: 16px;
}
QFrame#dropZone[drag="true"] {
    background-color: #1a0f35;
    border-color: #7c3aed;
}

/* ── Image Card ── */
QFrame#imageCard {
    background-color: #161629;
    border: 1px solid #1e1e38;
    border-radius: 10px;
}
QFrame#imageCard:hover {
    border-color: #2a2a4a;
    background-color: #1a1a30;
}

/* ── Remove Button ── */
QPushButton#removeBtn {
    background: transparent;
    color: #4b5563;
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
    background: #2d1a1a;
    color: #ef4444;
}

/* ── Status Indicator ── */
QLabel#statusDot { font-size: 11px; }
QLabel#statusText { font-size: 11px; color: #64748b; }

/* ── Tooltip ── */
QToolTip {
    background-color: #1e1e35;
    color: #f1f5f9;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    padding: 4px 8px;
}

/* ── Tab Bar ── */
QTabWidget#mainTabs::pane {
    border: none;
    background: #0d0d1a;
}
QTabWidget#mainTabs > QTabBar {
    background: #0a0a14;
    border-bottom: 1px solid #1e1e38;
}
QTabBar::tab {
    background: transparent;
    color: #475569;
    padding: 10px 28px;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}
QTabBar::tab:selected {
    color: #f1f5f9;
    border-bottom: 2px solid #7c3aed;
}
QTabBar::tab:hover:!selected {
    color: #94a3b8;
    background: #12121f;
}

/* ── Slider ── */
QSlider::groove:horizontal {
    background: #1e1e35;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #7c3aed;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #6d28d9;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #3b82f6);
    height: 4px;
    border-radius: 2px;
}
"""

STATUS_COLORS = {
    "pending":    "#64748b",
    "processing": "#f59e0b",
    "done":       "#22c55e",
    "error":      "#ef4444",
}

STATUS_ICONS = {
    "pending":    "○",
    "processing": "◐",
    "done":       "●",
    "error":      "✕",
}
