"""Unit tests for calibration manager and sample averaging."""
import unittest
from core.calibration_manager import CalibrationManager

class TestCalibration(unittest.TestCase):
    def setUp(self):
        self.mgr = CalibrationManager()

    def test_sample_averaging_median(self):
        self.mgr.start_sampling()
        # Add 5 samples with one outlier
        self.mgr.add_sample(10.0)
        self.mgr.add_sample(10.2)
        self.mgr.add_sample(10.1)
        self.mgr.add_sample(9.9)
        self.mgr.add_sample(50.0)  # Outlier

        val = self.mgr.get_average_sample()
        # Median should reject outlier and be close to 10.1
        self.assertAlmostEqual(val, 10.1, places=1)

    def test_commit_steering_angles(self):
        self.mgr.start_sampling()
        self.mgr.add_sample(2.5)
        self.mgr.add_sample(2.7)
        neu = self.mgr.commit_neutral_angle()
        self.assertAlmostEqual(neu, 2.6, places=1)
        self.assertEqual(len(self.mgr.sample_buffer), 0)

    def test_pedal_commit(self):
        self.mgr.start_sampling()
        self.mgr.add_sample(0.38)
        self.mgr.commit_pedal_relaxed(is_accelerator=True)
        self.assertAlmostEqual(self.mgr.accel_relaxed, 0.38, places=2)

if __name__ == "__main__":
    unittest.main()

