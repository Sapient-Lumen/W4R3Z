# ARCHIVE INDEX

For fastest human entry, open [`START_HERE.md`](START_HERE.md). For grouped human browsing after that, stay in [`ARCHIVE_INDEX.md`](ARCHIVE_INDEX.md). For fastest machine entry, open the top-level `entry_surfaces` object inside [`ARCHIVE_INDEX.json`](ARCHIVE_INDEX.json), then the top-level `compact_named_routes` object for the self-contained shortest named paths and compact `use_when` route-choice cues, then use `machine_front_door` for the richer routing map; after that, follow the declared fallback order: `START_HERE.md` for the shortest answer read, then `ARCHIVE_INDEX.md` for grouped human browsing, and only then `README.md` as the revision-aware release shell.

Use `ARCHIVE_INDEX.md` for grouped human browsing rather than first-pass answer entry. Use the authoritative machine surfaces in `ARCHIVE_INDEX.json` for the landing map, self-contained compact short-route surface, compact `use_when` route-choice cues, route arrays, route meanings, file-entry field meanings, the now-explicit `human_front_door` versus `machine_front_door` status split, front-door operator metadata, revision-memory routing, retained-ledger scope, chronology-order truth, and explicit JSON Pointer refs between those machine-facing surfaces. Exact current-bundle change detail belongs in [`REVISION-RECEIPT.json`](REVISION-RECEIPT.json), while retained recent revision memory belongs in [`CHANGELOG.md`](CHANGELOG.md), so this human index can stay generic rather than carrying a revision-specific mini-changelog.

## Canonical route summaries

The archive's compact **front-door operator kit** lives in [`docs/20-program/ideal-distribution-and-policy-portfolio.md`](docs/20-program/ideal-distribution-and-policy-portfolio.md). Human entry notes should point there and to the authoritative machine-readable kit in [`ARCHIVE_INDEX.json`](ARCHIVE_INDEX.json) rather than repeatedly re-listing the full nine-block sequence unless order itself is the point. When they do enumerate the kit, they should mirror the declared **display_order**; the live reasoning sequence is still the note's **front-door use order** section and the machine-readable `operating_sequence`.

Exact ordered route arrays still live in the authoritative `routes` object in [`ARCHIVE_INDEX.json`](ARCHIVE_INDEX.json), and the four compact preferred routes now also appear as self-contained ordered arrays in the top-level `compact_named_routes` object together with compact `use_when` route-choice cues. The bullets below keep the canonical route names but are intentionally summary-level for human browsing rather than full route-array duplicates.

