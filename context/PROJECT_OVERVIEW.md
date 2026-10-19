# Project Overview

## Purpose

Build a Windows desktop app named **SHET SHET NAKITA AKO** that previews a webcam feed and overlays smooth facial landmark dots or a selectable face contour. The current implementation processes frames on the local PC and has no recording, snapshot, identity recognition, upload, analytics, or telemetry feature in app code.

## Intended user experience

- Select or refresh the available camera list, start/stop preview, and see useful setup or device errors.
- See white dots at detected face, brow, eye, nose, and lip landmarks with a magenta eye glow, or select the original face-outline effect.
- Keep the overlay aligned as the preview resizes, changes aspect ratio, or is mirrored.
- Use the app with more than one face in view when MediaPipe detects them.
- Keep face frames and landmarks transient in memory; persist only UI preferences.

These are product goals. Refer to `REQUIREMENTS.md` and inspect implementation and checks for each feature's current status.

## Product principles

1. Camera video and landmark processing stay on the device; do not add upload, recording, telemetry, analytics, or identity recognition without an explicit scope change.
2. Camera and model resources must be released on stop, failure, and application close.
3. Communicate camera/model errors honestly and provide actionable setup steps.
4. Keep model acquisition explicit and integrity-checked rather than silently downloading it at launch.
5. Distinguish automated logic checks from real camera/manual validation.
6. Keep handoff/context records consistent with source and current validation evidence.

## Out of scope

No account system, network service, database, social features, recording/export, face identification, cloud processing, or installer/release packaging is in scope unless the user explicitly changes the product request.

## Evidence status

The current implementation is a local Python/PySide6 desktop app under `shet_shet/`. Architecture and check evidence are recorded in `ARCHITECTURE.md`, `REQUIREMENTS.md`, `WORK_STATE.md`, and `docs/REPOSITORY_AUDIT.md`. Actual webcam behavior remains unverified in this environment because no camera device was enumerated.
