# 572 — Nuclear emergency preparedness: chain-of-custody intake CLI, evidence contract, and field-kit pointer refactor

Revision: **rev0365**  
Base: **rev0364**  
Status: P0 evidence-intake hardening plus one bounded waste refactor. Public-context-only; no real-site readiness or unreadiness claim.

## Why this revision exists

Rev0364 made the claim gate honest, but the cube still had a practical failure mode: a future operator could receive a real or anonymized exercise packet and then summarize it narratively before the archive had a durable chain-of-custody record. Rev0365 turns the evidence path into an executable intake lane.

This revision intentionally avoids another layer of broad doctrine. It adds three concrete mechanisms:

1. **Evidence packet contract.** `cube/nuclear-emergency-bvps-evidence-packet-contract-rev0365.csv` defines the artifact classes that matter most, the minimum metadata that must travel with each artifact, and the states allowed before adjudication.
2. **Hashing intake CLI.** `tools/intake_nuclear_emergency_bvps_evidence_packet_rev0365.py` computes size and SHA-256 for a drop directory, joins a sidecar metadata CSV, and emits a chain-of-custody ledger. The included fixture proves the machinery works without pretending that any real Beaver Valley evidence has arrived.
3. **Field-kit pointer refactor.** Older BVPS field kits duplicate cube artifacts. Rev0365 does not delete history, but the new `field-kits/bvps-rev0365/fieldkit-pointer-manifest-rev0365.csv` references canonical cube paths instead of copying them again. Future field kits should follow that pattern.

## P0 rule

No artifact can support even a candidate evidence claim unless it has at least: artifact class, custodian or public source, received timestamp, scope/jurisdiction, hash, file size, redaction/sensitivity state, and linked request or gap. Even then, the only permitted effect is candidate evidence for adjudication. It is not readiness closure.

## Operational files

- `tools/intake_nuclear_emergency_bvps_evidence_packet_rev0365.py` — hashes a drop directory and writes a normalized ledger.
- `fixtures/bvps-evidence-intake-rev0365/mock-drop/metadata.csv` — safe fixture sidecar for the intake tool.
- `cube/nuclear-emergency-bvps-evidence-intake-fixture-ledger-rev0365.csv` — output from running the intake tool on the safe fixture.
- `tools/validate_nuclear_emergency_bvps_evidence_intake_contract_rev0365.py` — reruns the intake fixture and checks the contract/ledger cannot become a closure claim.
- `tools/validate_nuclear_emergency_bvps_no_readiness_overclaim_rev0365.py` — scans current-risk files for affirmative readiness-overclaim language.
- `tools/validate_bvps_fieldkit_pointer_manifest_rev0365.py` — verifies the rev0365 field kit points to canonical cube files and does not re-copy identical artifacts.

## Refactor boundary

The field-kit refactor is intentionally narrow. Rev0365 does **not** remove historical field-kit copies, historical SQLite mirrors, or giant matrices. It changes the forward pattern so new field kits do not add more duplicate-content debt while the evidence-intake path is still hot.

## Current state

The cube is now more capable of ingesting a lawful packet without losing provenance, but it still has no real Beaver Valley exercise evidence packet. The only honest state remains: **capture-ready / chain-of-custody-ready / claim-frozen / no local readiness conclusion**.
