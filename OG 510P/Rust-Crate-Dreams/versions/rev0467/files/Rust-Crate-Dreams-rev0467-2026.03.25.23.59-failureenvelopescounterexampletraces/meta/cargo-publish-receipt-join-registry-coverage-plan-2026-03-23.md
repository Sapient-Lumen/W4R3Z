# Cargo Publish Receipt Join registry-coverage plan — 2026-03-23

This note deepens **P-0477 Cargo Publish Receipt Join Kit** around one product question:

> what exact post-publish artifacts should another maintainer receive so local bytes, publish identity, registry capabilities, registry protection scope, and public visibility do not collapse into one fake “publish succeeded safely” story?

## Product stance

The crate should stay **post-publish, receiver-facing, and conservative**.
It should not become:

- a multi-registry publish orchestrator,
- a moderation backend,
- a malware scanner,
- or a provenance/attestation system.

Its job is to emit a compact pack that answers:

- what local package artifact the joined receipt is based on,
- which registry lane was used,
- what that registry can actually tell us,
- what protective claims were genuinely in scope for that lane,
- what visibility is still partial,
- and what still requires manual review.

## New first-class artifacts

### `registry-capability.receipt.json`

For one registry lane, record at least:

- `registry_name`
- `registry_url_class`
- `publish_route`
- `index_observation_support`
- `checksum_visibility`
- `pubtime_visibility`
- `trusted_publishing_support`
- `trusted_publishing_only_visibility`
- `docs_surface_coupling`
- `publish_notification_visibility`
- `malware_advisory_channel`
- `notes`

This keeps “Cargo can publish there” separate from “this registry exposes the same operational and security facts as crates.io”.

### `protection-scope.report.json`

For one release lane, record at least:

- `registry_name`
- `client_version_window`
- `upload_blocking_scope`
- `historical_audit_scope`
- `advisory_visibility_scope`
- `trusted_publishing_protection_scope`
- `crates_io_specific_mitigation`
- `alternate_registry_unknowns`
- `verdict`
- `manual_review_reasons`

This keeps “a crates.io mitigation exists” separate from “our release lane was protected”.

### `publish-join-bundle.manifest.json`

For one exported pack, record at least:

- subject package/version,
- included receipts/reports,
- required-for-review subset,
- registry capability receipt path,
- protection-scope report path,
- identity/visibility paths,
- share posture,
- and manual-review gaps.

This keeps “we zipped some publish artifacts” separate from “we exported an honest joined release bundle”.

## CLI / workflow refinement

### `cargo publish-join capture`
Should be able to emit local/capture/registry/identity slices plus optional registry-capability and protection-scope artifacts.

### `cargo publish-join explain`
Should render warnings such as:

- `crates_io_feature_not_observed_on_selected_registry`
- `trusted_publishing_identity_known_but_registry_capability_partial`
- `advisory_channel_known_only_for_crates_io`
- `client_version_window_outside_mitigation_scope`
- `alternate_registry_vendor_confirmation_required`

### `cargo publish-join bundle`
Should emit `publish-join-bundle.manifest.json` plus the underlying receipts/reports rather than assuming the joined zip explains itself.

## Good first scenario families

1. **crates.io enrichments and TP-only posture do not automatically transfer to an alternate registry lane**
2. **crates.io upload blocking / audit coverage do not prove alternate-registry protection scope**
3. **a portable bundle must keep bytes, identity, registry capability, protection scope, and visibility separate**

## Boundary reminders

Keep **P-0477** separate from:

- **P-0175** for preflight trusted-publishing route identity,
- registry-auth doctor work for login / credential-provider failures,
- crate-health / trust-lens work for long-horizon trust signals,
- and attestation/provenance work for signed artifact lineage.

## Sources

- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
