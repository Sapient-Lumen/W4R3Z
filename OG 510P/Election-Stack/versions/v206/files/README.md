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
- **Comms authenticity (synthetic media minimum):** `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- **Rumor control + status boards as verifiable surfaces:** `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- **PublicNotice feeds (bounded discovery + rollback detection):** `docs/200-publicnotice-feeds-and-mirror-index.md`
- **Official channel directory (where to look):** `docs/203-official-channel-directory-as-evidence.md`
- **Well-known discovery bootstrap (domain-first):** `docs/204-well-known-election-stack-discovery.md`
- **Cache/freshness posture for public pointer surfaces:** `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- **Digest cards (low-bandwidth publication):** `docs/206-digest-cards-and-low-bandwidth-publication.md`
- **Public surface parity snapshots (portable split-view evidence):** `docs/201-public-surface-parity-snapshots.md`
- **Official surface security snapshots (auditable hardening posture):** `docs/199-official-surface-security-snapshots.md`

- **Track A (Deployable Core):** `docs/track-a/README.md`
  - Curated bundle: `docs/track-a/BUNDLE.md`
  - Release gate: `docs/track-a/MVR_CHECKLIST.md`
- **Track B (Remote return research):** `docs/track-b/README.md`
  - Curated bundle: `docs/track-b/BUNDLE.md`
- **Track C (North Star):** `docs/track-c/README.md`
  - Curated bundle: `docs/track-c/BUNDLE.md`
- **Artifact index:** `docs/13-artifact-index.md`
- **Scope and track map:** `docs/154-project-scope-and-track-map.md`
- **Election lifecycle evidence map (operator + verifier alignment):** `docs/215-election-lifecycle-evidence-map.md`
- **Incident triage quickmap (symptom → packet):** `docs/216-incident-triage-and-evidence-quickmap.md`
- **Claim cards (bounded dispute framing):** `docs/217-claim-cards-and-traceability-minspec.md` (template: `artifacts/templates/claim-card.md`)
- **Epistemic tags + confidence rubric (deception-resistant statements):** `docs/218-epistemic-status-tags-and-confidence-rubric.md`
- **Uncertainty-safe public updates (tags + update commitments):** `docs/219-uncertainty-safe-public-updates.md`
- **PublicNotice graph resolution (supersedes/corrections → “current state”):** `docs/220-publicnotice-graph-resolution-and-effective-state.md`
- **PublicNotice monitoring + convergence (feeds + current state parity):** `docs/221-publicnotice-monitoring-and-convergence.md`
- **PublicNotice divergence dispute bundle minspec (parity failure handoff):** `docs/222-publicnotice-divergence-dispute-bundle-minspec.md` (checklist: `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`)
- **Public-surface capture notes (reproducibility without bundle bloat):** `docs/223-public-surface-capture-notes-and-reproducibility.md` (template: `artifacts/templates/public-surface-capture-note.md`)
- **Request context & variant probing (split-view root causes):** `docs/224-request-context-and-variant-probing-for-public-surfaces.md` (ties into `201`/`223`/`205`)
- **Compact request-context notation (req/vary/age):** `docs/232-compact-request-context-notes.md` (syntax + canonicalization contract + test vectors)
- **Redaction logs & transformation accountability (hashes-first):** `docs/225-redaction-logs-and-transformation-accountability.md` (template: `artifacts/templates/redaction-log.md`)
- **Maintainer protocol:** `docs/150-maintainer-bootstrap-and-change-protocol.md`
- **Refactor + growth discipline (anti-bloat):** `docs/227-refactor-and-growth-protocol.md`
- **Placeholder domains + doc address ranges (copy-paste safe examples):** `docs/231-placeholder-domains-and-identifiers.md`
- **External source pin exemptions (explicit triage):** `docs/228-external-source-pin-exemptions.md`
- **External source pinning workflow (sha256 without bundling):** `docs/233-pinning-workflow-for-external-sources.md`
- **External sources by primary tag (reading/triage view):** `docs/230-external-sources-by-primary-tag.md`
- **Experiment → spec promotion protocol (backlog → Track A candidate):** `docs/229-experiment-to-spec-promotion-protocol.md`
- **Near-term research agenda (kept small):** `docs/207-research-agenda-and-revision-ledger.md`



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
