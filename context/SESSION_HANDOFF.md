# Session Handoff

**State:** Real-time landmark-dot filter and resize-safe overlay implemented; local automated/headless checks pass; physical-camera validation is outstanding.

**Updated:** 2026-10-19

## Current implementation

- PySide6 desktop UI, OpenCV camera worker, MediaPipe Face Landmarker, full facial landmark dot overlay, optional face contour, aspect-fit/mirror alignment, smoothing/fade, settings, explicit model downloader, tests, and README setup are present. Tests cover fake-camera cleanup and preview coordinate mapping. See `context/ARCHITECTURE.md` and `docs/REPOSITORY_AUDIT.md` for evidence.
- Privacy scope is local transient frame/landmark processing, with preferences as the only intended persisted app data. Do not add recording, upload, telemetry, or face identity recognition without an explicit scope change.
- The keeper's previous “no app source” handoff/audit was stale and has been corrected.

## Last verified checks

- 12 unit tests — PASS (tracker behavior, fake-camera worker paths/snapshot isolation, overlay painting, and 4:3/16:9 aspect-fit mapping).
- `compileall`, `pip check`, model SHA-256, offscreen UI construction, and MediaPipe blank-frame inference — PASS.
- Windows `Get-PnpDevice -Class Camera` returned no devices. Actual camera capture and facial-dot alignment remain unverified.
- Context sync `51d461af37761c9c` and structural validation (18 files/sections) — PASS before this handoff update; refresh once more after final context edits.

## Next action

Run `README.md` on Windows 11 with a working webcam. Verify actual dot alignment while moving/turning/blinking/changing expressions, mirror mode, resize, tracking-loss recovery, camera stop/restart, and clean shutdown; then record results in `WORK_STATE.md`, `REQUIREMENTS.md`, and `SESSION_LOG.md`.
