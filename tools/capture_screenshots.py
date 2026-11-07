"""Automated screenshot capture script for documentation."""
import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap

from main import VirtualDriveMainWindow
from ui.styles import GLOBAL_STYLE
from utils.config_manager import config_manager

def capture_all_pages():
    os.makedirs("docs/screenshots", exist_ok=True)
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)

    window = VirtualDriveMainWindow()
    window.resize(1180, 720)
    window.show()

    # Allow layout pass
    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    # Capture Wizard Pages (Stack Index 0)
    window.stack.setCurrentIndex(0)
    wizard = window.wizard_page

    pages = [
        (0, "01_welcome.png"),
        (1, "02_camera_setup.png"),
        (2, "03_hand_detection.png"),
        (3, "04_steering_calibration.png"),
        (4, "05_pedal_calibration.png"),
        (5, "06_gamepad_test.png"),
        (6, "07_finish_setup.png"),
    ]

    for idx, filename in pages:
        wizard._go_to_page(idx)
        app.processEvents()
        time.sleep(0.05)
        app.processEvents()
        pix = window.grab()
        path = os.path.join("docs", "screenshots", filename)
        pix.save(path)
        print(f"Captured: {path}")

    # Capture Main Dashboard (Stack Index 1)
    window.stack.setCurrentIndex(1)
    app.processEvents()
    time.sleep(0.05)
    app.processEvents()
    pix = window.grab()
    path_dash = os.path.join("docs", "screenshots", "08_cockpit_dashboard.png")
    pix.save(path_dash)
    print(f"Captured: {path_dash}")

    # Capture Settings Page (Stack Index 2)
    window.stack.setCurrentIndex(2)
    app.processEvents()
    time.sleep(0.05)
    app.processEvents()
    pix = window.grab()
    path_sett = os.path.join("docs", "screenshots", "09_settings_page.png")
    pix.save(path_sett)
    print(f"Captured: {path_sett}")

    window.close()
    print("All screenshots captured successfully!")

if __name__ == "__main__":
    capture_all_pages()
