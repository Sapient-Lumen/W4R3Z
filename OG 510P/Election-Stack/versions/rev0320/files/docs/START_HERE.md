# Start here (read-order + “what this project is about”)

**Track:** Shared


> "Assume humans compromise systems, build evidence that survives it, and maximize the odds of justified eudaimonia for the innocent, future generations of humans and AI, and all agents who might possibly be able to change the course of history appropriately."
>
> *(This is intentionally “squishy.” Do not sanitize it into false precision. Treat uncertainty as a first-class citizen and pursue justice as optimistically as we can.)*

This archive is the working spec pack for **The Election Stack**: a **research + engineering** program for an election **transparency and evidence stack**.

It is deliberately split into **three tracks** so we can pursue an ambitious North Star without confusing
what is deployable today.

- **Track A — Deployable Core:** evidence infrastructure that can wrap paper/BMD/in-person workflows.
- **Track B — Remote Return / Hard-mode Research:** constrained experiments, with explicit non-claims.
- **Track C — North Star:** “fully electronic voting in its best imaginable form” — attestable devices,
  transparent manufacturing/provenance, and a verification ecosystem hardened against capture.


## Role-based reading paths (fast)

If you want a file-name based map (and a strict “what to ignore until needed” guardrail), start with:
- `docs/242-audience-reading-paths-and-what-to-ignore.md`

- **Maintainer / steward:** `150` (change protocol) → `227` (refactor + growth protocol) → `adr/INDEX.md` (decision register) → `151`/`161`/`214`/`230`/`233` (sources + citation map + generated indexes + pinning workflow) → `162` (release gate) → `docs/PUBLIC_SURFACES.md` (stable external surfaces) → `153` (freeze plan) → `183` (stewardship posture).
- **Verifier implementer:** `173` (evidence packets) → `176` (canonicalization + signing) → `179` (evidence API surface) → `docs/EVIDENCE_OBJECT_CATALOG.md` (kinds + schemas + examples) → `188` (MVP path) → `193` (publishable verifier reports) + `schemas/` + `artifacts/examples/`. *(Also see `docs/265-canonicalization-signing-timestamping-and-proof-packaging.md` for the CPP pattern and transparency-log option.)*
- **Election operator / program lead:** `08` (operations) → `276` (continuity/COOP as evidence) → `266` (physical security as evidence) → `215` (lifecycle evidence map) → `216` (incident triage quickmap) → `217` (claim cards) → `218` (epistemic tags) → `219` (uncertainty-safe updates) → `220` (notice graph resolution) → `221` (monitoring) → `222` (divergence handoff bundle) → `223` (capture notes) → `224` (request context) → `225` (redaction logs) → `04` (transparency log) → `23` (witness gossip) → `63–72` (results + ENR + publication) → `87`/`186–187` + `194–206` + `240` (incident comms, synthetic-media posture, rumor-control/status surfaces, feeds, parity snapshots, inspection challenges, discovery bootstrap, and cache/freshness posture) + Track A gate (`track-a/MVR_CHECKLIST.md`).
- **Researcher (remote return / North Star):** `172` (open questions) → Track B bundle (`track-b/BUNDLE.md`) and Track C bundle (`track-c/BUNDLE.md`) + `155–157` (attestation/provenance stack).

If you're maintaining or extending this archive, read:
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)


## 60-minute adopter path (outside view)

If you have ~60 minutes and you are deciding whether to pilot this with real institutions:

1. `docs/track-a/README.md` (what Track A is, what it wraps, what it emits)
2. `docs/166-scope-and-claims-contract.md` (what we assert)
3. `docs/167-non-claims-and-boundaries.md` (what we explicitly do **not** assert)
4. `docs/215-election-lifecycle-evidence-map.md` (where the evidence surfaces fit in a real election timeline)
5. `docs/track-a/PILOT.md` (what a minimal “one county” pilot looks like)

Optional (for public legitimacy framing):
- `docs/track-a/VOTER_VERIFICATION.md` + `docs/track-a/PERSONS_PATH.md`

