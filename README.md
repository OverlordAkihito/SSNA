# SHET SHET NAKITA AKO

A small Windows desktop camera app that overlays luminous facial landmark dots around faces visible to your webcam. Camera frames and face landmarks are processed on this PC. The app does not identify people, record video, save snapshots, or send frames to a server.

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

At startup the app scans camera indexes 0 through 7. Choose a camera and press **Start camera**. Use **Refresh** after plugging in a device. Choose the luminous landmark-dot filter or the existing face-contour filter, adjust contour colour and thickness, change tracking smoothing, toggle mirroring, or turn the effect off. Preferences are stored with Windows QSettings; camera frames and landmarks are not saved.

The dot filter uses MediaPipe's detected face-mesh landmarks for the face outline, eyebrows, eyelids/eyes, irises, nose and lips. White dots sit on individual landmarks; a soft magenta halo accents the eye regions. The landmarks are painted on a transparent layer over the preview and use the same aspect-fit frame rectangle, so letterboxing and window resizing do not shift the overlay. The selected mirror option is applied to the frame before detection and display.

## What “auto-tracking” means here

The app detects face landmarks in the live camera frame and draws smoothed dots or a face outline around each detected face. The tracker follows face shapes between frames; a briefly lost face fades out and can recover on reacquisition. It does not identify a person, assign a name, or build an identity profile. Detection and drawing happen locally while the camera is running. No video recording or snapshot feature is provided.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests exercise synthetic face-track behavior, fake-camera worker processing/cleanup, overlay painting, and preview coordinate mapping across aspect ratios. They do not prove physical webcam access, OS privacy behavior, or real-world face tracking quality.

## Troubleshooting

- **No camera detected:** connect or enable a webcam, press Refresh, and check Windows Settings → Privacy & security → Camera. Close apps that may already hold the camera.
- **Camera opens then stops:** reconnect it and retry. The app logs diagnostics under `%LOCALAPPDATA%\ShetShetNakitaAko\logs\app.log` without recording camera frames.
- **Missing model:** run the model download command above. The app will show this exact setup action rather than fetching files automatically.
- **Dependency install fails:** use 64-bit Python 3.12, recreate `.venv`, and reinstall with the command above. The pinned MediaPipe Tasks API is used for the landmark contour.
- **Camera is busy:** close conferencing or camera apps and restart this app.

## Project structure

- `shet_shet/main.py` — application entry point and diagnostics.
- `shet_shet/ui.py` — desktop interface and user controls.
- `shet_shet/preview.py` — aspect-fit camera preview and transparent landmark-dot/contour painter.
- `shet_shet/landmarks.py` — MediaPipe facial region landmark index groups.
- `shet_shet/camera.py` — camera scanning/capture, worker lifecycle, frame display and contour rendering.
- `shet_shet/vision.py` — MediaPipe Face Landmarker integration and normalized full-face coordinates.
- `shet_shet/tracking.py` — dependency-free multi-face association and smoothing.
- `scripts/download_model.py` — explicit model downloader.
- `tests/` — automated tracking logic tests.
- `context/` and `AGENTS.md` — project continuity and coding instructions.

## Current verification limits

The Codex build environment used to create this project did not enumerate a physical camera. Automated tracking tests and import/syntax checks can be run here; end-to-end camera operation and Windows privacy behavior still need a webcam-equipped manual run. Frame rate depends on the webcam, CPU and lighting; the UI reports the measured processing rate during use.
