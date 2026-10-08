# Start here (read-order + “what this project is about”)

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

- **Maintainer / steward:** `150` (change protocol) → `227` (refactor + growth protocol) → `adr/INDEX.md` (decision register) → `151`/`161`/`214`/`230`/`233` (sources + citation map + generated indexes + pinning workflow) → `162` (release gate) → `docs/PUBLIC_SURFACES.md` (stable external surfaces) → `153` (freeze plan) → `183` (stewardship posture).
- **Verifier implementer:** `173` (evidence packets) → `176` (canonicalization + signing) → `179` (evidence API surface) → `docs/EVIDENCE_OBJECT_CATALOG.md` (kinds + schemas + examples) → `188` (MVP path) → `193` (publishable verifier reports) + `schemas/` + `artifacts/examples/`.
- **Election operator / program lead:** `08` (operations) → `215` (lifecycle evidence map) → `216` (incident triage quickmap) → `217` (claim cards) → `218` (epistemic tags) → `219` (uncertainty-safe updates) → `220` (notice graph resolution) → `221` (monitoring) → `222` (divergence handoff bundle) → `223` (capture notes) → `224` (request context) → `225` (redaction logs) → `04` (transparency log) → `23` (witness gossip) → `63–72` (results + ENR + publication) → `87`/`186–187` + `194–206` (incident comms, synthetic-media posture, rumor-control/status surfaces, feeds, parity snapshots, inspection challenges, discovery bootstrap, and cache/freshness posture) + Track A gate (`track-a/MVR_CHECKLIST.md`).
- **Researcher (remote return / North Star):** `172` (open questions) → Track B bundle (`track-b/BUNDLE.md`) and Track C bundle (`track-c/BUNDLE.md`) + `155–157` (attestation/provenance stack).

If you're maintaining or extending this archive, read:
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)


## Recent additions (v40–v206)
This archive evolves quickly. To keep this “start here” doc readable, this section lists only **high‑leverage themes**.
For the complete change history, see `CHANGELOG.md` (and the compact near‑term queue in `docs/207`).

- **Public communications as verifiable evidence (Track A):** PublicNotice as the canonical comms artifact (`186`) plus
  rumor‑control/status surfaces (`195`), bounded discovery feeds (`200`), effective-state semantics (`220`), monitoring + convergence (`221`), divergence handoff bundles (`222`), official channel directory (`203`), domain‑first
  `.well-known` bootstrap (`204`), and cache/freshness posture (`205`) plus a bounded cache/freshness test plan checklist (see `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md`).
- **AI‑era authenticity posture (Track A):** minimum controls for synthetic media and forged comms (`194`), plus a verifiable
  PublicNotice signing key allow‑list (`208`) and auditable official‑surface security snapshots (`199`).
- **Split‑view / missingness hardening (Track A):** portable parity snapshots (`201`) (plus a tight snapshot diff helper),
  inspection challenges (`202`), liveness beacons as “missingness about missingness” (`210`),
  capture notes for raw fetch provenance (`223`), a tight request-context/variant-probing discipline (`224`), hashes-first redaction logs for transformed exhibits (`225`), a digest-only public fingerprint report for mirroring/equality checks (`226`, now also integrated into `tools/observer_verify_packet.py`), and a bounded anomaly-code rollup helper (`tools/surface_anomaly_rollup.py`).
- **Verifier ecosystem comparability (Shared):** publishable verifier reports (`193`) with stable problem codes
  (`docs/VERIFIER_PROBLEM_CODES.md`) **and profile IDs** (`docs/VERIFIER_PROFILES.md`) for compact capability claims + drift firewalls, plus a minimal policy-profile digest pin (`PacketVerificationReport.policy_profile_sha256`) and optional profile-object shipping for minimal report packets (see `188`, `193`, and `schemas/VerifierPolicyProfile.json`). Report packets now also repeat the policy pin on the envelope subject (digest only) for index-only scans. Packet reports also include an optional `manifest_jcs_sha256` pin (RFC8785-JCS canonical bytes) so bundle boundaries remain comparable across mirrors even if JSON is reformatted.
- **Governance/capture resistance surfaces (Shared):** witness governance as a publishable, portable surface (`hfv.witness.*`;
  see `132–135` and the witness-set anchoring notes in `204`/`210`).
- **Courtroom‑friendly packaging (Track A):** bounded evidence bundle recipes (`211`) aligned to catastrophe classes (`171`).
- **Epistemic tags + confidence (Shared):** a small labeling discipline for deception-resistant statements in claim cards and public notices (`218`).
- **Uncertainty-safe public updates (Track A):** a compact update contract (tags + commitments) for PublicNotice and signed statements (`219`) plus a 60s review quickcheck (`artifacts/checklists/public-update-epistemic-quickcheck.md`).
- **Notice graph resolution (Track A):** deterministic “current state” semantics for `supersedes_notice_id` and `correction_of_notice_id` so status boards and monitors render updates/corrections consistently (`220`).
- **Publication hygiene (Track A):** bounded public redaction checklist for releases and incident artifacts (`artifacts/checklists/public-artifact-redaction-checklist.md`), a conservative packet linter (`tools/public_artifact_lint.py`) (now also linting canonical `vary[...]`/`age[...]` compact notes), plus a bounded PublicationCoverageReport card helper for deadline-coverage summaries (`tools/publication_coverage_report_card.py`, `187`).
- **Compact request-context notes (Track A):** the `req[...] vary[...] age[...]` notation used in parity/capture artifacts is now explicitly specified and drift-tested (syntax + canonicalization contract + test vectors: `232`, `artifacts/test-vectors/compact_context_vectors.json`).
- **Placeholder domain conventions (Shared):** examples and templates now use RFC-reserved placeholders (`.example`, `.invalid`, doc IP ranges) and avoid restricted/loaded TLDs in copy-pasteable artifacts (`231`).
- **Lean drift firewalls (Maintainers):** example-packet payloads now have a bounded payload-vs-schema tripwire (`scripts/check_example_payloads_against_schemas.py`) to prevent silent rot, and normative docs are prevented from accreting new citations onto tombstone aliases; Track A docs may not cite unpinned external sources, and across the archive `source:` citations must be pinned (use `xref:` for unpinned/informative refs). Refactor/growth protocol: `227`.
- **Research → deployable promotion protocol (Shared):** a staged path (E0–E3) for advancing items from the backlog into stable surfaces without leaking untested assumptions into Track A (`229`; see also `172`).
- **External source pinning made navigable (Shared):** generated, no‑URL external-sources indexes (`214` flat; `230` grouped by primary tag) plus a small maintainer review queue (`docs/EXTERNAL_SOURCE_REVIEW_QUEUE.md`) now list lockfile IDs + pin status + retrieval date + tags to keep citations tight without bundling third‑party artifacts. Core NIST Voting CDF specs + implementation guidance are now **sha256 pinned** and cited as `source:` in Track A (`62`, `70`). Unpinned entries require explicit pin‑exemption + review‑by (`228`), and maintainers have a practical pinning workflow (`233`).
- **Operator minimum checklist (Track A):** rumor-control/status surfaces now include a size-disciplined “minimum deployable checklist” (`195.6`) and the external-sources index adds a small pin-first shortlist to keep drift resistance improving without archive bloat.
- **Lifecycle evidence map (Track A):** a one-page phase map (`215`) that links the real-world election timeline to the archive’s evidence surfaces and operator checklists (intended to reduce “where do I start?” confusion without adding new kinds).

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

The primary reader is an **LLM maintainer**. Start with the claims contract:
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
