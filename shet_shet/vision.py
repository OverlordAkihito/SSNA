"""MediaPipe Face Landmarker adapter and face-oval extraction."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import gettempdir
from typing import Any

import numpy as np

from .tracking import FaceShape

# MediaPipe's standard face-mesh oval path, clockwise around forehead and chin.
FACE_OVAL = (
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365,
    379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93,
    234, 127, 162, 21, 54, 103, 67, 109,
)


class FaceLandmarker:
    def __init__(self, model_path: Path, max_faces: int = 4) -> None:
        if not model_path.is_file():
            raise FileNotFoundError(
                f"Face model not found at {model_path}. Run: "
                "python scripts/download_model.py"
            )
        # MediaPipe 0.10 imports its legacy drawing module (and matplotlib) at
        # package import. Keep that cache inside this app's local user folder.
        mpl_config = Path(gettempdir()) / "ShetShetNakitaAko" / "matplotlib"
        mpl_config.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))
        import mediapipe as mp

        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=max_faces,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._mp = mp
        self._task: Any = mp.tasks.vision.FaceLandmarker.create_from_options(options)
        self._last_timestamp = -1

    def detect(self, rgb_frame: np.ndarray, timestamp_ms: int) -> list[FaceShape]:
        timestamp_ms = max(timestamp_ms, self._last_timestamp + 1)
        self._last_timestamp = timestamp_ms
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb_frame)
        result = self._task.detect_for_video(image, timestamp_ms)
        shapes: list[FaceShape] = []
        for landmarks in result.face_landmarks:
            if len(landmarks) <= max(FACE_OVAL):
                continue
            points = tuple(
                (min(1.0, max(0.0, float(landmarks[i].x))),
                 min(1.0, max(0.0, float(landmarks[i].y))))
                for i in FACE_OVAL
            )
            shapes.append(FaceShape(points))
        return shapes

    def close(self) -> None:
        self._task.close()
