# The Election Stack (Hardened Federated Voting Specs archive)

**Track:** Shared (cross-cutting)


This repository is an **election evidence + transparency stack**: protocols, schemas, and operational patterns that make election outcomes *auditable even under partial compromise*.

It is designed for the cases that decide legitimacy: contested counts, forged statements, suppressed publication, and institutional failure.
When institutions act quickly, the evidence supports immediate dispute resolution. When they do not, the evidence is built to **persist** (mirrorable, offline-verifiable) so future adjudicators and the historical record can still converge on what happened.

**Mission discipline:** do not let the specification become the mission. The mission is that, when an election is contested, affected people can converge on what happened using portable evidence. If a schema serves no plausible dispute, it should not exist; if a checklist is never drilled, it is not a capability.

## External anchors (standards we align *around*, not comply *to*)

For readers coming from election administration, certification, and lab/testing contexts, see:
- `docs/245-external-standards-and-alignment-map.md` — compact map to VVSG 2.0, NIST election cyber profiles, CDF guidance, and audit references.
- `docs/248-accessibility-usability-and-language-access-as-integrity.md` — minimal integrity-control set for accessibility and language access (with publishable proofs).

- Assurance-case skeleton + evidence minimization (maintainer pattern): `docs/246-assurance-case-skeleton-and-evidence-minimization.md`
- Ops controls (public comms + chain-of-custody as verifiable security controls): `docs/247-ops-security-controls-comms-and-chain-of-custody.md`
- Incident reporting + coordinated disclosure as evidence surfaces (digest-first, bounded): `docs/259-incident-reporting-and-coordinated-disclosure-as-evidence-surfaces.md`
- Threat-model ledger + safe red-teaming guardrails (bounded, non-weaponizing): `docs/249-threat-model-ledger-and-safe-red-teaming.md`
- Observation & challenge as evidence surfaces (privacy-first, anti-intimidation): `docs/250-observation-and-challenge-as-evidence-surfaces.md`
- Provisional ballots, curing, and canvass as evidence surfaces (privacy-first): `docs/251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md`
- Election night reporting (ENR) + unofficial results as evidence surfaces (snapshots + corrections log): `docs/252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md`
- Vote-by-mail distribution, tracking, and drop boxes as evidence surfaces (bounded, privacy-first): `docs/271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`
- Mail ballot intake, verification, and processing as evidence surfaces (counts-only, privacy-first): `docs/272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`
- Ballot accounting and reconciliation as evidence surfaces (end-to-end ledger + canvass bridge digests): `docs/273-ballot-accounting-and-reconciliation-as-evidence-surfaces.md`



## Outside view (why this exists, without politics)

This archive assumes a modern reality: election disputes are often decided by **legitimacy** and **evidence availability**, not only by counts.
That is why it treats **institutional volatility**, suppression, and “unverifiability attacks” as first-class risks—while staying neutral about parties and outcomes.

If authoritative evidence is published and independently verifiable, narrative attacks fail.
If evidence is suppressed or split-viewed, the suppression itself should become **checkable evidence** (missed deadlines, missing packets, divergent bytes).



This is the working archive for **The Election Stack** research program (historical name: **Hardened Federated Voting Specs / HFV**).
The name matters only insofar as it keeps us honest: we are engineering a **full-stack evidence layer** for elections, not selling a single voting modality.

## 60-minute outside view (for adopters under time pressure)

If you are deciding whether this is worth piloting, do **not** start by browsing the full directory.
Read these five items, in order:

1. `docs/START_HERE.md` (what this is; where to start)
2. `docs/track-a/README.md` (Track A deployable core — what it wraps, what it emits)
3. `docs/166-scope-and-claims-contract.md` (what we assert)
4. `docs/167-non-claims-and-boundaries.md` (what we explicitly do **not** assert)
5. `docs/track-a/PILOT.md` (what a minimal “one county” pilot looks like)

**Maintainers:** if you change this read-order or any linked entry docs, run `CHECK:artifacts/checklists/adopter-60-minute-path-smoke-test.md` and log a bounded row in `artifacts/registries/adopter-path-smoke-tests.csv`.

Optional voter-facing legitimacy framing:
- `docs/track-a/VOTER_VERIFICATION.md` + `docs/track-a/PERSONS_PATH.md`

If you need a fast briefing artifact (for commissioners/legislators/procurement):
- `artifacts/templates/adopter-slide-deck-outline.md`