- **direct_answer** — [`docs/20-program/ideal-distribution-and-policy-portfolio.md`](docs/20-program/ideal-distribution-and-policy-portfolio.md) → [`docs/20-program/opening-package-router.md`](docs/20-program/opening-package-router.md) → [`docs/20-program/package-choice-and-tie-break-rules.md`](docs/20-program/package-choice-and-tie-break-rules.md) → [`docs/20-program/transition-sequencing.md`](docs/20-program/transition-sequencing.md)
- **implementation_core** — [`docs/20-program/ideal-distribution-and-policy-portfolio.md`](docs/20-program/ideal-distribution-and-policy-portfolio.md) → [`docs/20-program/opening-package-router.md`](docs/20-program/opening-package-router.md) → [`docs/20-program/package-choice-and-tie-break-rules.md`](docs/20-program/package-choice-and-tie-break-rules.md) → [`docs/20-program/minimum-viable-implementation-stack.md`](docs/20-program/minimum-viable-implementation-stack.md) → [`docs/20-program/transition-sequencing.md`](docs/20-program/transition-sequencing.md)
- **prevention_response** — [`docs/20-program/ideal-distribution-and-policy-portfolio.md`](docs/20-program/ideal-distribution-and-policy-portfolio.md) → [`docs/20-program/mode-selection-and-escalation-heuristic.md`](docs/20-program/mode-selection-and-escalation-heuristic.md) → [`docs/20-program/prevention-and-response-doctrine.md`](docs/20-program/prevention-and-response-doctrine.md) → [`docs/20-program/transition-sequencing.md`](docs/20-program/transition-sequencing.md)
- **certification_core** — [`docs/20-program/ideal-distribution-and-policy-portfolio.md`](docs/20-program/ideal-distribution-and-policy-portfolio.md) → [`docs/20-program/measurement-and-scoreboard.md`](docs/20-program/measurement-and-scoreboard.md) → [`docs/10-framework/constitutional-verdicts-for-wealth-orders.md`](docs/10-framework/constitutional-verdicts-for-wealth-orders.md) → [`docs/20-program/mode-selection-and-escalation-heuristic.md`](docs/20-program/mode-selection-and-escalation-heuristic.md)
- **core_spine** — full framework-to-program backbone from [`docs/10-framework/immoral-wealth-inequality.md`](docs/10-framework/immoral-wealth-inequality.md) through [`docs/20-program/mode-selection-and-escalation-heuristic.md`](docs/20-program/mode-selection-and-escalation-heuristic.md); use `ARCHIVE_INDEX.json` for the exact ordered array.
- **case_work_core** — full case-work and cross-case learning path from [`docs/20-program/case-work-decision-path.md`](docs/20-program/case-work-decision-path.md) through [`docs/20-program/pattern-consequence-routing-and-revision-targets.md`](docs/20-program/pattern-consequence-routing-and-revision-targets.md); use `ARCHIVE_INDEX.json` for the exact ordered array.
- **archive_governance_core** — full archive-governance path from [`docs/00-meta/research-triage-and-closure-rules.md`](docs/00-meta/research-triage-and-closure-rules.md) through [`docs/00-meta/archive-policy.md`](docs/00-meta/archive-policy.md); use `ARCHIVE_INDEX.json` for the exact ordered array.
- **source_governance_core** — full source-governance path from [`docs/00-meta/source-function-map-and-coverage-gaps.md`](docs/00-meta/source-function-map-and-coverage-gaps.md) through [`SOURCES.json`](SOURCES.json); use `ARCHIVE_INDEX.json` for the exact ordered array.

## Human entry surfaces

- [`START_HERE.md`](START_HERE.md) — shortest human direct-answer entry
- [`ARCHIVE_INDEX.md`](ARCHIVE_INDEX.md) — grouped human browsing index and route summaries
- [`README.md`](README.md) — revision-aware release shell and top-level route map

## Machine and integrity surfaces

- [`ARCHIVE_INDEX.json`](ARCHIVE_INDEX.json) — authoritative machine landing map and routing surface, with the file catalog now distinguishing `machine_front_door` from the three `human_front_door` entry notes
- [`REVISION-RECEIPT.json`](REVISION-RECEIPT.json) — exact current-bundle receipt
- [`CHANGELOG.md`](CHANGELOG.md) — thin retained recent revision ledger
- [`SOURCES.md`](SOURCES.md) — human-readable source ledger
- [`SOURCES.json`](SOURCES.json) — machine-readable source ledger
- [`MANIFEST.json`](MANIFEST.json) — structured released-file inventory
- [`MANIFEST.sha256`](MANIFEST.sha256) — checksum ledger for released files
- [`VERSION`](VERSION) — current revision tag

## docs/00-meta

