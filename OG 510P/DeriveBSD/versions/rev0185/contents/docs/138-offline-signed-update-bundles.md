# Offline signed update bundles (RAUC / fwup lessons)

DeriveBSD’s default posture assumes “mirrors are hostile” and verification is local.
For **air-gapped** or constrained environments, it is useful to ship updates as a *single, signed file*.

Two practical ecosystem references:
- RAUC bundles: signed/verified update bundles + robust installation + boot integration. https://rauc.readthedocs.io/en/latest/basic.html
- fwup: image-based firmware updates using a ZIP archive with metadata/instructions; optional signing; supports A/B/trial/failback flows. https://github.com/fwup-home/fwup

## Lesson to steal

- bundle format is **self-contained**:
  - payload(s)
  - manifest/metadata
  - signature(s)
- apply is **transactional** and power-failure safe
- bundle can be transported over USB, file drop, or constrained links

## DeriveBSD mapping

### “Bundle” as an Artifact container

A DeriveBSD offline bundle can contain:
- one or more artifact payloads (host generation, microVM base, patchset)
- the relevant closure manifest/proof for each payload
- required attestations (provenance/SBOM)
- an optional snapshot of channel metadata (for anti-rollback/freeze)
- the policy decision record that authorized consumption

### Verification rules

- verify signatures + digests before unpacking/applying
- treat unpacking/applying as a **quarantine → verify → promote** workflow

### Why this matters

- supports secure update flows where network is unavailable or untrusted
- keeps the “explainability” chain intact even for sneaker-net updates

See also:
- `docs/126-zfs-send-distribution.md` (dataset-native transport)
- `docs/273-airgap-mirror-kits-and-sneakernet-updates.md` (offline carrier ergonomics)
- `docs/113-syspatch-style-patchsets.md` (small revertible updates)
- `docs/221-firmware-updates-as-artifacts.md` (firmware payloads + receipts as part of bundles)

Candidate RFC: *Offline bundle format + verifier + apply pipeline*.

Last updated: 2026-02-23
