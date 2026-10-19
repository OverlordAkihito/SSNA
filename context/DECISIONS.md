# Decision Register

This file stores durable decisions, not assumptions disguised as facts. Add an ID, status, date, rationale, consequences, and evidence/context for future decisions. Mark superseded decisions instead of erasing history.

## D-001 — Requirements are not implementation evidence

- **Status:** Confirmed operating rule
- **Decision:** Treat app feature descriptions as desired product behavior until repository inspection and relevant checks establish the actual state.
- **Rationale:** The supplied development guide explicitly requires a repository audit and warns against assuming a feature works because a UI element exists.
- **Consequences:** Audit features through UI, data access, identity/authorization and trusted backend boundaries where possible; use evidence-based statuses in `REQUIREMENTS.md`.

## D-002 — Repository-first development

- **Status:** Confirmed operating rule
- **Decision:** Inspect the actual repository before choosing architecture, dependencies, implementation sequence, or code patterns.
- **Rationale:** Prevents guessed frameworks/providers and unnecessary rewrites.
- **Consequences:** First initialization is audit-only; architecture and roadmap follow the audit.

## D-003 — No silent provider selection

- **Status:** Confirmed operating rule
- **Decision:** Do not silently pick auth, database, hosting, realtime, payment or external backup providers where the repo/configuration and owner have not established a choice.
- **Rationale:** Such choices affect security, cost, deployment, privacy and migration.
- **Consequences:** Complete provider-independent safe work if useful and record the exact choice/configuration needed.

## D-004 — Sensitive authorization must be trusted

- **Status:** Confirmed security rule
- **Decision:** Browser visibility or editable client state is not an authorization boundary.
- **Rationale:** Multi-user data, admin operations, private messages, moderation, subscriptions and backups require access control that cannot be bypassed by calling APIs directly.
- **Consequences:** Trace and test both permitted and denied operations at the trusted service boundary.

## D-005 — Smallest coherent safe change

- **Status:** Confirmed engineering rule
- **Decision:** Preserve sound existing behavior and make the smallest complete change that satisfies the task; avoid unrelated rewrites, duplicate systems, and unnecessary dependencies.
- **Rationale:** Improves maintainability and reduces regressions.
- **Consequences:** Expand scope only when dependencies, security, correctness or acceptance criteria require it.

## D-006 — Evidence-based validation reports

- **Status:** Confirmed operating rule
- **Decision:** Report checks as PASS/FAIL/NOT RUN using actual commands/results; do not infer success from intention or from unrelated earlier runs.
- **Rationale:** Makes the handoff reliable and avoids false completion claims.
- **Consequences:** Record environment/credential blockers and concrete next checks.

## App-specific technical decisions

### D-007 — Local-only webcam processing

- **Status:** Confirmed product constraint
- **Decision:** Process camera frames and face landmarks locally; provide no recording, snapshot, upload, telemetry, analytics, or identity-recognition feature.
- **Rationale:** This was an explicit requirement in the user-supplied app prompt and limits sensitive face data to transient local processing.
- **Consequences:** Review future dependency and data-flow changes for network or persistence behavior. Source inspection and a limited pinned-version smoke check are evidence, not a formal guarantee about every dependency.
- **Evidence:** `shet_shet/camera.py`, `shet_shet/vision.py`, `shet_shet/ui.py`, `context/USER_PROVIDED_PROMPTS.md`.

### D-008 — Explicit verified model installation

- **Status:** Confirmed implementation decision
- **Decision:** Download the MediaPipe model only when the owner runs the setup script; verify SHA-256 and size before atomically installing it.
- **Rationale:** Prevents silent startup networking and rejects an unexpected or changed model artifact.
- **Consequences:** First-time setup requires the explicit model command and network access; app startup reports the missing model with the setup command.
- **Evidence:** `scripts/download_model.py`, `shet_shet/vision.py`, `README.md`.

### D-009 — Paint tracking overlay in preview coordinates

- **Status:** Confirmed implementation decision
- **Decision:** Keep the camera image unmodified after RGB conversion and paint the facial effect in a separate Qt preview layer using the same aspect-fit rectangle as the image.
- **Rationale:** This avoids baking display scaling into capture data and keeps overlay positions aligned while the preview resizes or letterboxes.
- **Consequences:** Apply mirror transformation before both inference and display; test coordinate mapping independently; verify real face alignment on hardware.
- **Evidence:** `shet_shet/camera.py`, `shet_shet/preview.py`, `tests/test_preview.py`.
