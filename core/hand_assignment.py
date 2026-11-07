"""Hand assignment manager for pedals (Accelerator & Brake)."""
from typing import Tuple
from utils.logger import logger

class HandAssignment:
    def __init__(self, accelerator_hand: str = "Right", brake_hand: str = "Left"):
        self.accelerator_hand = "Right"
        self.brake_hand = "Left"
        self.set_assignment(accelerator_hand, brake_hand)

    def set_assignment(self, accelerator_hand: str, brake_hand: str) -> bool:
        acc = accelerator_hand.capitalize()
        brk = brake_hand.capitalize()

        if acc not in ("Left", "Right") or brk not in ("Left", "Right"):
            logger.error("Invalid hand assignment: Acc=%s, Brk=%s", accelerator_hand, brake_hand)
            return False

        if acc == brk:
            logger.warning("Accelerator and Brake cannot be assigned to the same hand (%s)", acc)
            return False

        self.accelerator_hand = acc
        self.brake_hand = brk
        logger.info("Hand assignment updated: Accelerator=%s, Brake=%s", self.accelerator_hand, self.brake_hand)
        return True

    def set_accelerator_hand(self, hand: str) -> bool:
        hand = hand.capitalize()
        if hand not in ("Left", "Right"):
            return False
        # Swap other hand automatically or return False
        other = "Left" if hand == "Right" else "Right"
        return self.set_assignment(hand, other)

    def set_brake_hand(self, hand: str) -> bool:
        hand = hand.capitalize()
        if hand not in ("Left", "Right"):
            return False
        other = "Left" if hand == "Right" else "Right"
        return self.set_assignment(other, hand)

    def get_assignment(self) -> Tuple[str, str]:
        return self.accelerator_hand, self.brake_hand

