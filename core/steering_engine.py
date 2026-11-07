"""Steering calculation engine based on dual wrist landmark orientation."""
import math
import time
from typing import Optional, Tuple
from core.smoothing import LowPassFilter, apply_deadzone, apply_response_curve
from core.sensitivity_manager import SensitivityManager
from core.calibration_manager import CalibrationManager
from utils.logger import logger

class SteeringEngine:
    def __init__(self, sensitivity_mgr: SensitivityManager, calibration_mgr: CalibrationManager):
        self.sensitivity_mgr = sensitivity_mgr
        self.calibration_mgr = calibration_mgr

        # Low pass filter for angle
        self.filter = LowPassFilter(alpha=self.sensitivity_mgr.steering_smoothing)

        # Output states
        self.raw_angle_deg: float = 0.0
        self.relative_angle_deg: float = 0.0
        self.smoothed_angle_deg: float = 0.0
        self.normalized_steering: float = 0.0  # -1.0 (Full Left) to +1.0 (Full Right)
        self.wheel_rotation_deg: float = 0.0    # Virtual wheel display angle

        # Tracking state
        self.is_tracking: bool = False
        self.last_track_time: float = time.time()
        self.grace_period_sec: float = 0.35  # Grace period before auto-centering

    def calculate_raw_angle(self, left_wrist: Tuple[float, float], right_wrist: Tuple[float, float]) -> float:
        """
        Calculates angle in degrees between Left Wrist (x1, y1) and Right Wrist (x2, y2).
        x and y are in normalized coordinates [0.0, 1.0] or pixel coordinates.
        y is inverted in screen space (0 at top).
        Right hand lower (y2 > y1) -> positive angle (Turning Right)
        Right hand higher (y2 < y1) -> negative angle (Turning Left)
        """
        dx = right_wrist[0] - left_wrist[0]
        dy = right_wrist[1] - left_wrist[1]

        # In case hands are swapped or directly vertical, dx shouldn't be zero
        rad = math.atan2(dy, dx)
        deg = math.degrees(rad)
        return deg

    def update(self, left_wrist: Optional[Tuple[float, float]], right_wrist: Optional[Tuple[float, float]]) -> float:
        """
        Updates the steering state.
        Returns normalized_steering (-1.0 to 1.0).
        """
        now = time.time()
        self.filter.set_alpha(self.sensitivity_mgr.steering_smoothing)

        if left_wrist is not None and right_wrist is not None:
            self.is_tracking = True
            self.last_track_time = now

            # 1. Calculate raw angle
            raw_deg = self.calculate_raw_angle(left_wrist, right_wrist)
            self.raw_angle_deg = raw_deg

            # 2. Compute angle relative to neutral calibration with wrapping
            neutral = self.calibration_mgr.neutral_angle
            diff = (raw_deg - neutral + 180.0) % 360.0 - 180.0
            self.relative_angle_deg = diff

            # 3. Apply low-pass filter
            smoothed_deg = self.filter.update(diff)
            self.smoothed_angle_deg = smoothed_deg

        else:
            self.is_tracking = False
            # Check grace period
            elapsed_loss = now - self.last_track_time
            if elapsed_loss > self.grace_period_sec:
                # Smoothly return to center
                center_speed = self.sensitivity_mgr.centering_speed
                if self.sensitivity_mgr.centering_enabled:
                    smoothed_deg = self.smoothed_angle_deg * (1.0 - center_speed)
                    if abs(smoothed_deg) < 0.1:
                        smoothed_deg = 0.0
                    self.smoothed_angle_deg = smoothed_deg
                    self.filter.reset(smoothed_deg)
                else:
                    self.smoothed_angle_deg = 0.0
                    self.filter.reset(0.0)
            else:
                smoothed_deg = self.smoothed_angle_deg

        # 4. Map to normalized steering (-1.0 to 1.0)
        # Determine calibrated limits
        calib_range = max(10.0, (abs(self.calibration_mgr.calibrated_right_max) + abs(self.calibration_mgr.calibrated_left_max)) / 2.0)
        
        # Sensitivity multiplier (50% = 1.0x, 100% = 2.0x, 10% = 0.2x)
        sens_multiplier = max(0.1, self.sensitivity_mgr.steering_sensitivity / 50.0)

        # Scale by calibrated range
        raw_norm = (self.smoothed_angle_deg / calib_range) * sens_multiplier
        raw_norm = max(-1.0, min(1.0, raw_norm))

        # 5. Apply deadzone (deadzone is in percent, e.g. 2.0% -> 0.02)
        deadzone_val = (self.sensitivity_mgr.steering_deadzone / 100.0)
        norm_deadzone = apply_deadzone(raw_norm, deadzone_val)

        # 6. Apply response curve
        self.normalized_steering = apply_response_curve(norm_deadzone, curve_type="linear")

        # 7. Map to virtual wheel rotation degrees for display
        max_wheel_rot = self.sensitivity_mgr.steering_max_rotation
        self.wheel_rotation_deg = self.normalized_steering * max_wheel_rot

        return self.normalized_steering

    def reset(self):
        self.raw_angle_deg = 0.0
        self.relative_angle_deg = 0.0
        self.smoothed_angle_deg = 0.0
        self.normalized_steering = 0.0
        self.wheel_rotation_deg = 0.0
        self.filter.reset(0.0)
        self.is_tracking = False

