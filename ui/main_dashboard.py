"""Main Racing Cockpit Dashboard."""
import cv2
import numpy as np
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QProgressBar, QSizePolicy
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal

from ui.steering_wheel import SteeringWheelWidget
from ui.pedal_visualization import DualPedalsWidget
from core.hand_assignment import HandAssignment
from core.virtual_controller import VirtualXboxController
from core.safety_manager import safety_manager
from utils.diagnostics import Diagnostics
from ui.styles import (
    COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, COLOR_PANEL_ALT, COLOR_PANEL_BORDER, COLOR_TEXT_SECONDARY
)

class MainDashboard(QWidget):
    open_settings_requested = Signal()
    emergency_stop_triggered = Signal()

    def __init__(
        self,
        hand_assignment: HandAssignment,
        controller: VirtualXboxController,
        diagnostics: Diagnostics,
        parent=None
    ):
        super().__init__(parent)
        self.hand_assignment = hand_assignment
        self.controller = controller
        self.diagnostics = diagnostics
        self.racing_active = True
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(12)

        # 1. TOP BAR
        top_bar = QFrame()
        top_bar.setObjectName("PanelCard")
        top_bar.setFixedHeight(58)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 0, 16, 0)
        top_layout.setSpacing(14)

        # Brand Logo
        logo_box = QHBoxLayout()
        logo_box.setSpacing(8)
        lbl_icon = QLabel("🏎")
        lbl_icon.setStyleSheet("font-size: 20px;")
        lbl_logo = QLabel("VIRTUAL DRIVE")
        lbl_logo.setStyleSheet("font-size: 18px; font-weight: 800; letter-spacing: 1.5px; color: #00A8FF;")
        logo_box.addWidget(lbl_icon)
        logo_box.addWidget(lbl_logo)
        top_layout.addLayout(logo_box)

        top_layout.addSpacing(16)

        # Status pills with glowing dots
        self.pill_cam = QLabel("● CAM: ACTIVE")
        self.pill_cam.setStyleSheet(
            "background-color: #0F2D1F; border: 1px solid #00E676; "
            "padding: 4px 12px; border-radius: 12px; color: #00E676; font-weight: 700; font-size: 11px;"
        )
        top_layout.addWidget(self.pill_cam)

        self.pill_track = QLabel("● HANDS: 2 TRACKED")
        self.pill_track.setStyleSheet(
            "background-color: #0F2D1F; border: 1px solid #00E676; "
            "padding: 4px 12px; border-radius: 12px; color: #00E676; font-weight: 700; font-size: 11px;"
        )
        top_layout.addWidget(self.pill_track)

        self.pill_ctrl = QLabel("● XBOX 360: READY")
        self.pill_ctrl.setStyleSheet(
            "background-color: #1A2234; border: 1px solid #243247; "
            "padding: 4px 12px; border-radius: 12px; color: #94A3B8; font-weight: 700; font-size: 11px;"
        )
        top_layout.addWidget(self.pill_ctrl)

        top_layout.addStretch()

        # Settings button
        btn_settings = QPushButton("⚙ Settings")
        btn_settings.setFixedHeight(36)
        btn_settings.setFixedWidth(100)
        btn_settings.clicked.connect(self.open_settings_requested.emit)
        top_layout.addWidget(btn_settings)

        # Emergency Stop Button
        self.btn_emergency = QPushButton("🛑 EMERGENCY STOP")
        self.btn_emergency.setObjectName("EmergencyButton")
        self.btn_emergency.setFixedHeight(40)
        self.btn_emergency.clicked.connect(self._on_emergency_clicked)
        top_layout.addWidget(self.btn_emergency)

        main_layout.addWidget(top_bar)

        # 2. CENTER WORKSPACE (3 Columns)
        center_layout = QHBoxLayout()
        center_layout.setSpacing(14)

        # LEFT PANEL: Live Camera Tracking
        left_card = QFrame()
        left_card.setObjectName("PanelCard")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)

        header_left = QHBoxLayout()
        lbl_left_title = QLabel("LIVE CAMERA TRACKING")
        lbl_left_title.setObjectName("SectionHeader")
        lbl_left_title.setStyleSheet("color: #00A8FF; font-weight: 700;")
        header_left.addWidget(lbl_left_title)
        header_left.addStretch()
        left_layout.addLayout(header_left)

        self.preview_label = QLabel("Initializing camera...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #0A0E17; border: 1px solid #1E293B; border-radius: 8px;")
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(self.preview_label)

        # Left / Right hand status pills
        badge_layout = QHBoxLayout()
        self.badge_left = QLabel("Left: DETECTED")
        self.badge_left.setStyleSheet("color: #00E676; font-weight: bold; font-size: 11px; background: #0F2D1F; padding: 3px 8px; border-radius: 4px;")
        self.badge_right = QLabel("Right: DETECTED")
        self.badge_right.setStyleSheet("color: #00E676; font-weight: bold; font-size: 11px; background: #0F2D1F; padding: 3px 8px; border-radius: 4px;")
        badge_layout.addWidget(self.badge_left)
        badge_layout.addStretch()
        badge_layout.addWidget(self.badge_right)
        left_layout.addLayout(badge_layout)

        center_layout.addWidget(left_card, stretch=4)

        # CENTER PANEL: Hero Animated Steering Wheel
        center_card = QFrame()
        center_card.setObjectName("TelemetryCard")
        center_card_layout = QVBoxLayout(center_card)
        center_card_layout.setContentsMargins(16, 16, 16, 16)
        center_card_layout.setAlignment(Qt.AlignCenter)

        lbl_wheel_title = QLabel("VIRTUAL STEERING WHEEL")
        lbl_wheel_title.setObjectName("SectionHeader")
        lbl_wheel_title.setStyleSheet("color: #FF6B00; font-weight: 700;")
        lbl_wheel_title.setAlignment(Qt.AlignCenter)
        center_card_layout.addWidget(lbl_wheel_title)

        self.wheel_widget = SteeringWheelWidget(self)
        self.wheel_widget.setMinimumSize(270, 270)
        center_card_layout.addWidget(self.wheel_widget, alignment=Qt.AlignCenter)

        # Real-time Telemetry readouts
        self.lbl_steer_stats = QLabel("Steering: +0°  |  Output: 0%")
        self.lbl_steer_stats.setStyleSheet("font-size: 14px; font-weight: 800; color: #FFFFFF;")
        self.lbl_steer_stats.setAlignment(Qt.AlignCenter)
        center_card_layout.addWidget(self.lbl_steer_stats)

        center_layout.addWidget(center_card, stretch=5)

        # RIGHT PANEL: Dual Racing Pedals
        right_card = QFrame()
        right_card.setObjectName("PanelCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(10)

        header_right = QHBoxLayout()
        lbl_pedal_title = QLabel("PROGRESSIVE RACING PEDALS")
        lbl_pedal_title.setObjectName("SectionHeader")
        lbl_pedal_title.setStyleSheet("color: #00E676; font-weight: 700;")
        header_right.addWidget(lbl_pedal_title)
        header_right.addStretch()
        right_layout.addLayout(header_right)

        self.pedals_widget = DualPedalsWidget(self)
        right_layout.addWidget(self.pedals_widget, stretch=1)

        # Assignment badges
        self.lbl_assign_info = QLabel(
            f"Throttle: {self.hand_assignment.accelerator_hand} Hand  •  "
            f"Brake: {self.hand_assignment.brake_hand} Hand"
        )
        self.lbl_assign_info.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        self.lbl_assign_info.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.lbl_assign_info)

        center_layout.addWidget(right_card, stretch=4)
        main_layout.addLayout(center_layout, stretch=1)

        # 3. BOTTOM TELEMETRY HUD BAR
        bottom_bar = QFrame()
        bottom_bar.setObjectName("PanelCard")
        bottom_bar.setFixedHeight(54)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(18, 0, 18, 0)
        bottom_layout.setSpacing(16)

        # Performance Monitor
        self.lbl_perf = QLabel("FPS: 30.0  |  LATENCY: 12ms")
        self.lbl_perf.setStyleSheet("font-family: monospace; font-size: 12px; color: #00A8FF; font-weight: bold;")
        bottom_layout.addWidget(self.lbl_perf)

        bottom_layout.addSpacing(10)

        # Live Gamepad Outputs
        self.lbl_axes = QLabel("XBOX 360  ➜  STEER: 0  |  RT: 0  |  LT: 0")
        self.lbl_axes.setStyleSheet("font-family: monospace; font-size: 12px; color: #FFFFFF; font-weight: 600;")
        bottom_layout.addWidget(self.lbl_axes)

        bottom_layout.addStretch()

        # Pause / Resume toggle
        self.btn_toggle_race = QPushButton("⏸ Pause Emulation")
        self.btn_toggle_race.setFixedHeight(34)
        self.btn_toggle_race.clicked.connect(self._toggle_racing)
        bottom_layout.addWidget(self.btn_toggle_race)

        main_layout.addWidget(bottom_bar)

    def _on_emergency_clicked(self):
        if not safety_manager.emergency_stop_active:
            safety_manager.trigger_emergency_stop("User Clicked Emergency Stop")
            self.btn_emergency.setText("▶ RESUME CONTROL")
            self.btn_emergency.setStyleSheet("background-color: #00E676; color: #000; font-weight: bold;")
            self.emergency_stop_triggered.emit()
        else:
            safety_manager.resume_control()
            self.btn_emergency.setText("🛑 EMERGENCY STOP")
            self.btn_emergency.setStyleSheet("")

    def _toggle_racing(self):
        self.racing_active = not self.racing_active
        if self.racing_active:
            self.btn_toggle_race.setText("⏸ Pause Emulation")
            self.btn_toggle_race.setObjectName("")
        else:
            self.btn_toggle_race.setText("▶ Resume Emulation")
            self.btn_toggle_race.setObjectName("PrimaryButton")
            self.controller.reset_neutral()

    def update_frame(self, frame_bgr: np.ndarray):
        if frame_bgr is None:
            return
        h, w, ch = frame_bgr.shape
        bytes_per_line = ch * w
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        scaled = pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)

    def update_telemetry(
        self,
        tracking_info: Dict[str, Any],
        steering_deg: float,
        steering_norm: float,
        wheel_rot: float,
        accel_pct: float,
        brake_pct: float,
        ctrl_steering: int,
        ctrl_accel: int,
        ctrl_brake: int
    ):
        # Update steering wheel
        self.wheel_widget.set_angle(wheel_rot, steering_norm)
        self.lbl_steer_stats.setText(f"Steering: {int(steering_deg):+d}°  |  Output: {int(steering_norm * 100):+d}%")

        # Update pedals
        self.pedals_widget.update_pedals(accel_pct, brake_pct)

        # Update badges
        left_ok = tracking_info.get("left_detected", False)
        right_ok = tracking_info.get("right_detected", False)

        self.badge_left.setText("Left: DETECTED" if left_ok else "Left: MISSING")
        self.badge_left.setStyleSheet(
            f"color: {'#00E676' if left_ok else '#FF1744'}; font-weight: bold; font-size: 11px; "
            f"background: {'#0F2D1F' if left_ok else '#331118'}; padding: 3px 8px; border-radius: 4px;"
        )

        self.badge_right.setText("Right: DETECTED" if right_ok else "Right: MISSING")
        self.badge_right.setStyleSheet(
            f"color: {'#00E676' if right_ok else '#FF1744'}; font-weight: bold; font-size: 11px; "
            f"background: {'#0F2D1F' if right_ok else '#331118'}; padding: 3px 8px; border-radius: 4px;"
        )

        # Top tracking pill
        if left_ok and right_ok:
            self.pill_track.setText("● HANDS: 2 TRACKED")
            self.pill_track.setStyleSheet(
                "background-color: #0F2D1F; border: 1px solid #00E676; "
                "padding: 4px 12px; border-radius: 12px; color: #00E676; font-weight: 700; font-size: 11px;"
            )
        elif left_ok or right_ok:
            self.pill_track.setText("● HANDS: 1 DETECTED")
            self.pill_track.setStyleSheet(
                "background-color: #33200F; border: 1px solid #FF8C00; "
                "padding: 4px 12px; border-radius: 12px; color: #FF8C00; font-weight: 700; font-size: 11px;"
            )
        else:
            self.pill_track.setText("● HANDS: LOST")
            self.pill_track.setStyleSheet(
                "background-color: #331118; border: 1px solid #FF1744; "
                "padding: 4px 12px; border-radius: 12px; color: #FF1744; font-weight: 700; font-size: 11px;"
            )

        # Controller connection pill
        if self.controller.is_connected:
            self.pill_ctrl.setText("● XBOX 360: ACTIVE")
            self.pill_ctrl.setStyleSheet(
                "background-color: #0F2D1F; border: 1px solid #00E676; "
                "padding: 4px 12px; border-radius: 12px; color: #00E676; font-weight: 700; font-size: 11px;"
            )
        else:
            self.pill_ctrl.setText("● XBOX 360: STANDBY")
            self.pill_ctrl.setStyleSheet(
                "background-color: #1A2234; border: 1px solid #243247; "
                "padding: 4px 12px; border-radius: 12px; color: #94A3B8; font-weight: 700; font-size: 11px;"
            )

        # Telemetry axes
        self.lbl_axes.setText(f"XBOX 360  ➜  STEER: {ctrl_steering:+d}  |  RT: {ctrl_accel}  |  LT: {ctrl_brake}")

        # Performance
        self.lbl_perf.setText(f"FPS: {self.diagnostics.fps:.1f}  |  LATENCY: {self.diagnostics.avg_latency_ms:.1f}ms")

    def refresh_hand_labels(self):
        self.lbl_assign_info.setText(
            f"Throttle: {self.hand_assignment.accelerator_hand} Hand  •  "
            f"Brake: {self.hand_assignment.brake_hand} Hand"
        )