- [`docs/00-meta/archive-growth-budgets-and-refactor-triggers.md`](docs/00-meta/archive-growth-budgets-and-refactor-triggers.md) — Archive growth budgets and refactor triggers *(active bridge)*
- [`docs/00-meta/archive-policy.md`](docs/00-meta/archive-policy.md) — Archive policy *(live anchor; canonical)*
- [`docs/00-meta/canonical-anchors-and-bridge-note-discipline.md`](docs/00-meta/canonical-anchors-and-bridge-note-discipline.md) — Canonical anchors and bridge-note discipline *(active bridge)*
- [`docs/00-meta/case-to-doctrine-promotion-and-quarantine.md`](docs/00-meta/case-to-doctrine-promotion-and-quarantine.md) — Case-to-doctrine promotion and quarantine *(active bridge)*
- [`docs/00-meta/charter.md`](docs/00-meta/charter.md) — Charter *(support)*
- [`docs/00-meta/claim-kinds-and-revision-burdens.md`](docs/00-meta/claim-kinds-and-revision-burdens.md) — Claim kinds and revision burdens *(active bridge)*
- [`docs/00-meta/doctrine-precedence-and-conflict-repair.md`](docs/00-meta/doctrine-precedence-and-conflict-repair.md) — Doctrine precedence and conflict repair *(active bridge)*
- [`docs/00-meta/doctrine-revision-and-demotion-under-case-pressure.md`](docs/00-meta/doctrine-revision-and-demotion-under-case-pressure.md) — Doctrine revision and demotion under case pressure *(active bridge)*
- [`docs/00-meta/note-status-and-supersession-discipline.md`](docs/00-meta/note-status-and-supersession-discipline.md) — Note status and supersession discipline *(active bridge)*
- [`docs/00-meta/preferred-terms-and-alias-map.md`](docs/00-meta/preferred-terms-and-alias-map.md) — Preferred terms and alias map *(active bridge)*
- [`docs/00-meta/release-readiness-and-bundle-integrity-checks.md`](docs/00-meta/release-readiness-and-bundle-integrity-checks.md) — Release readiness and bundle-integrity checks *(active bridge)*
- [`docs/00-meta/research-questions.md`](docs/00-meta/research-questions.md) — Research questions *(question ledger)*
- [`docs/00-meta/research-triage-and-closure-rules.md`](docs/00-meta/research-triage-and-closure-rules.md) — Research triage and closure rules *(active bridge)*
- [`docs/00-meta/revision-chronology-and-bundle-naming-discipline.md`](docs/00-meta/revision-chronology-and-bundle-naming-discipline.md) — Revision chronology and bundle-naming discipline *(active bridge)*
- [`docs/00-meta/source-function-map-and-coverage-gaps.md`](docs/00-meta/source-function-map-and-coverage-gaps.md) — Source-function map and coverage-gap discipline *(active bridge)*
- [`docs/00-meta/source-refresh-and-citation-compression.md`](docs/00-meta/source-refresh-and-citation-compression.md) — Source refresh and citation compression *(active bridge)*
- [`docs/00-meta/term-discipline-and-synonym-control.md`](docs/00-meta/term-discipline-and-synonym-control.md) — Term discipline and synonym control *(active bridge)*
## docs/10-framework

