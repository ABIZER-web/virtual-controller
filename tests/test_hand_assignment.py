"""Unit tests for hand assignment validation and swapping."""
import unittest
from core.hand_assignment import HandAssignment

class TestHandAssignment(unittest.TestCase):
    def test_default_assignment(self):
        assign = HandAssignment()
        self.assertEqual(assign.accelerator_hand, "Right")
        self.assertEqual(assign.brake_hand, "Left")

    def test_valid_swap(self):
        assign = HandAssignment()
        res = assign.set_assignment("Left", "Right")
        self.assertTrue(res)
        self.assertEqual(assign.accelerator_hand, "Left")
        self.assertEqual(assign.brake_hand, "Right")

    def test_reject_same_hand(self):
        assign = HandAssignment()
        # Must not allow both to be Right or both to be Left
        res = assign.set_assignment("Right", "Right")
        self.assertFalse(res)
        self.assertNotEqual(assign.accelerator_hand, assign.brake_hand)

        res2 = assign.set_assignment("Left", "Left")
        self.assertFalse(res2)
        self.assertNotEqual(assign.accelerator_hand, assign.brake_hand)

if __name__ == "__main__":
    unittest.main()

