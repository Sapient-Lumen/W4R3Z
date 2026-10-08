# Frontier salience snapshot — 2026-03-20 (115)

This pass did **not** open another auth framework, another TLS abstraction, or another mesh-control-plane ambition.
It deepened **P-0134 spiffe-identity-kit** by making another product-critical truth explicit:

- **“supports SPIFFE/SPIRE” is still too vague unless the crate can say where identity comes from, which trust domains are actually accepted, whether peer identity is surfaced to the application, and how rotation/failure posture really behaves.**

## Main judgment

The sharper missing layer is no longer merely “a Rust SPIFFE client” or “Rustls integration for SPIFFE.”
The sharper missing layer is a **crate-authored identity-source / trust-domain-policy / peer-identity / rotation-state kit**.

The current Rust and SPIFFE substrate now makes that specific:

1. Official SPIFFE docs now point Rust users to `spiffe` for Workload API access and `spiffe-rustls` for TLS/mTLS integration.
2. The `spiffe` crate now exposes high-level `X509Source` and `JwtSource` watchers with automatic reconnection and rotation handling.
3. `spiffe-rustls` builds `rustls` configs backed by live `X509Source` data, so new handshakes can adopt rotated SVIDs/bundles without restart.
4. `spiffe-rustls` also makes trust-domain and peer-ID authorization explicit, including federation-aware trust-domain policy.
5. `spiffe-rustls-tokio` now exposes `PeerIdentity` at the Tokio accept/connect layer rather than keeping identity only inside verifier internals.
6. `spire-api` now covers SPIRE’s Delegated Identity API, making non-direct issuance a real Rust surface rather than a hypothetical extension.
7. The SPIFFE core and Workload API specs make clear that the Workload API is typically a local endpoint with caller authenticity verified out-of-band, which makes source basis and endpoint posture materially important.
8. The SPIFFE federation spec makes clear that accepting other trust domains is a separate review surface from basic same-domain mTLS.

That means the next worthy move is not “another Rust SPIFFE wrapper.”
It is one conservative crate family that can publish:

- **identity-source truth**,
- **trust-domain-policy truth**,
- **peer-identity handoff truth**,
- **rotation-state truth**,
- and **redacted debug-bundle truth**.

## Why this beat nearby work

The archive already had adjacent lanes for:

- general trust/risk posture (**P-0017**),
- supply-chain identity and maintenance signals,
- workload identity as a broad territory-map item,
- and generic auth/networking integrations.

What it still lacked was one compact way to say:

- “this service uses a live Workload API X.509 source, not a static dev identity,”
- “new handshakes pick up rotations, but current connections remain on older material,”
- “the app only trusts a narrowed domain allowlist, not the whole bundle set,”
- and “the peer SPIFFE ID is returned to application code rather than disappearing into verifier-only logic.”

That is a real receiver-facing product boundary, not just more zero-trust enthusiasm.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still strongest among release-support lanes because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still unusually strong because current registry/advisory/audit substrate makes reviewable trust posture more buildable.
4. **P-0028 open-table-format-kit** — remains stronger after the last pass because Rust lakehouse substrate now exists but the reviewable contract above it is still missing.
5. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown phase/aftermath truth cuts across async frameworks.
6. **P-0134 spiffe-identity-kit** — materially stronger after this pass because Rust now has real SPIFFE substrate, but the reviewable workload-identity contract above it is still missing.
7. **P-0027 text-input-kit** — still unusually strong because edit-path, geometry, and accessibility-mirror truth cut across toolkits.
8. **P-0011 Crate Health Contract Kit** — still strong because maintainer/support posture remains distinct from trust/risk posture.

## What changed in the archive

Added:
- `entries/2026-03-20-295.md`
- `meta/frontier-salience-2026-03-20-115.md`
- `meta/spiffe-identity-kit-product-plan-2026-03-20.md`
- `meta/spiffe-identity-kit-lane-boundaries-2026-03-20.md`
- `fixtures/spiffe-identity-kit/README.md`
- `fixtures/spiffe-identity-kit/identity-source.receipt.schema.json`
- `fixtures/spiffe-identity-kit/trust-domain-policy.receipt.schema.json`
- `fixtures/spiffe-identity-kit/peer-identity.receipt.schema.json`
- `fixtures/spiffe-identity-kit/rotation-state.report.schema.json`
- `fixtures/spiffe-identity-kit/scenarios/agent_backed_x509_source_and_static_dev_identity_must_not_share_rotation_claims/README.md`
- `fixtures/spiffe-identity-kit/scenarios/agent_backed_x509_source_and_static_dev_identity_must_not_share_rotation_claims/identity-source.receipt.example.json`
- `fixtures/spiffe-identity-kit/scenarios/agent_backed_x509_source_and_static_dev_identity_must_not_share_rotation_claims/rotation-state.report.example.json`
- `fixtures/spiffe-identity-kit/scenarios/federated_bundle_allowlist_and_local_only_policy_must_not_share_peer_acceptance_claims/README.md`
- `fixtures/spiffe-identity-kit/scenarios/federated_bundle_allowlist_and_local_only_policy_must_not_share_peer_acceptance_claims/trust-domain-policy.receipt.example.json`
- `fixtures/spiffe-identity-kit/scenarios/federated_bundle_allowlist_and_local_only_policy_must_not_share_peer_acceptance_claims/peer-identity.receipt.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/spiffe-identity-kit.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy workload-identity contribution for Rust should now provide more than protocol correctness and more than one live TLS demo.
It should provide:

- one explicit **identity-source receipt**,
- one explicit **trust-domain-policy receipt**,
- one explicit **peer-identity receipt**,
- one explicit **rotation-state report**,
- and one compact way to diff those artifacts across releases and deployment modes.

That is a better answer to the current ecosystem than either:

- “just use the SPIFFE crates,”
- “just wire rustls to the agent,”
- or “just document the trust domains and hope the rest is obvious.”

## Freshness anchors

- SPIFFE library usage page — https://spiffe.io/docs/latest/deploying/libraries/
- SPIFFE core spec — https://spiffe.io/docs/latest/spiffe-specs/spiffe/
- SPIFFE Workload API spec — https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/
- SPIFFE Federation spec — https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/
- `spiffe` crate docs — https://docs.rs/crate/spiffe/latest
- `spiffe-rustls` crate docs — https://docs.rs/spiffe-rustls/latest/spiffe_rustls/
- `spiffe-rustls-tokio` crate docs — https://docs.rs/spiffe-rustls-tokio/latest/spiffe_rustls_tokio/
- `spire-api` crate docs — https://docs.rs/crate/spire-api/latest
