"""Screen 3: Two-Hand Detection Verification for Setup Wizard."""
import cv2
import numpy as np
from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from ui.styles import COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE

class HandSetupScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title_box = QVBoxLayout()
        lbl_title = QLabel("TWO-HAND DETECTION VERIFICATION")
        lbl_title.setObjectName("HeaderLabel")
        lbl_sub = QLabel("Raise both hands in front of the camera as if holding an imaginary steering wheel.")
        lbl_sub.setObjectName("SubtitleLabel")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        layout.addLayout(title_box)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Video Preview Frame
        preview_card = QFrame()
        preview_card.setObjectName("PanelCard")
        prev_layout = QVBoxLayout(preview_card)
        prev_layout.setContentsMargins(10, 10, 10, 10)

        self.preview_label = QLabel("Awaiting hand tracking stream...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #0c1017; border-radius: 8px; color: #6E8299;")
        self.preview_label.setFixedSize(520, 360)
        prev_layout.addWidget(self.preview_label)
        content_layout.addWidget(preview_card, stretch=2)

        # Status and Telemetry Panel
        status_card = QFrame()
        status_card.setObjectName("PanelCard")
        stat_layout = QVBoxLayout(status_card)
        stat_layout.setSpacing(16)
        stat_layout.setContentsMargins(16, 16, 16, 16)

        # Left Hand Status Pill
        self.card_left = QFrame()
        self.card_left.setObjectName("PanelCardAlt")
        cl_layout = QVBoxLayout(self.card_left)
        self.lbl_left_status = QLabel("LEFT HAND: Searching...")
        self.lbl_left_status.setStyleSheet("font-weight: bold; color: #FF3D00;")
        self.bar_left_conf = QProgressBar()
        self.bar_left_conf.setRange(0, 100)
        self.bar_left_conf.setValue(0)
        cl_layout.addWidget(self.lbl_left_status)
        cl_layout.addWidget(self.bar_left_conf)

        # Right Hand Status Pill
        self.card_right = QFrame()
        self.card_right.setObjectName("PanelCardAlt")
        cr_layout = QVBoxLayout(self.card_right)
        self.lbl_right_status = QLabel("RIGHT HAND: Searching...")
        self.lbl_right_status.setStyleSheet("font-weight: bold; color: #FF3D00;")
        self.bar_right_conf = QProgressBar()
        self.bar_right_conf.setRange(0, 100)
        self.bar_right_conf.setValue(0)
        cr_layout.addWidget(self.lbl_right_status)
        cr_layout.addWidget(self.bar_right_conf)

        # Guidance Box
        self.lbl_guidance = QLabel(
            "Instructions:\n"
            "• Hold both hands up at shoulder height\n"
            "• Keep knuckles and palms facing the camera\n"
            "• Keep hands inside the camera frame\n"
            "• Ensure adequate room lighting"
        )
        self.lbl_guidance.setStyleSheet("color: #8FA3BC; font-size: 12px; line-height: 1.6;")

        stat_layout.addWidget(self.card_left)
        stat_layout.addWidget(self.card_right)
        stat_layout.addWidget(self.lbl_guidance)
        stat_layout.addStretch()

        content_layout.addWidget(status_card, stretch=1)
        layout.addLayout(content_layout)

    def update_frame_and_detection(self, annotated_bgr: np.ndarray, info: Dict[str, Any]):
        # Update video preview
        if annotated_bgr is not None:
            h, w, ch = annotated_bgr.shape
            bytes_per_line = ch * w
            rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg)
            scaled = pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled)

        # Update Left Hand
        if info.get("left_detected", False):
            conf = int(info.get("left_confidence", 0.95) * 100)
            self.lbl_left_status.setText(f"LEFT HAND: Detected ({conf}%)")
            self.lbl_left_status.setStyleSheet(f"font-weight: bold; color: {COLOR_ACCENT_GREEN};")
            self.bar_left_conf.setValue(conf)
        else:
            self.lbl_left_status.setText("LEFT HAND: Not Detected")
            self.lbl_left_status.setStyleSheet(f"font-weight: bold; color: {COLOR_ACCENT_RED};")
            self.bar_left_conf.setValue(0)

        # Update Right Hand
        if info.get("right_detected", False):
            conf = int(info.get("right_confidence", 0.95) * 100)
            self.lbl_right_status.setText(f"RIGHT HAND: Detected ({conf}%)")
            self.lbl_right_status.setStyleSheet(f"font-weight: bold; color: {COLOR_ACCENT_GREEN};")
            self.bar_right_conf.setValue(conf)
        else:
            self.lbl_right_status.setText("RIGHT HAND: Not Detected")
            self.lbl_right_status.setStyleSheet(f"font-weight: bold; color: {COLOR_ACCENT_RED};")
            self.bar_right_conf.setValue(0)

