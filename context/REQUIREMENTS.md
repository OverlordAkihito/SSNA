# Requirements Register

**Evidence boundary:** The rows below describe the requested camera app and current source-backed status. Statuses are based on source inspection plus the listed focused checks; they do not imply successful real-camera operation.

## Status vocabulary

Use `Verified`, `Partial`, `UI-only`, `Missing`, `Unable to verify`, `Blocked`, or `Not applicable`. Every status has evidence and material gaps.

| ID | Requirement area | Expected behavior / acceptance summary | Current status and evidence |
|---|---|---|---|
| CAM-01 | Windows desktop UI | Launch a Windows desktop window with camera preview and controls. | Partial — PySide6 UI exists in `shet_shet/ui.py`; offscreen construction smoke check passed, but no native Windows interaction review was done. |
| CAM-02 | Camera discovery and selection | Scan available cameras, select one, refresh after device changes, handle no camera and open failure. | Partial — `CameraScanner` scans indexes 0–7 and `CameraWorker` reports open/read errors in `shet_shet/camera.py`; this environment enumerated no camera, so device behavior is unverified. |
| CAM-03 | Live preview lifecycle | Start and stop camera, show live frames, release camera/model resources on stop, failure, and close. | Partial — worker tests in `tests/test_camera.py` pass with a fake camera: frame data is surfaced and camera/model resources close after stop; open failure releases capture. Real device/driver behavior is still unverified. |
| CAM-04 | Facial landmark filter | Detect multiple face landmark sets and show pearl dots across face outline, eyebrows, eyes/irises, nose, and lips with a pink eye glow; retain optional contour mode. | Partial — full MediaPipe landmark arrays are returned by `shet_shet/vision.py`; region indices in `shet_shet/landmarks.py`; `shet_shet/preview.py` paints dots/halo and contour separately from the image. Tests exercise overlay painting using synthetic coordinates; actual face alignment and visual quality require webcam validation. |
| CAM-05 | User controls and preferences | Configure mirror, effect, dot/contour mode, outline colour/thickness, and smoothing; persist preferences. | Partial — controls and QSettings persistence implemented in `shet_shet/ui.py`; offscreen geometry and painter checks pass, but interactive persistence and real-camera alignment were not manually exercised. |
| CAM-06 | Local-only processing and minimization | Do not identify, record, save or upload frames/landmarks; keep processing local and avoid telemetry. | Partial — app flow has no network/recording path and only saves UI preferences; model is acquired by explicit script. MediaPipe 0.10.21 local smoke test emitted no Clearcut upload text; this does not prove every dependency is free of all network behavior. |
| CAM-07 | Setup and model integrity | Document setup; download model only on explicit request and verify before install. | Verified — `README.md`, `requirements.txt`, `scripts/download_model.py`; checked included model SHA-256 equals the script pin. |
| CAM-08 | Error states and diagnostics | Show useful setup/device failures and log diagnostics without frames. | Partial — fake-camera open-failure test verifies an actionable worker failure and capture release; visible UI presentation and physical permission errors remain unverified. |
| CAM-09 | Automated validation | Focused tests and syntax/dependency checks. | Verified for tested scope — 12 `unittest` checks, `compileall`, `pip check`, MediaPipe blank-frame task smoke, and offscreen UI smoke passed; these do not establish real webcam behavior. |
| CAM-10 | Real-device validation | Verify on a Windows 11 machine with a working camera and face in view. | Blocked — no camera device was enumerated in this environment. The owner should run the documented app manually with a webcam. |
| KEEPER-01 | Context continuity | Keep current work, handoff, architecture, privacy and generated state aligned with app source. | Verified structurally after this session's updates — see `scripts/context_validate.py`; it does not validate app behavior. |

## Requirements change policy

- Product goals are not proof of implementation. Keep statuses tied to inspected files and checks.
- Record camera, model, permission, and processing limitations directly; do not claim a real-device pass without observing one.
- Changes to capture, networking, storage, identity, or telemetry require explicit scope and corresponding privacy review.
