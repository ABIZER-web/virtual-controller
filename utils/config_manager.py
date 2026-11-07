"""Configuration manager for loading and saving settings in config.json."""
import json
import os
import copy
from typing import Any, Dict
from utils.logger import logger

DEFAULT_CONFIG: Dict[str, Any] = {
    "setup_completed": False,
    "camera": {
        "device_index": 0,
        "width": 640,
        "height": 480,
        "fps": 30,
        "mirror": True
    },
    "hand_tracking": {
        "min_detection_confidence": 0.65,
        "min_tracking_confidence": 0.65
    },
    "hand_assignment": {
        "accelerator_hand": "Right",
        "brake_hand": "Left"
    },
    "steering": {
        "neutral_angle": 0.0,
        "calibrated_left_max": -45.0,
        "calibrated_right_max": 45.0,
        "max_rotation_degrees": 180.0,
        "sensitivity": 50.0,
        "deadzone": 2.0,
        "smoothing": 0.35,
        "centering_enabled": True,
        "centering_speed": 0.15,
        "response_curve": "linear"
    },
    "pedals": {
        "accelerator": {
            "relaxed_val": 0.40,
            "pressed_val": 0.12,
            "deadzone": 5.0,
            "sensitivity": 50.0,
            "smoothing": 0.30,
            "response_curve": "linear"
        },
        "brake": {
            "relaxed_val": 0.40,
            "pressed_val": 0.12,
            "deadzone": 5.0,
            "sensitivity": 50.0,
            "smoothing": 0.30,
            "response_curve": "linear"
        }
    },
    "safety": {
        "grace_period_ms": 400,
        "emergency_release": True
    },
    "controller": {
        "enabled": True,
        "type": "xbox360"
    }
}

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config: Dict[str, Any] = copy.deepcopy(DEFAULT_CONFIG)
        self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_cfg = json.load(f)
                    self._merge_dicts(self._config, user_cfg)
                    logger.info("Configuration loaded successfully from %s", self.config_path)
            except Exception as e:
                logger.error("Failed to load config from %s: %s. Using defaults.", self.config_path, e)
        else:
            logger.info("No existing config file found. Using defaults.")
            self.save()
        return self._config

    def save(self) -> bool:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
            logger.info("Configuration saved to %s", self.config_path)
            return True
        except Exception as e:
            logger.error("Failed to save config to %s: %s", self.config_path, e)
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split(".")
        curr = self._config
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return default
        return curr

    def set(self, key_path: str, value: Any) -> None:
        keys = key_path.split(".")
        curr = self._config
        for k in keys[:-1]:
            if k not in curr or not isinstance(curr[k], dict):
                curr[k] = {}
            curr = curr[k]
        curr[keys[-1]] = value

    def reset_defaults(self) -> None:
        self._config = copy.deepcopy(DEFAULT_CONFIG)
        self.save()

    def _merge_dicts(self, base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        for k, v in updates.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._merge_dicts(base[k], v)
            else:
                base[k] = v

config_manager = ConfigManager()

