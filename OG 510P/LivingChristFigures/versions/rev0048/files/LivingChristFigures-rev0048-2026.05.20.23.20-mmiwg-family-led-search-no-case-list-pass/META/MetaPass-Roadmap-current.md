# MetaPass Roadmap — current

## Completed in rev0029

1. Manifest truthfulness check: the rev0028 stale-manifest bug is now recorded and QA-protected.
2. Operator dissent ledger: method critique now has a place to live that requires behavior-change fields.
3. Source provenance audit: existing sources are summarized by type, role, and provenance risk without pretending a live refresh happened.
4. Claim-type taxonomy: current claim types now have minimum evidence standards and public-wording cautions.
5. Evidence-debt dashboard: debt pressure is summarized as a work queue.
6. Boundary-rule coverage map: rules 15–25 are mapped to trigger subjects and required actions.
7. Public export checklist: public reading edition has gates before release.

## Next high-value metapasses

1. **Automated redaction-risk scan** — grep candidate/public/longform prose for phone-number-like strings, precise addresses, coordinates, plot numbers, individual case-story detail markers, and names in child/survivor/patient contexts.
2. **Source-role normalization pass** — collapse source_type variants such as `public_agency_source`, `public_agency_or_cemetery_source`, and `public_agency_source_fetch_limited` into a controlled vocabulary while preserving original labels.
3. **Evidence-strength scoring pass** — add a non-final evidence-strength field to claims: `direct_primary`, `independent_corrob`, `critical_counterevidence`, `context_only`, `capacity_not_proven`, etc.
4. **Negative-case ledger** — create a place for candidates rejected, deferred, or demoted so the cube does not only remember successful admissions.
5. **Office collision review** — identify offices whose boundaries overlap enough to confuse interpretation, especially name-after-death / public cemetery / unclaimed remains / disconnected dead.
6. **Public-reading table of contents draft** — build a boundary-first TOC without drafting the full public edition.
7. **Operator update audit** — revisit `opdist_0001` and ask which actual cube decisions changed because of operator-centrality critique.


## rev0030 completed

- Added automated redaction-risk scanner.
- Removed discovered exact public contact digits from the working cube.
- Added rule 26 and QA enforcement for configured high-risk scanner findings.

## Next likely metapass

- Source-role linting: ensure a public profile, nonprofit page, state page, academic paper, critical article, and directory page cannot silently do the same evidentiary work in claim rows.
- Evidence-age scoring: flag claims whose newest source is stale for current-capacity language.

## rev0031 completed

- Added `SCHEMA/` contract layer.
- Added front-matter contracts for candidates, office cards, and refresh notes.
- Added exact ledger/header contract plus JSON mirror parity checks.
- Added controlled source-type vocabulary for `Source-Registry-current.csv`.
- Added package release contract and schema validation report.
- Added `tools/schema_validate.py` and wired schema validation into QA.

## Next likely metapass after rev0031

- Evidence-strength scoring: add or derive a non-final field for claim rows that
  distinguishes direct primary evidence, independent corroboration, critical
  counterevidence, context-only evidence, and capacity-not-proven evidence.
- Negative-case ledger: record demoted/rejected/deferred candidates so the cube
  does not only remember admissions and boundary wins.


## rev0032 completed

- Added evidence lifecycle scoring and refresh-priority routing.
- Added `tools/evidence_lifecycle.py`.
- Added claim-level evidence-strength labels and candidate-level refresh queue.
- Added rule 28: evidence-lifecycle / refresh-priority rule.

## Next likely metapass after rev0032

- Negative-case ledger: record rejected, demoted, deferred, and not-yet-admitted candidates so the cube does not only remember successful admissions and boundary wins.
- Operator-update audit: convert at least one existing dissent row into an explicit before/after behavior-change receipt.


## rev0033 completed

- Added negative-case/deferred-candidate memory: `META/Negative-Case-Ledger-current.*`.
- Added online research intake: `META/Online-Research-Intake-current.*`; sources found in the same pass are not silently promoted into Source-Registry/claim evidence.
- Added operator-update receipts: `META/Operator-Update-Audit-current.*`, including a behavior-change receipt for `opdist_0001` without closing the critique.
- Added rules 29 and 30 and QA checks for the new instruments.

## Next likely metapass after rev0033

- Candidate-specific source-promotion pass: pick the highest-priority rows from `META/Online-Research-Intake-current.*`, promote selected sources to `Source-Registry-current.*`, and update candidate/claim/evidence-debt rows only where source-role and redaction review pass.
- Public-reading table of contents draft: build a boundary-first TOC using negative-case and evidence-lifecycle gates before beautiful candidate narration.

## rev0034 completed

- Added source-promotion decisions for all online-research intake rows.
- Added public-claim quarantine for every lifecycle row marked `now_or_before_any_public_claim`.
- Added refresh-sprint matrix and six candidate/cluster refresh notes.
- Added rules 31 and 32 plus QA checks for the new veto/quarantine layer.

## Next likely metapass after rev0034

