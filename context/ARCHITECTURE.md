# Architecture Record

## Evidence status at bootstrap

The original keeper records incorrectly described this workspace as keeper-only. That statement is superseded: source inspection confirms a Python Windows desktop camera application in `shet_shet/`, plus `scripts/download_model.py`, `tests/`, and pinned dependencies in `requirements.txt`. The corrected repository audit is `docs/REPOSITORY_AUDIT.md`.

## Current implementation facts

- **UI/runtime:** Python 3.12 with PySide6 Essentials; entry point `shet_shet/main.py` creates a QApplication and `MainWindow`.
- **UI state:** `shet_shet/ui.py` holds camera selection, status, preview, options and QSettings preferences. Camera discovery runs in `CameraScanner`; capture runs in `CameraWorker`.
- **Capture/vision flow:** OpenCV opens the selected camera and reads frames on the worker thread. Frames are converted BGR→RGB, optionally mirrored, passed to `FaceLandmarker` (`shet_shet/vision.py`), smoothed by `FaceTracker` (`tracking.py`), drawn, then copied into a latest-frame QImage for UI polling.
- **Model:** Google MediaPipe Face Landmarker task file is explicitly downloaded by `scripts/download_model.py`, with pinned SHA-256 verification. Runtime expects `models/face_landmarker.task` and does not download automatically.
- **Dependencies:** MediaPipe 0.10.21, OpenCV contrib 4.11.0.86, PySide6 Essentials 6.12.0, NumPy <2 in `requirements.txt`.
- **Persistence:** Only control preferences use QSettings. No application database, account system, server, cloud provider, frame recording, or snapshot persistence was found.
- **Diagnostics:** `shet_shet/main.py` writes application logs below `%LOCALAPPDATA%\ShetShetNakitaAko\logs` where possible. Source inspection shows no frame data written to logs.
- **Tests:** `tests/test_tracking.py` covers synthetic matching, smoothing, multiple tracks, expiration, and empty-shape rejection. `tests/test_camera.py` uses fakes to check one-frame processing, face count, stop cleanup, and camera-open failure cleanup. These do not validate a physical camera or real-face inference accuracy.

## Trust and resource boundaries

The desktop process handles camera frames locally. The OS and camera driver are outside the app boundary. The explicitly invoked model downloader connects to the pinned Google Storage URL over HTTPS and rejects oversized, undersized, or hash-mismatched files before replacement. Camera/model resources are released in the worker's `finally` block; actual driver behavior remains unverified without a physical camera.

## Guardrails

1. Do not add frame/network transmission, recording, identity recognition, telemetry, accounts, or cloud services without an explicit user scope change and privacy review.
2. Keep model acquisition explicit and checksum-pinned.
3. Avoid unnecessary persistence: preferences only unless a new requirement is approved.
4. Distinguish synthetic and headless checks from actual webcam operation.

## Unverified behavior

No physical camera was detected in the current environment. Camera scanning, permission denials, capture loss, face visibility/lighting performance, repeated device changes, and native Windows UX still require a webcam-equipped Windows 11 manual run.