Adopter-facing materials should usually be **generated from templates** (not embedded as a growing essay collection):
- `artifacts/templates/adopter-briefing.md` (2-page briefing template)
- `artifacts/templates/adopter-slide-deck-outline.md` (10-slide outline template)
- `artifacts/templates/procurement-language.md` (RFP / procurement language fragments)
- `artifacts/templates/after-action-report.md` (pilot AAR template)


## Recent additions (v40–v306)
This archive evolves quickly. To keep this “start here” doc readable, this section lists only **high‑leverage themes**.
For the complete change history, see `CHANGELOG.md` (and the compact near‑term queue in `docs/207`).


- **Continuity / contingency planning (Shared):** bounded COOP evidence surfaces (posture statement, plan digest, degraded modes, dependency digest, and continuity incident capsules) (`docs/276-*`).
- **Jurisdictional policy surface registry (Shared):** bounded taxonomy of jurisdiction-specific “policy knobs” with authoritative citations, without state-table bloat (`docs/262-*`).
- **Voter registration & list maintenance (Shared):** publishable digests for VRDB posture and lawful list maintenance without voter-file dumps (`docs/269-*`).
- **Ballot design/build/proof evidence surfaces (Shared):** publishable digests + approvals for ballot production, without precinct mapping disclosure (`docs/263-*`).
- **Adopter path drift firewall (Shared):** 60‑minute entry path smoke test checklist + bounded log so entry points don’t silently rot (`artifacts/checklists/adopter-60-minute-path-smoke-test.md`, `artifacts/registries/adopter-path-smoke-tests.csv`).

- **Checklist→capability gate (Shared):** new operator checklists/playbooks are treated as *draft* unless they have a drill scenario + publishable AAR/packet outputs; wired into maintainer + growth protocols and the exercises program (`docs/150`, `docs/227`, `docs/86`).

- **Time-to-refute measurement (Track A):** authenticity/disinformation response is treated as a measurable operational budget (TTR‑1/TTR‑2) and logged as bounded rows in `artifacts/registries/time-to-refute-evaluations.csv`; enforced via maintainer + change-review gates (`docs/240`, `docs/150`, catastrophe ordering checklist).

- **Claim discipline before implementation (Shared/Track A):** core normative docs now include a read-first pointer to `docs/166` + `docs/167`; do not start with the protocol spec.

- **Adopter reality + anti-theater posture (Shared/Track A):** the adopter briefing template now includes cost/staffing ballparks and “legibility theater” guardrails, and Track A docs explicitly name minimum substantive checks (independent verifier output, dissent/liveness, offline verification). Procurement language now includes anti-capture interoperability clauses (see `artifacts/templates/adopter-briefing.md`, `docs/track-a/README.md`, `artifacts/templates/procurement-language.md`).


- **Supply chain transparency expectations (Track A):** Track A now explicitly distinguishes evidence-layer supply-chain controls vs proprietary voting-system opacity; pilots should publish config/version IDs and update history as evidence (`docs/17`, `docs/track-a/PILOT.md`).
- **Public communications as verifiable evidence (Track A):** PublicNotice as the canonical comms artifact (`186`) plus
  rumor‑control/status surfaces (`195`), bounded discovery feeds (`200`), effective-state semantics (`220`), monitoring + convergence (`221`), divergence handoff bundles (`222`), official channel directory (`203`), domain‑first
  `.well-known` bootstrap (`204`), and cache/freshness posture (`205`) plus a bounded cache/freshness test plan checklist (see `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md`).
- **AI‑era authenticity posture (Track A):** minimum controls for synthetic media and forged comms (`194`), plus a drillable **authenticity response cell** checklist (`artifacts/checklists/authenticity-response-cell-checklist.md`), plus a verifiable
  PublicNotice signing key allow‑list (`208`) and auditable official‑surface security snapshots (`199`).
  - **Key rotation/rekey discipline for comms keys:** bounded protocol for PublicNotice signing key lifecycle (`239`) + shipped minimal keyset packet example.
- **Split‑view / missingness hardening (Track A):** portable parity snapshots (`201`) (plus a tight snapshot diff helper),
  inspection challenges (`202`), liveness beacons as “missingness about missingness” (`210`),
  capture notes for raw fetch provenance (`223`), a tight request-context/variant-probing discipline (`224`), hashes-first redaction logs for transformed exhibits (`225`), a digest-only public fingerprint report for mirroring/equality checks (`226`, now also integrated into `tools/observer_verify_packet.py`), and a bounded anomaly-code rollup helper (`tools/surface_anomaly_rollup.py`).
