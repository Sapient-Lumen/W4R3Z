# Verification matrix (what gets checked, when)

This is the minimal checklist DeriveBSD must satisfy end-to-end.

For the “day-0 defaults” view, see:
- `docs/97-non-negotiable-behaviors.md`

## Spec → Lock
- resolve sources to immutable identities (commit, digest)
- record hashes for every fetched input

## Lock → Plan
- policy evaluation produces a **policy decision record** (`docs/93-policy-decision-records.md`)
  - record is hashed (JCS) and stored as a content-addressed object
  - policy may require a signature by a policy authority key
- environment normalization is explicit (time/locale/tz)
  - if policy requires trustworthy time, emit `time.evidence.json` and enforce last-known-good time monotonicity (see `docs/142-trustworthy-time-roughtime.md`)

## Plan → Artifact
- sandbox on, network denied (except declared fetchers)
- enforce **store view minimization** for builders: only declared store objects in the input closure are visible; emit `storeview.manifest` bound into the Plan digest (see `docs/152-store-view-minimization.md`)
- outputs emitted into the store as **digest-identified objects** (`docs/56-store-layout-and-digests.md`)
- emit provenance bound to artifact digest
- optional: emit SBOM as a signed `sbom.statement` and (when vuln gates are enabled) a companion `vex.statement` bound to policy snapshot (see `docs/168-sboms-and-vex-as-evidence.md`)
- optional: run deterministic vulnerability queries against a pinned `vuln.db.snapshot` and emit `vuln.query.receipt` + `vuln-gate-receipt` when policy enables gating (see `docs/60-vulnerability-intel-and-gates.md`)
- emit a Build Record (buildinfo-like) for high-value artifacts (binds Plan+capsule+toolchain) (see `docs/141-build-records-buildinfo-and-rebuilders.md`)
- optional: require witness rebuild attestations for promotion (see `docs/116-witness-rebuilders-diffoscope.md`)
- optional: run a reproducibility variation harness (reprotest-like) and emit `repro.check.json` + diff reports for triage; allow “stabilized equivalence” only when policy explicitly permits it (see `docs/148-reproducibility-variation-harness-reprotest.md`)
- optional: run artifact/workload test suites in a dedicated runner (jail or microVM) and emit a digest-bound `test.receipt` for promotion gates (see `docs/166-test-receipts-and-promotion-gates.md`)

## Cache / Distribution
- mirrors are untrusted; only consume artifacts after:
  - digest verification
  - signature verification (trust-policy selected keys)
  - if signatures were produced via a crypto-domain, verify the corresponding `crypto.op.receipt` objects and policy bindings (see `docs/164-split-crypto-domains.md`)
  - required attestations (trust-policy)
  - channel metadata checks if using channels (anti-freeze/rollback)
  - if policy requires transparency evidence:
    - require Sigsum inclusion proof bundles (`docs/131-sigsum-lightweight-transparency.md`)
    - and/or require SCITT receipts (`docs/132-scitt-ledger-receipts.md`)
  - if consuming patchsets: require signature, target binding, and expiry/revocation checks (see `docs/113-syspatch-style-patchsets.md`)
  - if consuming ZFS streams: treat stream as an Artifact; quarantine → verify → promote (see `docs/126-zfs-send-distribution.md`)
  - if ZFS native encryption is enabled by policy, require key-use evidence for load/unload/change events and keep key material out of the store (see `docs/146-zfs-native-encryption-for-generations.md`)
  - if consuming offline bundles: treat bundle as an Artifact container; verify → unpack in quarantine → verify contents → promote (see `docs/138-offline-signed-update-bundles.md`)
  - if consuming delta artifacts: require from/to binding + platform constraints; fall back to full objects if missing (see `docs/139-bandwidth-efficient-deltas.md`)
    - if stream is bookmark-based or redacted, require explicit labeling + evidence (see `docs/130-zfs-bookmarks-and-redaction.md`)

## Activation / Launch
- verify policy decision record digest/signature (if required)
- compute closure manifest + require closure proof (`docs/90-closure-proof.md`)
- enforce store immutability invariants at activation/launch: store mounted read-only from snapshots; optionally emit `store.integrity.report` (see `docs/153-store-immutability-and-toc-tou.md`)
- enforce derived capability routing grants for each compartment (jail/microVM/service-jail) (see `docs/140-capability-routing-manifests.md`)
- optional: if a target declares `abi_profile: cheri-*`, enforce host/guest compatibility constraints before launch (see `docs/163-cheri-capability-lane.md`)
- switch atomically (host) or replace-image (microVM)
- microVM launch MUST declare device roles (base/private/volatile) when using template layering (see `docs/129-template-microvms-and-disposables.md`)
- host switching is tentative until a health gate passes; emit a `boot.health.report` object (see `docs/112-health-gated-updates.md`)
- optional: if rollback indices are enabled by policy, check monotonic rollback index before activation and advance it only after health success (see `docs/137-anti-rollback-rollback-index.md`)
- optional: if policy requires measured boot attestation, require a boot.attestation object (and optionally a verifier receipt) bound to the deployed generation before promoting/activating (see docs/176-measured-boot-attestation.md)

## Explain

`derive explain` is only authoritative when based on verified evidence:

- default: emit `unverified` status if verification fails
- `--require-verified`: fail hard

See: `docs/95-explainability-contract.md`.

## Rollback
- host rollback via ZFS boot environments (`docs/69-host-generations-bectl.md`)
- workload rollback via previous bundle digest (`docs/35-workload-rollout-rollback.md`)

Pointers:
- verification rules: `adrs/ADR-0009-artifact-verification.md`
- trust/caches: `docs/46-cache-trust-model.md`
- trust policy schema: `spec/trust.policy.schema.json`

Last updated: 2026-02-24

## Additions
- **antirollback.check** (auto path) and **manualRollbackOverride** (manual path) must be bound into Plan.
- **bootstrap.evidence** required for first activation.
- **toolchain.bundle** + **toolchain.buildrecord** required for builder images.
- **ports.impurity.class** recorded for adapter lane outputs.
