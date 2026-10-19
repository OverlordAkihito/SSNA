# Session Log

Keep this log concise: meaningful changes, durable decisions, important discoveries, incidents, and failed approaches that should not be repeated. It is not a transcript of every action.

## 2026-10-16 — Context keeper created

- Built a starter keeper from the provided prompt-completeness prompt, app development guide, and previous context-keeper note.
- Added root agent instructions, durable context files, a requirement register for the intended app, an audit-only first-run prompt, a recurring task prompt, a repository snapshot generator, and a context-file validator.
- Important boundary: no application source repository was included with the keeper source materials, so the actual stack, architecture and implementation status remain unknown. The feature list is recorded as goals only.
- No application tests, build, security assessment, provider integration or deployment were performed by creating this keeper.
- Next: install/merge into the actual project root and perform the read-first audit.

## Append future entries

Use a date and short heading. Include outcome, important files/decisions, checks actually run and their result, and remaining blockers only when useful for future work.

## 2026-10-19 — Camera worker tests

- Added `tests/test_camera.py` with deterministic fake-camera checks for latest-frame/face-count delivery, worker stop cleanup, and camera-open failure reporting/resource release.
- Updated README, requirements, architecture, and repository audit to distinguish fake-camera coverage from actual webcam validation.
- `unittest` now passes 7 tests; `compileall`, `pip check`, and `git diff --check` passed. Physical webcam behavior remains unverified because no camera is available in the environment.

## 2026-10-19 — Real-time facial landmark dot filter

- Kept full MediaPipe face landmark coordinates, added documented region index groups, and introduced a separate aspect-fit Qt preview overlay with pearl dots, magenta eye glow, optional face-contour mode, mirror-consistent coordinates, and brief miss fade. Cached full-mesh geometry for track matching and detached track snapshots before cross-thread UI publication.
- Updated UI preference persistence, README, requirements, architecture, decisions and audit notes. Camera stop/error now clears the last image from the preview.
- `unittest` passes 12 checks (tracker, fake-camera worker lifecycle/error/snapshot isolation, overlay painting, and 4:3/16:9 resize/aspect mapping); `compileall` and `pip check` pass. A webcam was still unavailable, so actual face alignment and visual behavior need Windows hardware validation.

## 2026-10-19 — Camera app build continued; stale context corrected

- Inspected the existing `shet_shet/` implementation and confirmed it is a local PySide6/OpenCV/MediaPipe Windows webcam face-contour app with explicit model download and synthetic tracker tests.
- Updated README headings/definition to satisfy keeper validation and document what tracking means. Replaced stale social-app/keeper-only overview, requirements, architecture, and security context with the actual camera app scope; added local-only/model-install decisions and updated work state and handoff.
- Checks: 5 tracker tests PASS; `compileall` PASS; `pip check` PASS; pinned model SHA-256 PASS; offscreen UI and MediaPipe blank-frame smoke PASS. Windows camera device query returned no devices, so real webcam/camera permission behavior remains unverified.
- Next: run on a Windows 11 computer with webcam and validate the actual capture/contour lifecycle, then update statuses from observed behavior.
