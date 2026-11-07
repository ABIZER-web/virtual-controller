"""Virtual Xbox 360 Controller interface using vgamepad with ViGEmBus support."""
import sys
from typing import Optional, Tuple
from utils.logger import logger

class VirtualXboxController:
    """
    Manages the virtual Xbox 360 controller emulation.
    Maps:
      - Steering: Left Stick X axis (-32768 to 32767)
      - Accelerator: Right Trigger RT (0 to 255)
      - Brake: Left Trigger LT (0 to 255)
    """
    def __init__(self):
        self.gamepad = None
        self.is_connected = False
        self.error_message = ""
        self.driver_installed = False

        # State tracking
        self.current_steering: int = 0
        self.current_accel: int = 0
        self.current_brake: int = 0

    def initialize(self) -> Tuple[bool, str]:
        """
        Attempts to initialize the virtual Xbox 360 gamepad.
        Returns (success: bool, status_message: str)
        """
        try:
            # Lazy import to avoid crash if ViGEmBus driver is missing
            import vgamepad as vg
            self.gamepad = vg.VX360Gamepad()
            self.is_connected = True
            self.driver_installed = True
            self.error_message = ""
            logger.info("Virtual Xbox 360 controller successfully initialized.")
            self.reset_neutral()
            return True, "Connected: Virtual Xbox 360 Controller ready."
        except RuntimeError as e:
            self.is_connected = False
            err = str(e)
            if "VIGEM_ERROR_BUS_NOT_FOUND" in err:
                self.driver_installed = False
                self.error_message = "ViGEmBus driver not found. Please install the ViGEmBus driver to enable Xbox 360 emulation."
            else:
                self.error_message = f"Gamepad runtime error: {err}"
            logger.warning("Virtual controller initialization failed: %s", self.error_message)
            return False, self.error_message
        except Exception as e:
            self.is_connected = False
            self.error_message = f"Failed to initialize virtual controller: {e}"
            logger.error(self.error_message)
            return False, self.error_message

    def update_inputs(self, steering_norm: float, accel_pct: float, brake_pct: float):
        """
        Updates controller inputs:
          - steering_norm: -1.0 (full left) to +1.0 (full right)
          - accel_pct: 0.0 to 100.0
          - brake_pct: 0.0 to 100.0
        """
        # Clamp inputs
        s_norm = max(-1.0, min(1.0, steering_norm))
        a_norm = max(0.0, min(100.0, accel_pct)) / 100.0
        b_norm = max(0.0, min(100.0, brake_pct)) / 100.0

        # Convert to Xbox 360 axis values
        # Left Stick X: -32768 to 32767
        if s_norm >= 0:
            raw_steering = int(s_norm * 32767)
        else:
            raw_steering = int(s_norm * 32768)
        raw_steering = max(-32768, min(32767, raw_steering))

        # Triggers: 0 to 255
        raw_accel = int(a_norm * 255)
        raw_brake = int(b_norm * 255)

        self.current_steering = raw_steering
        self.current_accel = raw_accel
        self.current_brake = raw_brake

        if self.is_connected and self.gamepad:
            try:
                # Left Joystick X axis
                self.gamepad.left_joystick(x_value=raw_steering, y_value=0)
                # Right Trigger: Accelerator
                self.gamepad.right_trigger(value=raw_accel)
                # Left Trigger: Brake
                self.gamepad.left_trigger(value=raw_brake)
                self.gamepad.update()
            except Exception as e:
                logger.error("Error sending gamepad update: %s", e)
                self.is_connected = False

    def reset_neutral(self):
        """Resets all controls to zero/center."""
        self.current_steering = 0
        self.current_accel = 0
        self.current_brake = 0
        if self.is_connected and self.gamepad:
            try:
                self.gamepad.left_joystick(x_value=0, y_value=0)
                self.gamepad.right_trigger(value=0)
                self.gamepad.left_trigger(value=0)
                self.gamepad.update()
            except Exception as e:
                logger.error("Error resetting gamepad: %s", e)

    def shutdown(self):
        """Safely release and shutdown the virtual controller."""
        if self.is_connected and self.gamepad:
            try:
                self.reset_neutral()
                del self.gamepad
                self.gamepad = None
            except Exception as e:
                logger.error("Error shutting down gamepad: %s", e)
        self.is_connected = False
        logger.info("Virtual controller shutdown complete.")

