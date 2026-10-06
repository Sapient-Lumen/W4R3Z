# Unified boot capsules and measured-boot receipts (make “what booted” a single hash)

DeriveBSD already treats host generations and boot environments as derived artifacts.
The missing “groundfloor” ergonomic win is to make **the boot payload itself** a single, signed, measurable object.

Linux ecosystems call this a **Unified Kernel Image (UKI)**: one signed EFI executable that packages:

- kernel
- initrd
- command line
- certificates / embedded policy
- metadata sections that UEFI can measure into TPM PCRs

DeriveBSD can adopt the *shape* (not the Linux specifics): call it a **Unified Boot Capsule (UBC)**.

## Goals

- **One hash** answers “what boot payload did we intend to run?”
- Measured boot is **debuggable** (event log explains PCRs)
- Boot policy can reference **named sections** instead of brittle raw PCR values
- Works with ZFS boot environments and health-gated switching

## Non-goals

- Mandating UEFI Secure Boot everywhere (but UBCs should be signable and SB-friendly).
- Replacing the existing boot manifest + attestation lanes; UBC tightens them.

## The UBC shape

A UBC is a signed UEFI application (PE/COFF) that embeds named sections:

- `.kernel` (DeriveBSD kernel)
- `.initrd` (early userspace)
- `.cmdline` (boot args; *must* be digest-bound)
- `.bootmanifest` (digest + pointer to `spec/boot.manifest.schema.json` object)
- `.pubkeys` (optional pinned keys / trust bundles for early verification)
- `.metadata` (human/debug fields; version, build-id, etc)

The **section list is the contract**. Adding a new section is a review event.

## Measurement semantics

Measured boot is only operable if it stays explainable.
Borrow a key UKI lesson: measure *named sections in a canonical order* and keep the event log.

DeriveBSD should:

- define a canonical measurement order for UBC sections
- record the event log as evidence
- prefer policies that replay event logs against a boot manifest (not “golden PCRs”)

This plugs directly into:
- PCR phase markers: `docs/245-boot-measurement-phases-and-pcr-separation.md`
- posture receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`

## Evidence

A minimal evidence flow:

1) Build produces:
   - `boot.capsule` (the UBC bytes; content-addressed)
   - `boot.manifest` (closure for boot-critical bytes)

2) Boot produces:
   - TPM event log pointer (or digest)
   - `boot.attestation` (quote + verifier receipt)

3) Policy can answer:
   - “did the machine boot an allowed capsule?”
   - “which phase markers were reached?”
   - “what changed between two boots?”

## Operational ergonomics (why this is worth it)

- Recovery is easier: a UBC can embed a tiny rescue initrd (still signed/measured).
- Fleet rollouts become legible: a rollout targets a *capsule digest*, not a pile of parts.
- Debugging “why did TPM unlock fail?” becomes tractable (section-by-section measurement).

## Where this plugs in

- Boot manifests: `spec/boot.manifest.schema.json`, `docs/313-boot-manifests-and-eventlog-replay.md`
- Bootchain policy: `spec/bootchain.policy.schema.json`
- Attestation receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- Sealed secrets: `docs/272-sealed-secrets-attested-unsealing.md`
- Host generations + boot env switching: `docs/284-bootenv-switching-as-evidence.md`

## References

- UAPI Group: Unified Kernel Image specification (measurement semantics):
  https://uapi-group.org/specifications/specs/unified_kernel_image/
- systemd-measure (precompute expected PCR values for a UKI):
  https://www.freedesktop.org/software/systemd/man/systemd-measure.html

Last updated: 2026-02-27r101
