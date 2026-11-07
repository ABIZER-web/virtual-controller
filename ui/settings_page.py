"""Settings page for runtime configuration adjustments."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider,
    QComboBox, QCheckBox, QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from core.camera_manager import camera_manager
from core.sensitivity_manager import SensitivityManager
from core.hand_assignment import HandAssignment
from core.virtual_controller import VirtualXboxController
from utils.config_manager import config_manager
from ui.styles import (
    COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, COLOR_PANEL_ALT, COLOR_PANEL_BORDER
)

class SettingsPage(QWidget):
    settings_saved = Signal()
    back_to_dashboard_requested = Signal()
    rerun_wizard_requested = Signal()

    def __init__(
        self,
        sensitivity_mgr: SensitivityManager,
        hand_assignment: HandAssignment,
        controller: VirtualXboxController,
        parent=None
    ):
        super().__init__(parent)
        self.sensitivity_mgr = sensitivity_mgr
        self.hand_assignment = hand_assignment
        self.controller = controller
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # Top Header Bar
        top_box = QHBoxLayout()
        btn_back = QPushButton("◀ Back to Cockpit")
        btn_back.setFixedHeight(36)
        btn_back.setFixedWidth(150)
        btn_back.clicked.connect(self.back_to_dashboard_requested.emit)
        top_box.addWidget(btn_back)

        top_box.addSpacing(16)
        lbl_head = QLabel("SIMULATOR CONFIGURATION")
        lbl_head.setObjectName("HeaderLabel")
        lbl_head.setStyleSheet("font-size: 18px; font-weight: 800; color: #00A8FF;")
        top_box.addWidget(lbl_head)
        top_box.addStretch()

        btn_wizard = QPushButton("🚀 Run Hardware Setup Wizard")
        btn_wizard.setObjectName("OrangeButton")
        btn_wizard.setFixedHeight(36)
        btn_wizard.clicked.connect(self.rerun_wizard_requested.emit)
        top_box.addWidget(btn_wizard)
        main_layout.addLayout(top_box)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(14)

        # 1. CAMERA SECTION
        cam_card = self._create_card("📷 CAMERA SETTINGS")
        cam_layout = QVBoxLayout(cam_card)

        self.chk_mirror = QCheckBox("Mirror Camera Stream (Natural Selfie View)")
        self.chk_mirror.setChecked(config_manager.get("camera.mirror", True))
        cam_layout.addWidget(self.chk_mirror)
        layout.addWidget(cam_card)

        # 2. STEERING SECTION
        steer_card = self._create_card("🏎 STEERING WHEEL RESPONSE")
        steer_layout = QVBoxLayout(steer_card)
        steer_layout.setSpacing(12)

        # Sensitivity
        self.lbl_steer_sens = QLabel(f"Steering Sensitivity: {int(self.sensitivity_mgr.steering_sensitivity)}%")
        self.lbl_steer_sens.setStyleSheet("font-weight: 600;")
        self.sl_steer_sens = QSlider(Qt.Horizontal)
        self.sl_steer_sens.setRange(10, 100)
        self.sl_steer_sens.setValue(int(self.sensitivity_mgr.steering_sensitivity))
        self.sl_steer_sens.valueChanged.connect(lambda v: self.lbl_steer_sens.setText(f"Steering Sensitivity: {v}%"))
        steer_layout.addWidget(self.lbl_steer_sens)
        steer_layout.addWidget(self.sl_steer_sens)

        # Max Angle
        self.lbl_steer_rot = QLabel(f"Maximum Virtual Wheel Rotation: {int(self.sensitivity_mgr.steering_max_rotation)}°")
        self.lbl_steer_rot.setStyleSheet("font-weight: 600;")
        self.sl_steer_rot = QSlider(Qt.Horizontal)
        self.sl_steer_rot.setRange(90, 360)
        self.sl_steer_rot.setValue(int(self.sensitivity_mgr.steering_max_rotation))
        self.sl_steer_rot.valueChanged.connect(lambda v: self.lbl_steer_rot.setText(f"Maximum Virtual Wheel Rotation: {v}°"))
        steer_layout.addWidget(self.lbl_steer_rot)
        steer_layout.addWidget(self.sl_steer_rot)

        # Deadzone
        self.lbl_steer_dz = QLabel(f"Center Deadzone: {self.sensitivity_mgr.steering_deadzone:.1f}%")
        self.lbl_steer_dz.setStyleSheet("font-weight: 600;")
        self.sl_steer_dz = QSlider(Qt.Horizontal)
        self.sl_steer_dz.setRange(0, 10)
        self.sl_steer_dz.setValue(int(self.sensitivity_mgr.steering_deadzone))
        self.sl_steer_dz.valueChanged.connect(lambda v: self.lbl_steer_dz.setText(f"Center Deadzone: {v:.1f}%"))
        steer_layout.addWidget(self.lbl_steer_dz)
        steer_layout.addWidget(self.sl_steer_dz)

        # Centering enabled
        self.chk_centering = QCheckBox("Smooth Auto-Centering on Hand Tracking Loss")
        self.chk_centering.setChecked(self.sensitivity_mgr.centering_enabled)
        steer_layout.addWidget(self.chk_centering)

        layout.addWidget(steer_card)

        # 3. PEDALS SECTION
        pedal_card = self._create_card("⚡ ACCELERATOR & BRAKE MAPPING")
        pedal_layout = QVBoxLayout(pedal_card)
        pedal_layout.setSpacing(12)

        row_hands = QHBoxLayout()
        lbl_acc_hand = QLabel("Throttle Hand:")
        lbl_acc_hand.setStyleSheet("font-weight: 600; color: #00E676;")
        self.combo_acc_hand = QComboBox()
        self.combo_acc_hand.addItems(["Right", "Left"])
        self.combo_acc_hand.setCurrentText(self.hand_assignment.accelerator_hand)

        lbl_brk_hand = QLabel("Brake Hand:")
        lbl_brk_hand.setStyleSheet("font-weight: 600; color: #FF3D00;")
        self.combo_brk_hand = QComboBox()
        self.combo_brk_hand.addItems(["Left", "Right"])
        self.combo_brk_hand.setCurrentText(self.hand_assignment.brake_hand)

        row_hands.addWidget(lbl_acc_hand)
        row_hands.addWidget(self.combo_acc_hand)
        row_hands.addSpacing(20)
        row_hands.addWidget(lbl_brk_hand)
        row_hands.addWidget(self.combo_brk_hand)
        row_hands.addStretch()
        pedal_layout.addLayout(row_hands)

        # Accel sensitivity
        self.lbl_acc_sens = QLabel(f"Throttle Sensitivity: {int(self.sensitivity_mgr.accel_sensitivity)}%")
        self.lbl_acc_sens.setStyleSheet("font-weight: 600;")
        self.sl_acc_sens = QSlider(Qt.Horizontal)
        self.sl_acc_sens.setRange(10, 100)
        self.sl_acc_sens.setValue(int(self.sensitivity_mgr.accel_sensitivity))
        self.sl_acc_sens.valueChanged.connect(lambda v: self.lbl_acc_sens.setText(f"Throttle Sensitivity: {v}%"))
        pedal_layout.addWidget(self.lbl_acc_sens)
        pedal_layout.addWidget(self.sl_acc_sens)

        # Brake sensitivity
        self.lbl_brk_sens = QLabel(f"Brake Sensitivity: {int(self.sensitivity_mgr.brake_sensitivity)}%")
        self.lbl_brk_sens.setStyleSheet("font-weight: 600;")
        self.sl_brk_sens = QSlider(Qt.Horizontal)
        self.sl_brk_sens.setRange(10, 100)
        self.sl_brk_sens.setValue(int(self.sensitivity_mgr.brake_sensitivity))
        self.sl_brk_sens.valueChanged.connect(lambda v: self.lbl_brk_sens.setText(f"Brake Sensitivity: {v}%"))
        pedal_layout.addWidget(self.lbl_brk_sens)
        pedal_layout.addWidget(self.sl_brk_sens)

        layout.addWidget(pedal_card)

        # Bottom Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)
        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setFixedHeight(40)
        btn_save.setFixedWidth(160)
        btn_save.clicked.connect(self._save_settings)

        btn_reset = QPushButton("Reset to Factory Defaults")
        btn_reset.setFixedHeight(40)
        btn_reset.setFixedWidth(190)
        btn_reset.clicked.connect(self._reset_defaults)

        btn_box.addWidget(btn_save)
        btn_box.addWidget(btn_reset)
        btn_box.addStretch()
        layout.addLayout(btn_box)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("PanelCard")
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: 700; color: #00A8FF; font-size: 13px; margin-bottom: 6px;")
        card.layout = QVBoxLayout(card)
        card.layout.addWidget(lbl)
        return card

    def _save_settings(self):
        # Validate hands
        acc_h = self.combo_acc_hand.currentText()
        brk_h = self.combo_brk_hand.currentText()
        if acc_h == brk_h:
            QMessageBox.warning(self, "Invalid Selection", "Accelerator and Brake cannot be assigned to the same hand.")
            return

        self.hand_assignment.set_assignment(acc_h, brk_h)
        config_manager.set("hand_assignment.accelerator_hand", acc_h)
        config_manager.set("hand_assignment.brake_hand", brk_h)

        # Steering
        self.sensitivity_mgr.steering_sensitivity = float(self.sl_steer_sens.value())
        self.sensitivity_mgr.steering_max_rotation = float(self.sl_steer_rot.value())
        self.sensitivity_mgr.steering_deadzone = float(self.sl_steer_dz.value())
        self.sensitivity_mgr.centering_enabled = self.chk_centering.isChecked()

        config_manager.set("steering.sensitivity", self.sensitivity_mgr.steering_sensitivity)
        config_manager.set("steering.max_rotation_degrees", self.sensitivity_mgr.steering_max_rotation)
        config_manager.set("steering.deadzone", self.sensitivity_mgr.steering_deadzone)
        config_manager.set("steering.centering_enabled", self.sensitivity_mgr.centering_enabled)

        # Pedals
        self.sensitivity_mgr.accel_sensitivity = float(self.sl_acc_sens.value())
        self.sensitivity_mgr.brake_sensitivity = float(self.sl_brk_sens.value())
        config_manager.set("pedals.accelerator.sensitivity", self.sensitivity_mgr.accel_sensitivity)
        config_manager.set("pedals.brake.sensitivity", self.sensitivity_mgr.brake_sensitivity)

        # Camera
        config_manager.set("camera.mirror", self.chk_mirror.isChecked())

        config_manager.save()
        QMessageBox.information(self, "Settings Saved", "Simulator settings have been updated successfully.")
        self.settings_saved.emit()

    def _reset_defaults(self):
        confirm = QMessageBox.question(
            self, "Reset Defaults", "Are you sure you want to restore all default settings?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            config_manager.reset_defaults()
            self.sensitivity_mgr.load_from_config(config_manager.load())
            QMessageBox.information(self, "Defaults Restored", "All settings restored to factory defaults.")
            self.settings_saved.emit()
