# RFC-0145: Portal sessions + permission store

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Portals solve dynamic capability acquisition, but real systems also need:
- long-lived **sessions** (screen share, remote control, global shortcuts)
- “remember my choice” without hidden, non-auditable state
- a coherent revocation + expiry story

If these are not standardized, apps and portal families diverge and users lose control.

## Proposal

Add two optional primitives:

1) **portal.session**: a signed receipt describing a long-lived portal session
- session_id, portal family, capset_digest
- expiry/lease linkage
- close semantics

2) **portal.permission.{grant,revoke}**: persistent, revocable “remember” records
- keyed by (app identity, portal family, resource_id, operations[])
- bound to request shape digest + prompt template digest
- includes constraints (TTL, max scope, redaction profile, etc.)

## Rationale

- Makes “remember” *policy-gated* and *auditable*
- Enables tooling (enumerate live sessions + stored permissions)
- Provides a portable contract for future portal families

## Compatibility

This is inspired by XDG Desktop Portal Request/Session conventions and the PermissionStore concept, but re-expressed as DeriveBSD evidence objects.

## Schemas

- `spec/portal.session.schema.json`
- `spec/portal.permission.grant.schema.json`
- `spec/portal.permission.revoke.schema.json`

## References

- Request: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html
- Session: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Session.html
- PermissionStore: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.PermissionStore.html
