import unittest

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from shet_shet.preview import CameraPreview
from shet_shet.landmarks import FACE_DOTS
from shet_shet.tracking import FaceShape, FaceTrack


class CameraPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_landmark_mapping_uses_letterboxed_image_rect(self):
        preview = CameraPreview()
        preview.resize(800, 800)
        image = QImage(640, 480, QImage.Format.Format_RGB32)
        image.fill(0)
        preview.set_frame(
            image, (), effect_enabled=True, style="dots", color="#68F7D5", thickness=3
        )
        rect = preview.image_rect()
        self.assertAlmostEqual(rect.width() / rect.height(), 4 / 3, places=3)
        center = preview.map_landmark((0.5, 0.5))
        self.assertAlmostEqual(center.x(), 400, places=1)
        self.assertAlmostEqual(center.y(), 400, places=1)
        self.assertGreater(rect.top(), 1)

    def test_landmark_mapping_stays_centered_after_aspect_change(self):
        preview = CameraPreview()
        preview.resize(1000, 600)
        image = QImage(640, 480, QImage.Format.Format_RGB32)
        image.fill(0)
        preview.set_frame(
            image, (), effect_enabled=True, style="dots", color="#68F7D5", thickness=3
        )
        center = preview.map_landmark((0.5, 0.5))
        self.assertAlmostEqual(center.x(), 500, places=1)
        self.assertAlmostEqual(center.y(), 300, places=1)

    def test_widescreen_camera_frame_is_letterboxed_without_coordinate_drift(self):
        preview = CameraPreview()
        preview.resize(800, 800)
        image = QImage(1280, 720, QImage.Format.Format_RGB32)
        image.fill(0)
        preview.set_frame(
            image, (), effect_enabled=True, style="dots", color="#68F7D5", thickness=3
        )
        rect = preview.image_rect()
        center = preview.map_landmark((0.5, 0.5))
        self.assertAlmostEqual(rect.width() / rect.height(), 16 / 9, places=3)
        self.assertAlmostEqual(center.x(), 400, places=1)
        self.assertAlmostEqual(center.y(), 400, places=1)

    def test_dot_overlay_paints_over_the_live_frame(self):
        preview = CameraPreview()
        preview.resize(640, 480)
        image = QImage(640, 480, QImage.Format.Format_RGB32)
        image.fill(0)
        points = tuple(((index % 32) / 32, (index % 24) / 24) for index in range(478))
        track = FaceTrack(1, FaceShape(points))
        preview.set_frame(
            image, (track,), effect_enabled=True, style="dots", color="#68F7D5", thickness=3
        )
        preview.show()
        self.app.processEvents()
        canvas = QImage(640, 480, QImage.Format.Format_ARGB32)
        canvas.fill(0)
        preview.render(canvas)
        self.assertFalse(canvas.isNull())
        landmark_index = next(index for index in FACE_DOTS if 0.12 < points[index][0] < 0.88
                              and 0.12 < points[index][1] < 0.88)
        landmark = points[landmark_index]
        pixel = canvas.pixelColor(preview.map_landmark(landmark).toPoint())
        self.assertGreater(max(pixel.red(), pixel.green(), pixel.blue()), 100)
        preview.close()


if __name__ == "__main__":
    unittest.main()
