"""Multi-step hardware configuration wizard with modern stepper navigation."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
import numpy as np
from typing import Dict, Any, List

from ui.welcome_screen import WelcomeScreen
from ui.camera_setup import CameraSetupScreen
from ui.hand_setup import HandSetupScreen
from ui.steering_setup import SteeringSetupScreen
from ui.pedal_setup import PedalSetupScreen
from ui.controller_test import ControllerTestScreen
from core.steering_engine import SteeringEngine
from core.pedal_engine import PedalEngine
from core.hand_assignment import HandAssignment
from core.sensitivity_manager import SensitivityManager
from core.virtual_controller import VirtualXboxController
from utils.config_manager import config_manager
from ui.styles import (
    COLOR_ACCENT_BLUE, COLOR_ACCENT_GREEN, COLOR_PANEL_ALT, COLOR_PANEL_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED
)

class WizardStepperHeader(QWidget):
    """Modern horizontal visual stepper header with glowing active steps and checkmarks."""
    def __init__(self, step_names: List[str], parent=None):
        super().__init__(parent)
        self.step_names = step_names
        self.current_step = 0
        self.step_labels = []
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(6)

        for i, name in enumerate(self.step_names):
            lbl = QLabel(f" {i + 1}. {name} ")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(28)
            self.step_labels.append(lbl)
            layout.addWidget(lbl)

        self.update_step(0)

    def update_step(self, step_idx: int):
        self.current_step = step_idx
        for i, lbl in enumerate(self.step_labels):
            if i < step_idx:
                # Completed
                lbl.setText(f" ✓ {self.step_names[i]} ")
                lbl.setStyleSheet(
                    f"background-color: #0F2D1F; border: 1px solid #00E676; "
                    f"border-radius: 14px; color: #00E676; font-weight: bold; font-size: 11px; padding: 2px 8px;"
                )
            elif i == step_idx:
                # Active
                lbl.setText(f" {i + 1}. {self.step_names[i]} ")
                lbl.setStyleSheet(
                    f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0055D4, stop:1 #0084FF); "
                    f"border: 1px solid #33A1FF; border-radius: 14px; color: #FFFFFF; font-weight: 800; font-size: 11px; padding: 2px 10px;"
                )
            else:
                # Upcoming
                lbl.setText(f" {i + 1}. {self.step_names[i]} ")
                lbl.setStyleSheet(
                    f"background-color: #111827; border: 1px solid #1E293B; "
                    f"border-radius: 14px; color: #64748B; font-size: 11px; padding: 2px 8px;"
                )


class FinishScreen(QWidget):
    start_racing_clicked = Signal()
    recalibrate_clicked = Signal()

    def __init__(self, hand_assignment: HandAssignment, parent=None):
        super().__init__(parent)
        self.hand_assignment = hand_assignment
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(22)

        lbl_check = QLabel("🏁")
        lbl_check.setStyleSheet("font-size: 48px;")
        lbl_check.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_check)

        lbl_congrats = QLabel("SETUP COMPLETE — YOU'RE READY TO RACE!")
        lbl_congrats.setObjectName("TitleLabel")
        lbl_congrats.setStyleSheet("color: #00E676; font-size: 24px; font-weight: 800; letter-spacing: 1px;")
        lbl_congrats.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_congrats)

        # Summary Card
        summary_card = QFrame()
        summary_card.setObjectName("PanelCard")
        summary_card.setFixedWidth(520)
        s_layout = QVBoxLayout(summary_card)
        s_layout.setSpacing(14)
        s_layout.setContentsMargins(24, 20, 24, 20)

        lbl_s_title = QLabel("CALIBRATED CONFIGURATION PROFILE")
        lbl_s_title.setObjectName("SectionHeader")
        lbl_s_title.setStyleSheet("color: #00A8FF; font-weight: 700;")
        s_layout.addWidget(lbl_s_title)

        self.lbl_steer_summary = QLabel("🏎  Steering: Dual Hands Orientation (Wrists Vector)")
        self.lbl_steer_summary.setStyleSheet("font-size: 13px; font-weight: 500;")
        
        self.lbl_acc_summary = QLabel(f"⚡  Throttle: {self.hand_assignment.accelerator_hand} Hand (Finger Squeeze)")
        self.lbl_acc_summary.setStyleSheet("font-size: 13px; font-weight: 600; color: #00E676;")
        
        self.lbl_brk_summary = QLabel(f"🛑  Brake: {self.hand_assignment.brake_hand} Hand (Finger Squeeze)")
        self.lbl_brk_summary.setStyleSheet("font-size: 13px; font-weight: 600; color: #FF3D00;")
        
        self.lbl_ctrl_summary = QLabel("🎮  Controller: Virtual Xbox 360 Gamepad (Analog)")
        self.lbl_ctrl_summary.setStyleSheet("font-size: 13px; font-weight: 500;")

        s_layout.addWidget(self.lbl_steer_summary)
        s_layout.addWidget(self.lbl_acc_summary)
        s_layout.addWidget(self.lbl_brk_summary)
        s_layout.addWidget(self.lbl_ctrl_summary)
        layout.addWidget(summary_card, alignment=Qt.AlignCenter)

        lbl_note = QLabel("Your preferences are saved in config.json and won't prompt again on startup.\nYou can re-open this wizard anytime in Settings.")
        lbl_note.setStyleSheet("color: #64748B; font-size: 12px; text-align: center;")
        lbl_note.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_note)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(16)
        btn_box.setAlignment(Qt.AlignCenter)

        self.btn_race = QPushButton("LAUNCH RACING COCKPIT 🚀")
        self.btn_race.setObjectName("PrimaryButton")
        self.btn_race.setFixedHeight(46)
        self.btn_race.setFixedWidth(240)
        self.btn_race.clicked.connect(self.start_racing_clicked.emit)

        self.btn_recalib = QPushButton("Recalibrate Hardware")
        self.btn_recalib.setFixedHeight(46)
        self.btn_recalib.setFixedWidth(180)
        self.btn_recalib.clicked.connect(self.recalibrate_clicked.emit)

        btn_box.addWidget(self.btn_race)
        btn_box.addWidget(self.btn_recalib)
        layout.addLayout(btn_box)

    def refresh_summary(self):
        self.lbl_acc_summary.setText(f"⚡  Throttle: {self.hand_assignment.accelerator_hand} Hand (Finger Squeeze)")
        self.lbl_brk_summary.setText(f"🛑  Brake: {self.hand_assignment.brake_hand} Hand (Finger Squeeze)")


class SetupWizard(QWidget):
    wizard_completed = Signal()

    def __init__(
        self,
        steering_engine: SteeringEngine,
        pedal_engine: PedalEngine,
        hand_assignment: HandAssignment,
        sensitivity_mgr: SensitivityManager,
        controller: VirtualXboxController,
        parent=None
    ):
        super().__init__(parent)
        self.steering_engine = steering_engine
        self.pedal_engine = pedal_engine
        self.hand_assignment = hand_assignment
        self.sensitivity_mgr = sensitivity_mgr
        self.controller = controller

        self.step_names = ["Welcome", "Camera", "Hands", "Steering", "Pedals", "Gamepad", "Ready"]
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # Visual Stepper Bar
        self.stepper = WizardStepperHeader(self.step_names, self)
        main_layout.addWidget(self.stepper)

        # Stacked Pages
        self.stack = QStackedWidget(self)

        self.page_welcome = WelcomeScreen(self)
        self.page_camera = CameraSetupScreen(self)
        self.page_hands = HandSetupScreen(self)
        self.page_steering = SteeringSetupScreen(self.steering_engine, self.sensitivity_mgr, self)
        self.page_pedals = PedalSetupScreen(self.pedal_engine, self.hand_assignment, self.sensitivity_mgr, self)
        self.page_controller = ControllerTestScreen(self.controller, self)
        self.page_finish = FinishScreen(self.hand_assignment, self)

        self.stack.addWidget(self.page_welcome)       # Index 0
        self.stack.addWidget(self.page_camera)        # Index 1
        self.stack.addWidget(self.page_hands)         # Index 2
        self.stack.addWidget(self.page_steering)      # Index 3
        self.stack.addWidget(self.page_pedals)        # Index 4
        self.stack.addWidget(self.page_controller)    # Index 5
        self.stack.addWidget(self.page_finish)        # Index 6

        main_layout.addWidget(self.stack, stretch=1)

        # Navigation Bar
        nav_bar = QHBoxLayout()
        self.btn_back = QPushButton("◀ Back")
        self.btn_back.clicked.connect(self._go_back)
        self.btn_back.setFixedWidth(120)
        self.btn_back.setFixedHeight(38)

        self.btn_next = QPushButton("Next Step ▶")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.clicked.connect(self._go_next)
        self.btn_next.setFixedWidth(140)
        self.btn_next.setFixedHeight(38)

        nav_bar.addWidget(self.btn_back)
        nav_bar.addStretch()
        nav_bar.addWidget(self.btn_next)
        main_layout.addLayout(nav_bar)

        # Connect signals
        self.page_welcome.start_setup_clicked.connect(lambda: self._go_to_page(1))
        self.page_welcome.skip_setup_clicked.connect(self._on_skip_setup)
        self.page_finish.start_racing_clicked.connect(self._finish_wizard)
        self.page_finish.recalibrate_clicked.connect(lambda: self._go_to_page(3))

        self._update_nav_state()

    def _go_to_page(self, index: int):
        self.stack.setCurrentIndex(index)
        self._update_nav_state()

    def _go_back(self):
        curr = self.stack.currentIndex()
        if curr > 0:
            self._go_to_page(curr - 1)

    def _go_next(self):
        curr = self.stack.currentIndex()
        if curr < self.stack.count() - 1:
            self._go_to_page(curr + 1)
        else:
            self._finish_wizard()

    def _update_nav_state(self):
        idx = self.stack.currentIndex()
        total = self.stack.count()

        # Update visual stepper
        self.stepper.update_step(idx)

        # Hide Back on first screen
        self.btn_back.setVisible(idx > 0 and idx < total - 1)
        # Hide Next on welcome and finish screen
        self.btn_next.setVisible(idx > 0 and idx < total - 1)

        if idx == 1:
            self.page_camera.refresh_devices()
        elif idx == 6:
            self.page_finish.refresh_summary()

    def _on_skip_setup(self):
        config_manager.set("setup_completed", True)
        config_manager.save()
        self.wizard_completed.emit()

    def _finish_wizard(self):
        config_manager.set("setup_completed", True)
        config_manager.save()
        self.wizard_completed.emit()

    def feed_frame_and_tracking(
        self,
        annotated_frame: np.ndarray,
        tracking_info: Dict[str, Any],
        steering_data: Dict[str, float],
        pedal_data: Dict[str, float],
        controller_data: Dict[str, int]
    ):
        """Dispatches live webcam data to whichever wizard page is active."""
        idx = self.stack.currentIndex()
        if idx == 2:  # Hands
            self.page_hands.update_frame_and_detection(annotated_frame, tracking_info)
        elif idx == 3:  # Steering
            self.page_steering.update_live_steering(
                steering_data.get("raw_angle", 0.0),
                steering_data.get("relative_angle", 0.0),
                steering_data.get("normalized", 0.0),
                steering_data.get("wheel_rotation", 0.0)
            )
        elif idx == 4:  # Pedals
            self.page_pedals.update_live_pedals(
                pedal_data.get("accelerator", 0.0),
                pedal_data.get("brake", 0.0)
            )
        elif idx == 5:  # Controller test
            self.page_controller.update_telemetry(
                controller_data.get("steering", 0),
                controller_data.get("accel", 0),
                controller_data.get("brake", 0)
            )