- [`docs/10-framework/acceptable-envelopes-and-substitution-limits.md`](docs/10-framework/acceptable-envelopes-and-substitution-limits.md) — Acceptable envelopes and substitution limits *(support)*
- [`docs/10-framework/anti-averaging-and-constitutional-vetoes.md`](docs/10-framework/anti-averaging-and-constitutional-vetoes.md) — Anti-averaging and constitutional vetoes *(support)*
- [`docs/10-framework/asset-composition-and-control.md`](docs/10-framework/asset-composition-and-control.md) — Asset composition and control constraints *(support)*
- [`docs/10-framework/asymmetric-tradeoffs-and-no-regret-priorities.md`](docs/10-framework/asymmetric-tradeoffs-and-no-regret-priorities.md) — Asymmetric tradeoffs and no-regret priorities *(support)*
- [`docs/10-framework/burden-of-proof-under-opacity-and-uncertainty.md`](docs/10-framework/burden-of-proof-under-opacity-and-uncertainty.md) — Burden of proof under opacity and uncertainty *(support)*
- [`docs/10-framework/carrying-costs-and-self-eroding-footholds.md`](docs/10-framework/carrying-costs-and-self-eroding-footholds.md) — Carrying costs and self-eroding footholds *(support)*
- [`docs/10-framework/claimability-take-up-and-administrative-friction.md`](docs/10-framework/claimability-take-up-and-administrative-friction.md) — Claimability, take-up, and administrative friction *(support)*
- [`docs/10-framework/claimant-load-and-per-person-adequacy.md`](docs/10-framework/claimant-load-and-per-person-adequacy.md) — Claimant load and per-person adequacy *(support)*
- [`docs/10-framework/constitutional-verdicts-for-wealth-orders.md`](docs/10-framework/constitutional-verdicts-for-wealth-orders.md) — Constitutional verdicts for wealth orders *(live anchor; canonical)*
- [`docs/10-framework/defensible-claims-and-title-security.md`](docs/10-framework/defensible-claims-and-title-security.md) — Defensible claims and title security *(support)*
- [`docs/10-framework/downside-discipline-and-loss-bearing.md`](docs/10-framework/downside-discipline-and-loss-bearing.md) — Downside discipline and loss-bearing *(support)*
- [`docs/10-framework/durability-windows-and-ratchet-tests.md`](docs/10-framework/durability-windows-and-ratchet-tests.md) — Durability windows and ratchet tests *(support)*
- [`docs/10-framework/encumbrance-and-debt-quality.md`](docs/10-framework/encumbrance-and-debt-quality.md) — Encumbrance and debt quality *(support)*
- [`docs/10-framework/floor-pass-rates-and-cohort-guardrails.md`](docs/10-framework/floor-pass-rates-and-cohort-guardrails.md) — Floor pass rates and cohort guardrails *(support)*
- [`docs/10-framework/forced-self-insurance-and-private-buffer-coercion.md`](docs/10-framework/forced-self-insurance-and-private-buffer-coercion.md) — Forced self-insurance and private buffer coercion *(support)*
- [`docs/10-framework/gatekeeper-dependence-and-unilateral-interruption-risk.md`](docs/10-framework/gatekeeper-dependence-and-unilateral-interruption-risk.md) — Gatekeeper dependence and unilateral interruption risk *(support)*
- [`docs/10-framework/group-stratification-and-excluded-groups.md`](docs/10-framework/group-stratification-and-excluded-groups.md) — Group stratification and excluded groups *(support)*
- [`docs/10-framework/ideal-wealth-distribution-bands.md`](docs/10-framework/ideal-wealth-distribution-bands.md) — Ideal wealth distribution bands *(support)*
- [`docs/10-framework/immoral-wealth-inequality.md`](docs/10-framework/immoral-wealth-inequality.md) — Immoral wealth inequality *(live anchor; canonical)*
- [`docs/10-framework/individual-ownership-and-intra-household-power.md`](docs/10-framework/individual-ownership-and-intra-household-power.md) — Individual ownership and intra-household power *(support)*
- [`docs/10-framework/intergenerational-circulation.md`](docs/10-framework/intergenerational-circulation.md) — Intergenerational circulation *(support)*
- [`docs/10-framework/intermediated-ownership-and-stewardship.md`](docs/10-framework/intermediated-ownership-and-stewardship.md) — Intermediated ownership and stewardship concentration *(support)*
- [`docs/10-framework/life-course-timing-and-early-footholds.md`](docs/10-framework/life-course-timing-and-early-footholds.md) — Life-course timing and early footholds *(support)*
- [`docs/10-framework/marginal-incidence-and-direction-of-change.md`](docs/10-framework/marginal-incidence-and-direction-of-change.md) — Marginal incidence and direction of change *(support)*
- [`docs/10-framework/minimum-asset-floor.md`](docs/10-framework/minimum-asset-floor.md) — Minimum asset floor *(live anchor; canonical)*
- [`docs/10-framework/non-extractive-wealth-formation.md`](docs/10-framework/non-extractive-wealth-formation.md) — Non-extractive wealth formation *(support)*
- [`docs/10-framework/ordinary-comprehensibility-and-low-expertise-operability.md`](docs/10-framework/ordinary-comprehensibility-and-low-expertise-operability.md) — Ordinary comprehensibility and low-expertise operability *(support)*
- [`docs/10-framework/portability-and-non-forfeiture-across-ordinary-transitions.md`](docs/10-framework/portability-and-non-forfeiture-across-ordinary-transitions.md) — Portability and non-forfeiture across ordinary transitions *(support)*
- [`docs/10-framework/present-accessibility-and-lock-up-of-claims.md`](docs/10-framework/present-accessibility-and-lock-up-of-claims.md) — Present accessibility, lock-up, and usable claims *(support)*
- [`docs/10-framework/promissory-offsets-and-backloaded-justice.md`](docs/10-framework/promissory-offsets-and-backloaded-justice.md) — Promissory offsets and backloaded justice *(support)*
- [`docs/10-framework/protected-footholds-and-anti-spend-down-traps.md`](docs/10-framework/protected-footholds-and-anti-spend-down-traps.md) — Protected footholds and anti-spend-down traps *(support)*
- [`docs/10-framework/protected-minima-and-anti-seizure-rules.md`](docs/10-framework/protected-minima-and-anti-seizure-rules.md) — Protected minima and anti-seizure rules *(support)*
- [`docs/10-framework/publicly-created-value-and-common-asset-capture.md`](docs/10-framework/publicly-created-value-and-common-asset-capture.md) — Publicly created value and common-asset capture *(support)*
- [`docs/10-framework/reconcentration-pressure.md`](docs/10-framework/reconcentration-pressure.md) — Reconcentration pressure *(support)*
- [`docs/10-framework/social-floor-and-private-wealth.md`](docs/10-framework/social-floor-and-private-wealth.md) — Social floor and private wealth *(support)*
- [`docs/10-framework/spatial-concentration-and-place-based-closure.md`](docs/10-framework/spatial-concentration-and-place-based-closure.md) — Spatial concentration and place-based closure *(support)*
- [`docs/10-framework/stress-tested-footholds-and-ordinary-shock-survivability.md`](docs/10-framework/stress-tested-footholds-and-ordinary-shock-survivability.md) — Stress-tested footholds and ordinary-shock survivability *(support)*
- [`docs/10-framework/target-selection-rules.md`](docs/10-framework/target-selection-rules.md) — Target selection rules *(live anchor; canonical)*
- [`docs/10-framework/upside-down-subsidies-and-the-hidden-wealth-state.md`](docs/10-framework/upside-down-subsidies-and-the-hidden-wealth-state.md) — Upside-down subsidies and the hidden wealth state *(support)*
- [`docs/10-framework/wealth-to-rule-conversion.md`](docs/10-framework/wealth-to-rule-conversion.md) — Wealth-to-rule conversion *(support)*
## docs/20-program

