# Boot manifests + event-log replay (make measured boot explainable)

Measured boot is operationally miserable if the only interface is “PCRs changed”.
DeriveBSD can avoid that by baking in a first-class **`boot.manifest`** object and a
clear **event-log replay** story.

This doc is an “ergonomics spine” for the existing lanes:
- Secure Boot binding: `docs/51-secure-boot-integration.md`, `docs/244-bootchain-revocation-and-allowlists.md`
- Measured boot evidence: `docs/176-measured-boot-attestation.md`, `docs/245-boot-measurement-phases-and-pcr-separation.md`
- Posture receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`

## 1) `boot.manifest`: the minimum boot-critical closure

A `boot.manifest` is a digest-bound list of **boot-critical components and inputs** for a deployed generation.
It’s the object we want operators and verifiers to *reason about*, instead of opaque PCR hex.

Schema: `spec/boot.manifest.schema.json` (example: `spec/examples/boot.manifest.json`).

### Typical contents

At minimum:
- loader (UEFI app / ZFS loader) digest
- kernel digest
- kernel modules digest (tree)
- activation/init digest
- cmdline profile digest (or loader config profile digest)

Optional (platform-dependent):
- shim or secure-boot intermediate digest
- microcode digests
- a **firmware policy** digest (what firmware floor is required, what capsules are allowed)

Key rule: **make it small and stable**.
If we shove “everything” into the manifest, policy becomes brittle and operators will disable it.

## 2) The event log is the “explainable transcript”

The TPM quote proves “these PCRs have these values”.
The event log answers “*why* do the PCRs have these values?”

DeriveBSD should treat the event log as an input-like artifact:
- canonicalize it into a stable representation
- hash it
- store the digest in `boot.attestation.tpm.eventlog_digest`

We don’t need one universal canonical format on day 0.
We *do* need an explicit identifier for the canonicalization rules so replay tools can be deterministic.
(See `boot.manifest.measurement.eventlog_canon`.)


DeriveBSD represents the canonicalized log as a typed artifact:
- `boot.eventlog.canon` (schema: `spec/boot.eventlog.canon.schema.json`, example: `spec/examples/boot.eventlog.canon.json`)
- wiring: `docs/443-boot-eventlog-canon-as-evidence-artifact.md`

### Canonicalization (practical rules)

- Preserve event order.
- Keep event type + PCR index + digest algorithm.
- For “image loaded” events, normalize to:
  - digest of the loaded image bytes (if available)
  - a stable label/path (metadata only)
- Strip volatile timestamps and firmware strings unless explicitly needed.
- Allow a small “unparsed blob digest” field for platform quirks, so we can improve parsers without losing integrity.

## 3) Verification strategy: replay beats golden PCRs

Avoid the default industry failure mode: “golden PCR allowlists per host”.

Preferred verifier posture:
1) Verify quote signature (AK / attester identity).
2) Check PCRs are consistent with the **replayed event log**.
3) Check that the event log corresponds to the expected `boot.manifest` (and any policy constraints like phase markers).

This supports variance without giving up security:
- minor firmware drift can be tolerated if it doesn’t affect measured components we care about
- known-good loader/kernel digests remain the primary policy anchors

This matches the policy guidance in:
- `docs/176-measured-boot-attestation.md` (PCR matching philosophy)
- `docs/226-platform-posture-and-attestation-results-as-evidence.md` (reference values + receipts)

## 4) Tooling hooks (keep it debuggable)

A greenfield OS can ship “day 0” affordances:

- `derive boot manifest show <deployment.ref>`
  - prints the resolved manifest, with human labels
- `derive attestation replay <boot.attestation> --reference <attestation.reference>`
  - replays event log → PCRs
  - emits a short, actionable diff:
    - “unexpected image digest at loader stage”
    - “phase marker missing: services”
    - “PCR 4 mismatch; first divergent event #17”

- `derive attestation explain <attestation.receipt>`
  - joins the receipt with:
    - the reference
    - the boot manifest
    - the boot attestation
  - so incident response can answer “what did the verifier think?” without vendor tooling.

## 5) Non-goals (v1)

- require measured boot on all systems
- require a single, universal event-log parser across all platforms
- runtime integrity monitoring as a prerequisite

## References (context only)

- tpm2-tools: `tpm2_eventlog` (parse binary event log; can compute/replay PCRs): https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_eventlog.1/
- go-eventlog (event-log replay helpers): https://github.com/google/go-eventlog
- Keylime measured boot notes (event log evaluation model): https://keylime.readthedocs.io/en/latest/user_guide/use_measured_boot.html
- UAPI Group: Linux TPM PCR Registry (measurement-to-PCR mapping reference): https://github.com/uapi-group/specifications/blob/main/specs/linux_tpm_pcr_registry.md
- systemd-stub (UKI measurements; useful measurement-boundary prior art): https://man7.org/linux/man-pages/man7/systemd-stub.7.html
- systemd-measure (PCR pre-calculation for UKI; reference only): https://www.freedesktop.org/software/systemd/man/systemd-measure.html

Last updated: 2026-02-28r163
