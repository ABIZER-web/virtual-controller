"""Screen 2: Camera Setup for Setup Wizard."""
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QCheckBox, QFrame
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal
from core.camera_manager import camera_manager
from utils.config_manager import config_manager
from ui.styles import COLOR_PANEL_ALT, COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE

class CameraSetupScreen(QWidget):
    camera_configured = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mirror: bool = True
        self._init_ui()
        camera_manager.frame_ready.connect(self.display_frame)
        camera_manager.status_changed.connect(self._on_worker_status)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Title
        title_box = QVBoxLayout()
        lbl_title = QLabel("CAMERA CONFIGURATION")
        lbl_title.setObjectName("HeaderLabel")
        lbl_sub = QLabel("Select your webcam, adjust resolution, and verify live video feed.")
        lbl_sub.setObjectName("SubtitleLabel")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        layout.addLayout(title_box)

        # Main content: Preview on left, Controls on right
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Live Preview Frame
        preview_card = QFrame()
        preview_card.setObjectName("PanelCard")
        prev_layout = QVBoxLayout(preview_card)
        prev_layout.setContentsMargins(10, 10, 10, 10)

        self.preview_label = QLabel("Awaiting camera stream...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #0c1017; border-radius: 8px; color: #6E8299;")
        self.preview_label.setFixedSize(520, 360)
        prev_layout.addWidget(self.preview_label)

        # Camera Status Label
        self.lbl_status = QLabel("Camera: Disconnected")
        self.lbl_status.setStyleSheet("color: #8FA3BC; font-size: 12px;")
        prev_layout.addWidget(self.lbl_status)

        content_layout.addWidget(preview_card, stretch=2)

        # Controls Side Panel
        ctrl_card = QFrame()
        ctrl_card.setObjectName("PanelCard")
        ctrl_layout = QVBoxLayout(ctrl_card)
        ctrl_layout.setSpacing(16)
        ctrl_layout.setContentsMargins(16, 16, 16, 16)

        # Device selection
        lbl_dev = QLabel("Webcam Device:")
        lbl_dev.setStyleSheet("font-weight: 600;")
        self.combo_devices = QComboBox()
        self.combo_devices.currentIndexChanged.connect(self._on_device_changed)

        # Resolution selection
        lbl_res = QLabel("Resolution:")
        lbl_res.setStyleSheet("font-weight: 600;")
        self.combo_res = QComboBox()
        self.combo_res.addItems(["640 x 480 (Recommended, Fast)", "1280 x 720 (HD)"])
        self.combo_res.currentIndexChanged.connect(self._on_res_changed)

        # Mirror mode
        self.chk_mirror = QCheckBox("Mirror Camera Preview")
        self.chk_mirror.setChecked(True)
        self.chk_mirror.toggled.connect(self._on_mirror_toggled)

        # Refresh cameras button
        self.btn_refresh = QPushButton("Refresh Device List")
        self.btn_refresh.clicked.connect(self.refresh_devices)

        ctrl_layout.addWidget(lbl_dev)
        ctrl_layout.addWidget(self.combo_devices)
        ctrl_layout.addWidget(lbl_res)
        ctrl_layout.addWidget(self.combo_res)
        ctrl_layout.addWidget(self.chk_mirror)
        ctrl_layout.addWidget(self.btn_refresh)
        ctrl_layout.addStretch()

        content_layout.addWidget(ctrl_card, stretch=1)
        layout.addLayout(content_layout)

    def refresh_devices(self):
        self.combo_devices.blockSignals(True)
        self.combo_devices.clear()
        cams = camera_manager.detect_available_cameras()
        for c in cams:
            self.combo_devices.addItem(c["name"], userData=c["index"])
        self.combo_devices.blockSignals(False)

        cfg_dev = config_manager.get("camera.device_index", 0)
        idx = self.combo_devices.findData(cfg_dev)
        if idx >= 0:
            self.combo_devices.setCurrentIndex(idx)
        else:
            self.combo_devices.setCurrentIndex(0)

        self._start_selected_camera()

    def _start_selected_camera(self):
        dev_idx = self.combo_devices.currentData()
        if dev_idx is None:
            dev_idx = 0

        res_str = self.combo_res.currentText()
        if "1280" in res_str:
            w, h = 1280, 720
        else:
            w, h = 640, 480

        camera_manager.start_camera(device_index=dev_idx, width=w, height=h, fps=30)

        config_manager.set("camera.device_index", dev_idx)
        config_manager.set("camera.width", w)
        config_manager.set("camera.height", h)
        config_manager.set("camera.mirror", self.chk_mirror.isChecked())
        config_manager.save()

    def _on_device_changed(self, idx):
        self._start_selected_camera()

    def _on_res_changed(self, idx):
        self._start_selected_camera()

    def _on_mirror_toggled(self, checked: bool):
        self.mirror = checked
        config_manager.set("camera.mirror", checked)
        config_manager.save()

    def _on_worker_status(self, is_active: bool, msg: str):
        if is_active:
            self.lbl_status.setText(f"Status: Connected ({msg})")
            self.lbl_status.setStyleSheet(f"color: {COLOR_ACCENT_GREEN};")
        else:
            self.lbl_status.setText(f"Status: {msg}")
            self.lbl_status.setStyleSheet(f"color: {COLOR_ACCENT_RED};")

    def display_frame(self, frame_bgr: np.ndarray):
        if frame_bgr is None:
            return
        frame = frame_bgr.copy()
        if self.chk_mirror.isChecked():
            frame = cv2.flip(frame, 1)

        # Convert to QImage
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        scaled_pix = pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pix)

