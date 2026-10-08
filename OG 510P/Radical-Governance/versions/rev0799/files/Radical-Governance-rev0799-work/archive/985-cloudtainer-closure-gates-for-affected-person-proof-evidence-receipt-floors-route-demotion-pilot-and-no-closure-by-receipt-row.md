# 985 — Cloudtainer closure gates for affected-person proof, evidence-receipt floors, route-demotion pilot, and no closure by receipt row

## One-line thesis

The evidence-receipt pilot only becomes substantive when receipts can block premature closure, force proof floors above official surfaces, and demonstrate that at least one low-risk route can leave active circulation without being deleted.

## Why this matters

Rev0786 made a necessary move: it stopped treating official sources as field validation and created a privacy-bounded receipt spine for unemployment-insurance and housing-continuity proof gaps. But a new spine can become a new theater. A receipt row can be read as a proof object merely because it is structured, generated, linted, and current.

This revision therefore changes the control plane rather than adding a broad doctrine family. Evidence receipts now carry proof floors, denominator gaps, closure blockers, and a boolean `can_close_gap` field. Lint enforces that a non-field-validated receipt cannot close the affected-person or source-preservation gaps. The cube can still say: this source justifies a test; this source is not enough to repair the claim.

The revision also pilots a tiny route-demotion review. Note `465` is preserved byte-for-byte in the archive, but its metadata status becomes `historical_preserved` because it is a low-dependency, non-front-door, non-first-citation alias/confusability pattern whose current contribution is sufficiently covered by later source, route, and taxonomy discipline. This is not deletion. It is proof that active circulation is a choice.

The governing rule is **no closure by receipt row**.

## Pattern pack

1. **A receipt has a floor.** The source class says the lowest thing the receipt proves: policy permission, implementation guidance, dataset boundary, partial system outcome, or field-validated person outcome.
2. **A receipt has a closure effect.** Until it reaches field-validated affected-person outcome proof, it should block closure of affected-person and claim-capture gaps instead of repairing them.
3. **A receipt has a denominator.** The cube must state whether non-users, abandonments, missing households, nonrespondents, and informal exits remain outside the evidence frame.
4. **A receipt has a privacy posture.** The archive stores proof requirements and source posture, not claim numbers, names, addresses, case IDs, screenshots, or private records.
5. **A receipt has a missing-next-proof tail.** Minimum next receipts must describe what would actually move the proof floor upward.
6. **A green generated surface is not proof.** Generated receipt parity proves that rows match metadata. It does not prove the public outcome.
7. **A route can be demoted without deletion.** Historical preservation keeps the text, hash, manifest row, source catalog, and searchability while removing the claim that the route is active operating guidance.
8. **Retirement is reversible only by reason.** A demoted note needs a rollback condition, successor/supporting route, and a review note; otherwise route subtraction becomes untraceable erasure.

## Closure-gated receipt model

The revised receipt spine adds four fields.

`proof_floor` identifies the actual evidentiary floor. Current rows remain below field validation: official policy, program playbook, survey/report, dataset boundary, oversight surface, or regulatory guidance. None is allowed to claim that an affected person was paid, housed, heard, or repaired.

`denominator_gap` states what population is still missing: non-users, people who abandoned a claim, survey nonrespondents, informal eviction households, applicants screened out before an application, or households whose remedy did not produce durable stability.

`closure_blocker_for` links the receipt to live gaps. Current UI and housing rows block `GAP-029-affected-person-outcome-validation` and `GAP-031-source-evidence-preservation-and-claim-capture` until a later packet records privacy-approved field or independently collected outcome evidence.

`can_close_gap` is false on every current receipt. Lint now rejects a row that says `can_close_gap: true` unless the proof floor is `field_validated_person_outcome` and the affected-person gap no longer says the cube lacks direct person/household evidence.

## UI closure gate

The unemployment-insurance proof floor cannot rise above official or program evidence until a bounded claimant sample can join issue state, notice receipt, claimant burden, cure path, appeal or waiver state, identity or overpayment classification, and money or debt state after cure. A clear DOL-style claim-status surface is useful, but it is still below the floor required to close a claimant-outcome gap.

