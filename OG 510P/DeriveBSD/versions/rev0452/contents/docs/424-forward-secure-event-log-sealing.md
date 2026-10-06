# Forward-secure event log sealing (tamper-evident local evidence)

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability
**Patterns:** Plan→Apply→Receipt  

DeriveBSD already treats logs as typed evidence (`event.record` → `event.segment`).
This lane makes the *integrity* of those segments machine-checkable after the fact:
**a digest-chained, signed sealing stream** that detects silent deletion/rewrite of local evidence.

This is not a public transparency log.
It is a *local, forward-secure-ish* integrity layer for the evidence spine.

## Prior art (steal the shape)

- systemd journal **Forward Secure Sealing (FSS)** (keyed sealing + verification keys stored out-of-band):
  - `journalctl --setup-keys` / verification: https://www.freedesktop.org/software/systemd/man/journalctl.html
  - `Seal=` configuration: https://www.freedesktop.org/software/systemd/man/journald.conf.html
  - on-disk format notes (includes sealing fields): https://systemd.io/JOURNAL_FILE_FORMAT/
- AWS CloudTrail **digest file chain** (hourly digest objects that hash log objects and chain signatures):
  - digest structure: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-digest-file-structure.html
  - validation overview: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
- Cryptographic scrutiny of journald sealing (useful for threat-model clarity):
  - https://eprint.iacr.org/2023/867.pdf

## DeriveBSD translation

### Core idea

Treat sealing as a derived operation that emits a **typed receipt**:

- Inputs: ordered set of `event.segment` file digests for a stream, plus the previous seal (optional)
- Output: `event.seal.receipt` (signed; hash-chainable)

Schema + example:
- `spec/event.seal.receipt.schema.json`
- `spec/examples/event.seal.receipt.json`

### What a seal commits to

A seal receipt commits to:

- **which stream** (`stream_id`)
- **which segments** (via `segments_root_digest` + optional range)
- **how it chains** (`previous_seal_digest`)
- **how to verify** (`verification.verification_key_digest`, export-safe)

The sealed set should be **ordered and normalized** before hashing.
`segments_root_digest` is `sha256(utf8(JCS({"stream_id": ..., "segments": [{"segment_id","file_digest"}, ...]})))` using the exact ordered segment list committed by the receipt.
(For small sets, the receipt may include `seal.segments[]` explicitly; for large sets, commit via the equivalent ordered list off-body.)

### Verification UX (evidence-as-product)

A verifier should be able to answer, without SSH and without bespoke scripts:

1) *Are any segments missing between seal N and seal N+1?*
2) *Did the host rewrite old segments after sealing?*
3) *Which verification key should be used, and where did it come from?*

DeriveBSD should expose:
- `derive evidence verify-seals --stream host:<id> --since ...` → a tiny report + the first failing receipt digest
- support-bundle attachments that include the relevant `event.seal.receipt` digests (export-governed)
  and, when continuity proof matters, the official support handoff may carry those digests through `event_seal_receipt_digests`; see `docs/625-incident-bundles-carry-event-seal-proof-by-digest.md`

### Where it plugs into existing patterns

- **Plan → Receipt:** sealing emits `event.seal.receipt` as a stable evidence object.
- **Broker → Lease:** key material for sealing must be accessed via a brokered operation (no ambient private keys).
- **Registry → Diff → Gate (optional):** policy may gate promotion/quarantine on “seal chain continuous” for a cohort.

## Tier/profile guidance

- **A (fleet host):** recommended-on; fleets need tamper-evident evidence.
- **D (appliance/regulatory):** recommended-on; compliance lanes frequently require integrity proofs.
- **B/C (workstation/general OS):** optional; user/admin may enable for high-assurance workloads.

This lane must be fully disable-able by policy (no fork; no global obligation).

See also:
- Structured event log as evidence: `docs/215-structured-event-log-as-evidence.md`
- Evidence spine overview: `docs/229-evidence-spine-overview.md`
- Export policies + receipts: `docs/251-export-policies-and-support-bundle-portal.md`

Last updated: 2026-03-21r355
