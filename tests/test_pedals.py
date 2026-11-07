"""Unit tests for Pedal squeeze calculations and independent controls."""
import unittest
from types import SimpleNamespace
from core.pedal_engine import PedalEngine
from core.sensitivity_manager import SensitivityManager
from core.calibration_manager import CalibrationManager
from core.hand_assignment import HandAssignment

class MockLandmark:
    def __init__(self, x: float, y: float, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

def create_mock_hand(relaxed: bool = True):
    # 21 points
    lms = [MockLandmark(0.5, 0.8) for _ in range(21)]
    # Wrist is index 0 (0.5, 0.8)
    # Middle finger MCP is index 9 (0.5, 0.5) -> palm scale = 0.3
    lms[0] = MockLandmark(0.5, 0.8)
    lms[9] = MockLandmark(0.5, 0.5)

    if relaxed:
        # Thumb tip (4) and Middle finger tip (12) are far apart
        lms[4] = MockLandmark(0.35, 0.4)
        lms[12] = MockLandmark(0.55, 0.2)
    else:
        # Squeezed: Thumb tip and Middle finger tip are touching
        lms[4] = MockLandmark(0.50, 0.3)
        lms[12] = MockLandmark(0.51, 0.31)

    return lms

class TestPedals(unittest.TestCase):
    def setUp(self):
        self.sens_mgr = SensitivityManager()
        self.calib_mgr = CalibrationManager()
        self.calib_mgr.accel_relaxed = 0.40
        self.calib_mgr.accel_pressed = 0.05
        self.calib_mgr.brake_relaxed = 0.40
        self.calib_mgr.brake_pressed = 0.05

        self.hand_assignment = HandAssignment(accelerator_hand="Right", brake_hand="Left")
        self.engine = PedalEngine(self.sens_mgr, self.calib_mgr, self.hand_assignment)

    def test_hand_scale_calculation(self):
        hand = create_mock_hand(relaxed=True)
        scale = self.engine.calculate_hand_scale(hand)
        self.assertAlmostEqual(scale, 0.3, places=2)

    def test_finger_squeeze_distance_relaxed_vs_pressed(self):
        hand_relaxed = create_mock_hand(relaxed=True)
        hand_pressed = create_mock_hand(relaxed=False)

        dist_rel = self.engine.calculate_finger_squeeze_distance(hand_relaxed)
        dist_prs = self.engine.calculate_finger_squeeze_distance(hand_pressed)

        # Pressed distance must be strictly smaller than relaxed distance
        self.assertLess(dist_prs, dist_rel)

    def test_independent_pedal_outputs(self):
        hand_relaxed = create_mock_hand(relaxed=True)
        hand_pressed = create_mock_hand(relaxed=False)

        # Right Hand (Accel) squeezed, Left Hand (Brake) relaxed
        outputs = self.engine.update(
            left_hand_landmarks=hand_relaxed,
            right_hand_landmarks=hand_pressed
        )

        self.assertGreater(outputs["accelerator"], 20.0)
        self.assertLess(outputs["brake"], 15.0)

    def test_safety_loss_release(self):
        hand_pressed = create_mock_hand(relaxed=False)
        self.engine.update(left_hand_landmarks=None, right_hand_landmarks=hand_pressed)

        # Now simulate loss of right hand
        self.engine.last_accel_time -= 1.0  # Expire grace period
        outputs = self.engine.update(left_hand_landmarks=None, right_hand_landmarks=None)
        self.assertEqual(outputs["accelerator"], 0.0)
        self.assertEqual(outputs["brake"], 0.0)

if __name__ == "__main__":
    unittest.main()

