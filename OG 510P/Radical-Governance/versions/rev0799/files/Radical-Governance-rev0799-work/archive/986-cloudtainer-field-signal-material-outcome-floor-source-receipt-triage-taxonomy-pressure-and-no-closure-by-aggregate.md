# 986 — Cloudtainer field signal, material outcome floor, source-receipt triage, taxonomy pressure, and no closure by aggregate

## One-line thesis

Aggregate claimant feedback and household outcome surfaces move the archive beyond official guidance, but they still cannot close affected-person, source-preservation, or material-distribution gaps without privacy-bounded person or household tails.

## Why this matters

Rev0786 and rev0787 made the evidence-receipt pilot honest: official surfaces no longer close the affected-person gap. The next risk is subtler. Once the archive finds something better than official guidance—claimant surveys, direct observation, right-to-counsel household outcomes, eviction-filing data—it may be tempted to treat the aggregate signal as the missing lived proof.

This pass pushes the floor upward without pretending it reached the top. The cube now records material-outcome dimensions for each receipt: money, debt, time burden, staff assistance, housing possession, displacement, counsel access, re-housing, durable stability, and denominator tails. It adds two high-value receipts: UI claimant observation/survey evidence and NYC right-to-counsel household outcome evidence. Both are better than policy text. Neither is a privacy-bounded claimant or household tail.

The governing rule is **no closure by aggregate**.

## Pattern pack

1. **Field signal is not field validation.** A claimant observed while filing, or a survey response after filing, is direct evidence of burden and comprehension. It is not proof that the person was paid, the debt was removed, the waiver succeeded, or the hardship ended.
2. **Household aggregate is not household tail.** A right-to-counsel report can show representation and remain/leave outcomes. It does not automatically show informal exits, lockouts, unrepresented defaults, shelter entry, re-housing, or stability after case closure.
3. **Material outcome must name the thing changed.** Each receipt should say whether it touches money, debt, time, care, housing, mobility, status, liberty, safety, coercion, or environmental condition.
4. **Denominator is part of power.** People outside the measured denominator are often where domination hides: non-users, abandonments, screen-outs, defaults, informal displacement, language barriers, and households that cannot wait.
5. **Procedure can still ration.** A beautiful notice, survey, appeal route, counsel right, or status page can coexist with too little money, staff, housing supply, legal capacity, or time.
6. **Source receipt level must be explicit.** A row should say whether it is only a source key, a section locator, a line/page locator, a captured passage, a content fingerprint, or a lawful archival receipt.
7. **Taxonomy pressure should be audited before normalized away.** The source-health ledger has many raw status and volatility labels; the generated audit now normalizes them for comparison without erasing the original text.
8. **Route demotion must be revalidated.** Historical preservation is not a one-time gesture. The note `465` demotion is rechecked against the current front-door and dependency map.

## UI field-signal pilot

The UI row now distinguishes three levels.

- Official policy and program playbooks can justify a test.
- Survey and observation evidence can identify actual claimant friction, staff-intervention points, confusing questions, and channel limits.
- Only a claimant outcome tail can show whether the person ultimately received money, cleared debt, obtained waiver or appeal relief, or avoided hardship.

The new `ER-UI-005` receipt therefore raises the proof floor above official guidance but keeps `GAP-029`, `GAP-031`, and `GAP-033` blocked. A future closure-ready receipt would need a privacy-approved sample that joins filing burden to eligibility, payment, overpayment/debt, waiver, appeal, and hardship outcomes without storing private identifiers in this cube.

## Housing field-signal pilot

The housing row now distinguishes filing exposure, counsel access, representation depth, possession, displacement, shelter or re-housing, and durable stability.

The new `ER-HC-005` receipt treats NYC right-to-counsel evidence as an aggregate household outcome signal. That is valuable: it is closer to material life than a statute, portal, or dashboard. But it still excludes or obscures households that never reached counsel, appeared by default, moved before a formal order, experienced illegal lockout, entered shelter, lost future rental access through screening, or became unstable after case closure.

A future closure-ready receipt would need household-tail sampling across represented, unrepresented, informal-exit, lockout, shelter/re-housing, and stability-after-case groups.

## Material outcome floor

Every evidence receipt now carries `material_outcome_dimensions`. This is intentionally not a new doctrine registry. It is a check against a recurring vice: describing process improvements without asking what changed in money, debt, housing, time, care, liberty, mobility, safety, or status.

