# Lease envelope + cross-lane joins

DeriveBSD standardizes **temporary authority** as *leases* (`docs/249-lease-registry-and-cross-lane-revocation.md`).

In practice, different lanes mint their own grant/session objects:
- portal grants
- secret grants
- breakglass grants
- debug/trace leases
- export actions

If each lane uses different field names and identifiers, operators lose the biggest advantage of the lease model: **one place to answer “what temporary power exists right now?”**

This doc introduces a small unifying object: `lease.envelope`.

## Design goal

- Keep lane-specific schemas stable.
- Create a single cross-lane *join table* with consistent identifiers and common metadata.
- Enable consistent tooling:
  - `lease ls` (active leases)
  - `lease revoke <lease_id>` (revocation evidence + fanout)
  - incident bundles that can include a minimal "authority context" snapshot

## `lease.envelope` (new)

A `lease.envelope` is **metadata only**:
- canonical `lease_id`
- time bounds (`created_at`, `expires_at`)
- issuer + subject selectors
- pointers to the lane object that actually grants authority (grant digest + kind)
- optional summary fields (non-sensitive)

See: `spec/lease.envelope.schema.json`.

## How envelopes are created

Two modes:

1. **Native**: the lane creates the envelope at grant issuance time.
2. **Synthesized**: the lease registry synthesizes an envelope from a lane grant object.

Either way, the envelope digest becomes the stable reference for:
- `lease.snapshot`
- incident bundles
- revocation events

## Migration strategy (keep it boring)

- Lane objects keep their existing `grant_id`/`session_id` fields.
- Lane objects SHOULD carry `lease_id` (already standardized in r45).
- Tooling builds `lease.envelope` records opportunistically:
  - if the lane provides one, store it
  - else synthesize it

This makes it safe to adopt incrementally.

## Revocation fanout

Revoking a lease means:

- record a `lease-revoke-event`
- perform lane-specific cleanup (close portal handles, stop trace sessions, withdraw secret delivery handles)

The envelope provides the minimal routing info:
- `lane`
- `target_kind`
- `target_digest`

## Composition with evidence spine

Leases are not just access control; they are *context*.

- For incidents: include a `lease.snapshot` (metadata-only) and optionally the referenced envelopes.
- For exports: bind the export attempt to a lease id and record it in `export.receipt`.