- [`docs/20-program/case-application-protocol.md`](docs/20-program/case-application-protocol.md) — Case application protocol *(active bridge)*
- [`docs/20-program/case-portfolio-caps-and-retirement.md`](docs/20-program/case-portfolio-caps-and-retirement.md) — Case-portfolio caps and retirement *(support)*
- [`docs/20-program/case-portfolio-triage-and-memo-selection.md`](docs/20-program/case-portfolio-triage-and-memo-selection.md) — Case-portfolio triage and memo selection *(support)*
- [`docs/20-program/case-staleness-and-recertification.md`](docs/20-program/case-staleness-and-recertification.md) — Case staleness and recertification *(active bridge)*
- [`docs/20-program/case-work-decision-path.md`](docs/20-program/case-work-decision-path.md) — Case-work decision path *(live anchor; canonical)*
- [`docs/20-program/comparison-set-selection-and-non-comparability.md`](docs/20-program/comparison-set-selection-and-non-comparability.md) — Comparison-set selection and non-comparability *(active bridge)*
- [`docs/20-program/confidence-labels-and-action-under-proof-debt.md`](docs/20-program/confidence-labels-and-action-under-proof-debt.md) — Confidence labels and action under proof debt *(support)*
- [`docs/20-program/counterarguments-and-failure-modes.md`](docs/20-program/counterarguments-and-failure-modes.md) — Counterarguments and failure modes *(support)*
- [`docs/20-program/country-pathways.md`](docs/20-program/country-pathways.md) — Country pathways *(support)*
- [`docs/20-program/cross-case-decision-path.md`](docs/20-program/cross-case-decision-path.md) — Cross-case decision path *(active bridge)*
- [`docs/20-program/cross-case-application-protocol.md`](docs/20-program/cross-case-application-protocol.md) — Cross-case application protocol *(active bridge)*
- [`docs/20-program/cross-case-comparison-and-pattern-extraction.md`](docs/20-program/cross-case-comparison-and-pattern-extraction.md) — Cross-case comparison and pattern extraction *(active bridge)*
- [`docs/20-program/pattern-consequence-routing-and-revision-targets.md`](docs/20-program/pattern-consequence-routing-and-revision-targets.md) — Pattern consequence routing and revision targets *(active bridge)*
- [`docs/20-program/pattern-confidence-and-export-burdens.md`](docs/20-program/pattern-confidence-and-export-burdens.md) — Pattern confidence and export burdens *(active bridge)*
- [`docs/20-program/pattern-deviant-cases-and-anomaly-handling.md`](docs/20-program/pattern-deviant-cases-and-anomaly-handling.md) — Pattern deviant cases and anomaly handling *(active bridge)*
- [`docs/20-program/distributional-budgeting-and-state-capacity.md`](docs/20-program/distributional-budgeting-and-state-capacity.md) — Distributional budgeting and state capacity *(support)*
- [`docs/20-program/dominant-breach-and-fastest-washout-selection.md`](docs/20-program/dominant-breach-and-fastest-washout-selection.md) — Dominant breach and fastest washout selection *(active bridge)*
- [`docs/20-program/emergency-exceptions-sunsets-and-repair-duties.md`](docs/20-program/emergency-exceptions-sunsets-and-repair-duties.md) — Emergency exceptions, sunsets, and repair duties *(support)*
- [`docs/20-program/hardening-gains-into-ratchets.md`](docs/20-program/hardening-gains-into-ratchets.md) — Hardening gains into ratchets *(support)*
- [`docs/20-program/housing-land-and-anti-monopoly.md`](docs/20-program/housing-land-and-anti-monopoly.md) — Housing, land, and anti-monopoly *(support)*
- [`docs/20-program/ideal-distribution-and-policy-portfolio.md`](docs/20-program/ideal-distribution-and-policy-portfolio.md) — Ideal distribution and policy portfolio *(live anchor; canonical)*
- [`docs/20-program/jurisdictional-mobility-and-anti-blackmail-rules.md`](docs/20-program/jurisdictional-mobility-and-anti-blackmail-rules.md) — Jurisdictional mobility and anti-blackmail rules *(support)*
- [`docs/20-program/measurement-and-scoreboard.md`](docs/20-program/measurement-and-scoreboard.md) — Measurement and scoreboard *(live anchor; canonical)*
- [`docs/20-program/minimum-evidence-pack-for-case-work.md`](docs/20-program/minimum-evidence-pack-for-case-work.md) — Minimum evidence pack for case work *(active bridge)*
- [`docs/20-program/minimum-viable-implementation-stack.md`](docs/20-program/minimum-viable-implementation-stack.md) — Minimum viable implementation stack *(support)*
- [`docs/20-program/mode-selection-and-escalation-heuristic.md`](docs/20-program/mode-selection-and-escalation-heuristic.md) — Mode selection and escalation heuristic *(live anchor; canonical)*
- [`docs/20-program/next-scoreboard-and-evidence-debt-selection.md`](docs/20-program/next-scoreboard-and-evidence-debt-selection.md) — Next scoreboard and evidence-debt selection *(active bridge)*
- [`docs/20-program/opening-package-router.md`](docs/20-program/opening-package-router.md) — Opening package router *(active bridge)*
- [`docs/20-program/package-choice-and-tie-break-rules.md`](docs/20-program/package-choice-and-tie-break-rules.md) — Package choice and tie-break rules *(active bridge)*
- [`docs/20-program/package-monitoring-and-reroute-triggers.md`](docs/20-program/package-monitoring-and-reroute-triggers.md) — Package monitoring and reroute triggers *(support)*
- [`docs/20-program/pattern-rival-explanations-and-disconfirmation.md`](docs/20-program/pattern-rival-explanations-and-disconfirmation.md) — Pattern rival explanations and disconfirmation *(active bridge)*
- [`docs/20-program/pattern-portability-and-transfer-limits.md`](docs/20-program/pattern-portability-and-transfer-limits.md) — Pattern portability and transfer limits *(active bridge)*
- [`docs/20-program/pattern-saturation-and-stopping-rules.md`](docs/20-program/pattern-saturation-and-stopping-rules.md) — Pattern saturation and stopping rules *(active bridge)*
- [`docs/20-program/pattern-null-results-and-parking-rules.md`](docs/20-program/pattern-null-results-and-parking-rules.md) — Pattern null results and parking rules *(active bridge)*
- [`docs/20-program/political-firewalls-against-wealth-rule.md`](docs/20-program/political-firewalls-against-wealth-rule.md) — Political firewalls against wealth rule *(support)*
- [`docs/20-program/predistribution-labor-and-wages.md`](docs/20-program/predistribution-labor-and-wages.md) — Predistribution: labor and wages *(support)*
- [`docs/20-program/prevention-and-response-doctrine.md`](docs/20-program/prevention-and-response-doctrine.md) — Prevention and response doctrine *(live anchor; canonical)*
- [`docs/20-program/provisional-passes-and-reopening-triggers.md`](docs/20-program/provisional-passes-and-reopening-triggers.md) — Provisional passes and reopening triggers *(support)*
- [`docs/20-program/review-cadence-and-durability-window-selection.md`](docs/20-program/review-cadence-and-durability-window-selection.md) — Review cadence and durability-window selection *(active bridge)*
- [`docs/20-program/social-inheritance-public-wealth-and-baby-bonds.md`](docs/20-program/social-inheritance-public-wealth-and-baby-bonds.md) — Social inheritance, public wealth, and baby bonds *(support)*
- [`docs/20-program/source-order-and-conflict-resolution.md`](docs/20-program/source-order-and-conflict-resolution.md) — Source order and conflict resolution *(active bridge)*
- [`docs/20-program/tax-capital-gains-inheritance-and-wealth.md`](docs/20-program/tax-capital-gains-inheritance-and-wealth.md) — Taxing capital, gains, inheritance, and wealth *(support)*
- [`docs/20-program/tax-expenditures-and-subsidy-hygiene.md`](docs/20-program/tax-expenditures-and-subsidy-hygiene.md) — Tax expenditures and subsidy hygiene *(support)*
- [`docs/20-program/transition-sequencing.md`](docs/20-program/transition-sequencing.md) — Transition sequencing *(active bridge)*
- [`docs/20-program/wealth-legibility-registries-and-enforcement.md`](docs/20-program/wealth-legibility-registries-and-enforcement.md) — Wealth legibility, registries, and enforcement *(support)*
## docs/90-open

- [`docs/90-open/open-questions.md`](docs/90-open/open-questions.md) — Open questions *(question ledger)*
