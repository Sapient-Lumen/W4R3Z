# RFC-0133: Persistent file capabilities (“bookmarks”) for sandboxed apps

Status: draft

## Motivation

DeriveBSD is leaning into capability mode and portal-mediated access.
This solves *dynamic* access (user picks a file; portal returns an FD).

However, real applications require **persistable** access patterns:

- “recent documents” that reopen after restart
- background services that must continue indexing an approved directory
- long-running workflows where a helper process needs access later

Without a platform primitive, ecosystems fall back to ambient filesystem access or fragile path-based ACLs.

## Proposal

Introduce a first-class evidence object: `fs.bookmark`.

A bookmark is a **signed, policy-bound claim ticket** that allows a compartment to re-acquire a narrowly scoped file capability later via the portal.

Bookmarks are:
- persistable (safe to store)
- revocable (explicit evidence)
- scoped (rights + target)
- explainable (bind to portal grants and policy decision records)

## Evidence objects

### `fs.bookmark` (signed)

Schema: `spec/fs.bookmark.schema.json`.

Binds:
- `bookmark_id` (stable)
- request/grant binding (`portal_grant_digest` or `portal_request_digest`)
- scope descriptor (file or directory)
- rights (read/write/stat/exec/etc)
- optional `expires_at` (long TTL supported, but policy-controlled)
- an opaque `cap_ref_digest` (implementation-dependent; never expose raw tokens)

### `fs.bookmark.revoke` (signed)

Schema: `spec/fs.bookmark.revoke.schema.json`.

Binds:
- `bookmark_id`
- `revoked_at`
- reason + policy decision digest

## Runtime behavior

### Claim flow

To use a bookmark, a compartment calls the portal with:
- `bookmark_id`
- desired operation
- optional sub-scope (e.g. relative path within an approved directory)

If allowed, the portal returns:
- a fresh FD/handle with rights minimized
- a `portal.grant` (optionally lease-backed)

DeriveBSD does not need a dedicated `fs.bookmark.claim` evidence object in v0; the `portal.grant` and policy decision record are the claim receipts.

### Revocation

- User or policy can revoke a bookmark.
- After revocation, claims fail closed.
- If a bookmark was also backed by a lease/proxy, revocation must invalidate the mediated handle.

## Implementation strategies (non-normative)

Multiple implementations can fit the same evidence contract:

- token-backed (macOS-like)
- document-portal style exported view (FUSE-like)
- handle-backed using stable file identifiers where possible

## Open questions

- Do we need explicit bookmark “upgrade” (read → read/write) workflows?
- Should bookmarks be namespace-scoped (per-app) or user-scoped with policy constraints?
- How should bookmarks interact with ZFS send/recv and dataset moves (stable identity semantics)?

