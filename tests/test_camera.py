import os
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication

from shet_shet.camera import CameraWorker
from shet_shet.tracking import FaceShape


class FakeCamera:
    def __init__(self, opened=True, block_after_first=False):
        self.opened = opened
        self.block_after_first = block_after_first
        self.read_count = 0
        self.second_read = threading.Event()
        self.allow_end = threading.Event()
        self.released = False

    def isOpened(self):
        return self.opened

    def set(self, *_args):
        return True

    def read(self):
        self.read_count += 1
        if self.read_count == 1:
            return True, np.zeros((64, 64, 3), dtype=np.uint8)
        self.second_read.set()
        if self.block_after_first:
            self.allow_end.wait(2)
        return False, None

    def release(self):
        self.released = True


class FakeLandmarker:
    def __init__(self, _path):
        self.closed = False

    def detect(self, _rgb, _timestamp):
        return [FaceShape(((0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75)))]

    def close(self):
        self.closed = True


class DetectionThenLossLandmarker(FakeLandmarker):
    def __init__(self, path):
        super().__init__(path)
        self.calls = 0

    def detect(self, _rgb, _timestamp):
        self.calls += 1
        if self.calls == 1:
            return [FaceShape(((0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75)))]
        return []


class TwoFrameCamera(FakeCamera):
    def __init__(self):
        super().__init__(block_after_first=True)
        self.allow_second = threading.Event()
        self.third_read = threading.Event()

    def read(self):
        self.read_count += 1
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        if self.read_count == 1:
            return True, frame
        if self.read_count == 2:
            self.second_read.set()
            if not self.allow_second.wait(2):
                return False, None
            return True, frame
        self.third_read.set()
        self.allow_end.wait(2)
        return False, None


class CameraWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_processes_latest_frame_and_releases_resources_when_stopped(self):
        camera = FakeCamera(block_after_first=True)
        landmarker = FakeLandmarker(Path("unused"))
        with patch("shet_shet.camera.open_camera", return_value=camera), patch(
            "shet_shet.camera.FaceLandmarker", return_value=landmarker
        ):
            worker = CameraWorker(0, Path("unused"), {"mirror": False, "effect": False})
            worker.start()
            self.assertTrue(camera.second_read.wait(2), "worker did not finish its first frame")
            latest = worker.latest_frame()
            self.assertIsNotNone(latest)
            image, tracks, face_count, fps = latest
            self.assertFalse(image.isNull())
            self.assertEqual(len(tracks), 1)
            self.assertEqual(face_count, 1)
            self.assertGreater(fps, 0)
            worker.stop()
            camera.allow_end.set()
            self.assertTrue(worker.wait(3000), "worker did not stop")

        self.assertTrue(camera.released)
        self.assertTrue(landmarker.closed)

    def test_camera_open_failure_releases_capture(self):
        camera = FakeCamera(opened=False)
        errors = []
        with patch("shet_shet.camera.open_camera", return_value=camera), patch(
            "shet_shet.camera.FaceLandmarker"
        ) as landmarker_factory:
            worker = CameraWorker(0, Path("unused"), {})
            worker.failed.connect(errors.append)
            with self.assertLogs("shet_shet.camera", level="ERROR") as captured:
                worker.start()
                self.assertTrue(worker.wait(3000), "worker did not exit after camera-open failure")
                self.app.processEvents()

        landmarker_factory.assert_not_called()
        self.assertTrue(camera.released)
        self.assertTrue(any("could not open this camera" in error.lower() for error in errors))
        self.assertIn("Camera worker stopped", captured.output[0])

    def test_published_track_snapshot_does_not_change_on_next_frame(self):
        camera = TwoFrameCamera()
        landmarker = DetectionThenLossLandmarker(Path("unused"))
        with patch("shet_shet.camera.open_camera", return_value=camera), patch(
            "shet_shet.camera.FaceLandmarker", return_value=landmarker
        ):
            worker = CameraWorker(0, Path("unused"), {"mirror": False, "effect": False})
            worker.start()
            self.assertTrue(camera.second_read.wait(2))
            first_frame = worker.latest_frame()
            self.assertIsNotNone(first_frame)
            first_tracks = first_frame[1]
            self.assertEqual(first_frame[2], 1)
            camera.allow_second.set()
            self.assertTrue(camera.third_read.wait(2))
            second_frame = worker.latest_frame()
            self.assertIsNotNone(second_frame)
            self.assertEqual(second_frame[2], 0)
            self.assertEqual(second_frame[1][0].misses, 1)
            self.assertEqual(first_tracks[0].misses, 0)
            worker.stop()
            camera.allow_end.set()
            self.assertTrue(worker.wait(3000))

        self.assertTrue(camera.released)
        self.assertTrue(landmarker.closed)


if __name__ == "__main__":
    unittest.main()
