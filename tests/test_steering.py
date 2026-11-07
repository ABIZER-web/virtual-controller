"""Unit tests for Steering calculations and smoothing."""
import unittest
import math
import time
from core.steering_engine import SteeringEngine
from core.sensitivity_manager import SensitivityManager
from core.calibration_manager import CalibrationManager
from core.smoothing import apply_deadzone, apply_response_curve, LowPassFilter

class TestSteering(unittest.TestCase):
    def setUp(self):
        self.sens_mgr = SensitivityManager()
        self.calib_mgr = CalibrationManager()
        self.calib_mgr.neutral_angle = 0.0
        self.calib_mgr.calibrated_left_max = -45.0
        self.calib_mgr.calibrated_right_max = 45.0
        self.engine = SteeringEngine(self.sens_mgr, self.calib_mgr)

    def test_horizontal_hands_neutral(self):
        # Left wrist at (0.3, 0.5), Right wrist at (0.7, 0.5) -> perfectly horizontal
        raw = self.engine.calculate_raw_angle((0.3, 0.5), (0.7, 0.5))
        self.assertAlmostEqual(raw, 0.0, places=3)

    def test_left_turn_angle(self):
        # Turning left: left hand down (y=0.6), right hand up (y=0.4)
        # dy = 0.4 - 0.6 = -0.2 -> negative angle
        raw = self.engine.calculate_raw_angle((0.3, 0.6), (0.7, 0.4))
        self.assertLess(raw, 0.0)

    def test_right_turn_angle(self):
        # Turning right: right hand down (y=0.6), left hand up (y=0.4)
        # dy = 0.6 - 0.4 = +0.2 -> positive angle
        raw = self.engine.calculate_raw_angle((0.3, 0.4), (0.7, 0.6))
        self.assertGreater(raw, 0.0)

    def test_deadzone_filter(self):
        # Values under deadzone should be 0.0
        self.assertEqual(apply_deadzone(0.01, deadzone=0.05), 0.0)
        self.assertEqual(apply_deadzone(-0.02, deadzone=0.05), 0.0)
        # Values above deadzone should scale smoothly
        scaled = apply_deadzone(0.10, deadzone=0.05)
        self.assertGreater(scaled, 0.0)

    def test_steering_update_limits(self):
        # Simulate extreme turn
        # Neutral = 0, Calibrated Right Max = 45
        # Set wrists for ~45 deg
        dx = 0.4
        dy = 0.4  # atan2(0.4, 0.4) = 45 deg
        norm = self.engine.update((0.3, 0.3), (0.7, 0.7))
        self.assertGreater(norm, 0.5)
        self.assertLessEqual(norm, 1.0)

    def test_centering_on_tracking_loss(self):
        # First update with right turn
        self.engine.update((0.3, 0.3), (0.7, 0.7))
        self.assertGreater(self.engine.smoothed_angle_deg, 10.0)

        # Force time elapsed beyond grace period
        self.engine.last_track_time = time.time() - 1.0
        # Update with lost tracking (None, None)
        self.engine.update(None, None)
        # Smoothed angle should decay towards center
        self.assertLess(self.engine.smoothed_angle_deg, 40.0)

if __name__ == "__main__":
    unittest.main()

