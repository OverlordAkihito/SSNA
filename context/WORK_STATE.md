# Work State

**Current state (2026-10-19):** Local Windows camera app now has selectable MediaPipe landmark-dot and face-contour effects with a separate aspect-fit overlay. Automated and headless checks pass. Real webcam operation remains unverified because Windows returned no camera devices.

**Current milestone:** Landmark-dot filter implemented and covered by automated/headless checks; hand off for physical-camera validation.

## Active work

- [x] Implement PySide6 camera UI, OpenCV capture worker, MediaPipe face contour, smoothing, control preferences, explicit model download, setup docs, and focused tracker tests.
- [x] Reconcile stale keeper-only context and audit notes with the actual application files.
- [x] Confirm the model file matches the pinned downloader SHA-256.
- [x] Add fake-camera tests for latest-frame processing, face count, stop cleanup, and camera-open failure cleanup.
- [x] Retain full MediaPipe face landmark arrays and map face outline, brows, eyes/irises, nose, and lips.
- [x] Add a separate Qt preview overlay with white dots, magenta eye halos, optional face contour, aspect-fit alignment, and short tracking-loss fade.
- [x] Keep mirror transformation in the frame path before inference and display so overlay geometry follows the visible mirrored frame.
- [x] Publish detached track snapshots so the camera thread cannot mutate data while the UI paints; cache center/bounds for full-mesh association.
- [ ] Run the app on Windows 11 with an accessible webcam and verify alignment during movement, head turns, blinking, expressions, mirroring, resizing, loss/recovery, stop/restart, and clean shutdown.
- [ ] After hardware validation, record observed behavior and any fixes here and in requirements/session log.

## Checks run this continuation

- `\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **PASS**, 12 tests: five synthetic tracker checks, three fake-camera worker lifecycle/error/snapshot checks, and four overlay/coordinate checks.
- `\.venv\Scripts\python.exe -m compileall -q shet_shet scripts\download_model.py tests` — **PASS**.
- `\.venv\Scripts\python.exe -m pip check` — **PASS**, no broken requirements.
- `Get-FileHash models\face_landmarker.task -Algorithm SHA256` — **PASS**, matches `EXPECTED_SHA256` in `scripts/download_model.py`.
- Offscreen visible main-window/dot-filter smoke plus MediaPipe blank-frame inference using the venv Python — **PASS**, window initialized and blank image yielded zero faces. MediaPipe printed normal CPU/XNNPACK and feedback warnings.
- `Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue` — **NOT AVAILABLE**, command returned no camera devices; this is an environment limitation, not a pass of camera capture.
- `\.venv\Scripts\python.exe scripts/context_sync.py` — **PASS**, snapshot fingerprint `51d461af37761c9c` before final status wording; refresh after it.
- `\.venv\Scripts\python.exe scripts/context_validate.py` — **PASS**, 18 required files and key sections.
- `git diff --check` — **PASS**; Git emitted only LF-to-CRLF working-copy warnings.

## Blockers / unknowns

- No physical camera was exposed by Windows, so actual device access, OS camera permission behavior, landmark-dot alignment/quality, disconnect recovery, and camera release are not confirmed.
- A blank-frame model smoke proves task initialization/inference only, not detection accuracy or dot alignment on a face.
- Dependency smoke showed no Clearcut upload text for the pinned MediaPipe version; it is not a comprehensive network audit.
- Git is available and the repo has a `.git` directory; review `git status` and final diff before handoff. Several app files are currently untracked as initial implementation artifacts.

## Next action

Run `README.md` on a Windows 11 PC with a webcam and verify dots follow the face across movements, expressions, mirroring, and resizing; then update this state with observed results.
