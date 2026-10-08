## v320 (2026-03-04)

- Added `docs/277-observability-metrics-and-anomaly-response-as-evidence-surfaces.md`: digest-first, ops-safe publishable evidence surfaces for operational metrics, alert ledgers, and outage/degraded-mode capsules; composes with incident disclosure (`259`), CommitLog (`261`), and proof packaging (`265`).
- Wired 277 into entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v319 (2026-03-04)

- Added `docs/276-contingency-planning-and-continuity-of-operations-as-evidence-surfaces.md`: bounded COOP evidence surfaces (CPS/CPD/DMR/DID/CIC) with hard anti-targeting stop conditions; composes with drills (`258`), incident comms (`247`, `259`), CommitLog (`261`), and proof packaging (`265`).
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md` (dedup/refresh), `docs/242-audience-reading-paths-and-what-to-ignore.md` (cleanup + 276 pointer), `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, and `docs/START_HERE.md`.

## v318 (2026-03-04)

- Added `docs/275-election-data-interoperability-and-schema-registry.md` (Schema Registry Digest pattern; NIST CDF/ERR + implementation guidance anchors; optional EML reference).
- De-duplicated `ARCHIVE_INDEX.md` “Recently added” list; wired 275 into entry points, reading paths, artifact index, and glossary.

## v317 — 2026-03-04 18:58 America/New_York
- Added `docs/274-cvr-ballot-images-and-public-data-release-governance.md`: Data Release Governance (DRG) pattern for CVRs/ballot images/public election datasets — digest-first provenance, privacy risk screens, explicit stop-conditions, and proof packaging (pairs with `261` + `265`). Primary anchors: NIST SP 1500-103 (CVR CDF), NIST GCR 24-058 (CDF guidance), BPC ballot images/CVRs explainer, Science Advances (2025) on privacy violations, Brennan Center on records/equipment access, EAC VVSG 2.0.
- Repaired `ARCHIVE_INDEX.md` to include pointers for docs 269–274.

## v316 — 2026-03-04 18:52 America/New_York
- Added `docs/273-ballot-accounting-and-reconciliation-as-evidence-surfaces.md`: bounded, privacy-first publishable digests for end-to-end ballot lifecycle accounting (inventory snapshots, ballot accounting ledger digests, polling-place ballot statement digests, central count intake reconciliation digests, and canvass reconciliation bridges). Anchors: EAC Guide to the Canvass; EAC/CISA Inbound Ballot Process; Brennan Center ballot accounting checklist; Election Group ballot management audit.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.
## v315 — 2026-03-04 18:45 America/New_York
- Added `docs/272-mail-ballot-intake-verification-and-processing-as-evidence-surfaces.md`: bounded, privacy-first publishable evidence surfaces for the back-office mail-ballot workflow (intake batch digests, verification rollup digests with reason-code dictionary, cure linkage, opening session ledgers, scanning feed digests, and reconciliation bridges). Explicit anti-weaponization and hard stop conditions. Anchors: CISA signature verification/cure, EAC chain of custody, CISA drop box resource, NCSL verification + ballot processing timing tables.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v314 — 2026-03-04 18:39 America/New_York
- Added `docs/271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`: bounded, privacy-first publishable evidence surfaces for vote-by-mail distribution and return logistics (outbound distribution ledger digests, return-channel ledger digests, optional ballot-tracking status feed digests, and drop box posture/collection digests) with explicit anti-weaponization and anti-PII stop conditions. Anchors: EAC drop box QSG + GCC/SCC resource doc; CISA drop box incendiary-device best practices.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v313 — 2026-03-04 18:33 America/New_York
- Added `docs/270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`: bounded, privacy-first publishable evidence surfaces for electronic pollbooks (EPBs): posture statement, configuration baseline attestation, readiness digest, aggregate-only check-in transaction ledger digest, ballot style assignment digest, sync integrity ledger digest, and outage/queue capsules. Includes strict stop conditions to avoid voter-file leakage, precinct attribution, and operational targeting. Anchors: EAC ESTEP EPB certification requirements and pre-election testing guidance; NIST VTS usability/accessibility EPB series; CISA election security resource library.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v312 — 2026-03-04 18:30 America/New_York
- Added `docs/269-voter-registration-and-list-maintenance-as-evidence-surfaces.md`: bounded, privacy-first evidence surfaces for VRDB posture and lawful list maintenance without voter-file dumps (VR-SPS, LMPD, registration change ledger digest, list maintenance report digest, access/audit log digest). Explicit anti-weaponization stop conditions. Anchors: EAC voter list maintenance best practices, DOJ NVRA guidance, NVRA §8 (52 U.S.C. §20507), NIST VRDB security considerations, and CISA election system hardening guidance.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v311 — 2026-03-04 18:20 America/New_York
- Added `docs/268-rumor-control-and-mis-disinformation-response-as-evidence-surfaces.md`: bounded, verifiable rumor-control corrections as publishable evidence surfaces (RumorControlPack + index + safe verification pointers). Explicit anti-amplification and anti-doxxing stop conditions; composes with PublicNotice feeds, ENR corrections logs, incident disclosure surfaces, CommitLog/transparency logs, and CPP.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v310 — 2026-03-04 18:14 America/New_York
- Added `docs/267-personnel-security-insider-risk-and-worker-safety-as-evidence-surfaces.md`: bounded, publishable proof surfaces for personnel security posture, role/access boundaries, access review ledgers, training/credentialing digests, insider-concern intake capsules, and threat/harassment handling capsules — privacy-first and anti-weaponization. Anchors: EAC poll worker best practices; EAC election official security; EAC personal security & mental health clearinghouse; EAC training tip sheets; CISA Insider Threat Mitigation Guide.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v309 — 2026-03-04 18:05 America/New_York
- Added `docs/266-physical-security-and-access-control-as-evidence-surfaces.md`: bounded, publishable physical-security and access-control evidence surfaces (posture statement, access log digest, key/credential attestation, seal inventory snapshot, facility incident capsule) with strict minimization and anti-weaponization stop conditions. Anchors: CISA physical security guidance/checklist; EAC EMG physical security chapter; EAC chain-of-custody best practices; NIST 800-53 PE controls.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v308 — 2026-03-04 17:52 America/New_York
- Added `docs/265-canonicalization-signing-timestamping-and-proof-packaging.md`: Crypto-Proof Packaging (CPP) pattern (canonicalize → hash → sign → timestamp → optional transparency log) to make publishable evidence surfaces stable and independently checkable without publishing sensitive artifacts.
- Updated entry points and indexes: `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`.

## v307 — 2026-03-04 17:44 America/New_York
- Added `docs/264-recounts-contests-and-certification-disputes-as-evidence-surfaces.md`: bounded publishable evidence surfaces for recounts, administrative contests/challenges, and certification disputes (declarations, custody attestations, tally-change ledgers, docket digests, certification status capsules) with strict privacy/ops-security stop conditions. Anchors: EAC recount + certification resources, NCSL recount overview, and CISA/NASS canvassing timeframes resource.
- Added `MANIFEST.sha256` and regenerated file hashes to match repository integrity expectations referenced in `README.md`.

## v306 — 2026-03-04 17:41 America/New_York
- Added `docs/263-ballot-design-ballot-building-and-proofing-as-evidence-surfaces.md`: bounded, publishable evidence surfaces for ballot production (contest-definition digest → style manifest digest → proof packet → approvals → print/export attestation), privacy-first and anti-weaponization.
- Repaired `ARCHIVE_INDEX.md` to point to real entry docs and recent additions.
- Updated `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, and `README.md` to include doc 263.

## v305 — 2026-03-04 17:35 America/New_York
- Added `docs/262-jurisdictional-policy-surface-registry.md`: Jurisdictional Policy Surface Registry (JPSR) pattern — bounded taxonomy of jurisdiction-specific policy knobs with cite-first authoritative references; hash-commitments rather than state-by-state annex bloat; strict privacy/ops-security stop conditions.
- Updated indexes/paths: `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `ARCHIVE_INDEX.md`, `README.md`.

## v304 — 2026-03-04 17:29 America/New_York
- Added `docs/261-public-commitments-and-transparency-logs-for-election-evidence.md`: digest-first CommitLog Entry (CLE) pattern for publishing public hash commitments with append-only history (transparency-log optional), composed with ENR/audit/incident/change-control evidence surfaces; strict privacy/ops-security/anti-weaponization stop conditions.
- Updated indexes/paths: `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `ARCHIVE_INDEX.md`, `README.md`.

## v303 — 2026-03-04 17:23 America/New_York
- Added `docs/260-risk-limiting-audits-and-post-election-tabulation-audits-as-evidence-surfaces.md`: Audit Publication Pack (APP) pattern for publishable audit proof surfaces (randomness/manifest/custody/discrepancies/escalation) using hashes + digests (privacy-first; anti-weaponization stop conditions), anchored to EAC/NIST/Verified Voting resources.
- Updated indexes/paths: `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `ARCHIVE_INDEX.md`, `README.md`.

## v302 — 2026-03-04 18:22 America/New_York
- Added `docs/259-incident-reporting-and-coordinated-disclosure-as-evidence-surfaces.md`: digest-first, bounded public incident reporting surfaces (Incident Disclosure Stub, Timeline Digest, External Notification Ledger, Public Communications Packet) with explicit anti-weaponization stop conditions, anchored to CISA/EAC/NIST incident guidance.
- Updated indexes/paths: `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `ARCHIVE_INDEX.md`, `README.md`.

## v301 — 2026-03-04 17:09 America/New_York
- Added `docs/258-training-tabletop-and-drills-as-evidence-surfaces.md`: minimal publishable artifacts for training/TTX/drills (charter, scenario abstract, decision/comms log, after-action + improvement ledger) with strict minimization and stop conditions.
- Updated indexes/paths: `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `ARCHIVE_INDEX.md`, `README.md`.

## v300 — 2026-03-04 17:06 America/New_York
- Added `docs/257-supply-chain-procurement-and-vendor-transparency-as-evidence-surfaces.md`: minimal publishable supply-chain artifacts (SBOM/provenance/inventory/vuln handling) + tight procurement clause checklist (no configs, no weaponization).
- Updated indexes and reading paths: `docs/13-artifact-index.md`, `docs/196-core-glossary-and-terms-of-art.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `ARCHIVE_INDEX.md`, `README.md`.

## v299 — 2026-03-04 18:07 America/New_York
- Added `docs/256-software-updates-and-configuration-control-as-evidence-surfaces.md`: minimal publishable artifacts for configuration baselines, approved change windows, software/firmware updates, emergency patches, and drift (hashes + attestations; explicit stop conditions).
- Wired cross-links: `README.md`, `ARCHIVE_INDEX.md`, audience paths, artifact index, glossary; repaired artifact-index row 254 formatting.

**Track:** Shared (change control integrity surfaces)

# Changelog

## v298 — 2026-03-04 17:49 America/New_York
- Added `docs/255-logic-and-accuracy-and-pre-election-testing-as-evidence-surfaces.md`: minimal publishable artifacts for L&A and broader pre-election testing of supporting technologies (hashes + logs; no dumps; explicit stop conditions).
- Wired cross-links: `README.md`, `ARCHIVE_INDEX.md`, audience paths, artifact index, glossary.

**Track:** Shared (pre-election integrity surfaces)

## v297 — 2026-03-04 17:15 America/New_York
- Added `docs/254-adjudication-duplication-and-voter-intent-as-evidence-surfaces.md`: minimal publishable artifacts for adjudication + ballot duplication + voter-intent standards (aggregate, privacy-first; explicit stop conditions).
- Wired cross-links: `README.md`, `ARCHIVE_INDEX.md`, audience paths, artifact index, glossary.

**Track:** Shared (post-capture integrity)

## v296 — 2026-03-04 17:03 America/New_York
- Added `docs/253-public-records-requests-retention-and-access-bounds.md`: minimal publishable PRR logs + response packets + retention attestations (privacy-first; anti-weaponization stop conditions).
- Wired cross-links: `ARCHIVE_INDEX.md`, `README.md`, artifact index, glossary.

**Track:** Shared (meta)




















## v295 — Election night reporting & unofficial results as evidence surfaces (ENR)

- Added `docs/252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md`: minimal publishable artifacts for ENR/unofficial results (non-finality banner, snapshot packs, and corrections log), with safe linkage to signed results releases and canvass reconciliation; anchored to EAC/CISA/NIST references.
- Updated `README.md`, `ARCHIVE_INDEX.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, artifact index (`docs/13-artifact-index.md`), and glossary (`docs/196-core-glossary-and-terms-of-art.md`); regenerated `MANIFEST.sha256`.

## v294 — Provisional ballots, curing, and canvass as evidence surfaces (minimal, privacy-first)

- Added `docs/251-provisional-ballots-curing-and-canvass-as-evidence-surfaces.md`: minimal publishable artifacts for provisional ballots, curing, and canvass reconciliation; strict PII minimization + anti-weaponization stop conditions; anchored to EAC/CISA/NCSL references.

## v293 — Observation & challenge as evidence surfaces (minimal, anti-intimidation)

- Added `docs/250-observation-and-challenge-as-evidence-surfaces.md`: defines minimal publishable observer/session/event/challenge records, strict privacy constraints, and stop-conditions to prevent intimidation/doxxing and dual-use detail.
- Cross-linked `README.md`, `ARCHIVE_INDEX.md`, and `docs/242-audience-reading-paths-and-what-to-ignore.md`.
- Updated artifact index (`docs/13-artifact-index.md`) and glossary (`docs/196-core-glossary-and-terms-of-art.md`); regenerated `MANIFEST.sha256`.

## v292 — Threat model ledger & safe red-teaming guardrails (bounded)

- Added `docs/249-threat-model-ledger-and-safe-red-teaming.md`: a non-weaponizing pattern for maintaining a compact threat-model ledger, publishing proofs safely, and setting stop-conditions for dual-use detail.
- Cross-linked `README.md`, `ARCHIVE_INDEX.md`, and `docs/242-audience-reading-paths-and-what-to-ignore.md`.
- Extended glossary (`docs/196-core-glossary-and-terms-of-art.md`) with minimal assurance vocabulary: TML, threat-informed defense, safe red-teaming.
- Updated artifact index (`docs/13-artifact-index.md`) and regenerated `MANIFEST.sha256`.

## v291 — Accessibility + language access as integrity controls (minimal publishable proofs)

- Added `docs/248-accessibility-usability-and-language-access-as-integrity.md`: minimal control set and minimal publishable-proof set for polling place accessibility, accessible voting equipment, voter-facing web accessibility (WCAG posture), and language assistance workflows; anchored to EAC/DOJ/W3C references (no bulk imports).
- Wired minimal cross-links in `README.md`, `ARCHIVE_INDEX.md`, and `docs/242-audience-reading-paths-and-what-to-ignore.md`; added row 248 to `docs/13-artifact-index.md`; added accessibility/language terms to `docs/196-core-glossary-and-terms-of-art.md`.
- Updated `MANIFEST.sha256` and `VERSION`.

## v290 — Ops controls: comms + chain of custody (publishable proofs, no bloat)

- Added `docs/247-ops-security-controls-comms-and-chain-of-custody.md`: treats public communications and chain of custody as first-class security controls; provides a tiny control matrix and “don’t bloat” publication rules, with pointers to EAC/CISA comms and custody anchors.
- Fixed artifact index row formatting around 245–246 and added row 247.
- Updated `README.md`, `ARCHIVE_INDEX.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, and `docs/196-core-glossary-and-terms-of-art.md` to reference the new ops-controls note.

## v289 — Assurance-case skeleton + evidence minimization pattern

- Added `docs/246-assurance-case-skeleton-and-evidence-minimization.md`: a tight maintainer pattern for a shallow claim tree + evidence minimization rules, with a small anchor-to-surface crosswalk and explicit “stop conditions” for riskier expansions.
- Added minimal index cross-links (README, ARCHIVE_INDEX, reading paths) and a small glossary addition.

## v288 — External anchors map (VVSG/NIST/CISA) + glossary linkage

- Added a bounded “external anchors” map to keep Track A/B/C reasoning tethered to widely used standards/guidance without importing compliance theater: `docs/245-external-standards-and-alignment-map.md`.
- Added minimal cross-links from `README.md`, `ARCHIVE_INDEX.md`, the artifact index (`docs/13`), and the core glossary (`docs/196`).

## v287 — Claude feedback coherentification (promotion guardrails become auditable)

- Added a bounded promotion decision log so Track B/C → Track A promotions (especially remote ballot return) are auditable without bundling long review appendices: `artifacts/registries/promotion-events.csv` (store only pointers/digests + ADR IDs).
- Wired the log into the non‑waivable remote‑return gate (`docs/229` §229.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §1.5) and made it part of the maintainer coherence gate (`docs/150` §150.7).
- Updated the Claude normative requirements digest (NR‑13), the registries index (`artifacts/registries/README.md`), and the feedback integration ledger (§11) to reference the new canonical surface.

## v286 — Claude feedback coherentification (drills become auditable via run log)

- Added a bounded drill run log to make “checklist → capability” auditable without bundling long exercise reports: `artifacts/registries/drill-runs.csv` (planned/completed + pointers only).
- Wired the log into the exercises program (`docs/86`) and scenario library (`docs/90`), and added a drill-run ID field to the AAR template (`artifacts/templates/after-action-report.md`).
- Enforced “planned drill run” bookkeeping for new/changed drill scenarios and operator checklists in maintainer/change-review gates (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Updated the Claude normative requirements digest (NR‑07) and the feedback integration ledger (4b) to include the new canonical surface.

## v285 — Claude feedback coherentification (turnout-oracle risk becomes auditable)

- Added a bounded turnout-oracle / turnout-surveillance risk assessment quickcheck + log for eligibility/revocation transparency work: `artifacts/checklists/turnout-oracle-risk-quickcheck.md`, `artifacts/registries/turnout-oracle-risk-assessments.csv` (store only pointers/digests).
- Wired the assessment into the Track B eligibility/revocation docs (`docs/75`, `docs/81`) and updated hazard `HZ‑026` to reference the new bounded recordkeeping.
- Enforced the boundary as a maintainer + change-review gate (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6) so transparency surfaces don’t silently become a turnout oracle.
- Updated the Claude normative requirements digest (NR‑16) and the feedback integration ledger (7.1) to include the new canonical enforcement surfaces.


## v284 — Claude feedback coherentification (representation duty + material floor enforced)

- Strengthened the witness/monitor public profile template with explicit **representation duty** and **material floor/accessibility** sections: `artifacts/templates/witness-profile.md`.
- Wired those expectations into operational surfaces: `artifacts/checklists/witness-ops-checklist.md`, `artifacts/checklists/monitor-accountability-checklist.md`, `docs/135-...`, `docs/131-...`.
- Added a small material-floor/accessibility recommendation block to the Track A pilot guide: `docs/track-a/PILOT.md`.
- Added an explicit change-review/maintainer gate for edits to voter-facing legitimacy framing surfaces (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Updated the Claude normative requirements digest (NR‑06) and the feedback integration ledger (4a) to include the new enforcement surfaces.


## v283 — Claude feedback coherentification (adopter entry path becomes auditable)

- Added a bounded 60‑minute adopter-path smoke test checklist + log so the “read these first” entry path doesn’t silently rot: `artifacts/checklists/adopter-60-minute-path-smoke-test.md`, `artifacts/registries/adopter-path-smoke-tests.csv`.
- Wired the smoke test into maintainer/change-review gates for edits to `README.md` 60‑minute path, `docs/START_HERE.md`, `docs/242`, and adopter briefing templates (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Updated the Claude normative requirements digest (NR‑02) and the feedback integration ledger (3a, 3d) to include the new enforcement surfaces.
- Regenerated the **PacketVerificationReport minimal example packet** so `tool.version` / `tool.archive_version` pins match the archive `VERSION` after the bump.
- Bumped `VERSION` to **v283** and regenerated `MANIFEST.sha256`.

## v282 — Claude feedback coherentification (time-to-refute becomes auditable)

- Added a bounded time-to-refute evaluation log to make authenticity/disinformation readiness measurable (TTR‑1/TTR‑2) without bundling long reports: `artifacts/registries/time-to-refute-evaluations.csv` (store only pointers/digests).
- Wired the log into the deepfake/time-to-refute posture (`docs/240`) and the exercises program (`docs/86`), and recorded it in the AAR template.
- Enforced as a maintainer + change-review gate for changes that affect authenticity response workflow or rumor-control/status-board semantics (`docs/150` 150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).

## v281 — Claude feedback coherentification (witness behavioral health made auditable)

- Added a bounded witness behavioral health log to make “witnesses exist” → “witnesses are behaving independently” auditable without bundling long reports: `artifacts/registries/witness-health-log.csv` (store only pointers/digests).
- Wired the log into witness governance and operations surfaces (`docs/135` WIT‑7; `artifacts/checklists/witness-ops-checklist.md`; `artifacts/checklists/witness-rotation-execution-checklist.md`).
- Enforced witness-health recordkeeping as a maintainer/change-review gate (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Updated the Claude normative requirements digest (NR‑10) and the feedback integration ledger to include the new canonical enforcement surfaces.
- Regenerated the **PacketVerificationReport minimal example packet** so `tool.version` / `tool.archive_version` pins match the archive `VERSION` after the bump.

## v280 — Claude feedback coherentification (legibility-theater enforcement + MAPT log)

- Added a bounded MAPT results log so “MAPT was run” is auditable without bundling long incident notes: `artifacts/registries/mapt-evaluations.csv`.
- Wired MAPT recordkeeping into the publication-compliance doc and the Track A pilot checklist so pilots/drills can publish a digest-first MAPT outcome (`docs/187`, `docs/track-a/PILOT.md`).
- Enforced MAPT-as-a-gate for publication pointer surfaces in the maintainer coherence protocol and catastrophe-ordering review checklist (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6), treating recurring failures as `HZ‑027`.
- Tightened the AAR template to record the MAPT log row(s) alongside other digest-first outputs (`artifacts/templates/after-action-report.md`).
- Updated the Claude normative requirements digest (NR‑04) and the feedback integration ledger (3c) to include the new canonical enforcement surfaces.
- Regenerated the **PacketVerificationReport minimal example packet** so `tool.version` / `tool.archive_version` pins match the archive `VERSION` after the bump.
- Bumped `VERSION` to **v280** and regenerated `MANIFEST.sha256`.

## v279 — Claude feedback coherentification (bounded admissibility planning index)

- Added a new bounded registry to track jurisdiction-specific admissibility planning without embedding long legal memos: `artifacts/registries/admissibility-jurisdiction-index.csv` (one row per venue; store only pointers/digests).
- Wired the registry into court-proofing and bundle-recipe guidance so “evidence is usable” planning stays visible and size-disciplined (`docs/43`, `docs/211`, `docs/track-a/PILOT.md`).
- Updated the Claude normative requirements digest (NR‑03) and the feedback integration ledger (3b) to include the new canonical planning surface.
- Regenerated the **PacketVerificationReport minimal example packet** so `tool.version` / `tool.archive_version` pins match the archive `VERSION` after the bump.
- Bumped `VERSION` to **v279** and regenerated `MANIFEST.sha256`.

## v278 — Claude feedback coherentification (accountable uncertainty gates)

- Added **NR‑15** to the Claude normative requirements digest: public comms must use explicit epistemic tags (`218`) and uncertainty‑safe update commitments (`219`), not bespoke hedge-language (`docs/244`).
- Wired the same requirement into the maintainer coherence gate and catastrophe-ordering review checklist so public-facing comms drift is caught during change review (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Updated the Claude feedback integration ledger mapping for epistemic tags/anti-hedging enforcement (`FEEDBACK_INTEGRATION_LEDGER.md`).
- Regenerated the **PacketVerificationReport minimal example packet** so `tool.version` / `tool.archive_version` pins match the archive `VERSION` after the bump (keeps offline examples replayable; release-gate drift firewall).
- Bumped `VERSION` to **v278** and regenerated `MANIFEST.sha256`.


## v277 — Claude feedback coherentification (external review becomes auditable)

- Added a new bounded registry for surface-focused external review sessions (who/when/what surface + challenge-report pointers), so “external review happened” is visible without bundling appendices: `artifacts/registries/external-review-log.csv`.
- Wired the external-review log expectation into the maintainer coherence gate for spec/tool correctness surfaces and Track A claim promotion (`docs/150` §150.7).
- Documented the external-review lane alongside CI release gates (`docs/162`), and updated the self-threat model to require logging sessions (`docs/243`).
- Updated the Claude normative requirements digest (NR‑09) and the integration ledger to point to the new auditable surface.
- Bumped `VERSION` to **v277** and regenerated `MANIFEST.sha256`.


## v276 — Claude feedback coherentification (schema/evidence objects must serve a dispute)

- Added an explicit ‘new evidence object’ gate: new schemas/kinds/POs/verifier outputs MUST name the plausible dispute they serve and update the claim→PO→evidence mapping (`artifacts/claims/claim-evidence-matrix.csv`, `docs/159`).
- Wired the same gate into maintainer change protocol and catastrophe-ordering review so archive growth remains mission-tethered, not spec theater (`docs/150` §150.7; `artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Tightened growth discipline to require dispute justification when adding schemas (`docs/227` §227.4.1).
- Updated the Claude normative requirements digest (NR‑01 enforcement surfaces).
- Bumped `VERSION` to **v276** and regenerated `MANIFEST.sha256`.


