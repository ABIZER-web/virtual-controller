"""Camera manager for webcam enumeration, threaded capture, and resolution selection."""
import cv2
import time
from typing import List, Dict, Optional, Any
from PySide6.QtCore import QObject, Signal, QThread
from utils.logger import logger

class CameraWorker(QThread):
    frame_ready = Signal(object)  # np.ndarray BGR
    status_changed = Signal(bool, str)

    def __init__(self, device_index: int = 0, width: int = 640, height: int = 480, target_fps: int = 30):
        super().__init__()
        self.device_index = device_index
        self.width = width
        self.height = height
        self.target_fps = target_fps
        self._running = False
        self.cap: Optional[cv2.VideoCapture] = None

    def run(self):
        self._running = True
        logger.info("Starting camera worker for device %d (%dx%d @ %d fps)", self.device_index, self.width, self.height, self.target_fps)

        # On Windows, try cv2.CAP_DSHOW first
        self.cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
        if not self.cap or not self.cap.isOpened():
            logger.info("CAP_DSHOW failed, falling back to default backend...")
            self.cap = cv2.VideoCapture(self.device_index)

        if not self.cap or not self.cap.isOpened():
            logger.error("Could not open camera device %d", self.device_index)
            self.status_changed.emit(False, f"Failed to open camera device {self.device_index}")
            self._running = False
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        # Warm up camera
        for _ in range(3):
            self.cap.read()
            time.sleep(0.02)

        self.status_changed.emit(True, f"Camera {self.device_index} Active")

        interval = 1.0 / max(1, self.target_fps)
        while self._running:
            t0 = time.time()
            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            self.frame_ready.emit(frame)

            elapsed = time.time() - t0
            sleep_time = interval - elapsed
            if sleep_time > 0.001:
                time.sleep(sleep_time)

        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info("Camera worker stopped.")

    def stop(self):
        self._running = False
        self.wait(1500)


class CameraManager(QObject):
    """Centralized manager for webcam lifecycle and global frame dispatching."""
    frame_ready = Signal(object)
    status_changed = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.worker: Optional[CameraWorker] = None
        self.current_device_index: int = 0
        self.current_width: int = 640
        self.current_height: int = 480
        self.current_fps: int = 30

    def detect_available_cameras(self, max_probe: int = 4) -> List[Dict[str, Any]]:
        """Probes camera indices to find active cameras."""
        # Temporarily stop active camera to release lock for probing
        was_running = self.is_running()
        if was_running:
            self.stop_camera()

        available = []
        for i in range(max_probe):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    available.append({
                        "index": i,
                        "name": f"Camera {i} ({w}x{h})",
                        "width": w,
                        "height": h
                    })
                cap.release()

        if not available:
            available.append({
                "index": 0,
                "name": "Default Webcam (Camera 0)",
                "width": 640,
                "height": 480
            })

        if was_running:
            self.start_camera(self.current_device_index, self.current_width, self.current_height, self.current_fps)

        return available

    def start_camera(self, device_index: int = 0, width: int = 640, height: int = 480, fps: int = 30):
        self.current_device_index = device_index
        self.current_width = width
        self.current_height = height
        self.current_fps = fps

        self.stop_camera()

        self.worker = CameraWorker(device_index=device_index, width=width, height=height, target_fps=fps)
        self.worker.frame_ready.connect(self._on_worker_frame)
        self.worker.status_changed.connect(self._on_worker_status)
        self.worker.start()

    def _on_worker_frame(self, frame):
        self.frame_ready.emit(frame)

    def _on_worker_status(self, is_active: bool, msg: str):
        self.status_changed.emit(is_active, msg)

    def is_running(self) -> bool:
        return self.worker is not None and self.worker.isRunning()

    def stop_camera(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker = None

camera_manager = CameraManager()
