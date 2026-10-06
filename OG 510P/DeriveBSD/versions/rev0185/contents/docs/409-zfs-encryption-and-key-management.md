# ZFS encryption + key management (data at rest, A–D viable)

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

DeriveBSD must make “data at rest” a first-class concern across all product shapes:

- **A (fleet host):** unattended boot, remote recovery, strict logging
- **B (workstation):** lost-device threat model, ergonomic unlock
- **C (general OS):** practical defaults without side paths
- **D (appliance/reg):** manufacturing provisioning, offline recovery, auditable controls

This doc defines a minimal ZFS-centric posture with explicit lanes.

## Threat model sketch

We care about:

- theft/loss of physical storage
- decommissioned disks
- “cold boot”/offline access to blocks
- accidental key exposure through logs/support bundles

We do **not** assume encryption defends against a fully compromised running kernel. Isolation + least authority handle that.

## Baseline posture (ZFS-native encryption)

Use **ZFS native encryption** for datasets that contain secrets or user data.

Design guidance:

- separate datasets for:
  - host system (bootable generations / BEs)
  - workload images (immutable artifacts)
  - mutable state (logs, caches)
  - user/home data (portable homes)
- treat dataset encryption as a **policy-derived property**: “which datasets require encryption?” is reviewable.

Key rules:

- key material must never be embedded in build artifacts
- key provisioning and unlock operations must produce **receipts/events**
- support bundles must redact keys and must not leak key locations/handles beyond policy

## Key sources (lanes)

DeriveBSD should support multiple key sources as policy-gated lanes:

### Lane 1: passphrase / interactive unlock (B)
- workstation posture, human present
- allow caching for session lifetime only (policy-controlled)

### Lane 2: TPM-sealed keys (A/B/D)
- key sealed to measured boot state + policy
- supports unattended boot while retaining tamper evidence

### Lane 3: remote unlock / escrowed recovery (A/D)
- remote unlock service is a capability-brokered operation
- requires explicit break-glass policy + strict receipts + rate limits
- avoids “silent” unlock pathways (must be observable)

### Lane 4: factory provisioning (D)
- manufacturing flow provisions per-device keys
- provisioning is receipted and exportable as part of the device dossier
- supports offline re-keying with strict audit trail

## Interaction with rollback + boot environments

Rollback must not become an encryption bypass.

Recommendations:

- system generations/BEs should avoid reusing mutable datasets that silently cross generations
- encryption keys for mutable datasets should be stable across a controlled retention window,
  while system datasets can be re-keyed on “generation boundary” events if policy wants it
- any re-key operation is an explicit plan → apply → receipt operation

## Portable homes / user data

For B (workstation) and some C (general OS) uses:

- prefer a dedicated encrypted dataset per “portable home”
- home export/import must be an artifact with a manifest (what is included, what is excluded)
- keys must be handled as first-class secrets (sealed and/or passphrase-derived) with receipts

## Receipts and evidence

Minimum artifacts to make this operable:

- key provisioning receipt (what was provisioned, what policy, what attester/hardware, never raw key material)
- unlock event (when, by what lane, under what policy)
- re-key plan + receipt
- support bundle redaction proof (what was redacted / filtered)

This integrates with the evidence spine (`docs/229-evidence-spine-overview.md`) and support bundles.

## Open questions (track in risk register)

- What is the minimal *cross-profile* key interface we standardize on?
- How do we represent “sealed to PCRs” vs “sealed to policy claim set” in receipts?
- What is the recovery UX for B without encouraging dangerous workarounds?