- Candidate-specific source-promotion pass for one cluster only, beginning with the least dangerous source class. Any promotion must update Source-Registry, claim rows, source freshness audit, evidence debt, and quarantine status together.
- Public-reading table of contents draft only after quarantine rows are used to mark which beautiful claims are not yet speakable publicly.


## rev0035 completed

- Completed the first candidate-specific source-promotion canary, choosing the least dangerous source class from the rev0034 matrix.
- Promoted two Aisha/project.ME local-reporting sources for non-referral shape only.
- Added source-promotion transaction audit and public-claim release ledger.
- Released `claim_0001` from public-current quarantine only for high-level non-referral shape; all capacity, referral, outcome, access, route, schedule, and contact wording remains blocked.
- Added rule 33 and QA checks for promotion/release receipts.

## Next likely metapass after rev0035

- Do not jump to a high-risk class. Next, either run a second low-risk canary on a non-contact-rich historical/context source, or draft the boundary-first public-reading table of contents using quarantine/release states as gates.
- Higher-risk promotions — survivor services, border offices, conflict-zone aid, helpline/contact directories — should remain blocked until each has an equivalent transaction audit and redaction review.


## rev0036 completed

- Completed a second low-risk canary: promotion of counterevidence rather than corroboration.
- Promoted the SAGE humanitarian-corridors article as Sant’Egidio selection/reception/power boundary evidence only.
- Updated source, claim, debt, intake, promotion-decision, transaction, operator-update, and boundary-rule artifacts together.
- Added rule 34: counterevidence promotion / no-release rule.

## Next likely metapass after rev0036

- Draft the boundary-first public-reading table of contents using quarantine/release states as gates, or run a hold-only review on a higher-risk source class without promotion.
- Do not promote survivor-service, border-route, conflict-zone, shelter, helpline, or directory sources without a candidate-specific transaction audit and redaction review.

## rev0037 roadmap note

Next likely deep pass: either Calais/HRO aggregate counterpressure promotion under route/no-location controls, or a boundary-first public-reading table of contents that starts from quarantine, no-map, and non-referral gates rather than candidate praise.


## rev0038 completed

- Completed Calais/HRO aggregate counterpressure promotion under no-route controls.
- Promoted the March 2026 HRO Calais-area report and Monthly Observations index as counterpressure/publication-infrastructure evidence only.
- Updated Calais candidate/claim/debt/quarantine/source-promotion ledgers together and added rule 36.

## Next likely metapass after rev0038

- Draft the boundary-first public-reading table of contents using quarantine/release states as gates.
- Or run a non-extractive image/name audit for entries whose public sources include camps, children, survivors, the dead, or resident imagery.


## rev0039 completed

- Completed Pacific survivor/crisis-service standards/funding no-referral pass.
- Promoted PAVE and regional counselling-framework context without releasing contact, shelter/refuge, current-capacity, or referral wording.
- Updated Pacific contact-rich cluster ledgers and added rule 37.

## Next likely metapass after rev0039

- Draft the boundary-first public-reading table of contents using quarantine/release states as gates.
- Or run a non-extractive image/name audit for entries whose sources include survivors, children, the dead, camps, refuges, or residents.

## rev0040 completed pass
Completed rev0040: Mexico buscadoras family-search no-field-map canary. Next useful pass: non-extractive image/name/case-story audit before any public death/disappearance/forensic/search-collective prose.

## rev0042 completed

- Completed the non-extractive image/name/case-story audit promised after the Mexico family-search pass.
- Used Garden of Innocence as a posthumous child-burial canary.
- Added rule 40 and held detail-rich official/anniversary/cemetery/critical sources as redaction-risk evidence, not public prose.
- Released no public claim.

## Next likely metapass after rev0042

- Draft the boundary-first public-reading table of contents using quarantine/release states as gates.
- Or run the same non-extractive audit on public cemetery, migrant grave, disconnected-dead, or family-search entries before any public memorial/death prose.

## rev0043 completed

- Completed Hart Island searchable-memory no-record-extraction canary.
- Promoted NYC Council/Data.gov/Legistar sources only as aggregate governance, data-privacy, and legislative-boundary evidence.
- Held live search/story surfaces and transcript logistics as non-extractive intake.
- Quarantined `claim_0257` and added rule 41.

## Next likely metapass after rev0043

- Draft the boundary-first public-reading table of contents using quarantine/release states as gates.
- Or run the same no-record/no-case-extraction audit on migrant graves, disconnected-dead offices, homeless memorials, or overdose memorial entries before public death/memorial prose.

## rev0045 completed

- Completed homeless memorial / mortality-data no-name extraction pass.
- Promoted aggregate/method/boundary sources for Dying Homeless, Homeless Persons Memorial Day, Homeless Deaths Count, and public-health mortality review.
- Held image/event local reporting as redaction-risk intake.
- Added rule 43 and quarantined claim_0072 before any public memorial prose.

## Next likely metapass after rev0045

- Draft the boundary-first public-reading table of contents using quarantine/release states as gates.
- Or run a non-extractive media/name audit on remaining death, disappearance, disconnected-dead, cemetery, or family-grief entries before any public prose.


- rev0047 completed a migrant death monitoring no-route/no-distress-signal pass; future work should cross-apply rule 45 to other border-death and shipwreck entries.
