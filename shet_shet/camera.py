"""Camera enumeration and a stoppable Qt worker for local video processing."""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from .tracking import FaceTracker
from .vision import FaceLandmarker

logger = logging.getLogger(__name__)


def open_camera(index: int) -> cv2.VideoCapture:
    backends = (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY)
    for backend in backends:
        camera = cv2.VideoCapture(index, backend)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return camera
        camera.release()
    return cv2.VideoCapture()


class CameraScanner(QThread):
    scan_complete = Signal(list)
    scan_error = Signal(str)

    def run(self) -> None:
        found: list[tuple[int, str]] = []
        try:
            for index in range(8):
                camera = open_camera(index)
                try:
                    if camera.isOpened():
                        ok, frame = camera.read()
                        if ok and frame is not None and frame.size:
                            found.append((index, f"Camera {index + 1}"))
                finally:
                    camera.release()
        except Exception as exc:
            logger.exception("Camera discovery failed")
            self.scan_error.emit(str(exc))
        self.scan_complete.emit(found)


class CameraWorker(QThread):
    status = Signal(str)
    failed = Signal(str)

    def __init__(self, camera_index: int, model_path: Path, options: dict[str, object]):
        super().__init__()
        self.camera_index = camera_index
        self.model_path = model_path
        self._options = dict(options)
        self._options_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._frame_lock = threading.Lock()
        self._latest: tuple[QImage, int, float] | None = None

    def latest_frame(self) -> tuple[QImage, int, float] | None:
        with self._frame_lock:
            return self._latest

    def set_options(self, options: dict[str, object]) -> None:
        with self._options_lock:
            self._options = dict(options)

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        camera = None
        landmarker = None
        tracker = FaceTracker()
        try:
            self.status.emit("Opening camera and loading face model…")
            camera = open_camera(self.camera_index)
            if not camera.isOpened():
                raise RuntimeError(
                    "Windows could not open this camera. Check Camera privacy settings "
                    "and close apps that may already be using it."
                )
            landmarker = FaceLandmarker(self.model_path)
            self.status.emit("Camera live · face tracking ready")
            started = time.perf_counter()
            frame_count = 0
            while not self._stop_event.is_set():
                ok, frame = camera.read()
                if not ok or frame is None or frame.size == 0:
                    if self._stop_event.is_set():
                        break
                    raise RuntimeError("The camera stopped returning frames. Reconnect it and try again.")

                with self._options_lock:
                    options = dict(self._options)
                if bool(options.get("mirror", True)):
                    frame = cv2.flip(frame, 1)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp_ms = int((time.perf_counter() - started) * 1000)
                try:
                    detections = landmarker.detect(rgb, timestamp_ms)
                except Exception:
                    logger.exception("Face landmark inference failed for one frame")
                    detections = []
                tracks = tracker.update(detections, float(options.get("smoothing", 0.35)))
                if bool(options.get("effect", True)):
                    self._draw_contours(rgb, tracks, str(options.get("color", "#68F7D5")), int(options.get("thickness", 3)))

                frame_count += 1
                now = time.perf_counter()
                fps = frame_count / max(0.001, now - started)
                h, w, _ = rgb.shape
                image = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()
                with self._frame_lock:
                    self._latest = (image, sum(track.misses == 0 for track in tracks), fps)
        except Exception as exc:
            logger.exception("Camera worker stopped")
            self.failed.emit(str(exc))
        finally:
            if landmarker is not None:
                try:
                    landmarker.close()
                except Exception:
                    logger.exception("Failed to close face landmarker")
            if camera is not None:
                camera.release()
            self.status.emit("Camera stopped")

    @staticmethod
    def _draw_contours(rgb, tracks, color_hex: str, thickness: int) -> None:
        color_hex = color_hex.lstrip("#")
        try:
            color = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            color = (104, 247, 213)
        points_by_track = []
        height, width = rgb.shape[:2]
        for track in tracks:
            points = [[round(x * (width - 1)), round(y * (height - 1))] for x, y in track.shape.points]
            if len(points) >= 3:
                points_by_track.append(np.array(points, dtype="int32").reshape((-1, 1, 2)))
        line_width = max(1, min(12, thickness))
        if not points_by_track:
            return
        glow = rgb.copy()
        cv2.polylines(glow, points_by_track, True, color, line_width + 5, cv2.LINE_AA)
        glow = cv2.GaussianBlur(glow, (0, 0), 5)
        cv2.addWeighted(glow, 0.23, rgb, 0.77, 0, dst=rgb)
        cv2.polylines(rgb, points_by_track, True, color, line_width, cv2.LINE_AA)