- **Verifier ecosystem comparability (Shared):** publishable verifier reports (`193`) with stable problem codes
  (`docs/VERIFIER_PROBLEM_CODES.md`) **and profile IDs** (`docs/VERIFIER_PROFILES.md`) for compact capability claims + drift firewalls, plus a minimal policy-profile digest pin (`PacketVerificationReport.policy_profile_sha256`) and optional profile-object shipping for minimal report packets (see `188`, `193`, and `schemas/VerifierPolicyProfile.json`). Report packets now also repeat the policy pin on the envelope subject (digest only) for index-only scans. Packet reports also include an optional `manifest_jcs_sha256` pin (RFC8785-JCS canonical bytes) so bundle boundaries remain comparable across mirrors even if JSON is reformatted.
- **Governance/capture resistance surfaces (Shared):** witness governance as a publishable, portable surface (`hfv.witness.*`;
  see `132–135` and the witness-set anchoring notes in `204`/`210`).
- **Courtroom‑friendly packaging (Track A):** bounded evidence bundle recipes (`211`) aligned to catastrophe classes (`171`).
  - v240: added templates for a one‑page crypto primer + expert-declaration outline, and wired admissibility planning into the Track A pilot (`docs/track-a/PILOT.md`).
- **Epistemic tags + confidence (Shared):** a small labeling discipline for deception-resistant statements in claim cards and public notices (`218`).
- **Uncertainty-safe public updates (Track A):** a compact update contract (tags + commitments) for PublicNotice and signed statements (`219`) plus a 60s review quickcheck (`artifacts/checklists/public-update-epistemic-quickcheck.md`).
- **Accountable uncertainty enforcement (Shared):** public comms surfaces now treat epistemic tags + update commitments as an enforced change-review invariant (maintainer + catastrophe review gates + hedge-language drift firewall: `docs/150`, `artifacts/checklists/catastrophe-ordering-review-checklist.md`, `scripts/check_no_hedging_in_public_templates.py`).
- **Notice graph resolution (Track A):** deterministic “current state” semantics for `supersedes_notice_id` and `correction_of_notice_id` so status boards and monitors render updates/corrections consistently (`220`).
- **Publication hygiene (Track A):** bounded public redaction checklist for releases and incident artifacts (`artifacts/checklists/public-artifact-redaction-checklist.md`), a conservative packet linter (`tools/public_artifact_lint.py`) (now also linting canonical `vary[...]`/`age[...]` compact notes), plus a bounded PublicationCoverageReport card helper for deadline-coverage summaries (`tools/publication_coverage_report_card.py`, `187`).
- **Adversarial publication under split delivery (Track A):** clarified common failure modes (A/B, geo/UA variance, WAF/CAPTCHA) and added a drill for selective delivery (`selective_delivery_split_view`) using parity snapshots + bounded request-context notes (`187`, `201`, `223–224`).
- **Compact request-context notes (Track A):** the `req[...] vary[...] age[...]` notation used in parity/capture artifacts is now explicitly specified and drift-tested (syntax + canonicalization contract + test vectors: `232`, `artifacts/test-vectors/compact_context_vectors.json`).
- **Track metadata completion (Shared):** operator-facing artifacts (checklists/templates) and ADRs now carry `**Track:** …` headers so documents remain self-scoping when copied or printed.
- **Placeholder domain conventions (Shared):** examples and templates now use RFC-reserved placeholders (`.example`, `.invalid`, doc IP ranges) and avoid restricted/loaded TLDs in copy-pasteable artifacts (`231`).
- **Archive can be wrong (Maintainers):** the archive/spec/tooling can be wrong; the self-threat model + minimum response loop are now explicit (`docs/243-archive-self-threat-model-and-spec-correctness.md`), alongside the spec-error response note template + playbook (PO‑104 / HZ‑024) (`docs/183` + `artifacts/playbooks/spec-error-response-playbook.md`).
- **External review is now a repeatable capability (Maintainers):** a surface-focused external-review session checklist makes critique actionable without “read the whole archive” failure modes (`artifacts/checklists/external-review-session-checklist.md`).
- **External review is now auditable (Maintainers):** a small registry logs which surfaces were externally reviewed (who/when/what + bounded refs/digests), without bundling long appendices (`artifacts/registries/external-review-log.csv`, `243`).

