# Work State

**Current state (2026-10-19):** Local Windows camera app has selectable MediaPipe landmark-dot and face-contour effects with a separate aspect-fit overlay. The dot appearance was tuned toward the user reference, and the supplied MP3 is connected to the filter OFF transition. Windows exposed no camera or audio endpoint, so live camera and audible output remain unverified.

**Current milestone:** Landmark-dot/contour filter and the supplied ON-to-OFF audio cue are implemented and covered by automated/headless checks; physical-camera and audible-output validation remain.

## Active work

- [x] Implement PySide6 camera UI, OpenCV capture worker, MediaPipe face contour, smoothing, control preferences, explicit model download, setup docs, and focused tracker tests.
- [x] Reconcile stale keeper-only context and audit notes with the actual application files.
- [x] Confirm the model file matches the pinned downloader SHA-256.
- [x] Add fake-camera tests for latest-frame processing, face count, stop cleanup, and camera-open failure cleanup.
- [x] Retain full MediaPipe face landmark arrays and map face outline, brows, eyes/irises, nose, and lips.
- [x] Add a separate Qt preview overlay with white dots, magenta eye halos, optional face contour, aspect-fit alignment, and short tracking-loss fade.
- [x] Tune the dot style toward the supplied reference with pearl highlights and vivid magenta glow anchored to detected iris centers; add a synthetic pixel assertion for the accent.
- [x] Bundle the user's exact MP3 and connect the existing filter checkbox's genuine ON-to-OFF transition to reusable background playback; preserve camera capture and restore settings silently.
- [x] Keep mirror transformation in the frame path before inference and display so overlay geometry follows the visible mirrored frame.
- [x] Publish detached track snapshots so the camera thread cannot mutate data while the UI paints; cache center/bounds for full-mesh association.
- [ ] Run the app on Windows 11 with an accessible webcam and verify alignment during movement, head turns, blinking, expressions, mirroring, resizing, loss/recovery, stop/restart, and clean shutdown.
- [ ] After hardware validation, record observed behavior and any fixes here and in requirements/session log.

## Checks run this continuation

- `\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **PASS**, 16 tests covering tracker, fake-camera cleanup/snapshot, overlay rendering, and audio transition/file/session behavior.
- `\.venv\Scripts\python.exe -m compileall -q shet_shet tests` — **PASS**.
- `\.venv\Scripts\python.exe -m pip check` — **PASS**, no broken requirements.
- Windows MCI open/close smoke on the bundled MP3 — **PASS**; playback was not started.
- Source MP3 and bundled copy SHA-256 — **PASS**, both `B4E56C8780B74D5DB370274BCD595446E4076996E0AF8D563BA3108539F7C093`.
- Offscreen `MainWindow` construction — **PASS**; saved filter restoration did not start the audio worker.
- Offscreen UI construction / MediaPipe blank-frame smoke from the previous implementation session — **PASS**; no camera was available.
- `Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue` and `Get-PnpDevice -Class AudioEndpoint -ErrorAction SilentlyContinue` — **NOT AVAILABLE**, returned no camera or audio endpoint devices. Actual capture and audible output were not tested.
- `\.venv\Scripts\python.exe scripts/context_sync.py` and `scripts/context_validate.py` — **PASS**, generated state refreshed and 18 required files/key sections validated.
- `git diff --check` — **PASS**.

## Blockers / unknowns

- Windows enumerated no physical camera or audio endpoint, so actual capture, OS camera permission behavior, landmark alignment/quality, disconnect recovery, audible sound/device routing, and volume/mute behavior are unconfirmed.
- A blank-frame model smoke proves task initialization/inference only, not detection accuracy or dot alignment on a face.
- Dependency smoke showed no Clearcut upload text for the pinned MediaPipe version; it is not a comprehensive network audit.
- Git is available; final diff was reviewed after the style refinement.

## Next action

Run `README.md` on a Windows 11 PC with a webcam and sound output. Verify dots/contour alignment across movement, mirroring, and resizing, and confirm the supplied cue plays once per ON-to-OFF while capture continues; then record observed results here.
