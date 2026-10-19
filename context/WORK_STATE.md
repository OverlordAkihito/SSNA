# Work State

**Current state (2026-10-19):** Local Windows camera app implemented; build-level checks pass. Real webcam operation remains unverified because Windows returned no camera devices.

**Current milestone:** Add hardware-independent coverage for the camera worker; real webcam validation remains outstanding.

## Active work

- [x] Implement PySide6 camera UI, OpenCV capture worker, MediaPipe face contour, smoothing, control preferences, explicit model download, setup docs, and focused tracker tests.
- [x] Reconcile stale keeper-only context and audit notes with the actual application files.
- [x] Confirm the model file matches the pinned downloader SHA-256.
- [x] Add fake-camera tests for latest-frame processing, face count, stop cleanup, and camera-open failure cleanup.
- [ ] Run the app on Windows 11 with an accessible webcam and a face in view; verify selection, start/stop, contour controls, disconnect/error, and clean shutdown.
- [ ] After hardware validation, record measured behavior and any fixes here and in requirements/session log.

## Checks run this continuation

- `\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **PASS**, 7 tests: five synthetic tracker checks and two fake-camera worker lifecycle/error checks.
- `\.venv\Scripts\python.exe -m compileall -q shet_shet scripts\download_model.py tests` — **PASS** after the added test module.
- `\.venv\Scripts\python.exe -m pip check` — **PASS**, no broken requirements.
- `Get-FileHash models\face_landmarker.task -Algorithm SHA256` — **PASS**, matches `EXPECTED_SHA256` in `scripts/download_model.py`.
- Offscreen UI plus MediaPipe blank-frame smoke using the venv Python — **PASS**, UI initialized and blank image yielded zero faces. MediaPipe printed normal CPU/XNNPACK and feedback warnings.
- `Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue` — **NOT AVAILABLE**, command returned no camera devices; this is an environment limitation, not a pass of camera capture.
- `\.venv\Scripts\python.exe scripts/context_sync.py` — **PASS**, snapshot fingerprint `99de548828cae27c` before this status note; refresh once more after editing context.
- `\.venv\Scripts\python.exe scripts/context_validate.py` — **PASS**, 18 required files and key sections.
- `git diff --check` — **PASS**; only Git LF-to-CRLF working-copy warnings were emitted.

## Blockers / unknowns

- No physical camera was exposed by Windows, so actual device access, OS camera permission behavior, face-contour quality, disconnect recovery, and camera release are not confirmed.
- A blank-frame model smoke proves task initialization/inference only, not detection accuracy on a face.
- Dependency smoke showed no Clearcut upload text for the pinned MediaPipe version; it is not a comprehensive network audit.
- Git is available and the repo has a `.git` directory; review `git status` and final diff before handoff. Several app files are currently untracked as initial implementation artifacts.

## Next action

Run `README.md` setup/run instructions on a Windows 11 PC with a webcam and validate the capture lifecycle and visible face contour, then update this state with observed results.
