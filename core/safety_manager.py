"""Safety and Emergency Stop Manager."""
import time
from typing import Callable, List
from utils.logger import logger

class SafetyManager:
    def __init__(self):
        self.emergency_stop_active: bool = False
        self.emergency_callbacks: List[Callable[[], None]] = []
        self.last_healthy_tracking: float = time.time()
        self.tracking_loss_warning: bool = False

    def register_callback(self, cb: Callable[[], None]):
        self.emergency_callbacks.append(cb)

    def trigger_emergency_stop(self, reason: str = "User Initiated"):
        self.emergency_stop_active = True
        logger.warning("EMERGENCY STOP TRIGGERED: %s", reason)
        for cb in self.emergency_callbacks:
            try:
                cb()
            except Exception as e:
                logger.error("Error in emergency stop callback: %s", e)

    def resume_control(self):
        self.emergency_stop_active = False
        logger.info("Control resumed from emergency stop.")

    def notify_tracking_health(self, is_tracking: bool):
        now = time.time()
        if is_tracking:
            self.last_healthy_tracking = now
            self.tracking_loss_warning = False
        else:
            if now - self.last_healthy_tracking > 1.0:
                self.tracking_loss_warning = True

safety_manager = SafetyManager()

