# 182 — Receipt profiles and mappings (SCITT/CT/custom)

**Track:** Shared

## Goal
Receipts prove that a statement/envelope was **submitted and/or included** in a
transparency service. Different ecosystems use different receipt families.

This archive stays profile-agnostic in core schemas, but it still needs:

- a registry of recognized receipt profiles (so examples and tools don't drift),
- mapping guidance for how to interpret receipts at a coarse level (acknowledged vs included),
- a semantics-tiers note (see `docs/185`) for stronger distinctions,
- a clear line between **presence checks** (offline) and **semantic verification** (profile-specific).

## Registry
- `artifacts/registries/receipt-profiles.csv`

A `TransparencyReceipt` may set:
- `receipt_type` in {`scitt`, `ct`, `custom`}
- `profile` (string, optional but recommended for interop)

Tools SHOULD warn on unknown `profile`.

## SCITT family (receipt_type = scitt)
SCITT drafts describe transparency services and receipt profiles (often COSE-based).

Mapping guidance (coarse):
- `receipt_semantics = acknowledged` means “the service accepted submission”
- `receipt_semantics = included` means “the service commits the entry into a verifiable structure”

The exact fields are profile-specific; this archive stores profile-native receipts as detached JSON blobs.

## CT family (receipt_type = ct)
Certificate Transparency-style receipts focus on inclusion and consistency proofs,
and are typically paired with gossip to detect split views.

Again: the payload is stored as a detached JSON blob; the archive cares that it is
portable, bound to the envelope, and can be compared across audiences.

## Custom
Allowed for research, but Track A SHOULD name the profile and document semantics.

## References
See the links pinned in `docs/references.md` and the sources lockfile.


## Related
- `docs/185` Receipt semantics tiers


## Notes on SCITT receipt work (freshness)

The SCITT working group has a standards-track receipt profile draft for COSE receipts with CCF (`draft-ietf-scitt-receipts-ccf-profile`), which is relevant as an interoperability reference when defining `receipt_profile` identifiers in this archive.