For UI, the material floor is money and debt after cure. Application completion and clear status matter because they affect that floor, not because they substitute for it.

For housing, the material floor is possession, displacement, shelter or re-housing, and durable stability. Counsel and rental assistance matter because they affect those floors, not because they substitute for them.

For source preservation, the material floor is lower but still concrete: a reader must be able to reconstruct which source supported which claim, where the passage was, what the source could not prove, and what would be needed before the claim could be relied on for closure.

## Audit/refactor

The refactor in this pass targets comparison waste rather than adding a new registry.

`tools/build_source_health.py` now emits normalized health-status and volatility counts alongside the raw labels. The raw source-health ledger still preserves its original labels, but generated output exposes taxonomy pressure: how many distinct raw labels are being collapsed into a smaller comparison set. This gives the next maintainer a measurable starting point for controlled vocabulary work without forcing a destructive historical rewrite.

`tools/build_evidence_receipts.py` now emits material-outcome-dimension counts and source-receipt-level counts. That turns the receipt surface into a prioritization tool: it can show whether the cube is accumulating receipt rows while still lacking money, debt, housing, stability, or passage-capture proof.

`tools/lint_archive.py` now checks that every receipt has material dimensions, a field-sample requirement, and a source-receipt level; that generated receipt summaries match metadata; and that generated source-health normalization output exists. This is bureaucracy only in the useful sense: it blocks false closure and reveals where the archive is overcounting.

## Route-demotion revalidation

Note `465` remains historical-preserved rather than active. Rev0788 updates its retirement review to the current release and points to this audit note because the source-health taxonomy-pressure output now absorbs the useful alias/categorization warning at a more concrete maintenance layer.

The route is still not deleted. It remains in the archive, manifest, source catalog, generated index, and hash surface. It should return to active status only if a future case needs it as first citation for alias-collision doctrine that the later evidence, source, and taxonomy routes do not preserve.

## What remains deliberately open

`GAP-029` remains open because no privacy-bounded claimant or household outcome sample exists in the cube.

`GAP-031` remains open because a source key plus section locator is not a captured passage, content fingerprint, or lawful archival receipt.

`GAP-033` moves to in progress but remains open because two material case signals do not yet amount to a theory of budgets, staffing, ownership, coercion, redistribution, or capture.

`GAP-030` remains in progress because normalized generated counts are not a controlled vocabulary and one demoted note is not a retirement system.

## Failure modes

- **Aggregate laundering:** a survey, observation, filing count, or representation percentage is treated as proof of completed person or household outcome.
- **Material substitution:** clear process evidence substitutes for money, debt relief, possession, re-housing, care, liberty, mobility, safety, or status.
- **Denominator capture:** only people who reached the official channel are counted.
- **Receipt inflation:** a better receipt floor is mistaken for a closure-ready floor.
- **Source locator theater:** a heading or page reference is treated as source preservation even though no passage capture or fingerprint exists.
- **Vocabulary theater:** normalized generated counts are treated as a cleaned taxonomy before owner-approved vocabulary rules exist.
- **Demotion drift:** historical-preserved status is not periodically rechecked against active dependencies.

## Anti-theater tests

1. Pick a UI receipt. Can it show money or debt state after cure, not only burden, status, or feedback?
2. Pick a housing receipt. Can it show possession, displacement, shelter/re-housing, and durable stability, not only filing or representation?
3. Pick a receipt with an aggregate proof floor. Does it still block `GAP-029`, `GAP-031`, and `GAP-033`?
4. Pick a material-outcome dimension. Is there at least one receipt naming the real-world thing that should change?
5. Pick a source locator. Can the reader tell whether it is a key, section locator, passage capture, fingerprint, or archival receipt?
6. Pick the source-health generated surface. Does it show raw label pressure and normalized counts instead of hiding category sprawl?
7. Pick note `465`. Is it still preserved and hashable while remaining outside active routing?
8. Pick the gap ledger. Are field validation, source preservation, material outcome theory, and route/taxonomy work still live rather than paper-repaired?

## Source posture

Use the DOL claimant-observation and survey-design pages as evidence that direct claimant research can expose filing burden, staff-intervention points, and survey-denominator limits. Use the Digital Government Hub UI practice synthesis as external context, not as law. Use NYC OCJ, NYC Comptroller, and Eviction Lab right-to-counsel and filing sources as aggregate household and program-implementation signals, not as household-tail validation. None of these sources closes a live gap by itself.
