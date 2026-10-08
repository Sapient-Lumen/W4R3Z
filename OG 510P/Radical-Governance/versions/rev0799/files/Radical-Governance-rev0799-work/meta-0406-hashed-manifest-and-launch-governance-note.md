# Meta 0406 — hashed manifest and launch-governance increment

## What changed

This revision adds three tightly related notes around:

- executable interoperability through reference implementations and conformance testing,
- visible trust and capability registries for shared ecosystems,
- federated launch rehearsals before mandatory or consequential shared go-live.

It also upgrades the machine-readable manifest so entries carry SHA-256 hashes and byte sizes, making continuation bundles easier to verify, compare, and merge.

## Why this matters

The archive has now moved one layer beyond “publish standards” and “publish registries.” It now asks whether a public ecosystem has:

- executable proof of interoperability,
- a real trust layer rather than ad hoc whitelisting,
- launch evidence from independent participants,
- integrity metadata strong enough to support later merging.

## Merge guidance

When merged into the larger archive, cross-link:

- `412` with narrow-waist governance, interoperability assessments, and diffable rules,
- `413` with delegated authority, registries, trust services, and certification notes,
- `414` with incident command, public deployment registries, and migration/change-window notes.

Keep the hashed manifest even if the full archive later moves to stronger provenance tooling.
