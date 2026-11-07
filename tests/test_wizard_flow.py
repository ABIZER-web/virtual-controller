"""Unit tests verifying setup completion persistence and view routing."""
import unittest
import sys
from PySide6.QtWidgets import QApplication
from utils.config_manager import config_manager
from main import VirtualDriveMainWindow

class TestWizardFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_first_launch_opens_wizard(self):
        config_manager.set("setup_completed", False)
        config_manager.save()

        window = VirtualDriveMainWindow()
        self.assertEqual(window.stack.currentIndex(), 0)  # Setup Wizard
        window.close()

    def test_completed_setup_opens_dashboard_directly(self):
        config_manager.set("setup_completed", True)
        config_manager.save()

        window = VirtualDriveMainWindow()
        self.assertEqual(window.stack.currentIndex(), 1)  # Cockpit Dashboard directly!
        window.close()

    def test_rerun_wizard_from_settings(self):
        config_manager.set("setup_completed", True)
        config_manager.save()

        window = VirtualDriveMainWindow()
        self.assertEqual(window.stack.currentIndex(), 1)

        # Go to settings
        window.dashboard_page.open_settings_requested.emit()
        self.assertEqual(window.stack.currentIndex(), 2)

        # Click Re-run Wizard
        window.settings_page.rerun_wizard_requested.emit()
        self.assertEqual(window.stack.currentIndex(), 0)  # Returns to wizard

        # Back to dashboard
        window.wizard_page.wizard_completed.emit()
        self.assertEqual(window.stack.currentIndex(), 1)
        self.assertTrue(config_manager.get("setup_completed", False))

        window.close()

if __name__ == "__main__":
    unittest.main()

