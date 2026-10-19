# Architecture Record

## Evidence status at bootstrap

The inspected workspace is the context-keeper kit, not the target application. Its detected contents and audit limitation are recorded in `docs/REPOSITORY_AUDIT.md`. The keeper scripts are Python, but this does not establish the application's language or architecture. No app source, runtime, backend, data store, authentication, or provider was found here; all app architecture remains unknown until the actual application root is supplied and audited.

## Current-state facts to establish in `docs/REPOSITORY_AUDIT.md`

- Languages, frameworks, build tooling, package managers, entry points and key directories.
- Runtime/hosting assumptions and environment/configuration inputs (names only; never values for secrets).
- Client/server or trusted-service boundaries.
- Persistence, database/storage, schema/migrations and data ownership rules.
- Authentication/session setup and role/authorization enforcement points.
- Chat/realtime, media upload, external backup and billing/subscription integrations where present.
- Tests, lint/type-check/build commands and observed results.
- Feature-by-feature evidence and ranked security/reliability risks.

## Architecture guardrails

1. Do not select a new framework, backend, database, auth service, cloud host, realtime provider, QR package, payment provider or external storage provider without evidence or an explicit owner decision.
2. Prefer one clear trusted path for sensitive operations; do not create overlapping backends/data stores without a concrete rationale.
3. A browser-only UI cannot be treated as a trusted authority for authentication, authorization, billing entitlements, moderation, protected backups, or cross-user access control.
4. Enforce record ownership and authorization at the trusted server/service layer; UI checks support usability but do not replace authorization.
5. Document data model, retention/deletion, migration, recovery and compatibility implications when relevant.
6. Keep provider-independent interfaces only when they solve a real current requirement; avoid speculative abstraction layers.
7. Separate confirmed current architecture from recommended target architecture. Mark proposals as `Proposed` until selected.

## Decisions not yet made

Provider selection, production URL, deployment environment, persistence technology, realtime transport, payment system, and external backup destination remain undecided here unless the actual repository or owner configuration establishes otherwise. Do not fill these gaps with invented values.

## Next architecture work

The application audit is blocked because this workspace contains only the keeper. After opening the actual app root, update this file with evidence-backed architecture facts and source paths/symbols. Record target architecture separately in `docs/ARCHITECTURE_DECISIONS.md` with trust boundaries, data ownership, service responsibilities, migration stages, and unresolved choices. A recommendation is not a fact about what is implemented.