The new UI closure receipt therefore asks a narrower question: does the archive possess a privacy-approved sample or independent outcome series showing that valid claimants delayed or blocked by integrity controls were actually paid, had debt removed, obtained waiver relief, or received another completed remedy? If not, the UI case can keep its tests but must not call the affected-person gap repaired.

## Housing closure gate

The housing proof floor cannot rise above dataset or oversight evidence until household tails are joined from filing or assistance to possession, displacement, shelter, re-housing, screening/application effect, and durable stability. Eviction filings, right-to-counsel percentages, assistance awards, and tenant-screening guidance all identify risk and design tests. They do not prove where the household ended up.

The new housing closure receipt therefore asks whether the archive has a household-follow-up method that includes informal move-outs, illegal lockouts, households that never reached counsel, households screened out before a lease, and households whose assistance did not post or did not preserve possession. Without that, the case remains useful but not validated.

## Route-demotion pilot

The archive has long said it wants retirement discipline, but almost every route remained active in some form. Rev0787 changes one low-risk note status from `active` to `historical_preserved`: note `465`, on confusability budgets and alias-collision registers.

The demotion is intentionally conservative. Note `465` is not a front-door target, not a first citation, not a dispatcher, and not a dependency in current note metadata. It remains in `archive/`, `generated/ARCHIVE_INDEX.json`, `generated/MANIFEST.json`, and the source catalog. The metadata adds a demotion-review object with successor/supporting routes, reasons, and rollback conditions. Lint now rejects historical-preserved notes that remain front-door targets, first citations, current-revision notes, or unreviewed status changes.

This does not solve route gravity. It proves the cube can subtract active status without pretending to delete history.

## Audit/refactor

The audit/refactor in this pass is deliberately small and risk-facing.

First, `tools/build_evidence_receipts.py` now generates proof-floor and closure-blocker summaries so the human surface shows not only receipt rows but whether any row actually supports closure. Second, `tools/lint_archive.py` now performs closure-gate validation over evidence receipts and historical-preserved route validation over note metadata. Third, note-status labels now distinguish active routes from historical-preserved routes instead of leaving every preserved file in active circulation by default.

This is a refactor of archive truthfulness, not a new registry family.

## What remains deliberately open

The affected-person gap remains open because no direct claimant or household field sample has been collected. The source-preservation gap remains open because claim-level passage receipts are still not fully captured. The route-retirement gap moves only to an in-progress pilot because one low-risk demotion is not a taxonomy control system. License, maintainer, contribution, and power/material-outcome gaps remain open.

## Failure modes

- **Receipt laundering:** a receipt row is treated as proof because it is generated and linted.
- **Floor inflation:** an official policy source is described as field validation.
- **Denominator erasure:** non-users, abandonments, informal exits, and nonrespondents remain outside the frame.
- **Closure by pilot:** a live pilot is marked repaired before it has external evidence.
- **Demotion by neglect:** an active note is silently hidden without a review object or rollback condition.
- **Deletion by status:** historical preservation is mistaken for authorization to remove the file.
- **Successor theater:** a newer route is named as successor without showing what protected element it actually preserves.

## Anti-theater tests

1. Pick any evidence receipt. Does it say its proof floor, denominator gap, closure blocker, and whether it can close a gap?
2. Pick any receipt whose source keys are official policies, guidance, surveys, dashboards, reports, or datasets. Does lint prevent it from claiming closure?
3. Pick `GAP-029` or `GAP-031`. Can a below-field receipt make the gap look repaired?
4. Pick a UI receipt. Can the packet show money or debt state after cure for a claimant, not just a clear status message?
5. Pick a housing receipt. Can the packet show possession, displacement, shelter, re-housing, and durable stability for a household, not just a filing or award?
6. Pick note `465`. Is it still preserved and hashable while no longer counted as an active route?
7. Pick any future historical-preserved note. Does lint require it to be non-current, non-front-door, non-first-citation, and reviewed?
8. Pick the generated evidence surface. Does it show closure blockers and proof-floor counts instead of only a pretty receipt table?

## Source posture

Use the existing OMB, DOL, GAO, Eviction Lab, NYC Comptroller, and CFPB source keys as source-boundary anchors. They justify burden measurement, claim-status visibility, claimant-experience research, eviction-data limits, right-to-counsel implementation scrutiny, and tenant-screening/housing-access tails. They still do not prove field validation, claimant payment, household possession, or durable stability by themselves.
