# Project Overview

## Purpose

Build and maintain a multi-user social/community application with user profiles and relationships, messaging, account administration, moderation, privacy controls, subscription-state visibility, and robust data recovery.

## Intended user experiences

- **Client/user experience:** register or sign in, manage a profile, discover users through a stable public-facing ID/search, interact through connections/likes, use the in-scope chat modes, control profile/location/privacy visibility, use a QR profile link, and manage eligible data/deletion preferences.
- **Admin/moderation experience:** authorized account management, report review, moderation actions, appropriate subscription-state visibility, auditable privileged operations, and supported backup/recovery workflows.
- **Owner/developer experience:** reliable setup, tests, explicit configuration requirements, documented architecture, safe migrations, practical handoff, and clear release gates.

These are goals, not a confirmation that any screen, API, data model, or secure workflow exists.

## Historical project description

The development guide says the app had been described as built with HTML and JavaScript. It explicitly warns the coding agent not to assume that this description fully represents the current repository. Verify the actual stack from repository files.

## Product principles

1. Multi-user isolation and trusted authorization must be real; hiding a control in the browser is not security.
2. Keep the smallest coherent architecture capable of the required features; preserve working behavior and avoid duplicate systems.
3. Privacy is a product behavior: public/private settings and consent must affect actual data returned and actions allowed.
4. Security-sensitive capabilities require evidence-based validation, not UI-only completion claims.
5. Unconfigured provider integrations must be labeled unconfigured; do not fabricate connectivity or successful payments/backups.
6. Feature implementation should follow prerequisites and the real repository's state, not a blind checklist.
7. Each meaningful task should leave enough accurate context for a new AI session to continue safely.

## Out of scope unless explicitly added

Do not silently select payment, hosting, identity, database, realtime chat, or external backup providers. Do not infer business rules—such as whether “add people” means follow, friend, or request—from vague labels; find existing requirements or document the chosen, justified model.

## Evidence status

At keeper creation, no application source repository was supplied. The actual implementation, stack, and feature status remain unknown until the first-run audit.
