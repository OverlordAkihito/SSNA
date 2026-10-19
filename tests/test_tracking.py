import unittest

from shet_shet.tracking import FaceShape, FaceTracker


def oval(cx: float, cy: float = 0.5, radius: float = 0.1) -> FaceShape:
    return FaceShape(((cx - radius, cy - radius), (cx + radius, cy - radius),
                      (cx + radius, cy + radius), (cx - radius, cy + radius)))


class FaceTrackerTests(unittest.TestCase):
    def test_track_id_survives_motion(self):
        tracker = FaceTracker()
        first = tracker.update([oval(0.3)], smoothing=1.0)[0]
        moved = tracker.update([oval(0.34)], smoothing=1.0)[0]
        self.assertEqual(first.track_id, moved.track_id)
        self.assertAlmostEqual(moved.shape.center[0], 0.34)

    def test_smoothing_reduces_single_frame_jump(self):
        tracker = FaceTracker()
        tracker.update([oval(0.3)], smoothing=0.25)
        moved = tracker.update([oval(0.5)], smoothing=0.25)[0]
        self.assertAlmostEqual(moved.shape.center[0], 0.35)

    def test_multiple_faces_keep_distinct_ids(self):
        tracker = FaceTracker()
        original = tracker.update([oval(0.2), oval(0.8)], smoothing=1.0)
        updated = tracker.update([oval(0.79), oval(0.21)], smoothing=1.0)
        by_x = {round(track.shape.center[0], 1): track.track_id for track in updated}
        self.assertEqual(by_x[0.2], original[0].track_id)
        self.assertEqual(by_x[0.8], original[1].track_id)

    def test_track_expires_after_brief_detection_loss(self):
        tracker = FaceTracker(max_missed_frames=2)
        tracker.update([oval(0.4)])
        self.assertEqual(len(tracker.update([])), 1)
        self.assertEqual(len(tracker.update([])), 1)
        self.assertEqual(len(tracker.update([])), 0)

    def test_invalid_empty_shapes_are_ignored(self):
        tracker = FaceTracker()
        self.assertEqual(tracker.update([FaceShape(())]), ())


if __name__ == "__main__":
    unittest.main()
