"""Unit tests for Virtual Xbox 360 controller mappings and safety."""
import unittest
from core.virtual_controller import VirtualXboxController

class TestVirtualController(unittest.TestCase):
    def setUp(self):
        self.ctrl = VirtualXboxController()

    def test_steering_axis_mapping(self):
        # Full Left (-1.0) -> -32768
        self.ctrl.update_inputs(steering_norm=-1.0, accel_pct=0.0, brake_pct=0.0)
        self.assertEqual(self.ctrl.current_steering, -32768)

        # Center (0.0) -> 0
        self.ctrl.update_inputs(steering_norm=0.0, accel_pct=0.0, brake_pct=0.0)
        self.assertEqual(self.ctrl.current_steering, 0)

        # Full Right (+1.0) -> 32767
        self.ctrl.update_inputs(steering_norm=1.0, accel_pct=0.0, brake_pct=0.0)
        self.assertEqual(self.ctrl.current_steering, 32767)

        # Half Right (0.5)
        self.ctrl.update_inputs(steering_norm=0.5, accel_pct=0.0, brake_pct=0.0)
        self.assertAlmostEqual(self.ctrl.current_steering, 16383, delta=2)

    def test_pedal_trigger_mapping(self):
        # 0% -> 0
        self.ctrl.update_inputs(steering_norm=0.0, accel_pct=0.0, brake_pct=0.0)
        self.assertEqual(self.ctrl.current_accel, 0)
        self.assertEqual(self.ctrl.current_brake, 0)

        # 100% -> 255
        self.ctrl.update_inputs(steering_norm=0.0, accel_pct=100.0, brake_pct=100.0)
        self.assertEqual(self.ctrl.current_accel, 255)
        self.assertEqual(self.ctrl.current_brake, 255)

        # 50% -> ~127
        self.ctrl.update_inputs(steering_norm=0.0, accel_pct=50.0, brake_pct=50.0)
        self.assertAlmostEqual(self.ctrl.current_accel, 127, delta=1)
        self.assertAlmostEqual(self.ctrl.current_brake, 127, delta=1)

    def test_reset_neutral(self):
        self.ctrl.update_inputs(steering_norm=1.0, accel_pct=80.0, brake_pct=60.0)
        self.ctrl.reset_neutral()
        self.assertEqual(self.ctrl.current_steering, 0)
        self.assertEqual(self.ctrl.current_accel, 0)
        self.assertEqual(self.ctrl.current_brake, 0)

    def test_graceful_missing_driver(self):
        # Controller should not crash if driver is missing, but return False with clear status
        success, msg = self.ctrl.initialize()
        if not success:
            self.assertIn("ViGEmBus", msg)
            self.assertFalse(self.ctrl.is_connected)

if __name__ == "__main__":
    unittest.main()

