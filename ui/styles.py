"""Premium Motorsport Design System and QSS Styling for Virtual Drive."""

COLOR_BG = "#0A0E17"
COLOR_PANEL = "#111827"
COLOR_PANEL_ALT = "#1A2234"
COLOR_PANEL_BORDER = "#243247"
COLOR_PANEL_HOVER = "#232F46"

COLOR_ACCENT_BLUE = "#00A8FF"
COLOR_ACCENT_BLUE_HOVER = "#2EB8FF"
COLOR_ACCENT_ORANGE = "#FF6B00"
COLOR_ACCENT_ORANGE_HOVER = "#FF8533"
COLOR_ACCENT_GREEN = "#00E676"
COLOR_ACCENT_RED = "#FF1744"

COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#94A3B8"
COLOR_TEXT_MUTED = "#64748B"

GLOBAL_STYLE = f"""
QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT_PRIMARY};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
    font-size: 13px;
}}

/* Window & Panels */
QMainWindow {{
    background-color: {COLOR_BG};
}}

QFrame#PanelCard {{
    background-color: {COLOR_PANEL};
    border: 1px solid {COLOR_PANEL_BORDER};
    border-radius: 12px;
}}

QFrame#PanelCardAlt {{
    background-color: {COLOR_PANEL_ALT};
    border: 1px solid {COLOR_PANEL_BORDER};
    border-radius: 10px;
}}

QFrame#TelemetryCard {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #141C2C, stop:1 #0F1623);
    border: 1px solid {COLOR_PANEL_BORDER};
    border-radius: 12px;
}}

/* Typography */
QLabel {{
    background-color: transparent;
    color: {COLOR_TEXT_PRIMARY};
}}

QLabel#TitleLabel {{
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 2px;
}}

QLabel#SubtitleLabel {{
    font-size: 13px;
    color: {COLOR_TEXT_SECONDARY};
}}

QLabel#HeaderLabel {{
    font-size: 15px;
    font-weight: 700;
    color: {COLOR_ACCENT_BLUE};
    letter-spacing: 0.5px;
}}

QLabel#SectionHeader {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: {COLOR_TEXT_SECONDARY};
}}

/* Buttons */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #151E2D);
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_PANEL_BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #28374F, stop:1 #1C273B);
    border-color: {COLOR_ACCENT_BLUE};
    color: #FFFFFF;
}}

QPushButton:pressed {{
    background: #0F1724;
    border-color: #0077B6;
}}

QPushButton#PrimaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0084FF, stop:1 #0055D4);
    color: #FFFFFF;
    border: 1px solid #33A1FF;
    border-radius: 8px;
    font-weight: 700;
}}

QPushButton#PrimaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A94FF, stop:1 #0066F0);
    border-color: #80C8FF;
}}

QPushButton#PrimaryButton:pressed {{
    background: #0044AA;
}}

QPushButton#OrangeButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF6B00, stop:1 #D94800);
    color: #FFFFFF;
    border: 1px solid #FF8C33;
    border-radius: 8px;
    font-weight: 700;
}}

QPushButton#OrangeButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF8020, stop:1 #F05500);
    border-color: #FFB380;
}}

QPushButton#EmergencyButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D50000, stop:1 #9B0000);
    color: #FFFFFF;
    border: 2px solid #FF5252;
    border-radius: 8px;
    font-weight: 800;
    font-size: 13px;
    padding: 8px 16px;
    letter-spacing: 1px;
}}

QPushButton#EmergencyButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF1744, stop:1 #C50024);
    border-color: #FFFFFF;
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 6px;
    background: #141C2B;
    border: 1px solid #1E293B;
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0055D4, stop:1 {COLOR_ACCENT_BLUE});
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: #FFFFFF;
    border: 2px solid {COLOR_ACCENT_BLUE};
    width: 16px;
    height: 16px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {COLOR_ACCENT_BLUE_HOVER};
    border-color: #FFFFFF;
}}

/* Progress Bars */
QProgressBar {{
    border: 1px solid {COLOR_PANEL_BORDER};
    border-radius: 6px;
    background-color: #0E1522;
    text-align: center;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 11px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0066DD, stop:1 {COLOR_ACCENT_BLUE});
    border-radius: 5px;
}}

/* ComboBox */
QComboBox {{
    background-color: {COLOR_PANEL_ALT};
    border: 1px solid {COLOR_PANEL_BORDER};
    border-radius: 6px;
    padding: 6px 12px;
    color: #FFFFFF;
    font-weight: 500;
}}

QComboBox:hover {{
    border-color: {COLOR_ACCENT_BLUE};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLOR_PANEL};
    border: 1px solid {COLOR_PANEL_BORDER};
    selection-background-color: #0066CC;
    selection-color: #FFFFFF;
    color: #FFFFFF;
    padding: 4px;
}}

/* CheckBoxes */
QCheckBox {{
    spacing: 8px;
    color: #FFFFFF;
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {COLOR_PANEL_BORDER};
    background-color: {COLOR_PANEL_ALT};
}}

QCheckBox::indicator:hover {{
    border-color: {COLOR_ACCENT_BLUE};
}}

QCheckBox::indicator:checked {{
    background-color: {COLOR_ACCENT_BLUE};
    border-color: #80C8FF;
}}

/* ScrollBars */
QScrollBar:vertical {{
    background: #0B0F19;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: #1E293B;
    min-height: 20px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: #334155;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""