- **Lean drift firewalls (Maintainers):** example-packet payloads now have a bounded payload-vs-schema tripwire (`scripts/check_example_payloads_against_schemas.py`) to prevent silent rot, and normative docs are prevented from accreting new citations onto tombstone aliases; Track A docs may not cite unpinned external sources, and across the archive `source:` citations must be pinned (use `xref:` for unpinned/informative refs). Refactor/growth protocol: `227`.
- **Research → deployable promotion protocol (Shared):** a staged path (E0–E3) for advancing items from the backlog into stable surfaces without leaking untested assumptions into Track A (`229`; see also `172`).
- **Promotion under political pressure is a first-class hazard (Shared):** drills and hazard register now explicitly treat premature Track B→A promotion (especially remote ballot return) as an integrity/capture incident (`229.7`, `artifacts/registries/drill-scenarios.csv` `premature_promotion_remote_return`, HZ‑025).
- **Verification capacity as a first-class constraint (Shared):** the backlog now explicitly tracks who can actually run verifiers and how verdicts reach the public under adversarial conditions (`172.2.2`).
- **Verifier onboarding is now templated (Shared):** a 1–2 page onboarding mini‑curriculum template for newsrooms/watchdogs/campaigns to pre‑position offline verification and publish replayable outputs (`artifacts/templates/verifier-onboarding-mini-curriculum.md`, `241`).
- **Non-human franchise as explicit research (Shared):** the backlog now names the identity-integrity / sybil constraint for AI standing without implying Track A readiness (`docs/172-open-research-questions-and-experiment-backlog.md` (section 172.6), non-claim `167` N‑7).
- **Privacy vs verifiability (Track B; shared implications):** the backlog now explicitly tracks the tension between unlinkable eligibility and public verifiability for revocation/dispute lanes (`172.3.1`, `15`, `81`).
- **External source pinning made navigable (Shared):** generated, no‑URL external-sources indexes (`214` flat; `230` grouped by primary tag) plus a small maintainer review queue (`docs/EXTERNAL_SOURCE_REVIEW_QUEUE.md`) now list lockfile IDs + pin status + retrieval date + tags to keep citations tight without bundling third‑party artifacts. Core NIST Voting CDF specs + implementation guidance are now **sha256 pinned** and cited as `source:` in Track A (`62`, `70`). Unpinned entries require explicit pin‑exemption + review‑by (`228`), and maintainers have a practical pinning workflow (`233`).
- **Operator minimum checklist (Track A):** rumor-control/status surfaces now include a size-disciplined “minimum deployable checklist” (`195.6`) and the external-sources index adds a small pin-first shortlist to keep drift resistance improving without archive bloat.
- **Lifecycle evidence map (Track A):** a one-page phase map (`215`) that links the real-world election timeline to the archive’s evidence surfaces and operator checklists (intended to reduce “where do I start?” confusion without adding new kinds).
- **Institutional volatility as a first-class risk (Track A):** threat model now includes a scoped “certification/ecosystem compromise” adversary; standards-alignment and results-publishing docs now carry compact pinned references (see `01`, `19`, `63`, `68`, and ``adr/0003-institutional-volatility-as-threat.md``).
- **Results publishing hardening (Track A):** compact results lifecycle taxonomy + correction discipline (`234`), results-object canonicalization + link-forward hashing (`235`), and a tight results-release transparency profile for PBB anchoring/witness checkpointing/time ordering (`236`).
- **Results release packaging clarified (Track A):** RRPs are now published as `EvidenceEnvelope` payloads (`kind: hfv.results.release_package`) to avoid signature-layer ambiguity; PBB `RESULTS` leaves commit to the envelope payload digest (`238`, `adr/0004`).
- **Institutional milestone binding (Track A):** a minimal, digest-first pattern for canvass/certification/recount milestones using `PublicNotice.notice_type=election_milestone` + a stable milestone registry (see `237`).

