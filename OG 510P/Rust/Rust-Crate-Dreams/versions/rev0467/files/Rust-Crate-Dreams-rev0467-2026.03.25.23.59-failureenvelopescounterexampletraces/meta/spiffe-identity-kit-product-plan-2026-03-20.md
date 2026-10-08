# spiffe-identity-kit — product plan (2026-03-20)

This note sharpens **P-0134 spiffe-identity-kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to replace the current SPIFFE Rust crates, become a mesh control plane, or hide zero-trust decisions behind one “secure” badge.
It should be a **small crate family plus CLI** that helps teams publish one reviewable answer to:

- where workload identity comes from,
- how credential freshness/rotation really works,
- which trust domains are accepted,
- whether peer identity is handed to application code,
- and what portable redacted evidence exists when issuance or mTLS fails.

The missing value is the **boring workload-identity contract layer** above today’s real substrate: official SPIFFE specs, `spiffe` Workload API watchers, `spiffe-rustls` builders, `spiffe-rustls-tokio` peer extraction, and `spire-api` delegated identity.

## What the crate should provide other people

For service teams, platform/security teams, library authors, and incident reviewers, the crate should provide:

1. **One identity-source receipt** instead of “this service uses SPIFFE somewhere”.
2. **One trust-domain-policy receipt** instead of vague federation posture.
3. **One peer-identity receipt** instead of guessing whether the app can actually see the authenticated peer.
4. **One rotation-state report** instead of hand-waving about live reload or automatic rotation.
5. **One compact debug bundle** instead of ad hoc logs and screenshots from failed mTLS incidents.

## Four first-class review objects

### 1. Identity-source receipt

Named classes for `0.1` should focus on source basis such as:

- `workload_api_live_x509`
- `workload_api_live_jwt`
- `spire_delegated_identity`
- `static_dev_identity`
- `manual_review_required`

This object should answer:

- whether the workload gets identity directly from the Workload API or via SPIRE delegation,
- whether the surface is X.509, JWT, or mixed,
- which transport/endpoint class is in use,
- and whether the source is expected to rotate automatically.

### 2. Trust-domain-policy receipt

Named classes for `0.1` should focus on bundle-acceptance posture such as:

- `any_in_bundle_set`
- `allow_list`
- `local_only`
- `application_narrowed`
- `manual_review_required`

This object should answer:

- whether federation is effectively enabled by accepting all bundle-set domains,
- whether the app narrows to a reviewed allowlist,
- whether only the local trust domain is accepted,
- and whether peer-ID authorization is stricter than raw bundle acceptance.

### 3. Peer-identity receipt

Named classes for `0.1` should focus on handoff/visibility such as:

- `peer_identity_returned_to_app`
- `peer_identity_available_in_middleware`
- `verified_but_not_exposed`
- `authorization_only`
- `manual_review_required`

This object should answer:

- whether peer SPIFFE IDs are surfaced after handshake,
- whether the handoff occurs in `tokio-rustls`, `tower`, or app-level middleware,
- whether authorization happens post-verification or only implicitly in the verifier,
- and whether downstream code can log, route, or audit on peer identity.

### 4. Rotation-state report

Named classes for `0.1` should focus on freshness/runtime posture such as:

- `watch_driven_live_rotation`
- `new_handshakes_use_updated_material`
- `source_loss_blocks_new_material`
- `static_until_restart`
- `manual_review_required`

This object should answer:

- whether the subject relies on watch-driven updates,
- whether new handshakes pick up rotated SVIDs/bundles,
- whether current connections stay valid while the source is unavailable,
- and whether restart/rebuild is required to adopt new identity material.

## Recommended `0.1` command surface

### `cargo spiffe-surface capture`
Capture workload-identity posture and emit:
- `identity-source.receipt.json`
- `trust-domain-policy.receipt.json`
- `peer-identity.receipt.json`
- `rotation-state.report.json`

### `cargo spiffe-surface check`
Run conservative coherence checks and emit:
- `spiffe-surface-check.report.json`

### `cargo spiffe-surface explain`
Render a human-readable summary of the decisive source, policy, peer-handoff, and rotation findings.

### `cargo spiffe-surface diff`
Compare two captures across release/deployment/config changes.

### `cargo spiffe-surface bundle`
Produce one compact `.spiffesurfacebundle.zip` containing reports, notes, and selected imports.

## Recommended crate/workspace split

- `spiffe_surface_model`
- `spiffe_surface_capture`
- `spiffe_surface_check`
- `cargo-spiffe-surface`

## `0.1` artifact set

Core artifacts should be:
- `spiffe-surface.toml`
- `identity-source.receipt.json`
- `trust-domain-policy.receipt.json`
- `peer-identity.receipt.json`
- `rotation-state.report.json`
- `spiffe-surface-check.report.json`
- `spiffe-notes.summary.md`

## Discovery order

1. **Import source basis**
   - `spiffe` / `spire-api` usage and config
   - Workload API endpoint type and source mode
   - X.509 vs JWT path
2. **Import trust-domain posture**
   - federation bundle availability
   - `AnyInBundleSet` / allowlist / local-only style narrowing
   - peer-ID authorizer basis
3. **Import peer handoff surface**
   - whether `PeerIdentity` is returned
   - where authorization runs relative to cryptographic verification
   - whether app code can see the authenticated peer
4. **Import freshness/rotation posture**
   - watcher/reconnect behavior
   - handshake freshness claims
   - source-loss/runtime caveats
5. **Render conservative checks**
   - reject claims that flatten static identities into live ones
   - reject claims that flatten verifier-only auth into app-visible peer identity
   - reject claims that flatten bundle-set acceptance into reviewed allowlists

## Ranking discipline

A good `0.1` should not let “supports SPIFFE” become the contract.
It should keep separate:

- `identity_source_known`
- `trust_domain_scope_known`
- `peer_handoff_known`
- `rotation_posture_known`
- `source_loss_posture_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- SPIFFE Workload API and federation semantics
- `spiffe` watcher/reconnect/rotation support
- `spiffe-rustls` authorizer and trust-domain policy surfaces
- `spiffe-rustls-tokio` peer-identity extraction
- SPIRE Delegated Identity support where present

### Do not flatten into one fake verdict
- “the service uses SPIFFE”
- “rotation is automatic”
- “peer identity is verified”
- “federation works”
- “mTLS is enabled”

The point is to publish a small, reviewable answer to **where identity comes from, who is trusted, what the app can see, and how freshness behaves under rotation and failure**.
