# Reproducibility & Ops (Nix, systemd, AFK safety, and provenance)

## 10.1 Nix baseline
Project MUST provide a Nix flake that pins toolchains and dependencies.

## 10.2 AFK runtime integration (Linux)
Preferred:
- run AFK work in a systemd user scope (`systemd-run --user --scope ...`) so kill semantics terminate the whole cgroup.

Fallbacks:
- cgroup v2 direct
- setsid/process-group kill

## 10.3 Provenance of evaluation snapshots (recommended)
To keep results interpretable across changing definitions:
- each run MUST record hashes of scorecard + probes + holdouts,
- and SHOULD produce an attestation artifact binding these hashes to the run outputs.

Optional implementations:
- simple: sign a manifest JSON (GPG)
- structured: adopt supply-chain style attestations (SLSA/in-toto ideas)
- pragmatic: sigstore/cosign signing of the run manifest blob

This is primarily for **provenance and history**, not distrust.

## 10.4 Artifact bundling
Every run MUST produce a self-contained bundle:
- ExperimentSpec + registries snapshot
- seeds
- queue DB / journal
- result store (or references)
- HTML report + tabular exports

## 10.5 Redaction & portability
Provide `grlab redact` and `grlab export --public`.

## 10.6 Optional experiment tracking adapters
If MLflow/W&B/DVC are enabled, they MUST:
- read from the local artifact store/manifests,
- and never become the only source of truth.

## 10.7 CI expectations (expanded)
CI SHOULD:
- run determinism smoke tests,
- run AFK interrupt test (kill mid-run, resume, ensure no corruption),
- run metamorphic checks,
- verify evaluation snapshot hashes are stable,
- run baseline regression suite.