## v275 — Claude feedback coherentification (dispute‑lane usability gate)

- Added an explicit “dispute‑lane evidence surface” gate so changes to envelope kinds / bundle semantics also update court-proofing and admissibility planning artifacts (`artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Wired the same gate into the maintainer coherence protocol for Track A public/operational surfaces (`docs/150-maintainer-bootstrap-and-change-protocol.md` §150.7).
- Updated the Claude normative requirements digest (NR‑03 surfaces) and the integration ledger mapping for admissibility/use-in-court.
- Bumped `VERSION` to **v275** and regenerated `MANIFEST.sha256`.


## v274 — Claude feedback coherentification (checklist→drill capability gate)

- Strengthened the anti-theater posture (“a checklist is not a capability unless drilled”) by wiring a drillability requirement into maintainer and growth protocols (`docs/150` §150.7; `docs/227` §227.4.1b) and the exercises program (`docs/86`).
- Updated the catastrophe ordering review checklist to require drillable operational surfaces when introducing/altering checklists/playbooks (`artifacts/checklists/catastrophe-ordering-review-checklist.md` §6).
- Extended the Claude normative requirements digest with an explicit NR‑14 for drilled capability (`docs/244-...`) and updated the integration ledger mapping for drills.
- Bumped `VERSION` to **v274** and regenerated `MANIFEST.sha256`.



## v273 — Claude feedback coherentification (NR‑13 enforcement gates)

- Strengthened the *non‑waivable* promotion guardrails for remote ballot return by adding an explicit gate to the catastrophe ordering review checklist (`artifacts/checklists/catastrophe-ordering-review-checklist.md` §1.5) and linking it from the promotion protocol (`docs/229-...` §229.7).
- Updated the procurement language template to mark remote-ballot-return promotion guardrails as non‑waivable (`artifacts/templates/procurement-language.md` §10).
- Linked the normative requirements digest from the top-level archive index (`ARCHIVE_INDEX.md`).
- Bumped `VERSION` to **v273** and regenerated `MANIFEST.sha256`.


## v272 — Claude normative requirements digest (maintainer non‑negotiables)

- Added a compact maintainer-facing checklist of normative requirements derived from the preserved Claude feedback artifact, pointing to canonical implementation surfaces without duplicating feedback text (`docs/244-claude-normative-requirements-digest.md`).
- Linked the digest from stewardship/audit surfaces (`README.md`, `FEEDBACK_INTEGRATION_LEDGER.md`) and added it to the numbered artifact index (`docs/13-artifact-index.md`).
- Bumped `VERSION` to **v272** and regenerated `MANIFEST.sha256`.

## v271 — Claude feedback coherentification (external review as repeatable capability)

- Added a bounded external-review session checklist so “spec could be wrong” reviews are surface-focused, reproducible, and produce actionable challenge+response artifacts (`artifacts/checklists/external-review-session-checklist.md`).
- Updated the archive self-threat model to require surface-focused external review before promoting new claims into Track A (`docs/243-archive-self-threat-model-and-spec-correctness.md`).
- Added the jurisdictional admissibility matrix template to the court-proofing doc’s canonical template list (`docs/43-evidence-bundles-and-court-proofing.md`).
- Bumped `VERSION` to **v271**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.


## v270 — Claude feedback coherentification (enforced anti-hedge discipline in public templates)

- Added a release-gate drift firewall to prevent hedge-language from sneaking into public-facing templates and Track A adopter/voter narrative docs (require explicit epistemic tags instead): `scripts/check_no_hedging_in_public_templates.py`.
- Removed remaining “appears/seems” wording in targeted public-facing surfaces (observer kit README, verifier onboarding mini-curriculum, voter verification story) to keep uncertainty accountable.
- Bumped `VERSION` to **v270**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.


## v269 — Claude feedback coherentification (legibility-theater failure is a tracked hazard)

- Added a first-class hazard entry for **MAPT failure / legibility theater** so “technically published but operationally useless” is treated as an incident, not a vibes dispute (HZ‑027).
- Updated publication-compliance guidance to classify recurring MAPT failure as HZ‑027 for hazard tracking (`docs/187-publication-compliance-and-coverage.md`).
- Bumped `VERSION` to **v269** and regenerated `MANIFEST.sha256`.


## v268 — Claude feedback coherentification (anti-theater ballot definition publication)

- Tightened the ballot-definition integrity pipeline to treat PDF renders as *derivative review aids*, forbid PDF-only publication, and require digest-first pointers aligned with MAPT (`docs/60-ballot-definition-integrity-pipeline.md`).
- Tightened the ballot-definition pipeline checklist to enforce the same derivative-render rules and to require MAPT-passable, mirrorable `bd.json` publication (no “PDF as API”) (`artifacts/checklists/ballot-definition-pipeline-checklist.md`).
- Updated `docs/60` references to use pinned `source:` identifiers (NIST BD CDF + NIST CDF implementation guidance + RFC8785 JCS) to keep Track A citations tight and replayable.
- Bumped `VERSION` to **v268**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.


## v267 — Claude feedback coherentification (drills produce digest-addressed capability, not just checklists)

- Tightened the AAR template to require digest pins for produced public packets and to explicitly record comms/uncertainty discipline (epistemic tags, next_update_at, correction chains, MAPT) (`artifacts/templates/after-action-report.md`).
- Tightened the public-notice example packet README to make it a comms-drill skeleton and to require pairing it with independent PacketVerificationReports for publishable drill outcomes (`artifacts/examples/evidence_packet_public_notice/README.txt`).
- Tightened the exercises program to require digest pins for any public packets created during exercises (`docs/86-exercises-and-gamedays-program.md`).
- Bumped `VERSION` to **v267**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.


## v266 — Claude feedback coherentification (epistemic-tag discipline in remaining public templates)

- Tightened the credential reissuance notice template to be PublicNotice-first, tag-disciplined, and digest-pointer oriented (avoids hedge-language and screenshot-based “comms theater”) (`artifacts/templates/voter-key-reissuance-notice.md`).
- Tightened the public audit report template to be claim/evidence oriented (tagged bullets + required digest pointers) and to publish digest-first summaries as `PublicNotice` `audit_result` notices (`artifacts/templates/public-audit-report.md`).
- Bumped `VERSION` to **v266**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.

## v265 — Claude feedback coherentification (privacy vs verifiability: turnout-surveillance boundary)

- Surfaced the privacy/turnout‑surveillance boundary in Track B eligibility transparency docs so remote‑return research cannot smuggle surveillance risk via vague language (`docs/75`, `docs/81`).
- Updated `docs/167` non‑claims to explicitly disclaim turnout‑surveillance prevention in remote‑return transparency surfaces (Track B research boundary).
- Added a first‑class hazard entry for turnout surveillance / privacy leakage via eligibility transparency (HZ‑026).
- Bumped `VERSION` to **v265**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.

## v264 — Claude feedback coherentification (court usability: claim-first bundles + admissibility posture)

- Rewrote `docs/43-evidence-bundles-and-court-proofing.md` to align with the claim-first, bounded bundle posture: small packets that are offline-verifiable, digest-first, and explicitly usable by humans in proceedings (cover sheet + admissibility worksheet + transformation accountability).
- Bumped `VERSION` to **v264**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.

## v263 — Claude feedback coherentification (digest-first comms templates + hedge-language ban)

- Tightened the incident-communications drafting worksheet to require epistemic tags + explicit missingness and to treat status/rumor surfaces as digest-first (MAPT-passable) views (`artifacts/templates/incident-communications.md`).
- Tightened the public status page template so every load-bearing statement is backed by a `PublicNotice`/feed digest short form and the page stays MAPT-passable under incident stress (`artifacts/templates/public-status-page.md`).
- Added a one-line pointer from the status-board guidance to the “keep it boring” status-page template (`docs/195`).
- Added a maintainer-facing non-negotiable: no “likely/probably/appears/seems” hedge-language in load-bearing public artifacts; use explicit epistemic tags (`docs/227` → `docs/218`/`docs/219`).
- Bumped `VERSION` to **v263**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.

## v262 — Claude feedback coherentification (epistemic-tag discipline in adopter/procurement surfaces)

- Tightened adopter-facing slide-deck outline rules to require epistemic tags for any non-strictly-observed statements (avoid “likely/probably” hedges without accountability).
- Tightened procurement-language template to require epistemic tagging + correction-chain semantics for public status/incident updates (so uncertainty is explicit and updates are auditable).
- Updated the artifact handoff index to point to the canonical drill scenario registry (`artifacts/registries/drill-scenarios.csv`) while keeping the thin pointer checklist to avoid prose drift.
- Bumped `VERSION` to **v262**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.

## v261 — Claude feedback coherentification (premature promotion pressure surfaced as drill + hazard)

- Added a governance-grade drill scenario for **premature Track B→A promotion pressure** (remote ballot return) and wired it into the exercises program (`artifacts/registries/drill-scenarios.csv`, `docs/86`, `docs/18`).
- Added a corresponding capture/failure-mode hazard entry (HZ‑025) so “promotion under political pressure” is tracked as a first-class risk (`artifacts/hazards/hazard-register.csv`).
- Tightened the catastrophe-ordering review checklist to explicitly require `docs/229` + `docs/166`/`docs/167` updates when scope is promoted toward Track A (anti-silent-scope-creep).
- Updated the stewardship plan to name premature promotion pressure as an explicit assumption-drift risk and require publishing guardrails even under emergency/equity arguments (`docs/183`).
- Bumped `VERSION` to **v261**, regenerated the PacketVerificationReport example packet, and regenerated `MANIFEST.sha256`.

## v260 — Claude feedback coherentification (witness liveness coherence + MAPT pointer-surface reminder)

- Consolidated witness behavioral health (“liveness beyond cosigning”) into a single canonical section in `docs/135` (removed duplicate block, fixed subsection numbering, preserved the required `hfv.witness.liveness_dissent_report` compression artifact).
- Tightened `docs/183` by removing a repeated heading label (keeps the stewardship plan compact and less error-prone under pressure).
- Added an explicit MAPT reminder to the rumor-control/status-board guidance so machine-facing pointer surfaces remain operationally usable during incidents (`docs/195` → `docs/187`).
- Bumped `VERSION` to **v260**, refreshed the PacketVerificationReport example packet pins, and regenerated `MANIFEST.sha256`.

## v259 — Claude feedback coherentification (adopter/procurement scope clarity)

- Removed a small duplication in the adopter briefing “what stays the same” section (keeps the doc tight; avoids implying two different supply-chain postures).
- Clarified the procurement-language template scope so Track A wrapper procurements don’t accidentally imply “must replace the voting system with open source,” while still requiring MAPT-compliant publication outputs.
- Bumped `VERSION` to **v259**, regenerated the PacketVerificationReport example packet (pins drift firewall), and regenerated `MANIFEST.sha256`.

## v258 — Claude feedback coherentification (MAPT surfaced in adoption/procurement)

- Surfaced MAPT (minimal adversarial publication test) in adopter-facing decision artifacts so “technically public” cannot be operationally opaque (`artifacts/templates/adopter-briefing.md`, `artifacts/templates/procurement-language.md`; canonical: `docs/187-publication-compliance-and-coverage.md`).
- Bumped `VERSION` to **v258**, regenerated the PacketVerificationReport example pins, and regenerated `MANIFEST.sha256`.

## v257 — Claude feedback integration (archive self-threat model + spec-correctness loop)

- Added an explicit **archive self-threat model** doc defining ARCH-* hazards and the minimum incident-style response loop when the spec/tooling is wrong (`docs/243-archive-self-threat-model-and-spec-correctness.md`).
- Wired that “the archive can be wrong” posture into the Track A threat model + assurance plan (meta-notes; pointers to bounded external challenge reports and the spec-error response playbook).
- Updated `docs/13-artifact-index.md`, `ARCHIVE_INDEX.md`, and the Claude feedback integration ledger mapping for 4d.
- Bumped `VERSION` to **v257**, regenerated PacketVerificationReport example pins, and regenerated `MANIFEST.sha256`.

## v256 — Claude feedback integration (Track C bundle deployment honesty + promotion protocol coherence)

- Added an explicit **Deployment honesty** callout to the generated Track C bundle so North Star material cannot be misread as Track A deployment guidance (`artifacts/bundles/track-c.toml` → `docs/track-c/BUNDLE.md`).
- Fixed a section-number collision in the promotion protocol: `docs/229` now uses **229.7** (premature deployment hazard) and **229.8** (political immune system) so citations remain unambiguous under pressure.
- Bumped `VERSION` to **v256**, regenerated the PacketVerificationReport example pins, and regenerated `MANIFEST.sha256`.

## v255 — Claude feedback integration (non-US contexts surfaced + example packet pins fixed)

- Surfaced a compact **non-US scope note** in the audience reading paths and pointed non-US adopters/reviewers to the open adaptation questions (`docs/242-...`, `docs/172` (172.9)).
- Added the corresponding mapping row in the Claude feedback integration ledger (`FEEDBACK_INTEGRATION_LEDGER.md`).
- Regenerated the **PacketVerificationReport minimal example packet** so `tool.version` / `tool.archive_version` pins match the archive `VERSION` (keeps offline examples replayable; release-gate drift firewall).

## v254 — Claude feedback integration (non-human participation: AI as witness/monitor + sybil agenda)

- Explicitly allowed **automated / AI-run witness and monitor operators**, but only with accountable controlling parties, disclosed update authority, and signed charters/profiles (`docs/139-ct-policy-inspired-admission-and-removal.md`, `artifacts/templates/witness-profile.md`).
- Extended witness governance to name the automation boundary: automated witnesses inherit operator incentives and must meet the same dissent/liveness expectations (`docs/135-...`, WIT‑7c).
- Tightened the non-human franchise framing to include the **near-term participation surface** (witness/monitor/verifier roles) and a bounded list of analog edge cases in human franchise debates (`docs/167` N‑7; `docs/172` 172.6).

## v253 — Claude feedback integration (non-claims-first gating in core Track A specs)

- Added a **read-first non-claims gating note** to the core normative docs (`docs/00`–`06`, `08`, `09`) and a **boundary reminder** inside `docs/03-protocol-spec.md` so implementers encounter `docs/166` + `docs/167` before reading the spec.
- Updated the **builder path** in `docs/242-audience-reading-paths-and-what-to-ignore.md` to start with `docs/166` + `docs/167` (claim discipline before implementation).


## v252 — Claude feedback integration (Track A supply-chain expectations surfaced)

- Surfaced Track A’s **supply-chain “dog that doesn’t bark”** reality and the minimal transparency recommendations (for opaque/proprietary voting stacks) directly in the Track A pilot + Track A navigation + adopter/procurement templates (`docs/track-a/PILOT.md`, `docs/track-a/README.md`, `artifacts/templates/adopter-briefing.md`, `artifacts/templates/procurement-language.md`, canonical: `docs/17-supply-chain-and-build-integrity.md`).
- Fixed a minor section-numbering inconsistency in the procurement language template (promotion guardrails section).

## v251 — Claude feedback integration (adopter translation artifacts + bounded external challenge interface)

- Added a **10-slide adopter deck outline** template so election directors/procurement/legislators can consume Track A without reading the archive (generated artifact; max-10 slides; non-claims early): `artifacts/templates/adopter-slide-deck-outline.md`.
- Added a **bounded external challenge report** template so external reviewers can contest a specific claim/proof/tool behavior with a minimal reproducer (packet digest/test vector) rather than “read the whole repo”: `artifacts/templates/external-challenge-report.md`.
- Wired these templates into the adopter maps and stewardship loop (`README.md`, `docs/START_HERE.md`, `docs/242-audience-reading-paths-and-what-to-ignore.md`, `docs/183-archive-stewardship-and-long-horizon-plan.md`) and updated the artifact list + feedback ledger (`docs/20-artifacts-checklists-and-templates.md`, `FEEDBACK_INTEGRATION_LEDGER.md`).

## v250 — Claude feedback integration (court cover sheet for "evidence gets used")

- Added a 1-page **court bundle cover sheet** template (claim + bundle digest + how-to-verify + custody summary) to close the gap between “evidence exists” and “evidence is usable in proceedings” (`artifacts/templates/court-cover-sheet.md`).
- Updated court bundle recipes to recommend shipping the cover sheet as the packet’s human entrypoint (`docs/211-court-evidence-bundle-recipes.md`).
- Updated the artifact index of templates and the feedback integration ledger to treat the cover sheet as a canonical admissibility surface (`docs/20-artifacts-checklists-and-templates.md`, `FEEDBACK_INTEGRATION_LEDGER.md`).

## v249 — Claude feedback integration (witness ecosystem surfaced in Track A pilot + bundle)

- Made the witness/monitor ecosystem explicit in the minimal Track A pilot: seed witness set + public profiles + bootstrapping trust assumption + liveness+dissent reporting in the critical window (`docs/track-a/PILOT.md`, DOC:`135`, DOC:`139`).
- Added witness governance + admission policy to Track A quick navigation and curated bundle so adopters see the load-bearing social layer early (`docs/track-a/README.md`, `artifacts/bundles/track-a.toml`, generated `docs/track-a/BUNDLE.md`).


## v248 — Claude feedback integration (Track C deployment honesty + boundary hygiene)

- Added a consistent **deployment honesty** callout to Track C (“North Star”) documents so they cannot be misread as Track A deployment guidance, and so readers are routed to non‑claims **N‑4** and the promotion protocol before engaging the North Star material (`docs/155–157`, `docs/169–170`, `docs/175`, `docs/track-c/*`).
- Updated the feedback integration ledger to treat Track C entrypoints as canonical surfaces for the supply‑chain “dog that doesn’t bark” honesty requirement (`FEEDBACK_INTEGRATION_LEDGER.md`, section 4c).


## v247 — Claude feedback integration (time-to-refute operational wiring)

- Made the **time-to-refute operational model** explicit across core surfaces: defined TTR‑1/TTR‑2 clocks, pre-positioned tooling, and the "how verification reaches the public" pathway (`docs/194` + `docs/241`).
- Wired the TTR discipline into the exercise program and scenario library (including the legibility-theater drop drill) and anchored it to the TTR drill plan + refutation packet checklist (`docs/86`, `docs/90`, `artifacts/templates/time-to-refute-test-plan.md`, `artifacts/checklists/time-to-refute-refutation-packet-checklist.md`).
- Surfaced the voter-facing verification story from the observer kit entrypoint (so the offline verifier doesn’t read as "ballot verification").

## v246 — Claude feedback integration (human stress drills surfaced)

- Made the **human process layer** drill requirement explicit by surfacing the key “overload / pressure / forged official statement” scenarios in the exercise program (`docs/86`) and scenario index (`docs/90`).
- Required Track A pilots to run (and write up) at least one of the human-stress scenarios before polls close (`docs/track-a/PILOT.md`).
- Updated the feedback integration ledger to treat `docs/86` + `docs/90` as canonical surfaces for the drill requirement.


## v245 — Claudes feedback integration (anti-theater + error-path coherence)

- Strengthened **Track A adoption realism** by wiring publication compliance + missingness surfaces into Track A navigation and the minimal pilot (MAPT + liveness/missingness).
- Strengthened the **“what if the archive/tool is wrong?”** path by linking observer/verifier workflows to the spec/verifier error response playbook (no silent patching; publish disagreements).
- Added procurement‑side **anti-capture promotion guardrails**: any promotion of experimental surfaces must follow the promotion protocol (independent review + adversarial non‑claims + rollback).
- Added missing **Track** labels to a small number of meta/template docs for repo-wide coherence.

## v244 — Feedback navigation coherence polish

- Added a direct pointer to `FEEDBACK_INTEGRATION_LEDGER.md` in `ARCHIVE_INDEX.md` so offline readers can map Claude’s feedback items to implementation surfaces without hunting.

## v243 — Audience reading paths + “what to ignore” guardrail (size discipline)

- Added a stable, bounded audience map with strict 15/60‑minute reading paths for adopters, verifiers, and builders, plus a “what to ignore until needed” attention budget guardrail (`docs/242-audience-reading-paths-and-what-to-ignore.md`).
- Updated the README’s strict 60‑minute adopter path to point to the audience map for non-adopter entry paths.
- Updated `docs/START_HERE.md` and `ARCHIVE_INDEX.md` to surface the new map as a primary navigation surface, and updated the Claude feedback integration ledger mapping for the size/entry-path requirement.

## v242 — Track A supply chain transparency expectations + voter narrative hardening

- Made the Track A stance on **opaque/proprietary voting system supply chain** explicit: evidence wrappers compensate for opacity they cannot eliminate; dispute value increases with underlying system transparency (`docs/17`).
- Added a Track A **wrapper transparency** lane to the pilot so pilots exercise “declare what ran / update history” rather than assuming it (`docs/track-a/PILOT.md`).
- Added procurement language for proprietary-system transparency minimums (`artifacts/templates/procurement-language.md`) and surfaced the same expectation in the adopter briefing template (`artifacts/templates/adopter-briefing.md`).
- Clarified the boundary as a **non-claim**: Track A does not attest vendor build/provenance integrity for proprietary voting systems (`docs/167`).
- Hardened the voter-facing story against the “become a cryptographer or distrust everything” adversarial framing (`docs/track-a/VOTER_VERIFICATION.md`).


## v241 — adversarial publication failure modes + split-delivery drill

- Clarified adversarial publication tactics that create “it exists but you can’t verify it” conditions (A/B, geo/UA variance, WAF/CAPTCHA, pointer churn) and how to capture them as evidence (`docs/187`).
- Added drill scenario `selective_delivery_split_view` to practice proving split delivery using parity snapshots + bounded request-context notes (`artifacts/registries/drill-scenarios.csv`; see `docs/18`, `docs/201`, `docs/223–224`).
- Updated `docs/18-failure-drills.md` human-layer minimums accordingly.

## v240 — legal admissibility lane tightened + spec-error response made real

- Tightened the **“evidence gets used”** lane (Claude §3b) without adding bloat:
  - Fixed `docs/211` admissibility template reference formatting and added explicit pointers for a one‑page crypto primer + expert lane.
  - Added templates:
    - `artifacts/templates/crypto-primer-one-page.md`
    - `artifacts/templates/expert-declaration-outline.md`
- Made the **archive-can-be-wrong** response loop concrete (Claude §4d / PO‑104 / HZ‑024):
  - Added `artifacts/templates/spec-error-response-note.md`
  - Wired the playbook to the template: `artifacts/playbooks/spec-error-response-playbook.md`
- Updated the Track A pilot to require **admissibility planning** (matrix + dry‑run bundle) and to produce at least one filled worksheet + primer (`docs/track-a/PILOT.md`).
- Listed the new templates/playbook in `docs/20-artifacts-checklists-and-templates.md`.

## v239 — verifier onboarding + privacy/verifiability tension surfaced

- Added a **verifier onboarding mini-curriculum** template so newsrooms/watchdogs/campaigns can pre-position the observer-kit workflow:
  - `artifacts/templates/verifier-onboarding-mini-curriculum.md`
  - Linked from `docs/241-verifier-capacity-and-distribution.md` and listed in `docs/20-artifacts-checklists-and-templates.md`.
- Added an explicit open research item on the **privacy vs verifiability** tension for eligibility + revocation surfaces:
  - `docs/172-open-research-questions-and-experiment-backlog.md` → **172.3.1**
  - Cross-linked from `docs/15-privacy-and-eligibility-tokens.md` (Track B honesty).

## v238 — political-pressure comms drill (human layer, contested window)

- Added a required human-layer drill scenario for **political pressure to publish unverified claims**:
  - Drill registry entry: `political_pressure_unverified_claims` (trigger: `rumor_detected`, notice: `status_update`)
  - Uses existing uncertainty-safe update discipline (`219`) via `artifacts/checklists/public-update-epistemic-quickcheck.md`
- Linked the new drill from `docs/18-failure-drills.md` and expanded the feedback integration map for §4b.

## v237 — verifier capacity made publishable (who will look + where reports land)

- Added verifier capacity directory surface to prevent “evidence exists but no one verifies” legibility theater:
  - New evidence kind: `hfv.verifier.capacity_roster` (Track A; experimental)
  - New payload schema: `schemas/VerifierCapacityRoster.json`
  - New template: `artifacts/templates/verifier-capacity-roster-payload.json`
  - New doc: `docs/241-verifier-capacity-and-distribution.md` (capacity model + wiring + pilot requirement)
- Wired capacity/distribution into the comms authenticity / time-to-refute spine:
  - `docs/194.4` and `docs/240` now explicitly require pre-election capacity visibility for TTR targets to be real.
- Made capacity first-class in verifier-facing and Track A deployment docs:
  - `docs/188` now pulls the capacity roster as part of “verify the verifiers.”
  - `docs/179` adds a small optional verifier-ecosystem meta profile and includes witness liveness+dissent in witness governance.
  - `docs/193` adds a compact “where reports land” distribution section.
  - Track A pilot now includes “capacity roster + report landing” as a deployed surface (`docs/track-a/PILOT.md`).
- Added a size-disciplined operator checklist for pilots:
  - `artifacts/checklists/pilot-after-action-minimum-publishables.md` (replayable outputs, roster, witness health, TTR observations)
  - `artifacts/templates/after-action-report.md` now links the checklist.

## v236 — adopter reality + anti-theater / anti-capture hardening

- Upgraded the adopter briefing template to include **cost/staffing ballparks** and **anti-legibility-theater guardrails** (so an election director can reason about operational impact in ~10 minutes).
- Strengthened the archive’s **vendor capture** defenses:
  - expanded `docs/183` vendor-capture threat model with concrete signals + mitigations,
  - added explicit “anti-capture / interoperability” clauses to `artifacts/templates/procurement-language.md`.
- Added a compact “anti-legibility-theater checks” section to `docs/track-a/README.md` to keep Track A deployments substantively verifiable (not just schema-valid).
- Updated `FEEDBACK_INTEGRATION_LEDGER.md` pointers for Claude §24 and adopter-facing requirements.

## v235 — witness health becomes verifier-facing + reference hygiene

- Propagated **witness liveness+dissent** evidence (`hfv.witness.liveness_dissent_report`) into verifier-facing docs (`188`, `177`, `91`, `92`, `179`) so “verify the verifiers” is part of the operational path, not just governance prose.
- Tightened voter-facing verification story to point to witness liveness+dissent reports as a concrete public signal (`docs/track-a/VOTER_VERIFICATION.md`).
- Fixed internal reference hygiene: replaced ambiguous `172.6`/`172.1.1` file-like refs with explicit links to the canonical file + section (`docs/172-open-research-questions-and-experiment-backlog.md`, `176`), and updated the feedback integration ledger accordingly.

## v234 (2026-02-27)

Continue Claude-feedback integration with **bounded, verifiable surfaces**: make witness “behavioral health” and time-to-refute drills concrete without inflating the archive.

- Added witness health report evidence kind `hfv.witness.liveness_dissent_report`:
  - New payload schema: `schemas/WitnessLivenessDissentReport.json`
  - New example packet: `artifacts/examples/evidence_packet_witness_liveness_dissent_report_minimal/`
  - Registries + catalogs updated (`envelope-kinds.csv`, `envelope-attachment-requirements.csv`, `docs/EVIDENCE_OBJECT_CATALOG.md`)
- Expanded `docs/135` with “liveness beyond cosigning” behavioral signals and a compact required public report shape.
- Tightened `artifacts/templates/witness-profile.md` to include health-report pointers and dissent/refusal counts.
- Expanded `docs/240` with TTR‑1/TTR‑2 clocks, minimum roles/pathway, and compact drill artifacts:
  - `artifacts/templates/time-to-refute-test-plan.md`
  - `artifacts/checklists/time-to-refute-refutation-packet-checklist.md`
- Tightened AI-franchise posture as research/non-claim (don’t dismiss; treat as agenda): `docs/167` (N‑7) and `docs/172.6`.
- Added a compact “outside view” neutrality + legibility framing to `README.md`.


## v233 (2026-02-27)

Continue Claude-feedback integration with **minimal new surface area**: add an AI-era refutation discipline doc, and tighten governance docs to treat witness + promotion + deployment as first-class “project self-threats”.

- Added `docs/240-deepfake-frontier-and-time-to-refute.md` (measurable time-to-refute posture + minimal refutation packet shape; no deepfake-detection claims).
- Wired `240` into the comms/authenticity spine (`186`, `195`, `219`), Track A bundle, and the numbered index.
- Tightened `docs/135` (explicit “witness problem is the whole problem” posture + bootstrapping/degraded-mode note).
- Tightened `docs/229` (promotion protocol gets a minimal “political immune system” guardrail section).
- Tightened `docs/183` (explicit deployment-cliff posture + institutional refusal/assumption drift notes).
- Expanded `FEEDBACK_INTEGRATION_LEDGER.md` mapping to include Claude sections 8/9/10/11/15/24.


## v232 (2026-02-27)

Preserve the Claude feedback input as a first-class, offline-readable artifact (without duplicating it across docs), and link it from the integration ledger + index.

- Added `evidence/feedback/claude-opus4_6-feedback_2026-02-27.md` (sha256 pinned in `FEEDBACK_INTEGRATION_LEDGER.md`).
- Added `evidence/feedback/README.md` to explain size-discipline posture.
- Linked feedback trail from `README.md` and `ARCHIVE_INDEX.md`.
- Regenerated `artifacts/examples/evidence_packet_packet_verification_report_minimal` to pin tool/archive version to v232.

## v231 (2026-02-27)

Claude-feedback coherence pass: clarify that offline verification surfaces are primarily for representative verifiers (not “every voter”), strengthen court-admissibility planning with a minimal crypto-primer + expert lane, and add a compact feedback-integration ledger to keep multi-turn integration auditable without archive bloat.

- Representative verification clarity:
  - `docs/177` now names the intended audience (observers/journalists/civil society/courts) and links the voter-facing posture (`docs/track-a/VOTER_VERIFICATION.md`).
  - `docs/179` now includes the same audience note for verifier implementers.
- “Evidence is used” gap (admissibility):
  - `docs/211.5` now explicitly calls for a one-page crypto primer and (where required) an expert-declaration lane.
  - Updated `artifacts/templates/court-admissibility-worksheet.md` and `artifacts/templates/jurisdictional-admissibility-matrix.md` to capture these expectations.
- Systematic integration hygiene:
  - Added `FEEDBACK_INTEGRATION_LEDGER.md` and linked it from `README.md` and `docs/START_HERE.md`.

## v230 (2026-02-27)

Claude-feedback coherence pass: tighten the archive’s “human dignity / human crisis” framing in coercion-related docs, make time-to-refute guidance reachable from uncertainty-safe update procedures, strengthen witness-incentive research framing (CT analogy + front-group detection), add a bounded non-US portability question, and remove an accidental temp output directory for size discipline. Also updates the verifier-report emitter to generate Track-tagged notes and regenerates the pinned example packet.

- Size discipline:
  - Removed accidental `tmp_emit_pvr/` build output from the shipped archive; `scripts/build_manifest.py` now excludes it if reintroduced.
- Coercion framing coherence:
  - `docs/34` and `docs/40` now explicitly point readers to `docs/07` (“coercion as lived experience”) before choosing mitigations or publication granularity.
- Comms authenticity operations:
  - `docs/219` now explicitly links forged-statement response to `docs/194.4` (time-to-refute) and the authenticity response cell checklist.
- Research backlog refinements:
  - `docs/172.2.2` now names the CT incentive gap (reputation may be too weak) and front-group/class-capture detection as explicit open questions.
  - Added `docs/172.9` (Non-US election contexts portability).
- Tooling / examples:
  - `tools/observer_verify_packet.py --emit-evidence-object` now emits a Track-tagged `notes/README.md` for determinism.
  - Regenerated `artifacts/examples/evidence_packet_packet_verification_report_minimal` to pin tool/archive version to v230.

## v229 (2026-02-27)

Claude-feedback coherence pass: make the **human legitimacy constraints** explicit in core scope docs, and formalize the “what if the spec/verifier is wrong?” loop as a first-class hazard/PO (bounded playbook + registry linkage). Also makes Track B’s non-deployment posture visible in the generated Track B bundle page.

- Human legitimacy surfaces made explicit (scope map + claims contract):
  - `docs/154` adds a short “Human legitimacy surfaces” subsection (representation duty, material floor, crisis usability).
  - `docs/166` adds a compact “Human legitimacy constraints” subsection (representation duty + material floor).
- Archive self-failure posture (spec/verifier substantive errors):
  - Added `PO-104` (external challenge / spec correction loop) and `HZ-024` (false-confidence incident).
  - Added `artifacts/playbooks/spec-error-response-playbook.md` and linked it from `docs/183`.
  - `CLM-025` now explicitly includes the external-critique + regression-vector requirement.
- Track B generated bundle:
  - `artifacts/bundles/track-b.toml` purpose now includes the standard “Deployment honesty” preface, so `docs/track-b/BUNDLE.md` inherits it.

## v228 (2026-02-27)

Claude-feedback coherence pass: reduce “voter as threat-model persona” drift by wiring the person-facing framing into the threat model, and make coercion’s lived experience harder to sanitize. Also made the human-franchise assumption explicit in identity/eligibility docs so the non-human franchise research is not accidentally implied.

- Voter/person framing:
  - `docs/01` now includes a short “Human framing” section that points to Track A voter-facing narratives (`track-a/VOTER_VERIFICATION.md`, `track-a/PERSONS_PATH.md`) and the representation duty.
- Coercion honesty:
  - `docs/07` adds a compact “Coerced person’s path” list of named experiences (guardrail against checkbox-ification).
  - `docs/33` now tells readers to start with the named-experience list before protocol families.
- Franchise scope clarity:
  - `docs/15` and `docs/80` add an explicit “Franchise scope note” pointing to non-claim `167` N‑7 and research item `docs/172-open-research-questions-and-experiment-backlog.md` (section 172.6).

## v227 (2026-02-27)

Claude-feedback coherence pass: make Track B’s “not deployable” posture hard to miss in every Track B document, and explicitly frame the witness ecosystem as **countervailing power** (a governance constraint, not just a cryptographic one). Also added a short mission-discipline reminder and tightened a few “system” phrasings.

- Track B deployment honesty (systematic):
  - Added a standardized “Deployment honesty” preface (links to `167` N-2 and the promotion protocol `229`) to all Track B docs.
- Witness ecosystem clarity:
  - Added “Witnesses as countervailing power” framing to `135`.
- Mission discipline:
  - Root `README.md` now includes a short “do not let the specification become the mission” constraint.
- Minor wording:
  - `05` now refers to “this stack” (not “this system”) in key management intro.

## v226 (2026-02-27)

Claude-feedback coherence pass: tighten the “evidence is used” bridge (court usability planning), and make the representation duty legible via short witness/monitor profiles (bounded templates + small doc wiring).

- Legal usability planning (bounded, jurisdiction-specific):
  - Added `artifacts/templates/jurisdictional-admissibility-matrix.md` (one-page-per-forum planning sheet).
  - `docs/211` now points pilots/filings to the matrix template in addition to the bundle-local admissibility worksheet.
- Representation duty made legible (who verifies on behalf of voters):
  - Added `artifacts/templates/witness-profile.md` (short public profile template linking to signed COI/charter/key artifacts).
  - `docs/135` adds WIT-1b recommending the public profile.
  - `docs/131` adds a small “public monitor profile” recommendation, reusing the same template.
- Pilot learning capture:
  - Expanded `artifacts/templates/after-action-report.md` with a small “Pilot deployment additions” section (what evidence was actually used; time-to-refute observations).
- Updated `docs/20` templates/checklists list to include the new artifacts.


## v225 (2026-02-27)

Claude-feedback coherence pass: make the **time-to-refute** posture more operational (bounded checklist + explicit status-board lane) and fix a small drift in drill references.

- Added a bounded operator checklist for authenticity response under deepfake/forgery pressure:
  - `artifacts/checklists/authenticity-response-cell-checklist.md` (ties `194.4` targets to a drillable workflow).
- Wired time-to-refute into operator surfaces:
  - `docs/194` now names pre-positioned prerequisites and points to the new checklist.
  - `docs/195` adds an explicit authenticity-verdict lane for rumor-control/status boards.
- Drill registry coherence:
  - `artifacts/registries/drill-scenarios.csv` time-to-refute scenario now references the new checklist and points at `194.4` (not `194.5`).
- Example packet notes hygiene:
  - Added missing `**Track:**` header to `artifacts/examples/evidence_packet_packet_verification_report_minimal/notes/README.md`.


## v224 (2026-02-27)

Claude-feedback coherence pass: remove remaining “LLM-first” language drift from stewardship surfaces, fix a small numbering hazard, and make schema-catalog metadata consistent with the Track header discipline.

- Stewardship framing cleanup:
  - `docs/183` retitled to **LLM-maintained** (not “LLM-first”), clarifies human deployability, fixes duplicated step numbering, and restores monotonic section order.
  - Bundle + index text updated to match (no “LLM-first” phrasing).
- Schema catalog metadata:
  - `schemas/SCHEMA_CATALOG.md` now includes a `**Track:** Shared (cross-cutting)` header; generator updated (`scripts/gen_schema_catalog.py`) so this remains deterministic.

## v223 (2026-02-27)

Claude-feedback coherence pass: finish Track metadata coverage for remaining markdown surfaces (ADRs + operator artifacts) and fix a minor comms-authenticity section numbering drift.

- Track metadata completion:
  - Added `**Track:** …` headers to remaining non-numbered markdown files (root indices, ADRs, and `artifacts/*` checklists/templates) using `Shared (cross-cutting)` by default.
- Minor coherence fix:
  - `docs/194` renumbered subsections so **Time-to-refute** is `194.4` and **non-claims** are `194.5`.

## v222 (2026-02-27)

Claude-feedback coherence sweep: remove remaining reader-model mismatch in the claims contract, and make Track metadata consistent across *all* docs (including generated API-surface indices).

- Claims contract alignment:
  - `docs/166` now explicitly separates **maintenance** (LLM + stewards) vs **deployment** (humans under pressure) readers, and points adopters to Track A + the briefing/pilot artifacts.
- Voter-facing honesty surfaced in verifier entry points:
  - `docs/91` now states explicitly that most voters will not run verifiers; verification is performed by replayable representatives (monitors/journalists/civil society/courts) and links to `track-a/VOTER_VERIFICATION.md`.
- Track metadata normalization (anti-drift):
  - Added `**Track:** …` headers to non-numbered docs and Track readmes.
  - Updated generators (`scripts/gen_*`) so generated public-surface docs (`PUBLIC_SURFACES`, `EVIDENCE_OBJECT_CATALOG`, code/profile lists, tombstones, Track A MVR) include Track headers deterministically.

## v221 (2026-02-27)

Claude-feedback coherence pass: fill the remaining “non-human franchise” open-question gap, tighten the “evidence persists” posture when institutions are slow/failed, and reduce drift between legacy open-questions docs and the canonical backlog.

- Open research backlog alignment:
  - `docs/172` adds **172.2.2** (verification capacity: who checks, how it reaches the public) and **172.6** (non-human franchise / AI standing; identity-integrity + sybil constraints).
- Durability beyond “fast adjudication”:
  - Root `README.md` now states the design goal explicitly: evidence supports immediate dispute resolution *and* persists for later adjudication/historical record.
  - `docs/211` adds a short section on court bundles remaining useful when courts are slow or institutions refuse to act.
- Drift reduction:
  - `docs/12` now points to the canonical non-claims (`167`) and canonical backlog (`172`) and is treated as a bounded legacy summary.

**Correction note:** prior changelog text referenced a scoped non-human franchise item in `172` before it was actually present. That gap is now closed in `docs/172-open-research-questions-and-experiment-backlog.md` (section 172.6).


## v220 (2026-02-27)

Claude-feedback pass: institutional-volatility “legibility theater” defense, witness bootstrapping clarity, and coercion-as-experience honesty (kept size-bounded; mostly edits + one small checklist).

- Outside-view adoption: root `README.md` now leads with a strict 60-minute “outside view” path to reduce first-impression overwhelm.
- Institutional volatility (publication under adversarial minimal compliance):
  - `docs/187` now defines a concrete **Minimal Adversarial Publication Test (MAPT)** and treats MAPT-failure as a publication incident even if artifacts “exist somewhere.”
  - Added `artifacts/checklists/minimal-adversarial-publication-test.md` (bounded operator checklist; pointer surfaces, statements, data).
- Witness ecosystem honesty + robustness:
  - `docs/135` adds a publishable **witness liveness score** concept (beyond routine cosigns), a front-group defense note for stakeholder classes, and an explicit bootstrapping section naming the initial witness set as a trust assumption with an expansion plan.
- Coercion as lived experience:
  - `docs/07` now names coercion as a human dignity / surveillance experience (not just a crypto threat model) and adds a deployment honesty rule that front-loads `167` N‑2 + supervised override access.
  - `docs/33` now points readers to `167` N‑2 and `07` for the lived-experience framing.
  - `docs/track-b/README.md` now explicitly instructs reading `167` N‑2 before Track B protocol specs.


## v219 (2026-02-27)

Tight “human legitimacy surfaces + admissibility packaging” pass (kept size-bounded; templates + short Track A docs):

- Clarified audience split: `docs/START_HERE.md` now distinguishes maintenance (LLM) vs deployment (humans in crisis) readers and adds optional legitimacy framing reads.
- Track A human-facing coherence:
  - `docs/track-a/README.md` adds explicit supply-chain transparency recommendation tiers (T0–T2), a “representation duty” note, and a material-floor statement.
  - Added `docs/track-a/PERSONS_PATH.md` (a compact “being a voter” experience map tied to evidence surfaces).
  - `docs/track-a/VOTER_VERIFICATION.md` now names representation duty explicitly and states the material recovery floor.
- Legal “evidence that gets used” tightened without pretending jurisdictional uniformity:
  - `docs/211` adds a minimal admissibility worksheet section and links to a new template.
  - Added `artifacts/templates/court-admissibility-worksheet.md` (1–2 page bundle-local worksheet).
- Drill posture: `docs/18` now requires human-layer overload drills (conflicting reports, forged statements, political pressure), pointing to the canonical drill registry.
- Supply-chain doc alignment: `docs/17` adds Track A wrapper transparency recommendations for opaque vendor stacks.


## v218 (2026-02-27)

Tight “adoption translation + human-pressure resilience” pass (kept size-bounded; no new envelope kinds):

- Added a minimal Track A pilot plan (`docs/track-a/PILOT.md`) and a voter-facing verification narrative (`docs/track-a/VOTER_VERIFICATION.md`).
- Added an adopter briefing template (`artifacts/templates/adopter-briefing.md`) and wired it into Track A and `START_HERE`.
- Added a strict 60-minute adopter reading path in `docs/START_HERE.md` (outside-view navigation).
- Strengthened open questions + boundaries:
  - `172` now includes legal admissibility/uptake, witness boundary conditions + behavioral capture detection, and a scoped non-human franchise research item.
  - `167` adds an explicit non-claim for non-human franchise and expands coercion boundary with a human-experience note.
- Strengthened capture- and rumor-era posture:
  - `135` now states the witness/monitor boundary condition explicitly and adds “liveness beyond cosigning” behavioral health signals.
  - `194` adds a drilled time-to-refute operational model (faster-than-rumor posture).
  - `187` adds an adversarial publication test to resist “legibility theater.”
  - `229` adds a premature deployment hazard guardrail for political pressure on Track B→A promotion.
- Added three human-pressure drill scenarios (conflicting reports overload, forged official statement time-to-refute, legibility theater publication drop) to `artifacts/registries/drill-scenarios.csv`.
- Stewardship hardening: `183` adds a minimal external challenge loop + vendor capture threat model; `211` notes admissibility variability; `17` clarifies Track A supply-chain realities.



## v217 (2026-02-27)

Tight “ObserverKit canonicalization + portability” pass (small but high‑leverage interop hardening):

- ObserverKit manifest signing is now unambiguously defined and implemented using RFC8785-JCS canonical bytes (docs/92); `schemas/ObserverKitManifest.json` now requires `canonicalization: "RFC8785-JCS"`.
- ObserverKit ships an embedded `tools/jcs.py` mirror (`observer-kit/tools/jcs.py`) and the offline verifier uses it; added drift firewall `scripts/check_observer_kit_jcs_mirror.py` to keep the embedded JCS implementation byte-identical to the archive’s canonical `tools/jcs.py`.
- Fixed doc path drift: `95` now points to `observer-kit/tools/offline_verifier.py` (not a nonexistent `tools/offline_verifier.py`).



## v216 (2026-02-27)

Tight “PublicNotice feed/type coherence” pass (small but high-leverage interop + drift firewalls):

- Fixed a real schema mismatch: `schemas/PublicNoticeFeed.json` now includes `election_milestone` in `entries[].notice_type` so feeds can faithfully summarize all valid PublicNotice types.
- Added drift firewall `scripts/check_public_notice_type_coherence.py` and wired it into the release gate to prevent future silent divergence between PublicNotice and PublicNoticeFeed notice-type vocabularies.
- Tightened operator-facing guidance:
  - `docs/195` now includes `election_milestone` in the status-board entry vocabulary.
  - `docs/220` adds a tiny deterministic rule for rendering milestone notices as a separate time-ordered timeline.
  - `artifacts/templates/incident-communications.md` now includes `audit_result` and `election_milestone` and points milestone authors to `237`.


## v215 (2026-02-27)

Tight “PublicNotice key lifecycle hardening” pass (comms authenticity ergonomics + shipped example):

- Added `239` (PublicNotice key lifecycle + rekey protocol): bounded, digest-first discipline for planned rotation and emergency rekey (revocation/compromise) using `hfv.public.notice_signing_keyset`, receipts/gossip, and split-view escalation.
- Added a shipped minimal example packet: `artifacts/examples/evidence_packet_public_notice_signing_keyset_minimal` (keyset payload + envelope + required attachments; placeholder signatures) so verifiers/operators have a concrete interop target.
- Added template `artifacts/templates/public-notice-key-rotation-payload.json` and wired it into `docs/20` and the HZ-020 comms playbook (digest-first key rotation update notice).
- Updated `208` to point to `239` for operational details; updated Track A bundle and indexes.



## v214 (2026-02-27)

Tight “results-release envelope publication hardening” pass (interop + missingness surfaces):

- Added required attachment rules for `hfv.results.release_package` (receipt + gossip summary) in `artifacts/registries/envelope-attachment-requirements.csv` so results intervals cannot be selectively withheld without leaving portable missingness evidence.
- Added a minimal shipped example packet: `artifacts/examples/evidence_packet_results_release_package_minimal` (schema-valid RRP payload + envelope + required attachments; placeholder signatures).
- Added an EvidenceEnvelope digest test vector for the RRP payload template to keep canonical digest computation stable (`artifacts/test-vectors/envelope_vectors.json`).
- Tightened `236` and `238` to explicitly bind results-release envelopes to the required attachment policy and to point to the minimal example packet.


## v213 (2026-02-27)

Tight “results-release publication shape + signature-layering interop” pass (small but high-leverage):

- Added `238` (RRPs as EvidenceEnvelope payloads): makes results-release publication single-path and verifiable; avoids inner/outer signature ambiguity and binds PBB `RESULTS` leaves to the envelope payload digest.
- Added ADR `0004` (RRP signed via EvidenceEnvelope): records the interface decision and its verifier-visible consequences.
- Registered new envelope kind: `hfv.results.release_package` → `schemas/ResultsReleasePackage.json`.
- Relaxed `ResultsReleasePackage.json`: `package_signature` is no longer required and is explicitly deprecated for Track A publication (envelope signatures are authoritative).
- Extended results hashing test vectors with a “no inner signature” RESULTS-leaf vector (`artifacts/test-vectors/results_hash_vectors.json`) and updated results docs (`63`, `68`, `236`) to reference the envelope kind.
- Refined supply-chain attestation guidance (`97`) and added a lockfile reference for the in-toto/DSSE envelope layer spec (`xref: intoto_envelope_v1_md`).


## v212 (2026-02-27)

Tight “institutional milestone binding + PublicNotice taxonomy” pass (small, high-leverage additions):

- Fixed a real formatting ambiguity in `docs/01` so adversaries A6 (verifier ecosystem) and A7 (institutional/certification ecosystem) are clearly separated and correctly attributed.
- Added `237` (canvass/certification/recount as evidence surfaces): a minimal pattern for publishing institutional milestones as digest-first, receipted+gossiped PublicNotices bound to results-release digests (ties to `234`, `236`, and ADR 0003).
- Extended `schemas/PublicNotice.json` with a new notice type `election_milestone` and an optional `milestone_id` field (required when `notice_type=election_milestone`) to keep milestone events comparable without adding new evidence kinds.
- Added a bounded milestone ID registry: `artifacts/registries/election-milestones.csv`, a drift firewall (`scripts/check_election_milestones_registry.py`), and wired the check into the release gate.
- Added an operator template: `artifacts/templates/public-notice-election-milestone-payload.json`, and indexed it in `docs/20`.


## v211 (2026-02-27)

Tight “results interop drift tripwires + log-model coherence” pass (small, high-leverage fixes):

- Added minimal **results hashing test vectors** (`artifacts/test-vectors/results_hash_vectors.json`) plus a drift firewall (`scripts/check_results_hash_vectors.py`) to keep `235` CRO TBS-hashing and RESULTS-leaf `payload_hash_b64` derivations consistent across implementations. (`source: rfc8785_txt`)
- Refactored `docs/04` (PBB/transparency log) to match `schemas/LogEntry.json` field names (`node_signature_b64`, `server_timestamp_ms`, `node_id`) and to clarify which timestamps are informational vs ordering evidence.
- Extended `schemas/LogEntry.json` with optional `time_beacon_digests` (content-addressed references to published `hfv.time.beacon` envelopes) so deployments can bind ordering epochs to independently-verifiable time evidence without trusting the log’s wall-clock.
- Wired the above into `31`/`38`/`192`/`236` (time + results anchoring docs) and tightened the operator secure-time checklist accordingly.


## v210 (2026-02-27)

Tight “results anchoring + hash correctness” hardening pass (small, high-leverage fixes):

- Added `236` (results release transparency profile): standardizes how results releases are anchored into the PBB (LogEntry `entry_type=RESULTS`), checkpointed by witnesses, and ordered via time-attestation policy without introducing large artifacts. (`source: rfc8785_txt`, `source: rfc3161_txt`)
- Fixed the reference drift tool `tools/enr_drift_detector.py` to follow `235` CRO hashing rules (hash TBS(CRO) with `cro_hash` omitted) and to fail loud when a CRO’s declared hash disagrees with the computed TBS hash.
- Extended `schemas/LogEntry.json` to include `RESULTS` as a first-class `entry_type`, and aligned protocol/transparency-log docs with the schema’s `payload_hash_b64` naming.
- Tightened results-object schemas (`CanonicalResultsObject`, `ENRUpdate`, `ResultsReleasePackage`) to expect `sha256:<hex>` digest strings for key hash/link fields (keeps interop failures crisp).



## v209 (2026-02-27)

Tight “results object interop + correction linkage” hardening pass (small schema additions):

- Added `235` (results-object canonicalization + chain-linking): defines JCS hashing rules for CRO/ENRUpdate/RRP and avoids self-referential hash ambiguity (ties to `176` and `234`). (`source: rfc8785_txt`)
- Fixed doc↔schema mismatches for results objects with **additive** schema updates:
  - `CanonicalResultsObject` now allows optional `prev_cro_hash`; `cro_hash` description specifies TBS(CRO) hashing (omit `cro_hash`).
  - `ENRUpdate` now allows optional `prev_cro_hash`/`cro_hash` linkage and adds correction fields (`is_correction`, `correction_reason`, bounded detail) to support monotonicity + drift rules.
  - `ResultsReleasePackage` tightens `generated_at` to date-time and adds optional linkage fields (`cro_hash`, `prev_package_hash`) for audit-friendly chaining.
- Wired `235` into `63` and `68`, and updated `69` correction handling to match `234` + the new `ENRUpdate` correction fields.
- Added an operator template for digest-first results corrections: `artifacts/templates/public-notice-results-correction-payload.json`, and referenced it from `20`, `234`, and the comms playbook.


## v208 (2026-02-27)

Tight “results lifecycle + contact surface” hardening pass (no schema changes):

- Added `234` to define a compact **results status taxonomy** (`unofficial` + `counts_status`) and **correction discipline** (no silent edits; link-forward; digest-first notices).
- Wired `234` into `63` (ENR) and `68` (results pipeline) to reduce ambiguity between “more complete” and “more official.”
- Clarified `69` drift detection: cross-register inconsistency checks are handled via `209` (separate evidence object), not as DriftAlert classes.
- Added operator templates for results releases:
  - `artifacts/templates/results-release-package-payload.json`
  - `artifacts/templates/public-notice-results-release-payload.json`
  and indexed them in `20`.
- Added `security.txt` as an **informative** item in `199` snapshots, with a lockfile citation ID (`rfc9116_txt`); regenerated external-source indexes.


## v207 (2026-02-27)

Tight “institutional + reporting” hardening pass (no schema changes):

- Added a scoped adversary class for **institutional/certification ecosystem compromise** (Track A threat model), with pointers to existing capture-resistance and governance surfaces.
- Added compact **standards + reference citations** for ENR and results-pipeline docs (prefer pinned NIST CDF + guidance; use `xref:` for unpinned pages).
- Tightened the Results API contract template to explicitly carry **ERR/CDF version + canonicalization** expectations.
- Added ADR-0003 documenting the decision to treat institutional volatility as a first-class risk while keeping Track A claims conservative.

## v206 (2026-02-26)

External-source pin-triage hygiene + ENR citations (tight; no schema changes):

- Tightened external-source `pin_exemption` semantics: reserve `blocked` for explicit retrieval constraints; moved pending-pin stable artifacts to `temporary` and mutable web pages to `mutable`, with review windows aligned to deterministic caps (lockfile + regenerated indexes).
- Updated Track A ENR docs to use lockfile-based citations: `63` now cites EAC/NIST/IFES ENR guidance via `xref:` IDs, and `68` cites pinned NIST CDF specs + RFC 8785 as `source:`.
- Added `docs/233-pinning-workflow-for-external-sources.md` plus `tools/pin_external_source.py` (maintainer helper: compute/write sha256 pins without bundling bytes); small wiring updates in `191`, `228`, and entrypoints.

## v205 (2026-02-26)

Compact request-context note drift hardening (tight; no schema changes):

- Added `docs/232-compact-request-context-notes.md`: bounded `req[]/vary[]/age[]` notation, canonicalization contract, and safety discipline for publishable request-context hints (ties into `223`/`224`).
- Hardened `tools/compact_notes.py` canonicalization to normalize/coarsen known keys (drop Accept-Language q-weights; clamp cookie state; coerce geo/asn) and to sanitize values (prevents delimiter injection / accidental bloat in diffs).
- Added compact-note test vectors (`artifacts/test-vectors/compact_context_vectors.json`) plus a release-gate drift firewall (`scripts/check_compact_context_vectors.py`) to keep tooling + docs aligned.
- Small wiring updates across entrypoints/templates/checklists to point to `232`.

## v204 (2026-02-26)

Placeholder safety + example consistency (tight; no schema changes):

- Added `docs/231-placeholder-domains-and-identifiers.md`: reserved placeholder domains/TLDs and documentation address ranges for copy-paste-safe examples (ties into `189.4` and `201`).
- Replaced misleading `example` placeholders under restricted TLDs (e.g., "example dot gov") across templates, tools, registries, and shipped example packets with RFC-reserved `.example` / `.invalid` forms; updated the Track A comms/discovery example set (`203`/`204`/`201`) so digests and pointers remain mutually coherent.
- Added `scripts/check_no_forbidden_example_tlds.py` as a release-gate drift firewall to prevent reintroducing restricted placeholder TLDs (see `231`).

## v203 (2026-02-26)

External-source triage ergonomics (tight; no schema changes):

- Extended `scripts/gen_external_sources_index.py` to generate `docs/EXTERNAL_SOURCE_REVIEW_QUEUE.md`: a small, no-URL maintainer queue of *unpinned* sources sorted by `review_by`, with citation counts and top referencing docs.
- Updated the generated external-sources index summary (`docs/214`) and the pin-exemptions protocol tooling section (`docs/228`) to point to the review queue.

## v202 (2026-02-26)

Pinned core CDF + example hygiene sources (tight; no schema changes):

- Pinned sha256 for core NIST Voting **Common Data Formats** specs (BD/CVR/VRI/ERR/EEL) and NIST CDF implementation guidance; Track A CDF docs now cite these as `source:` (not `xref:`) so deployable guidance is auditably anchored (`docs/62`, `docs/70`; lockfile + generated indexes).
- Pinned sha256 for RFC example-domain/IP references (RFC 2606/5737/3849/9637) and NIST SP 800-122 (PII handling) to reduce “blocked by default” drift risk in publishable-safe placeholder guidance (`docs/189` citations remain informative).
- Pinned sha256 for VoteAgain (USENIX Security 2020) revoting paper, keeping coercion/revoting references stable without bundling the PDF.
- Tightened the pin-exemptions protocol wording: only mark sources `blocked` after an actual failed fetch attempt (`docs/228`).

## v201 (2026-02-26)

CDF source grounding + tag hygiene (tight; no schema changes):

- Added lockfile entries for core NIST Voting **Common Data Formats** specs (BD/CVR/VRI/ERR/EEL) plus implementation guidance, and updated Track A CDF docs to cite them via the lockfile (`xref:`) so drift risk is explicit and reviewable (`docs/62`, `docs/70`).
- Normalized lockfile tags to **lower_snake_case** (no hyphens) and tightened the drift firewall to enforce `[a-z0-9_]+` tags, reducing accidental tag-cardinality growth and keeping generated triage views stable (`evidence/lock/external-sources.toml`, `scripts/check_external_sources_lockfile.py`, `scripts/gen_external_sources_index.py`).
- Added a short tag-conventions section to the pin-exemptions protocol (`docs/228`).

## v200 (2026-02-26)

Citation discipline + reading/triage ergonomics (tight; no schema changes):

- Removed raw external URLs from early Track A/B docs and routed all external references through the lockfile (`source:` / `xref:`), keeping citations stable and reviewable without bundling third-party artifacts (`docs/06`, `docs/07`, `docs/11`; new lockfile IDs).
- Added a second generated external-sources view grouped by **primary tag** (first tag; each source appears once to avoid duplication): `docs/230-external-sources-by-primary-tag.md` (generator: `scripts/gen_external_sources_index.py`).
- Tightened `docs/references.md` into a small lockfile-first pointer page (no raw URLs; points to the generated indexes).
- Replaced an unsafe placeholder `example dot gov` URL in a code example with the RFC2606-reserved `.example` TLD (`docs/201`).

## v199 (2026-02-26)

Research → deployable promotion discipline (tight, no schema changes):

- Added `docs/229-experiment-to-spec-promotion-protocol.md` (E0–E3 staged promotion protocol + bounded “experiment card”) to prevent untested assumptions from leaking into Track A surfaces.
- Wired the protocol into the backlog and entrypoints (`172`, `207`, `docs/START_HERE.md`, `README.md`, `ARCHIVE_INDEX.md`, `docs/13`).

## v198 (2026-02-26)

Unpinned external source drift risk tightening (tight, no third-party bundling):

- Release gate now enforces **bounded review windows** for unpinned lockfile entries: `review_by` must be within a deterministic cap relative to `retrieved` (caps depend on `pin_exemption`; see `docs/228`).
- Unpinned lockfile entries now MUST include `retrieved` (so review windows are meaningful and auditable).
- `scripts/verify_external_sources_lock.py` now surfaces `retrieved` and the computed review window (vs cap) for unpinned SKIP lines, making local triage faster without opening the lockfile.
- Updated policy/playbook docs to reflect the enforced windows (`docs/151`, `docs/191`, `docs/228`).

## v197 (2026-02-26)

Source-citation semantics hardening (tight, no schema changes):

- The release gate now enforces that any `source: <id>` citation across the archive refers to pinned external bytes (sha256 present); use `xref:` for unpinned/informative refs (`scripts/check_external_sources_lockfile.py`; policy `docs/151`).
- `scripts/verify_external_sources_lock.py` now uses `tomllib` and surfaces `pin_exemption` + `review_by` for unpinned entries in its SKIP output, making local triage faster without opening the lockfile (`docs/228`).
- Fixed one stray `source:` citation that pointed at an intentionally-unpinned RFC entry (`docs/189`).

## v196 (2026-02-26)

External source triage tightening (tight, no third-party bundling):

- Unpinned external sources now require explicit `pin_exemption` + `review_by` markers in the lockfile, making drift risk reviewable and preventing “sha256 blank forever” footguns (`docs/228`; `evidence/lock/external-sources.toml`; `scripts/check_external_sources_lockfile.py`).
- The generated no-URL external sources index (`docs/214`) now surfaces exemption + review-by columns for quick pin triage without expanding the archive.
- Updated source pinning policy + playbook docs to match the explicit exemption protocol (`docs/151`, `docs/191`).

## v195 (2026-02-26)

Archive maintenance + drift-firewall coherency (tight, no schema changes):

- Added `docs/227-refactor-and-growth-protocol.md` (refactor classes + tombstones + growth discipline) so structural reorganizations don’t create link rot or accidental semantic drift.
- Added intent metadata for `tools/compare_public_fingerprints.py` in the tool-maturity registry (`artifacts/registries/tool-maturity.csv`).
- Refreshed the minimal PacketVerificationReport example packet pins (tool version/archive version + registry digest pins) so publishable verifier outputs remain comparable across releases.
- Updated entrypoints/indexes to reference the new refactor protocol and regenerated `MANIFEST.sha256`.

## v194 (2026-02-26)

Public fingerprint drift-firewall hardening (tight, no schema changes):

- Public fingerprint hashing now preserves *multiple* warning conditions per file (e.g., truncation + JSON canonicalization failure) instead of dropping one, keeping comparability diagnostics honest (`tools/public_fingerprint_report.py`).
- Verifier now elevates key public fingerprint warnings into stable publishable WARN codes (`public_fingerprint_input_truncated`, `public_fingerprint_json_canonicalize_failed`) so mirrored packets don’t silently compare on partial/non-canonical surfaces (`tools/observer_verify_packet.py`; `docs/226`; registry + generated code list).

## v193 (2026-02-26)

Public fingerprint reviewer ergonomics + verifier-surface hardening (tight, no schema changes):

- Added `tools/compare_public_fingerprints.py` to compare two packets' *public fingerprints* and print a tight, path-keyed diff when they differ (helps mirror/dispute-bundle review without bundling large bodies).
- Added `--verify-public-fingerprint` to `tools/observer_verify_packet.py` to verify a shipped `public-fingerprint.json` matches computed bounded packet surfaces; introduced new publishable verifier problem codes (`public_fingerprint_*`) for mismatch/invalid/missing/unavailable outcomes.
- Updated publishable preflight + divergence bundle + fingerprint docs/checklists to wire the reviewer flow (`docs/173`, `docs/222`, `docs/226`, checklist `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`) and updated `docs/193` + tool index.

## v192 (2026-02-26)

Public fingerprint ergonomics + stability tightening (tight, no schema changes):

- Made `tools/public_fingerprint_report.py` output optionally **stable-bytes** via `--stable` (omits `generated_at`) and added `--write-default` convenience to write `<packet_dir>/public-fingerprint.json`.
- Integrated public fingerprint computation into `tools/observer_verify_packet.py` (`--public-fingerprint`, `--public-fingerprint-out`, `--public-fingerprint-stable`) so dispute bundles can ship a verifier report *and* a digest-only mirror-equality artifact with one command.
- Updated publishable preflight + divergence-bundle docs/checklist to prefer stable fingerprint output (`docs/173`, `docs/222`, `docs/226`, checklist `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`).

## v191 (2026-02-26)

Digest-only mirror comparability (tight, no schema changes):

- Added a deterministic **public fingerprint** report tool for publishable packets, hashing only bounded surfaces (envelopes + JSON objects + small notes) and JCS-canonicalizing JSON to reduce formatting drift (`tools/public_fingerprint_report.py`; `DOC:docs/226...`).
- Wired the public fingerprint into publishable preflight guidance and the PublicNotice divergence dispute bundle flow (`docs/173`, `docs/222`, checklist `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`).
- Removed dead duplicate compact-notes parsing logic from the parity snapshot compare helper to reduce drift risk (`tools/compare_public_surface_parity_snapshots.py`).


## v190 (2026-02-26)

Compact-notes drift hardening + canonical variance hints (tight, no schema changes):

- Added a shared stdlib parser/canonicalizer for compact request-context notes (`req[...] vary[...] age[...]`) to reduce cross-tool drift (`tools/compact_notes.py`).
- Canonicalized `vary[...]` emission in capture distillers (lower-case, comma-separated, no spaces; dedup+sorted) so publishable variance hints compare cleanly across capture tools (`tools/http_capture_common.py`).
- Hardened publishable lint to WARN on non-canonical or unbounded `vary[...]` and non-integer `age[...]` tokens (both JSON notes and packet text surfaces), keeping split-view bundles tight and publication-safe (`tools/public_artifact_lint.py`).
- Updated request-context guidance + capture-note template/quickchecks to prefer canonical `vary[...]`/`age[...]` forms (docs `223`/`224`; template `artifacts/templates/public-surface-capture-note.md`; checklists `artifacts/checklists/public-surface-capture-note-quickcheck.md`, `artifacts/checklists/public-artifact-redaction-checklist.md`).


## v189 (2026-02-26)

Publication hygiene ergonomics + safer example literals (no schema changes):

- Added WARN-only suppression directives (`lint-allow: <code>`) scoped to packet `redaction-log.md` so rare, justified publication exceptions are explicit and reviewable (`tools/public_artifact_lint.py`; template `artifacts/templates/redaction-log.md`; checklist `artifacts/checklists/public-artifact-redaction-checklist.md`; policy `docs/189`).
- Reduced noisy false positives for *non-identifying placeholders*: the publishable lint no longer WARNs on RFC-reserved example IPv4 blocks or reserved example email domains, and it recognizes the expanded IPv6 documentation space (`3fff::/20`) alongside `2001:db8::/32` (`tools/public_artifact_lint.py`).
- Added `--list-codes` / `--explain <code>` for the publishable lint to keep remediation tight without expanding docs (`tools/public_artifact_lint.py`).
- Added cite-first external pins for documentation placeholders and PII framing (unpinned best-effort entries where retrieval is blocked), and regenerated the generated index (`evidence/lock/external-sources.toml`, `docs/214`).


## v188 (2026-02-26)

Tight operator ergonomics + publication safety (no schema changes):

- Enhanced the parity snapshot compare helper to canonicalize and diff compact request-context notes (`req[]/vary[]/age[]`), surfacing key-level context deltas (ua/lang/cache/etc) when snapshots differ (`tools/compare_public_surface_parity_snapshots.py`).
- Hardened the publishable lint: added high-signal token patterns (Google API keys, Stripe live keys), added WARNs for phone/lat-long coordinate literals, and reported line numbers for findings in packet text surfaces to make remediation faster without printing bodies (`tools/public_artifact_lint.py`).
- Updated the sensitive-material policy and redaction checklist to reflect expanded publishable-lint PII warnings (`docs/189`, `artifacts/checklists/public-artifact-redaction-checklist.md`).


## v187 (2026-02-26)

Publishable safety + split-view ergonomics tightening (tight, no schema changes):

- Hardened `tools/public_artifact_lint.py` with conservative **secret-token markers** (FAIL on likely cloud/API tokens; expanded private-key marker coverage) and added WARNs for likely PII literals (IP addresses, email addresses) to reduce accidental publication of identifying material.
- Refined the split-view variant probing recipe to include **cookie/challenge gating** as a first-class axis and to require `req[...] vary[...] age[...]` note lines for each probe (docs `224`).
- Added a tiny operator checklist for split-view variant probing (`CHECK:artifacts/checklists/split-view-variant-probing-checklist.md`) and indexed it in `docs/20`.


## v186 (2026-02-26)

Publishable preflight tightening (tight, no schema changes):

- Extended `tools/public_artifact_lint.py` to also scan small **text surfaces** in packet-shaped bundles (root `README.*`, `capture-note.md`, `redaction-log.md`, plus `notes/**/*.md|txt`) for obvious header-marker leaks and private-key markers, and to apply the same `req[...]` compact-notation checks outside JSON.
- Added `--lint-public` (and `--lint-max-string`) to `tools/observer_verify_packet.py` to run the publishable hygiene lint and surface only stable summary codes (`public_artifact_lint_failed` / `public_artifact_lint_warn`) in the packet verification report.
- Added the new lint summary codes to the verifier problem-code registry and updated operator guidance/checklists to prefer the one-command preflight (`docs/173`, `docs/177`, `docs/193`, `docs/222`; checklist `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`).

## v185 (2026-02-26)

Request-context canonicalization + parity diff context surfacing (tight, no schema changes):

- Normalized compact `req[...]` hint values (Accept-Language primary tag only, canonical cache/resolver spellings, coarse geo/asn forms) in the bounded capture helper (`tools/http_capture_common.py`) to keep publishable notes comparable across capture tools.
- Expanded `tools/public_artifact_lint.py` request-context checks: flags additional header-marker leaks (`Set-Cookie`, `X-Api-Key`) and warns on suspicious/unbounded `lang`/`geo`/`asn`/`cache`/`resolver` values.
- Enhanced the parity snapshot compare helper to surface `req[...] vary[...] age[...]` context deltas when snapshots differ (`tools/compare_public_surface_parity_snapshots.py`).
- Tightened request-context guidance to prefer ISO 3166-2 `region=CC-SS` and primary BCP47 language tags (docs `224`; template `artifacts/templates/public-surface-capture-note.md`; checklist `artifacts/checklists/public-surface-capture-note-quickcheck.md`).
- Regenerated the minimal PacketVerificationReport example packet so its embedded tool/archive version pins match `v185`.

## v184 (2026-02-26)

Tight capture robustness + publishable preflight wiring (no schema changes):

- Made the stdlib HTTP capture parser tolerant of indented status lines common in `wget -S/--server-response` captures, reducing “missing status line” false negatives in distillers (`tools/http_capture_common.py`).
- Normalized compact `age[...]` request-context notes to deterministic integer seconds (keeps publishable notes comparable across capture tools) (`tools/http_capture_common.py`).
- Wired “publishable packet preflight” into the places operators follow: added explicit `public_artifact_lint` invocation guidance in canonical packet docs (`173`) and the PublicNotice divergence dispute minspec + checklist (`222`; `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`).
- Tightened split-view challenge guidance so monitors include bounded `req[...] vary[...] age[...]` hints when mismatches are plausible (`docs/202`) and clarified capture-note tooling tolerance (`docs/223`).

## v183 (2026-02-26)

Publication safety hardening for request-context notes (tight, no schema changes):

- Added `resolver_hint` to capture-note guidance and template to classify resolver-driven split views without leaking transcripts (docs `223`; template `artifacts/templates/public-surface-capture-note.md`).
- Clarified `cache_bypass` semantics in `docs/224` (record header-level bypass attempts; avoid publishing cache-buster query values).
- Hardened the publishable packet linter to catch accidental auth/cookie header marker leaks and unsafe `req[]` cookie values; added a warning when `req[] ua` looks like a full user-agent string (`tools/public_artifact_lint.py`).
- Pinned and indexed RFC 9110 (HTTP Semantics) for `Vary` / content-negotiation guidance in split-view investigations (`source: rfc9110_txt`; regenerated `docs/214`).

## v182 (2026-02-26)

Compact request-context note encoding + tool support (tight, no schema changes):

- Added a canonical compact `req[...]` / `vary[...]` / `age[...]` notation for request-context + response-variance hints (docs `224.2a`) to keep split-view investigations copy/pasteable across parity snapshots, liveness beacons, and capture notes.
- Extended the stdlib capture distillers to optionally emit these notes (`tools/http_capture_to_parity_observation.py`, `tools/http_capture_to_observation.py`; helper in `tools/http_capture_common.py`).
- Tightened operator guidance to prefer canonical encoding where context matters (docs `201`, `210`, `216`, `223`; checklist `artifacts/checklists/public-surface-capture-note-quickcheck.md`; template `artifacts/templates/public-surface-capture-note.md`).
- Updated the near-term agenda to track this tightening as part of public-surface authenticity ergonomics (`docs/207`).

## v181 (2026-02-26)

Tight integrations + lockfile-first reference hygiene (no schema changes):

- Updated incident/dispute bundle guidance to explicitly carry bounded request context (`224`) and transformation accountability (`225`) where relevant (docs `211`, `216`, `222`; checklist `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`).
- Refactored `docs/references.md` to be lockfile-first (prefer `source:` / `xref:` IDs; reduced dependence on raw URLs).
- Added three unpinned external-source entries (ENR checklist + NIST ENR page + IFES briefing) and regenerated `214`.

## v180 (2026-02-26)

Hashes-first redaction logs (tight, no schema changes):

- Added `DOC:docs/225-redaction-logs-and-transformation-accountability.md`: a small redaction-log convention (source/derived digests + bounded transformation reasons) to rebut “you edited the evidence” without bundling removed material.
- Added `TEMPLATE:artifacts/templates/redaction-log.md` and `CHECK:artifacts/checklists/redaction-log-quickcheck.md` for bundle-ready `redaction-log.md` entries.
- Updated `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`, capture-note and divergence-bundle guidance (`223`, `222`), and claim-card surfaces (`217`, `artifacts/templates/claim-card.md`) to cite and ship `redaction-log.md` when transformations are load-bearing.
- Updated navigation (`README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/13-artifact-index.md`), Track A curation, and the artifacts/templates index (`docs/20`).

## v179 (2026-02-25)

Request-context discipline for split-view investigations (tight, no schema changes):

- Added `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`: bounded fields + probing recipe (UA/lang/cache/geo/Vary) to classify split-view root causes without bundle bloat.
- Updated `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`, `DOC:docs/201-public-surface-parity-snapshots.md`, `TEMPLATE:artifacts/templates/public-surface-capture-note.md`, and `CHECK:artifacts/checklists/public-surface-capture-note-quickcheck.md` to record request context and response variance hints when relevant.
- Updated navigation (`README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/13-artifact-index.md`) and Track A curation to include `224`.

## v178 (2026-02-25)

Doc-ID collision drift firewall (tight, meta-engineering):

- Added `SCRIPT:scripts/check_doc_number_collisions.py` and wired it into `scripts/release_gate.py` to prevent numbered doc ID collisions except via tombstone aliases.
- Updated `DOC:docs/162-release-and-ci-evidence-pipeline.md` and `DOC:docs/163-artifact-reference-conventions.md` to document the policy.

## v177 (2026-02-25)

Surface-capture time pinning (tight, no new schemas):

- Extended `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md` to record `time_source`/`time_uncertainty` and optionally pin time proof digests (RFC3161/Roughtime/time beacon) by reference to `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md`.
- Updated `TEMPLATE:artifacts/templates/public-surface-capture-note.md` and `CHECK:artifacts/checklists/public-surface-capture-note-quickcheck.md` accordingly.
- Updated `DOC:docs/222-publicnotice-divergence-dispute-bundle-minspec.md` to optionally include `hfv.time.beacon` / bounded time proofs when wall-clock timing is disputed.

## v176 (2026-02-25)

Public-surface capture provenance tightening (no new schemas):

- Added `docs/223-public-surface-capture-notes-and-reproducibility.md`: minimal capture-note convention for pinning raw HTTP capture bytes behind hashes-first artifacts (parity snapshots / divergence bundles) without shipping bodies by default.
- Added `artifacts/templates/public-surface-capture-note.md`: canonical `capture-note.md` template for dispute bundles.
- Added `artifacts/checklists/public-surface-capture-note-quickcheck.md`: 1-page gate to keep capture notes small, secret-free, and digest-complete.
- Updated claim-card template to include optional acquisition-note pins (`artifacts/templates/claim-card.md`).
- Cross-linked `223` from `201`, `205`, `210`, `216`, `221`, `222`, and the divergence bundle checklist; updated `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/13-artifact-index.md`, and Track A curation.

## v175 (2026-02-25)

Parity-failure dispute handoff tightening (no new schemas):

- Added `docs/222-publicnotice-divergence-dispute-bundle-minspec.md`: minimal handoff bundle recipe for PublicNotice effective-state divergence (turns `221` non-convergence into a bounded, offline-verifiable dispute artifact).
- Added `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`: one-page assembly checklist aligned to `222`.
- Extended publishable surface anomaly codes with `surface_effective_state_divergence` (registry + generated `docs/SURFACE_ANOMALY_CODES.md`) and referenced it from parity snapshot guidance (`201`) and monitoring outputs (`221`).
- Cross-linked `222` from `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `215`, `216`, `211`, and `08`; included `222` in Track A curation (bundle regeneration).

## v174 (2026-02-25)

PublicNotice monitoring + convergence (tight, no new schemas):

- Added `docs/221-publicnotice-monitoring-and-convergence.md`: a small monitor contract for feed/notices integrity checks, split-view detection, and deterministic effective-state comparisons via `220`.
- Added `artifacts/checklists/publicnotice-feed-monitoring-checklist.md`: operator routine for continuous feed integrity + parity + convergence monitoring (bounded incident routine with `201` + `186`).
- Cross-linked `221` from `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `200`, and `220`; included `221` in Track A curation.

## v173 (2026-02-25)

Notice graph semantics + epistemic-tag format unification (tight, no new schemas):

- Added `docs/220-publicnotice-graph-resolution-and-effective-state.md`: deterministic semantics for resolving `supersedes_notice_id` and `correction_of_notice_id` into an effective “current official state” for status boards and monitors.
- Refactored epistemic-tag formatting to use the canonical `[TAG|CONF]` syntax from `218` across `219`, `artifacts/checklists/public-update-epistemic-quickcheck.md`, and `artifacts/templates/public-statement-template.md` (and removed the non-standard `CORRECTED` tag example).
- Cross-linked `220` from `186`, `195`, `200`, and `219`; updated `README.md`, `ARCHIVE_INDEX.md`, and `docs/START_HERE.md`; included `220` in Track A curation and updated `docs/13-artifact-index.md`.

## v172 (2026-02-25)

Uncertainty-safe public updates (tight, no new schemas):

- Added `docs/219-uncertainty-safe-public-updates.md`: compact update contract for PublicNotice and signed statements using epistemic tags (`218`) with auditable corrections.
- Added `artifacts/checklists/public-update-epistemic-quickcheck.md`: 60-second pre-publish gate for tagged updates + reproducibility hooks.
- Updated `artifacts/templates/public-statement-template.md` to include scope + epistemic-tag placeholders and an optional claim-card pointer.
- Cross-linked `219` from `186`, `195`, `216`, `08`, `README.md`, `ARCHIVE_INDEX.md`, and `docs/START_HERE.md`; included `219` in Track A curation (bundle regeneration).

## v171 (2026-02-25)

Epistemic discipline (tight, no new schemas):

- Added `docs/218-epistemic-status-tags-and-confidence-rubric.md`: small tag + confidence rubric for deception-resistant statements in claim cards and public notices.
- Updated claim-card surfaces to require tags: `docs/217-...` + `artifacts/templates/claim-card.md` (and cross-links from `216`, `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`).
- Added a glossary entry for epistemic tags (`196`) and included `218` in Track A curation (regenerated bundle docs).

## v170 (2026-02-25)

Claim-boundary ergonomics (bundle-ready, size-disciplined):

- Added `docs/217-claim-cards-and-traceability-minspec.md`: a tight claim-card minspec for shipping alongside evidence bundles, explicitly tying disputes to PO-IDs and bounded evidence tokens.
- Added `artifacts/templates/claim-card.md`: canonical claim-card template (intended to ship as `claim.md` inside a bundle).
- Cross-linked claim cards from `README.md`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`, `docs/211-...`, `docs/216-...`, and updated `docs/13-artifact-index.md` + Track A bundle generation.

## v169 (2026-02-25)

Tight incident triage ergonomics (no schema bloat):

- Added `docs/216-incident-triage-and-evidence-quickmap.md`: a compact symptom→packet map linking common incident allegations to bounded evidence kinds, operator checklists, and claim-first bundle recipes.
- Added `artifacts/checklists/incident-triage-quickcheck.md`: a one-page “first 30 minutes” checklist aligned to `216`.
- Promoted operator navigation in Track A’s curated bundle by adding `08`, `215`, `216`, and `211` (generated from `artifacts/bundles/track-a.toml`).

## v168 (2026-02-25)

Lifecycle alignment without schema bloat:

- Added `docs/215-election-lifecycle-evidence-map.md`: a one-page phase map linking the real-world election timeline to the archive’s evidence/public-surface lanes and operator checklists.
- Updated `docs/START_HERE.md`, `docs/08-operations.md`, `README.md`, and `ARCHIVE_INDEX.md` to cross-link the new map (navigation-only; no new kinds).

## v167 (2026-02-25)

Tight triage ergonomics for publishable `surface_*` anomaly codes (no bloat):

- Added `tools/surface_anomaly_rollup.py`: bounded rollup of anomaly-note codes across packets/payloads (helps summarize cache/split-view symptoms without shipping bodies).
- Wired the helper into the operator smoke gate and tool maturity registry.
- Updated `tools/README.md` and `docs/START_HERE.md` to point to the new rollup workflow.

## v166 (2026-02-25)

Tight operator ergonomics for missingness surface diffs (no bloat):

- Added `tools/compare_liveness_beacons.py`: bounded diff between two LivenessBeacon payloads/packets (exit 0 if no diffs; exit 3 if diffs).
- Wired the new helper into the operator smoke gate using two small synthetic diff vectors under `artifacts/test-vectors/`.
- Updated `docs/210`, `tools/README.md`, and the tool maturity registry to point to the new diff workflow.

## v165 (2026-02-25)

Tight operator ergonomics for split-view triage (no bloat):

- Added `tools/compare_public_surface_parity_snapshots.py`: bounded diff between two PublicSurfaceParitySnapshot payloads/packets (exit 0 if no diffs; exit 3 if diffs).
- Wired the new helper into the operator smoke gate using two small synthetic diff vectors under `artifacts/test-vectors/`.
- Updated `docs/201` and `tools/README.md` to point to the new diff workflow.

## v164 (2026-02-25)

Tight publication-hygiene drift firewalls (no bloat):

- Centralized publishable allowlists in `tools/publication_policy.py` (shared freshness-header keys, disallowed body/capture keys, default bounds) to reduce drift across operator helpers.
- Updated `tools/public_artifact_lint.py` (and the bounded HTTP capture helpers) to import the shared policy constants.
- Added a release-gate check `scripts/check_example_packets_public_artifact_lint.py` that runs the publishable linter across all `artifacts/examples/evidence_packet_*` directories.

## v163 (2026-02-25)

Tight publication hygiene drift firewall (no bloat):

- Added `tools/public_artifact_lint.py`: conservative publishable-packet lint (flags obvious body/capture fields, unbounded strings/headers, and unknown `surface_*` anomaly-note codes).
- Wired the linter into the operator smoke gate and maturity registry (`smoke_tested=yes`) so the publishable-redaction ergonomics can’t silently rot.
- Updated the public artifact redaction checklist and `tools/README.md` to point to the new lint step.

## v162 (2026-02-25)

Tight operator ergonomics for publication-coverage workflows (no bloat):

- Added `tools/publication_coverage_report_card.py`: a bounded, copy/pasteable digest card for `hfv.coverage.publication_report` envelopes (wired into `tools/evidence_object_card.py` + smoke gate).
- Promoted the public-surface anomaly-code registry pin to the default output of `tools/public_surface_pins.py --json` (keeps comparability pins complete without requiring `--all`).

## v161 (2026-02-25)

Tight evidence-minimizing publication hygiene (no bloat):

- Added a bounded **public artifact redaction checklist** (`artifacts/checklists/public-artifact-redaction-checklist.md`) and linked it from offline bundles (`92`) and retention policy (`98`).
- Fixed `tools/public_surface_parity_snapshot_card.py` to actually emit its bounded mismatch diagnostics, and to only treat **lowercase snake_case** note prefixes as anomaly codes (avoids misclassifying freeform notes).

## v160 (2026-02-25)

Tight comparability for cache/split-view monitoring without schema bloat:

- Added a **publishable surface anomaly-code registry** (`artifacts/registries/surface-anomaly-codes.csv`) and generated reference list (`docs/SURFACE_ANOMALY_CODES.md`) for use in bounded monitoring `notes` fields (parity snapshots + liveness beacons).
- Extended the release gate + public-surface pin helper to cover the new registry (`tools/public_surface_pins.py --all`) and added a strict drift firewall (`scripts/check_surface_anomaly_codes_registry.py`).
- Upgraded `tools/public_surface_parity_snapshot_card.py` to provide tighter mismatch diagnostics (digest grouping + note/parse-error cues) while staying bounded.
- Updated `docs/201`, `docs/210`, `docs/207`, and `docs/START_HERE.md` to point to the anomaly-code surface and reinforce the `code[:context]` convention.

## v159 (2026-02-25)

Tight maintainability + robustness for bounded HTTP capture tooling (no bloat):

- Refactored capture parsing into `tools/http_capture_common.py` (shared by both capture→observation helpers) to reduce duplication and harden multi-response selection logic.
- Expanded status-line support (HTTP/2.0, HTTP/3) and added a LF-only + HTTP/2 regression vector (`artifacts/test-vectors/http_capture_http2_lf_example.txt`) wired into the operator smoke gate.
- Updated the tooling maturity registry to include the new shared library module.

## v158 (2026-02-25)

Tight regression coverage for parity evidence + multi-response captures (no bloat):

- Wired `tools/public_surface_parity_snapshot_card.py` into the operator smoke gate and upgraded its maturity registry entry to `smoke_tested=yes` so the parity publication surface can’t silently rot.
- Added a redirect-chain capture regression vector (`artifacts/test-vectors/http_capture_redirect_chain_example.txt`) and extended the smoke gate to ensure capture tooling always selects the **last** HTTP response block.
- Fixed status-line parsing in `tools/http_capture_to_observation.py` and tightened the smoke gate contract to require `http_status` for bounded HTTP capture→observation workflows.
- Refreshed the minimal `PacketVerificationReport` example packet so embedded `tool.version/tool.archive_version` pins match `v158` after the version bump.

## v157 (2026-02-25)

Tight operator ergonomics for split-view parity snapshots (no bloat):

- Added `tools/http_capture_to_parity_observation.py`: converts a bounded HTTP capture (curl/wget output) into a schema-valid `PublicSurfaceParitySnapshot.observations[]` entry (status + `sha256:<hex>` body digest + served envelope `kind`/`payload_digest`/`tbs_digest` when parseable).
- Added a small synthetic regression vector (`artifacts/test-vectors/http_capture_public_notice_feed_example.txt`) and wired the tool into the operator smoke gate.
- Updated `docs/201` and `tools/README.md` to point to the capture→parity-observation workflow.

## v156 (2026-02-25)

Tight correctness hardening for evidence-minimizing capture tooling (no bloat):

- Fixed `tools/http_capture_to_observation.py` to emit schema-valid `sha256:<hex>` digests and to always include `observed_at` (defaults to “now (UTC)” if not supplied).
- Strengthened the operator smoke gate to enforce `observed_at` and digest formatting for the capture→observation workflow.
- Updated the cache/freshness drill docs + checklist (`205`, `210`, and the test plan artifact) and `tools/README.md` to match the now-schema-valid output contract.

## v155 (2026-02-25)

Tight evidence minimization for cache/split-view disputes (no bloat):

- Added `tools/http_capture_to_observation.py`: converts a raw HTTP capture (curl/wget output) into a bounded `observations[]` snippet (status + payload digest + freshness headers) without shipping response bodies.
- Wired a small synthetic capture vector into the operator smoke gate (`scripts/check_operator_tools_smoke.py`) and classified the tool in `artifacts/registries/tool-maturity.csv`.
- Updated cache/freshness drill artifacts (`205`, `210`, and the cache/freshness test plan checklist) to point to the capture→observation workflow.

## v154 (2026-02-25)

Tight operator ergonomics for freshness/missingness evidence (no bloat):

- Added `tools/liveness_beacon_card.py` and wired it into the operator smoke gate so liveness beacons have a bounded, publishable summary surface (and a regression vector).
- Tightened cache/split-view escalation glue: added a stale-pointer bundle recipe to `211` and clarified in `202` that freshness disputes should pair parity snapshots with beacons (headers) rather than expanding snapshot schema.
- Updated incident playbook + tooling index to reference the new beacon digest card (kept bounded; no new protocol surfaces).

## v153 (2026-02-25)

Tight operational hardening for freshness/parity evidence lanes (no bloat):

- Added minimal **example evidence packets** for `hfv.coverage.liveness_beacon` (`docs/210`) and `hfv.public.surface_parity_snapshot` (`docs/201`) so verifier tooling has regression vectors without rehosting large artifacts.
- Expanded `PublicSurfaceParitySnapshot.subject.surface_kind` to explicitly cover the machine-facing pointer surfaces used in cache/freshness disputes (`well_known_discovery`, `official_channel_directory`, `public_notice_feed`, `public_notice_signing_keyset`) to reduce “other” ambiguity.
- Tightened incident ops linkage by adding a small **stale-pointer / cache split-view** subroutine to the public notice + rumor response playbook (`HZ-020`).

## v152 (2026-02-25)

Tight cache/freshness operationalization for Track A (no bloat):

- Added a bounded **public-surface cache + freshness test plan** checklist (`artifacts/checklists/public-surface-cache-and-freshness-test-plan.md`) so `205` can be executed as a repeatable drill rather than prose.
- Wired the posture into existing evidence lanes: clarified **freshness header capture** (`ETag`, `Cache-Control`, `Age`, `Last-Modified`) in LivenessBeacons (`210`) and extended the parity monitoring checklist to record/compare those headers across vantages.
- Updated `205` and the near-term agenda (`207`) to point to the new operator artifact; added the checklist to the Track A artifact quick list (`20`).

## v151 (2026-02-24)

Tight source-pinning hardening for Track A (no bloat):

- Pinned the previously-unpinned Lindeman & Stark (2012) RLA reference (`stark_gentle_introduction_rla_2012_pdf`) in the external-sources lockfile (sha256 added; PDF still not bundled).
- Added `scripts/check_track_a_pinned_sources.py` and wired it into the release gate: numbered docs whose **Track:** includes `A` may not cite unpinned external sources.
- Added a tight citation-role split: `source: <id>` means pinned/normative; `xref: <id>` means informative or currently-unpinned (still lockfile-tracked). Updated lockfile tooling to treat both as citations, and converted unpinned `source:` refs to `xref:` so Track A can keep a strict pinned guarantee without blocking informative references.
- Updated source-pinning guidance (`151`) and the release gate doc (`162`) to reflect the new firewall.
- Regenerated the minimal PacketVerificationReport example packet so tool/version pins match v151 and the example remains a valid regression vector.
- Reclassified the external reading list (`docs/21`) as Track B (research annex) to avoid implying the bibliography itself is a deployable control surface.

## v150 (2026-02-24)

Tight drift firewalls for publishable verifier report packets (no bloat):

- Strengthened `scripts/check_packet_verification_report_linkage.py` to require the reference verifier to emit the key comparability pins (registry digests + manifest digests) in public report mode, catching silent regressions.
- Added `scripts/check_packet_verification_report_emit_packet.py` and wired it into the release gate; it runs `tools/observer_verify_packet.py --emit-evidence-object` and verifies that the emitted packet actually ships the pinned policy profile object and repeats `policy_profile_sha256` on the envelope subject.
- Updated `docs/162` to document the new required drift firewall.

## v149 (2026-02-24)

Tight comparability pins for attachment + receipt interpretation (no bloat):

- Added optional `attachment_requirements_sha256` and `receipt_profiles_sha256` to `schemas/PacketVerificationReport.json` so publishable packet reports can declare which attachment/receipt registries were used for required-attachment checks and transparency receipt profile interpretation; bumped PacketVerificationReport `report_version` to `1.1.4`.
- Updated the reference verifier tool (`tools/observer_verify_packet.py`) to emit these pins automatically when the registry files exist.
- Updated publishable verifier report guidance (`docs/193`) and strengthened the example-pin drift firewall; regenerated the minimal packet-report example so the new pins are present and consistent.

## v148 (2026-02-24)

Tight comparability improvement (no bloat):

- Added optional `manifest_jcs_sha256` to `PacketVerificationReport` (sha256 over RFC8785-JCS canonical bytes of a JSON manifest) so bundle boundaries remain comparable across mirrors even if JSON is reformatted; bumped `report_version` to `1.1.3`.
- Updated the reference verifier tool (`tools/observer_verify_packet.py`) to emit `manifest_jcs_sha256` when `manifest.json` parses as JSON; updated verifier docs (`188`, `193`) and strengthened the example-packet drift check.
- Regenerated the minimal packet-report example to include the new field and keep pins consistent.

## v147 (2026-02-24)

Tight maintainability improvements (no bloat):

- Strengthened the external-sources lockfile drift firewall: every `[[source]]` entry now MUST include a **non-empty tag list** and a short note (size-capped) so triage/search stays cheap and the lockfile stays lean.
- Filled the one missing tag list entry (`eac_incident_response_comms_guide_pdf`) so generated source indexes remain informative.
- Updated `VerifierPolicyProfile` schema + template text to reference the preferred `PacketVerificationReport.policy_profile_sha256` field (instead of legacy note-string pins).
- Added a minimal “verifier policy profile digest” row to the Track A public-surface checklist (`195`) so deployable rumor-control/status surfaces include comparability pins.

## v146 (2026-02-24)

Small, high-leverage drift-resistance improvements (no bloat):

- Added `scripts/check_no_tombstone_refs.py` and wired it into the release gate so normative docs cite canonical docs, not tombstone aliases; updated policy notes in `162` and `163`.
- Publishable verifier report packets now repeat `policy_profile_sha256` on the `EvidenceEnvelope.subject` (digest only) to support index-only scans; strengthened the verifier-report example pin check and regenerated the minimal report-packet example.

## v145 (2026-02-24)

Tight verifier comparability packaging (no bloat):

- `tools/observer_verify_packet.py --emit-evidence-object` now **ships the policy profile bytes** as a detached, content-addressed object (`objects/sha256-<hex>.json`) when `--policy-profile <file>` is provided; the manifest includes the artifact so report packets are fully offline-comparable.
- Strengthened drift firewalls: `scripts/check_example_report_pins.py` now requires the minimal packet-report example to include the pinned policy profile artifact (and verifies its hash).
- Updated verifier docs (`188`, `193`) and added a compact comparability claim + proof obligation (`CLM-039`, `PO-015`).

## v144 (2026-02-24)

Tight comparability + citation-surface refactors (no bloat):

- Policy-profile digest pins are now **formatting-independent**: `tools/observer_verify_packet.py --policy-profile` computes `policy_profile_sha256` over RFC8785-JCS canonical bytes (docs/176) and bumps PacketVerificationReport `report_version` to `1.1.2`.
- Added `tools/policy_profile_digest.py` to compute `sha256:<hex>` pins for `VerifierPolicyProfile` JSON files (JCS canonical bytes) without network access.
- Refactored external-source drift firewalls + source index generation to scan repo markdown surfaces consistently (docs + artifacts/checklists + playbooks), using a shared helper (`scripts/_shared/md_scan.py`); updated `docs/162` accordingly.
- Regenerated the minimal PacketVerificationReport example packet and refreshed the report template to align with v144 and the canonical policy-profile digest rule.

## v143 (2026-02-24)

Tight verifier comparability upgrade (no bloat):

- Promoted the verifier policy profile digest to a first-class field: added optional `policy_profile_sha256` to `schemas/PacketVerificationReport.json` (still compatible with legacy `notes[]` pin strings).
- Updated `tools/observer_verify_packet.py` to emit `policy_profile_sha256` via `--policy-profile` (path) or `--policy-profile-sha256` (direct pin) and bumped PacketVerificationReport `report_version` to `1.1.1`.
- Strengthened drift firewalls: `scripts/check_packet_verification_report_linkage.py` now asserts the policy-profile pin is emitted and schema-valid; `scripts/check_example_report_pins.py` requires the pin in the minimal packet-report example.
- Regenerated `artifacts/examples/evidence_packet_packet_verification_report_minimal/` and refreshed `artifacts/templates/packet-verification-report-example.json` to align with v143.

## v142 (2026-02-24)

Tight schema + comparability hardening (no bloat):

- Added `schemas/VerifierPolicyProfile.json` and wired it into schema validation (`scripts/validate_schemas.py`) so the policy-profile template stays machine-parseable and comparable across verifier outputs.
- Updated `docs/188` to cite the policy-profile schema and clarified that publishable reports should pin the profile via sha256 in `PacketVerificationReport.notes[]`.
- Refreshed the minimal PacketVerificationReport example packet so embedded `tool.version/tool.archive_version` pins match `v142`.

## v141 (2026-02-24)

Tight comparability + drift-resistance improvements (no bloat):

- External sources index (`214`) now ranks the unpinned “pin-first” shortlist using **in-repo citation counts** (load-bearing signal) in addition to tag-based authority heuristics; generator updated.
- Added a minimal **verifier policy profile** template (`artifacts/templates/verifier-policy-profile.json`) and documented the publishable digest hook in `docs/188`.

## v140 (2026-02-24)

Tight, high-leverage improvements (still no archive bloat):

- External sources index (`214`) now includes a compact summary + “pin-first” shortlist of unpinned sources; generator updated accordingly.
- Added unpinned-source triage guidance to `docs/151` to prevent normative drift on mutable/blocked sources.
- Added a size-disciplined Track A “minimum deployable checklist” to `docs/195` (rumor-control/status as verifiable public surfaces).
- Updated `docs/START_HERE.md` recent-additions range to include v140.

## v139 (2026-02-24)

Tight meta-engineering consistency fixes (no bloat):

- Fixed a Track A doc reference typo in the claims contract (`docs/166`) and clarified agenda discipline (`docs/207`) to point to the correct maintainer entrypoints (`150` + `183`).
- Added `scripts/check_doc_backtick_refs.py` and wired it into the release gate to catch filename typos in backticked doc references (not visible to markdown link checkers).
- Strengthened LLM maintainer guardrails with an explicit dual-use boundary pointer to `167` (N‑6).
- Removed contradictory wording in pinned-source notes for RFC 8615 and RFC 9111 so the lockfile and generated index (`docs/214`) stay coherent.
- Refreshed the minimal PacketVerificationReport example packet so embedded `tool.version/tool.archive_version` pins match `v139`.

## v138 (2026-02-24)

Tight example ordering conventions (stable diffs, no bloat):

- Added `scripts/check_example_ordering_conventions.py` and wired it into the release gate: shipped examples must use canonical ordering (OfficialChannelDirectory channels by `channel_id`; PublicNoticeFeed entries honor declared `ordering`).
- Refreshed the comms/discovery example set to follow those conventions (reordered OfficialChannelDirectory example; updated WellKnown discovery pin chain).

## v137 (2026-02-24)

Tight external-sources navigation (no URLs, no bloat):

- Added `scripts/gen_external_sources_index.py` to generate `docs/214-external-sources-index.md` (lockfile IDs + pin status + retrieval date + tags + short notes; intentionally no URLs).
- Refactored `docs/161` to point to the generated index + canonical lockfile (reduces manual drift).
- Wired the generator into `scripts/release_gate.py`, documented it in `docs/162`, and added minimal pointers from `docs/151` and `ARCHIVE_INDEX.md`.

## v136 (2026-02-24)

Tight example-packet coherence + navigation (no bloat):

- Refactored example-packet `README.txt` conventions: single-envelope examples now declare `Example evidence packet for <kind>.` + `- Payload: <schema>`; bundle examples declare `- Envelopes:` + `- Payload schemas:`.
- Strengthened `scripts/check_example_packet_readmes.py` to enforce kind/schema coherence and a stable `Verify:` command that targets the packet directory.
- Added `scripts/gen_example_packets_index.py` and generated `docs/213-example-packets-index.md` (compact index of shipped example packets); wired into `scripts/release_gate.py`.

## v135 (2026-02-24)

Tight example-packet actionability (no bloat):

- Standardized `artifacts/examples/evidence_packet_*` READMEs to include a one-line `Verify:` command using `tools/observer_verify_packet.py`.
- Strengthened `scripts/check_example_packet_readmes.py`: READMEs remain size-capped and now must include a stable verifier command (prevents unusable examples / silent drift).

## v134 (2026-02-24)

Tight example-packet usability + drift firewall (no bloat):

- Added `scripts/check_example_packet_readmes.py` and wired it into the release gate: every shipped `artifacts/examples/evidence_packet_*` must include a tiny `README.txt` (size-capped) so implementer intent does not silently drift.
- Added missing `README.txt` notes for: `evidence_packet_enr_receipted`, `evidence_packet_packet_verification_report_minimal`, and `evidence_packet_publication_compliance_minimal`.

## v133 (2026-02-24)

Tight smoke-harness coherence (meta-engineering, no bloat):

- Added `scripts/check_operator_smoke_coverage.py` and wired it into the release gate: any tool marked `smoke_tested=yes` in `artifacts/registries/tool-maturity.csv` must be invoked by `scripts/check_operator_tools_smoke.py`.
- Expanded `scripts/check_operator_tools_smoke.py` dispatch coverage to include the Track A comms/discovery example packets, and required the `verifier_profiles_sha256` comparability pin from `tools/public_surface_pins.py --json`.
- Documented the new gate step in `docs/162` and clarified maintenance guidance in `docs/212`.

## v132 (2026-02-24)

Tight comparability-pin hygiene (small, operator-facing, no bloat):

- Extended `tools/public_surface_pins.py --all` to include a sha256 pin for `artifacts/registries/tool-maturity.csv`.
- Added `scripts/check_public_surface_pins_coverage.py` and wired it into the release gate: `public_surface_pins.py --all --json` must cover and correctly hash stable registry bytes when present.
- Documented the new gate step in `docs/162` and clarified `--all` usage in `docs/193`.

## v131 (2026-02-24)

Tight comms/discovery coherence drift firewall (no bloat):

- Added `scripts/check_discovery_pointer_coherence.py` and wired it into the release gate: verifies that the WellKnown/OfficialChannelDirectory/PublicNoticeFeed example set is mutually coherent (pinned payload digests + consistent discovery URLs) and that channel IDs used by examples are registered in `official-channels.csv`.
- Added a short coherence note to `docs/204` and documented the new gate step in `docs/162`.

## v130 (2026-02-24)

Salient drift firewalls + comms/discovery example alignment (kept lean):

- Added `scripts/check_example_payloads_against_schemas.py` and wired it into the release gate: bounded payload-vs-schema drift tripwire for shipped example packets (stdlib-only).
- Realigned the Track A comms/discovery example packets (`PublicNoticeFeed`, `OfficialChannelDirectory`, `WellKnownElectionStackDiscovery`) to match their declared schemas (and to use canonical `official-channels.csv` IDs).
- Tightened `schemas/WellKnownElectionStackDiscovery.json`: `pointers` now requires at least the OfficialChannelDirectory + PublicNoticeFeed payload digests (portable comparability anchor).

## v129 (2026-02-24)

Tight governance + drift-firewall improvements for registries and curated entrypoints:

- Added `scripts/check_registries_readme.py` and wired it into the release gate: every `artifacts/registries/*.csv` must be listed in `artifacts/registries/README.md` (prevents silent surface drift).
- Updated `artifacts/registries/README.md` to include verifier profile/code registries and tool maturity registry (keeps registry catalog complete).
- Added `docs/212-tooling-maturity-and-evidence-safety.md` to the Track A curated bundle (`artifacts/bundles/track-a.toml`).
- Refreshed the `evidence_packet_packet_verification_report_minimal` example so `tool.version/tool.archive_version` pins match `v129` after the version bump.

## v128 (2026-02-24)

Tight operator-safety improvements without inflating the archive:

- Added a **tool maturity + evidence-safety registry**: `artifacts/registries/tool-maturity.csv` + `docs/212-tooling-maturity-and-evidence-safety.md`; wired drift firewall `scripts/check_tool_maturity_registry.py` into the release gate.
- Added Track A **comms/discovery example packets** with required receipt+gossip attachments:
  - `artifacts/examples/evidence_packet_public_notice_feed`
  - `artifacts/examples/evidence_packet_official_channel_directory`
  - `artifacts/examples/evidence_packet_well_known_discovery`
- Extended operator smoke tests (`scripts/check_operator_tools_smoke.py`) to cover the new card tools and dispatch (`tools/evidence_object_card.py`).
- Strengthened verifier-output pin checking: `scripts/check_example_report_pins.py` now validates `verifier_profiles_sha256` when present.
- Public surfaces index (`docs/PUBLIC_SURFACES.md`) now includes the tool maturity registry entry.

## v127 (2026-02-24)

Tight clarity + anti-bloat improvements around doc aliases and release hygiene:

- Generated tombstone alias index: added `scripts/gen_tombstone_index.py` and generated `docs/TOMBSTONES.md`; wired generator into `scripts/release_gate.py`.
- Leaned the main numbered artifact index (`docs/13-artifact-index.md`) by omitting tombstone rows (canonical docs only); tombstones remain supported and auditable via `docs/TOMBSTONES.md`.
- Clarified the canonical OONI corroboration doc: moved the normative content to `docs/119-ooni-corroboration.md` and converted the old filename into a tombstone alias (stable references, less ambiguity).
- Tightened cache artifact policy: `scripts/check_no_cache_artifacts.py` now rejects `dist/` directories (aligns with `clean_local_artifacts.py` + manifest/zip exclusions).

## v126 (2026-02-24)

Tight meta-engineering + release hygiene (keeps the archive small and reproducible):

- Added a stdlib-only cleanup helper `scripts/clean_local_artifacts.py` to remove local cache/build artifacts (e.g., `__pycache__/`, `*.pyc`, `.pytest_cache/`, `evidence/cache/`, `dist/`) before running the release gate or packaging.
- Made deterministic ZIP packaging more robust: `scripts/build_release_zip.py` now excludes **nested** cache dirs (e.g., `tools/__pycache__/`) in addition to top-level prefixes.
- Updated the LLM maintainer protocol (`docs/183`) to explicitly include the cleanup step when running scripts locally.
- Refreshed the `evidence_packet_packet_verification_report_minimal` example so embedded `tool.version/tool.archive_version` pins match `v126` and include the optional `verifier_profiles_sha256` pin when present.

## v125 (2026-02-24)

Tight improvements focused on *comparability* and *anti-ambiguity* without inflating the archive:

- Added **verifier profile IDs** as a small public surface: `artifacts/registries/verifier-profiles.csv`, plus generated `docs/VERIFIER_PROFILES.md`.
  - `schemas/VerifierReport.json` now supports `supported_profiles[]` and `verifier_profiles_sha256` (optional comparability pin).
  - `schemas/PacketVerificationReport.json` supports optional `verifier_profiles_sha256`.
  - `tools/public_surface_pins.py` and `tools/observer_verify_packet.py` emit the profile-registry pin when present.
- Reduced false split-view alarms for PublicNotice feeds by standardizing **entry ordering**:
  - `schemas/PublicNoticeFeed.json` adds optional `ordering`.
  - `docs/200` adds canonical ordering guidance; template updated.
- Public surfaces index now includes verifier profiles; glossary adds a minimal definition.

## v124 (2026-02-24)

- Refactored the verifier-facing Evidence API surface doc (`docs/179`) to define **support profiles** (base integrity, public comms/discovery, witness governance) so implementations can make explicit, comparable claims without inflating the “minimum.”
- Expanded the generated public-surfaces index to include the **Track A comms/discovery spine** schemas (PublicNotice/Feed/SigningKeyset, OfficialChannelDirectory, WellKnown discovery) and the key monitoring surfaces (parity snapshots, security snapshots, liveness beacons), plus the bundle manifest schema; regenerated `docs/PUBLIC_SURFACES.md`.
- Compressed `docs/START_HERE.md` “Recent additions” into a small set of themes and pointed readers to `CHANGELOG.md` and `docs/207` (anti-bloat refactor).

## v123 (2026-02-24)

- Strengthened witness governance bootstrap as a public surface: added optional `witness_set_payload_sha256` (+ `witness_set_url`) to the well-known discovery payload (`schemas/WellKnownElectionStackDiscovery.json`), updated the spec (`docs/204`) and drafting template.
- Extended liveness beacons to observe witness governance drift: `schemas/LivenessBeacon.json` now permits a `witness_set` observation surface; updated `docs/210` and the beacon template to record the WitnessSet payload digest when available.
- Made the bootstrapping recommendation explicit in witness cosigning guidance (`docs/132`): publish the current WitnessSet digest via the well-known discovery surface to reduce selective disclosure risk.
- Linked witness-set selective disclosure/capture detection to the monitoring stack: extended `HZ-023` detection artifacts to include well-known discovery + liveness beacons.

## v122 (2026-02-24)

- Refactored witness governance payload schemas to reduce drift and key-confusion: introduced `schemas/WitnessMember.json` and used it from both `WitnessSet` and `WitnessSetChange` (consistent field names + shared semantics).
- Tightened anti-rollback semantics for witness governance: `WitnessSet` now supports optional hash-chaining via `previous_witness_set_payload_sha256`.
- Added an explicit (optional) binding from EPB witness policy to the published witness set via `EPB.witness_policy.witness_set_payload_sha256` (unambiguous witness ID → key resolution).
- Added bounded drafting templates for witness governance + compromise disclosure: `witness-set-payload.json`, `witness-set-change-payload.json`, `key-compromise-event-payload.json`.
- Extended schema drift checks to validate the new templates (and the liveness-beacon template) during the release gate.

## v121 (2026-02-24)

- Made witness governance a first-class, portable evidence surface: registered envelope kinds `hfv.witness.set` and `hfv.witness.set_change` (receipted+gossiped) and added a corresponding proof obligation/hazard pair (`PO-013`, `HZ-023`) to keep capture-resistance explicit.
- Registered `hfv.incident.key_compromise_event` (receipted+gossiped) so key-compromise announcements are publishable artifacts under the same anti-burying rules as other integrity evidence.
- Refactored `docs/159` to treat the CSV ledger as canonical (reduces drift by avoiding duplicated enumerations in prose) and updated witness docs (`132`, `134`, `135`) to label the new envelope kinds.

## v120 (2026-02-24)

- Added drift firewall `scripts/check_hazard_catastrophe_classes.py` (hazard register must use valid `C1..C5`) and wired it into `scripts/release_gate.py`.
- Made `CatastropheClass` a REQUIRED hazard-register field (doc update in `docs/158`) and added a tight change-review checklist: `artifacts/checklists/catastrophe-ordering-review-checklist.md`.
- Treated `dist/` as non-normative output: excluded it from `MANIFEST.sha256` and size-budget accounting to prevent release-zip accumulation bloat.

## v119 (2026-02-24)

- Elevated the archive’s catastrophe ordering into a bounded, stable vocabulary: added `artifacts/registries/catastrophe-classes.csv`, added drift firewall `scripts/check_catastrophe_classes_registry.py`, annotated the hazard register with `CatastropheClass`, and cross-linked from `docs/171` and `docs/158`.
- Tightened the receipt “don’t lie” invariant: clarified `docs/14`, added a receipt-UX misrepresentation response checklist, added hazard `HZ-022` and proof obligation `PO-014`, and regenerated the Track A MVR checklist.

## v118 (2026-02-24)

- Pinned sha256 for RFC 8615 (\`.well-known\` URIs) and RFC 9111 (HTTP caching) in the external sources lockfile (tightened evidence locking for public-surface guidance).
- Added the NDSS 2024 CT monitor inspections paper to the sources lockfile and updated monitor accountability guidance to cite it via \`source:\` (keeps external refs auditable and non-bloating).

## v117 (2026-02-24)

- Tightened liveness beacons against cohort-shaping of the monitoring ecosystem: `schemas/LivenessBeacon.json` now supports an optional `probe_cohort_plan_payload_sha256` (linking to a `ProbeCohortPlan`) and coarse `vantage` metadata (ASN/country-level; no IPs).
- Updated `docs/210` and `docs/104` to explicitly connect parity/missingness monitoring to the cohort-shaping threat model (`docs/127`–`130`), and updated the audience parity monitoring checklist accordingly.
- Extended the monitor-cohort capture hazard (`HZ-011`) to include liveness beacons as a detection artifact.

## v116 (2026-02-24)

- Added missing `schemas/EvidenceBundleManifest.json` and wired it into schema drift checks (the release gate now validates an example packet `manifest.json` against the schema). This closes a long-standing “spec says it exists” gap without growing the verifier TCB.
- Added `docs/211-court-evidence-bundle-recipes.md` (Track A): bounded, claim-first bundle recipes aligned to catastrophe classes (suppression, fork, cross-register, comms impersonation).
- Cross-linked court bundle recipes from `docs/43`.

## v115 (2026-02-24)

- Added `docs/210-liveness-beacons-and-missingness-surface.md` (Track A) plus `schemas/LivenessBeacon.json`, registered `hfv.coverage.liveness_beacon`, and added a drafting template. This provides a bounded, independent heartbeat stream that records reachability + observed digests for key public pointer surfaces, making “missingness about missingness” harder to bury.
- Integrated liveness beacons into the publication stack: updated `docs/181` (second-order missingness) and `docs/187` (compliance/coverage), updated proof obligation `PO-012`, and added beacon linkage to the deadline-miss hazard (`HZ-007`).
- Updated the audience parity monitoring checklist to include publishing liveness beacons during incidents.

## v114 (2026-02-23)

- Added `docs/208-publicnotice-signing-keys-and-channel-identity.md` (Track A) plus `schemas/PublicNoticeSigningKeyset.json`, registered `hfv.public.notice_signing_keyset`, and added a drafting template. This creates a verifiable root for “which keys can speak as the jurisdiction” for PublicNotices.
- Anchored PublicNotice signing keyset digests into discovery surfaces (`schemas/WellKnownElectionStackDiscovery.json`, `schemas/OfficialChannelDirectory.json`) and updated the comms spine (`docs/186`, `docs/195`, `docs/203`, `docs/204`).
- Added `docs/209-cross-register-consistency-evidence.md` (Track A) plus `schemas/CrossRegisterConsistencyReport.json`, registered `hfv.results.cross_register_consistency_report`, and added a drafting template; integrated into drift detection (`docs/69`) and proof obligation `PO-004`.
- Extended precinct closeout omission detection to optionally anchor physical custody evidence (`custody_anchor_sha256` in `schemas/PrecinctCloseoutIndex.json`; doc update in `docs/198`).
- Added a bounded “coverage without revealing the detection surface” pattern via `CoverageReport.commitments.canary_plan_commitment_sha256` (schema update + doc/checklist updates in `docs/61`, `docs/174`, `artifacts/checklists/canary-monitoring-checklist.md`).
- Tightened publication-contract missingness defenses (echoing + independent corroboration notes) in `docs/181`.
- Added `observer-kit/TCB.md` and linked it from the verifier MVP path (`docs/188`) for a courtroom-friendly minimum-TCB answer.
- Strengthened witness governance caution around financial bonding (docs `135`, `143`).

## v113 (2026-02-23)

- Added `docs/207-research-agenda-and-revision-ledger.md` (Shared): a two-screen near-term work queue that binds active research threads to claims/proof obligations/hazards and keeps backlog growth bounded.
- Refactored the long backlog to point at the compact agenda (`docs/172`) and extended the LLM maintainer protocol with an explicit “update the near-term agenda” step (`docs/183`).
- Updated entrypoints and canonical index (`docs/13-artifact-index.md`, `docs/START_HERE.md`, `ARCHIVE_INDEX.md`).
- Added a small meta-note to the evidence continuity hazard to keep agenda threads from getting lost during refactors (`artifacts/hazards/hazard-register.csv`, HZ-017).

## v112 (2026-02-23)

- Added `docs/206-digest-cards-and-low-bandwidth-publication.md` (Track A): tight practice for publishing bounded digest cards so SMS/screenshot/print channels can be re-anchored to verifiable objects.
- Added operator digest-card tools for discovery and hardening surfaces: `tools/official_channel_directory_card.py`, `tools/well_known_discovery_card.py`, `tools/official_surface_security_snapshot_card.py`, and wired dispatch via `tools/evidence_object_card.py`.
- Cross-linked digest-card guidance from the comms/public-surface spine (`docs/195`, `docs/199`, `docs/203`, `docs/204`, `docs/205`) and refreshed the official comms hardening checklist.
- Updated Track A navigation and indexes (`docs/track-a/README.md`, `artifacts/bundles/track-a.toml`, `docs/13-artifact-index.md`, `docs/START_HERE.md`, `ARCHIVE_INDEX.md`, `README.md`).

## v111 (2026-02-23)

- Added `docs/205-cache-and-freshness-controls-for-public-surfaces.md` (Track A): minimal cache/freshness posture for machine-facing pointer surfaces (feed/directory/well-known) so stale-pointer and replay-by-proxy confusion is bounded and provable.
- Cross-linked cache/freshness guidance from the comms/public-surface spine (`docs/195`, `docs/200`, `docs/203`, `docs/204`) and added a small glossary term (`docs/196`).
- Added an external reference entry for HTTP caching (RFC 9111) to the sources lockfile (`evidence/lock/external-sources.toml`) and refreshed Track A navigation/bundle configuration (`docs/13-artifact-index.md`, `docs/track-a/README.md`, `artifacts/bundles/track-a.toml`, `ARCHIVE_INDEX.md`, `docs/START_HERE.md`).

## v110 (2026-02-23)

- Added `docs/204-well-known-election-stack-discovery.md` (Track A): a domain-first `/.well-known` bootstrap surface that points to the latest comms discovery anchors (directory/feed digests) and is designed to be bounded + hard to bury.
- Added a new evidence object schema: `schemas/WellKnownElectionStackDiscovery.json`.
- Registered new envelope kind `hfv.public.well_known_discovery` in `artifacts/registries/envelope-kinds.csv` (experimental, additive).
- Declared required attachments for `hfv.public.well_known_discovery` (receipt + gossip) in `artifacts/registries/envelope-attachment-requirements.csv` (anti selective disclosure of bootstrap pointers).
- Added an operator drafting template: `artifacts/templates/well-known-election-stack-discovery-payload.json`.
- Extended `OfficialChannelDirectory` to optionally include `discovery.well_known_url` (schema + template) and cross-linked the well-known bootstrap into the comms spine (`docs/195`, `docs/200`, `docs/203`).
- Added an external reference entry for `.well-known` URIs (RFC 8615) to the sources lockfile (`evidence/lock/external-sources.toml`) and refreshed indexes/bundles/catalogs (`docs/13`, `docs/START_HERE.md`, `docs/track-a/*`, `ARCHIVE_INDEX.md`, generated `docs/EVIDENCE_OBJECT_CATALOG.md` + `docs/PUBLIC_SURFACES.md`).

## v109 (2026-02-23)

- Added `docs/203-official-channel-directory-as-evidence.md` (Track A): a tight, publishable directory of declared official channels for a jurisdiction/election — the comms discovery anchor that other surfaces can cite by digest.
- Added a new evidence object schema: `schemas/OfficialChannelDirectory.json`.
- Registered new envelope kind `hfv.public.official_channel_directory` in `artifacts/registries/envelope-kinds.csv` (core, additive).
- Declared required attachments for `hfv.public.official_channel_directory` (receipt + gossip) in `artifacts/registries/envelope-attachment-requirements.csv` (anti selective disclosure of discovery surfaces).
- Added an operator drafting template: `artifacts/templates/official-channel-directory-payload.json`.
- Cross-linked the directory into Track A navigation and refreshed indexes/glossary (`docs/track-a/README.md`, `artifacts/bundles/track-a.toml`, `docs/13-artifact-index.md`, `docs/START_HERE.md`, `docs/196-core-glossary-and-terms-of-art.md`, `ARCHIVE_INDEX.md`, `docs/20-artifacts-checklists-and-templates.md`).

## v108 (2026-02-23)

- Added `docs/202-public-surface-challenges-and-escalating-split-views.md` (Track A): ties PublicNotice feeds (`docs/200`) and parity snapshots (`docs/201`) into the existing public-inspection challenge flow so independent monitors can be asked (auditable) to check the same surfaces and publish comparable evidence.
- Added a drafting template for endpoint parity challenges: `artifacts/templates/public-inspection-challenge-endpoint-parity.json` (uses `schemas/PublicInspectionChallenge.json`, no new protocol surface).
- Updated the audience parity monitoring checklist to include issuing inspection challenges on suspected/disputed mismatches (`artifacts/checklists/audience-parity-monitoring-checklist.md`).
- Refreshed the artifacts/templates index (`docs/20-artifacts-checklists-and-templates.md`) and cross-linked challenge guidance from the comms spine (`docs/200`, `docs/201`).
- Updated Track A bundle + indexes (`artifacts/bundles/track-a.toml`, `docs/track-a/README.md`, `docs/13-artifact-index.md`, `docs/START_HERE.md`, `ARCHIVE_INDEX.md`).

## v107 (2026-02-23)

- Added `docs/201-public-surface-parity-snapshots.md` (Track A): a bounded, publishable snapshot object for proving split-view / parity failures across official channels (especially for the “latest PublicNotice feed” surface).
- Added a new evidence object schema: `schemas/PublicSurfaceParitySnapshot.json`.
- Registered new envelope kind `hfv.public.surface_parity_snapshot` in `artifacts/registries/envelope-kinds.csv` (experimental, additive).
- Declared required attachments for `hfv.public.surface_parity_snapshot` (receipt + gossip) in `artifacts/registries/envelope-attachment-requirements.csv` (anti selective disclosure of parity evidence).
- Added an operator drafting template: `artifacts/templates/public-surface-parity-snapshot-payload.json`.
- Added an operator digest-card tool: `tools/public_surface_parity_snapshot_card.py`, and wired dispatch via `tools/evidence_object_card.py`.
- Cross-linked parity snapshot guidance into comms surfaces (`docs/186`, `docs/195`, `docs/200`) and updated indexes/bundles (`docs/13`, `docs/START_HERE.md`, `docs/track-a/README.md`, `artifacts/bundles/track-a.toml`).

## v106 (2026-02-23)

- Added `docs/200-publicnotice-feeds-and-mirror-index.md` (Track A): a bounded, rollback-detectable discovery/index surface for `PublicNotice` statements (anti split-view comms).
- Added a new evidence object schema: `schemas/PublicNoticeFeed.json`.
- Registered new envelope kind `hfv.public.notice_feed` in `artifacts/registries/envelope-kinds.csv` (core, additive).
- Declared required attachments for `hfv.public.notice_feed` (receipt + gossip) in `artifacts/registries/envelope-attachment-requirements.csv` (anti selective disclosure).
- Added an operator drafting template: `artifacts/templates/public-notice-feed-payload.json`.
- Added an operator digest-card tool: `tools/public_notice_feed_card.py`, and wired dispatch via `tools/evidence_object_card.py`.
- Cross-linked feed guidance into comms surfaces (`docs/186`, `docs/195`, `docs/198`, `docs/179`) and updated indexes/bundles (`docs/13`, `docs/START_HERE.md`, `docs/track-a/README.md`, `artifacts/bundles/track-a.toml`).

## v105 (2026-02-23)

- Added `docs/199-official-surface-security-snapshots.md` (Track A): a tight pattern for publishing content-addressed snapshots of official domain/email anti-spoofing posture so comms hardening is auditable.
- Added a new evidence object schema: `schemas/OfficialSurfaceSecuritySnapshot.json`.
- Registered new envelope kind `hfv.public.surface_security_snapshot` in `artifacts/registries/envelope-kinds.csv` (experimental, additive).
- Added an operator drafting template: `artifacts/templates/official-surface-security-snapshot-payload.json`.
- Updated comms guidance to reference snapshots where helpful: `docs/194`, `docs/195`, `docs/196`, `docs/START_HERE.md`, `docs/track-a/README.md`, `README.md`, `ARCHIVE_INDEX.md`, `docs/13-artifact-index.md`.
- Tightened the official comms channel hardening checklist to cite pinned RFC sources for SPF/DKIM/DMARC and to recommend publishing snapshots (`artifacts/checklists/official-communications-channels-hardening-checklist.md`).

## v104 (2026-02-23)

- Added `docs/198-precinct-closeout-index-and-omission-detection.md` (Track A): closeout index + chaining pattern to make missing precinct packets provable (anti selective omission).
- Added a new evidence object schema for closeout indexes: `schemas/PrecinctCloseoutIndex.json`.
- Registered a new envelope kind for the closeout index: `hfv.results.closeout_index` in `artifacts/registries/envelope-kinds.csv`.
- Added an operator drafting template: `artifacts/templates/precinct-closeout-index-payload.json`.
- Cross-linked the closeout index lane from `docs/195`, `docs/197`, `docs/196`, `docs/track-a/README.md`, `docs/START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/13-artifact-index.md`.
- Updated the Track A curated bundle (`artifacts/bundles/track-a.toml` → regenerated `docs/track-a/BUNDLE.md`).

## v103 (2026-02-23)

- Added `docs/197-precinct-closeout-evidence-capture-and-publication.md` (Track A): minimal pattern for poll-tape/seal snapshots packaged as micro-packets and bound to `PublicNotice` digests.
- Added `artifacts/checklists/precinct-closeout-evidence-capture-checklist.md` (Track A ops): operator checklist for closeout capture → packet → publish → parity.
- Cross-linked the closeout micro-packet lane from `docs/63`, `docs/177`, `docs/186`, `docs/195`, `docs/196`, `docs/START_HERE.md`, and `docs/13-artifact-index.md`.
- Refactored `docs/09-audit-recovery.md` to cite lockfile IDs instead of embedding fragile external URLs (`docs/161` guidance).
- Updated the Track A curated bundle (`artifacts/bundles/track-a.toml` → regenerated `docs/track-a/BUNDLE.md`).

## v102 (2026-02-23)

- Added `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md` (Track A): minimal pattern for rumor-control and incident status surfaces bound to `PublicNotice` digests.
- Added `docs/196-core-glossary-and-terms-of-art.md` (Shared): compact glossary for recurring terms.
- Cross-linked the new comms surface guidance from `docs/186`, `docs/193`, `docs/194`, `docs/START_HERE.md`, and `ARCHIVE_INDEX.md`.
- Updated the Track A curated bundle (`artifacts/bundles/track-a.toml` → regenerated `docs/track-a/BUNDLE.md`).

## v101 (2026-02-23)

- Added `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md` (Track A): a tight, deployable minimum control set for AI-era forged statements—bind public claims to digests, require parity monitoring, and treat media-provenance signals as advisory.
- Cross-linked comms authenticity guidance from `docs/37` and `docs/186`.
- Added `docs/194` to the Track A curated bundle (`artifacts/bundles/track-a.toml` → regenerated `docs/track-a/BUNDLE.md`).

## v100 (2026-02-22)

- Added `tools/public_surface_pins.py` (stdlib-only) to print copy/pasteable sha256 pins for stable registry bytes used as optional comparability pins in publishable verifier outputs.
- Hardened operator “card” UX: `tools/verifier_report_card.py` and `tools/packet_verification_report_card.py` now emit bounded warnings when a report’s declared registry pins do not match the local canonical bytes.
- Added a release-gate drift firewall for verifier-report examples: `scripts/check_example_report_pins.py` enforces that any `_sha256` pins match canonical registry bytes and that PacketVerificationReport examples use the current archive VERSION.
- Extended the operator-tools smoke test to cover `tools/public_surface_pins.py` JSON output.

## v99 (2026-02-22)

- Added optional comparability pins to implementation-scoped verifier identity reports: `VerifierReport` now supports `verifier_problem_codes_sha256` and `envelope_kinds_sha256` (schema: `schemas/VerifierReport.json`; template updated).
- Updated the publishable verifier-report card helper to print these pins when present (`tools/verifier_report_card.py`), and updated `docs/193` guidance accordingly.

## v98 (2026-02-22)

- Added optional comparability pins to publishable packet-scoped verifier output: `PacketVerificationReport` now supports `verifier_problem_codes_sha256` and `envelope_kinds_sha256` (schema: `schemas/PacketVerificationReport.json`).
- Updated the reference verifier tool to populate those digests from canonical registry bytes when available (`tools/observer_verify_packet.py`), and bumped `report_version` to 1.1.0.
- Updated operator-facing output: `tools/packet_verification_report_card.py` now prints codebook + kind-registry digests when present; `docs/193` and the schema-validation template were refreshed accordingly.

## v97 (2026-02-22)

- Strengthened the “public surfaces” index by adding per-surface sha256 digests (short + full) and listing `schemas/VerifierReport.json` explicitly (`scripts/gen_public_surface_index.py` → `docs/PUBLIC_SURFACES.md`).
- Added a small publishability/comparability note to `docs/193`: when publishing verifier outputs, optionally cite the sha256 of `artifacts/registries/verifier-problem-codes.csv` so readers can confirm the exact codebook used.

## v96 (2026-02-22)

- Hardened detached-payload and attachment reads against **symlink escapes**: `tools/path_safety.safe_join(..., must_exist=True)` now enforces resolved-path containment, and packet readers anchor lookups at the packet root (`tools/packet_common.py`, `tools/observer_verify_packet.py`).
- Added a conservative release-gate check that forbids symlinks anywhere in the archive: `scripts/check_no_symlinks.py` (wired into `scripts/release_gate.py`; documented in `docs/162`).
- Added a compact “public surfaces” index (registries + schemas external consumers may depend on): `docs/PUBLIC_SURFACES.md` (generated by `scripts/gen_public_surface_index.py`; wired into `scripts/release_gate.py` and linked from `docs/START_HERE.md`).
- Extended the operator-tools smoke test with an explicit symlink-escape regression case (`scripts/check_operator_tools_smoke.py`).

## v95 (2026-02-22)

- Hardened safe-relative-path validation against percent-encoded traversal and control/whitespace tricks: `tools/path_safety.py` now rejects percent-escapes and control chars + leading/trailing whitespace.
- Reduced drift by reusing the shared path-safety rules in the example-packet path scanner: `scripts/check_packet_paths.py` now imports `tools/path_safety.py`.
- Extended the operator-tools smoke test with percent-encoded traversal cases to prevent regressions (`scripts/check_operator_tools_smoke.py`).

## v94 (2026-02-22)

- Hardened operator tooling against path traversal: `tools/packet_common.py` now resolves detached payloads via `path_safety.safe_join` and rejects unsafe `payload_pointer.uri` values (enforces the safe-path rule in `docs/176`).
- Extended the operator-tools release-gate smoke test with an explicit unsafe-URI regression check (`scripts/check_operator_tools_smoke.py`).

## v93 (2026-02-22)

- Added a shared packet-reading helper module to reduce operator-tool drift: `tools/packet_common.py` (centralizes detached-payload lookup + payload_digest recomputation per `docs/176`).
- Refactored the three operator “card” tools to use the shared helper; PublicNotice digest recomputation now respects envelope canonicalization/media_type rules for detached payloads.
- Added a one-command card renderer that auto-detects kind and dispatches to the right specialized card tool when available: `tools/evidence_object_card.py`.
- Extended the operator-tools release-gate smoke test to cover the new dispatcher tool: `scripts/check_operator_tools_smoke.py`.

## v92 (2026-02-22)

- Added a stdlib-only “packet verification card” helper for publishing/verifying packet-scoped verifier outputs: `tools/packet_verification_report_card.py` (recomputes payload_digest + tbs_digest per `docs/176` and prints a bounded, copy/pasteable summary).
- Added a release-gate smoke test for operator-facing helper tools to prevent UI rot: `scripts/check_operator_tools_smoke.py` (wired into `scripts/release_gate.py`; documented in `docs/162`).
- Added a maintainer helper for pinning external source hashes when network fetch is blocked: `scripts/pin_source_sha256_from_file.py` (documented in `docs/191`).
- Updated `docs/193` and `tools/README.md` to point at the new packet-report card tool.


## v91 (2026-02-22)

- Added a stdlib-only “verifier card” helper for publishing/verifying implementation-scoped verifier reports: `tools/verifier_report_card.py` (recomputes payload_digest + tbs_digest per `docs/176` and prints a copy/pasteable summary).
- Threaded the helper into the publishable verifier-report guidance and offline walkthrough (`docs/193`, `docs/177`) and listed it in the operator-facing tools index (`tools/README.md`).


## v90 (2026-02-22)

- Fixed a publishability bug: `tools/observer_verify_packet.py` now actually emits `PacketVerificationReport.verifier_report_tbs_digest` when the linkage is provided via `--verifier-report-envelope` / `--verifier-report-tbs-digest`.
- Added a release-gate drift firewall to prevent regressions: `scripts/check_packet_verification_report_linkage.py` (wired into `scripts/release_gate.py`; documented in `docs/162`).
- Added a minimal example packet for publishing an implementation-scoped verifier identity report as evidence: `artifacts/examples/evidence_packet_verifier_report_minimal/` (linked from `docs/193`).


## v89 (2026-02-22)

- Added an optional linkage field to `PacketVerificationReport` so packet-scoped results can point to an implementation-scoped verifier identity report: `verifier_report_tbs_digest` (schema: `schemas/PacketVerificationReport.json`).
- Extended `tools/observer_verify_packet.py` with `--verifier-report-envelope` / `--verifier-report-tbs-digest` to populate the linkage field (without changing the packet verification semantics); updated `docs/193` and `tools/README.md`.
- Updated the packet-report schema validation template to include the new linkage field and current version markers (`artifacts/templates/packet-verification-report-example.json`).


## v88 (2026-02-22)

- Registered the previously-described implementation-scoped verifier report as a first-class evidence kind: added `hfv.verifier.report` → `schemas/VerifierReport.json` to `artifacts/registries/envelope-kinds.csv` (unblocks consistent publication + verifier onboarding).
- Added a schema-valid ship template for implementation reports and wired it into example validation: `artifacts/templates/verifier-report-payload.json` + `scripts/validate_schemas.py`.
- Added a documentation drift firewall for envelope-kind references (`kind:` / `Envelope kind:`) and wired it into the one-command release gate: `scripts/check_doc_envelope_kind_references.py`, `scripts/release_gate.py` (updated `docs/162`, `docs/179`, `docs/188`, `docs/193`, and `docs/START_HERE.md`).

## v87 (2026-02-22)

- Pinned seven RFC sources in the external-sources lockfile (previously unpinned) to harden citation stability: RFC 8659, 4033, 7208, 6376, 7489, 8461, 8460 (`evidence/lock/external-sources.toml`).
- Added operator-friendly problem-code UX to `tools/observer_verify_packet.py`: `--list-codes` (print the full publishable surface) and `--explain <code>` (print severity + one-line summary).
- Updated `docs/193` and `tools/README.md` to point at the new flags.

## v86 (2026-02-22)

- Added a strict drift firewall for the publishable verifier problem-code surface: new `scripts/check_verifier_problem_codes_registry.py` (enforces exact columns, formatting, required sentinel, and sorted order) and wired it into `scripts/release_gate.py`.
- Hardened `tools/observer_verify_packet.py` against accidental code drift in non-public mode: if any unknown codes appear, it now emits stable `unknown_problem_code:<code>` sentinel(s) in addition to the original problem strings.
- Refactored the release-gate documentation to reduce future drift: `docs/162` now treats `scripts/release_gate.py` as authoritative, adds the missing required checks, and removes the long hand-copied command list.

## v85 (2026-02-22)

- Promoted publishable verifier reason-codes to a first-class registry: added `artifacts/registries/verifier-problem-codes.csv` and refactored `tools/verifier_problem_codes.py` to load from it (regenerated `docs/VERIFIER_PROBLEM_CODES.md`; updated `docs/193`).
- Extended `tools/observer_verify_packet.py` with `--emit-evidence-object <out_dir>` to generate a **minimal verifier-report packet** (EvidenceEnvelope + detached payload + manifest) for publication; added `--issuer-id` and documented the flow in `docs/193`.
- Updated the tools status index to reflect the new publishable-report ergonomics (`tools/README.md`).

## v84 (2026-02-22)

- Fixed the canonical packet-layout snippet to match reference tools (`docs/173` now includes `envelopes/` and clarifies that canonical bytes live under `objects/`).
- Hardened publishable verifier output: added `unknown_problem_code` and made `tools/observer_verify_packet.py --public` suppress unrecognized codes so published reports stay comparable (`tools/verifier_problem_codes.py`, `docs/193`, regenerated `docs/VERIFIER_PROBLEM_CODES.md`).
- Added a minimal example packet publishing a `PacketVerificationReport` as evidence (`artifacts/examples/evidence_packet_packet_verification_report_minimal/`) and updated the offline walkthrough to point to the publishable report surface (`docs/177`).
- Tightened `PacketVerificationReport` schema with simple pattern constraints for `packet_dir` and `problems[]`.

## v83 (2026-02-22)

- Added publishable verifier-report guidance and privacy hardening: new `docs/193-publishable-verifier-reports.md` plus generated `docs/VERIFIER_PROBLEM_CODES.md` (from `tools/verifier_problem_codes.py`).
- Upgraded `tools/observer_verify_packet.py` with `--public` mode (sanitize packet_dir + emit codes-only problems; status can be PASS_WITH_WARNINGS when only WARN codes occur).
- Added a schema-valid PacketVerificationReport example template and wired it into schema/example validation (`artifacts/templates/packet-verification-report-example.json`, `scripts/validate_schemas.py`).

## v82 (2026-02-22)

- Clarified the verifier output split: `VerifierReport` (implementation identity + conformance) vs a **packet-scoped** `PacketVerificationReport` intended for publishable bundle integrity results (docs/42, docs/30, docs/43, docs/188; new schema `schemas/PacketVerificationReport.json`).
- Extended the envelope kind registry with `hfv.verifier.packet_verification_report` and threaded it into the minimal verifier API surface (`docs/179`).
- Upgraded `tools/observer_verify_packet.py` into a tighter offline drift firewall: it now checks kind/track/schema registry alignment, required attachment rels, envelope-version major compatibility, and can emit a JSON `PacketVerificationReport` (`--json`, `--out`).

## v81 (2026-02-22)

- Added a generated Evidence Object Catalog (`docs/EVIDENCE_OBJECT_CATALOG.md`) plus generator script and release-gate wiring (`scripts/gen_evidence_object_catalog.py`, `scripts/release_gate.py`, `docs/160`, `docs/162`). This compresses verifier onboarding: kind → schema → required attachments → example packet.
- Clarified semver compatibility rules for `EvidenceEnvelope.envelope_version` (minor/patch vs major breaking changes) in `docs/173`, and linked from the maintainer change protocol (`docs/150`).
- Added cross-links in verifier entrypoints (`README.md`, `docs/START_HERE.md`, `docs/179`, `docs/13`).
- Added two research prompts on comms-SLA breach artifacts and public digest UX (`docs/172`) and pointed `docs/186` at the digest-card helper (`tools/public_notice_card.py`).

## v80 (2026-02-22)

- Added a structured PublicNotice update commitment field: optional `next_update_at` (RFC3339) in the PublicNotice schema + templates, enabling monitors to check update promises without parsing prose (`schemas/PublicNotice.json`, template updates).
- Added a dedicated follow-up status-update drafting template that uses `supersedes_notice_id` to chain notices (`artifacts/templates/public-notice-status-update-payload.json`), and updated the rumor-response playbook + comms-as-evidence doc to reference it (`artifacts/playbooks/public-notice-and-rumor-response.md`, `docs/186`).
- Upgraded drift firewalls: `scripts/validate_schemas.py` now validates all PublicNotice ship templates (including rumor-control + status-update) and performs a lightweight ordering sanity check (`next_update_at` must not precede `issued_at`).
- Improved the operator digest-card helper to display `supersedes_notice_id` and `next_update_at` (and warn on implausible timestamps), keeping “what we promised” visible on comms surfaces (`tools/public_notice_card.py`).
- Added a drill scenario for **missed next update commitment** (treat as a comms SLA breach; publish a status_update that acknowledges delay and resets `next_update_at`) (`artifacts/registries/drill-scenarios.csv`).

## v79 (2026-02-22)

- Added a schema-valid **rumor-control PublicNotice** drafting template and wired it into schema/example validation (`artifacts/templates/public-notice-rumor-control-payload.json`, updates to `scripts/validate_schemas.py`; referenced from `docs/186` and the rumor-response playbook).
- Added an optional DNS hardening baseline reference for **DNSSEC** and cited it from disinformation/comms guidance (`source: rfc4033_txt`; updates to `evidence/lock/external-sources.toml`, `docs/37`, `docs/161`).
- Added a drill scenario for **digest mismatch across official comms channels** (treat as split-view/compromise and respond with a new PublicNotice) (`artifacts/registries/drill-scenarios.csv`).
- Added a compact tools status index (operator-facing helpers vs prototype vs skeletons) to reduce misreadings during incidents (`tools/README.md`; linked from `docs/START_HERE.md`).

## v78 (2026-02-22)

- Hardened **PublicNotice correction semantics**: JSON Schema now enforces that `notice_type=="correction"` requires `correction_of_notice_id`, and that `correction_of_notice_id` implies `notice_type=="correction"` (`schemas/PublicNotice.json`).
- Added a compact correction drafting template: `artifacts/templates/public-notice-correction-payload.json` (validated in `scripts/validate_schemas.py`).
- Extended the PublicNotice example packet to include a linked correction notice (still toy/unsigned), demonstrating explicit correction linkage (`artifacts/examples/evidence_packet_public_notice/`).
- Upgraded `tools/public_notice_card.py` to print correction linkage and best-effort channel URL resolution from `official-channels.csv`, with warnings for semantic mismatches.

## v77 (2026-02-22)

- Added a cite-only DNS CAA baseline reference and threaded CT/CAA hardening into disinformation-resilience guidance and the official comms channel hardening checklist (`source: rfc8659_txt`, `source: rfc9162_txt`; updates to `docs/37` and `artifacts/checklists/official-communications-channels-hardening-checklist.md`).
- Refactored the envelope digest vector tripwire to allow `payload_path` (vectors can reference existing JSON artifacts instead of duplicating payload bytes) and added a vector binding the canonical PublicNotice payload template (`scripts/check_envelope_vectors.py`, `artifacts/test-vectors/envelope_vectors.json`, `docs/190`).
- Updated the authoritative sources citation map to include DNS CAA as part of the comms hardening baseline (`docs/161`).

## v76 (2026-02-22)

- Added an operator-facing hardening checklist for official communications channels (bounded, registry-first) and referenced it from comms-as-evidence and disinformation-resilience docs (`artifacts/checklists/official-communications-channels-hardening-checklist.md`, updates to `docs/186` and `docs/37`).
- Added cite-only baseline references for SPF/DKIM/DMARC and MTA-STS/TLS reporting (RFCs) and cited them from disinformation-resilience guidance (new lockfile entries; citations in `docs/37`).
- Improved the PublicNotice digest-card helper to warn when `payload.channels` contains unknown channel IDs (catches registry drift during drills/incidents) (`tools/public_notice_card.py`).
- Normalized indentation in the official-channels registry drift firewall for readability (no behavior change) (`scripts/check_official_channels_registry.py`).

## v75 (2026-02-22)

- Recorded the comms-as-evidence decision as ADR 0002 and added an ADR drift firewall (every ADR must be indexed and include Status/Date) wired into the release gate (`adr/0002-public-communications-as-evidence-via-publicnotice.md`, `adr/INDEX.md`, `scripts/check_adr_index.py`, `scripts/release_gate.py`, `docs/162`).
- Refactored the incident communications template into a PublicNotice-mapped drafting worksheet and updated comms playbooks/docs to reference the canonical PublicNotice payload template + channel registry (`artifacts/templates/incident-communications.md`, `artifacts/templates/public-notice-payload.json`, `docs/87`, `docs/20`, `artifacts/playbooks/coercion-response-playbook.md`).

## v74 (2026-02-22)

- Added a tiny shared CSV-registry helper to reduce copy/paste drift across release-gate scripts, and refactored the registry drift firewalls to use it (`scripts/_shared/registry.py`, updated `scripts/check_drill_scenarios.py`, `scripts/check_known_issues_registry.py`, `scripts/check_official_channels_registry.py`).
- Added a short registry index to keep future additions bounded and discoverable (`artifacts/registries/README.md`).
- Strengthened `scripts/validate_schemas.py` with a stdlib-only cross-registry check: `PublicNotice.channels` values in the ship template and example packets must be known `channel_id`s from `artifacts/registries/official-channels.csv`.
- Documented registry location/index in the release-gate doc (`docs/162`).

## v73 (2026-02-22)

- Added a canonical **official comms channels** registry (bounded list of “where to look” for official updates) and wired it into Track A drift firewalls (`artifacts/registries/official-channels.csv`, `scripts/check_official_channels_registry.py`, `scripts/release_gate.py`, `docs/162`).
- Tightened the comms-as-evidence surface so `PublicNotice.channels` can be unambiguous: template uses registry channel IDs and the schema guidance points to the registry (`artifacts/templates/public-notice-payload.json`, `schemas/PublicNotice.json`).
- Improved offline verification ergonomics for rumor-control parity checks: `public_notice_card.py` now prints the declared channels (when present) alongside the digest card (`tools/public_notice_card.py`, `docs/177`).
- Added baseline, election-relevant references for hardening official comms channels (cite-only; no bundling) and referenced them from the comms spec (`evidence/lock/external-sources.toml`, `docs/186`, `docs/45`, `docs/161`).

## v72 (2026-02-22)

- Upgraded `scripts/validate_schemas.py` from parse-only to a drift firewall: when `jsonschema` is available it meta-validates all schemas and validates a small set of "ship" examples (templates + example envelopes), with format checking enabled; falls back to parse-only mode if the library is unavailable.
- Added a new comms authenticity drill scenario for domain hijack / certificate mis-issuance leading to fake notices (`artifacts/registries/drill-scenarios.csv`).
- Tightened the AI-era rumor-dynamics research backlog with an explicit question about hardening official comms channels while keeping verification cheap (`docs/172`).
- Made the COI disclosure JSON template format-valid under strict format checking (`artifacts/templates/coi-disclosure-template.json`).

## v71 (2026-02-22)

- Added a minimal, schema-valid `PublicNotice` payload starter template for operators and integrators (`artifacts/templates/public-notice-payload.json`) and wired it into the comms-as-evidence doc + rumor-response playbook (`docs/186`, `artifacts/playbooks/public-notice-and-rumor-response.md`).
- Added a stdlib-only helper to print a human-friendly PublicNotice “digest card” (recomputes payload + TBS digests per docs/176; no signature verification) to support copy/pasteable rumor-control parity checks (`tools/public_notice_card.py`); documented in the offline verification walkthrough (`docs/177`).

## v70 (2026-02-22)

- Refactored the exercise scenario library doc to be a thin index over the canonical drill-scenario registry (avoids scenario drift across prose) and added ops-reality scenarios (DDoS/selective drop, ballot definition substitution, VRDB rollback, ENR drift/injection, credential recovery wave) to the registry (`docs/90`, `artifacts/registries/drill-scenarios.csv`).
- Added a minimal "known issues" registry format plus a drift firewall (status enum + file refs) to support patch/mitigation transparency as part of comms-as-evidence (`artifacts/registries/known-issues.csv`, `scripts/check_known_issues_registry.py`, `docs/37`, `docs/87`, `docs/162`, `scripts/release_gate.py`).
- Added an informative CISA "Rumor vs. Reality" (rumorcontrol) source pin and cited it in disinformation/comms-as-evidence docs (`evidence/lock/external-sources.toml`, `docs/37`, `docs/186`, `docs/161`).

## v69 (2026-02-22)

- Canonicalized PublicNotice correction linkage to `correction_of_notice_id` (kept `correction_of` as a deprecated alias) and updated comms specs/playbooks accordingly (`schemas/PublicNotice.json`, `docs/186`, `artifacts/playbooks/public-notice-and-rumor-response.md`).
- Extended the drill scenario registry with channel-takeover and synthetic-media rumor-control drills (`artifacts/registries/drill-scenarios.csv`).
- Added an informative C2PA Content Credentials specification reference to the external source lockfile and cited it in disinformation/AI-era rumor-control docs (`evidence/lock/external-sources.toml`, `docs/37`, `docs/172`, `docs/161`).

## v68 (2026-02-22)

- Added a canonical drill scenario registry (`artifacts/registries/drill-scenarios.csv`) and a drift firewall (`scripts/check_drill_scenarios.py`), wired into the Track A release gate (docs/162, scripts/release_gate.py).
- Refactored incident-response comms to a single canonical evidence surface: `hfv.public.notice` (PublicNotice). Updated core docs + ops playbooks/checklists and marked `schemas/IncidentCommsPackage.json` as legacy.
- Expanded pinned comms references with EAC/CISA public communications guidance and the EAC AI toolkit (lockfile + citation map), and cited them in the AI-era rumor-control backlog (docs/172) and comms specs (docs/87, docs/186).

## v67 (2026-02-22)

- Added a canonical ADR decision registry (`adr/INDEX.md`) and wired it into maintainer and freeze-plan navigation (`docs/START_HERE.md`, `docs/153`, `ARCHIVE_INDEX.md`).
- Tightened the claims/hazards spine for narrative attacks: added claim-matrix rows and a hazard entry for forged media / fake “official” statements, and updated playbooks + resilience docs to reference `PublicNotice` as an evidence artifact (`docs/27`, `docs/37`, `docs/186`).
- Added LLM maintainer guardrails to reinforce anti-bloat + anti-hallucination discipline (`docs/183`) and extended the requirements traceability starter with comms-as-evidence requirements (`docs/25`).

## v66 (2026-02-22)

- Aligned front-matter naming with **The Election Stack** (HFV as historical alias) and added role-based reading paths in `docs/START_HERE.md` for maintainers, verifiers, operators, and researchers.
- Tightened long-horizon stewardship guidance with explicit compression patterns to prevent archive bloat (`docs/183`).
- Expanded the open research backlog with AI-era synthetic-media / forged-artifact questions and updated disinformation + incident-communications docs to reference the new surface (`docs/172`, `docs/37`, `docs/186`).
- Added authoritative sources for AI risk framing and disinformation tactics to the external sources lockfile + citation map (`evidence/lock/external-sources.toml`, `docs/161`).

## v65 (2026-02-22)

- Refactored `schemas/TimeBeacon.json` to remove redundant embedded signatures and to capture time-source + uncertainty + optional proof digests (envelope signatures remain the authenticity mechanism); refreshed the minimal `hfv.time.beacon` example packet to match.
- Hardened envelope-kind schema hygiene with a new drift firewall: `scripts/check_envelope_payload_schemas.py` (wired into the release gate) and tightened `schemas/VerifierProvenance.json` to meet the required conventions.

## v64 (2026-02-22)

- Updated the Roughtime external-source pin to the current NTP WG draft (draft-ietf-ntp-roughtime-17) and refreshed citations in the secure-time docs (docs/31, docs/38, docs/192).
- Added a minimal `hfv.time.beacon` example evidence packet (`artifacts/examples/evidence_packet_time_beacon_minimal`) to keep the new kind exercised by the shipped verifier tooling.
- Added `scripts/check_attachment_registry_integrity.py` and wired it into the release gate to ensure attachment-requirements rows reference registered kinds and existing schemas (no duplicate kind+rel rows); documented in `docs/162`.
## v63 (2026-02-22)

- Added a tight, evidence-focused time-attestation + timestamping guide (docs/192) and updated time-ordering docs (docs/31, docs/38) to cite authoritative time protocol and log-management sources (RFC5905/8915/3161, Roughtime draft, NIST SP 800-92r1).
- Added `hfv.time.beacon` to the envelope kind registry (payload schema `schemas/TimeBeacon.json`) to stabilize signed time-beacon evidence semantics.
- Expanded `evidence/lock/external-sources.toml` with pinned time-protocol references (and one best-effort unpinned operational guidance source where access is restricted).

## v62 (2026-02-22)

- Replaced raw external URLs in core ops and assurance docs (`docs/08`, `docs/10`) with `source:` citations, and added a minimal authoritative source list to `docs/17`.
- Expanded `evidence/lock/external-sources.toml` with pinned (citation-first) references for NIST voting security recommendations, SSDF (SP 800-218 + r1 IPD), C-SCRM (SP 800-161r1), TUF, and the in-toto pipeline-integrity paper.
- Added `scripts/build_release_zip.py` to generate deterministic release ZIPs (stable ordering + timestamps) and documented it in `docs/162`.

## v61 (2026-02-22)

- Added pinned NIST CSF 2.0 (CSWP 29) and NIST SP 800-61r3 (incident response; CSF 2.0 profile) to the external source lockfile, and cited them in incident response / comms docs (docs/87, docs/134, docs/186, docs/161).
- Added a lockfile lean-ness drift firewall: `scripts/check_unused_sources.py` (wired into `scripts/release_gate.py` and documented in docs/162).
- Updated docs/191 to reflect the new unused-source enforcement.

## v60 (2026-02-22)

- Strengthened the shipped-example drift firewall: `scripts/check_object_uri_alignment.py` now verifies object *bytes* match declared sha256 digests and rejects orphan objects in `objects/` (prevents silent bloat + broken examples).
- Extended external-source verification to support an optional `local_filename` field (for basename collisions / unstable URL basenames), and documented it in `docs/191`.
- Fixed a typo in `docs/162` (the docs ≥170 raw-URL rule) and updated the `check_object_uri_alignment` description to match the stronger integrity check.
- Added an IETF SCITT “verifiable refusal events” draft to the external source lockfile and cited it in `docs/167` as a worked example of verifiable refusal/non-claim event structure.

## v59 (2026-02-22)

- Ensured all external-source lockfile entries are exercised by docs (added missing `source:` citations in `docs/19`, `docs/21`, and `docs/186`; and added the EAC E2E evaluation process page to the lockfile).
- Added `scripts/report_source_usage.py` (and referenced it in `docs/191`) to help maintainers keep the lockfile lean by showing citation locations and unused IDs.
- Tightened `scripts/check_external_sources_lockfile.py` to enforce snake_case source IDs.

## v58 (2026-02-22)

- Added `docs/191` + a small helper (`scripts/fetch_source_sha256.py`) to make external-source pinning repeatable without bundling large artifacts.
- Added a drift firewall for newer evidence docs: `scripts/check_no_raw_urls_modern_docs.py` (wired into `scripts/release_gate.py` + documented in `docs/162`) enforces that docs ≥170 cite via `source: <id>` rather than embedding raw external URLs.
- Expanded the external sources lockfile with incident-reporting and RLA references (CISA guidance + RLA/CSD papers), and updated evidence-facing docs (`docs/179`, `docs/184–186`) to cite lockfile IDs.

## v57 (2026-02-22)

- Added `scripts/check_external_sources_lockfile.py` to enforce lockfile hygiene and to ensure every `source: <id>` citation resolves to `evidence/lock/external-sources.toml` (drift firewall; prevents stale/typo citations).
- Added pinned entries for RFC 8785 (JCS) and RFC 9421 (HTTP Message Signatures); updated docs to cite lockfile IDs and removed duplicate unused SCITT alias entries from the lockfile.
- Tightened EvidenceEnvelope verifier robustness: `tools/envelope_common.py` now applies RFC8785-JCS canonicalization even when `payload_pointer.media_type` is omitted, and `tools/observer_verify_packet.py` surfaces explicit diagnostics for non-JSON media types and JSON parse failures (docs/176 clarified to match).

## v56 (2026-02-22)

- Added a drift firewall for example packet object naming: `scripts/check_object_uri_alignment.py` enforces that detached payload/attachment URIs under `objects/` are content-addressed (`sha256-<hex>.*`) and that filenames match declared digests.
- Wired the new check into `scripts/release_gate.py` and updated `docs/162` + `docs/176` to document the convention.

## v55 (2026-02-22)

- Hardened offline packet verification against path traversal: `tools/observer_verify_packet.py` now rejects unsafe `payload_pointer.uri`, attachment `uri`, and `manifest.json` `artifacts[].url` values.
- Added a drift firewall for shipped examples: `scripts/check_packet_paths.py` (wired into `scripts/release_gate.py`).
- Clarified safe-path requirements for detached payloads in `docs/176` and updated the release checklist in `docs/162`.
- Removed accidental Python cache artifacts from the packaged tree, and hardened `scripts/release_gate.py` to run with `PYTHONDONTWRITEBYTECODE=1` so the gate does not create `__pycache__` during checks.

## v54 (2026-02-22)

- Centralized EvidenceEnvelope digest rules in `tools/envelope_common.py` and refactored `tools/envelope_wrap.py` and `tools/observer_verify_packet.py` to share the same implementation (reduces drift risk).
- Added a tiny EvidenceEnvelope interoperability vector set (`artifacts/test-vectors/envelope_vectors.json`) plus a release-gate tripwire (`scripts/check_envelope_vectors.py`).
- Added two maintainability drift firewalls: `scripts/check_version_consistency.py` (VERSION/CHANGELOG/START_HERE agree) and `scripts/check_size_budget.py` (reject accidental archive bloat).
- Added `docs/190` and updated `docs/162`, `docs/176`, and `docs/START_HERE.md` to surface the new tripwires.

## v53 (2026-02-21)

- Fixed RFC8785 / JSON.stringify number serialization edge cases in `tools/jcs.py` (notably `1e20`/`1e21`/`1e30` formatting).
- Added drift tripwires to the release gate:
  - `scripts/check_jcs_vectors.py` (tiny RFC8785 canonicalization vectors)
  - `scripts/check_no_cache_artifacts.py` (reject `__pycache__`, `*.pyc`, and non-empty `evidence/cache`)
- Clarified number formatting boundaries in `docs/176` and updated the release-gate checklist in `docs/162`.

# Changelog

## v52 (2026-02-21)

- Implemented a tighter RFC8785-JCS canonicalizer (`tools/jcs.py`) with JSON.stringify-compatible number formatting (e.g., `1.0` canonicalizes to `1`) and NaN/Infinity rejection.
- Refactored envelope tooling and offline verification to use the shared JCS implementation (`tools/envelope_wrap.py`, `tools/observer_verify_packet.py`, `tools/jcs_canonicalize.py`).
- Refreshed bundled example evidence packets so detached payload bytes and envelope digests match the updated canonicalization (and trimmed unreferenced objects to avoid bloat).
- Upgraded the ENR drift detector example to hash CROs using RFC8785-JCS canonical bytes.

## v51 (2026-02-21)

- Fixed and hardened the offline packet verifier (`tools/observer_verify_packet.py`) so `payload_digest` is recomputed per RFC8785-JCS for JSON payloads (docs/176), and so payload pointers / manifest URLs enforce hash+size integrity.
- Added a drift firewall for example packets: `scripts/check_example_packets.py` verifies every `artifacts/examples/evidence_packet_*` directory stays self-consistent.
- Added a one-command release gate runner: `scripts/release_gate.py` (uses `scripts/build_manifest.py --check` so it works without git).
- Extended `scripts/build_manifest.py` with `--check` mode and updated `docs/162`, `README.md`, and `docs/START_HERE.md` accordingly.

## v50 (2026-02-21)

- Added a secrets drift firewall: `scripts/check_no_private_keys.py` fails the release if private key material (PEM/OpenSSH/P12/PFX) is present anywhere in the repo.
- Added a tight maintainer policy doc for sensitive material: `docs/189-sensitive-material-and-secrets.md`.
- Wired the new check into the required release gate (`docs/162`) and surfaced the policy in `README.md` and `docs/START_HERE.md`.

## v49 (2026-02-21)

- Added a small link-rot drift firewall: `scripts/check_doc_links.py` scans in-repo markdown and fails on broken relative links.
- Added a tombstone-shape drift firewall: `scripts/check_tombstones.py` enforces that tombstone docs stay small, flat, and point to a live canonical target.
- Wired both checks into the required release gate (`docs/162`) and clarified tombstone policy enforcement in `docs/163`.


## v48 (2026-02-21)

- Fixed a broken Track A bundle entry for ENR/public-results security by updating the bundle definition to point at the canonical doc `docs/63-election-night-reporting-and-public-results-security.md`.
- Added a tombstone alias `docs/63-results-api-and-enr-hardening.md` to prevent link-rot for older references.
- Hardened `scripts/gen_track_bundles.py` so curated bundles fail fast if any referenced doc path is missing.
- Added a tight verifier-facing execution path: `docs/188-verifier-minimum-viable-path.md` (packet → policy → report) and surfaced it in entrypoints.
- Improved ObserverKit ergonomics and safety: richer `observer-kit/README.md` + `offline_verifier.py` now checks for unsafe paths, validates optional byte-size fields, and provides clearer signature diagnostics.


## v47 (2026-02-21)

- Removed accidental Python cache artifacts (`__pycache__/`, `*.pyc`) from the archive to avoid bloat and non-deterministic diffs.
- Hardened `scripts/build_manifest.py` to exclude common cache/build directories and bytecode files.
- Reordered and normalized this changelog so the latest release is always at the top.
- Refreshed maintainer navigation docs (`docs/START_HERE.md`, `docs/161`, `docs/167`, `docs/172`) to reflect v46-era additions and to make dual-use boundaries explicit.


## v46 (2026-02-21)

- Added publication compliance coverage: TriggerEvents + PublicationCoverageReport (`docs/187`, new schemas, new tool).
- Extended PublicNotice schema with additional notice types and optional correction/linkage fields.
- Added new envelope kinds and attachment requirements for trigger events and publication coverage reports.
- Added example packet: `artifacts/examples/evidence_packet_publication_compliance_minimal`.
- Updated external source lockfile URL for SCITT receipts draft; added CISA landing page entry (hash pending).


## v45 (2026-02-21)

- Added a registry-backed publication trigger vocabulary (`docs/184`, `artifacts/registries/publication-triggers.csv`) and a drift-firewall script (`scripts/check_publication_triggers.py`).
- Added receipt semantics tiers (`docs/185`) and extended `TransparencyReceipt` schema with optional `semantics_tier` and `mmd_seconds`.
- Added incident communications as evidence (`docs/186`), a new `PublicNotice` payload schema, a new envelope kind `hfv.public.notice`, and a toy example packet (`artifacts/examples/evidence_packet_public_notice`).
- Extended Track bundles to include the new shared docs and comms evidence guidance.
- Updated external sources lockfile with pinned hashes for key references (SCITT drafts, incident comms guide) without bundling PDFs.


## v44 (2026-02-21) — Stewardship constitution + A2→A3 trajectory

- Added archive stewardship + long-horizon plan for LLM maintainers: `docs/183`.
- Embedded the project’s “sacred invariant” and maintenance read-order in `docs/START_HERE.md`.
- Clarified **A2 now → A3 later** trajectory and **spec-first posture** in `docs/166` and track entrypoints.


## v43 (2026-02-21) — Publication contract + receipt profile registry

- Added a **PublicationContract** and **PublicationSuppressionReport** to make evidence publication deadlines explicit and deadline breaches portable: `docs/181`, `schemas/PublicationContract.json`, `schemas/PublicationSuppressionReport.json`.
- Added receipt profile registry + drift firewall (`artifacts/registries/receipt-profiles.csv`, `scripts/check_receipt_profiles.py`) and upgraded `tools/observer_verify_packet.py` to validate receipt profiles and verify attachments.
- Added example packet: `artifacts/examples/evidence_packet_publication_contract/`.
- Added playbook + hazard for deadline breach handling.


## v42 (2026-02-21) — Receipt + gossip attachments

- Standardized receipt and gossip attachments to harden publication against selective disclosure: `docs/180` + new schemas `schemas/TransparencyReceipt.json` and `schemas/GossipSummary.json`.
- Added per-kind attachment requirements registry (`artifacts/registries/envelope-attachment-requirements.csv`) and CI check (`scripts/check_attachment_requirements.py`).
- Updated the offline observer kit to verify attachment integrity (not just payloads and envelopes).
- Fixed pointer media type naming drift by preferring `media_type` while accepting deprecated `content_type` for backward compatibility (schema updates + tooling updates).
- Added receipted example packets: updated `evidence_packet_minimal` and added `evidence_packet_enr_receipted`.
- Added PO-009 + CLM-035 to treat receipted+gossiped publication as a first-class deliverable.


## v41 (2026-02-21) — Evidence API surface + kind registry

- Added an envelope kind registry (`docs/178`, `artifacts/registries/envelope-kinds.csv`) to keep verifiers’ supported kinds small and stable.
- Added a minimal offline verifier surface doc (`docs/179`) and linked it from Track entrypoints.
- Added `scripts/check_envelope_kinds.py` and wired it into the release pipeline (`docs/162`) to prevent kind drift in examples.
- Extended artifact reference conventions with `REG:` tokens and updated tooling accordingly.
- Updated START_HERE + indices to surface the “API surface” and prevent scope/maintenance drift.


## v40 (2026-02-21) — Envelope-first refactor + offline observer kit

- EvidenceEnvelope schema updated to require exactly one of `payload_inline` or `payload_pointer`, with `canonicalization` and `tbs_digest`.
- Added canonicalization & signing rules (`docs/176`) and offline observer walkthrough (`docs/177`).
- Added stdlib reference tools: `tools/jcs_canonicalize.py`, `tools/envelope_wrap.py`, `tools/observer_verify_packet.py`.
- Added minimal example evidence packet under `artifacts/examples/evidence_packet_minimal/`.
- Added `schemas/CoverageReport.json` and tightened coverage publication guidance.
- Added PO-008, claims CLM-033/034, and hazard HZ-018 (format drift).


## v39 (2026-02-21) — Evidence packets + coverage accounting + endorsement governance

- Added canonical evidence envelopes and packet layout (`docs/173`) and new schemas (`EvidenceEnvelope`, `EvidencePointer`).
- Added executable toy coverage accounting (`docs/174`, `tools/coverage_accounting.py`, `artifacts/coverage/*`).
- Added minimum governance spec for endorsement/reference registries (`docs/175`) plus governance schemas.
- Extended proof obligations, claims, hazards, and response playbooks for the above.
- Updated track bundles and regenerated generated artifacts (BUNDLE + MVR).


## v38 (2026-02-21)

- Added a reusable public-randomness kernel for seeded sampling (anti-grinding): `docs/168-public-randomness-beacons-and-seeded-sampling.md`.
- Expanded North Star “anti-capture” design for endorsements/reference values and tied it to SCITT receipt/API work:
  - `docs/169-endorsement-and-reference-value-transparency.md`
  - Updated `docs/141-scitt-transparency-service-profile.md` with receipts + SCRAPI notes.
- Added a concrete supply-chain provenance profile using SLSA + in-toto and pinned additional sources: `docs/170-slsa-and-intoto-provenance-profile.md`.
- Added a socio-technical threat model treating humans as first-class adversaries: `docs/171-human-adversary-model-and-legitimacy-attacks.md`.
- Added an explicit open research backlog: `docs/172-open-research-questions-and-experiment-backlog.md`.
- Updated registries:
  - Added PO-204 (auditable software build provenance).
  - Added CLM-029 and updated hazards/PO linkages for North Star supply-chain + registry capture.


## v37 (2026-02-21)

- Added a claims constitution and explicit boundaries:
  - `docs/166-scope-and-claims-contract.md`
  - `docs/167-non-claims-and-boundaries.md`
- Updated `docs/START_HERE.md` to state archive size-discipline (no wholesale external PDFs) and to front-load claims/non-claims.
- Updated track READMEs (A/B/C) to align with claim tiers and link the constitution docs.
- Updated track bundles to include the constitution docs and regenerated `docs/track-*/BUNDLE.md`.
- Updated top-level navigation in `README.md` and `ARCHIVE_INDEX.md`.


## v36 (2026-02-21)

- Added an authoritative proof-obligations registry: `docs/164-proof-obligations-registry.md` + `artifacts/proof_obligations/proof-obligations.csv`.
- Added curated track bundles (TriKEM-style navigation hardening):
  - Bundle definitions: `artifacts/bundles/*.toml`
  - Generated pages: `docs/track-a|b|c/BUNDLE.md` (via `scripts/gen_track_bundles.py`)
- Added a generated Track A minimum viable release gate keyed to proof obligations: `docs/track-a/MVR_CHECKLIST.md` (via `scripts/gen_track_a_mvr.py`).
- Added `docs/165-track-bundles-and-minimum-viable-sets.md` and new CI check `scripts/check_proof_obligations.py`.
- Expanded claim/evidence matrix to include explicit public-inspection ecosystem claims (PO-101..103) and North Star POs (PO-201..203).


## v35 (2026-02-21)

- Added track entrypoints: `docs/START_HERE.md` and `docs/track-a|b|c/README.md`.
- Added release gate doc: `docs/162-release-and-ci-evidence-pipeline.md`.
- Added artifact reference conventions: `docs/163-artifact-reference-conventions.md`.
- Standardized claim/hazard references using TYPE:path tokens; added playbooks under `artifacts/playbooks/`.
- Added validation scripts: `scripts/check_tracks.py` and `scripts/validate_artifact_refs.py`; strengthened `scripts/check_index.py`.
- Added missing incident checklists (ballot definition, availability) and cohort audit checklist.


## v34 (2026-02-21)

Docs + navigation refactor to make the archive easier to maintain and harder to misread.

### Structure
- Moved numbered specs into `docs/` (TriKEM-style layout) and updated references.
- Regenerated `docs/13-artifact-index.md` as a track-grouped table with tombstone annotations.
- Added a `**Track:**` header to every numbered spec to prevent scope confusion during edits.

### Evidence scaffolds
- Expanded `artifacts/claims/claim-evidence-matrix.csv` with an initial “top claims” set.
- Expanded `artifacts/hazards/hazard-register.csv` with an initial “top hazards” set.


## v33 (2026-02-21)

Process + scope refactor to keep the archive survivable and to clarify what it is “about”.

### Scope and structure
- Added explicit three-track framing (Deployable Core / Remote Return Research Annex / North Star).
- Added a single scope map to prevent “are we abandoning the full election stack?” confusion.

### TriKEM-derived meta-engineering upgrades
- Filled an initial external-sources lockfile with sha256 pins (where retrievable).
- Added hazard register + claim/evidence matrix scaffolds.
- Added “generated canonical spec contract” + manifest tooling to prevent silent drift.

### North Star upgrades
- Added a concrete attestation + provenance stack plan (RATS/EAT + in-toto + SCITT-style transparency).
- Added a first-pass attestation claim profile and reference-value registry structure.
- Added a manufacturing evidence pipeline sketch (what gets signed, by whom, and how it’s audited).


## v31 (2026-02-21)

- Maintainer bootstrap/change protocol.
- Authoritative sources lockfile template.
- ADR process + freeze plan.
- Public inspection hardening (seeded challenges, gossip, suppression proofs, coverage metrics).
