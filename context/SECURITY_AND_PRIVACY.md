# Security and Privacy Context

This document states non-negotiable design constraints for the intended multi-user application. It does not claim that the current code already satisfies them.

## Identity and authorization

- Establish user identity through the configured trusted authentication flow; never accept a client-supplied email, user ID, role, provider profile object, or public identifier as proof of identity.
- Keep private provider credentials and privileged keys out of browser code, committed files, logs, prompts, and context documents.
- Enforce access control at trusted backend/service boundaries for every sensitive operation; hiding a button is only a UI convenience.
- Test unauthorized/direct-call cases for admin, moderator, account management, private data, messaging, reports and backups.
- Do not allow editable cosmetic tags (`owner`, `admin`, `paid`, etc.) to grant real permissions.
- Never display or retrieve an existing password for an admin. Use reset/invitation/recovery workflows.

## Data isolation and minimization

- Every user-owned record needs a clear owner and access rule. Prevent one user from reading or modifying another user's private records.
- Search and public IDs should expose only approved public data and should resist enumeration where appropriate.
- Keep only data needed for a feature. Protect messages, reports, backups, tokens and account data. Avoid placing real records in test fixtures or memory files.
- Document deletion semantics, retention, cascades, restore effects and recovery constraints. Soft deletion, trashing and permanent deletion are distinct states.

## Location and profile privacy

- Location/nearby features are opt-in and explain what is shared.
- Private settings or missing/revoked permission must affect backend eligibility/results, not just hide information in the UI.
- Use the least precise, shortest-lived location representation that satisfies the purpose. Do not add covert/background location tracking or log raw precise coordinates without a clear need.
- Profile QR codes encode a stable public route/identifier, never session tokens, passwords, private database keys or unnecessary sensitive information.

## Moderation, account protection and abuse controls

- Validate permissions and audit high-impact admin/moderation actions without logging secrets or unnecessary private content.
- Protect report review notes and evidence from reporters and unauthorized users.
- Prevent duplicate/spam submissions and rate-limit automated search/auth abuse where appropriate.
- Account lockout/rate limiting must not become an easy denial-of-service vector against an innocent account; recovery must remain possible.

## Subscription and backup controls

- Subscription status is separate from role/tag labels. Trusted records/webhooks/configured provider confirmation—not a browser flag—must determine paid entitlements.
- Do not store card numbers or payment secrets in the app.
- Protect backups separately from the regular user session where appropriate. Authorize/audit restores, validate data and version, make a recovery point before destructive replacement, and do not report provider success before confirmation.
- Never silently overwrite production data from an unverified backup.

## Implementation and evidence checklist

For relevant changes, establish: trust boundary; owner/role rule; validation; permitted and denied paths; privacy effect; logs/audit trail; recovery/rollback; test evidence; and any configuration/owner action still needed. If any element cannot be verified, report it as a gap rather than a pass.
