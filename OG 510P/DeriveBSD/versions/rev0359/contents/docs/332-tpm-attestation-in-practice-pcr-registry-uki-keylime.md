# TPM attestation in practice: PCR registries, measured payloads, and Keylime-style verifiers

DeriveBSD already defines a *measured boot* lane (`boot.manifest` → `boot.attestation` → `attestation.reference` → `attestation.receipt`).
The tricky part in real fleets isn’t “can we quote PCRs?” — it’s making **PCR meaning** and **measurement boundaries** stable enough that:

- references can be shared across machines (not per-host snowflakes)
- failures are explainable (“what changed?”) rather than opaque (“PCR mismatch”)
- secret release + rollout gates can consume the results without bespoke glue

This doc captures concrete ecosystem lessons that are worth baking in *now*.

## 1) Treat PCR meaning as a registry, not tribal knowledge

A common failure mode:
- Team A assumes PCR 7/11 means X.
- Team B measures something else into the same PCR.
- Months later, policy gates fail mysteriously.

DeriveBSD should explicitly pin **which PCRs carry which semantics** in the *reference values object*:
- `attestation.reference.pcr_selection` already captures which PCRs are quoted.
- Add an explicit *intent* note in the reference object’s `notes` (and/or a verifier-side policy module) that names the intended registry.

Reference point:
- UAPI Group’s Linux TPM PCR Registry is a good model for publishing “what measures into what PCR” as a living spec.
  (We don’t need Linux parity; we need the *discipline*.)

See: `docs/245-boot-measurement-phases-and-pcr-separation.md`.

## 2) Measure the *payload you care about*, not “everything vaguely boot-related”

Measured boot gets operable when the attestation can be interpreted as:

> “This host booted generation G, whose boot-critical closure is M (boot.manifest).”

DeriveBSD’s guardrails:
- keep `boot.manifest` small and stable (loader/kernel/modules/init + cmdline profile)
- prefer **event-log replay** against the manifest over brittle “golden PCR” allowlists
- measure phase markers into a dedicated PCR so policy can gate on milestones (firmware → loader → kernel → services → online)

See:
- `docs/313-boot-manifests-and-eventlog-replay.md`
- `docs/245-boot-measurement-phases-and-pcr-separation.md`

## 3) UKI-style thinking is useful even if we’re BSD-first

The Linux ecosystem’s Unified Kernel Image (UKI) work is valuable as a **measurement-boundary pattern**:
- a single bootable payload (kernel+initrd+cmdline+metadata) with clear measurement semantics
- tooling to pre-calculate/verify expected PCR values (useful for “known payload” gates)

DeriveBSD can reuse the pattern without adopting systemd:
- treat “boot payloads” (loader + kernel bundle + initrd-equivalent) as a typed, digest-addressed unit
- make the measurement boundary explicit and stable in the boot-manifest vocabulary

Pointers (context): see `docs/32-curated-references.md` (systemd-stub, systemd-measure).

## 4) Keylime’s architecture maps cleanly onto Derive’s evidence spine

Keylime is a practical reference implementation for remote attestation workflows:
- **agent** on the node collects TPM quote + event log evidence
- **registrar** tracks node identities/enrollment
- **verifier** evaluates evidence and produces an integrity verdict
- **tenant/CLI** drives workflows

DeriveBSD’s mapping:
- enrollment/provisioning is already modeled as receipts (`docs/314-attester-provisioning-and-key-lifecycle-receipts.md`)
- verifier output should always be a signed `attestation.receipt` (never “an API response only”)
- “continuous posture” becomes a receipt chain (`docs/315-durable-attestation-and-posture-timelines.md`)

This avoids the usual bolt-on:
- attestation outputs become reusable gates for secrets, rollouts, and incident bundles.

## 5) Evolving reference policies without bricking fleets

If you bind secrets strictly to PCR values, you will eventually need a controlled way to *evolve* acceptable states.
The TPM ecosystem’s `PolicyAuthorize` pattern is a useful mental model:
- references are signed and versioned
- verifiers can accept “new good states” with an explicit authorization step

DeriveBSD should model that evolution explicitly as:
- new `attestation.reference` objects (new digests)
- receipts that record exactly which reference was used
- rollout policy that can stage the transition (cohorting) and preserve rollback semantics

See: `docs/62-replay-rollback-freeze.md`, `docs/231-ab-updates-and-recovery-semantics.md`.

Last updated: 2026-02-26r91
