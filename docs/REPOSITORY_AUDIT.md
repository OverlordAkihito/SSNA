# Repository Audit

**Audit date:** 2026-10-19

**Scope:** Current workspace `C:\Users\Jenren B. Datan\Downloads\SD-Card\DEV\projects\SSNA`.

**Result:** A functional-scope implementation exists for a local Windows webcam face-contour app. Build/headless validation is positive; physical camera behavior is **unable to verify** in this environment.

## Stack and entry points

- Python 3.12 virtual environment; requirements in `requirements.txt`.
- PySide6 Essentials desktop UI; app entrypoint `shet_shet/main.py`, launched by `run.bat` or the README command.
- OpenCV camera enumeration/capture in `shet_shet/camera.py`.
- MediaPipe Face Landmarker adapter and oval extraction in `shet_shet/vision.py`; synthetic association/smoothing logic in `shet_shet/tracking.py`.
- Setup model downloader in `scripts/download_model.py`, with pinned URL, SHA-256, size bounds, temporary file, and atomic replacement.
- UI tracker tests in `tests/test_tracking.py`.

## Data and trust boundaries

All camera capture, inference and rendering are intended to occur in the local desktop process. Frames and landmarks are transient; QSettings stores the UI options. No application server, database, identity/account system, recording/export path, or cloud integration was found. Model acquisition uses explicit HTTPS download only when the setup script is invoked. Runtime logs are configured under `%LOCALAPPDATA%\ShetShetNakitaAko\logs`; source inspection shows no frame writes.

## Source evidence and current gaps

| Area | Evidence | Finding |
|---|---|---|
| UI and camera controls | `shet_shet/ui.py` | Start/stop, camera selection/refresh, preview, effect/mirror/colour/thickness/smoothing controls, status and FPS/face count exist. |
| Capture lifecycle | `shet_shet/camera.py` | Camera scanner and worker run off the UI thread; worker releases capture and landmarker in `finally`. Physical driver lifecycle not exercised. |
| Face contour | `shet_shet/vision.py`, `tracking.py`, `camera.py` | Up to four face landmarks, oval contour, matching/smoothing and overlay are implemented. Accuracy on real faces is unverified. |
| Model acquisition | `scripts/download_model.py`, `requirements.txt` | Download is explicit and verifies expected SHA-256. Checked local model hash matched pin. |
| Tests | `tests/test_tracking.py`, `tests/test_camera.py` | Seven tests cover synthetic tracker behavior and fake-camera worker frame/cleanup/error paths; no physical capture or real-face accuracy assertion. |
| Privacy | `shet_shet/ui.py`, `camera.py`, `main.py`, `vision.py` | No app-level upload/recording/persistence for frames found by source inspection. Limited MediaPipe 0.10.21 blank-frame smoke emitted no Clearcut text; comprehensive dependency network audit not performed. |

## Validation observed 2026-10-19

- `\.venv\Scripts\python.exe -m unittest discover -s tests -v` — PASS, seven tests including fake-camera worker lifecycle/error paths.
- `\.venv\Scripts\python.exe -m compileall -q shet_shet scripts\download_model.py tests` — PASS.
- `\.venv\Scripts\python.exe -m pip check` — PASS, no broken requirements.
- `Get-FileHash models\face_landmarker.task -Algorithm SHA256` — PASS, equals downloader pin.
- Offscreen `MainWindow` construction and MediaPipe blank-frame inference — PASS; zero faces returned as expected.
- `Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue` — no devices returned; actual camera discovery/opening, permission behavior, live contours, disconnect and shutdown remain NOT RUN / unable to verify.
- Keeper context sync and structural validation — PASS; latest result is recorded in `WORK_STATE.md`.

## Security and reliability risks (gaps, not confirmed defects)

- Actual camera access and OS camera privacy interaction need a webcam-equipped Windows 11 check.
- Face contour fidelity and performance under varied faces/lighting/movement are unmeasured.
- No comprehensive third-party dependency network-behavior audit was performed. Reassess privacy/network behavior on dependency upgrades.
- No installer, code signing, deployment, or release packaging is present or verified.

## Best next action

Run the setup/run flow from `README.md` on Windows 11 with a working webcam; validate discovery, preview, contour controls, stop/restart, device disconnect, and clean shutdown, then update requirement status from direct observation.
