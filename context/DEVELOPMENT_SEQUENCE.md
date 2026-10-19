# Development Sequence and Release Checks

Use this order as a focused guide for the local Windows camera application. Inspect current source and evidence before repeating completed work. Do not import the former social-app roadmap; accounts, backend, billing, chat, and backups are outside current scope.

## Build sequence

1. **Repository audit and task context** — read `AGENTS.md`, current handoff/work state, requirements, architecture, and privacy notes; inspect affected code and available hardware.
2. **Camera foundation** — confirm camera enumeration, permission/error states, frame delivery, stop/restart, and cleanup.
3. **Face landmark path** — return actual MediaPipe coordinates, associate/smooth tracks, and handle temporary loss/recovery.
4. **Preview alignment and effect** — paint dots/contour in the same aspect-fit coordinate space as the image; apply mirror transformation consistently; keep overlay separate from frame pixels.
5. **Usability and privacy** — provide filter controls and persistence for preferences only; ensure app code does not save or transmit frames/landmarks and clears preview after stop/failure.
6. **Validation** — run focused unit/headless tests and the app on Windows with a camera; state the distinct evidence provided by each.
7. **Handoff** — update README, requirements, architecture/privacy/decision notes, work state, session log, generated snapshot, and handoff.

## App-specific release/acceptance checklist

Mark each item PASS only with direct evidence; use FAIL or NOT RUN as appropriate.

- [ ] Setup instructions install the pinned dependencies and retrieve/verify the model only when explicitly requested.
- [ ] App starts with a useful empty/error state when no usable camera or model is present.
- [ ] Windows camera permission denial, camera-busy, read failure, stop, restart, and close release resources and show useful feedback.
- [ ] A real camera feed is visible while camera is enabled; it stops and the last frame is cleared when stopped or failed.
- [ ] Face Landmarker returns the expected facial-region coordinates for visible faces.
- [ ] Dots align to face outline, brows, eyes/irises, nose, and lips on live video; eye accents are visible without obscuring the eye.
- [ ] Overlay follows translation, head turn, blinking, expression changes, temporary loss and reacquisition without unacceptable jitter or lag.
- [ ] Mirroring and preview resize/aspect ratio preserve alignment.
- [ ] Existing contour effect remains available; filter/effect controls and smoothing preferences work.
- [ ] Frames and landmarks are not recorded, persisted, logged, or transmitted by app code; review network behavior when dependencies change.
- [ ] Automated tests cover tracking, camera-worker cleanup/error handling, overlay rendering, and coordinate transform; report limitations honestly.
- [ ] README, context, and release status distinguish fake/headless checks from physical-camera/manual validation.
- [ ] Git diff contains only intended files and no secrets or generated runtime data.

## Release gate output

Create/update `docs/RELEASE_CHECKLIST.md` when a release gate is requested. Record PASS / FAIL / NOT RUN with evidence and blockers. Do not claim live camera acceptance without running the app on a supported Windows machine and observing the effect on a face.