Earlier high‑leverage additions:
- Public randomness kernel for seeded sampling: `docs/168-public-randomness-beacons-and-seeded-sampling.md`
- Endorsement/reference-value transparency (North Star anti‑capture): `docs/169-endorsement-and-reference-value-transparency.md`
- Supply‑chain provenance profile (SLSA + in‑toto): `docs/170-slsa-and-intoto-provenance-profile.md`

If you ever worry “are we backing away from the full stack?”, the answer is **no**:
the archive is organizing the full stack into *tracks* so claims remain honest and auditable.

## Archive scope without archive bloat

This archive is **full‑stack in design scope**, but **size‑disciplined**:

- Do **not** embed third‑party PDFs or external works wholesale.
- Prefer citations + short excerpts (only when necessary) + pinned sources (`evidence/lock/`).
- Never include secrets (especially private keys): see `docs/189-sensitive-material-and-secrets.md`.
- Prefer original synthesis as **schemas, checklists, drills, and proof obligations**.

The primary **maintenance** reader is an **LLM maintainer**. The primary **deployment** readers are humans in crisis: election operators, legal counsel, journalists, and civil society. Use Track A entry points + templates so those readers can act without absorbing the whole archive.

Start with the claims contract:
- `166-scope-and-claims-contract.md`
- `167-non-claims-and-boundaries.md`

## Entry points (by track)
- **Track A:** `track-a/README.md`
  - Quick: `track-a/BUNDLE.md`
  - Release gate: `track-a/MVR_CHECKLIST.md`
- **Track B:** `track-b/README.md`
  - Quick: `track-b/BUNDLE.md`
- **Track C:** `track-c/README.md`
  - Quick: `track-c/BUNDLE.md`

## Global read order (15–30 minutes)
1. `154-project-scope-and-track-map.md`
2. `166-scope-and-claims-contract.md` + `167-non-claims-and-boundaries.md`
3. `00-design-goals.md`
4. `01-threat-model.md`
5. `04-transparency-log.md` + `23-witness-gossip-and-cross-checkpointing.md`
6. `159-proof-obligations-ledger.md` + `164-proof-obligations-registry.md`
7. `160-generated-canonical-spec-contract.md`
8. Pick a track readme and follow the suggested deep dives.

## If you are maintaining this archive
Start with `150-maintainer-bootstrap-and-change-protocol.md`.

## Canonical evidence packaging (new)
- Evidence envelopes + packet layout: `docs/173-canonical-evidence-envelopes-and-packets.md`
- Coverage accounting deliverable: `docs/174-coverage-accounting-and-representativeness.md`
- Publication compliance coverage: `docs/187-publication-compliance-and-coverage.md`

## Offline verification starting point
If you're an independent observer, start with:
- `docs/188-verifier-minimum-viable-path.md`
- `docs/177-observer-kit-offline-verification-walkthrough.md`
- example packets:
  - `artifacts/examples/evidence_packet_minimal/` (suppression report + required attachments)
  - `artifacts/examples/evidence_packet_enr_receipted/` (ENR update + required attachments)
  - `artifacts/examples/evidence_packet_publication_compliance_minimal/` (TriggerEvents + PublicNotice + publication coverage)
  - `artifacts/examples/evidence_packet_packet_verification_report_minimal/` (publishable packet verification report as evidence)
- reference checker: `tools/observer_verify_packet.py`
- release-gate: `scripts/check_example_packets.py` (keeps examples from silently rotting)


## Stewardship

- Feedback ledger: `../FEEDBACK_INTEGRATION_LEDGER.md`

- **Time-to-refute discipline (AI-era authenticity):** measurable TTR posture + minimal refutation packet shape (`240`) plus drill templates/checklists.
- **Witness behavioral health (beyond cosigning):** capture-resistant witness governance with publishable dissent + health reporting (`135`; evidence kind `hfv.witness.liveness_dissent_report`).
- If you need to move results across systems or publish schemas safely, see `275-election-data-interoperability-and-schema-registry.md`.
