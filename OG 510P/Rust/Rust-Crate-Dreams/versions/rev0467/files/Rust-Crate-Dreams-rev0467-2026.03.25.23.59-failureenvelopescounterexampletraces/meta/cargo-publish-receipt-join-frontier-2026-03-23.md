# Cargo Publish Receipt Join frontier — 2026-03-23

This pass deepens **P-0477 Cargo Publish Receipt Join Kit** instead of opening another release helper, another registry trust score, or another publish dashboard.

## Main judgment

The sharper missing layer is now **registry coverage honesty**.

Rust publishing increasingly spans:

- crates.io-specific enrichments such as `pubtime`, trusted-publishing-only posture, blocked-trigger policy, and publish notifications,
- alternate registries that Cargo can target but that may not expose the same APIs, moderation posture, or operational safeguards,
- and release workflows where a maintainer wants one joined receipt without pretending every registry lane has crates.io-grade visibility or mitigations.

The current Cargo advisory makes this especially concrete.
crates.io deployed an upload-side mitigation on March 13, 2026 and audited all previously published crates, but the advisory also says alternate-registry users need to verify their exposure with the registry vendor and that older Cargo on alternate registries may remain vulnerable even after Rust 1.94.1 ships.
That means the missing crate is not just a receipt joiner.
It is a receipt joiner that can publish **which registry lane was in play**, **which protections/capabilities were actually observed**, and **where the review must stop**.

## Receiver-facing artifacts worth promoting now

### `registry-capability.receipt.json`
A compact statement of what the selected registry lane actually exposes and what is only inferred or unavailable.
For `0.1`, record at least:

- registry name / url class,
- index-observation posture,
- `pubtime` support,
- trusted-publishing support class,
- trusted-publishing-only visibility,
- docs/public-surface coupling posture,
- publish-notification visibility,
- malware/advisory watch posture,
- and notes on provider / host / vendor limits.

### `protection-scope.report.json`
A compact statement of what protective claims were really in scope for this lane.
For `0.1`, keep separate:

- upload blocking,
- post-hoc audit coverage,
- advisory/public-notification coverage,
- client-version caveats,
- crates.io-only mitigations,
- alternate-registry unknowns,
- and manual-review requirements.

### `publish-join-bundle.manifest.json`
The first file another maintainer should open.
It should inventory local-package receipts, capture-basis receipts, registry capability/protection receipts, identity reports, visibility reports, and notes without pretending that copied artifacts are self-explanatory.

## Why this is worth doing

This lane is valuable because current Rust workflows can now honestly say all of the following at once:

- “the bytes matched,”
- “trusted publishing was used,”
- “the index entry was observed,”
- and still **not** know whether a crates.io-specific mitigation or advisory channel applied to the registry lane actually used.

A worthy crate contribution here gives other people a boring, reviewable answer instead of letting those claims blur together.

## Boundary reminder

Keep this lane separate from:

- **P-0175 Trusted Publishing Tooling Kit** — preflight / workflow-route identity before publish,
- registry-auth doctor work — client-side credential failures,
- malware-notification or moderation systems,
- provenance / attestation systems,
- and generic dependency-trust dashboards.

## Sources

- https://doc.rust-lang.org/cargo/reference/registries.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
