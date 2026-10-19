# Security and Privacy Context

This project is a local webcam preview and face-contour app. It has no user identity, account system, backend, or authorization roles. The context keeper originally carried social-app security requirements; those were not applicable to this app and are superseded here.

## Identity and authorization

- Not applicable to current scope: no identity, server, private multi-user records, or privileged account operations were found.
- Do not add account identity or access-controlled remote features without an explicit product decision and an appropriate trusted boundary.

## Camera and face-data handling

- Camera frames and facial landmarks are processed in memory on the local machine. Do not upload, record, export, save snapshots, identify people, or derive identity profiles without an explicit scope change.
- Camera access is initiated by the user pressing Start; no background camera capture is intended.
- Keep UI preferences distinct from image/landmark data. QSettings preferences are the only intended app persistence.
- Handle permission denial, camera busy/disconnect, and model errors clearly. Always release the capture device and landmarker when stopping or exiting.
- Do not write camera frames, facial landmarks, or sensitive content to logs. Current diagnostics record operational messages/errors only by source inspection.

## Dependency and model acquisition

- Dependency installation and model download are explicit setup actions. The model downloader uses HTTPS, a size bound, and SHA-256 verification before replacing the target file.
- The current MediaPipe version was pinned after a local smoke test of 0.10.21 produced no Clearcut upload text; this observation is limited and is not proof of absence of all network activity in every dependency/runtime condition.
- Review dependency changes for privacy effects before updating versions or adding packages.

## Implementation and evidence checklist

For capture or model changes, inspect data flow, persistence, network use, cleanup on stop/failure/exit, errors, and focused tests. Mark real webcam behavior unverified until tested on a device. Never convert an offscreen UI smoke test or synthetic tracker test into a claim of camera correctness.
