"""Integration test verifying application instantiation and clean shutdown."""
import unittest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from main import VirtualDriveMainWindow

class TestAppLaunch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_window_instantiation_and_shutdown(self):
        window = VirtualDriveMainWindow()
        self.assertIsNotNone(window)
        self.assertEqual(window.stack.count(), 3)
        # Verify initial page is Setup Wizard or Dashboard
        self.assertIn(window.stack.currentIndex(), (0, 1))

        # Test simulated shutdown
        window.close()

if __name__ == "__main__":
    unittest.main()

