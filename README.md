# SHET SHET NAKITA AKO

A small Windows desktop camera app that draws a smoothed facial contour around faces visible to your webcam. Camera frames and face landmarks are processed on this PC. The app does not identify people, record video, save snapshots, or send frames to a server.

## Requirements

- Windows 11, 64-bit.
- Python 3.12 (64-bit CPython recommended; required by the pinned MediaPipe wheel).
- A webcam that Windows can access.
- Internet access for installing dependencies and the one-time MediaPipe task model download.

## Install it safely

Open this folder in VS Code or PowerShell, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\download_model.py
```

The model script downloads the MediaPipe Face Landmarker task file from Google's official MediaPipe model storage into `models/face_landmarker.task`. It runs only when you call it. The model is not silently fetched at application startup.

## Run

```powershell
.\.venv\Scripts\python.exe -m shet_shet.main
```

Or double-click `run.bat` after setup.

At startup the app scans camera indexes 0 through 7. Choose a camera and press **Start camera**. Use **Refresh** after plugging in a device. Choose a contour colour, line width, smoothing, mirroring, or turn the contour effect off from the right-hand controls. Preferences are stored with Windows QSettings; camera frames and landmarks are not saved.

## What “auto-tracking” means here

The app detects face landmarks in the live camera frame and draws a smoothed outline around each detected face. The tracker follows face shapes between frames; it does not identify a person, assign a name, or build an identity profile. Detection and drawing happen locally while the camera is running. No video recording or snapshot feature is provided.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests exercise synthetic face-track behavior and worker processing/cleanup using a fake camera. They do not prove physical webcam access, OS privacy behavior, or real-world face tracking quality.

## Troubleshooting

- **No camera detected:** connect or enable a webcam, press Refresh, and check Windows Settings → Privacy & security → Camera. Close apps that may already hold the camera.
- **Camera opens then stops:** reconnect it and retry. The app logs diagnostics under `%LOCALAPPDATA%\ShetShetNakitaAko\logs\app.log` without recording camera frames.
- **Missing model:** run the model download command above. The app will show this exact setup action rather than fetching files automatically.
- **Dependency install fails:** use 64-bit Python 3.12, recreate `.venv`, and reinstall with the command above. The pinned MediaPipe Tasks API is used for the landmark contour.
- **Camera is busy:** close conferencing or camera apps and restart this app.

## Project structure

- `shet_shet/main.py` — application entry point and diagnostics.
- `shet_shet/ui.py` — desktop interface and user controls.
- `shet_shet/camera.py` — camera scanning/capture, worker lifecycle, frame display and contour rendering.
- `shet_shet/vision.py` — MediaPipe Face Landmarker integration and face-oval points.
- `shet_shet/tracking.py` — dependency-free multi-face association and smoothing.
- `scripts/download_model.py` — explicit model downloader.
- `tests/` — automated tracking logic tests.
- `context/` and `AGENTS.md` — project continuity and coding instructions.

## Current verification limits

The Codex build environment used to create this project did not enumerate a physical camera. Automated tracking tests and import/syntax checks can be run here; end-to-end camera operation and Windows privacy behavior still need a webcam-equipped manual run. Frame rate depends on the webcam, CPU and lighting; the UI reports the measured processing rate during use.