For other audiences (verifiers, builders) and a strict “what to ignore until needed” map:
- `docs/242-audience-reading-paths-and-what-to-ignore.md`

## Start here
- **Start here:** `docs/START_HERE.md`
- **Claims + boundaries:** `docs/166-scope-and-claims-contract.md` + `docs/167-non-claims-and-boundaries.md`
- **Evidence API surface (verifier minimum):** `docs/179-evidence-api-surface.md`
- **Evidence object catalog (kinds + schemas + examples):** `docs/EVIDENCE_OBJECT_CATALOG.md`
- **Public commitments + transparency logs (publish hashes without disclosure):** `docs/261-public-commitments-and-transparency-logs-for-election-evidence.md`
- **Canonicalization + signing + timestamping (make commitments stable and checkable):** `docs/265-canonicalization-signing-timestamping-and-proof-packaging.md`
- **Jurisdictional policy knobs (bounded registry; cite-first):** `docs/262-jurisdictional-policy-surface-registry.md`
- **Voter registration & list maintenance (VRDB integrity without PII dumps):** `docs/269-voter-registration-and-list-maintenance-as-evidence-surfaces.md`
- **Electronic pollbooks & voter check-in (EPB integrity without voter-file leakage):** `docs/270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`
- **Ballot accounting + reconciliation (end-to-end counts; canvass bridge):** `docs/273-ballot-accounting-and-reconciliation-as-evidence-surfaces.md`
- **Verifier MVP path (packet → policy → report):** `docs/188-verifier-minimum-viable-path.md`
- **Publishable verifier output:** `docs/193-publishable-verifier-reports.md` + `docs/VERIFIER_PROBLEM_CODES.md`
- **Observer kit (offline verification):** `docs/177-observer-kit-offline-verification-walkthrough.md`
- **Pre‑election testing (L&A + supporting tech evidence surfaces):** `docs/255-logic-and-accuracy-and-pre-election-testing-as-evidence-surfaces.md`
- **Physical security + access control (publishable digests; no sensitive layouts):** `docs/266-physical-security-and-access-control-as-evidence-surfaces.md`
- **Personnel security + insider risk + worker safety (bounded, privacy-first):** `docs/267-personnel-security-insider-risk-and-worker-safety-as-evidence-surfaces.md`
- **Contingency planning + continuity of operations (COOP) as evidence surfaces:** `docs/276-contingency-planning-and-continuity-of-operations-as-evidence-surfaces.md`
- **Observability, metrics, and anomaly response (digest-first):** `docs/277-observability-metrics-and-anomaly-response-as-evidence-surfaces.md`
- **Software updates + configuration control (baselines, patches, drift):** `docs/256-software-updates-and-configuration-control-as-evidence-surfaces.md`
- **Incident comms as evidence (rumor control):** `docs/186-incident-communications-as-evidence.md`
- **Rumor control corrections (mis/disinfo response as evidence surfaces):** `docs/268-rumor-control-and-mis-disinformation-response-as-evidence-surfaces.md`
- **Comms authenticity (synthetic media minimum):** `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- **Deepfake frontier + time-to-refute discipline:** `docs/240-deepfake-frontier-and-time-to-refute.md`
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
- **Post-election audits / RLAs as publishable evidence surfaces:** `docs/260-risk-limiting-audits-and-post-election-tabulation-audits-as-evidence-surfaces.md`
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
5. `256–258` change control + supply chain + exercises (updates, drift, vendor transparency, preparedness artifacts)

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


## Stewardship

- Feedback integration map: `FEEDBACK_INTEGRATION_LEDGER.md`
- Claude normative requirements (maintainer checklist): `docs/244-claude-normative-requirements-digest.md`

## Feedback trail (auditability)

- Cross-walk from Claude feedback → canonical implementation surfaces: `FEEDBACK_INTEGRATION_LEDGER.md`.
- Preserved feedback source: `evidence/feedback/claude-opus4_6-feedback_2026-02-27.md`.

- Adjudication, duplication, and voter intent as evidence surfaces (privacy-first): `docs/254-adjudication-duplication-and-voter-intent-as-evidence-surfaces.md`
- Ballot design, ballot building, and proofing as evidence surfaces: `docs/263-ballot-design-ballot-building-and-proofing-as-evidence-surfaces.md`

### Interoperability (schemas + profiles)
- `docs/275-election-data-interoperability-and-schema-registry.md` — publishable schema/profile commitments (hashes-first), anchored to NIST CDFs.
