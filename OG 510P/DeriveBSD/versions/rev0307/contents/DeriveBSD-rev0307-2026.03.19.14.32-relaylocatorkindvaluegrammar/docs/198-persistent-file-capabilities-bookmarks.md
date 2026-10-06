# Persistent file capabilities (“bookmarks”) for sandboxed apps

Portals make **one-time** dynamic access possible in capability mode (user picks a file, portal returns an FD).

But real programs often need **persistent** access:
- reopen “recent documents” after restart
- background indexing / sync of previously approved folders
- workflows that span processes (editor → helper → renderer)

If we don’t provide a first-class pattern here, ecosystems regress to ambient filesystem access.

This doc proposes a DeriveBSD primitive: **persistent file capabilities** (“bookmarks”).

## Lessons to steal

Two existing patterns are worth baking into DeriveBSD’s ground floor:

- **macOS security-scoped bookmarks**: the app stores an opaque bookmark token representing user-approved access, then later re-resolves it and calls `startAccessingSecurityScopedResource()` to regain sandbox access.
- **XDG Document Portal**: the host exports selected files into a per-user, restricted view (FUSE-mounted) that sandboxed apps can access; access is mediated and revocable.

References:
- Apple App Sandbox file access: https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox
- `startAccessingSecurityScopedResource()`: https://developer.apple.com/documentation/Foundation/URL/startAccessingSecurityScopedResource%28%29
- XDG Documents portal spec: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Documents.html

## What “bookmark” means in DeriveBSD

A **bookmark** is a *signed, policy-bound* object that lets a compartment re-acquire a **narrow file capability** later, without ambient path opens.

The bookmark itself is **not** a raw capability; it is a claim ticket.
To use it, the requester must call the portal/broker and exchange it for a fresh FD/handle with rights-minimization applied.

Key properties:
- **persistable**: safe to store in app state
- **revocable**: user or policy can disable it
- **scoped**: describes *what* is accessible (file/folder) and *how* (rights)
- **evidence-bearing**: issuance, claim, and revocation are all receipted

## Why bake this in early

- It removes the biggest ergonomic reason capability mode gets abandoned: “I can’t reopen my files.”
- It gives DeriveBSD a unified story for desktop-style “recent documents” *and* server-style persistent grants.
- It makes revocation and audit receipts part of the platform rather than ad-hoc app state.

## Proposed contract (v0)

### 1) Portal issues a bookmark

After an interactive file selection (or explicit policy-only approval), the portal may mint `fs.bookmark`:

- binds to a `portal.grant` (or the request digest)
- records **rights + scope**
- includes an **opaque capability reference digest** (implementation-dependent)
- assigns a stable `bookmark_id`

Schema: `spec/fs.bookmark.schema.json`.

### 2) App claims a bookmark to get a fresh FD

To reopen, a compartment submits:

- `bookmark_id`
- requested operation (read/write/exec/stat)
- optional sub-scope (e.g. relative path within an approved directory)

Portal returns:
- a fresh FD/handle with rights minimized
- a normal `portal.grant` (optionally with a `lease_id`)

(If desired, DeriveBSD can also define a small `fs.bookmark.claim` receipt, but v0 can reuse `portal.grant` + standard policy decision records.)

### 3) Revocation

Revocation must be explicit and evidence-bearing:

- emit `fs.bookmark.revoke`
- future claims fail closed

Schema: `spec/fs.bookmark.revoke.schema.json`.

### 4) Implementation strategies (non-normative)

DeriveBSD should allow multiple implementations under the same evidence shape:

- **token-backed** (macOS-like): portal stores or derives opaque per-bookmark data; apps store only `bookmark_id`.
- **document-portal style**: portal exports chosen files into a restricted view namespace; bookmark stores the exported file id.
- **handle-backed** (advanced): on systems with stable file handles, portal can map bookmark → file handle + mount identity.

## Threat model notes

- Bookmark storage is not a privilege escalation: without a portal claim, the bookmark is inert.
- Claims are subject to policy and can require fresh consent (e.g., after TTL, after policy snapshot change).
- Prefer **directory capabilities + relative opens** over path strings.
- For write access, require stronger UI wording + explicit receipts.

## Integration points

- Portals: `docs/179-portals-and-powerbox.md`
- Leases + revocation: `docs/182-capability-leases-and-revocation.md`
- Consent + audit receipts: `docs/185-portal-consent-and-audit-receipts.md`
- Capability routing manifests (apps declare “I will request bookmarks”): `docs/140-capability-routing-manifests.md`

Last updated: 2026-02-24
