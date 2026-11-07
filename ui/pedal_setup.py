"""Screens 5, 6 & 8: Pedal Hand Assignment, Calibration & Sensitivity Tuning."""
import numpy as np
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider,
    QFrame, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from ui.pedal_visualization import DualPedalsWidget
from core.hand_assignment import HandAssignment
from core.calibration_manager import calibration_manager
from core.sensitivity_manager import SensitivityManager
from core.pedal_engine import PedalEngine
from utils.config_manager import config_manager
from ui.styles import COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE, COLOR_ACCENT_GREEN, COLOR_ACCENT_RED

class PedalSetupScreen(QWidget):
    assignment_changed = Signal(str, str)

    def __init__(
        self,
        pedal_engine: PedalEngine,
        hand_assignment: HandAssignment,
        sensitivity_mgr: SensitivityManager,
        parent=None
    ):
        super().__init__(parent)
        self.pedal_engine = pedal_engine
        self.hand_assignment = hand_assignment
        self.sensitivity_mgr = sensitivity_mgr
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)

        title_box = QVBoxLayout()
        lbl_title = QLabel("PEDAL ASSIGNMENT & GESTURE CALIBRATION")
        lbl_title.setObjectName("HeaderLabel")
        lbl_sub = QLabel("Assign hands to Accelerator and Brake, calibrate finger squeeze gesture, and tune response.")
        lbl_sub.setObjectName("SubtitleLabel")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        main_layout.addLayout(title_box)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left Column: Hand Assignment Cards (Screens 5 & 6)
        assign_card = QFrame()
        assign_card.setObjectName("PanelCard")
        assign_layout = QVBoxLayout(assign_card)
        assign_layout.setSpacing(14)
        assign_layout.setContentsMargins(16, 16, 16, 16)

        lbl_assign_title = QLabel("Hand Assignment")
        lbl_assign_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #168CFF;")
        assign_layout.addWidget(lbl_assign_title)

        # Accelerator Choice
        lbl_acc_choose = QLabel("ACCELERATOR HAND:")
        lbl_acc_choose.setStyleSheet("font-weight: 600; color: #00E676;")
        assign_layout.addWidget(lbl_acc_choose)

        acc_btn_layout = QHBoxLayout()
        self.btn_acc_left = QPushButton("Left Hand")
        self.btn_acc_right = QPushButton("Right Hand (Recommended)")
        self.btn_acc_left.clicked.connect(lambda: self._set_accel_hand("Left"))
        self.btn_acc_right.clicked.connect(lambda: self._set_accel_hand("Right"))
        acc_btn_layout.addWidget(self.btn_acc_left)
        acc_btn_layout.addWidget(self.btn_acc_right)
        assign_layout.addLayout(acc_btn_layout)

        # Brake Choice
        lbl_brk_choose = QLabel("BRAKE HAND:")
        lbl_brk_choose.setStyleSheet("font-weight: 600; color: #FF3D00; margin-top: 8px;")
        assign_layout.addWidget(lbl_brk_choose)

        brk_btn_layout = QHBoxLayout()
        self.btn_brk_left = QPushButton("Left Hand (Recommended)")
        self.btn_brk_right = QPushButton("Right Hand")
        self.btn_brk_left.clicked.connect(lambda: self._set_brake_hand("Left"))
        self.btn_brk_right.clicked.connect(lambda: self._set_brake_hand("Right"))
        brk_btn_layout.addWidget(self.btn_brk_left)
        brk_btn_layout.addWidget(self.btn_brk_right)
        assign_layout.addLayout(brk_btn_layout)

        # Gesture Calibration Buttons
        lbl_calib_title = QLabel("Finger Squeeze Calibration")
        lbl_calib_title.setStyleSheet("font-weight: 700; font-size: 13px; color: #FF8C32; margin-top: 10px;")
        assign_layout.addWidget(lbl_calib_title)

        calib_grid = QGridLayout()
        # Accelerator Calibration
        self.btn_acc_relax = QPushButton("Record Accel Relaxed")
        self.btn_acc_press = QPushButton("Record Accel Squeezed")
        self.btn_acc_relax.clicked.connect(lambda: self._record_pedal(True, False))
        self.btn_acc_press.clicked.connect(lambda: self._record_pedal(True, True))
        calib_grid.addWidget(self.btn_acc_relax, 0, 0)
        calib_grid.addWidget(self.btn_acc_press, 0, 1)

        # Brake Calibration
        self.btn_brk_relax = QPushButton("Record Brake Relaxed")
        self.btn_brk_press = QPushButton("Record Brake Squeezed")
        self.btn_brk_relax.clicked.connect(lambda: self._record_pedal(False, False))
        self.btn_brk_press.clicked.connect(lambda: self._record_pedal(False, True))
        calib_grid.addWidget(self.btn_brk_relax, 1, 0)
        calib_grid.addWidget(self.btn_brk_press, 1, 1)

        assign_layout.addLayout(calib_grid)

        self.lbl_calib_status = QLabel("Relax = 0% input. Squeeze fingers = increase input.")
        self.lbl_calib_status.setStyleSheet("color: #8FA3BC; font-size: 11px;")
        assign_layout.addWidget(self.lbl_calib_status)

        assign_layout.addStretch()
        content_layout.addWidget(assign_card, stretch=1)

        # Center: Live Animated Dual Pedals (Screen 8)
        self.pedals_widget = DualPedalsWidget(self)
        content_layout.addWidget(self.pedals_widget, stretch=1)

        # Right Column: Sensitivity Controls
        sens_card = QFrame()
        sens_card.setObjectName("PanelCard")
        sens_layout = QVBoxLayout(sens_card)
        sens_layout.setSpacing(12)
        sens_layout.setContentsMargins(16, 16, 16, 16)

        lbl_sens_title = QLabel("Pedal Sensitivity Tuning")
        lbl_sens_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #168CFF;")
        sens_layout.addWidget(lbl_sens_title)

        # Accel Sensitivity
        self.lbl_acc_sens = QLabel(f"Throttle Sensitivity: {int(self.sensitivity_mgr.accel_sensitivity)}%")
        self.slider_acc_sens = QSlider(Qt.Horizontal)
        self.slider_acc_sens.setRange(10, 100)
        self.slider_acc_sens.setValue(int(self.sensitivity_mgr.accel_sensitivity))
        self.slider_acc_sens.valueChanged.connect(self._on_acc_sens_changed)
        sens_layout.addWidget(self.lbl_acc_sens)
        sens_layout.addWidget(self.slider_acc_sens)

        # Brake Sensitivity
        self.lbl_brk_sens = QLabel(f"Brake Sensitivity: {int(self.sensitivity_mgr.brake_sensitivity)}%")
        self.slider_brk_sens = QSlider(Qt.Horizontal)
        self.slider_brk_sens.setRange(10, 100)
        self.slider_brk_sens.setValue(int(self.sensitivity_mgr.brake_sensitivity))
        self.slider_brk_sens.valueChanged.connect(self._on_brk_sens_changed)
        sens_layout.addWidget(self.lbl_brk_sens)
        sens_layout.addWidget(self.slider_brk_sens)

        # Accel Deadzone
        self.lbl_acc_dz = QLabel(f"Throttle Deadzone: {self.sensitivity_mgr.accel_deadzone:.1f}%")
        self.slider_acc_dz = QSlider(Qt.Horizontal)
        self.slider_acc_dz.setRange(0, 15)
        self.slider_acc_dz.setValue(int(self.sensitivity_mgr.accel_deadzone))
        self.slider_acc_dz.valueChanged.connect(self._on_acc_dz_changed)
        sens_layout.addWidget(self.lbl_acc_dz)
        sens_layout.addWidget(self.slider_acc_dz)

        # Brake Deadzone
        self.lbl_brk_dz = QLabel(f"Brake Deadzone: {self.sensitivity_mgr.brake_deadzone:.1f}%")
        self.slider_brk_dz = QSlider(Qt.Horizontal)
        self.slider_brk_dz.setRange(0, 15)
        self.slider_brk_dz.setValue(int(self.sensitivity_mgr.brake_deadzone))
        self.slider_brk_dz.valueChanged.connect(self._on_brk_dz_changed)
        sens_layout.addWidget(self.lbl_brk_dz)
        sens_layout.addWidget(self.slider_brk_dz)

        sens_layout.addStretch()
        content_layout.addWidget(sens_card, stretch=1)

        main_layout.addLayout(content_layout)
        self._update_button_highlights()

    def _set_accel_hand(self, hand: str):
        if self.hand_assignment.set_accelerator_hand(hand):
            self._save_assignment()
        else:
            QMessageBox.warning(self, "Invalid Assignment", "Accelerator and Brake cannot be assigned to the same hand.")

    def _set_brake_hand(self, hand: str):
        if self.hand_assignment.set_brake_hand(hand):
            self._save_assignment()
        else:
            QMessageBox.warning(self, "Invalid Assignment", "Accelerator and Brake cannot be assigned to the same hand.")

    def _save_assignment(self):
        config_manager.set("hand_assignment.accelerator_hand", self.hand_assignment.accelerator_hand)
        config_manager.set("hand_assignment.brake_hand", self.hand_assignment.brake_hand)
        config_manager.save()
        self._update_button_highlights()
        self.assignment_changed.emit(self.hand_assignment.accelerator_hand, self.hand_assignment.brake_hand)

    def _update_button_highlights(self):
        acc = self.hand_assignment.accelerator_hand
        brk = self.hand_assignment.brake_hand

        self.btn_acc_left.setStyleSheet("background-color: #00E676; color: #000;" if acc == "Left" else "")
        self.btn_acc_right.setStyleSheet("background-color: #00E676; color: #000;" if acc == "Right" else "")

        self.btn_brk_left.setStyleSheet("background-color: #FF3D00; color: #FFF;" if brk == "Left" else "")
        self.btn_brk_right.setStyleSheet("background-color: #FF3D00; color: #FFF;" if brk == "Right" else "")

    def _record_pedal(self, is_accel: bool, is_pressed: bool):
        dist = self.pedal_engine.raw_accel_dist if is_accel else self.pedal_engine.raw_brake_dist
        calibration_manager.add_sample(dist)
        pedal_name = "Throttle" if is_accel else "Brake"
        state_name = "Squeezed" if is_pressed else "Relaxed"

        if is_pressed:
            calibration_manager.commit_pedal_pressed(is_accel)
        else:
            calibration_manager.commit_pedal_relaxed(is_accel)

        calibration_manager.save_calibration()
        self.lbl_calib_status.setText(f"Recorded {pedal_name} {state_name} ({dist:.3f})")

    def _on_acc_sens_changed(self, val: int):
        self.sensitivity_mgr.accel_sensitivity = float(val)
        self.lbl_acc_sens.setText(f"Throttle Sensitivity: {val}%")
        config_manager.set("pedals.accelerator.sensitivity", float(val))
        config_manager.save()

    def _on_brk_sens_changed(self, val: int):
        self.sensitivity_mgr.brake_sensitivity = float(val)
        self.lbl_brk_sens.setText(f"Brake Sensitivity: {val}%")
        config_manager.set("pedals.brake.sensitivity", float(val))
        config_manager.save()

    def _on_acc_dz_changed(self, val: int):
        self.sensitivity_mgr.accel_deadzone = float(val)
        self.lbl_acc_dz.setText(f"Throttle Deadzone: {val:.1f}%")
        config_manager.set("pedals.accelerator.deadzone", float(val))
        config_manager.save()

    def _on_brk_dz_changed(self, val: int):
        self.sensitivity_mgr.brake_deadzone = float(val)
        self.lbl_brk_dz.setText(f"Brake Deadzone: {val:.1f}%")
        config_manager.set("pedals.brake.deadzone", float(val))
        config_manager.save()

    def update_live_pedals(self, accel_pct: float, brake_pct: float):
        self.pedals_widget.update_pedals(accel_pct, brake_pct)

