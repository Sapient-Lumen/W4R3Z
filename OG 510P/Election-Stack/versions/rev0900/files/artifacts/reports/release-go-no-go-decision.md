# Release go/no-go decision record

Archive version: `v900`  
Release date: `2026-06-18`  
Synthetic-only. This is not live election evidence, not certification, not outcome proof, not proof of intent or fraud, not current-authority determination, and not legal advice.

## Topline

- Synthetic research release: `GO_SYNTHETIC_RELEASE_ONLY`.
- Live pilot use: `NO_GO_LIVE_PILOT_WITHOUT_LOCAL_INTAKE_REDACTION_REVIEW_ACCESSIBILITY_LANGUAGE_REVIEW_CUSTODY_PROVENANCE_INDEPENDENT_REVIEW_EXTERNAL_REVIEW_SOURCE_REFRESH_AND_LEDGER_EVIDENCE`.
- Certification claims: `NO_GO_CERTIFICATION_CLAIMS`.
- Current public-authority reliance: `NO_GO_CURRENT_AUTHORITY_WITHOUT_SOURCE_REFRESH_OR_PINNING`.
- Legal/court use: `NO_GO_LEGAL_USE_WITHOUT_COUNSEL_REVIEWED_JURISDICTION_WORKSHEET`.

## Current signals

- Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`.
- Synthetic smoke: `PASS`.
- Evaluator scorecard: `PASS` `100/100`.
- Negative controls: `PASS` across `8` fixtures.
- Local pilot intake: `NO_GO_LIVE_PILOT_LOCAL_INTAKE_INCOMPLETE` with `17` missing live-evidence rows.
- Redaction/publication gate: `NO_GO_PUBLIC_RELEASE_REDACTION_REVIEW_INCOMPLETE` with `14` missing approval rows.
- Accessibility/language gate: `NO_GO_PUBLIC_RELEASE_ACCESSIBILITY_LANGUAGE_REVIEW_INCOMPLETE` with `14` missing approval rows.
- Custody/provenance gate: `NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE_INCOMPLETE` with `14` missing custody-record rows.
- Independent-review/conflict gate: `NO_GO_INDEPENDENT_REVIEW_CONFLICT_EVIDENCE_INCOMPLETE` with `14` missing review-evidence rows.
- Adopter source-authority capture: `70` missing captures across `70` quarantined state/local rows.
- Capture-record validator fixtures: `7` fixtures, `5` negative, `0` expectation failures, `0` valid promotions.
- Mission-kernel live-evidence intake: `NO_GO_NO_LIVE_EVIDENCE_SUBMITTED` with `0` live objects, `0` drill objects, and `7` missing work items.
- Full mission-kernel non-production drill replay: `DRILL_COMPLETE_NOT_LIVE_READY` with `7/7` work items complete, `28` valid drill objects, `28` required evidence classes, and `0` live objects.
- CDF export replay bridge: `SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE` across `12` comparison rows and `6` synthetic CVR records; full NIST conformance claim: `False`.
- Independent CDF replay verifier: `INDEPENDENT_SYNTHETIC_CDF_REPLAY_AGREES_NOT_CONFORMANCE` across `12` comparison rows and `6` synthetic CVR records; primary-report agreement: `True`; CRO agreement: `True`; full NIST conformance claim: `False`.
- Ballot-accounting reconciliation: `SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE` across `4` contest accounting rows and `6` synthetic CVR records; live custody claim: `False`.
- Election-event log reconciliation: `SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL` across `12` event rows; missing required roles: `0`; live EEL claim: `False`.
- Source reviews expired at release date: `0`.
- Unpinned sources due within 30 days: `0`.

## Decision criteria

- `RGN-001` / `GO_SYNTHETIC_RELEASE` — Synthetic research release may proceed only when the archive ZIP and extracted tree verify and the release-gate summary is current.
- `RGN-002` / `NO_GO_LIVE_PILOT` — Live pilot use must wait for local configuration live evidence ledgers external review and jurisdiction signoff.
- `RGN-003` / `NO_GO_CURRENT_AUTHORITY` — Current voter-facing authority reliance must wait for source refresh/pinning, local official confirmation, and adopter capture records for quarantined state/local xrefs.
- `RGN-004` / `NO_GO_CERTIFICATION` — The stack must not claim certification conformance or attack-free status from synthetic rehearsals or negative controls.
- `RGN-005` / `NO_GO_LEGAL_USE` — Court public-records or admissibility reliance must wait for counsel-reviewed jurisdiction worksheets and local preservation policy.
- `RGN-006` / `CONDITIONAL_REVIEW` — Offline verification should be rehearsed before promotion beyond synthetic publication.
- `RGN-007` / `CONDITIONAL_REVIEW` — AI-assisted public-message use requires human approval PII discipline and prohibited-use controls before publication.
- `RGN-008` / `CONDITIONAL_REVIEW` — Non-voting election technology claims must stay mapped to external assessment lanes without implying RABET-V or EAC certification unless independently documented.
- `RGN-009` / `GO_SYNTHETIC_RELEASE` — Expected-failure fixtures support synthetic regression confidence when all temporary tamper cases fail closed.
- `RGN-010` / `GO_SYNTHETIC_RELEASE` — Human-review and trust-recovery handoff outputs may be published as synthetic examples when they preserve bounded public language and non-claim boundaries.
- `RGN-011` / `NO_GO_LIVE_PILOT` — Live pilot promotion must wait for a complete local-pilot intake matrix with authority scope official channels privacy retention reviewers source freshness external review and legal boundaries.
- `RGN-012` / `NO_GO_LIVE_PILOT` — Public release of local evidence must wait for redaction policy closure, reviewer approval, and public/private field separation.
- `RGN-013` / `NO_GO_LIVE_PILOT` — Voter-facing public artifacts must wait for accessibility/language policy closure, local reviewer approval, plain-language review, language-access parity, accessible text equivalents, and human-help fallback.
- `RGN-014` / `NO_GO_LIVE_PILOT` — Live evidence reliance must wait for custody/provenance records covering capture scope, collector role, capture environment, digest lineage, transfer handoff, access logs, public/private separation, incident freeze, source-review custody, chain gaps, and disposition.
- `RGN-015` / `NO_GO_LIVE_PILOT` — Independent-review or third-party-validation language must wait for reviewer scope conflict disclosures qualifications reproducibility transcript dissent route public-summary approval reviewer access records and remediation/retest closure.
- `RGN-016` / `NO_GO_LIVE_PILOT` — Live mission-kernel closeout must wait for authority custody export replay audit adjudication independent-verifier public-approval and incident-remedy evidence rows to close.
- `RGN-017` / `NO_GO_LIVE_PILOT` — Live mission-kernel evidence intake must validate authorized local records by digest source authority redaction/public-boundary review and retention context before any closeout reliance claim.
- `RGN-018` / `CONDITIONAL_REVIEW` — Mission-kernel evidence submitter drills may proceed only as non-production operator exercises that hash external records and preserve live no-go boundaries.
- `RGN-019` / `CONDITIONAL_REVIEW` — Full mission-kernel drill replay may proceed only as a non-production exercise that validates all live-closeout work items through the shared submitter and intake validator while preserving zero live evidence objects.

## Source-review burn-down snapshot

- Sources: `1216`.
- Pinned: `118`.
- Unpinned: `1098`.
- Due within 7 days: `0`.
- Due within 14 days: `0`.
- Due within 30 days: `0`.
- Official websites due within 30 days: `0`.

## Required before live promotion

- Complete local-pilot intake requirements with jurisdiction-specific evidence, named owners, and authority boundaries.
- Replace synthetic Example County outputs with jurisdiction-specific artifacts.
- Complete redaction/publication review before public release of local evidence-derived artifacts.
- Complete accessibility/language, plain-language, fallback, and human-help review before voter-facing public release.
- Complete custody/provenance records before treating local packets as field evidence.
- Complete independent-review/conflict disclosures, reviewer scope, transcripts, dissent routes, and remediation/retest records before third-party-validation or live-pilot claims.
- Refresh or pin current-authority sources before voter-facing reliance.
- Add valid adopter capture records and human approvals before promoting quarantined state/local xrefs into public-answer guidance.
- Populate live drill, external-review, witness-health, MAPT, TTR, and admissibility ledgers.
- Obtain local counsel and election-office review before court, public-records, or legal-use claims.
- Run an offline verification drill and preserve its transcript.
