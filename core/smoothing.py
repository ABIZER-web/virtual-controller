"""Filtering, smoothing, deadzone, and response curves for analog inputs."""
import math

class LowPassFilter:
    """Exponential Moving Average filter."""
    def __init__(self, alpha: float = 0.35, initial_value: float = 0.0):
        self.alpha = max(0.01, min(1.0, alpha))
        self.current_value = initial_value
        self.initialized = False

    def update(self, target_value: float) -> float:
        if not self.initialized:
            self.current_value = target_value
            self.initialized = True
        else:
            self.current_value = self.alpha * target_value + (1.0 - self.alpha) * self.current_value
        return self.current_value

    def reset(self, val: float = 0.0):
        self.current_value = val
        self.initialized = False

    def set_alpha(self, alpha: float):
        self.alpha = max(0.01, min(1.0, alpha))


def apply_deadzone(value: float, deadzone: float) -> float:
    """
    Applies deadzone to a normalized value [-1.0, 1.0] or [0.0, 1.0].
    Smoothly interpolates beyond deadzone to avoid jump.
    """
    if deadzone <= 0.0:
        return value
    deadzone = min(0.99, max(0.0, deadzone))

    if value >= 0:
        if value < deadzone:
            return 0.0
        return (value - deadzone) / (1.0 - deadzone)
    else:
        abs_v = abs(value)
        if abs_v < deadzone:
            return 0.0
        scaled = (abs_v - deadzone) / (1.0 - deadzone)
        return -scaled


def apply_response_curve(value: float, curve_type: str = "linear", exponent: float = 1.5) -> float:
    """
    Applies a response curve (linear, exponential, s-curve).
    Maintains sign for signed inputs.
    """
    if curve_type == "linear" or exponent == 1.0:
        return value

    sign = 1.0 if value >= 0 else -1.0
    abs_v = abs(value)

    if curve_type == "exponential":
        scaled = math.pow(abs_v, exponent)
        return sign * scaled
    elif curve_type == "s-curve":
        # Smooth hermite interpolation
        scaled = abs_v * abs_v * (3.0 - 2.0 * abs_v)
        return sign * scaled

    return value

