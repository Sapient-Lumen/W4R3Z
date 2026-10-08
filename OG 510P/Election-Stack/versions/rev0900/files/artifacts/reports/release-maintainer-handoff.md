# Release maintainer handoff pack

**Synthetic example only. This is not live election evidence, not certification, and not legal advice.**

Archive version: `v900`  
Release date: `2026-06-18`  
Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`

## Boundary

Release maintainer handoff only; synthetic rehearsal outputs are not live election evidence, not certification, not outcome proof, not proof of intent or fraud, and not legal advice.

## Current synthetic outputs

- Packet smoke status: `PASS` across `20` packets.
- Evaluator scorecard: `PASS` `100/100`.
- Negative controls: `PASS` across `8` expected-failure fixtures.
- Trust-recovery modes: `11`.
- Human-review scenarios: `10`.
- Local pilot intake: `NO_GO_LIVE_PILOT_LOCAL_INTAKE_INCOMPLETE` with `17` missing live-evidence rows.
- Redaction/publication gate: `NO_GO_PUBLIC_RELEASE_REDACTION_REVIEW_INCOMPLETE` with `14` missing approval rows.
- Accessibility/language gate: `NO_GO_PUBLIC_RELEASE_ACCESSIBILITY_LANGUAGE_REVIEW_INCOMPLETE` with `14` missing approval rows.
- Custody/provenance gate: `NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE_INCOMPLETE` with `14` missing custody-record rows.
- Independent-review/conflict gate: `NO_GO_INDEPENDENT_REVIEW_CONFLICT_EVIDENCE_INCOMPLETE` with `14` missing review-evidence rows.
- Mission-kernel live-closeout workqueue: `NO_GO_LIVE_CLOSEOUT_EVIDENCE_INCOMPLETE` with `5` critical blocker rows and `7` total rows.
- Mission-kernel live-evidence intake: `NO_GO_NO_LIVE_EVIDENCE_SUBMITTED` with `0` live objects, `0` drill objects, and `7` missing work items.
- Full mission-kernel non-production drill replay: `DRILL_COMPLETE_NOT_LIVE_READY` with `7/7` work items complete, `28` valid drill objects, `28` required evidence classes, and `0` live objects.
- Ballot-accounting reconciliation: `SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE` with `4` contest accounting rows and `0` errors; live custody claim: `False`.
- Election-event log reconciliation: `SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL` with `12` event rows, `0` errors, and `0` missing required roles; live EEL claim: `False`.

## Release-gate inventory

- Child steps: `172` plus final `build_manifest.py` manifest check/write step.
- The handoff pack is a maintainer summary; run `python3 scripts/release_gate.py` for the authoritative gate.

## Source-review pressure

- Sources total: `1216`.
- Pinned: `118`.
- Unpinned: `1098`.
- Expired review windows at release date: `0`.
- Due within 30 days: `0`.

## Handoff actions

- `RMH-001` / `release_digest`: current release is being sealed → release maintainer.
- `RMH-002` / `synthetic_rehearsal_status`: Example County outputs changed → release maintainer.
- `RMH-003` / `source_review_triage`: external source review queue is near release date → source reviewer.
- `RMH-004` / `failure_handoff`: verifier output fails or public artifact is stale/divergent → incident lead plus release maintainer.
- `RMH-005` / `human_review_handoff`: reviewer dissent redaction or ambiguous evidence requires human decision → human review lead.
- `RMH-006` / `release_gate_inventory`: release gate step list or generated outputs change → release maintainer.
- `RMH-007` / `residual_non_live_status`: reader may mistake synthetic rehearsal for field evidence → release maintainer.
- `RMH-008` / `go_no_go_decision`: current release may be mistaken for live-pilot approval → release maintainer.
- `RMH-009` / `local_pilot_intake`: reader may treat synthetic release as a jurisdiction-ready live pilot → release maintainer.
- `RMH-010` / `redaction_publication_no_go`: reader may publish evidence-derived artifacts before privacy redaction review → release maintainer and privacy reviewer.
- `RMH-011` / `accessibility_language_no_go`: reader may publish voter-facing artifacts before accessibility language-access plain-language fallback and human-help review → release maintainer accessibility reviewer and language-access lead.
- `RMH-012` / `evidence_custody_provenance_no_go`: reader may treat digest-valid packets as local field evidence without custody transfer access sealing or disposition records → release maintainer custody lead and records custodian.
- `RMH-013` / `independent_review_conflict_no_go`: reader may treat self-tested synthetic release as independent third-party validation or live-pilot approval → release maintainer external review coordinator and reviewer panel chair.
- `RMH-014` / `mission_kernel_closeout`: reader may mistake synthetic replay for mission-complete live readiness → release maintainer and jurisdiction authority liaison.
- `RMH-015` / `mission_kernel_live_workqueue`: reader may leave mission blockers as prose rather than collecting local closeout evidence → release maintainer and jurisdiction authority liaison.
- `RMH-016` / `mission_kernel_live_evidence_intake`: operator is ready to replace empty workqueue slots with jurisdictional closeout evidence → release maintainer jurisdiction authority liaison custody lead and redaction reviewer.
- `RMH-017` / `mission_kernel_evidence_submitter`: operator needs to hash local closeout records without copying private source records into the governed archive → release maintainer jurisdiction authority liaison custody lead and redaction reviewer.
- `RMH-018` / `mission_kernel_full_drill_replay`: operator needs to know whether all seven closeout rows can traverse the submitter and intake validator before a real jurisdiction supplies records → release maintainer jurisdiction authority liaison custody lead redaction reviewer and independent verifier lead.

## Residual non-live items

- No live pilot deployment evidence is claimed in this release.
- External review, MAPT, TTR, witness-health, and admissibility rows remain pre-pilot placeholders unless a live row says otherwise.
- Synthetic Example County packets exercise verifier and handoff behavior only.
- Source-review triage identifies review pressure but does not certify a source as current authority.
- Local pilot intake remains no-go until jurisdiction-specific authority, source, privacy, retention, review, and legal evidence is added.
- Public release of local evidence remains no-go until redaction review and local approval are recorded.
- Voter-facing public release remains no-go until accessibility, language-access, plain-language, fallback, and human-help review are recorded.
- Live field-evidence reliance remains no-go until custody/provenance capture, transfer, access, public-derivative, chain-gap, and disposition records are recorded.
- Independent-validation and live-pilot claims remain no-go until reviewer scope, conflict disclosures, transcripts, dissent routes, public summary approval, and remediation/retest records are recorded.
- Mission-kernel live-closeout workqueue rows remain blocked until authorized local evidence, digests, approvals, redaction/public-boundary review, and retention/disposition records are supplied.
- The shipped live-evidence intake submission is deliberately empty; zero live evidence objects and zero non-production drill objects are present in this synthetic archive.
- The evidence submitter drill hashes temporary external records only to test plumbing; drill success is not live closeout evidence or authorization.
- The full mission-kernel drill replay completes all seven workqueue rows and twenty-eight evidence-class objects in non-production mode while preserving zero live evidence objects and zero live-readiness claims.
- The synthetic ballot-accounting reconciliation checks BD/CVR count completeness but is not live custody evidence, certification, or outcome proof.
- The synthetic election-event log reconciliation binds replay artifacts by digest and time order but is not live EEL evidence, full NIST EEL/CDF conformance, certification, or outcome proof.

## Source triage categories

- `pinned`: `118` — No immediate review required; keep pinned byte hash and citation role stable.
- `unpinned_expired_review`: `0` — Release-blocking until refreshed, pinned, demoted, or replaced.
- `unpinned_due_within_30_days`: `0` — Schedule source refresh or pinning before relying on these as current authority.
- `unpinned_due_later`: `1098` — Keep in ordinary source-review queue.
- `unpinned_missing_review_by`: `0` — Release-blocking hygiene issue; add review_by or pin durable bytes.
- `special_case_high_risk_due_within_30_days`: `0` — Prioritize before voter-facing high-risk special-case use.
- `official_websites_due_within_30_days`: `0` — Prioritize official-site refresh where current public instructions may change.

## Operator commands

```bash
python3 tools/release_maintainer_handoff_pack.py --json
python3 scripts/check_release_maintainer_handoff.py
```
