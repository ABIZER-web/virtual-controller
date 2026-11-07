"""Screen 9: Virtual Xbox Controller Test & Status Verification."""
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from core.virtual_controller import VirtualXboxController
from ui.styles import COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, COLOR_ACCENT_ORANGE

class ControllerTestScreen(QWidget):
    def __init__(self, controller: VirtualXboxController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title_box = QVBoxLayout()
        lbl_title = QLabel("VIRTUAL XBOX 360 CONTROLLER VERIFICATION")
        lbl_title.setObjectName("HeaderLabel")
        lbl_sub = QLabel("Test real-time gamepad axes output and verify game connection status.")
        lbl_sub.setObjectName("SubtitleLabel")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        layout.addLayout(title_box)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left Column: Controller Hardware Status Card
        status_card = QFrame()
        status_card.setObjectName("PanelCard")
        stat_layout = QVBoxLayout(status_card)
        stat_layout.setSpacing(16)
        stat_layout.setContentsMargins(18, 18, 18, 18)

        lbl_head = QLabel("Emulation Status")
        lbl_head.setStyleSheet("font-weight: 700; font-size: 15px; color: #168CFF;")
        stat_layout.addWidget(lbl_head)

        self.lbl_conn_status = QLabel("Controller: Disconnected")
        self.lbl_conn_status.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF3D00;")
        stat_layout.addWidget(self.lbl_conn_status)

        self.btn_init = QPushButton("Initialize Virtual Xbox Controller")
        self.btn_init.setObjectName("PrimaryButton")
        self.btn_init.setFixedHeight(40)
        self.btn_init.clicked.connect(self._on_init_clicked)
        stat_layout.addWidget(self.btn_init)

        # Driver details box
        self.driver_box = QFrame()
        self.driver_box.setObjectName("PanelCardAlt")
        drv_layout = QVBoxLayout(self.driver_box)
        drv_layout.setSpacing(8)

        lbl_drv_title = QLabel("ViGEmBus Driver Requirement:")
        lbl_drv_title.setStyleSheet("font-weight: 600; color: #FF8C32;")
        self.lbl_driver_info = QLabel(
            "Windows Xbox 360 emulation requires the official ViGEmBus driver.\n"
            "If initialization fails, click below to install or download the driver."
        )
        self.lbl_driver_info.setStyleSheet("color: #8FA3BC; font-size: 12px; line-height: 1.4;")
        self.btn_driver_download = QPushButton("Download ViGEmBus Driver")
        self.btn_driver_download.clicked.connect(self._open_driver_download)

        drv_layout.addWidget(lbl_drv_title)
        drv_layout.addWidget(self.lbl_driver_info)
        drv_layout.addWidget(self.btn_driver_download)
        stat_layout.addWidget(self.driver_box)

        stat_layout.addStretch()
        content_layout.addWidget(status_card, stretch=1)

        # Right Column: Real-time Gamepad Axis Telemetry
        axis_card = QFrame()
        axis_card.setObjectName("PanelCard")
        axis_layout = QVBoxLayout(axis_card)
        axis_layout.setSpacing(16)
        axis_layout.setContentsMargins(18, 18, 18, 18)

        lbl_axis_title = QLabel("Virtual Controller Output Stream")
        lbl_axis_title.setStyleSheet("font-weight: 700; font-size: 15px; color: #FF8C32;")
        axis_layout.addWidget(lbl_axis_title)

        # Steering Axis: Left Stick X (-32768 to 32767)
        self.lbl_axis_steer = QLabel("Steering [Left Stick X]: 0 (-32768 to +32767)")
        self.lbl_axis_steer.setStyleSheet("font-weight: 600;")
        self.bar_steer = QProgressBar()
        self.bar_steer.setRange(-32768, 32767)
        self.bar_steer.setValue(0)
        axis_layout.addWidget(self.lbl_axis_steer)
        axis_layout.addWidget(self.bar_steer)

        # Accelerator Axis: Right Trigger RT (0 to 255)
        self.lbl_axis_accel = QLabel("Throttle [Right Trigger RT]: 0 (0 to 255)")
        self.lbl_axis_accel.setStyleSheet("font-weight: 600; color: #00E676;")
        self.bar_accel = QProgressBar()
        self.bar_accel.setRange(0, 255)
        self.bar_accel.setValue(0)
        axis_layout.addWidget(self.lbl_axis_accel)
        axis_layout.addWidget(self.bar_accel)

        # Brake Axis: Left Trigger LT (0 to 255)
        self.lbl_axis_brake = QLabel("Brake [Left Trigger LT]: 0 (0 to 255)")
        self.lbl_axis_brake.setStyleSheet("font-weight: 600; color: #FF3D00;")
        self.bar_brake = QProgressBar()
        self.bar_brake.setRange(0, 255)
        self.bar_brake.setValue(0)
        axis_layout.addWidget(self.lbl_axis_brake)
        axis_layout.addWidget(self.bar_brake)

        # Game Connection Guide Note
        lbl_guide = QLabel(
            "Game Configuration:\n"
            "1. Launch your racing game (Forza, F1, Assetto Corsa, etc.)\n"
            "2. Select 'Xbox 360 Controller' in game settings\n"
            "3. Left stick steers, RT accelerates, LT brakes"
        )
        lbl_guide.setStyleSheet("color: #6E8299; font-size: 12px; line-height: 1.5; margin-top: 10px;")
        axis_layout.addWidget(lbl_guide)

        axis_layout.addStretch()
        content_layout.addWidget(axis_card, stretch=1)

        layout.addLayout(content_layout)

    def _on_init_clicked(self):
        success, msg = self.controller.initialize()
        if success:
            self.lbl_conn_status.setText("Controller: Connected & Active")
            self.lbl_conn_status.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_ACCENT_GREEN};")
            QMessageBox.information(self, "Virtual Gamepad", "Virtual Xbox 360 Controller connected successfully!")
        else:
            self.lbl_conn_status.setText(f"Controller: Error\n({msg})")
            self.lbl_conn_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_ACCENT_RED};")
            QMessageBox.warning(
                self,
                "Driver Required",
                f"{msg}\n\nPlease install the ViGEmBus driver to enable virtual controller emulation."
            )

    def _open_driver_download(self):
        import os
        if os.path.exists("ViGEmBus_Setup.exe"):
            os.startfile("ViGEmBus_Setup.exe")
        else:
            url = "https://github.com/ViGEm/ViGEmBus/releases/latest"
            webbrowser.open(url)

    def update_telemetry(self, raw_steer: int, raw_accel: int, raw_brake: int):
        self.lbl_axis_steer.setText(f"Steering [Left Stick X]: {raw_steer:+d}")
        self.bar_steer.setValue(raw_steer)

        self.lbl_axis_accel.setText(f"Throttle [Right Trigger RT]: {raw_accel}")
        self.bar_accel.setValue(raw_accel)

        self.lbl_axis_brake.setText(f"Brake [Left Trigger LT]: {raw_brake}")
        self.bar_brake.setValue(raw_brake)

