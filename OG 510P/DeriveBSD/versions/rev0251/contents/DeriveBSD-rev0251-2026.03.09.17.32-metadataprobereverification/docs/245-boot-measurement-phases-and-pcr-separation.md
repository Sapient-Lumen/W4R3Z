# Boot measurement phases and PCR separation (measured-boot ergonomics)

Measured boot (TPM quotes + event logs) is powerful, but brittle if we try to pin a single PCR value to "the whole boot".

A practical pattern is to measure **phase markers** into a dedicated PCR so policy can reason about *which milestone was reached* and *what was executed before it*.

## Why phases matter

Without phase separation:
- PCR values become opaque and hard to debug
- small firmware or initrd drift forces large allowlists
- you can't distinguish "booted kernel but userspace never started" from "system reached services but failed later"

With phases:
- you can compute expected PCRs per phase path
- you can gate secrets/services on specific phases (least authority)
- you can attach failures to a crisp milestone for rollback + incident capture

## DeriveBSD direction

- Keep `boot-attestation` as the primary evidence object (`spec/boot.attestation.schema.json`).
- Canonicalize and store the boot measurement log (already supported via digests in receipts).
- Introduce a **phase vocabulary** for DeriveBSD hosts and builders:
  - `firmware` → `loader` → `kernel` → `initrd` → `sysinit` → `services` → `online`

A small, BSD-native helper (loader module, initrd hook, and/or early userspace) can extend a dedicated PCR with literal phase markers.

### Policy usage

- Admission control can require "phase >= services" before enabling sensitive portals.
- Health gating can use phase markers to classify failures:
  - never reached `sysinit` → treat as boot-path failure, try-counters should fall back
  - reached `services` but failed later → treat as service graph failure, collect svc evidence

### Evidence usage

- `attestation.reference` should specify which PCR(s) carry phase markers.
- Verifier receipts should include reason codes that mention missing/incorrect phase markers.

## Implementation note (avoid Linux dependencies)

The **pattern** is what's important, not the exact tooling.

Linux uses `systemd-pcrphase` to extend phase markers into PCR 11. DeriveBSD can implement the same semantics with a tiny initrd binary and a strict ABI.

## References

- systemd phase measurements (PCR 11): https://www.freedesktop.org/software/systemd/man/systemd-pcrphase.service.html
- systemd doc: TPM2 PCR measurements overview: https://systemd.io/TPM2_PCR_MEASUREMENTS/
- UAPI Group: Linux TPM PCR Registry (phase-marker PCR conventions are best treated as published semantics): https://github.com/uapi-group/specifications/blob/main/specs/linux_tpm_pcr_registry.md

Last updated: 2026-02-26r91
