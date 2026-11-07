"""Pedal calculation engine for analog Accelerator and Brake gestures."""
import math
import time
from typing import Optional, List, Dict, Any
from core.smoothing import LowPassFilter, apply_deadzone, apply_response_curve
from core.sensitivity_manager import SensitivityManager
from core.calibration_manager import CalibrationManager
from core.hand_assignment import HandAssignment
from utils.logger import logger

class PedalEngine:
    def __init__(
        self,
        sensitivity_mgr: SensitivityManager,
        calibration_mgr: CalibrationManager,
        hand_assignment: HandAssignment
    ):
        self.sensitivity_mgr = sensitivity_mgr
        self.calibration_mgr = calibration_mgr
        self.hand_assignment = hand_assignment

        # Independent filters
        self.accel_filter = LowPassFilter(alpha=self.sensitivity_mgr.accel_smoothing)
        self.brake_filter = LowPassFilter(alpha=self.sensitivity_mgr.brake_smoothing)

        # Output states (0.0 to 100.0%)
        self.accel_pct: float = 0.0
        self.brake_pct: float = 0.0

        # Raw distance measurements
        self.raw_accel_dist: float = 0.35
        self.raw_brake_dist: float = 0.35

        # Tracking status
        self.accel_tracking: bool = False
        self.brake_tracking: bool = False
        self.last_accel_time: float = time.time()
        self.last_brake_time: float = time.time()
        self.grace_period_sec: float = 0.25

    @staticmethod
    def calculate_hand_scale(landmarks: List[Any]) -> float:
        """
        Calculates hand scale using distance from Wrist (0) to Middle Finger MCP (9).
        Prevents division by zero.
        """
        w = landmarks[0]
        m = landmarks[9]
        dx = m.x - w.x
        dy = m.y - w.y
        scale = math.sqrt(dx * dx + dy * dy)
        return max(0.05, scale)

    @staticmethod
    def calculate_finger_squeeze_distance(landmarks: List[Any]) -> float:
        """
        Calculates normalized squeeze distance between Thumb Tip (4) and Middle Finger Tip (12).
        Scaled relative to hand palm size.
        """
        scale = PedalEngine.calculate_hand_scale(landmarks)
        thumb = landmarks[4]
        middle = landmarks[12]

        dx = thumb.x - middle.x
        dy = thumb.y - middle.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist / scale

    def update(
        self,
        left_hand_landmarks: Optional[List[Any]],
        right_hand_landmarks: Optional[List[Any]]
    ) -> Dict[str, float]:
        """
        Updates accelerator and brake values according to hand assignments.
        Returns {'accelerator': float, 'brake': float} in range 0.0 to 100.0.
        """
        now = time.time()
        self.accel_filter.set_alpha(self.sensitivity_mgr.accel_smoothing)
        self.brake_filter.set_alpha(self.sensitivity_mgr.brake_smoothing)

        accel_hand = self.hand_assignment.accelerator_hand  # 'Left' or 'Right'
        brake_hand = self.hand_assignment.brake_hand        # 'Left' or 'Right'

        accel_landmarks = right_hand_landmarks if accel_hand == "Right" else left_hand_landmarks
        brake_landmarks = right_hand_landmarks if brake_hand == "Right" else left_hand_landmarks

        # --- PROCESS ACCELERATOR ---
        if accel_landmarks is not None:
            self.accel_tracking = True
            self.last_accel_time = now
            dist = self.calculate_finger_squeeze_distance(accel_landmarks)
            self.raw_accel_dist = dist

            # Mapping: relaxed is large dist, pressed is small dist
            relaxed = self.calibration_mgr.accel_relaxed
            pressed = self.calibration_mgr.accel_pressed
            denom = relaxed - pressed
            if abs(denom) < 0.01:
                denom = 0.01

            raw_squeeze = (relaxed - dist) / denom
            raw_squeeze = max(0.0, min(1.0, raw_squeeze))

            # Sensitivity multiplier
            sens_multiplier = max(0.2, self.sensitivity_mgr.accel_sensitivity / 50.0)
            scaled = min(1.0, raw_squeeze * sens_multiplier)

            # Deadzone
            deadzone = self.sensitivity_mgr.accel_deadzone / 100.0
            dz_squeeze = apply_deadzone(scaled, deadzone)

            # Response curve & smoothing
            curved = apply_response_curve(dz_squeeze, curve_type="linear")
            smoothed = self.accel_filter.update(curved)
            self.accel_pct = max(0.0, min(100.0, smoothed * 100.0))
        else:
            self.accel_tracking = False
            if now - self.last_accel_time > self.grace_period_sec:
                # Emergency release
                self.accel_pct = 0.0
                self.accel_filter.reset(0.0)

        # --- PROCESS BRAKE ---
        if brake_landmarks is not None:
            self.brake_tracking = True
            self.last_brake_time = now
            dist = self.calculate_finger_squeeze_distance(brake_landmarks)
            self.raw_brake_dist = dist

            relaxed = self.calibration_mgr.brake_relaxed
            pressed = self.calibration_mgr.brake_pressed
            denom = relaxed - pressed
            if abs(denom) < 0.01:
                denom = 0.01

            raw_squeeze = (relaxed - dist) / denom
            raw_squeeze = max(0.0, min(1.0, raw_squeeze))

            sens_multiplier = max(0.2, self.sensitivity_mgr.brake_sensitivity / 50.0)
            scaled = min(1.0, raw_squeeze * sens_multiplier)

            deadzone = self.sensitivity_mgr.brake_deadzone / 100.0
            dz_squeeze = apply_deadzone(scaled, deadzone)

            curved = apply_response_curve(dz_squeeze, curve_type="linear")
            smoothed = self.brake_filter.update(curved)
            self.brake_pct = max(0.0, min(100.0, smoothed * 100.0))
        else:
            self.brake_tracking = False
            if now - self.last_brake_time > self.grace_period_sec:
                # Emergency release
                self.brake_pct = 0.0
                self.brake_filter.reset(0.0)

        return {"accelerator": self.accel_pct, "brake": self.brake_pct}

    def reset(self):
        self.accel_pct = 0.0
        self.brake_pct = 0.0
        self.accel_tracking = False
        self.brake_tracking = False
        self.accel_filter.reset(0.0)
        self.brake_filter.reset(0.0)

