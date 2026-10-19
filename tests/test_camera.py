import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QCoreApplication

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


class CameraWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

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
            image, face_count, fps = latest
            self.assertFalse(image.isNull())
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


if __name__ == "__main__":
    unittest.main()
