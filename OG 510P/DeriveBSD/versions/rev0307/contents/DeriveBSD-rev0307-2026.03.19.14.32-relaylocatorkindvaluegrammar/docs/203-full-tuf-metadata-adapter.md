# Full TUF metadata adapter (optional)

DeriveBSD adopts TUF’s *client-side invariants* in a minimal form (`docs/61-channel-metadata-tuf-inspired.md`).

There’s also a strong “ecosystem leverage” argument for optionally supporting **full TUF metadata**:

- interoperability with existing TUF tooling and repositories
- robust delegation patterns for community repositories
- a well-studied update flow that resists rollback/freeze/mix-and-match attacks

References:
- TUF spec (latest): https://theupdateframework.github.io/specification/latest/
- TUF security overview: https://theupdateframework.io/docs/security/
- Delegations primer (FAQ): https://theupdateframework.io/docs/faq/

## DeriveBSD direction

Add an **adapter lane** that can:

1) **Publish** DeriveBSD channel views as a TUF repository:
   - map `channel.root/snapshot/timestamp/targets` onto TUF roles
   - encode targets metadata that references Derive artifact digests (closure proofs stay Derive-native)
   - optionally use TUF delegations for “ports-like” community repositories (split trust by subtree)

2) **Ingest** upstream TUF repositories:
   - verify TUF roles as specified
   - translate the accepted snapshot/targets set into a DeriveBSD `channel view` object
   - emit Derive evidence explaining which TUF files were used and why acceptance succeeded

## Important boundary

TUF handles “what is current and signed” for a repository.
DeriveBSD still decides “what is allowed” via `trust.policy` + policy decision records.

The adapter lane exists so that:
- DeriveBSD doesn’t reinvent delegation/witnessed key rotation logic
- communities can reuse proven repository practices

See also:
- `docs/61-channel-metadata-tuf-inspired.md`
- `docs/127-uptane-director-targets.md`

Last updated: 2026-02-24
