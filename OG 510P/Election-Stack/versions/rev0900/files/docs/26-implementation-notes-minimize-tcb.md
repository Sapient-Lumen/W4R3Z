# Implementation notes: minimize TCB (paranoid)

**Track:** A (Deployable core)


This doc is intentionally opinionated: “general-purpose web app + cloud” is the default failure mode.

## Attack surface minimization (MUST)
- Critical services SHOULD be implemented in memory-safe languages.
- Crypto verification code MUST be small, deterministic, and heavily tested.
- Separate responsibilities into isolated processes:
  1) intake validation,
  2) log append/sequencing,
  3) witness verification,
  4) tally/proof generation (offline where possible).

## Secrets & keys
- No long-lived secrets on internet-facing hosts.
- Use HSMs for log signing keys; threshold keys for tally.
- Treat build/signing keys as Tier-0 assets with dedicated ceremonies.

## Determinism and reproducibility
- Reproducible builds are REQUIRED for all verifiers and witness software.
- Publish build provenance and hashes; require multi-party signing before release.

## Verification usability (MUST)
- Provide a “one-button verifier” that:
  - downloads checkpoints from multiple witnesses,
  - verifies proofs,
  - produces a machine-readable report.
- Publish independent verification implementations (N-version programming).