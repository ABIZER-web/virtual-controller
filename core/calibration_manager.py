"""Calibration manager for steering angles and pedal gesture ranges."""
from typing import Dict, Any, List
import numpy as np
from utils.logger import logger
from utils.config_manager import config_manager

class CalibrationManager:
    def __init__(self):
        self.neutral_angle: float = 0.0
        self.calibrated_left_max: float = -45.0
        self.calibrated_right_max: float = 45.0

        # Pedals: relaxed distance vs pressed distance (normalized landmark distance)
        self.accel_relaxed: float = 0.35
        self.accel_pressed: float = 0.10

        self.brake_relaxed: float = 0.35
        self.brake_pressed: float = 0.10

        # Buffer for averaging samples during calibration
        self.sample_buffer: List[float] = []

        self.load_calibration()

    def load_calibration(self):
        cfg = config_manager.load()
        st = cfg.get("steering", {})
        self.neutral_angle = float(st.get("neutral_angle", 0.0))
        self.calibrated_left_max = float(st.get("calibrated_left_max", -45.0))
        self.calibrated_right_max = float(st.get("calibrated_right_max", 45.0))

        pedals = cfg.get("pedals", {})
        acc = pedals.get("accelerator", {})
        self.accel_relaxed = float(acc.get("relaxed_val", 0.35))
        self.accel_pressed = float(acc.get("pressed_val", 0.10))

        brk = pedals.get("brake", {})
        self.brake_relaxed = float(brk.get("relaxed_val", 0.35))
        self.brake_pressed = float(brk.get("pressed_val", 0.10))

    def save_calibration(self):
        config_manager.set("steering.neutral_angle", self.neutral_angle)
        config_manager.set("steering.calibrated_left_max", self.calibrated_left_max)
        config_manager.set("steering.calibrated_right_max", self.calibrated_right_max)

        config_manager.set("pedals.accelerator.relaxed_val", self.accel_relaxed)
        config_manager.set("pedals.accelerator.pressed_val", self.accel_pressed)

        config_manager.set("pedals.brake.relaxed_val", self.brake_relaxed)
        config_manager.set("pedals.brake.pressed_val", self.brake_pressed)
        config_manager.save()
        logger.info("Calibration data saved successfully.")

    def start_sampling(self):
        self.sample_buffer.clear()

    def add_sample(self, val: float):
        self.sample_buffer.append(val)

    def get_average_sample(self, default: float = 0.0) -> float:
        if not self.sample_buffer:
            return default
        # Drop outliers if enough samples
        if len(self.sample_buffer) >= 5:
            arr = np.array(self.sample_buffer)
            med = float(np.median(arr))
            return med
        return float(np.mean(self.sample_buffer))

    def commit_neutral_angle(self) -> float:
        avg = self.get_average_sample(0.0)
        self.neutral_angle = avg
        self.sample_buffer.clear()
        logger.info("Committed neutral steering angle: %.2f deg", self.neutral_angle)
        return self.neutral_angle

    def commit_left_max(self) -> float:
        avg = self.get_average_sample(-45.0)
        self.calibrated_left_max = avg
        self.sample_buffer.clear()
        logger.info("Committed left max steering angle: %.2f deg", self.calibrated_left_max)
        return self.calibrated_left_max

    def commit_right_max(self) -> float:
        avg = self.get_average_sample(45.0)
        self.calibrated_right_max = avg
        self.sample_buffer.clear()
        logger.info("Committed right max steering angle: %.2f deg", self.calibrated_right_max)
        return self.calibrated_right_max

    def commit_pedal_relaxed(self, is_accelerator: bool) -> float:
        avg = self.get_average_sample(0.35)
        if is_accelerator:
            self.accel_relaxed = avg
            logger.info("Committed Accelerator Relaxed: %.3f", avg)
        else:
            self.brake_relaxed = avg
            logger.info("Committed Brake Relaxed: %.3f", avg)
        self.sample_buffer.clear()
        return avg

    def commit_pedal_pressed(self, is_accelerator: bool) -> float:
        avg = self.get_average_sample(0.10)
        if is_accelerator:
            self.accel_pressed = avg
            logger.info("Committed Accelerator Pressed: %.3f", avg)
        else:
            self.brake_pressed = avg
            logger.info("Committed Brake Pressed: %.3f", avg)
        self.sample_buffer.clear()
        return avg

calibration_manager = CalibrationManager()

