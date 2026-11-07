"""Sensitivity management for steering, accelerator, and brake."""
from typing import Dict, Any

class SensitivityManager:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # Steering defaults
        self.steering_sensitivity = 50.0  # 1% to 100%
        self.steering_deadzone = 2.0     # Degrees or percent
        self.steering_smoothing = 0.35   # Alpha
        self.steering_max_rotation = 180.0
        self.centering_enabled = True
        self.centering_speed = 0.15

        # Pedal defaults
        self.accel_sensitivity = 50.0
        self.accel_deadzone = 5.0
        self.accel_smoothing = 0.30

        self.brake_sensitivity = 50.0
        self.brake_deadzone = 5.0
        self.brake_smoothing = 0.30

        self.load_from_config(self.config)

    def load_from_config(self, cfg: Dict[str, Any]):
        st = cfg.get("steering", {})
        self.steering_sensitivity = float(st.get("sensitivity", 50.0))
        self.steering_deadzone = float(st.get("deadzone", 2.0))
        self.steering_smoothing = float(st.get("smoothing", 0.35))
        self.steering_max_rotation = float(st.get("max_rotation_degrees", 180.0))
        self.centering_enabled = bool(st.get("centering_enabled", True))
        self.centering_speed = float(st.get("centering_speed", 0.15))

        pedals = cfg.get("pedals", {})
        acc = pedals.get("accelerator", {})
        self.accel_sensitivity = float(acc.get("sensitivity", 50.0))
        self.accel_deadzone = float(acc.get("deadzone", 5.0))
        self.accel_smoothing = float(acc.get("smoothing", 0.30))

        brk = pedals.get("brake", {})
        self.brake_sensitivity = float(brk.get("sensitivity", 50.0))
        self.brake_deadzone = float(brk.get("deadzone", 5.0))
        self.brake_smoothing = float(brk.get("smoothing", 0.30))

