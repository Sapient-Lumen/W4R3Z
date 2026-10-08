# spiffe-identity-kit lane boundaries — 2026-03-20

This note keeps **P-0134 spiffe-identity-kit** from collapsing into fake “supports SPIFFE/SPIRE” language.

A workload-identity support crate must keep at least these eight truths separate:

1. **where identity material comes from**,
2. **whether the identity path is X.509, JWT, or delegated**, 
3. **how credential freshness/rotation actually works**,
4. **which trust domains are accepted**,
5. **where peer authorization runs**,
6. **whether peer identity is exposed to application code**,
7. **what happens when the source becomes unavailable**, and
8. **what evidence can be shared safely after failure**.

## What belongs in this lane

The lane is about questions like:

- Is the workload using a live Workload API source, delegated identity, or a static dev/test identity?
- Do new handshakes use rotated SVIDs and bundles without restart?
- Under federation, are all bundle-set trust domains accepted, or only a reviewed allowlist?
- Does the app get a `PeerIdentity`, or is identity only enforced inside TLS verification?
- Is source loss handled as stale-but-running, fail-new-handshakes, or manual-review territory?
- Can the crate emit a redacted issue bundle without private keys or raw credentials?

## What does **not** belong here

Do **not** collapse this seam into:

- a new service mesh,
- a CA or secret-management platform,
- a general Rust TLS framework,
- a generic zero-trust policy engine,
- or a transport-agnostic “auth solved” slogan.

Those may contribute evidence, but this lane is specifically the receiver-facing contract for **identity source**, **trust-domain policy**, **peer handoff**, and **rotation/failure posture**.

## Preferred artifacts

If this lane keeps sharpening, prefer tiny artifacts such as:

- `identity-source.receipt.json`
- `trust-domain-policy.receipt.json`
- `peer-identity.receipt.json`
- `rotation-state.report.json`

The point is not to produce another identity stack.
The point is to make it reviewable whether a consumer is looking at:

- `workload_api_live_x509`,
- `spire_delegated_identity`,
- `static_dev_identity`,
- `any_in_bundle_set`,
- `allow_list`,
- `peer_identity_returned_to_app`,
- `verified_but_not_exposed`,
- or `watch_driven_live_rotation`.

## LLM/archive reminder

Do **not** let future passes rephrase this seam as:

- “Rust has SPIFFE crates now,”
- “mTLS is enabled, so identity is solved,”
- “the verifier checked the peer, so the app can obviously see it,”
- or “federation works by default, so trust-domain scope is obvious.”

The sharper missing value is a receiver-facing contract that says **what identity source is actually used, what trust-domain scope is accepted, whether peer identity is surfaced, and how freshness behaves under rotation and failure**.
