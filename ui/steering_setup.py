"""Screen 4 & Screen 7: Steering Calibration & Sensitivity Tuning."""
import numpy as np
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider,
    QComboBox, QFrame, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from ui.steering_wheel import SteeringWheelWidget
from core.calibration_manager import calibration_manager
from core.sensitivity_manager import SensitivityManager
from core.steering_engine import SteeringEngine
from utils.config_manager import config_manager
from ui.styles import COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE, COLOR_ACCENT_GREEN

class SteeringSetupScreen(QWidget):
    calibration_updated = Signal()

    def __init__(self, steering_engine: SteeringEngine, sensitivity_mgr: SensitivityManager, parent=None):
        super().__init__(parent)
        self.steering_engine = steering_engine
        self.sensitivity_mgr = sensitivity_mgr
        self.calib_step = 0  # 0: Neutral, 1: Left, 2: Right, 3: Completed
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)

        title_box = QVBoxLayout()
        lbl_title = QLabel("DUAL-HAND STEERING CALIBRATION")
        lbl_title.setObjectName("HeaderLabel")
        lbl_sub = QLabel("Calibrate neutral orientation, rotation range, and tune responsiveness.")
        lbl_sub.setObjectName("SubtitleLabel")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        main_layout.addLayout(title_box)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left Column: Calibration Workflow Card
        calib_card = QFrame()
        calib_card.setObjectName("PanelCard")
        calib_layout = QVBoxLayout(calib_card)
        calib_layout.setSpacing(14)
        calib_layout.setContentsMargins(16, 16, 16, 16)

        lbl_flow_title = QLabel("Step-by-Step Calibration")
        lbl_flow_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #168CFF;")
        calib_layout.addWidget(lbl_flow_title)

        # Instructions Banner
        self.lbl_instruction = QLabel("Step 1: Hold hands level in the neutral steering position.")
        self.lbl_instruction.setStyleSheet("background-color: #1C2635; padding: 10px; border-radius: 6px; font-weight: 600;")
        calib_layout.addWidget(self.lbl_instruction)

        # Angle status
        self.lbl_live_raw = QLabel("Current Orientation Angle: 0.0°")
        self.lbl_live_raw.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        calib_layout.addWidget(self.lbl_live_raw)

        # Action Buttons
        self.btn_rec_neutral = QPushButton("1. Record Neutral Center")
        self.btn_rec_neutral.setObjectName("PrimaryButton")
        self.btn_rec_neutral.clicked.connect(self._record_neutral)

        self.btn_rec_left = QPushButton("2. Record Full Left Turn")
        self.btn_rec_left.setObjectName("OrangeButton")
        self.btn_rec_left.clicked.connect(self._record_left)

        self.btn_rec_right = QPushButton("3. Record Full Right Turn")
        self.btn_rec_right.setObjectName("OrangeButton")
        self.btn_rec_right.clicked.connect(self._record_right)

        calib_layout.addWidget(self.btn_rec_neutral)
        calib_layout.addWidget(self.btn_rec_left)
        calib_layout.addWidget(self.btn_rec_right)

        # Calibration readouts
        self.lbl_calib_summary = QLabel(
            f"Neutral: {calibration_manager.neutral_angle:.1f}° | "
            f"Left Max: {calibration_manager.calibrated_left_max:.1f}° | "
            f"Right Max: {calibration_manager.calibrated_right_max:.1f}°"
        )
        self.lbl_calib_summary.setStyleSheet("color: #00E676; font-size: 12px; margin-top: 8px;")
        calib_layout.addWidget(self.lbl_calib_summary)

        calib_layout.addStretch()
        content_layout.addWidget(calib_card, stretch=1)

        # Center: Live Virtual Steering Wheel Showcase
        wheel_card = QFrame()
        wheel_card.setObjectName("PanelCard")
        wheel_layout = QVBoxLayout(wheel_card)
        wheel_layout.setAlignment(Qt.AlignCenter)
        self.wheel_widget = SteeringWheelWidget(self)
        self.wheel_widget.setFixedSize(280, 280)
        wheel_layout.addWidget(self.wheel_widget)
        content_layout.addWidget(wheel_card, stretch=1)

        # Right Column: Sensitivity Tuning Sliders (Screen 7)
        tuning_card = QFrame()
        tuning_card.setObjectName("PanelCard")
        tuning_layout = QVBoxLayout(tuning_card)
        tuning_layout.setSpacing(12)
        tuning_layout.setContentsMargins(16, 16, 16, 16)

        lbl_tune_title = QLabel("Steering Response Tuning")
        lbl_tune_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #FF8C32;")
        tuning_layout.addWidget(lbl_tune_title)

        # Sensitivity Slider
        self.lbl_sens_val = QLabel(f"Sensitivity: {int(self.sensitivity_mgr.steering_sensitivity)}%")
        self.slider_sens = QSlider(Qt.Horizontal)
        self.slider_sens.setRange(10, 100)
        self.slider_sens.setValue(int(self.sensitivity_mgr.steering_sensitivity))
        self.slider_sens.valueChanged.connect(self._on_sens_changed)
        tuning_layout.addWidget(self.lbl_sens_val)
        tuning_layout.addWidget(self.slider_sens)

        # Max Rotation
        self.lbl_rot_val = QLabel(f"Virtual Wheel Max: {int(self.sensitivity_mgr.steering_max_rotation)}°")
        self.slider_rot = QSlider(Qt.Horizontal)
        self.slider_rot.setRange(90, 360)
        self.slider_rot.setValue(int(self.sensitivity_mgr.steering_max_rotation))
        self.slider_rot.valueChanged.connect(self._on_rot_changed)
        tuning_layout.addWidget(self.lbl_rot_val)
        tuning_layout.addWidget(self.slider_rot)

        # Deadzone Slider
        self.lbl_dz_val = QLabel(f"Center Deadzone: {self.sensitivity_mgr.steering_deadzone:.1f}%")
        self.slider_dz = QSlider(Qt.Horizontal)
        self.slider_dz.setRange(0, 10)
        self.slider_dz.setValue(int(self.sensitivity_mgr.steering_deadzone))
        self.slider_dz.valueChanged.connect(self._on_dz_changed)
        tuning_layout.addWidget(self.lbl_dz_val)
        tuning_layout.addWidget(self.slider_dz)

        # Smoothing Slider
        self.lbl_smooth_val = QLabel(f"Smoothing Filter: {int(self.sensitivity_mgr.steering_smoothing * 100)}%")
        self.slider_smooth = QSlider(Qt.Horizontal)
        self.slider_smooth.setRange(5, 80)
        self.slider_smooth.setValue(int(self.sensitivity_mgr.steering_smoothing * 100))
        self.slider_smooth.valueChanged.connect(self._on_smooth_changed)
        tuning_layout.addWidget(self.lbl_smooth_val)
        tuning_layout.addWidget(self.slider_smooth)

        tuning_layout.addStretch()
        content_layout.addWidget(tuning_card, stretch=1)

        main_layout.addLayout(content_layout)

    def _record_neutral(self):
        angle = self.steering_engine.raw_angle_deg
        calibration_manager.add_sample(angle)
        neu = calibration_manager.commit_neutral_angle()
        calibration_manager.save_calibration()
        self.lbl_instruction.setText("Step 2: Rotate hands to full comfortable LEFT lock, then click Record Left.")
        self._update_calib_labels()
        self.calibration_updated.emit()

    def _record_left(self):
        angle = self.steering_engine.relative_angle_deg
        calibration_manager.add_sample(angle)
        calibration_manager.commit_left_max()
        calibration_manager.save_calibration()
        self.lbl_instruction.setText("Step 3: Rotate hands to full comfortable RIGHT lock, then click Record Right.")
        self._update_calib_labels()
        self.calibration_updated.emit()

    def _record_right(self):
        angle = self.steering_engine.relative_angle_deg
        calibration_manager.add_sample(angle)
        calibration_manager.commit_right_max()
        calibration_manager.save_calibration()
        self.lbl_instruction.setText("Calibration Complete! Steering limits saved.")
        self._update_calib_labels()
        self.calibration_updated.emit()

    def _update_calib_labels(self):
        self.lbl_calib_summary.setText(
            f"Neutral: {calibration_manager.neutral_angle:.1f}° | "
            f"Left Max: {calibration_manager.calibrated_left_max:.1f}° | "
            f"Right Max: {calibration_manager.calibrated_right_max:.1f}°"
        )

    def _on_sens_changed(self, val: int):
        self.sensitivity_mgr.steering_sensitivity = float(val)
        self.lbl_sens_val.setText(f"Sensitivity: {val}%")
        config_manager.set("steering.sensitivity", float(val))
        config_manager.save()

    def _on_rot_changed(self, val: int):
        self.sensitivity_mgr.steering_max_rotation = float(val)
        self.lbl_rot_val.setText(f"Virtual Wheel Max: {val}°")
        config_manager.set("steering.max_rotation_degrees", float(val))
        config_manager.save()

    def _on_dz_changed(self, val: int):
        self.sensitivity_mgr.steering_deadzone = float(val)
        self.lbl_dz_val.setText(f"Center Deadzone: {val:.1f}%")
        config_manager.set("steering.deadzone", float(val))
        config_manager.save()

    def _on_smooth_changed(self, val: int):
        alpha = val / 100.0
        self.sensitivity_mgr.steering_smoothing = alpha
        self.lbl_smooth_val.setText(f"Smoothing Filter: {val}%")
        config_manager.set("steering.smoothing", alpha)
        config_manager.save()

    def update_live_steering(self, raw_angle: float, relative_angle: float, normalized: float, wheel_rot: float):
        self.lbl_live_raw.setText(f"Current Relative Angle: {relative_angle:+.1f}°")
        self.wheel_widget.set_angle(wheel_rot, normalized)

