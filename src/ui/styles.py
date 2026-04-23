APP_STYLE = """
/* ── Base ── */
QMainWindow, QWidget {
    background-color: #ffffff;
    color: #0f172a;
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
    background: #f1f5f9;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #16a34a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Frame / Card ── */
QFrame#card {
    background-color: #f0fdf4;
    border: 1px solid #dcfce7;
    border-radius: 14px;
}
QFrame#settingsPanel {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}

/* ── Labels ── */
QLabel#sectionTitle {
    color: #64748b;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
}
QLabel#appTitle {
    color: #0f172a;
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
    background-color: #ffffff;
    color: #64748b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#scaleBtn:hover {
    background-color: #f0fdf4;
    color: #16a34a;
    border-color: #16a34a;
}
QPushButton#scaleBtn[active="true"] {
    background-color: #16a34a;
    color: #ffffff;
    border-color: #16a34a;
}

/* ── Method Combo ── */
QComboBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QComboBox:hover { border-color: #16a34a; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94a3b8;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    color: #0f172a;
    selection-background-color: #16a34a;
    selection-color: #ffffff;
    outline: none;
    padding: 4px;
}

/* ── Line Edit ── */
QLineEdit {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #16a34a; }
QLineEdit:hover { border-color: #cbd5e1; }

/* ── Browse Button ── */
QPushButton#browseBtn {
    background-color: #ffffff;
    color: #64748b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12px;
}
QPushButton#browseBtn:hover {
    background-color: #f0fdf4;
    color: #16a34a;
    border-color: #16a34a;
}

/* ── Primary Action Button ── */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #16a34a, stop:1 #15803d);
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
        stop:0 #15803d, stop:1 #166534);
}
QPushButton#primaryBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #166534, stop:1 #14532d);
}
QPushButton#primaryBtn:disabled {
    background: #e2e8f0;
    color: #94a3b8;
}

/* ── Secondary Button ── */
QPushButton#secondaryBtn {
    background-color: transparent;
    color: #64748b;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#secondaryBtn:hover {
    background-color: #f0fdf4;
    color: #16a34a;
    border-color: #16a34a;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #e2e8f0;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #16a34a, stop:1 #22c55e);
    border-radius: 4px;
}

/* ── Drop Zone ── */
QFrame#dropZone {
    background-color: #f8fafc;
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
}
QFrame#dropZone[drag="true"] {
    background-color: #f0fdf4;
    border-color: #16a34a;
}

/* ── Image Card ── */
QFrame#imageCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}
QFrame#imageCard:hover {
    border-color: #bbf7d0;
    background-color: #f0fdf4;
}

/* ── Remove Button ── */
QPushButton#removeBtn {
    background: transparent;
    color: #94a3b8;
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
QLabel#statusText { font-size: 11px; color: #64748b; }

/* ── Tooltip ── */
QToolTip {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px 8px;
}

/* ── Tab Bar ── */
QTabWidget#mainTabs::pane {
    border: none;
    background: #ffffff;
}
QTabWidget#mainTabs > QTabBar {
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
}
QTabBar::tab {
    background: transparent;
    color: #64748b;
    padding: 10px 28px;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
}
QTabBar::tab:selected {
    color: #16a34a;
    border-bottom: 2px solid #16a34a;
}
QTabBar::tab:hover:!selected {
    color: #0f172a;
    background: #f0fdf4;
}

/* ── Slider ── */
QSlider::groove:horizontal {
    background: #e2e8f0;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #16a34a;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #15803d;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #16a34a, stop:1 #22c55e);
    height: 4px;
    border-radius: 2px;
}

/* ── Dialog ── */
QDialog {
    background: #ffffff;
    color: #0f172a;
}
"""

STATUS_COLORS = {
    "pending":    "#94a3b8",
    "processing": "#f59e0b",
    "done":       "#16a34a",
    "error":      "#ef4444",
    "skipped":    "#94a3b8",
}

STATUS_ICONS = {
    "pending":    "○",
    "processing": "◐",
    "done":       "●",
    "error":      "✕",
    "skipped":    "–",
}
