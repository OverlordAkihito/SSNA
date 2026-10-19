# Requirements Register

**Evidence boundary:** The rows below describe the requested camera app and current source-backed status. Statuses are based on source inspection plus the listed focused checks; they do not imply successful real-camera operation.

## Status vocabulary

Use `Verified`, `Partial`, `UI-only`, `Missing`, `Unable to verify`, `Blocked`, or `Not applicable`. Every status has evidence and material gaps.

| ID | Requirement area | Expected behavior / acceptance summary | Current status and evidence |
|---|---|---|---|
| CAM-01 | Windows desktop UI | Launch a Windows desktop window with camera preview and controls. | Partial — PySide6 UI exists in `shet_shet/ui.py`; offscreen construction smoke check passed, but no native Windows interaction review was done. |
| CAM-02 | Camera discovery and selection | Scan available cameras, select one, refresh after device changes, handle no camera and open failure. | Partial — `CameraScanner` scans indexes 0–7 and `CameraWorker` reports open/read errors in `shet_shet/camera.py`; this environment enumerated no camera, so device behavior is unverified. |
| CAM-03 | Live preview lifecycle | Start and stop camera, show live frames, release camera/model resources on stop, failure, and close. | Partial — worker tests in `tests/test_camera.py` pass with a fake camera: frame data is surfaced and camera/model resources close after stop; open failure releases capture. Real device/driver behavior is still unverified. |
| CAM-04 | Facial landmark filter | Detect multiple face landmark sets and show pearl dots across face outline, eyebrows, eyes/irises, nose, and lips with a pink eye glow; retain optional contour mode. | Partial — full MediaPipe landmark arrays are returned by `shet_shet/vision.py`; region indices in `shet_shet/landmarks.py`; `shet_shet/preview.py` paints pearl dots plus a saturated glow anchored to detected iris-center landmarks, with the contour separately selectable. Synthetic tests check dot painting and magenta glow pixels; actual face alignment and match to the reference style require webcam validation. |
| CAM-05 | User controls and preferences | Configure mirror, effect, dot/contour mode, outline colour/thickness, and smoothing; persist preferences. Turning the effect off hides only the overlay and plays the supplied cue once per ON-to-OFF transition. | Partial — the existing checkbox controls only the overlay and continues sending options to the running camera worker; saved state is restored silently. Transition tests cover ON→OFF, OFF→OFF, OFF→ON, and a subsequent ON→OFF. |
| CAM-06 | Local-only processing and minimization | Do not identify, record, save or upload frames/landmarks; keep processing local and avoid telemetry. | Partial — app flow has no network/recording path and only saves UI preferences; model is acquired by explicit script. MediaPipe 0.10.21 local smoke test emitted no Clearcut upload text; this does not prove every dependency is free of all network behavior. |
| CAM-07 | Setup and model integrity | Document setup; download model only on explicit request and verify before install. | Verified — `README.md`, `requirements.txt`, `scripts/download_model.py`; checked included model SHA-256 equals the script pin. |
| CAM-08 | Error states and diagnostics | Show useful setup/device failures and log diagnostics without frames. | Partial — fake-camera open-failure test verifies an actionable worker failure and capture release; missing audio logs a warning and MCI failures log diagnostics. Physical permission errors and audible playback remain unverified. |
| CAM-09 | Automated validation | Focused tests and syntax/dependency checks. | Verified for tested scope — 16 `unittest` checks, `compileall`, `pip check`, MediaPipe blank-frame task smoke, offscreen UI smoke, and MCI open/close of the supplied MP3 passed; these do not establish actual camera behavior or audible output. |
| CAM-10 | Real-device validation | Verify on a Windows 11 machine with a working camera and face in view. | Blocked — no camera device was enumerated in this environment. The owner should run the documented app manually with a webcam. |
| CAM-11 | Filter-off MP3 cue | Play the supplied MP3 once on a genuine effect ON-to-OFF transition, without stopping capture; ignore duplicate OFF state and clean up audio on exit. | Partial — the exact supplied MP3 is bundled at `assets/audio/shet-shet-nakita-ko-akosidogie-meme-oicwbjyekq0_Jd8GzV3n.mp3` (copied SHA-256 matches source); transition and missing-file tests pass, and Windows MCI opened/closed it. No audio endpoint was enumerated, so audible output is unverified. |
| KEEPER-01 | Context continuity | Keep current work, handoff, architecture, privacy and generated state aligned with app source. | Verified structurally after this session's updates — see `scripts/context_validate.py`; it does not validate app behavior. |

## Requirements change policy

- Product goals are not proof of implementation. Keep statuses tied to inspected files and checks.
- Record camera, model, permission, and processing limitations directly; do not claim a real-device pass without observing one.
- Changes to capture, networking, storage, identity, or telemetry require explicit scope and corresponding privacy review.
