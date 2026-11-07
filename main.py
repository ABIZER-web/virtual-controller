"""
VIRTUAL DRIVE — Virtual Racing Simulator Controller
Main application entry point.
"""
import sys
import os
import time
import numpy as np

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt, QTimer, QThread, Signal, Slot
from PySide6.QtGui import QKeyEvent, QIcon

from utils.logger import logger, setup_logger
from utils.config_manager import config_manager
from utils.diagnostics import Diagnostics

from core.camera_manager import camera_manager
from core.hand_tracker import HandTracker
from core.hand_assignment import HandAssignment
from core.sensitivity_manager import SensitivityManager
from core.calibration_manager import calibration_manager
from core.steering_engine import SteeringEngine
from core.pedal_engine import PedalEngine
from core.virtual_controller import VirtualXboxController
from core.safety_manager import safety_manager

from ui.styles import GLOBAL_STYLE
from ui.setup_wizard import SetupWizard
from ui.main_dashboard import MainDashboard
from ui.settings_page import SettingsPage


class TrackingWorker(QThread):
    """
    Dedicated worker thread for MediaPipe processing and steering/pedal mathematics.
    Prevents any GUI frame rate drops or UI stuttering.
    """
    tracking_processed = Signal(object, dict, dict, dict, dict)

    def __init__(
        self,
        hand_tracker: HandTracker,
        steering_engine: SteeringEngine,
        pedal_engine: PedalEngine,
        virtual_controller: VirtualXboxController,
        hand_assignment: HandAssignment,
        diagnostics: Diagnostics
    ):
        super().__init__()
        self.hand_tracker = hand_tracker
        self.steering_engine = steering_engine
        self.pedal_engine = pedal_engine
        self.virtual_controller = virtual_controller
        self.hand_assignment = hand_assignment
        self.diagnostics = diagnostics

        self._running = False
        self._latest_frame: Optional[np.ndarray] = None
        self._has_new_frame = False

    def supply_frame(self, frame_bgr: np.ndarray):
        self._latest_frame = frame_bgr
        self._has_new_frame = True

    def run(self):
        self._running = True
        logger.info("TrackingWorker started.")

        while self._running:
            if not self._has_new_frame or self._latest_frame is None:
                self.msleep(5)
                continue

            t0 = time.time()
            frame = self._latest_frame
            self._has_new_frame = False

            mirror = config_manager.get("camera.mirror", True)
            accel_h = self.hand_assignment.accelerator_hand
            brake_h = self.hand_assignment.brake_hand
            curr_angle = self.steering_engine.relative_angle_deg

            # 1. Process frame with MediaPipe Hand Landmarker
            annotated_frame, info = self.hand_tracker.process_frame(
                frame_bgr=frame,
                mirror=mirror,
                accelerator_hand=accel_h,
                brake_hand=brake_h,
                steering_angle=curr_angle
            )

            # 2. Update Steering Engine
            steering_norm = self.steering_engine.update(
                left_wrist=info.get("left_wrist"),
                right_wrist=info.get("right_wrist")
            )

            # 3. Update Pedal Engine
            pedals = self.pedal_engine.update(
                left_hand_landmarks=info.get("left_landmarks"),
                right_hand_landmarks=info.get("right_landmarks")
            )
            accel_pct = pedals["accelerator"]
            brake_pct = pedals["brake"]

            # 4. Check Safety & Update Virtual Xbox Controller
            if safety_manager.emergency_stop_active:
                ctrl_steer = 0
                ctrl_accel = 0
                ctrl_brake = 0
                self.virtual_controller.reset_neutral()
            else:
                self.virtual_controller.update_inputs(
                    steering_norm=steering_norm,
                    accel_pct=accel_pct,
                    brake_pct=brake_pct
                )
                ctrl_steer = self.virtual_controller.current_steering
                ctrl_accel = self.virtual_controller.current_accel
                ctrl_brake = self.virtual_controller.current_brake

            # Record telemetry & diagnostics
            latency_ms = (time.time() - t0) * 1000.0
            self.diagnostics.record_frame(latency_ms)

            steering_data = {
                "raw_angle": self.steering_engine.raw_angle_deg,
                "relative_angle": self.steering_engine.relative_angle_deg,
                "normalized": steering_norm,
                "wheel_rotation": self.steering_engine.wheel_rotation_deg
            }

            pedal_data = {
                "accelerator": accel_pct,
                "brake": brake_pct
            }

            controller_data = {
                "steering": ctrl_steer,
                "accel": ctrl_accel,
                "brake": ctrl_brake
            }

            # Emit clean packet to Qt GUI thread
            self.tracking_processed.emit(
                annotated_frame,
                info,
                steering_data,
                pedal_data,
                controller_data
            )

        logger.info("TrackingWorker stopped.")

    def stop(self):
        self._running = False
        self.wait(1000)


class VirtualDriveMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VIRTUAL DRIVE — Virtual Racing Simulator Controller")
        self.resize(1180, 720)
        self.setMinimumSize(960, 600)

        # 1. Initialize core managers
        self.cfg = config_manager.load()
        self.diagnostics = Diagnostics()

        self.hand_assignment = HandAssignment(
            accelerator_hand=config_manager.get("hand_assignment.accelerator_hand", "Right"),
            brake_hand=config_manager.get("hand_assignment.brake_hand", "Left")
        )

        self.sensitivity_mgr = SensitivityManager(self.cfg)
        self.virtual_controller = VirtualXboxController()

        # Connect emergency stop reset callback
        safety_manager.register_callback(self.virtual_controller.reset_neutral)

        # Initialize engines
        self.steering_engine = SteeringEngine(self.sensitivity_mgr, calibration_manager)
        self.pedal_engine = PedalEngine(self.sensitivity_mgr, calibration_manager, self.hand_assignment)
        self.hand_tracker = HandTracker(model_path="assets/models/hand_landmarker.task")

        # 2. Setup Central Navigation Stack
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.wizard_page = SetupWizard(
            steering_engine=self.steering_engine,
            pedal_engine=self.pedal_engine,
            hand_assignment=self.hand_assignment,
            sensitivity_mgr=self.sensitivity_mgr,
            controller=self.virtual_controller,
            parent=self
        )

        self.dashboard_page = MainDashboard(
            hand_assignment=self.hand_assignment,
            controller=self.virtual_controller,
            diagnostics=self.diagnostics,
            parent=self
        )

        self.settings_page = SettingsPage(
            sensitivity_mgr=self.sensitivity_mgr,
            hand_assignment=self.hand_assignment,
            controller=self.virtual_controller,
            parent=self
        )

        self.stack.addWidget(self.wizard_page)       # Index 0
        self.stack.addWidget(self.dashboard_page)    # Index 1
        self.stack.addWidget(self.settings_page)     # Index 2

        # Connect inter-screen navigation
        self.wizard_page.wizard_completed.connect(self._on_wizard_completed)
        self.dashboard_page.open_settings_requested.connect(lambda: self.stack.setCurrentIndex(2))
        self.settings_page.back_to_dashboard_requested.connect(lambda: self.stack.setCurrentIndex(1))
        self.settings_page.settings_saved.connect(self._on_settings_saved)
        self.settings_page.rerun_wizard_requested.connect(self._rerun_wizard)

        # 3. Determine Initial View (Setup Wizard vs Dashboard)
        setup_done = config_manager.get("setup_completed", False)
        if setup_done:
            logger.info("Setup already completed. Opening Main Racing Dashboard.")
            self.stack.setCurrentIndex(1)
        else:
            logger.info("First launch detected. Opening Multi-Step Setup Wizard.")
            self.stack.setCurrentIndex(0)

        # 4. Start Threaded Architecture
        self.tracking_worker = TrackingWorker(
            hand_tracker=self.hand_tracker,
            steering_engine=self.steering_engine,
            pedal_engine=self.pedal_engine,
            virtual_controller=self.virtual_controller,
            hand_assignment=self.hand_assignment,
            diagnostics=self.diagnostics
        )
        self.tracking_worker.tracking_processed.connect(self._on_tracking_processed)
        self.tracking_worker.start()

        # Start camera acquisition
        cam_idx = config_manager.get("camera.device_index", 0)
        cam_w = config_manager.get("camera.width", 640)
        cam_h = config_manager.get("camera.height", 480)
        cam_fps = config_manager.get("camera.fps", 30)
        camera_manager.frame_ready.connect(self.tracking_worker.supply_frame)
        camera_manager.start_camera(device_index=cam_idx, width=cam_w, height=cam_h, fps=cam_fps)

        # Attempt background initialization of virtual controller if setup is already done
        if setup_done:
            self.virtual_controller.initialize()

    def _on_wizard_completed(self):
        logger.info("Setup wizard completed. Transitioning to dashboard.")
        self.virtual_controller.initialize()
        self.dashboard_page.refresh_hand_labels()
        self.stack.setCurrentIndex(1)

    def _on_settings_saved(self):
        self.dashboard_page.refresh_hand_labels()
        self.stack.setCurrentIndex(1)

    def _rerun_wizard(self):
        self.wizard_page._go_to_page(0)
        self.stack.setCurrentIndex(0)

    @Slot(object, dict, dict, dict, dict)
    def _on_tracking_processed(
        self,
        annotated_frame: np.ndarray,
        info: dict,
        steering_data: dict,
        pedal_data: dict,
        controller_data: dict
    ):
        curr_page = self.stack.currentIndex()
        if curr_page == 0:  # Setup Wizard
            self.wizard_page.feed_frame_and_tracking(
                annotated_frame, info, steering_data, pedal_data, controller_data
            )
        elif curr_page == 1:  # Main Dashboard
            self.dashboard_page.update_frame(annotated_frame)
            self.dashboard_page.update_telemetry(
                tracking_info=info,
                steering_deg=steering_data["relative_angle"],
                steering_norm=steering_data["normalized"],
                wheel_rot=steering_data["wheel_rotation"],
                accel_pct=pedal_data["accelerator"],
                brake_pct=pedal_data["brake"],
                ctrl_steering=controller_data["steering"],
                ctrl_accel=controller_data["accel"],
                ctrl_brake=controller_data["brake"]
            )

    def keyPressEvent(self, event: QKeyEvent):
        # Emergency Stop Shortcut: ESC
        if event.key() == Qt.Key_Escape:
            logger.warning("ESC key pressed: triggering emergency stop.")
            self.dashboard_page._on_emergency_clicked()
        super().keyPressEvent(event)

    def closeEvent(self, event):
        logger.info("Shutting down Virtual Drive...")
        camera_manager.stop_camera()
        if hasattr(self, "tracking_worker") and self.tracking_worker.isRunning():
            self.tracking_worker.stop()
        self.virtual_controller.shutdown()
        event.accept()


def main():
    setup_logger()
    logger.info("Initializing Virtual Drive Application...")
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)

    window = VirtualDriveMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

