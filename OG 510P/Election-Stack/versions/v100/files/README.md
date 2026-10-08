# The Election Stack (Hardened Federated Voting Specs archive)

This repository is an **election evidence + transparency stack**: protocols, schemas, and operational patterns that make election outcomes *auditable even under partial compromise*.

This is the working archive for **The Election Stack** research program (historical name: **Hardened Federated Voting Specs / HFV**).
The name matters only insofar as it keeps us honest: we are engineering a **full-stack evidence layer** for elections, not selling a single voting modality.

## Start here
- **Start here:** `docs/START_HERE.md`
- **Claims + boundaries:** `docs/166-scope-and-claims-contract.md` + `docs/167-non-claims-and-boundaries.md`
- **Evidence API surface (verifier minimum):** `docs/179-evidence-api-surface.md`
- **Evidence object catalog (kinds + schemas + examples):** `docs/EVIDENCE_OBJECT_CATALOG.md`
- **Verifier MVP path (packet → policy → report):** `docs/188-verifier-minimum-viable-path.md`
- **Publishable verifier output:** `docs/193-publishable-verifier-reports.md` + `docs/VERIFIER_PROBLEM_CODES.md`
- **Observer kit (offline verification):** `docs/177-observer-kit-offline-verification-walkthrough.md`
- **Incident comms as evidence (rumor control):** `docs/186-incident-communications-as-evidence.md`

- **Track A (Deployable Core):** `docs/track-a/README.md`
  - Curated bundle: `docs/track-a/BUNDLE.md`
  - Release gate: `docs/track-a/MVR_CHECKLIST.md`
- **Track B (Remote return research):** `docs/track-b/README.md`
  - Curated bundle: `docs/track-b/BUNDLE.md`
- **Track C (North Star):** `docs/track-c/README.md`
  - Curated bundle: `docs/track-c/BUNDLE.md`
- **Artifact index:** `docs/13-artifact-index.md`
- **Scope and track map:** `docs/154-project-scope-and-track-map.md`
- **Maintainer protocol:** `docs/150-maintainer-bootstrap-and-change-protocol.md`



It is intentionally built to wrap **any casting method** (paper, BMD, kiosk, limited remote return), while keeping a **North Star** track for “fully electronic voting done right”.

## The three-track framing (do not confuse these)

### Track A — Deployable Core (evidence-based elections)
A practical stack for real deployments **today**:
- paper ballot of record / voter-verifiable paper record
- verifiable tally pipeline
- election-night reporting (ENR) hardening
- transparency logs, witnesses, monitoring, incident comms, and court-usable evidence bundles

### Track B — Remote Return Research Annex (hard-mode experiments)
Protocols/patterns for remote return contexts, with explicit non-claims around coercion and malware.
This track exists to **learn** and to document “what would have to be true”.

### Track C — North Star (fully electronic voting in its best imaginable form)
A “build the ecosystem” program:
- attestable hardware (remote attestation roles + evidence flow)
- transparent manufacturing + provenance (signed supply-chain statements)
- endorsement/reference-value transparency and split-world resistance

See **`docs/154-project-scope-and-track-map.md`** and **`155–157`** for the North Star attestation/provenance stack.

## Quick start reading order

If you have 30–45 minutes:
1. `00` goals → `01` threat model → `02` architecture → `03` protocol
2. `04` transparency log → `23` witness gossip → `140–149` public inspections hardening
3. `09` audit/recovery → `63–72` results/ENR and evidence publication
4. `150–153` maintainer protocol + sources lockfile + ADR/change control

If you are focusing on the North Star:
- `155–157` (attestation, claims, manufacturing pipeline)
- `141` (SCITT profile) + `145` (deadlines) + `147` (inspection gossip)

## Working with this archive safely (LLM/human)

- Follow `docs/150-maintainer-bootstrap-and-change-protocol.md`.
- Pin upstream sources in `evidence/lock/external-sources.toml` (see `151` and `161`).
- Record semantic decisions as ADRs in `adr/`.
- Keep “no silent drift” as a hard rule: regenerate manifests and update the changelog on every release.
- Run the one-command gate before tagging: `python3 scripts/release_gate.py` (see `docs/162`)
- Keep example packets live: `scripts/check_example_packets.py` (verifies `artifacts/examples/evidence_packet_*`)
- Keep dual-use boundaries explicit (no operational attack playbooks): see `docs/167-non-claims-and-boundaries.md` (N-6).
- Never ship secrets or private keys: `docs/189-sensitive-material-and-secrets.md` (enforced by `scripts/check_no_private_keys.py`).

## Integrity

- `MANIFEST.sha256` records sha256 of all tracked files.
- `scripts/build_manifest.py` can regenerate it.

## Version

See `VERSION` and `CHANGELOG.md`.

## Canonical evidence packaging (anti-drift)
- Evidence envelopes + packet layout: `docs/173-canonical-evidence-envelopes-and-packets.md`
- Coverage accounting deliverable: `docs/174-coverage-accounting-and-representativeness.md`
