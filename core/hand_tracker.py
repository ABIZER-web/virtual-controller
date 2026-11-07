"""Hand tracking using MediaPipe Hand Landmarker."""
import os
import time
import math
from typing import Optional, Tuple, List, Dict, Any
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from utils.logger import logger

class HandTracker:
    def __init__(self, model_path: str = "assets/models/hand_landmarker.task"):
        self.model_path = model_path
        self.landmarker = None
        self._init_detector()

        # Cached outputs
        self.left_hand_landmarks: Optional[List[Any]] = None
        self.right_hand_landmarks: Optional[List[Any]] = None
        self.left_wrist: Optional[Tuple[float, float]] = None
        self.right_wrist: Optional[Tuple[float, float]] = None
        self.left_confidence: float = 0.0
        self.right_confidence: float = 0.0

    def _init_detector(self):
        if not os.path.exists(self.model_path):
            logger.error("MediaPipe model file not found at: %s", self.model_path)
            return

        base_options = mp_python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        try:
            self.landmarker = vision.HandLandmarker.create_from_options(options)
            logger.info("MediaPipe HandLandmarker initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize MediaPipe HandLandmarker: %s", e)

    def process_frame(
        self,
        frame_bgr: np.ndarray,
        mirror: bool = True,
        accelerator_hand: str = "Right",
        brake_hand: str = "Left",
        steering_angle: float = 0.0
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Processes a BGR image frame.
        Returns (annotated_frame_bgr, detection_info)
        """
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None
        self.left_wrist = None
        self.right_wrist = None
        self.left_confidence = 0.0
        self.right_confidence = 0.0

        if frame_bgr is None or self.landmarker is None:
            return frame_bgr, self._get_status_dict()

        h, w, _ = frame_bgr.shape
        display_frame = frame_bgr.copy()
        if mirror:
            display_frame = cv2.flip(display_frame, 1)

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        try:
            results = self.landmarker.detect(mp_image)
        except Exception as e:
            logger.error("Error during hand detection: %s", e)
            return display_frame, self._get_status_dict()

        if results.hand_landmarks:
            detected_hands = []
            for idx, landmarks in enumerate(results.hand_landmarks):
                score = 0.95
                label = ""
                if results.handedness and idx < len(results.handedness):
                    top_hand = results.handedness[idx][0]
                    score = top_hand.score
                    label = top_hand.category_name  # 'Left' or 'Right'
                detected_hands.append({
                    "landmarks": landmarks,
                    "score": score,
                    "label": label,
                    "wrist_x": landmarks[0].x,
                    "wrist_y": landmarks[0].y
                })

            # Identify Left vs Right Hand
            # When mirrored, the user's physical left hand appears on the left half (smaller x)
            # and right hand appears on the right half (larger x).
            if len(detected_hands) == 1:
                hand = detected_hands[0]
                # If on left half of screen, mark as Left, else Right
                if hand["wrist_x"] < 0.5:
                    self.left_hand_landmarks = hand["landmarks"]
                    self.left_wrist = (hand["wrist_x"], hand["wrist_y"])
                    self.left_confidence = hand["score"]
                else:
                    self.right_hand_landmarks = hand["landmarks"]
                    self.right_wrist = (hand["wrist_x"], hand["wrist_y"])
                    self.right_confidence = hand["score"]
            elif len(detected_hands) >= 2:
                # Sort by x coordinate
                detected_hands.sort(key=lambda h_dict: h_dict["wrist_x"])
                left_candidate = detected_hands[0]
                right_candidate = detected_hands[1]

                self.left_hand_landmarks = left_candidate["landmarks"]
                self.left_wrist = (left_candidate["wrist_x"], left_candidate["wrist_y"])
                self.left_confidence = left_candidate["score"]

                self.right_hand_landmarks = right_candidate["landmarks"]
                self.right_wrist = (right_candidate["wrist_x"], right_candidate["wrist_y"])
                self.right_confidence = right_candidate["score"]

        # Draw overlays on display_frame
        self._draw_overlay(
            display_frame,
            w,
            h,
            accelerator_hand,
            brake_hand,
            steering_angle
        )

        return display_frame, self._get_status_dict()

    def _draw_overlay(
        self,
        frame: np.ndarray,
        w: int,
        h: int,
        accel_hand: str,
        brake_hand: str,
        steering_angle: float
    ):
        connections = vision.HandLandmarksConnections.HAND_CONNECTIONS

        # Helper to draw single hand
        def draw_single_hand(landmarks, role_label: str, role_color: Tuple[int, int, int]):
            # Draw bones
            for conn in connections:
                pt1 = landmarks[conn.start]
                pt2 = landmarks[conn.end]
                p1 = (int(pt1.x * w), int(pt1.y * h))
                p2 = (int(pt2.x * w), int(pt2.y * h))
                cv2.line(frame, p1, p2, (230, 230, 230), 2, cv2.LINE_AA)

            # Draw joints
            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (40, 40, 240), -1, cv2.LINE_AA)
                cv2.circle(frame, (cx, cy), 2, (255, 255, 255), -1, cv2.LINE_AA)

            # Label role above hand
            wrist = landmarks[0]
            wx, wy = int(wrist.x * w), int(wrist.y * h)
            # Find topmost point
            min_y = min([lm.y for lm in landmarks])
            tx = int(landmarks[12].x * w)
            ty = max(25, int(min_y * h) - 15)

            cv2.putText(
                frame,
                role_label,
                (tx - 35, ty),
                cv2.FONT_HERSHEY_DUPLEX,
                0.7,
                role_color,
                2,
                cv2.LINE_AA
            )

        # Draw Left hand
        if self.left_hand_landmarks:
            is_acc = (accel_hand == "Left")
            role = "ACCELERATOR" if is_acc else "BRAKE"
            color = (50, 220, 50) if is_acc else (50, 50, 230)
            draw_single_hand(self.left_hand_landmarks, role, color)

        # Draw Right hand
        if self.right_hand_landmarks:
            is_acc = (accel_hand == "Right")
            role = "ACCELERATOR" if is_acc else "BRAKE"
            color = (50, 220, 50) if is_acc else (50, 50, 230)
            draw_single_hand(self.right_hand_landmarks, role, color)

        # Draw imaginary steering wheel connector between wrists
        if self.left_wrist and self.right_wrist:
            pt_left = (int(self.left_wrist[0] * w), int(self.left_wrist[1] * h))
            pt_right = (int(self.right_wrist[0] * w), int(self.right_wrist[1] * h))

            # Glowing steering bar
            cv2.line(frame, pt_left, pt_right, (0, 255, 100), 4, cv2.LINE_AA)
            cv2.circle(frame, pt_left, 7, (0, 255, 0), -1, cv2.LINE_AA)
            cv2.circle(frame, pt_right, 7, (0, 255, 0), -1, cv2.LINE_AA)

            # Center hub point
            mid_x = int((pt_left[0] + pt_right[0]) / 2)
            mid_y = int((pt_left[1] + pt_right[1]) / 2)
            cv2.circle(frame, (mid_x, mid_y), 5, (255, 200, 0), -1, cv2.LINE_AA)

            # Top angle display banner
            angle_text = f"{int(steering_angle):+d} deg"
            cv2.putText(
                frame,
                angle_text,
                (30, 45),
                cv2.FONT_HERSHEY_DUPLEX,
                0.9,
                (255, 140, 20),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                frame,
                "Virtual Steering Wheel",
                (w - 280, 45),
                cv2.FONT_HERSHEY_DUPLEX,
                0.65,
                (255, 200, 50),
                1,
                cv2.LINE_AA
            )

    def _get_status_dict(self) -> Dict[str, Any]:
        return {
            "left_detected": self.left_hand_landmarks is not None,
            "right_detected": self.right_hand_landmarks is not None,
            "both_detected": (self.left_hand_landmarks is not None) and (self.right_hand_landmarks is not None),
            "left_wrist": self.left_wrist,
            "right_wrist": self.right_wrist,
            "left_confidence": self.left_confidence,
            "right_confidence": self.right_confidence,
            "left_landmarks": self.left_hand_landmarks,
            "right_landmarks": self.right_hand_landmarks
        }

