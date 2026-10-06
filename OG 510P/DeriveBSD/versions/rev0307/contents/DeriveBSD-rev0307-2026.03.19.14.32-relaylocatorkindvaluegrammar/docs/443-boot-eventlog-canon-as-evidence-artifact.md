# Canonical boot event log as an evidence artifact

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability
**Patterns:** Registry→Diff→Gate, Bundles

Measured boot is only useful if it is **explainable**.
PCR hex tells you *that* something changed; the boot event log tells you *why*.

DeriveBSD already includes the digest hook:
- `boot.attestation.tpm.eventlog_digest` is “digest of canonicalized measured boot event log”.

This doc makes the missing “what is the canonicalized object?” surface explicit by introducing a typed artifact:
`boot.eventlog.canon`.

## The artifact

- Schema: `spec/boot.eventlog.canon.schema.json`
- Example: `spec/examples/boot.eventlog.canon.json`

A `boot.eventlog.canon` is an **order-preserving**, stable representation of the boot event log suitable for:
- event-log replay (debuggable PCR divergence)
- remote attestation verifiers (policy checks over “what was measured”)
- incident/support bundles (operator UX)

The object is designed to be safe-by-default:
- digests are the security-relevant fields
- human hints are explicitly marked as **untrusted**
- unparsed content can be retained as `unparsed_blob_digest` so parsers can improve without losing integrity

## Canonicalization discipline (`canon_id`)

`canon_id` names the canonicalization ruleset.
Treat changes to canonicalization as a review surface:
- add upstream spec revision identifiers
- add a DeriveBSD suffix when we introduce phase markers or other local conventions

Recommended naming shape:
- `tcg-pfp-<rev>+cel-<rev>+derivebsd-phase-<rev>`

Rationale: verifiers and replay tooling must be able to pick the correct interpretation deterministically.

## Bundle/export posture

`boot.eventlog.canon` is valuable in bundles, but it can carry privacy-sensitive hint fields (paths, firmware strings).
Support/export bundles should include either:
- the canonical object with `redaction.mode: none` (strict environments), or
- a redacted variant (`hints-stripped` or `hints-hashed`) with `unredacted_digest` recorded

This keeps incident response operable without making fingerprinting the default.

## Where this plugs in

- Explainable measured boot (event-log replay): `docs/313-boot-manifests-and-eventlog-replay.md`
- Measured boot + attestation lane: `docs/176-measured-boot-attestation.md`
- Durable attestation time series: `docs/315-durable-attestation-and-posture-timelines.md`
- Remote attestation admission: `docs/388-remote-attestation-admission-and-enrollment.md`

## References

- TCG Canonical Event Log (CEL) format (draft; field trust notes are especially relevant):
  - https://trustedcomputinggroup.org/wp-content/uploads/TCG_IWG_CEL_v1_r0p41_pub.pdf
- TCG PC Client Platform Firmware Profile v1.06 (event log + integrity hooks):
  - https://trustedcomputinggroup.org/wp-content/uploads/TCG-PC-Client-Platform-Firmware-Profile-Version-1.06-Revision-52_pub-3.pdf
- TCG Guidance on Integrity Measurements and Event Log Processing (verifier guidance; log trust pitfalls):
  - https://trustedcomputinggroup.org/wp-content/uploads/TCG-Guidance-Integrity-Measurements-Event-Log-Processing_V1.0_R131_PUB.pdf
- TPM2 tooling reference (`tpm2_eventlog` parser + PCR replay helper):
  - https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_eventlog.1/

Last updated: 2026-02-28r163
