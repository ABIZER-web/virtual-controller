"""Screen 1: Welcome Screen for Setup Wizard."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from ui.steering_wheel import SteeringWheelWidget
from ui.styles import COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE, COLOR_TEXT_MUTED

class WelcomeScreen(QWidget):
    start_setup_clicked = Signal()
    skip_setup_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_demo_wheel)
        self._anim_angle = 0.0
        self._anim_dir = 1.0
        self._timer.start(30)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(24)

        # Title Card
        title_box = QVBoxLayout()
        title_box.setAlignment(Qt.AlignCenter)
        title_box.setSpacing(8)

        lbl_logo = QLabel("VIRTUAL DRIVE")
        lbl_logo.setObjectName("TitleLabel")
        lbl_logo.setStyleSheet("font-size: 38px; font-weight: 800; letter-spacing: 2px; color: #168CFF;")
        lbl_logo.setAlignment(Qt.AlignCenter)

        lbl_sub = QLabel("Your Hands. Your Steering. Your Race.")
        lbl_sub.setObjectName("SubtitleLabel")
        lbl_sub.setStyleSheet("font-size: 16px; font-weight: 500; color: #8FA3BC;")
        lbl_sub.setAlignment(Qt.AlignCenter)

        title_box.addWidget(lbl_logo)
        title_box.addWidget(lbl_sub)
        main_layout.addLayout(title_box)

        # Animated Wheel Showcase
        self.wheel_widget = SteeringWheelWidget(self)
        self.wheel_widget.setFixedSize(300, 300)
        main_layout.addWidget(self.wheel_widget, alignment=Qt.AlignCenter)

        # Description text
        lbl_desc = QLabel(
            "Experience complete webcam hand-tracked racing simulation.\n"
            "Emulates a real Xbox 360 controller with dual-wrist analog steering\n"
            "and independent finger-squeeze pedals."
        )
        lbl_desc.setStyleSheet("color: #6E8299; font-size: 13px; line-height: 1.5;")
        lbl_desc.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(lbl_desc)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(16)

        self.btn_start = QPushButton("Start Hardware Setup")
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.setFixedHeight(44)
        self.btn_start.setMinimumWidth(200)
        self.btn_start.clicked.connect(self.start_setup_clicked.emit)

        self.btn_skip = QPushButton("Skip Setup (Safe Defaults)")
        self.btn_skip.setFixedHeight(44)
        self.btn_skip.setMinimumWidth(200)
        self.btn_skip.clicked.connect(self.skip_setup_clicked.emit)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_skip)
        main_layout.addLayout(btn_layout)

    def _animate_demo_wheel(self):
        """Gentle back-and-forth demo rotation on the welcome screen."""
        self._anim_angle += self._anim_dir * 0.8
        if self._anim_angle > 35.0:
            self._anim_dir = -1.0
        elif self._anim_angle < -35.0:
            self._anim_dir = 1.0
        self.wheel_widget.set_angle(self._anim_angle, self._anim_angle / 90.0)

    def stop_animation(self):
        self._timer.stop()

