# rev0188 — `exposurerisk`

Timestamp: `2026.05.25.00.00 UTC`

## Added

- `31-exposure-liability-lifecycle.md`
- `32-exposure-refactor-report.md`
- `33-exposure-state-vocabulary.md`
- `02-dossiers/coverage-position-state-labels-become-operational-control-planes.md`
- `02-dossiers/indemnity-pass-through-maps-become-supply-chain-risk-infrastructure.md`
- `02-dossiers/subrogation-evidence-packets-become-incident-response-artifacts.md`
- `02-dossiers/reserve-release-evidence-becomes-capital-governance-infrastructure.md`
- `02-dossiers/self-insured-retention-thresholds-become-operational-control-points.md`

## Changed

- Refactored the exposure / liability / insurance / underwriting family into a lifecycle with normalized states.
- Tagged 31 existing dossiers with exposure roles, stages, and state terms.
- Added exposure audit, lifecycle map, state lexicon, and risk-transfer clause index files under `INDEX/`.
- Rebuilt dossier index, decision-grade scores, graph audit, and schema values.

## Conceptual move

Exposure is not merely risk. Exposure is a stateful financial control plane: allocation, attachment, conditions, trigger, notice, defense, reserve, payment, erosion, recovery, renewal, and closure.

# Changelog

## rev0187 — 2026.05.25.00.00 UTC — lineagecustody

### Status
Focused audit/refactor revision. Converts the archive's scattered provenance, custody, transformation, resolver, traceability, and lineage material into a reusable state family.

### Added
- New framework files: `28-provenance-and-lineage-lifecycle.md`, `29-lineage-refactor-report.md`, and `30-lineage-state-vocabulary.md`.
- New dossiers:
  - `resolver-successor-maps-become-passport-continuity-infrastructure.md`
  - `transformation-replay-bundles-become-regulatory-audit-artifacts.md`
  - `derived-data-use-rights-become-ai-contract-boilerplate.md`
  - `provenance-diff-services-become-diligence-infrastructure.md`
  - `custody-break-certificates-become-litigation-and-assurance-artifacts.md`
- New index artifacts: `INDEX/lineage-family-audit.csv`, `INDEX/lineage-lifecycle-map.tsv`, `INDEX/lineage-state-lexicon.json`, `INDEX/lineage-refactor-actions.csv`, and `INDEX/custody-break-risk-register.csv`.
- New source entries: **[S1565]–[S1576]** covering W3C PROV, C2PA, OpenLineage, SLSA, in-toto, SPDX, GS1 Digital Link / resolver standards, and the European Commission DPP consultation.

### Changed
- Tagged the existing provenance/custody/lineage family with `refactor_cluster: provenance-lineage`, `lineage_role`, `lineage_stage`, and `state_family: provenance`.
- Rebuilt dossier index, graph, schema values, evidence audit, migration priority list, research watchlist, frontmatter coverage, and graph audit.
- Updated README, principles, cube, seed bank, constellations, schema, research signal ledger, operational index, and consolidation map.

### Design decisions
- Treated provenance as too broad to remain an undifferentiated quality label.
- Split lineage into subject binding, source capture, transform declaration, packaging, signature, resolver, disclosure, redaction, transfer, diff, replay, verification, dispute, correction, supersession, and archive stages.
- Promoted only missing mechanism surfaces: resolver continuity, transformation replay, derived-use rights, provenance diffs, and custody-break certificates.

### Next likely moves
- Refactor `scope / comparability / translation` next; it is now the most overloaded remaining vocabulary.
- Add a fallback/graceful-degradation model if live checks, resolvers, wallets, and registries continue to create outage and stale-if-error questions.
- Audit small-actor burden across product passports, EUDR, AI documentation, repair evidence, and delegated-authority systems.

# Changelog

## rev0183 — 2026.05.25.00.00 UTC — decisiongrade

### Status
Evidence/decision revision. Converts the archive's schema, graph, and adversarial vocabulary into a decision-grade audit layer: what is strongly evidenced, what is speculative, what should be watched, and what should eventually be consolidated.

### Added
- New framework files: `15-evidence-confidence-audit.md`, `16-decision-grade-rubric.md`, `17-transfer-atlas.md`, and `18-consolidation-and-overfit-map.md`.
- New dossiers:
  - `cryptographic-agility-registries-become-trust-transition-infrastructure.md`
  - `notified-body-queue-position-becomes-market-access-infrastructure.md`
  - `delegated-ai-agent-authority-logs-become-consumer-protection-infrastructure.md`
  - `data-space-access-rules-become-industrial-border-controls.md`
  - `provenance-nonparticipation-labels-become-media-trust-infrastructure.md`
- New index files: `decision-grade-scores.csv/json`, `evidence-audit.csv`, `transfer-atlas.tsv`, `taxonomy-merge-candidates.csv`, and `research-watchlist.csv`.
- New sources **[S1516]–[S1531]** covering PQC transition, AI Act transparency, C2PA provenance, common European data spaces, notified-body/EUDAMED surfaces, FTC impersonation rules, OpenAI agent tools, and NIST AI RMF material.

### Changed
- Backfilled minimal YAML front matter for 113 older dossiers, bringing front-matter coverage to 100% of dossier files.
- Rebuilt dossier index, graph, schema values, migration priority list, graph audit, and frontmatter coverage file.
- Updated README, principles, cube, seed bank, constellations, schema, research signal ledger, operational index, migration workbench, adversary matrix, and frontmatter report.

### Design decisions
- Treated rev0183 as an evidence audit rather than another pure expansion pass.
- Added new dossiers only where the audit exposed a missing institutional surface: cryptographic transition state, assessor queue capacity, delegated agent authority, data-space borders, and provenance absence semantics.
- Marked inferred front matter clearly so full metadata coverage improves navigation without pretending to be fully reviewed classification.
- Added consolidation guidance because future progress now requires pruning as much as expansion.

### Next likely moves
- Replace inferred metadata on top decision-grade dossiers with reviewed metadata.
- Consolidate freshness, successor, ranking, exception, and authoritative-rendering clusters.
- Deliberately test the decision-grade rubric outside managed legibility.
- Downgrade or merge DG-C/DG-D items after manual review.

## rev0182 — 2026.05.24.00.00 UTC — stressgraph

### Status
Structural stress-test revision; turns the operational index into a more adversarial datacube by adding attack vocabulary, product-biography lifecycle modeling, anti-legibility doctrine, graphfill, and broader front-matter coverage.

### Added
- New framework/model files: `11-adversary-falsifier-matrix.md`, `12-frontmatter-graphfill-report.md`, `13-product-biography-lifecycle.md`, and `14-anti-legibility-model.md`.
- New dossiers: `public-proof-profile-registries-become-verification-constitutions.md`, `graph-poisoning-becomes-a-standing-governance-attack-surface.md`, `resolver-capture-becomes-a-hidden-passport-bottleneck.md`, `informal-market-refuges-form-around-over-legible-infrastructure.md`, `redaction-boundary-ledgers-become-ai-assurance-controls.md`, and `recall-state-propagation-becomes-resale-market-infrastructure.md`.
- New index artifacts: `INDEX/adversary-matrix.csv`, `INDEX/product-biography-state-map.tsv`, `INDEX/frontmatter-coverage.json`, and `INDEX/graph-audit.json`.
- New source entries: **[S1504]–[S1515]**.

### Changed
- Rebuilt the dossier index after adding six dossiers and front-matter backfill.
- Expanded YAML front matter to 85 of 198 dossiers.
- Expanded the graph to 106 edges, spanning reliance-object lifecycle, validation/conformance, product biography, incident routing, authority checks, anti-legibility, and adversarial layers.
- Updated README, principles, cube, schema, seed bank, constellation map, research signal ledger, migration workbench, and revision manifest.

### Design decisions
- Chose a stressgraph release rather than another narrow packet-governance release because the archive needed a stronger adversarial and falsifier vocabulary.
- Treated proof-profile registries, resolver capture, graph poisoning, redaction boundaries, informal refuges, and recall propagation as stress tools that pressure-test existing dossiers.
- Added product biography as a lifecycle parallel to reliance-object governance so product passports, repair, recall, resale, and destruction can be reasoned about as state transitions rather than scattered examples.
- Kept older broad civilizational dossiers only lightly touched; the new front matter remains explicitly marked as inferred where it was not written during the original dossier promotion.

### Next likely moves
- Run an evidence audit on 20 high-impact dossiers and add source-confidence / staleness fields.
- Backfill front matter to at least 100 dossiers only after auditing whether the inferred fields are useful.
- Add graph edges for older civilizational fronts without forcing them into packet language.
- Consider promoting repair-event privacy profiles, refurbished-identity splits, software-update histories as used-product diligence, and proof-request overreach appeals.


## rev0181 — 2026.05.23.00.00 UTC — operationalindex

### Status
Structural-plus-frontier revision; makes the rev0180 schema operational by adding machine-readable indexes, a migration workbench, reviewed front matter for high-leverage recent dossiers, and five new dossiers that push the archive into adjacent proof-object domains.

### Added
- New framework file: `08-operational-index.md`.
- New framework file: `09-research-signal-ledger.md`.
- New framework file: `10-migration-workbench.md`.
- New index directory: `INDEX/`.
- New index file: `INDEX/dossier-index.csv`.
- New index file: `INDEX/dossier-index.json`.
- New index file: `INDEX/dossier-graph.tsv`.
- New index file: `INDEX/schema-values.json`.
- New index file: `INDEX/migration-priority.csv`.
- New dossier: `02-dossiers/small-supplier-evidence-brokers-become-market-access-infrastructure.md`.
- New dossier: `02-dossiers/grid-connection-queue-position-becomes-industrial-policy.md`.
- New dossier: `02-dossiers/repair-right-evidence-becomes-consumer-infrastructure.md`.
- New dossier: `02-dossiers/model-documentation-packets-become-ai-procurement-boilerplate.md`.
- New dossier: `02-dossiers/incident-report-routing-becomes-operational-resilience-infrastructure.md`.
- New source entries: **[S1494]–[S1503]**.

### Changed
- Updated README to describe the operational-index release and the new `INDEX/` layer.
- Backfilled YAML front matter for ten high-leverage recent reliance-object dossiers: transformation-code escrow, split/merge correction notices, amendment-recipient registries, correction-materiality thresholds, appeal-stay labels, and the five rev0180 corrective dossiers.
- Added YAML front matter to all five rev0181 dossiers.
- Added a research signal ledger connecting EU repair, Data Act, Digital Product Passport, AI Act/GPAI, interconnection queues, IEA data-center demand, SEC/CIRCIA incident reporting, NVD status-aware enrichment, W3C credentials, and C2PA provenance.
- Added a migration workbench that recommends frontmatter30 + graphfill as the next strongest move.
- Added graph TSV edges linking the new dossiers to product passports, packet lifecycle, queue governance, validation reports, source-witness nonresponse, and data-minimization layers.

### Design decisions
- Chose an operational-index release because rev0180 made the schema visible but not yet queryable. The archive now has an index broad enough for navigation while avoiding false precision in older dossiers.
- Promoted `small-supplier evidence brokers become market-access infrastructure` to correct the assumption that every actor can operate the new proof systems directly.
- Promoted `grid-connection queue position becomes industrial policy` because AI/data-center electricity demand, storage, and interconnection reform make queue position an allocation surface rather than a mere backlog.
- Promoted `repair-right evidence becomes consumer infrastructure` because a repair right is operational only when consumers and independent repairers can produce admissible evidence of access, refusal, repair, warranty status, and dispute.
- Promoted `model-documentation packets become AI procurement boilerplate` because AI governance is increasingly becoming a packet, annex, redaction, change-notice, and suitability problem.
- Promoted `incident-report routing becomes operational-resilience infrastructure` because incident reporting creates recipient-specific materiality clocks, update states, and correction-afterlife duties.

### Next likely moves
- Run a `frontmatter30` revision that annotates the 30 highest-priority dossiers from `INDEX/migration-priority.csv`.
- Run a `graphfill` revision that converts `07-graph-backbone.md` into a denser reviewed graph with at least 100 typed edges.
- Build a product-biography lifecycle model parallel to the reliance-object lifecycle.
- Promote public proof-profile registries, graph poisoning, informal-market refuge, or data-room escrow-access arbitration if the next session prioritizes anti-legibility and abuse paths.

## rev0180 — 2026.05.23.00.00 UTC — schemabones

### Status
Structural revision; turns the previous critique into a working next version by adding controlled schema, a reliance-object lifecycle model, typed graph edges, and five corrective dossiers that rebalance the archive toward nonresponse, privacy, non-reliance, fraud, and minimization.

### Added
- New framework file: `05-cube-schema.md`.
- New framework file: `06-reliance-object-lifecycle.md`.
- New framework file: `07-graph-backbone.md`.
- New dossier: `02-dossiers/source-witness-nonresponse-defaults-become-broker-policy.md`.
- New dossier: `02-dossiers/recipient-graph-privacy-proofs-become-broker-trust-products.md`.
- New dossier: `02-dossiers/non-reliance-packet-states-become-version-lifecycle-controls.md`.
- New dossier: `02-dossiers/compliance-object-forgery-becomes-organized-fraud-infrastructure.md`.
- New dossier: `02-dossiers/data-minimization-proofs-become-procurement-requirements.md`.
- New source entries: **[S1480]–[S1493]**.

### Changed
- Updated README to describe the schema-bones revision and the new archive map.
- Added two admission principles: prefer state transitions over noun proliferation, and require an abuse/burden pass.
- Added a controlled-cube operating note to `01-speculation-cube.md`, clarifying that the huge accumulated lists are now a primitive inventory rather than the finite cube axes.
- Rebuilt the seed bank around transfer rights, stay abuse, escrow-access arbitration, custody-failure scorecards, small-supplier evidence brokers, grid-connection queue position, repair-right evidence, identity-graph poisoning, and public proof-profile infrastructure.
- Added a constellation note that treats the new dossiers as corrective infrastructure rather than simply another managed-legibility run.
- Expanded sources with NIST NVD, EU Data Act, Cyber Resilience Act, DORA, Digital Product Passport, EUDR, EUDR Information System, IEA Energy and AI, W3C Verifiable Credentials, W3C BBS selective disclosure, NIST Privacy Framework, GS1 Digital Link, and EU Digital Identity Wallet privacy material.

### Design decisions
- Made the revision a schema release because the corpus had become strong but increasingly warehouse-like: the long substrate axis mixed domains, actors, artifacts, lifecycle stages, examples, and mini-theses.
- Promoted `source-witness nonresponse defaults become broker policy` because appeal and correction machinery fails unless silence, refusal, expired retention, and unverifiable source state become governed outcomes.
- Promoted `recipient-graph privacy proofs become broker trust products` because amendment and stay routing require reliance graphs, but full graph exposure leaks sensitive buyer, lender, insurer, counsel, platform, and regulator relationships.
- Promoted `non-reliance packet states become version lifecycle controls` because correction-materiality schedules need a terminal state for prior packet versions that are no longer admissible for specified reliance purposes.
- Promoted `compliance-object forgery becomes organized fraud infrastructure` because proof objects become attack surfaces once passports, due-diligence statements, validation reports, VEX assertions, stays, and non-reliance markers gate market access.
- Promoted `data-minimization proofs become procurement requirements` to correct the archive's legibility bias: mature governance often means proving enough while revealing less.

### Next likely moves
- Promote `reliance-right transfer notices become closing covenants` if amendment, appeal, stay, correction, and non-reliance rights start traveling through loan assignments, insurance novations, reinsurance, platform migrations, subcontracting, and asset sales.
- Develop `stay-label abuse filters become appeal-system infrastructure` if weak appeals are used to delay closing, force reserves, suspend eligibility, or manipulate score treatment.
- Develop `small-supplier evidence brokers become trade infrastructure` if product passports, EUDR, cyber attestations, and repair evidence begin excluding smaller suppliers without shared proof utilities.
- Open a cross-domain dossier on `grid-connection queue position becomes industrial policy` if AI/data-center electricity demand, storage, renewables, and industrial load make interconnection position the scarce asset.

## rev0179 — 2026.05.15.19.56 UTC — appealstays

### Status
Compact continuation revision; broadens the archive by promoting an appeal-stay-label thesis that sits between identity/materiality appeals and final correction-materiality consequences.

### Added
- New dossier: `02-dossiers/appeal-stay-labels-become-reliance-controls.md`.
- New source entries: **[S1467]–[S1479]**.

### Changed
- Updated README to reflect the new pending-appeal reliance-control layer and the rebuilt next queue.
- Rebuilt the seed bank around source-witness nonresponse defaults, recipient-graph privacy proofs, reliance-right transfer notices, stay-label abuse filters, escrow-access arbitration, custody-failure fault classes, and non-reliance packet states after promoting the appeal-stay thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include appeal-stay labels as the interim control layer that decides whether an appealed packet subject remains usable, score-excluded, holdback-reserved, manual-review-only, processing-restricted, eligibility-suspended, or non-reliance-pending.
- Extended the principles and Speculation Cube with stay-scope schedules, interim reliance controls, score-exclusion flags, holdback-reserve labels, manual-review-only states, processing-restricted states, stay-expiry timers, stay-propagation receipts, stay overrides, and stay-abuse filters.
- Expanded the source register with ICO/EDPB, U.S. Code/FCRA, Regulation V, FTC, FAR, GAO/eCFR, Federal Rules of Appellate and Civil Procedure, HL7 FHIR, Atlassian Jira, GitLab, and CycloneDX material on processing restriction, disputed-information labeling, direct-dispute outcomes, protest stays, appeal stays, automatic judgment stays, task/workflow status, blocked relations, and contextual vulnerability status.

### Design decisions
- Promoted `appeal-stay labels become reliance controls` because the archive had just added correction-materiality schedules, but still lacked the machine-readable interim state that governs packet use while an identity or materiality appeal is pending.
- Treated the key bottleneck as **interim reliance authority** — not whether an appeal ultimately succeeds, but whether downstream systems may continue automated use, must route to manual review, must exclude disputed subjects from scores, must reserve money, or must suspend eligibility before the merits are decided.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because appeal-stay labels are the operational bridge between identity-match appeal queues, amendment-recipient registries, correction-materiality schedules, and non-reliance packet states.

### Next likely moves
- Watch `source-witness nonresponse defaults become broker policy` as stay decisions start depending on native vendors, source owners, data-room custodians, and system administrators that may not answer inside transaction windows.
- Track `recipient-graph privacy proofs become broker trust products` if brokers must prove stay routing and appeal standing without exposing every buyer-side insurer, lender, auditor, counsel, or platform user.
- Test `reliance-right transfer notices become closing covenants` if appeal, stay, amendment, and materiality-review rights begin traveling through asset sales, loan assignments, insurance novations, reinsurance, subcontracting, and platform migrations.
- Develop `stay-label abuse filters become appeal-system infrastructure` if weak appeals start being used to block scores, delay holdback releases, suspend eligibility, or force manual review for leverage.

## rev0178 — 2026.05.15.19.50 UTC — correctionmateriality

### Status
Compact continuation revision; broadens the archive by promoting a correction-materiality thesis that sits downstream of identity-match appeals and turns packet corrections into consequence classes rather than undifferentiated edits.

### Added
- New dossier: `02-dossiers/correction-materiality-thresholds-become-packet-boilerplate.md`.
- New source entries: **[S1454]–[S1466]**.

### Changed
- Updated README to reflect the new correction-materiality layer and the rebuilt next queue.
- Rebuilt the seed bank around appeal-stay labels, source-witness nonresponse defaults, recipient-graph privacy proofs, reliance-right transfer notices, escrow-access arbitration, custody-failure fault classes, and non-reliance packet states after promoting the correction-materiality thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include correction-materiality schedules as the grammar that decides whether a sustained correction is hygiene, record-only, disclosure-only, amended-packet, score-restatement, notice-triggering, covenant-impacting, holdback-reopening, eligibility-changing, or non-reliance.
- Extended the principles and Speculation Cube with materiality-class schedules, score-delta triggers, severity-band crossings, denominator-change thresholds, cumulative immateriality, qualitative trigger fields, reliance-purpose-specific materiality, materiality-label appealability, and recipient routing by correction class.
- Expanded the source register with SEC, PCAOB, Federal Rules of Civil Procedure, GDPR, Regulation V, NVD, FIRST CVSS, FedRAMP, and FDA/eCFR material on materiality, non-reliance, disclosure correction, harmlessness, risk-tiered notification, dispute determinations, severity thresholds, significant-change notifications, and reportable versus record-only corrections.

### Design decisions
- Promoted `correction-materiality thresholds become packet boilerplate` because the archive had just added identity-match appeals, but still lacked the consequence grammar for deciding when a corrected packet merely records a fix, when it must notify recipients, and when it reopens reliance, money, eligibility, or non-reliance.
- Treated the key bottleneck as **consequence classification after correction** — not whether the correction is true, but whether it changes a score, denominator, status, notice class, reliance purpose, warranty cap, covenant, holdback, or eligibility screen enough to require a stronger packet event.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because materiality schedules are the operational sequel to source-object identity warranties, split/merge correction notices, amendment-recipient registries, and identity-match appeals.

### Next likely moves
- Develop `appeal-stay labels become reliance controls` if pending identity or materiality appeals need standardized interim states such as usable, score-excluded, holdback-reserved, disclosure-only, manual-review-only, or processing-restricted.
- Watch `source-witness nonresponse defaults become broker policy` as appeals start depending on native vendors, source owners, data-room custodians, and system administrators that may not answer inside transaction windows.
- Track `recipient-graph privacy proofs become broker trust products` if brokers must prove appeal standing, notice scope, and materiality-class routing without exposing every buyer-side relying party.
- Test `reliance-right transfer notices become closing covenants` if amendment, appeal, and materiality-review rights begin traveling through asset sales, loan assignments, insurance novations, reinsurance, subcontracting, and platform migrations.

## rev0177 — 2026.05.15.19.13 UTC — matchappeals

### Status
Compact continuation revision; broadens the archive by promoting an identity-match-appeal thesis that sits downstream of source-object identity warranties, split/merge correction notices, transform escrow, and amendment-recipient registries.

### Added
- New dossier: `02-dossiers/identity-match-appeals-become-broker-support-queues.md`.
- New source entries: **[S1440]–[S1453]**.

### Changed
- Updated README to reflect the new identity-appeal layer and the rebuilt next queue.
- Rebuilt the seed bank around correction-materiality thresholds, appeal-stay labels, source-witness nonresponse defaults, recipient-graph privacy proofs, reliance-right transfer notices, escrow-access arbitration, and custody-failure fault classes after promoting the identity-match-appeal thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include identity-match appeal queues as the redress front door for disputed source-object joins, false splits, duplicate reversals, stale remaps, unjoined near-matches, and recipient-scope mistakes.
- Extended the principles and Speculation Cube with appeal standing, challenged canonical subjects, disputed-match interim labels, source-witness response logs, false-join and false-split case files, appeal outcome codes, statement-of-disagreement packets, and amendment-triggering appeal results.
- Expanded the source register with ONC, HL7 FHIR, IHE PIXm, CVE Program, CFPB, EU GDPR, GitHub, Atlassian Jira, and GitLab material on cross-organizational matching, duplicate/linkage correction, cross-reference managers, dispute procedures, direct-dispute investigations, recipient notification after rectification, alert reopening, duplicate issue links, and linked-issue relation management.

### Design decisions
- Promoted `identity-match appeals become broker support queues` because the archive had just created amendment-recipient registries, but still lacked the challenge path through which buyers, sellers, insurers, lenders, platforms, source owners, and recipients can contest the object and recipient identity decisions that determine packet meaning.
- Treated the key bottleneck as **redress for canonical-subject decisions** — not merely whether a broker can amend a packet, but whether the parties affected by a join, split, duplicate reversal, stale remap, or recipient-scope decision can file evidence, obtain an interim label, get a reasoned outcome, and trigger downstream amendment routing.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because identity appeals are the operational sequel to source-object identity warranties, transform-code escrow, split/merge correction notices, and amendment-recipient registries.

### Next likely moves
- Develop `correction-materiality thresholds become packet boilerplate` if markets need cleaner boundaries between hygiene corrections, notice-class escalation, score restatements, holdback reopeners, covenant events, and eligibility changes.
- Test `appeal-stay labels become reliance controls` if pending challenges start affecting whether a packet subject remains usable, score-excluded, holdback-reserved, manual-review-only, or processing-restricted.
- Watch `source-witness nonresponse defaults become broker policy` as appeals begin depending on native vendors, source owners, and data-room custodians that may not respond inside transaction windows.
- Track `recipient-graph privacy proofs become broker trust products` if brokers must prove appeal standing and amendment-recipient scope without revealing every buyer-side relying party.

## rev0176 — 2026.05.15.18.34 UTC — recipientgraph

### Status
Compact continuation revision; broadens the archive by promoting an amendment-recipient-registry thesis that sits downstream of split/merge correction notices and turns packet amendment delivery into reliance-graph infrastructure.

### Added
- New dossier: `02-dossiers/amendment-recipient-registries-become-reliance-graph-infrastructure.md`.
- New source entries: **[S1427]–[S1439]**.

### Changed
- Updated README to reflect the new recipient-graph layer and the rebuilt next queue.
- Rebuilt the seed bank around identity-match appeals, correction-materiality thresholds, reliance-right transfer notices, recipient-graph privacy proofs, escrow-access arbitration, and custody-failure fault classes after promoting the amendment-recipient thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include amendment-recipient registries as the routing substrate that decides who is entitled to receive which packet amendment, under which reliance purpose, endpoint, delegate, and residual post-expiry right.
- Extended the principles and Speculation Cube with recipient capacity, reliance grants, notice-class filters, delegated endpoints, subscriber leases, stream configuration, recipient-scope proofs, over-notice liability, downstream-forwarding duties, successor-recipient rules, and stale-recipient repair.
- Expanded the source register with HL7 FHIR, W3C WebSub, OpenID Shared Signals, IETF SET delivery, CloudEvents, FHIR Consent, OASIS XACML, Federal Rules of Civil Procedure, E-SIGN, and OSCAL material on event subscriptions, topic filters, endpoints, stream IDs, push/poll delivery, acknowledgements, purpose-bound recipient rights, service channels, electronic-record consent, and role/party graphs.

### Design decisions
- Promoted `amendment-recipient registries become reliance-graph infrastructure` because the archive had just added packet amendment notices, but still lacked the durable routing substrate required to know who relied on which packet version, for which purpose, through which delegate or platform, and with which amendment entitlement.
- Treated the key bottleneck as **recipient entitlement after correction** — not merely whether a correction notice was produced, but whether it reached the legally and economically relevant class of recipients without leaking to the wrong parties or missing expired-but-still-entitled ones.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because recipient registries are the operational sequel to delivery attestations, delegate freshness, propagation budgets, source-object identity warranties, transform escrow, and split/merge amendment notices.

### Next likely moves
- Test whether `identity-match appeals become broker support queues` deserves promotion now that both correction notices and recipient-graph mistakes need a front-door challenge path.
- Develop `correction-materiality thresholds become packet boilerplate` if markets need cleaner boundaries between hygiene corrections, notice-class escalation, score restatements, holdback reopeners, covenant events, and eligibility changes.
- Watch whether `recipient-graph privacy proofs become broker trust products` becomes urgent once brokers must prove correct recipient scope without exposing every buyer-side insurer, lender, auditor, counsel, or downstream platform user.
- Track `reliance-right transfer notices become closing covenants` if amendment rights start following asset sales, loan assignments, insurance novations, reinsurance, subcontracting, or platform migrations.

## rev0175 — 2026.05.14.04.56 UTC — amendmentnotice

### Status
Compact continuation revision; broadens the archive by promoting a split/merge-correction-notice thesis that sits downstream of source-object identity warranties and transformation-code escrow.

### Added
- New dossier: `02-dossiers/split-merge-correction-notices-become-packet-amendment-events.md`.
- New source entries: **[S1414]–[S1426]**.

### Changed
- Updated README to reflect the new packet-amendment layer and the rebuilt next queue.
- Rebuilt the seed bank around identity-match appeals, amendment-recipient registries, escrow-access arbitration, custody-failure fault classes, comparable-by-reliance-purpose clauses, and correction-materiality thresholds after promoting the split/merge thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include split/merge correction notices as the layer that asks whether later subject remaps, duplicate reversals, rejected IDs, or canonical-ID retirements require formal amendment of already-relied-upon packets.
- Extended the principles and Speculation Cube with canonical-subject amendment events, corrected-score restatements, reliance-recipient graphs, historical-packet supersession, amendment-dispute windows, remap materiality thresholds, and holdback-reopening criteria.
- Expanded the source register with HL7 FHIR, GitHub, Jira, NVD, CSAF, CycloneDX, SPDX, and JSON Patch material on duplicate/successor links, merge operations, provenance, named issue events, changelog webhooks, CVE change history, rejected identifiers, stable advisory tracking IDs, BOM versioning, typed relationships, and machine-readable patch deltas.

### Design decisions
- Promoted `split/merge correction notices become packet amendment events` because the archive had source-object identity warranties and transformation-code escrow, but still lacked the afterlife layer for correcting a canonical subject graph after another institution has relied on the packet.
- Treated the key bottleneck as **amended reliance after identity correction** — not merely whether the current graph is right, but whether earlier packets, scores, residue counts, waiver histories, and holdback triggers have changed meaning enough to require notice, restatement, dispute windows, or supersession rules.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because split/merge amendments are the operational sequel to object-identity warranties, normalization-loss schedules, non-comparable-state carve-outs, and transform replay.

### Next likely moves
- Test whether `identity-match appeals become broker support queues` deserves promotion now that correction notices need a front-door challenge path.
- Develop `amendment-recipient registries become reliance-graph infrastructure` if packet amendments require durable records of who relied on which version for which purpose.
- Watch whether `escrow-access arbitration becomes a confidentiality market` becomes more urgent once correction disputes need before/after graphs and transform evidence without exposing proprietary mapping logic or sensitive source data.
- Track `correction-materiality thresholds become packet boilerplate` as a smaller clause-level sequel if markets need to distinguish hygiene corrections from score, holdback, covenant, or eligibility restatements.


## rev0174 — 2026.05.14.02.21 UTC — noncompstates

### Status
Compact continuation revision; broadens the archive by promoting a non-comparable-state-carve-out thesis that sits between normalization-loss warranties and source-object identity warranties.

### Added
- New dossier: `02-dossiers/non-comparable-state-carve-outs-become-diligence-battlegrounds.md`.
- New source entries: **[S1403]–[S1413]**.

### Changed
- Updated README to reflect the new burden-allocation layer around declared non-comparability, plus the rebuilt next queue.
- Rebuilt the seed bank around split/merge correction notices, identity-match appeals, escrow-access arbitration, custody-failure fault classes, and comparable-by-reliance-purpose clauses after promoting the non-comparable-state thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include non-comparable-state carve-outs as the layer that asks whether a correct no-map, broader/narrower, unknown, under-investigation, accepted-risk, or retained-unmapped label is missing proof, disclosed limitation, seller carve-out, buyer approval right, score exclusion, or holdback trigger.
- Extended the principles and Speculation Cube with no-map declarations, source-broader/source-narrower states, unknown/future enum handling, under-investigation state treatment, accepted-risk non-closure, comparability coverage ratios, carve-out burden allocation, and reliance-purpose-specific comparability clauses.
- Expanded the source register with HL7 FHIR, W3C SKOS, NIST/NCCoE OLIR, AWS OCSF extension, Microsoft Graph, OASIS CSAF, CycloneDX VEX, GitHub Dependabot, Tenable accept-rule, and NIST OSCAL material on context-bound mappings, mapping relationships, no-map outcomes, equivalence strength, set-theory relationship assertions, schema extensions, unknown/future states, VEX status justifications, platform-native alert states, accepted-risk semantics, and deterministic profile resolution.

### Design decisions
- Promoted `non-comparable-state carve-outs become diligence battlegrounds` because the archive had established normalization-loss warranties, source-object identity warranties, and transform escrow, but still lacked the contractual conflict around states that are correctly preserved yet cannot be relied on under the buyer’s target category.
- Treated the key bottleneck as **burden allocation under declared non-comparability** — not merely whether a mapping is exact, lossy, or replayable, but whether a non-comparable label functions as missing evidence, disclosed limitation, seller carve-out, broker warranty boundary, buyer approval right, score exclusion, or holdback trigger.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because non-comparable carve-outs are the practical dispute layer above semantic-loss schedules and below object-identity, transformation-custody, and substitute-control scorecard compression.

### Next likely moves
- Develop `split/merge correction notices become packet amendment events` if packet subject remaps start changing scores, residue counts, holdback triggers, or waiver histories after closing.
- Test whether `identity-match appeals become broker support queues` deserves promotion as the procedural sequel to object-identity warranties.
- Watch whether `escrow-access arbitration becomes a confidentiality market` becomes the practical sequel to transformation-code escrow once proprietary mapping logic and security-sensitive source extracts enter custody.


## rev0173 — 2026.05.14.00.35 UTC — transformescrow

### Status
Compact continuation revision; broadens the archive by promoting a transformation-code-escrow thesis that sits beneath source-object identity warranties and above substitute-control scorecard shorthand.

### Added
- New dossier: `02-dossiers/transformation-code-escrow-becomes-packet-custody.md`.
- New source entries: **[S1390]–[S1402]**.

### Changed
- Updated README to reflect the new replay-custody layer under normalized diligence packets, plus the rebuilt next queue.
- Rebuilt the seed bank around non-comparable-state carve-outs, split/merge correction notices, identity-match appeals, escrow-access arbitration, and custody-failure fault classes after promoting the transformation-code escrow thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include transformation-code escrow as the custody layer that asks whether a broker can reproduce, explain, or challenge the packet-producing run after schemas, code, source APIs, dependencies, or runtime environments drift.
- Extended the principles and Speculation Cube with mapping-code custody, schema-version pinning, lookup-table escrow, clock-policy preservation, validation-apparatus retention, runtime-environment replayability, manual-review disclosure, signed transform-run attestations, replay-rights clauses, hash commitments, neutral-custodian access rules, and custody-failure fault classes.
- Expanded the source register with dbt, Great Expectations, OpenLineage, in-toto, SLSA, Reproducible Builds, GitHub Artifact Attestations, Sigstore, Airflow, and OSCAL material on transform artifacts, project manifests, validation checkpoints, lineage facets, schema versioning, link attestations, provenance authenticity, reproducible environments, build metadata, signed bundles, versioned DAG contracts, and structured assessment reports.

### Design decisions
- Promoted `transformation-code escrow becomes packet custody` because the archive had just added normalization-loss warranties and source-object identity warranties, but those claims still require a replayable production record if a later dispute asks how the packet was actually generated.
- Treated the key bottleneck as **custody of the transform apparatus** — not merely whether a normalized packet exists, but whether the mapping code, configuration, schema versions, source snapshots, lookup tables, clock rules, validation tests, runtime environment, and attestations remain preserved strongly enough to rerun or adjudicate it.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because transform escrow is the evidentiary substrate beneath renewal-history normalization, semantic-loss schedules, object-identity warranties, and later scorecard compression.

### Next likely moves
- Test whether `non-comparable-state carve-outs become diligence battlegrounds` deserves promotion as the next contractual conflict above normalization-loss schedules.
- Develop `split/merge correction notices become packet amendment events` if packet subject remaps start changing scores, residue counts, holdback triggers, or waiver histories after closing.
- Watch whether `escrow-access arbitration becomes a confidentiality market` becomes the practical sequel to transformation-code escrow once proprietary mapping logic and security-sensitive source extracts enter custody.

## rev0172 — 2026.05.13.23.54 UTC — objectjoin

### Status
Compact continuation revision; broadens the archive by promoting a source-object-identity-warranty thesis that sits beneath normalization-loss warranties and above substitute-control scorecard shorthand.

### Added
- New dossier: `02-dossiers/source-object-identity-warranties-become-broker-liability-caps.md`.
- New source entries: **[S1378]–[S1389]**.

### Changed
- Updated README to reflect the new join-liability layer under normalized renewal-history packets, plus the rebuilt next queue.
- Rebuilt the seed bank around non-comparable-state carve-outs, transformation-code escrow, split/merge correction notices, identity-match appeals, and identity-graph poison records after promoting the source-object identity thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include source-object identity warranties as the layer that asks whether a normalized packet attached preserved fields and semantic-loss schedules to the right native records.
- Extended the principles and Speculation Cube with native-ID preservation, identity namespaces, canonical subject spines, join-key tables, same-subject relation labels, confidence bands, split/merge ledgers, unjoined near-match registers, identity-loss disclosures, replay packets, false-join liability caps, and correction paths.
- Expanded the source register with W3C PROV, NIST OSCAL, ServiceNow, Atlassian Jira, GitHub Dependabot, Google Security Command Center, Microsoft Graph, AWS Security Lake / OCSF, OpenLineage, SLSA, and CycloneDX material on alternate/specialized entities, UUID linkage, native record IDs, issue/changelog identities, repository-local alert numbers, source/finding/resource identities, alert/incident/evidence identities, source-identification fields, lineage naming, artifact subjects, and `bom-ref` packet identity.

### Design decisions
- Promoted `source-object identity warranties become broker liability caps` because the archive had just added normalization-loss warranties, but those warranties still assume the broker joined the correct source objects before mapping fields. The next bottleneck is the same-subject assertion itself.
- Treated the key bottleneck as **warranted object identity** — not whether a field was preserved or semantically weakened, but whether the native records bundled under one canonical packet subject actually refer to the same obligation, finding, exception, artifact, asset, dependency, or risk state.
- Kept the revision in the same lifecycle-governance lane rather than opening a new topic family, because object-identity joins are the substrate under renewal-history normalization, normalization-loss schedules, substitute-control scorecards, and later cutover forensics.

### Next likely moves
- Test whether `non-comparable-state carve-outs become diligence battlegrounds` deserves promotion as the next contractual conflict above normalization-loss schedules.
- Develop `transformation-code escrow becomes packet custody` if replayability starts depending on retained mapping code, join thresholds, schema versions, lookup tables, and clock policies.
- Watch whether `split/merge correction notices become packet amendment events` becomes the operational sequel to source-object identity warranties.

## rev0171 — 2026.05.13.22.10 UTC — normloss

### Status
Compact continuation revision; broadens the archive by promoting a normalization-loss-warranty thesis that sits above renewal-history normalization brokers and below substitute-control scorecard shorthand.

### Added
- New dossier: `02-dossiers/normalization-loss-warranties-become-diligence-language.md`.
- New source entries: **[S1367]–[S1377]**.

### Changed
- Updated README to reflect the new warranty layer above normalized renewal-history packets, plus the rebuilt next queue.
- Rebuilt the seed bank around expiry-boundary arbitration clauses, transfer-destroying covenant breaches, source-object identity warranties, non-comparable-state carve-outs, and transformation-code escrow after promoting the normalization-loss thesis.
- Updated the constellation map so managed legibility and maintenance work now explicitly include normalization-loss warranties as the contractual surface that says what a buyer, insurer, lender, auditor, or agency may rely on after brokered normalization.
- Extended the principles and Speculation Cube with loss-bearing warranty schedules, source-object identity matrices, field-preservation tables, semantic-equivalence maps, inferred-event registers, retained-unmapped payload, retention-loss disclosures, validation packets, materiality thresholds, and transformation-code custody.
- Expanded the source register with HL7 FHIR, W3C SKOS, W3C PROV, NIST OSCAL, AWS Security Lake, AWS OCSF transformation guidance, OpenLineage, JSON Schema, W3C SHACL, and dbt material on context-dependent mapping, semantic equivalence, provenance, profile resolution, custom-source conversion, schema validation, lineage facets, transformation observation, validation reports, and data-test assertions.

### Design decisions
- Promoted `normalization-loss warranties become diligence language` because the archive had already established both generic translation-loss proofs and renewal-history normalization brokers, but still lacked the deal-language layer that allocates responsibility for what was lost, inferred, weakened, omitted, retained as unmapped payload, or declared non-comparable during packet construction.
- Treated the key bottleneck as **warranted semantic loss** — not whether a broker can normalize histories, but whether another institution can safely rely on a declared preservation/loss schedule when pricing risk, closing a transaction, granting eligibility, or enforcing a remediation covenant.
- Kept the revision tight by adding one full dossier and wiring it into the same lifecycle-governance lane rather than starting a new topic family.

### Next likely moves
- Watch whether `source-object identity warranties become broker liability caps` deserves promotion as the join-confidence layer under normalization-loss warranties.
- Revisit `expiry-boundary arbitration clauses become workflow boilerplate` once the archive needs a direct contract-language layer above gate-expiry disputes.
- Develop `transfer-destroying covenant breaches become deal-control language` if enough examples show deals naming discontinuance, enlargement, operator substitution, transfer-filing failure, or continuity loss as separate breaches.

## rev0170 — 2026.05.13.21.18 UTC — renewalbroker

### Status
Compact continuation revision; broadens the archive by promoting a renewal-history-normalization thesis that sits above extension-lineage disclosures and below substitute-control scorecard shorthand.

### Added
- New dossier: `02-dossiers/renewal-history-normalization-services-become-a-quiet-broker-market.md`.
- New source entries: **[S1355]–[S1366]**.

### Changed
- Updated README to reflect the new cross-tool renewal-history broker layer above extension-lineage disclosures, plus the rebuilt next queue.
- Rebuilt the seed bank around expiry-boundary arbitration clauses, transfer-destroying covenant breaches, and normalization-loss warranties after promoting the renewal-history normalization thesis.
- Updated the constellation map so managed-legibility and maintenance work now explicitly include renewal-history normalization services as the broker layer between raw lineage exhibits and downstream scorecards.
- Extended the principles and Speculation Cube with renewal-history normalization defensibility, cross-tool-lineage crosswalkability, source-object identity matching, duplicate-event reconciliation, retention-window comparability, normalization-loss legibility, and replayable transformation recipes so the archive can reason about comparability across unlike history systems rather than only about native lineage export.
- Expanded the source register with current NIST, OCSF, AWS, ServiceNow, GitHub, Atlassian, Microsoft, Google Cloud, OASIS, and CycloneDX material on POA&M data models, open security schemas, security-data normalization, table APIs, audit-log export/stream semantics, issue changelogs, security-alert aggregation, finding-state time series, security-advisory exchange, and vulnerability-exploitability context.

### Design decisions
- Promoted `renewal-history normalization services become a quiet broker market` because the archive had already established that renewal lineage can become a diligence exhibit, but still lacked the broker layer that makes lineage comparable when the source systems use different clocks, statuses, IDs, retention windows, and event semantics.
- Treated the key bottleneck as **defensible semantic normalization** — not merely whether original due dates, extensions, approvals, reopenings, and finding updates can be exported, but whether another institution can see which meanings were preserved, inferred, weakened, deduplicated, or declared non-comparable during translation.
- Kept the revision tight by adding one real promotion and wiring it into managed-legibility, maintenance work, extension-lineage diligence, and procurement-scorecard shorthand.

### Next likely moves
- Watch whether `expiry-boundary arbitration clauses become workflow boilerplate` deserves promotion once contracts start naming valid-at-submission, valid-at-award, valid-at-deployment, or valid-at-use rules explicitly.
- Develop `transfer-destroying covenant breaches become deal-control language` if enough examples show deals naming discontinuance, enlargement, operator substitution, transfer-filing failure, or continuity loss as separate breaches.
- Test whether `normalization-loss warranties become diligence language` should sharpen into a dossier on crosswalk errors, source-priority disputes, and broker liability.

## rev0169 — 2026.05.13.21.00 UTC — legacyhandoff

### Status
Compact continuation revision; broadens the archive by promoting a legacy-status-transfer-attestation thesis that sits above grandfathering price terms and beside gate-expiry dispute work.

### Added
- New dossier: `02-dossiers/legacy-status-transfer-attestations-become-closing-artifacts.md`.
- New source entries: **[S1344]–[S1354]**.

### Changed
- Updated README to reflect the new beneficial-status handoff layer above grandfathering clauses, plus the rebuilt next queue.
- Rebuilt the seed bank around renewal-history normalization services, expiry-boundary arbitration clauses, and transfer-destroying covenant breaches after promoting the legacy-status transfer thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include legacy-status transfer attestations as a closing-file layer between grandfathering price terms and state-transition notice services.
- Extended the principles and Speculation Cube with status-transfer attestation portability, legacy-status handoff assurance, transfer-destroying act legibility, agency-acknowledgment timing, continuity-break detectability, and status-survival holdback language so the archive can reason about whether old-state benefits survive owner/operator handoff rather than only whether the benefit exists.
- Expanded the source register with current eCFR, Connecticut DEEP, EPA, Fannie Mae, New Haven, Seven Hills, Scott City, Reading, Quincy, and Horseshoe Bend material on permit transfer, administratively continued coverage, legal nonconforming loan documentation, due-diligence letters, run-with-the-land nonconformities, recording-ready certificates, and conduct limits after ownership change.

### Design decisions
- Promoted `legacy-status transfer attestations become closing artifacts` because it had remained unresolved across several revisions and now has a cleaner upstream/downstream position: grandfathering-price work tells us old-state treatment can be valuable, while gate-expiry and waiver work tell us expiring proof and exception timing are becoming dispute layers. The missing transaction layer is whether the value survives the handoff.
- Treated the key bottleneck as **beneficial-status handoff assurance** — not merely whether old-state reliance is lawful or price-bearing, but whether another institution can rely on a portable, dated, scoped statement about transfer survival, destructive acts, agency acknowledgement, continuous coverage, and post-close duties.
- Kept the revision tight by adding one real promotion and wiring it into conditioned-place governance, maintenance work, and closing-file evidence practice.

### Next likely moves
- Test whether `renewal-history normalization services become a quiet broker market` should sharpen into a cross-tool lineage-translation dossier.
- Watch whether `expiry-boundary arbitration clauses become workflow boilerplate` deserves promotion once contracts start naming valid-at-submission, valid-at-award, valid-at-deployment, or valid-at-use rules explicitly.
- Develop `transfer-destroying covenant breaches become deal-control language` if enough examples show deals naming discontinuance, enlargement, operator substitution, transfer-filing failure, or continuity loss as separate breaches.

## rev0168 — 2026.05.13.19.54 UTC — gatewindow

### Status
Compact continuation revision; broadens the archive by promoting a gate-expiry-dispute thesis that sits between convergence-proof gates and proceed-before-convergence waivers.

### Added
- New dossier: `02-dossiers/gate-expiry-disputes-become-a-service-layer.md`.
- New source entries: **[S1333]–[S1343]**.

### Changed
- Updated README to reflect the new validity-at-crossing layer above convergence-proof gates and below waiver handling, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, renewal-history normalization services, and expiry-boundary arbitration clauses after promoting the gate-expiry thesis.
- Updated the constellation map so managed legibility, conditioned-place governance, and maintenance work now explicitly include gate-expiry disputes as a distinct layer between convergence-proof gates and proceed-before-convergence waivers.
- Extended the principles and Speculation Cube with validity-at-crossing receipts, proof TTL enforcement, gate-time clock authority, cached-status disputability, grace-period boundaries, and expiry-boundary arbitration so the archive can reason about proof freshness at the exact crossing boundary rather than only whether a gate once passed.
- Expanded the source register with Section508.gov, OGC, OpenID, W3C, Microsoft, GitHub, AWS, ServiceNow, Tenable, and Google Cloud material on report refresh duties, certificate expiry, trust-chain expiration, credential validity periods, exemption expiry, deployment protection, approval timeouts, bypass descriptions, extension schedules, expiring accept rules, and post-deploy analysis gates.

### Design decisions
- Promoted `gate-expiry disputes become a service layer` because the archive had already established explicit proof gates, waiver paths, compensating-control packets, post-waiver certificates, residue expiry, extension penalties, and renewal-lineage exhibits, but still lacked a direct dossier on the boundary case where the proof existed yet may not have been live when the dependent action crossed.
- Treated the key bottleneck as **validity-at-crossing reconstruction** — not merely whether a clearance, approval, report, exemption, trust chain, or validation result existed, but whether another institution can prove it was alive under the correct clock, cache, grace, and bypass rules at the moment of use.
- Kept the revision tight by making one real promotion while deliberately wiring it into three existing lanes: managed-legibility proof objects, conditioned-place action clearance, and maintenance/waiver governance.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `renewal-history normalization services become a quiet broker market` should sharpen into a cross-tool lineage-translation dossier.
- Watch whether `expiry-boundary arbitration clauses become workflow boilerplate` deserves promotion once contracts start naming valid-at-submission, valid-at-award, valid-at-deployment, or valid-at-use rules explicitly.



## rev0167 — 2026.03.28.08.58 UTC — lineagepack

### Status
Compact continuation revision; broadens the archive by promoting an extension-lineage-disclosure thesis that sits above extension-frequency pricing and below substitute-control scorecard shorthand.

### Added
- New dossier: `02-dossiers/extension-lineage-disclosures-become-diligence-exhibits.md`.
- New source entries: **[S1322]–[S1332]**.

### Changed
- Updated README to reflect the new extension-lineage layer above extension-frequency penalties and below substitute-control sufficiency scorecards, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and renewal-history normalization services after promoting the renewal-history-packet thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include extension-lineage disclosures as a distinct layer between extension-frequency penalties and scorecard shorthand.
- Extended the principles and Speculation Cube with renewal-history packet portability, extension-history exportability, original-versus-current due-date comparability, schedule tabs, and approval chains so the archive can reason about portable renewal stories rather than only deadline counts.
- Expanded the source register with current ServiceNow, FedRAMP, Microsoft, and GitHub material on repeat-extension requests, schedule-tab detail, historical authorization/version requirements, preserved expired exemptions, activity-log retention/export, timeline comments, and reopen/reappear audit events.

### Design decisions
- Promoted `extension-lineage disclosures become diligence exhibits` because the archive had already established residue inventories, burn-down covenants, extension-frequency pricing, and comparative scorecards, but still lacked a dossier on the transport layer between them: how another institution inspects the full renewal story behind a current exception state.
- Treated the key bottleneck as **portable renewal-history legibility** — not merely whether deadlines were extended often, but whether another institution can inspect original due dates, added-time totals, approver chains, justifications, preserved records, and reopen events in one usable packet.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly sensitive to portable history rather than only present-state labels.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `renewal-history normalization services become a quiet broker market` should sharpen into a dossier on cross-tool lineage translation.


## rev0166 — 2026.03.28.08.50 UTC — renewalprice

### Status
Compact continuation revision; broadens the archive by promoting an extension-frequency thesis that sits above burn-down-covenant work and below extension-lineage diligence or gate-expiry dispute work.

### Added
- New dossier: `02-dossiers/extension-frequency-penalties-become-underwriting-inputs.md`.
- New source entries: **[S1316]–[S1321]**.

### Changed
- Updated README to reflect the new extension-frequency-penalty layer above residue burn-down covenants and below substitute-control sufficiency scorecards, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and extension-lineage disclosures after promoting the renewal-churn pricing thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include extension-frequency penalties as a distinct layer between burn-down covenants and scorecard shorthand.
- Extended the principles and Speculation Cube with extension-lineage legibility, rollover-count comparability, expiry-reset visibility, resurfaced-after-accept events, and renewal-churn penalizability so the archive can reason about repeated deadline pushes rather than only current backlog shape.
- Expanded the source register with current FedRAMP, ServiceNow, Microsoft, Tenable, and GitHub material on quarterly progress cycles, configurable multiple-extension counts, due-date governance rules, expiring accept rules, resurfaced findings, and dismissed-alert reopen lineage.

### Design decisions
- Promoted `extension-frequency penalties become underwriting inputs` because the archive had already established residue inventories, burn-down covenants, and comparative scorecards, but still lacked a dossier on the next scarce signal once tolerated incompleteness becomes clocked: how often the same operator keeps asking to move the deadline again.
- Treated the key bottleneck as **renewal-churn legibility** — not merely whether residue exists, nor only how quickly some portion closes, but whether another institution can see repeated extensions, expired tolerances, resurfaced findings, reopened dismissals, and rollover counts clearly enough to price them.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly sensitive to repeated deadline pushes.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `extension-lineage disclosures become diligence exhibits` should sharpen into a dossier on portable renewal-history packets.


## rev0165 — 2026.03.28.08.42 UTC — burnrate

### Status
Compact continuation revision; broadens the archive by promoting a burn-down-covenant thesis that sits above supervisory residue inventories and below extension-pricing or gate-expiry dispute work.

### Added
- New dossier: `02-dossiers/residue-burn-down-covenants-become-contract-language.md`.
- New source entries: **[S1308]–[S1315]**.

### Changed
- Updated README to reflect the new burn-down-covenant layer above conditional-acceptance residue inventories and below substitute-control sufficiency scorecards, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and extension-frequency penalties after promoting the burn-down-covenant thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include residue burn-down covenants as a distinct layer between residue inventories and scorecard shorthand.
- Extended the principles and Speculation Cube with closure-velocity comparability, maximum-residue-age covenantability, extension-ceiling enforceability, overdue-escalation triggers, and burn-down-attestation language so the archive can reason about backlog promises rather than only backlog visibility.
- Expanded the source register with current FedRAMP, CISA, ServiceNow, Microsoft, and GitHub material on POA&M reassessment and monthly vendor check-ins, quarterly progress expectations, due-dated remediation, exception-extension workflows, recommendation SLAs, and remediation-velocity metrics.

### Design decisions
- Promoted `residue burn-down covenants become contract language` because the archive had already established residue inventories, late-validation certificates, and substitute-control scorecards, but still lacked a dossier on the enforceable promises another institution will increasingly demand once tolerated incompleteness is visible.
- Treated the key bottleneck as **closure obligation legibility** — not merely whether residue exists or can be counted, nor only whether historical outcomes look good, but whether another institution can bind the operator to maximum age, closure velocity, extension discipline, and explicit consequences for missed burn-down promises.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly covenant-aware.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `extension-frequency penalties become underwriting inputs` should sharpen into a dossier on repricing repeated deadline pushes and renewal churn.


## rev0164 — 2026.03.28.08.35 UTC — residueledger

### Status
Compact continuation revision; broadens the archive by promoting a supervisory-residue thesis that sits above post-waiver validation certificates and beside substitute-control scorecard work while leaving room for legacy-status transfer and gate-expiry disputes.

### Added
- New dossier: `02-dossiers/conditional-acceptance-residue-inventories-become-a-supervisory-surface.md`.
- New source entries: **[S1298]–[S1307]**.

### Changed
- Updated README to reflect the new residue-inventory layer above post-waiver validation certificates and below substitute-control sufficiency scorecards, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and residue burn-down covenants after promoting the supervisory-residue thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include conditional-acceptance residue inventories as a distinct layer between post-waiver validation certificates and scorecard shorthand.
- Extended the principles and Speculation Cube with accepted-residue inventoryability, residue-owner clarity, residue-aging comparability, residue-expiry surveillance, and extension-churn language so the archive can keep reasoning about tolerated incompleteness after a conditional pass instead of collapsing everything into pass/fail or summary scores.
- Expanded the source register with current NIST, ServiceNow, AWS, Microsoft, and Google Cloud material on POA&Ms, exception durations, deferred states, accepted and past-due issue dashboards, expiring policy exemptions, expiring mute rules, and reopened findings.

### Design decisions
- Promoted `conditional-acceptance residue inventories become a supervisory surface` because the archive had already established waiver packets, late-validation certificates, and comparative scorecards, but still lacked a dossier on the live backlog of tolerated incompleteness that remains after an item is not fully cured and yet not fully failed.
- Treated the key bottleneck as **supervisory residue legibility** — not merely whether an exception was granted or later validated, nor only whether an operator’s historical score looks good, but whether another institution can see the still-open obligations, aging residue, expiry risk, and extension churn that remain in flight right now.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly backlog-aware.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `residue burn-down covenants become contract language` should sharpen into a dossier on closure velocity, extension ceilings, and maximum tolerated residue age.


## rev0163 — 2026.03.28.08.28 UTC — controlscore

### Status
Compact continuation revision; broadens the archive by promoting a comparative substitute-control thesis that sits above post-waiver validation certificates and below more explicit residue-inventory and gate-expiry work.

### Added
- New dossier: `02-dossiers/substitute-control-sufficiency-scorecards-become-procurement-shorthand.md`.
- New source entries: **[S1288]–[S1297]**.

### Changed
- Updated README to reflect the new substitute-control-sufficiency-scorecard layer above post-waiver validation certificates, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and conditional-acceptance residue inventories after promoting the scorecard thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include comparative substitute-control scorecards between late-validation certificates and later cutover-forensics.
- Extended the principles and Speculation Cube with substitute-control sufficiency scoring, late-pass-rate comparability, revert-incidence benchmarking, validation-latency benchmarking, conditional-residue visibility, and procurement-score portability so the archive can keep reasoning about comparative post-waiver quality rather than only about single-case authorization or ratification.
- Expanded the source register with current ServiceNow, AWS, Microsoft, GitHub, and Google Cloud material on change-success dashboards, KPI review, pipeline pass-rate reports, fleet-wide compliance reporting, deployment histories, merge gating, and DORA-style performance metrics.

### Design decisions
- Promoted `substitute-control sufficiency scorecards become procurement shorthand` because the archive had already established explicit waivers, substitute-control packets, and late-validation certificates, but still lacked a dossier on the comparative surface that lets another institution judge whether those substitute controls usually hold across many cases.
- Treated the key bottleneck as **comparative post-waiver legibility** — not merely whether a single waiver was disciplined or a single late validation passed, but whether many such outcomes compress into a buyer-readable shorthand that changes admission, pricing, and trust.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly scorecard-aware.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `conditional-acceptance residue inventories become a supervisory surface` should sharpen into a dossier on tolerated incompleteness, aging follow-up burdens, and operator residue queues.



## rev0162 — 2026.03.28.08.24 UTC — recheckseal

### Status
Compact continuation revision; broadens the archive by promoting a late-validation thesis that sits above waiver exhibits and below broader closing-artifact, gate-expiry, and scorecard work.

### Added
- New dossier: `02-dossiers/post-waiver-validation-certificates-become-a-service-tier.md`.
- New source entries: **[S1276]–[S1287]**.

### Changed
- Updated README to reflect the new post-waiver-validation-certificates layer above compensating-control bundles, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and substitute-control sufficiency scorecards after promoting the late-validation thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include post-waiver validation certificates between substitute-control packets and later cutover-forensics.
- Extended the principles and Speculation Cube with certificate portability, verdict legibility, partial-pass coding, temporary-control sunset discipline, revert-window usability, and related post-waiver language so the archive can keep reasoning about ratification after an exception rather than only about authorization and replay.
- Expanded the source register with current ServiceNow, AWS, Google Cloud, Azure, and GitHub material on post-implementation testing, change reporting, request timelines, deployment verification, analysis jobs, release details, bake-time monitoring, short-horizon reverts, post-deployment approvals, and portable deployment status records.

### Design decisions
- Promoted `post-waiver validation certificates become a service tier` because the archive had already established lawful early crossings and structured compensating-control bundles, but still lacked a dossier on the later compact verdict that says whether the waived action was actually rechecked strongly enough to count as cured, ratified, reverted, or still provisional.
- Treated the key bottleneck as **late-validation legibility** — not merely whether someone was allowed to proceed early, nor only whether the bundle looked disciplined at approval time, but whether another institution can later rely on a compact verdict about what happened after the exception crossed the gate.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly ratification-aware.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `substitute-control sufficiency scorecards become procurement shorthand` should sharpen into a dossier on comparative late-pass rates, revert incidence, and post-waiver quality ranking.


## rev0161 — 2026.03.28.08.14 UTC — controlpacket

### Status
Compact continuation revision; broadens the archive by promoting a waiver-exhibit thesis that sits above waiver authorization and below post-cutover replay while leaving room for legacy-status transfer, gate-expiry, and post-waiver validation work.

### Added
- New dossier: `02-dossiers/compensating-control-bundles-become-waiver-exhibits.md`.
- New source entries: **[S1264]–[S1275]**.

### Changed
- Updated README to reflect the new compensating-control-bundle layer above proceed-before-convergence waivers, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and post-waiver validation certificates after promoting the waiver-exhibit thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include attached substitute-control packets as a distinct layer above waiver authorization rather than as generic release hygiene.
- Extended the principles and Speculation Cube with bundle-completeness, rollback-attachment, telemetry-attachment, and post-waiver-validation language so the archive can keep reasoning about what makes an exception package defensible instead of merely traceable.
- Expanded the source register with current GitHub, AWS, ServiceNow, Microsoft, and Google Cloud material on bypass comments, required reviewers, wait timers, runbooks, change-request planning packets, verification tasks, telemetry analysis, postdeploy hooks, and automatic rollback.

### Design decisions
- Promoted `compensating-control bundles become waiver exhibits` because the archive had already established gates, mismatches, and lawful early crossings, but still lacked a dossier on the substitute-control packet that determines whether an authorized exception can later be defended as disciplined rather than improvised.
- Treated the key bottleneck as **substitute-control legibility** — not merely whether someone was allowed to proceed early, but whether the rollback, monitoring, testing, scope-limiting, and follow-up controls attached to that permission were structured enough to survive buyer scrutiny and dispute.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly packet-aware.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `post-waiver validation certificates become a service tier` should sharpen into a dossier on after-the-fact rechecks, substitute-control verdicts, and late admissibility.


## rev0160 — 2026.03.28.08.08 UTC — earlywaive

### Status
Compact continuation revision; broadens the archive by promoting a waiver-dispute thesis that sits above convergence-proof gating and alongside cutover-forensics while leaving room for legacy-status transfer, gate-expiry, and compensating-control work.

### Added
- New dossier: `02-dossiers/proceed-before-convergence-waivers-become-a-standing-dispute-class.md`.
- New source entries: **[S1256]–[S1263]**.

### Changed
- Updated README to reflect the new proceed-before-convergence-waiver layer above convergence-proof gates and alongside cutover-mismatch forensics, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and compensating-control waiver exhibits after promoting the waiver-dispute thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include authorized pre-proof proceeding as a distinct dispute surface rather than as generic urgency noise.
- Extended the principles and Speculation Cube with waiver-coding, waiver-scope, compensating-control, and post-waiver-review language so the archive can keep reasoning about lawful early crossings rather than only about whether a gate or mismatch replay existed.
- Expanded the source register with current GitHub, AWS, Microsoft, Argo CD, and Google Cloud material on deployment-rule bypasses, emergency change templates, bypassed checks, approval timeouts, sync-window overrides, and ignore-failure continuation paths.

### Design decisions
- Promoted `proceed-before-convergence waivers become a standing dispute class` because the archive had already established checkpoints and post-cutover replay, but still lacked a dossier on the explicitly authorized “go anyway” path that appears when urgency, hotfix, or emergency logic is allowed to outrun normal proof.
- Treated the key bottleneck as **lawful premature crossing** — not merely whether a gate existed or whether a bad crossing can be reconstructed later, but whether another institution can distinguish a disciplined exception from convenience laundering.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly waiver-aware.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `compensating-control bundles become waiver exhibits` should sharpen into a dossier on attached mitigations, rollback duties, and post-waiver validation.



## rev0159 — 2026.03.28.08.00 UTC — cutovertrace

### Status
Compact continuation revision; broadens the archive by promoting a cutover-forensics thesis that sits above convergence-proof gating and below legacy-status transfer-attestation, waiver-dispute, and gate-expiry work.

### Added
- New dossier: `02-dossiers/cutover-mismatch-forensics-becomes-a-standing-liability-class.md`.
- New source entries: **[S1246]–[S1255]**.

### Changed
- Updated README to reflect the new cutover-mismatch-forensics layer above convergence-proof gates and the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, proceed-before-convergence waivers, and gate-expiry disputes after promoting the cutover-forensics thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include post-gate mismatch reconstruction above convergence-proof checkpoints.
- Extended the principles and Speculation Cube with gate-crossing attribution, wrong-revision detectability, proof-expiry disputability, approval/bypass traceability, and post-cutover replay language so the archive can keep reasoning about defective crossings rather than only about whether a gate existed.
- Expanded the source register with current Google Cloud, AWS, GitHub, Kubernetes, Microsoft, and Datadog material on rollout details, execution history, manual approvals, bypass traces, audit logs, provisioning logs, revision history, and deployment comparison surfaces.

### Design decisions
- Promoted `cutover-mismatch forensics becomes a standing liability class` because the archive had already established that action can be delayed until proof exists, but still lacked a dossier on how later institutions reconstruct whether the gate was crossed correctly, on the right revision, under the right timing window, and with the right attached evidence.
- Treated the key bottleneck as **post-cutover accountability** — not merely whether a workflow had a gate, but whether another institution can later replay the crossing strongly enough to route blame, remedy, audit outcome, or insurance consequence.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly mismatch-aware.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `proceed-before-convergence waivers become a standing dispute class`.
- Test whether `gate-expiry disputes become a service layer` should sharpen into a dossier on expired proof objects, stale approvals, and timing-bound release liability.



## rev0158 — 2026.03.28.07.55 UTC — proofgate

### Status
Compact continuation revision; broadens the archive by promoting a convergence-proof-gate thesis that sits above propagation-lag budgets and below cutover-forensics, legacy-status transfer-attestation, and waiver-dispute work.

### Added
- New dossier: `02-dossiers/convergence-proof-gates-become-workflow-defaults.md`.
- New source entries: **[S1239]–[S1245]**.

### Changed
- Updated README to reflect the new convergence-proof-gate layer above propagation-lag budgets and the rebuilt next queue.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and proceed-before-convergence waivers after promoting the convergence-proof-gate thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include proceed/hold checkpoints that require explicit convergence proof above declared propagation timing.
- Extended the principles and Speculation Cube with convergence-checkpoint, verify-surface, gate-bypass, and rollback-coupling language so the archive can keep reasoning about when action is allowed to advance rather than only about how long convergence should take.
- Expanded the source register with current Google Cloud, AWS, Microsoft, Kubernetes, and GitHub material on policy simulation, propagation verification, rollout completion, post-deploy verification, telemetry-backed release analysis, and deployment protection rules.

### Design decisions
- Promoted `convergence-proof gates become workflow defaults` because the archive had already established that propagation windows can be disclosed and even warranted, but still lacked a dossier on the stronger question of when a consequential workflow must halt until readiness is explicitly proven.
- Treated the key bottleneck as **proceed authority** — not merely whether another institution knows the lag budget, but whether it has a portable proof checkpoint that authorizes release, promotion, approval, or downstream action.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly gate-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `proceed-before-convergence waivers become a standing dispute class` should sharpen into a dossier on override bundles, bypass reason codes, and post-gate review.


## rev0157 — 2026.03.28.07.45 UTC — syncwarranty

### Status
Compact continuation revision; broadens the archive by promoting a propagation-lag-budget thesis that sits above delegate-change propagation and below cutover-forensics, legacy-status transfer-attestation, and convergence-proof-gating work.

### Added
- New dossier: `02-dossiers/propagation-lag-budgets-become-buyer-visible-service-commitments.md`.
- New source entries: **[S1232]–[S1238]**.

### Changed
- Updated README to reflect the new propagation-lag-budget layer above delegate-change propagation and the rebuilt next queue.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and convergence-proof gates after promoting the propagation-budget thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include warranted downstream-convergence timing as a distinct layer above propagation-delay forensics.
- Extended the principles and Speculation Cube with propagation-budget, sync-cadence, convergence-window, and revocation-lag-ceiling language so the archive can keep reasoning about timing as a contractual surface rather than only an observed one.
- Expanded the source register with current AWS, Microsoft, Atlassian, Okta, and GitHub material on practical propagation windows, provisioning cycles, configurable sync intervals, and externally named SCIM timing.

### Design decisions
- Promoted `propagation-lag budgets become buyer-visible service commitments` because the archive had already established that delegate changes can propagate slowly and cause incidents, but still lacked a dossier on how those timing windows themselves begin turning into something customers compare, negotiate, and rely on ahead of time.
- Treated the key bottleneck as **warranted convergence timing** — not merely whether downstream systems eventually catch up, but whether another institution is entitled to know how long that should take, which surfaces are covered, and what happens if the declared window is missed.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly budget-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `convergence-proof gates become workflow defaults` should sharpen into a dossier on checkpointed proceed/hold decisions around high-consequence state changes.



## rev0156 — 2026.03.28.07.39 UTC — lagtrace

### Status
Compact continuation revision; broadens the archive by promoting a delegate-change-propagation thesis that sits above delegate freshness and below cutover-forensics, legacy-status transfer-attestation, and propagation-budget work.

### Added
- New dossier: `02-dossiers/delegate-change-propagation-delays-become-a-standing-incident-class.md`.
- New source entries: **[S1227]–[S1231]**.

### Changed
- Updated README to reflect the new delegate-change-propagation layer above delegate freshness and the rebuilt next queue.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and propagation-lag service commitments after promoting the delegate-change-propagation thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include proof of which downstream queues, approval paths, mailing lists, and connected services had and had not absorbed a delegate change at the moment of a consequential event.
- Extended the principles and Speculation Cube with propagation-latency, convergence-traceability, and stale-binding exposure language so the archive can keep reasoning about source-correct but downstream-stale responsibility graphs.
- Expanded the source register with current Google Cloud, AWS, Microsoft, and PagerDuty material on eventual consistency, group-membership propagation, connected-SaaS lag, delayed policy effectiveness, and change-correlation context.

### Design decisions
- Promoted `delegate-change propagation delays become a standing incident class` because the archive had already established that a route can be live and a delegate can be fresh, but still lacked a dossier on the interval in which the source-of-truth was correct while downstream systems were still acting on the prior delegate graph.
- Treated the key bottleneck as **authoritative-change diffusion** — not merely whether the role owner changed, but whether that change had actually converged across queues, lists, approval paths, and connected services strongly enough to rely on.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly propagation-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `propagation-lag budgets become buyer-visible service commitments` should sharpen into a dossier on warranted downstream-convergence windows and revocation-lag ceilings.


## rev0155 — 2026.03.28.07.32 UTC — roleledger

### Status
Compact continuation revision; broadens the archive by promoting a delegate-freshness thesis that sits above escalation-path liveness and below cutover-forensics, legacy-status transfer-attestation, and delegate-change propagation work.

### Added
- New dossier: `02-dossiers/delegate-freshness-proofs-become-a-service-metric.md`.
- New source entries: **[S1221]–[S1226]**.

### Changed
- Updated README to reflect the new delegate-freshness layer above escalation-route liveness and the rebuilt next queue.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and delegate-change propagation delays after promoting the delegate-freshness thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include proof that the named backup, approver, or emergency contact still matched current role and staffing reality when a live route was invoked.
- Expanded the source register with current FINRA, Microsoft, AWS, and PagerDuty material on emergency-contact upkeep, recurring access reviews, stale-role remediation, escalation schedules, backup contact methods, and verification/testing of notification paths.

### Design decisions
- Promoted `delegate-freshness proofs become a service metric` because the archive had already established that consequential notice can be routed to a live path, but still lacked a dossier on how another institution later proves that the named delegate at the end of that path was still the right current owner.
- Treated the key bottleneck as **current responsibility binding** — not merely whether a route existed or was live, but whether the person, backup, or approver named by that route still matched role, staffing, and identity reality strongly enough to rely on.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly freshness-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `delegate-change propagation delays become a standing incident class` should sharpen into a dossier on downstream queue drift, stale mailing lists, and approval-path lag.




## rev0154 — 2026.03.28.07.23 UTC — routepulse

### Status
Compact continuation revision; broadens the archive by promoting an escalation-path-liveness thesis that sits above nonreceipt reason codes and below delegate-freshness, cutover-forensics, and legacy-status transfer-attestation work.

### Added
- New dossier: `02-dossiers/escalation-path-liveness-checks-become-a-compliance-service.md`.
- New source entries: **[S1216]–[S1220]**.

### Changed
- Updated README to reflect the new escalation-path-liveness layer above nonreceipt reason codes and the rebuilt next queue.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and delegate-freshness proofs after promoting the escalation-path-liveness thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include proof that the nominal escalation route was still live, staffed, and owned when notice needed to become action.
- Expanded the source register with current FINRA, CMS, NIST, AWS, and Atlassian material on emergency-contact upkeep, communication-plan review, call-tree testing, endpoint health checks, and heartbeat expiration alerts.

### Design decisions
- Promoted `escalation-path liveness checks become a compliance service` because the archive had already established that consequential notices can be watched, authenticated, delivery-attested, and reason-coded, but still lacked a dossier on how another institution later proves that the queue, delegate, number, inbox, or endpoint on the far side of escalation was actually live.
- Treated the key bottleneck as **live responsibility** — not merely whether a notice was sent, authentic, or diagnosably failed, but whether the supposed handoff path still terminated in a monitored, staffed, reachable owner strongly enough to matter.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly liveness-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `delegate-freshness proofs become a service metric` should sharpen into a dossier on role ownership, backup approvers, and directory-vs-reality drift.





## rev0153 — 2026.03.28.07.17 UTC — reasonmesh

### Status
Compact continuation revision; broadens the archive by promoting a nonreceipt-reason-code thesis that sits above delivery attestation and below escalation-path-liveness, cutover-forensics, and legacy-status transfer-attestation work.

### Added
- New dossier: `02-dossiers/nonreceipt-reason-codes-become-a-liability-grammar.md`.
- New source entries: **[S1211]–[S1215]**.

### Changed
- Updated README to reflect the new nonreceipt-reason-code layer above delivery attestation and the rebuilt next queue.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and escalation-path liveness checks after promoting the nonreceipt-reason-code thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include reason-coded nondelivery and failed-notice handling above authenticity and delivery evidence.
- Expanded the source register with current IETF, USPS, AWS, and Twilio material on enhanced delivery-status codes, postal nondelivery endorsements, cloud bounce subtypes, and message failure states.

### Design decisions
- Promoted `nonreceipt reason codes become a liability grammar` because the archive had already established that consequential notices are watched, can be authenticated, and can often be proven delivered or not delivered, but still lacked a dossier on how another institution later names *why* notice failed strongly enough to route remedy, retry, blame, or legal sufficiency.
- Treated the key bottleneck as **reason-bearing failure** — not merely whether a notice existed, was trustworthy, or even appears to have been delivered, but whether the failure mode can be normalized into something another institution can act on without reopening every channel-specific detail by hand.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly failure-grammar-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `escalation-path liveness checks become a compliance service` should sharpen into a dossier on dead queues, stale delegates, and proof of live responsibility.


## rev0152 — 2026.03.28.07.12 UTC — receipttrail

### Status
Compact continuation revision; broadens the archive by promoting a delivery-attestation thesis that sits above notice-authenticity and below nonreceipt-liability grammar, cutover-forensics, and legacy-status transfer-attestation work.

### Added
- New dossier: `02-dossiers/delivery-attestations-become-an-evidentiary-service-tier.md`.
- New source entries: **[S1207]–[S1210]**.

### Changed
- Updated README to reflect the new delivery-attestation layer above notice authenticity and the rebuilt next queue.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and nonreceipt reason codes after promoting the delivery-attestation thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include proof that an authentic notice reached the intended recipient scope or escalation path.
- Expanded the source register with current USPS, PACER, AWS, and Twilio material on proof of delivery, automated service notices, delivery-status logging, and status callbacks.

### Design decisions
- Promoted `delivery attestations become an evidentiary service tier` because the archive had already established that consequential states are watched and that routed notices can be authentic, but still lacked a dossier on what later proves that the right recipient, endpoint, or escalation queue was actually reached.
- Treated the key bottleneck as **proof of arrival** — not merely whether a notice existed or was genuine, but whether another institution can later show that it reached the required scope in time strongly enough to shift liability or justify action.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly receipt-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `nonreceipt reason codes become a liability grammar` should sharpen into a dossier on wrong-queue, rejected-endpoint, and unstaffed-escalation disputes.



## rev0151 — 2026.03.28.07.05 UTC — proofsignal

### Status
Compact continuation revision; broadens the archive by promoting a notice-authenticity thesis that sits above notice-service coverage and below delivery-attestation, cutover-forensics, and legacy-status transfer-attestation work.

### Added
- New dossier: `02-dossiers/notice-authenticity-proofs-become-an-assurance-layer.md`.
- New source entries: **[S1202]–[S1206]**.

### Changed
- Updated README to reflect the new notice-authenticity layer above watch services and the new next queue.
- Extended the principles with proof-of-origin legibility, signature-verification portability, channel-trust ordering, anti-spoof control coverage, and delivery-result attestability as enforceable surfaces.
- Expanded the Speculation Cube to better represent proof-bearing notices, trust-path verification, anti-spoof controls, caller-ID authentication, and verification-result logging.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and delivery attestations after promoting the notice-authenticity thesis.
- Updated the constellation map so managed legibility, conditioned-place governance, and maintenance work now explicitly include a notice-assurance layer above watch services.
- Expanded the source register with current FEMA, OASIS, CISA, and FCC material on digitally signed alerts, CAP signature support, email anti-spoof controls, and caller-ID authentication.

### Design decisions
- Promoted `notice-authenticity proofs become an assurance layer` because the archive had already established that consequential states are published, synchronized, provisionally usable, grandfathered, and watched, but still lacked a dossier on what makes a routed notice trustworthy enough to justify action without reopening the whole verification chain by hand.
- Treated the key bottleneck as **actionable trust** — not merely whether a notice exists or arrives quickly, but whether another institution can later show that the notice was authentic, intact, properly routed, and strong enough to defend after the fact.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly proof-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `delivery attestations become an evidentiary service tier` should sharpen into a dossier on receipt proofs, escalation completion, and wrong-recipient dispute handling.




## rev0150 — 2026.03.28.06.59 UTC — watchlayer

### Status
Compact continuation revision; broadens the archive by promoting a notice-service thesis that sits above grandfathering-value design and below notice-authenticity proof, cutover-forensics, and legacy-status transfer-attestation work.

### Added
- New dossier: `02-dossiers/state-transition-notice-services-become-a-quiet-vendor-market.md`.
- New source entries: **[S1197]–[S1201]**.

### Changed
- Updated README to reflect the new notice-service layer above grandfathering and the new next queue.
- Extended the principles with subscription-routing precision, notice-authenticity assurance, alert-fatigue triage, watchlist scoping, and historical-notice reconstructability as enforceable surfaces.
- Expanded the Speculation Cube to better represent alert channels, watchlist routing, authenticated notices, delivery attestations, and notice-fatigue filtering.
- Rebuilt the seed bank around cutover-mismatch forensics, legacy-status transfer attestations, and notice-authenticity proofs after promoting the notice-service thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit notice-service layer above grandfathering and so quiet infrastructure now treats watch layers as operational infrastructure.
- Expanded the source register with current FEMA, FDA, and NOAA material on authenticated alerting, Common Alerting Protocol, recall subscriptions, and watch / warning notification services.

### Design decisions
- Promoted `state-transition notice services become a quiet vendor market` because the archive had already established how consequential states become visible, synchronized, provisionally usable, and sometimes economically valuable, but still lacked a dossier on who is paid to keep watching those states closely enough for another institution to act in time.
- Treated the key bottleneck as **managed attention** — not merely whether a state exists or even whether it changed, but whether a trustworthy, use-case-specific, and fast-enough notice reaches the right party before loss, delay, or mispricing compounds.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly notice-aware.

### Next likely moves
- Promote `cutover-mismatch forensics becomes a standing liability class`.
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Test whether `notice-authenticity proofs become an assurance layer` should sharpen into a dossier on authenticated routing, delivery attestation, and alert-spoof dispute handling.


## rev0149 — 2026.03.24.04.41 UTC — carryright

### Status
Compact continuation revision; broadens the archive by promoting a grandfathering-clause thesis that sits above provisional-use policy and below notice-service, cutover-forensics, and legacy-status transfer-attestation work.

### Added
- New dossier: `02-dossiers/grandfathering-clauses-become-price-terms.md`.
- New source entries: **[S1191]–[S1196]**.

### Changed
- Updated README to reflect the new grandfathering-value layer above provisional-use policy.
- Extended the principles with grandfathering-transfer clarity, legacy-status proofability, continued-use price sensitivity, cutover holdback design, and beneficial-status loss triggers as enforceable surfaces.
- Expanded the Speculation Cube to better represent value-bearing old-state governance.
- Rebuilt the seed bank around state-transition notice services, cutover-mismatch forensics, and legacy-status transfer attestations after promoting the grandfathering-clause thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit grandfathering-value layer above provisional use and so maintenance work now explicitly includes legacy-status continuity design.
- Expanded the source register with current FEMA, EPA, and local-government material on effective/preliminary/pending/historic flood products, grandfathering-facing flood-insurance workflows, legal nonconforming uses, and certificates used to establish grandfathered rights.

### Design decisions
- Promoted `grandfathering clauses become price terms` because the archive had already established how consequential states are published, synchronized, and used provisionally, but still lacked a dossier on the more valuable question of who gets to preserve an advantageous old-state treatment when the new state is already in motion.
- Treated the key bottleneck as **beneficial-status continuity** — not merely whether a status is visible or temporarily usable, but whether a party can keep, prove, transfer, or lose a favorable old-state treatment in a way that materially changes price or transaction structure.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly legacy-value-aware.

### Next likely moves
- Promote `state-transition notice services become a quiet vendor market`.
- Revisit `cutover-mismatch forensics becomes a standing liability class`.
- Test whether `legacy-status transfer attestations become closing artifacts` should sharpen into a dossier on portable proof that beneficial old-state treatment survives handoff.

## rev0148 — 2026.03.24.04.29 UTC — graypass

### Status
Compact continuation revision; broadens the archive by promoting a provisional-use-policy thesis that sits above effective-date synchronization and below notice-service, cutover-forensics, and grandfathering-value work.

### Added
- New dossier: `02-dossiers/provisional-use-policies-become-procurement-boilerplate.md`.
- New source entries: **[S1187]–[S1190]**.

### Changed
- Updated README to reflect the new provisional-use / interim-admissibility layer above effective-date synchronization.
- Extended the principles with interim-use allowance clarity, grandfathering-rule legibility, pre-effective action bounds, conditional-award portability, and advisory-only labeling discipline as enforceable surfaces.
- Expanded the Speculation Cube to better represent provisional-use-policy quality dimensions.
- Rebuilt the seed bank around state-transition notice services, cutover-mismatch forensics, and grandfathering clauses after promoting the provisional-use thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit provisional-use layer above state machines and so maintenance work now explicitly includes interim-use policy design.
- Expanded the source register with current EPA, FEMA, USACE, and NRCS material on administrative continuance, no-action-assurance boundaries, advisory-only preliminary products, non-final map use limits, preliminary-jurisdiction election, and waiver-to-expedite-finality.

### Design decisions
- Promoted `provisional-use policies become procurement boilerplate` because the archive had already established how consequential states are published, challenged, timed, and synchronized, but still lacked a dossier on what another institution may actually do while those states remain unsettled.
- Treated the key bottleneck as **interim admissibility** — not merely when a status changes, but which actions remain lawful, advisory, conditionally allowed, grandfathered, or forbidden before finality or effectiveness arrives.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly provisional-use-aware.

### Next likely moves
- Promote `state-transition notice services become a quiet vendor market`.
- Revisit `cutover-mismatch forensics becomes a standing liability class`.
- Test whether `grandfathering clauses become price terms` should sharpen into a dossier on the market value of continued old-state reliance.

## rev0147 — 2026.03.24.04.24 UTC — cutovermesh

### Status
Compact continuation revision; broadens the archive by promoting an effective-date-synchronization thesis that sits above determination state machines and below provisional-use boilerplate, state-transition notices, and cutover-mismatch forensic work.

### Added
- New dossier: `02-dossiers/effective-date-synchronization-services-become-a-workflow-tier.md`.
- New source entries: **[S1184]–[S1186]**.

### Changed
- Updated README to reflect the new synchronization layer above state machines and the new next queue.
- Extended the principles with cross-system clock alignment, cutover-notice quality, downstream-propagation completeness, and old-state retirement discipline.
- Expanded the Speculation Cube to better represent cutover governance and propagation quality above determination-state legibility.
- Rebuilt the seed bank around provisional-use policies, state-transition notice services, and cutover-mismatch forensics after promoting the synchronization thesis.
- Updated the constellation map so conditioned-place governance now explicitly includes the synchronization layer above draft/preliminary/final/effective state machines.
- Expanded the source register with current FEMA, EPA, and USACE material on automated notifications and workflow-relevant state-change surfaces.

### Design decisions
- Promoted `effective-date synchronization services become a workflow tier` because the archive had already established that consequential statuses pass through draft, preliminary, final, and effective states, but still lacked a dossier on who translates those clocks into safe downstream action.
- Treated the key bottleneck as **cross-system cutover discipline** — not merely whether a state is visible or challengeable, but whether every dependent workflow knows exactly when to stop using the old state and start honoring the new one.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly synchronization-aware.

### Next likely moves
- Promote `provisional-use policies become procurement boilerplate`.
- Revisit `state-transition notice services become a quiet vendor market`.
- Test whether `cutover-mismatch forensics becomes a standing liability class` should sharpen into a dossier on early/late cutover blame and old-state retirement failures.


## rev0146 — 2026.03.24.04.16 UTC — stateclock

### Status
Compact continuation revision; broadens the archive by promoting a determination-state-machine thesis that sits above scoreboard appeals and below synchronization, provisional-use, and state-transition notice work.

### Added
- New dossier: `02-dossiers/preliminary-final-effective-state-machines-become-procurement-calendars.md`.
- New source entries: **[S1178]–[S1183]**.

### Changed
- Updated README to reflect the new state-machine layer above scoreboard appeals and the new next queue.
- Extended the principles with state-transition legibility, provisional-use discipline, publication-cutover governance, effective-date synchronization, and draft/provisional/final/effective status labels as enforceable surfaces.
- Expanded the Speculation Cube to better represent state-transition legibility, provisional-use discipline, publication-cutover governance, effective-date synchronization, and contest-window usability.
- Rebuilt the seed bank around effective-date synchronization services, provisional-use policies, and state-transition notice services after promoting the state-machine thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit state-machine layer above redress and so maintenance work now explicitly includes draft-to-effective transition discipline.
- Expanded the source register with current EPA, NRCS, FEMA, and USACE material on draft-to-official compliance states, preliminary-to-final determinations, appeal windows, and delayed effectiveness after final determination.

### Design decisions
- Promoted `preliminary-final-effective state machines become procurement calendars` because the archive had already established how conditioned-place determinations become searchable, replayable, rankable, and appealable, but still lacked a dossier on when those same determinations are actually usable by downstream institutions.
- Treated the key bottleneck as **state-governed usability** — not merely whether a status is visible or even challengeable, but whether another institution may rely on it yet, must treat it as provisional, or must wait for a later cutover.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly state-machine-aware.

### Next likely moves
- Promote `effective-date synchronization services become a workflow tier`.
- Revisit `provisional-use policies become procurement boilerplate`.
- Test whether `state-transition notice services become a quiet vendor market` should sharpen into a dossier on cutover visibility and downstream propagation.


## rev0145 — 2026.03.24.04.09 UTC — redressmesh

### Status
Compact continuation revision; broadens the archive by promoting a scoreboard-appeal-workflows thesis that sits above fault-class scoreboards and below drift/override vendor rankings, casepack tooling, and other correction-governance work.

### Added
- New dossier: `02-dossiers/scoreboard-appeal-workflows-become-a-governance-service-tier.md`.
- New source entries: **[S1169]–[S1177]**.

### Changed
- Updated README to reflect the new redress layer above comparative scoreboards and the new next queue.
- Extended the principles with reconsideration / score-appeal / map-challenge language as enforceable surfaces.
- Expanded the Speculation Cube to better represent classification-correction latency, peer-group challengeability, denominator-dispute resolution, appellate-record portability, and provisional-score labeling.
- Rebuilt the seed bank around source-drift scoreboards, override-rate scoreboards, and appeal-casepack generators after promoting the scoreboard-appeal thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit redress layer above comparative scoreboards and maintenance work now explicitly includes dispute-to-correction propagation.
- Expanded the source register with current EPA, USACE, NRCS, FEMA, and Pennsylvania PUC material on correction requests, field revisits, hearings, technical appeals, and formal challenge pathways.

### Design decisions
- Promoted `scoreboard-appeal workflows become a governance service tier` because the archive had already established how fault patterns become public or semi-public scoreboards, but still lacked a dossier on what lets a party actually contest a consequential score before qualification, pricing, or supervisory treatment hardens around it.
- Treated the key bottleneck as **appealable comparability** — not merely whether a score exists, but whether coding, denominator choice, peer grouping, stale-window math, and source corrections can be challenged through a governed path with timelines and propagation rules.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly redress-aware.

### Next likely moves
- Promote `source-drift scoreboards become vendor selection shorthand`.
- Revisit `override-rate scoreboards become buyer diligence shortcuts`.
- Test whether `appeal-casepack generators become a qualification-adjacent workflow tier` should sharpen into a dossier on reusable correction bundles.


## rev0144 — 2026.03.24.03.52 UTC — faultboard

### Status
Compact continuation revision; broadens the archive by promoting a fault-class-scoreboards thesis that sits above override-misuse forensics and below vendor/buyer-facing scoreboard governance, appeals, and ranking work.

### Added
- New dossier: `02-dossiers/fault-class-scoreboards-become-qualification-filters.md`.
- New source entries: **[S1161]–[S1168]**.

### Changed
- Updated README to reflect the new scoreboard thesis, sharper lifecycle-governance framing, and new next queue.
- Updated `01-speculation-cube.md` with comparability, normalization, qualification-band, legitimacy, and appealability bottlenecks.
- Updated `03-seed-bank.md` to promote source-drift scoreboards, override-rate scoreboards, and scoreboard-appeal workflows.
- Updated `04-constellations.md` so place-governance and maintenance lanes now explicitly culminate in comparative scoreboards.
- Updated `SOURCES.md` with current PUC, PHMSA, EPA, and FEMA material supporting comparative qualification and dashboard logic.

### Editorial notes
- Kept the addition narrow by promoting the comparative layer above fault taxonomy and override forensics rather than broadening outward into generic vendor rankings.
- Preserved the archive’s main spine: local conditioned-place governance now ends not just in replay, warranty, and dispute, but in comparative ranking surfaces that can alter admission and oversight upstream.

## rev0143 — 2026.03.24.03.41 UTC — urgencyaudit

### Status
Compact continuation revision; broadens the archive by promoting an override-misuse-forensics thesis that sits above source-drift warranties and below scoreboards, buyer-facing discipline signals, and other dispute-routing work.

### Added
- New dossier: `02-dossiers/override-misuse-forensics-becomes-a-standing-dispute-class.md`.
- New source entries: **[S1157]–[S1160]**.

### Changed
- Updated README to reflect the new override-forensics layer above source-drift warranties.
- Extended the principles with override-validity adjudicability, emergency-claim falsifiability, allegation-to-determination latency, forensic-bundle sufficiency, and misuse-pattern comparability as enforceable surfaces.
- Expanded the Speculation Cube to better represent override-forensics quality dimensions and post-override reviewability.
- Rebuilt the seed bank around fault-class scoreboards, source-drift scoreboards, and override-rate scoreboards after promoting the override-forensics thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit override-forensics layer above source-drift warranties and so maintenance work now explicitly includes post-override claims review.
- Expanded the source register with current Pennsylvania PUC materials on alleged-violation intake, recurring DPC review, expanded accountability under Act 127 of 2024, and concrete case-summary patterns involving emergency-response failures, late reports, compliance training, and penalties.

### Design decisions
- Promoted `override-misuse forensics becomes a standing dispute class` because the archive had already established how emergency pathways are designed, how stale states are classified, how replay quality is priced, and who owns live-source drift, but still lacked a dossier on how later reviewers decide whether urgency was genuine or was used to launder weak diligence.
- Treated the key bottleneck as **override validity after the fact** — not merely whether a break-glass route existed, but whether a later claim, enforcement, or underwriting review can distinguish a lawful emergency from opportunistic use of fallback rights.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly override-forensics-aware.

### Next likely moves
- Promote `fault-class scoreboards become contractor qualification filters`.
- Revisit `source-drift scoreboards become vendor selection shorthand`.
- Test whether `override-rate scoreboards become buyer diligence shortcuts` should sharpen into a dossier on discipline transparency and prequalification.

## rev0142 — 2026.03.24.03.38 UTC — driftclause

### Status
Compact continuation revision; broadens the archive by promoting a source-drift-warranty thesis that sits above replay-quality underwriting and below drift scoreboards, missed-notice disputes, and other liability-routing work.

### Added
- New dossier: `02-dossiers/source-drift-warranties-become-contract-language.md`.
- New source entries: **[S1154]–[S1156]**.

### Changed
- Updated README to reflect the new drift-warranty / change-notice layer above replay-quality grading.
- Extended the principles with source-drift warranty clarity, change-notice latency, supersession-notice routing, watch-coverage completeness, and rerun-support accountability as enforceable surfaces.
- Expanded the Speculation Cube to better represent source-drift warranty clarity, change-notice latency, supersession-notice routing, watch-coverage completeness, and rerun-support accountability.
- Rebuilt the seed bank around override-misuse forensics, fault-class scoreboards, and source-drift scoreboards after promoting the drift-warranty thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit source-drift-warranty layer above replay-quality underwriting.
- Expanded the source register with current EPA and FEMA material on snapshot-in-time composites, ongoing official map changes, and revalidated-versus-superseded determination outcomes.

### Design decisions
- Promoted `source-drift warranties become contract language` because the archive had already established how decision-state bundles are preserved, classified, and priced, but still lacked a dossier on which party is actually obligated to notice when upstream official reality changes under a still-active reliance state.
- Treated the key bottleneck as **drift ownership** — not merely whether a source is authoritative, or whether a replay bundle exists, but whether anyone has contractually accepted the duty to monitor, classify, notify, and support rerun when material source changes occur.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly drift-warranty-aware.

### Next likely moves
- Promote `override-misuse forensics becomes a standing dispute class`.
- Revisit `fault-class scoreboards become contractor qualification filters`.
- Test whether `source-drift scoreboards become vendor selection shorthand` should be sharpened into a dossier on buyer-facing drift-performance rankings.

## rev0141 — 2026.03.24.03.19 UTC — riskgrade

### Status
Compact continuation revision; broadens the archive by promoting a replay-quality-underwriting thesis that sits above stale-clearance fault classification and below warranty, forensic, and scoreboard work.

### Added
- New dossier: `02-dossiers/replay-quality-grades-become-underwriting-inputs.md`.
- New source entries: **[S1143]–[S1153]**.

### Changed
- Updated README to reflect the new replay-quality / underwriting layer above stale-fault diagnosis.
- Extended the principles with replay-quality grading, underwriting relevance, reserve sensitivity, evidence-discipline pricing, and contractor-eligibility portability as enforceable surfaces.
- Expanded the Speculation Cube to better represent replay-quality grades plus their money-facing quality dimensions.
- Rebuilt the seed bank around source-drift warranties, override-misuse forensics, and fault-class scoreboards after promoting the replay-quality thesis.
- Updated the constellation map so conditioned-place governance now includes the underwriting layer above stale-fault diagnosis and so maintenance work now explicitly includes money-facing replay quality.
- Expanded the source register with current Treasury/FIO, FEMA, banking-regulation, Pennsylvania 811, EPA, PHMSA, and eCFR material on underwriting-data collection, required flood-determination forms, durable loan-file retention, five-year locate records, legally dependable compliance logs, and excavation-damage loss stakes.

### Design decisions
- Promoted `replay-quality grades become underwriting inputs` because the archive had already established how conditioned-place decisions are searched, structured, preserved, refreshed, overridden, and fault-classified, but still lacked a dossier on how those governance-trail differences begin changing money terms.
- Treated the key bottleneck as **money-facing reconstructability** — not merely whether a trail exists after a dispute, but whether its quality is legible enough to influence premiums, reserves, contractor eligibility, and reliance appetite before the next loss.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly underwriting-aware.

### Next likely moves
- Promote `source-drift warranties become contract language`.
- Revisit `override-misuse forensics becomes a standing dispute class`.
- Test whether `fault-class scoreboards become contractor qualification filters` should sharpen into a broader buyer-visible discipline dossier.

## rev0140 — 2026.03.24.03.12 UTC — faulttree

### Status
Compact continuation revision; broadens the archive by promoting a stale-clearance-fault-class thesis that sits above emergency-override constitutions and below money-facing replay-quality and warranty work.

### Added
- New dossier: `02-dossiers/stale-clearances-split-into-distinct-fault-classes.md`.
- New source entries: **[S1136]–[S1142]**.

### Changed
- Updated README to reflect the new fault-class layer above override constitutions.
- Extended the principles with fault-class legibility, fault-attribution precision, cure-path specificity, blame-routing clarity, and override-misuse separability as enforceable surfaces.
- Expanded the Speculation Cube to better represent stale-state fault classes, reason-coded failure review, and the new fault-class quality dimensions.
- Rebuilt the seed bank around replay-quality underwriting, source-drift warranties, override-misuse forensics, and fault-class scoreboards after promoting the stale-clearance thesis.
- Updated the constellation map so conditioned-place governance now includes the explicit stale-fault layer above override constitutions and so maintenance work now explicitly includes reason-coded stale-state analysis.
- Expanded the source register with current EPA, USACE, FEMA, Pennsylvania 811, PHMSA, and eCFR material on calendar expiry, changed conditions, pre-expiry revision on new information, revalidation-versus-supersession, lawful-start lapses, compromised marks, fallback proceed rights, emergency-misuse prohibitions, and excavation-damage stakes.

### Design decisions
- Promoted `stale clearances split into distinct fault classes` because the archive had already established how determinations are searched, structured, refreshed, and overridden, but still lacked a dossier on how later incidents distinguish one insufficiency mode from another.
- Treated the key bottleneck as **reason-coded stale-state diagnosis** — not only whether a clearance was no longer good enough, but which specific subtype of insufficiency occurred and therefore which actor, cure path, reserve posture, and software obligation should follow.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly fault-class-aware.

### Next likely moves
- Promote `replay-quality grades become underwriting inputs`.
- Revisit `source-drift warranties become contract language`.
- Test whether `override-misuse forensics becomes a standing dispute class` should sharpen into a broader claims-and-enforcement dossier.

## rev0139 — 2026.03.24.03.04 UTC — breakglass

### Status
Compact continuation revision; broadens the archive by promoting an emergency-override-constitution thesis that sits above re-review-trigger grammars and below fault-class, insurance, and abuse-forensics work.

### Added
- New dossier: `02-dossiers/emergency-override-constitutions-become-procurement-questions.md`.
- New source entries: **[S1127]–[S1135]**.

### Changed
- Updated README to reflect the new break-glass / override-constitution layer above re-review-trigger grammars.
- Extended the principles with override-boundary clarity, fallback-authority routing, break-glass justification quality, override-window discipline, and post-override reconciliation timeliness as enforceable surfaces.
- Expanded the Speculation Cube to better represent break-glass authorities, emergency proceed-stop grammars, and the new override-quality dimensions.
- Rebuilt the seed bank around stale-clearance fault classes, replay-quality underwriting, source-drift warranties, and override-misuse forensics.
- Updated the constellation map so conditioned-place governance now includes the override-constitution layer above trigger grammars and so allocation now explicitly includes bounded exception paths.
- Expanded the source register with current OSHA, Pennsylvania 811, USACE, EPA, FEMA, and eCFR material on cautious proceed rights, emergency definitions, direct-contact fallback rules, special emergency permit processing, temporary emergency permits, and floodplain permit continuity under disaster tempo.

### Design decisions
- Promoted `emergency override constitutions become procurement questions` because the archive had already established how determinations are searched, structured, scoped, preserved, and refreshed, but still lacked a dossier on what governs action when those ordinary sufficiency rules have already failed and delay is itself dangerous.
- Treated the key bottleneck as **bounded exception choreography** — not whether rules disappear under pressure, but whether systems can define narrow trigger classes, authority holders, temporary precautions, duration ceilings, and handback obligations strongly enough to act without collapsing into discretionary chaos.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly break-glass-aware.

### Next likely moves
- Promote `stale clearances split into distinct fault classes`.
- Revisit `source-drift warranties become contract language`.
- Test whether `replay-quality grades become underwriting inputs` should be sharpened into a money-facing dossier.

## rev0138 — 2026.03.24.02.53 UTC — tripwire

### Status
Compact continuation revision; broadens the archive by promoting a re-review-trigger-grammar thesis that sits above reliance-scope matrices and below stale-clearance fault classification.

### Added
- New dossier: `02-dossiers/re-review-trigger-grammars-become-procurement-language.md`.
- New source entries: **[S1120]–[S1126]**.

### Changed
- Updated README to reflect the new trigger-grammar layer above reliance-scope matrices.
- Extended the principles with trigger-taxonomy codification, supersession detectability, condition-change observability, rerun-obligation routing, and freshness-boundary legibility as enforceable surfaces.
- Expanded the Speculation Cube to better represent determination-validity substrates plus trigger-taxonomy clarity, supersession detectability, condition-change observability, rerun-obligation routing, and freshness-boundary legibility.
- Rebuilt the seed bank around stale-clearance fault classes, override constitutions, replay-quality underwriting, and source-drift warranties.
- Updated the constellation map so conditioned-place governance now includes the trigger-grammar layer above reliance-scope matrices.
- Expanded the source register with current eCFR, USACE, NRCS, and FEMA material on one-year and 180-day refresh windows, five-year JD validity with early revision on new information, hydrologic and agricultural-activity review triggers, map supersession, and revalidation letters.

### Design decisions
- Promoted `re-review trigger grammars become procurement language` because the archive had already established what determination packages are for and who might accept them, but still lacked a dossier on what events make those packages unsafe to reuse.
- Treated the key bottleneck as **portable freshness logic** — not merely whether a determination once existed, but whether institutions share a usable grammar for elapsed-time expiry, source supersession, changed conditions, changed activities, and rerun obligations.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly freshness-aware.

### Next likely moves
- Promote `stale clearances split into distinct fault classes`.
- Revisit `source-drift warranties become contract language`.
- Test whether `replay-quality grades become underwriting inputs` should be sharpened into a money-facing dossier.

## rev0137 — 2026.03.24.02.49 UTC — scopegrid

### Status
Compact continuation revision; broadens the archive by promoting a reliance-scope-matrix thesis that sits above reliance-grade attestation and below explicit institution-to-institution contracting, routing, and blame.

### Added
- New dossier: `02-dossiers/reliance-scope-matrices-become-procurement-exhibits.md`.
- New source entries: **[S1114]–[S1119]**.

### Changed
- Updated README to reflect the new scope-matrix / transaction-class layer above reliance-grade attestations.
- Extended the principles with transaction-class specificity, scope-exclusion legibility, re-review trigger clarity, determination-profile portability, and out-of-scope misuse resistance as enforceable surfaces.
- Expanded the Speculation Cube to better represent transaction-class specificity, scope-exclusion legibility, re-review trigger clarity, determination-profile portability, and out-of-scope misuse risk.
- Rebuilt the seed bank around stale-clearance fault classes, override constitutions, replay-quality underwriting, and scope-mismatch claims.
- Updated the constellation map so conditioned-place governance now includes the explicit scope-matrix layer above reliance-grade source attestations.
- Expanded the source register with current FEMA, eCFR, USACE, and NRCS material on loan-grade flood determinations, official flood-map sources with supersession risk, approved jurisdictional determinations, and certified wetland determinations tied to distinct downstream uses.

### Design decisions
- Promoted `reliance-scope matrices become procurement exhibits` because the archive had already established who may stand behind a source bundle, but still lacked a dossier on the structured table that says what that bundle is actually sufficient for.
- Treated the key bottleneck as **transaction-class specificity** — not merely whether another institution accepts a package in general, but whether the package is expressly bounded to lending, acquisition, permitting, agricultural compliance, excavation, resale, or later dispute.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly scope-aware.

### Next likely moves
- Promote `replay-quality grades become underwriting inputs`.
- Revisit `stale clearances split into distinct fault classes`.
- Test whether `scope-mismatch claims become a routine liability class` should be sharpened into a dossier on out-of-scope reliance fights.

## rev0136 — 2026.03.24.02.40 UTC — reliancepack

### Status
Compact continuation revision; broadens the archive by promoting a reliance-grade-source-attestation thesis that sits above preserved source snapshots and below lender, insurer, permitting, and acquisition acceptance.

### Added
- New dossier: `02-dossiers/reliance-grade-source-attestations-become-a-service-tier.md`.
- New source entries: **[S1106]–[S1113]**.

### Changed
- Updated README to reflect the new reliance / admissibility layer above source-snapshot escrow.
- Extended the principles with source-authority sufficiency, reliance-scope fit, attestor accountability, and warranty-scope clarity as enforceable surfaces.
- Expanded the Speculation Cube to better represent source-authority sufficiency, reliance-scope fit, warranty-scope clarity, attestor accountability, and admissibility-profile portability.
- Rebuilt the seed bank around stale-clearance fault classes, override constitutions, replay-quality underwriting, and reliance-scope matrices.
- Updated the constellation map so conditioned-place governance now includes the reliance-attestation layer above source-snapshot escrow.
- Expanded the source register with current USGS, EPA, FEMA, eCFR, Pennsylvania DEP, and New York DEC material on authoritative sources, title-search caveats, approximate registries, nightly-updated databases, parcel-specific flood determinations, and environmental-professional qualification rules.

### Design decisions
- Promoted `reliance-grade source attestations become a service tier` because the archive had already established how decision-state bundles are preserved, but still lacked a dossier on what makes another institution accept those bundles as sufficient for a named transaction or liability posture.
- Treated the key bottleneck as **use-case-specific admissibility** — not merely whether a source was checked or preserved, but whether an actor is willing to stand behind that source bundle for lending, redevelopment, permitting, resale, underwriting, or later dispute.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly reliance-aware.

### Next likely moves
- Promote `replay-quality grades become underwriting inputs`.
- Revisit `stale clearances split into distinct fault classes`.
- Test whether `reliance-scope matrices become procurement exhibits` should be sharpened into a dossier on scope-coded warranty products.

## rev0135 — 2026.03.24.02.31 UTC — snapshotvault

### Status
Compact continuation revision; broadens the archive by promoting a source-snapshot-escrow thesis that sits above replay-grade clearance logs and below money-facing claim, resale, and enforcement fights.

### Added
- New dossier: `02-dossiers/source-snapshot-escrow-becomes-liability-tail-infrastructure.md`.
- New source entries: **[S1094]–[S1105]**.

### Changed
- Updated README to reflect the new escrow / preserved-source layer above replay-grade clearance logs.
- Extended the principles with source-snapshot custody and escrow bundles as enforceable surfaces.
- Expanded the Speculation Cube to better represent source-snapshot completeness, snapshot custody separability, live-source drift tolerance, successor-system migration survivability, and decision-state bundle replayability.
- Rebuilt the seed bank around stale-clearance fault classes, override constitutions, replay-quality underwriting, and source-drift warranties.
- Updated the constellation map so conditioned-place governance now includes the escrowed-source layer above incident replay.
- Expanded the source register with current OSHA, Pennsylvania One Call, EPA, New York DEC, and NARA material on digital locate logs, approximate and changeable registries, nightly-refreshed remediation databases, preserved metadata, and migration-safe electronic recordkeeping.

### Design decisions
- Promoted `source-snapshot escrow becomes liability-tail infrastructure` because the archive had already established how work is green-lit and later replayed, but still lacked a dossier on what preserved source bundle makes that replay durable once live systems drift.
- Treated the key bottleneck as **preserved decision-state substrate** — not merely whether a log exists, but whether another institution can later recover the exact external layers, documents, metadata, and custody details that made the decision reasonable at the time.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly snapshot-aware.

### Next likely moves
- Promote `stale clearances split into distinct fault classes`.
- Revisit `replay-quality grades become underwriting inputs`.
- Test whether `source-drift warranties become contract language` should be sharpened into a procurement-facing dossier.

## rev0134 — 2026.03.24.02.23 UTC — claimtrail

Compact continuation revision; broadens the archive by promoting a replay-grade-clearance-log thesis that bridges excavation tickets, one-call response records, retained voice logs, environmental permit recordkeeping, corrective-action logs, and current e-reporting systems into a tighter evidentiary bottleneck.

### Added
- New dossier: `02-dossiers/replay-grade-clearance-logs-become-insurance-evidence.md`.
- New source entries: **[S1086]–[S1093]**.

### Changed
- Updated README to reflect the new incident-replay layer above field-work middleware.
- Extended the principles with clearance-log provenance and replay-oriented enforceable surfaces.
- Expanded the Speculation Cube to better represent ticket-to-work linkage, decision-state reconstructability, source-snapshot custody, stale-clearance detectability, and incident-replay portability.
- Rebuilt the seed bank around stale-clearance fault classes, override constitutions, source-snapshot escrow, and replay-quality underwriting.
- Updated the constellation map so conditioned-place governance now includes the evidentiary replay layer above action-specific green lights.
- Expanded the source register with current Pennsylvania one-call, eCFR, EPA, and PHMSA material on digital ticket logging, indexed record access, permit record retention, standardized corrective-action documentation, legally dependable electronic logs, and electronic permit submissions.

### Design decisions
- Promoted `replay-grade clearance logs become insurance evidence` because the archive had already established how work gets green-lit, but still lacked a dossier on what evidence object decides blame, coverage, and credibility after that green light is challenged.
- Treated the key bottleneck as **reconstructable decision state** — not merely whether an approval existed, but whether institutions can later prove what was checked, what was returned, what had changed, and whether the authorization had gone stale.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly replay-aware.

### Next likely moves
- Promote `stale clearances split into distinct fault classes`.
- Revisit `source-snapshot escrow becomes a vendor feature`.
- Test whether `replay-quality grades become underwriting inputs` should be sharpened into a money-facing dossier.

## rev0133 — 2026.03.24.02.15 UTC — greenlight

Compact continuation revision; broadens the archive by promoting an action-clearance thesis that bridges one-call systems, excavation safety, institutional controls, construction permitting, and fragmented contaminated-site data into a tighter operational bottleneck.

### Added
- New dossier: `02-dossiers/action-clearance-objects-become-field-work-middleware.md`.
- New source entries: **[S1077]–[S1085]**.

### Changed
- Updated README to reflect the new field-work middleware layer above machine-readable restriction objects.
- Extended the principles with dig-safe tickets, permit-to-work releases, and action-specific green-light objects as enforceable surfaces.
- Expanded the Speculation Cube to better represent excavation / drilling / utility-locating domains plus pre-action clearance latency, rule-set snapshot fidelity, clearance replayability, and override governance.
- Rebuilt the seed bank around stale clearances, override design, replay-grade logs, and restriction-quality underwriting.
- Updated the constellation map so conditioned-place governance now includes the operational clearance layer above search and restriction-object ingestion.

## rev0132 — 2026.03.24.02.04 UTC — constraintapi

### Status
Compact continuation revision; broadens the archive by promoting a machine-readable restriction-object thesis that sits above routine parcel search and below full workflow automation.

### Added
- New dossier: `02-dossiers/machine-readable-restriction-objects-become-transaction-middleware.md`.
- New source entries: **[S1072]–[S1076]**.

### Changed
- Updated README to reflect the shift from restriction search alone to transaction-middleware objects.
- Extended the Speculation Cube with restriction-object completeness, geometry-to-document alignment, machine-actionability, workflow-ingestion cost, and exception-encoding quality.
- Rebuilt the seed bank around orphaned controls, control-violation telemetry, restriction-quality grades, and residue-accounting disputes after promoting the restriction-object thesis.
- Expanded the constellation map so both place-governance and maintenance-first infrastructure now include structured restriction objects as an operational layer above search.
- Expanded the source register with official EPA, California DTSC, and New York material on environmental-data modernization, state-data standardization pressure, public search/download surfaces, land-use-restriction sites, and easement-layer publishing.

### Design decisions
- Promoted `machine-readable restriction objects become transaction middleware` because the archive had already established durable restrictions and search layers, but still lacked a dossier on how those restrictions become software-usable inputs for ordinary systems.
- Treated the key bottleneck as **machine-actionable legibility** — not merely whether a control is legally valid or publicly discoverable, but whether it survives as a structured object that underwriting, planning, GIS, and operational systems can reliably ingest.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly object-aware.

### Next likely moves
- Promote `restriction quality grades become underwriting inputs`.
- Revisit `control-violation telemetry becomes a supervisory layer`.
- Test whether `orphaned institutional controls become a public repair backlog` should be reframed as a record-repair and successor-custody dossier.
- Keep pruning for overlap with shadow zoning, routine conveyancing, and post-closure stewardship material.

## rev0131 — 2026.03.24.01.57 UTC — titlemesh

### Status
Compact continuation revision; broadens the archive by promoting a restriction-lookup thesis that bridges shadow zoning, title diligence, environmental registries, and routine parcel search.

### Added
- New dossier: `02-dossiers/restriction-search-infrastructure-becomes-routine-conveyancing.md`.
- New source entries: **[S1066]–[S1071]**.

### Changed
- Updated README to reflect the shift from shadow zoning alone to the lookup layer above it.
- Extended the Speculation Cube with restriction-search latency, registry-reconciliation quality, parcel-boundary precision, document-link completeness, and false-negative risk.
- Rebuilt the seed bank around orphaned controls, control-violation telemetry, discoverability grades, and residue-accounting disputes after promoting the restriction-search thesis.
- Expanded the constellation map so both place-governance and maintenance-first infrastructure now include the search layer that makes conditioned parcels routinely legible.
- Expanded the source register with official EPA, eCFR, Pennsylvania, and New York material on all-appropriate-inquiry requirements, title-search caveats, covenant registries, searchable remediation databases, and multi-program contaminated-site map surfaces.

### Design decisions
- Promoted `restriction-search infrastructure becomes routine conveyancing` because the archive had already established durable land-use restrictions and post-closure stewardship, but still lacked a direct dossier on how ordinary institutions actually find those restrictions fast enough to transact on them.
- Treated the key bottleneck as **transaction-legible discoverability** — not merely whether a restriction is legally valid, but whether it survives as an actionable search result across land records, public registries, parcel maps, and due-diligence workflows.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly search-aware.

### Next likely moves
- Promote `orphaned institutional controls become a public repair backlog`.
- Revisit `control-violation telemetry becomes a supervisory layer`.
- Test whether `restriction discoverability grades become underwriting inputs` deserves a full dossier or should remain nested under routine conveyancing.
- Keep pruning for overlap with shadow zoning, title-search legibility, and post-closure stewardship material.

## rev0130 — 2026.03.24.01.43 UTC — shadowcadastre

### Status
- complete

### Added
- New dossier: `02-dossiers/institutional-controls-become-a-shadow-zoning-layer.md`.
- New source entries: **[S1057]–[S1065]**.

### Changed
- Updated README to center the archive on land-use-control discoverability, title-search legibility, restricted-use continuity, and residual-risk parcel governance.
- Tightened the Speculation Cube so lifecycle-governance prompts now name restriction discoverability, covenant continuity, control enforceability, parcel restrictions, and shadow-cadastre logic as first-class variables.
- Updated the constellation map so place becomes a governing variable now includes conditioned parcels and maintenance outruns novelty now includes land-use-control layers beneath stewardship.
- Rebuilt the seed bank around restriction-search infrastructure, orphaned controls, violation telemetry, and residue accounting.
- Expanded the source register with current EPA, eCFR, NRC, DOE, and EPA OIG material on institutional controls, deed notices, restricted-use license termination, and long-term stewardship.

### Design decisions
- Promoted institutional controls rather than residue-accounting disputes because the archive had already built the chain from retirement proof to closure documents to release packets to aftercare and was ready for the next narrower question of how the place itself remains governed after closure is recognized.
- Kept the move tight by treating the new layer not as generic environmental law, but as shadow zoning: durable place restrictions encoded into title records, covenants, stewardship plans, and regulator-held archives.
- Avoided sprawling into a full contaminated-land or real-estate-policy branch; left restriction-search infrastructure, orphaned controls, violation telemetry, and residue accounting in the seed bank.

### Next likely moves
- Promote restriction-search infrastructure becomes routine conveyancing.
- Test whether orphaned institutional controls deserve a full dossier or should remain nested under shadow zoning, record custody, and public repair.
- Test whether control-violation telemetry deserves a full dossier or should remain nested under enforcement, stewardship, and residual-risk place governance.

## rev0129 — 2026.03.24.01.34 UTC — aftercare

### Status
- complete

### Added
- New dossier: `02-dossiers/post-closure-monitoring-continuity-becomes-a-service-market.md`.
- New source entries: **[S1050]–[S1056]**.

### Changed
- Updated README to center the archive on records-custody continuity, successor-ready stewardship, and monitoring-window transferability.
- Tightened the Speculation Cube so lifecycle-governance prompts now name monitoring-window transferability, records-custody continuity, successor-steward handoff integrity, and site-transition readiness as first-class variables.
- Updated the constellation map so maintenance outruns novelty now includes the stewardship layer above release packets and bond-release evidence.
- Rebuilt the seed bank around residue accounting, closure-document forgery, and monitoring-custody bottlenecks.
- Expanded the source register with current eCFR and DOE material on hazardous-waste and landfill post-closure care, Class VI post-injection monitoring, and DOE long-term stewardship operations.

### Design decisions
- Promoted post-closure monitoring continuity rather than residue-accounting disputes because the archive had already built the chain from retirement proof to portable closure documents to release packets and was ready for the next narrower question of who actually keeps obligations, records, and monitoring alive after nominal closure.
- Kept the move tight by treating the new service layer not as generic maintenance, but as supervised-tail continuity: monitoring, records custody, reporting cadence, land-use controls, and successor handoff.
- Avoided sprawling into a whole environmental-remediation-management branch; left residue accounting, closure-document forgery, and monitoring-custody bottlenecks in the seed bank.

### Next likely moves
- Promote residue-accounting disputes become governance fights.
- Test whether closure-document forgery deserves a full dossier or should remain nested under destruction certificates, release packets, and enforcement design.
- Test whether monitoring-custody records deserve a full dossier or should remain nested under post-closure continuity, information management, and successor transition.

## rev0128 — 2026.03.24.01.26 UTC — releasepack

### Status
- complete

### Added
- New dossier: `02-dossiers/bond-release-evidence-becomes-a-service-tier.md`.
- New source entries: **[S1039]–[S1049]**.

### Changed
- Updated README to center the archive on phased capital release, release-packet audience fit, and post-closure monitoring continuity.
- Tightened the Speculation Cube so lifecycle-governance prompts now name phased capital-release choreography, release-packet audience fit, and post-closure monitoring continuity as first-class variables.
- Updated the constellation map so maintenance outruns novelty now includes the evidence-service layer above portable closure documents.
- Rebuilt the seed bank around residue accounting, closure-document forgery, and post-closure monitoring windows.
- Expanded the source register with current OSMRE, EPA, NRC, and BOEM material on reclamation bonds, hazardous-waste and landfill financial assurance, Class VI site closure, nuclear decommissioning funding, and offshore decommissioning risk.

### Design decisions
- Promoted bond-release evidence rather than residue-accounting disputes because the archive had already built the chain from governed biographies to retirement proof to portable closure documents and was ready for the narrower question of what evidence actually unlocks reserved capital and liability reduction.
- Kept the move tight by treating the service tier not as generic consulting, but as the multi-audience evidence-pack layer that sits between field closure work and financial or regulatory release.
- Avoided sprawling into a whole project-finance or environmental-liability branch; left residue accounting, closure-document forgery, and post-closure monitoring windows in the seed bank.

### Next likely moves
- Promote residue-accounting disputes become governance fights.
- Test whether closure-document forgery deserves a full dossier or should remain nested under destruction certificates, release packets, and enforcement design.
- Test whether post-closure monitoring windows deserve a full dossier or should remain nested under bond-release evidence, long-tail care, and supervised closure.

## rev0127 — 2026.03.24.01.17 UTC — waybill

### Status
- complete

### Added
- New dossier: `02-dossiers/destruction-certificates-become-trade-documents.md`.
- New source entries: **[S1034]–[S1038]**.

### Changed
- Updated README to center the archive on portable closure documents, countersigned manifests, and document-routed exit proof.
- Tightened the Speculation Cube so lifecycle-governance prompts now name closure-document portability, countersignature choreography, and document-routing interoperability as first-class variables.
- Updated the constellation map so maintenance outruns novelty now includes destruction certificates as the documentary layer above retirement proof.
- Rebuilt the seed bank around residue accounting, bond-release evidence, and closure-document forgery.
- Expanded the source register with current EPA, Basel Convention, European Commission, and NIST material on manifests, movement documents, digital waste routing, and sanitization certificates.

### Design decisions
- Promoted destruction certificates rather than residue-accounting disputes because the archive had already built governed object biographies, retirement notices, and retirement proof and was ready for the narrower question of what evidence object another institution can actually route on.
- Kept the move tight by treating the certificate not as generic paperwork, but as the portable control document that can trigger liability release, custody transfer, market acceptance, and closure recognition.
- Avoided sprawling into a full waste-trade or fraud-governance branch; left residue accounting, bond-release evidence, and closure-document forgery in the seed bank.

### Next likely moves
- Promote residue-accounting disputes become governance fights.
- Promote bond-release evidence becomes a service tier.
- Test whether closure-document forgery deserves a full dossier or should remain nested under destruction certificates, retirement proof, and enforcement design.

# Changelog


## rev0166 — 2026.03.28.08.50 UTC — renewalprice

### Status
Compact continuation revision; broadens the archive by promoting an extension-frequency thesis that sits above burn-down-covenant work and below extension-lineage diligence or gate-expiry dispute work.

### Added
- New dossier: `02-dossiers/extension-frequency-penalties-become-underwriting-inputs.md`.
- New source entries: **[S1316]–[S1321]**.

### Changed
- Updated README to reflect the new extension-frequency-penalty layer above residue burn-down covenants and below substitute-control sufficiency scorecards, plus the rebuilt next queue.
- Rebuilt the seed bank around legacy-status transfer attestations, gate-expiry disputes, and extension-lineage disclosures after promoting the renewal-churn pricing thesis.
- Updated the constellation map so conditioned-place governance and maintenance work now explicitly include extension-frequency penalties as a distinct layer between burn-down covenants and scorecard shorthand.
- Extended the principles and Speculation Cube with extension-lineage legibility, rollover-count comparability, expiry-reset visibility, resurfaced-after-accept events, and renewal-churn penalizability so the archive can reason about repeated deadline pushes rather than only current backlog shape.
- Expanded the source register with current FedRAMP, ServiceNow, Microsoft, Tenable, and GitHub material on quarterly progress cycles, configurable multiple-extension counts, due-date governance rules, expiring accept rules, resurfaced findings, and dismissed-alert reopen lineage.

### Design decisions
- Promoted `extension-frequency penalties become underwriting inputs` because the archive had already established residue inventories, burn-down covenants, and comparative scorecards, but still lacked a dossier on the next scarce signal once tolerated incompleteness becomes clocked: how often the same operator keeps asking to move the deadline again.
- Treated the key bottleneck as **renewal-churn legibility** — not merely whether residue exists, nor only how quickly some portion closes, but whether another institution can see repeated extensions, expired tolerances, resurfaced findings, reopened dismissals, and rollover counts clearly enough to price them.
- Kept the revision tight by making one real promotion and only the surrounding edits needed to make the lifecycle-governance lane explicitly sensitive to repeated deadline pushes.

### Next likely moves
- Revisit `legacy-status transfer attestations become closing artifacts`.
- Promote `gate-expiry disputes become a service layer`.
- Test whether `extension-lineage disclosures become diligence exhibits` should sharpen into a dossier on portable renewal-history packets.

## rev0126 — 2026.03.24.01.12 UTC — tailproof

### Status
- complete

### Added
- New dossier: `02-dossiers/retirement-proof-becomes-governance-infrastructure.md`.
- New source entries: **[S1031]–[S1033]**.

### Changed
- Updated README to center this revision on destruction attestations, chain-of-custody closure, decommissioning-proof admissibility, and bond-release evidence.
- Tightened the Speculation Cube so lifecycle-governance prompts now name destruction-attestation credibility, residue accounting, decommissioning-proof admissibility, and bond-release evidence sufficiency as first-class variables.
- Updated the constellation map so maintenance outruns novelty now includes the proof-of-exit layer above cleanup and decommissioning.
- Rebuilt the seed bank around destruction certificates, residue accounting, and bond-release evidence.
- Expanded the source register with current European Commission and BOEM material on verified battery recovery, unsold-goods destruction rules, and offshore decommissioning obligations.

### Design decisions
- Promoted retirement proof rather than destruction certificates because the archive had already built cleanup tails, governed object biographies, retirement notices, and retained lifecycle state and was ready for the narrower question of what evidence another institution will accept as genuine closure.
- Kept the move tight by treating proof not as generic audit obsession, but as the specific closure object that lets regulators, buyers, lenders, insurers, and host communities decide whether a lifecycle tail is still open.
- Avoided sprawling into a whole circular-economy or waste-law branch; left destruction certificates, residue accounting, and bond-release evidence in the seed bank.

### Next likely moves
- Promote destruction certificates become trade documents.
- Promote residue-accounting disputes become governance fights.
- Test whether bond-release evidence deserves a full dossier or should remain nested under retirement proof, decommissioning, and liability-tail governance.

## rev0125 — 2026.03.23.22.59 UTC — gradegate

### Status
- complete

### Added
- New dossier: `02-dossiers/grade-floors-become-procurement-defaults.md`.
- New source entries: **[S1027]–[S1030]**.

### Changed
- Updated README to center the archive on minimum acceptable equivalence, no-weaker-than floors, waiver-needed grades, and grade-backed migration review.
- Tightened the Speculation Cube so managed-legibility prompts now ask when compressed equivalence labels stop being descriptive shorthand and start becoming buyer-side thresholds.
- Updated the constellation map so managed legibility now includes grade floors as the buyer-control layer above semantic-equivalence grades.
- Rebuilt the seed bank around orphan-age metrics, history-export rights, and grade-waiver accountability.
- Expanded the source register with current SLSA, OpenSSF Baseline, and Scorecard material on assurance levels, maturity levels, remediation thresholds, and aggregate risk scoring.

### Design decisions
- Promoted grade floors rather than orphan-age distributions because the archive had already built translation-loss proofs, semantic-equivalence grades, public replay, procurement-facing review, and history-retention terms and was ready for the narrower question of what minimum acceptable grade another institution will actually enforce.
- Kept the move tight by treating the floor not as a generic security rating system but as the specific threshold a buyer can apply to translated trust and evidence policies.
- Avoided sprawling into a whole assurance-level theory; left orphan-age metrics, history-export rights, and waiver accountability in the seed bank.

### Next likely moves
- Promote orphan-age distributions become service metrics.
- Promote history-export rights become continuity clauses.
- Test whether grade-waiver logs deserve a full dossier or should remain nested under grade floors, procurement terms, and exception governance.

## rev0124 — 2026.03.23.22.45 UTC — retainspan

### Status
Compact continuation revision that turns the archive from buyer-readable retained timelines and orphan-state queues toward the contractual question of how long prior state must remain usable for diligence, renewal, and dispute review.

### Added
- New dossier: `02-dossiers/history-retention-floors-become-procurement-terms.md`.
- New source entries: **[S1025]–[S1026]**.

### Changed
- Updated README to center the archive on oldest-queryable-state, exportable-history windows, attribution-preserving retention, and verification continuity.
- Tightened the Speculation Cube so managed-legibility prompts now name history-retention floors, exportable-history windows, and still-verifiable past state as first-class variables.
- Updated the constellation map so managed legibility now includes history-retention floors as the contractual layer above historical-state views and before orphan-state backlogs.
- Rebuilt the seed bank around grade floors, orphan-age metrics, and history-export rights.
- Expanded the source register with current OpenID and NVD material on dated conformance assurance, non-expiring certifications, per-CVE changelogs, and retained remediated or rejected records.

### Design decisions
- Promoted history-retention floors rather than grade floors because the archive had already built historical-state views, retirement markers, procurement-facing evidence, and orphan-state backlogs and was ready for the narrower question of how long those past states must stay usable before another institution can rely on them.
- Kept the move tight by treating retention not as generic storage policy, but as the specific floor on queryable, exportable, attributable, and still-verifiable history that buyers may begin negotiating.
- Avoided sprawling into a full records-management theory; left grade floors, orphan-age metrics, and history-export rights in the seed bank.

### Next likely moves
- Promote grade floors become procurement defaults.
- Promote orphan-age distributions become service metrics.
- Test whether history-export rights deserves a full dossier or should remain nested under retention floors, portability, and provider-exit continuity.


## rev0123 — 2026.03.23.22.31 UTC — orphanqueue

### Status
Compact continuation revision that turns the archive from buyer-readable retained timelines toward the explicit queue of residual states that still need purge, repair, rerouting, or archival classification.

### Added
- New dossier: `02-dossiers/orphan-state-inventories-become-reconciliation-backlogs.md`.
- New source entries: **[S1021]–[S1024]**.

### Changed
- Updated README to center the archive on unresolved residual-state counts, orphan-age distributions, repair ownership, and purge-vs-archive separation.
- Tightened the Speculation Cube so managed-legibility prompts now ask when ecosystems stop treating withdrawn, deleted, deprecated, or source-orphaned records as edge cases and start managing them as explicit repair backlogs.
- Updated the constellation map so managed legibility now includes orphan-state inventories as the operational queue above historical-state views.
- Rebuilt the seed bank around history-retention floors, grade floors, and orphan-age metrics.
- Expanded the source register with current OSV, NVD, and OpenID materials on orphaned records, synchronized product/deprecation inventories, maintained historical subordinate events, and modified-feed synchronization.

### Design decisions
- Promoted orphan-state inventories rather than history-retention floors because the archive had already built retirement markers, successor-gap semantics, historical-state views, and buyer-readable timelines and was ready for the narrower question of who carries the unresolved remainder once those states persist.
- Kept the move tight by treating the orphan inventory not as generic data cleanup, but as the specific backlog object that tracks valid-but-orphaned, rejected-but-visible, deleted-pending-purge, archive-only, and still-unreconciled states.
- Avoided sprawling into a full retention-policy or staffing theory; left history-retention floors, grade floors, and orphan-age metrics in the seed bank.

### Next likely moves
- Promote history-retention floors become procurement terms.
- Promote grade floors become procurement defaults.
- Test whether orphan-age distributions deserves a full dossier or should remain nested under orphan-state inventories, service metrics, and due-diligence review.


## rev0122 — 2026.03.23.22.17 UTC — afterview

### Status
Compact continuation revision that turns the archive from retirement hygiene and semantic-compression work toward buyer-readable timelines of what changed, when, and why.

### Added
- New dossier: `02-dossiers/historical-state-views-become-buyer-due-diligence-surfaces.md`.

### Changed
- Updated README to center the archive on retained state timelines, reason-coded retirements, dated public listings, and buyer-readable history panes.
- Tightened the Speculation Cube so managed-legibility prompts now ask when buyers stop accepting only a current green state and start asking for retained historical-state views.
- Updated the constellation map so managed legibility now includes historical-state views as the review layer above retirement markers and before orphan-state reconciliation.
- Rebuilt the seed bank around orphan-state inventories, grade floors, and history-retention floors.
- Reused the existing source register entries on procurement, audit history, change histories, historical trust artifacts, and dated certification listings rather than adding duplicate IDs.

### Design decisions
- Promoted historical-state views rather than orphan-state inventories because the archive had already built retirement markers, successor-gap semantics, procurement-facing evidence, and timeline-preserving trust artifacts and was ready for the buyer-facing pane that sits above them.
- Kept the move tight by treating the historical view not as generic observability or analytics, but as the specific due-diligence object that compresses prior state transitions into something another institution can review quickly.
- Avoided sprawling into a full retention-policy or data-warehouse branch; left orphan-state inventories, grade floors, and history-retention floors in the seed bank.

### Next likely moves
- Promote orphan-state inventories become reconciliation backlogs.
- Promote grade floors become procurement defaults.
- Test whether history-retention floors deserves a full dossier or should remain nested under historical-state views, procurement review, and retirement hygiene.


## rev0121 — 2026.03.23.22.03 UTC — equivtag

### Status
Compact continuation revision that turns the archive from full semantic-drift proofs toward compressed equivalence labels that ordinary migration and procurement workflows can actually govern by.

### Added
- New dossier: `02-dossiers/semantic-equivalence-grades-become-migration-shorthand.md`.
- New source entries: **[S1015]–[S1020]**.

### Changed
- Updated README to center the archive on exact-vs-stricter-vs-weaker labels, partial comparability, non-comparable translations, and grade-backed migration review.
- Tightened the Speculation Cube so managed-legibility prompts now ask when ecosystems stop reading full migration proofs every time and start governing by compressed equivalence labels instead.
- Updated the constellation map so managed legibility now includes semantic-equivalence grades as the compression layer above translation-loss proofs and before broader procurement or public-result use.
- Rebuilt the seed bank around orphan-state inventories, historical-state views, and grade floors.
- Expanded the source register with current Trivy, Sigstore, Kyverno, and Ratify documentation to ground the archive’s new emphasis on compressed equivalence classes above full proof objects.

### Design decisions
- Promoted semantic-equivalence grades rather than orphan-state inventories because the archive had already built trust-policy portability, translation intermediaries, replay surfaces, public result matrices, regression alerts, disclosure windows, and translation-loss proofs and was ready for the summary layer that makes those proofs governable at ordinary review speed.
- Kept the move tight by treating grades not as a generic scoring fad but as the specific shorthand that compresses a full semantic-drift proof into a reusable governance signal.
- Avoided sprawling into a full procurement language branch; left orphan-state inventories, historical-state views, and grade floors in the seed bank.

### Next likely moves
- Promote historical-state views become buyer due-diligence surfaces.
- Promote grade floors become procurement defaults.
- Test whether orphan-state inventories deserves a full dossier or should remain nested under successor gaps, retirement notices, and historical-state review.

## rev0120 — 2026.03.23.21.44 UTC — closemark

### Status
Compact continuation revision; keeps the archive tight while extending the security-evidence / legibility cluster.

### Added
- New dossier: `02-dossiers/regression-retirement-markers-become-evidence-hygiene.md`.

### Changed
- Updated README to foreground regression-retirement markers as the next hygiene layer after disclosure windows and successor-gap semantics.
- Extended the Speculation Cube with resolved-vs-withdrawn labels, retirement timestamps, and historical-only notice flags.
- Refreshed the constellation map so managed legibility now explicitly includes post-alert closure semantics.
- Rebuilt the seed bank around semantic-equivalence grades, orphan-state inventories, and historical-state views.
- Expanded the source register with new sources on audit-change events, retired / reversed CVE states, historical-key revocation reasons, and vulnerability notifications for removed findings.

### Design decisions
- Promoted regression-retirement markers instead of semantic-equivalence grades because the archive already had strong signals that closure state is becoming machine-actionable across multiple ecosystems.
- Kept the dossier focused on notice lifecycle and evidence hygiene rather than broadening into generic ticketing or incident-management theory.
- Treated explicit retirement as a higher-value layer than silent disappearance because historical verification and downstream automation now depend on that distinction.

### Next likely moves
- Promote semantic-equivalence grades become migration shorthand.
- Test whether historical-state views deserve a separate dossier or should stay nested under retirement hygiene.
- Keep pruning seeds that fail to name a concrete control surface.

## rev0119 — 2026.03.23.21.26 UTC — gapsignal

### Status
Compact continuation revision; extends the archive’s remap / retirement / legibility lane by naming the operational meaning of missing successors.

### Added
- New dossier: `02-dossiers/successor-gap-reason-codes-become-operator-signals.md`.

### Changed
- Updated README to reflect the new successor-gap-reason-code thesis and revision metadata.
- Extended the Speculation Cube with unresolved-successor markers, contested-replacement states, archive-only continuation flags, and gap-reason visibility.
- Tightened the managed-legibility constellation so successor brokerage now includes explicit reason codes for unresolved handoffs, not only freshness and continuity.
- Rebuilt the seed bank around regression-retirement markers, semantic-equivalence grades, and orphan-state inventories.
- Expanded the source register with NVD, CVE, OSV, and Red Hat materials on rejection reasons, deleted/orphaned records, and advisory invalidation.

### Design decisions
- Promoted successor-gap reason codes rather than semantic-equivalence grades because the archive’s current remap lane still had an interpretive hole around what a missing successor means operationally.
- Treated the core problem as action routing, not taxonomy neatness: the value is telling downstream systems whether to purge, follow a duplicate, consult archives, wait for repair, or escalate.
- Kept the move compact by editing only the map files that sharpen the successor / retirement cluster rather than spawning a larger new branch.

### Next likely moves
- Promote regression-retirement markers into a full dossier.
- Test whether semantic-equivalence grades deserve promotion or should remain nested under translation-loss proofs.
- Explore whether orphan-state inventories deserve a separate dossier or should remain subordinate to successor-gap reasoning.

## rev0118 — 2026.03.23.21.08 UTC — diffwitness

### Status
Compact continuation revision that turns the archive from cross-engine policy translation toward explicit evidence about what that translation preserved, weakened, tightened, or failed to carry.

### Added
- New dossier: `02-dossiers/translation-loss-proofs-become-an-audit-surface.md`.
- New source entries: **[S993]–[S1000]**.

### Changed
- Updated README to center the archive on semantic-drift manifests, equivalence grades, response-shape dependence, and case-backed migration approval.
- Tightened the Speculation Cube so managed-legibility prompts now ask when interoperability is no longer satisfied by translation alone and starts requiring explicit proof of what semantic residue remained.
- Updated the constellation map so managed legibility now includes translation-loss proofs as the audit layer above trust-bundle translators.
- Rebuilt the seed bank around successor-gap reason codes, regression-retirement markers, and semantic-equivalence grades.
- Expanded the source register with Trivy, Sigstore, Kyverno, and Ratify material on ordered priority, match defaults, policy reports, provider-specific success semantics, and versioned verification responses.

### Design decisions
- Promoted translation-loss proofs rather than successor-gap reason codes because the archive had already built portable trust bundles, translation intermediaries, replay fixtures, public result matrices, and regression governance, and was ready for the narrower question of how a translation becomes inspectable enough to audit.
- Kept the move tight by treating the proof not as a generic migration log but as the specific artifact that declares preserved, tightened, weakened, reordered, and unresolved semantics across unlike policy engines.
- Avoided sprawling into a full certification or legal-liability program; left successor-gap reason codes, regression-retirement markers, and equivalence-grade shorthand in the seed bank.

### Next likely moves
- Promote successor-gap reason codes become operator signals.
- Test whether regression-retirement markers deserves a full dossier or should remain nested under regression-disclosure windows, conformance-regression alerts, and machine-readable retirement notices.
- Test whether semantic-equivalence grades deserves a full dossier or should remain nested under translation-loss proofs, public replay-result matrices, and buyer-facing scoreboards.

## rev0117 — 2026.03.23.20.56 UTC — windowrule

### Status
Compact continuation revision that turns the archive from routed downgrade alerts toward governed disclosure timing, audience, and retirement rules for those regressions.

### Added
- New dossier: `02-dossiers/regression-disclosure-windows-become-a-governance-surface.md`.
- New source entries: **[S990]–[S992]**.

### Changed
- Updated README to center the archive on batching rules and disclosure-window governance above contract-trigger alerts.
- Tightened the Speculation Cube so managed-legibility prompts now ask when a visible regression stops being merely detectable and starts needing explicit rules for confirmation, batching, and notice retirement.
- Updated the constellation map so managed legibility now includes regression-disclosure windows as the governance layer above alerting and before longer-lived retirement and remap regimes.
- Rebuilt the seed bank around translation-loss proofs, successor-gap reason codes, and regression-retirement markers.
- Expanded the source register with Docker Scout notification-boundary documentation and OpenID material on result-reporting policy and public certification listings.

### Design decisions
- Promoted regression-disclosure windows rather than translation-loss proofs because the archive had already built replay fixtures, public matrices, downgrade alerts, buyer review, and freshness logic and was ready for the narrower question of when a detected regression must become an official notice.
- Kept the move tight by treating the disclosure window not as generic incident response but as the specific governed span that decides confirmation thresholds, batching rights, audience scope, and notice-retirement conditions.
- Avoided sprawling into a full communications-policy theory; left translation-loss proofs, successor-gap reason codes, and regression-retirement markers in the seed bank.

### Next likely moves
- Promote translation-loss proofs become an audit surface.
- Test whether successor-gap reason codes deserves a full dossier or should remain nested under successor-map freshness, retirement notices, and migration infrastructure.
- Test whether regression-retirement markers deserves a full dossier or should remain nested under regression-disclosure windows, conformance-regression alerts, and machine-readable retirement notices.

## rev0116 — 2026.03.23.20.55 UTC — maptempo

### Status
Compact continuation revision that turns the archive from successor brokerage toward measurable lag and freshness guarantees on the handoff layer itself.

### Added
- New dossier: `02-dossiers/successor-map-freshness-guarantees-become-a-service-metric.md`.
- New source entries: **[S987]–[S989]**.

### Changed
- Updated README to center the archive on map-lag budgets, last-validated successor timestamps, staleness disclosure, and freshness-class signaling.
- Tightened the Speculation Cube so managed-legibility prompts now ask when remap layers stop being mere lookup aids and start needing explicit freshness guarantees.
- Updated the constellation map so managed legibility now includes successor-map freshness as the reliability layer above successor-map brokers and before broader migration intermediation.
- Rebuilt the seed bank around regression-disclosure windows, translation-loss proofs, and successor-gap reason codes.
- Expanded the source register with NVD maintenance guidance, OSV incremental-download documentation, and Red Hat's security-data changelog to ground the archive's new emphasis on update tempo and lag visibility.

### Design decisions
- Promoted successor-map freshness rather than regression-disclosure windows because the archive had already built retirement notices, successor brokers, continuity layers, replay surfaces, and contract-trigger logic and was ready for the narrower question of when a handoff map is recent enough to trust.
- Kept the move tight by treating freshness not as a generic data-quality virtue but as the specific service property of a maintained remap layer that downstream automation may already rely on.
- Avoided sprawling into a full observability program; left regression-disclosure windows, translation-loss proofs, and successor-gap reason codes in the seed bank.

### Next likely moves
- Promote regression-disclosure windows become a governance surface.
- Promote translation-loss proofs become an audit surface.
- Test whether successor-gap reason codes deserves a full dossier or should remain nested under successor-map freshness, retirement notices, and migration tooling.

## rev0115 — 2026.03.23.20.40 UTC — policybridge

### Status
Compact continuation revision that turns the archive from portable trust bundles toward preserved trust intent across unlike policy engines.

### Added
- New dossier: `02-dossiers/trust-bundle-translators-become-interoperability-intermediaries.md`.
- New source entries: **[S983]–[S986]**.

### Changed
- Updated README to center the archive on policy-intent preservation, translation-loss visibility, engine-specific semantic drift, and portable trust-policy migration.
- Tightened the Speculation Cube so managed-legibility prompts now ask when trust policy stops being portable enough as a bundle and starts requiring maintained translation across incompatible engines.
- Updated the constellation map so managed legibility now includes trust-bundle translators as the bridge layer above signer-trust profiles and alongside compatibility shims.
- Rebuilt the seed bank around successor-map freshness guarantees, regression-disclosure windows, and translation-loss proofs.
- Expanded the source register with Kyverno and Ratify material on attestors, signature-vs-attestation policy structure, provider models, runtime overrides, and policy-provider composition.

### Design decisions
- Promoted trust-bundle translators rather than successor-map freshness because the archive had already built signer independence, trust bundles, public replay, migration brokers, and downgrade watch layers and was ready for the bridge that keeps the same trust intent alive across unlike engines.
- Kept the move tight by treating the translator not as a generic file converter but as the specific intermediary that maps admissibility logic while declaring what semantics were preserved, approximated, or dropped.
- Avoided sprawling into a full certification regime; left successor-map freshness, regression-disclosure windows, and translation-loss proofs in the seed bank.

### Next likely moves
- Promote successor-map freshness guarantees become a service metric.
- Promote regression-disclosure windows become a governance surface.
- Test whether translation-loss proofs deserves a full dossier or should remain nested under trust-bundle translators, public replay-result matrices, and procurement-facing conformance review.

## rev0114 — 2026.03.23.20.26 UTC — tripwire

### Status
Compact continuation revision that turns the archive from public replay-result visibility toward routed downgrade signals that buyers may start treating as service events.

### Added
- New dossier: `02-dossiers/conformance-regression-alerts-become-contract-triggers.md`.
- New source entries: **[S978]–[S982]**.

### Changed
- Updated README to center the archive on downgrade visibility, regression-alert latency, notice semantics, and contract-relevant thresholding.
- Tightened the Speculation Cube so managed-legibility prompts now ask when a pass/fail downgrade stops being a comparison detail and starts becoming a routed event with remedy-clock semantics.
- Updated the constellation map so managed legibility now includes conformance-regression alerts as the watch layer above public replay-result matrices.
- Rebuilt the seed bank around trust-bundle translators, successor-map freshness guarantees, and regression-disclosure windows.
- Expanded the source register with Dependency-Track and OpenID material on notifications, automated response, published conformance logs, and public interoperability pass-rate reporting.

### Design decisions
- Promoted conformance-regression alerts rather than trust-bundle translators because the archive had already built replay fixtures, public result matrices, procurement-facing review, and notification plumbing and was ready for the moment when a visible downgrade starts to matter commercially.
- Kept the move tight by treating the alert as the specific watch-and-escalation layer over named cases, not as a generic incident-management or SLA theory.
- Avoided sprawling into full contract-language analysis; left trust-bundle translation and successor-map freshness in the seed bank.

### Next likely moves
- Promote trust-bundle translators become interoperability intermediaries.
- Promote successor-map freshness guarantees become a service metric.
- Test whether regression-disclosure windows deserves a full dossier or should remain nested under conformance-regression alerts, public replay-result matrices, and procurement-facing scoreboards.

## rev0113 — 2026.03.23.20.14 UTC — handoffmap

### Status
Compact continuation revision that turns the archive from retirement-state signaling toward maintained remap layers that tell downstream systems what now governs.

### Added
- New dossier: `02-dossiers/successor-map-brokers-become-migration-infrastructure.md`.
- New source entries: **[S973]–[S977]**.

### Changed
- Updated README to center the archive on cross-ecosystem remap chains, migration handoff confidence, and successor freshness.
- Tightened the Speculation Cube so managed-legibility prompts now ask when retirement pointers stop being enough and maintained successor maps become the real coordination layer.
- Updated the constellation map so managed legibility now includes successor-map brokers as the migration layer above retirement notices and before full translation intermediation.
- Rebuilt the seed bank around conformance-regression alerts, trust-bundle translators, and successor-map freshness guarantees.
- Expanded the source register with NVD and OSV material on deprecated-to chains, withdrawn and upstream relations, duplicate-record replacement instructions, and incremental change tracking.

### Design decisions
- Promoted successor-map brokers rather than conformance-regression alerts because the archive had already built retirement notices, portability, replay, precedence, trust policy, and continuity layers and was ready for the maintained handoff layer that tells buyers what replaces what.
- Kept the move tight by treating the broker not as a generic migration consultancy but as the specific remap service that reconciles retirement, alias, upstream, duplicate, and replacement signals into actionable successor chains.
- Avoided sprawling into a full standards-translation program; left conformance-regression alerts and trust-bundle translators in the seed bank.

### Next likely moves
- Promote conformance-regression alerts become contract triggers.
- Promote trust-bundle translators become interoperability intermediaries.
- Test whether successor-map freshness guarantees deserves a full dossier or should remain nested under successor-map brokers, continuity, and public replay-result matrices.

## rev0112 — 2026.03.23.20.02 UTC — trustbundle

### Status
Compact continuation revision that turns the archive from signer differentiation toward portable trust-policy expression.

### Added
- New dossier: `02-dossiers/signer-trust-profiles-become-portable-policy-bundles.md`.
- New source entries: **[S964]–[S972]**.

### Changed
- Updated README to center the archive on portable trust policy, signer-class allowlists, repository-order defaults, and policy-bundle translation.
- Tightened the Speculation Cube so managed-legibility prompts now ask when signer trust stops being a hidden local setting and becomes a reusable policy object.
- Updated the constellation map so managed legibility now includes signer-trust profiles as the operational layer between independent signers and local trust overrides.
- Rebuilt the seed bank around successor-map brokers, conformance-regression alerts, and trust-bundle translators.
- Expanded the source register with OpenSSF, Trivy, Aqua, OpenVEX, Sigstore, and Docker material on repository priority, multi-party trust, policy-controller resources, sample trust policies, and attestation-driven validation.

### Design decisions
- Promoted signer-trust profiles rather than successor-map brokers because the archive had already built signer independence, precedence, portability, and public result surfaces and was ready for the layer that operationalizes whose statements count across tools.
- Kept the move tight by treating trust profiles not as a generic PKI or policy-engine topic but as the specific portable bundle that packages admissible signer classes, roots, repositories, and countersignature defaults.
- Avoided bloating the archive into a full trust-distribution program; left successor mapping, regression alerts, and trust-bundle translation in the seed bank.

### Next likely moves
- Promote successor-map brokers become migration infrastructure.
- Promote conformance-regression alerts become contract triggers.
- Test whether trust-bundle translators deserves a full dossier or should remain nested under signer-trust profiles, local overrides, and compatibility shims.

## rev0111 — 2026.03.23.19.46 UTC — passgrid

### Status
Compact continuation revision that turns the archive from executable proof objects toward public comparison surfaces that buyers can scan faster than raw artifacts.

### Added
- New dossier: `02-dossiers/public-replay-result-matrices-become-a-buyer-shortcut.md`.
- New source entries: **[S961]–[S963]**.

### Changed
- Updated README to center the archive on public pass/fail compression, named-fixture comparison, regression visibility, and result-governance fights.
- Tightened the Speculation Cube so managed-legibility prompts now ask when a replayable support claim hardens into a public buyer-facing matrix rather than remaining a private proof bundle.
- Updated the constellation map so managed legibility now includes public replay-result matrices as the compression layer above replay fixtures and alongside public result registries and scoreboards.
- Rebuilt the seed bank around successor-map brokers, signer-trust profiles, and conformance-regression alerts.
- Expanded the source register with Docker and Dependency-Track material on signed test attestations, scanner comparison, and public badge-like result surfaces.

### Design decisions
- Promoted public replay-result matrices rather than successor-map brokers because the archive had already built portability, precedence, propagation, replay, retirement, and signer-independence layers and was ready for the public compression surface that sits above raw proof artifacts.
- Kept the move tight by treating the matrix as a buyer shortcut over named replay fixtures, not as a general dashboard or benchmarking program.
- Avoided sprawling into a full certification-registry program; left successor mapping and signer-trust policy bundles in the seed bank.

### Next likely moves
- Promote signer-trust profiles become portable policy bundles.
- Promote successor-map brokers become migration infrastructure.
- Test whether conformance-regression alerts deserves a full dossier or should remain nested under public replay-result matrices and public result registries.

## rev0110 — 2026.03.23.19.29 UTC — countersign

### Status
Compact continuation revision that turns the archive from retirement-state signaling toward signer-class differentiation and credibility layering for machine-readable exception claims.

### Added
- New dossier: `02-dossiers/independent-exception-signers-become-a-credibility-premium.md`.
- New source entries: **[S958]–[S960]**.

### Changed
- Updated README to center the archive on signer independence, countersignature value, signer-class visibility, and trust-profile policy bundles.
- Tightened the Speculation Cube so managed-legibility prompts now ask when a signed exception claim stops being judged only by format and starts being judged by signer independence and accountability.
- Updated the constellation map so managed legibility now includes signer independence as the trust-tier layer above portability and precedence.
- Rebuilt the seed bank around public replay-result matrices, successor-map brokers, and signer-trust policy bundles.
- Expanded the source register with NTIA/CISA and Docker material on third-party VEX authorship, signed attestations, derivative-image attestations, and downstream verification against published keys.

### Design decisions
- Promoted independent exception signers rather than public replay-result matrices because the archive had already built portability, precedence, propagation, replay, and retirement layers and was ready to distinguish self-issued machine-readable claims from separately accountable signed claims.
- Kept the move tight by treating signer independence not as a generic PKI or identity topic but as the specific credibility premium that appears once portable exception objects start affecting procurement, trust policy, and scanner-visible truth.
- Avoided bloating the archive into a full trust-market program; left signer-trust profiles and public replay matrices in the seed bank.

### Next likely moves
- Promote public replay-result matrices become a buyer shortcut.
- Promote successor-map brokers become migration infrastructure.
- Test whether signer-trust profiles deserves a full dossier or should remain nested under signer independence, precedence, and local trust policy.

## rev0109 — 2026.03.23.19.17 UTC — sunsettag

### Status
Compact continuation revision that turns the archive from executable support proof toward explicit end-of-life signaling for machine-readable evidence.

### Added
- New dossier: `02-dossiers/machine-readable-retirement-notices-become-a-buyer-control-surface.md`.
- New source entries: **[S952]–[S957]**.

### Changed
- Updated README to center the archive on tombstone records, successor mapping, archive pointers, and buyer-side retirement control.
- Tightened the Speculation Cube so managed-legibility prompts now ask when a feed, format, or evidence source stops governing and how downstream systems learn that fact in machine-readable form.
- Updated the constellation map so managed legibility now includes retirement notices as the exit layer after publication, portability, precedence, propagation, replay, and continuity.
- Rebuilt the seed bank around independent signers, public replay-result matrices, and successor-map brokers.
- Expanded the source register with Red Hat, NVD, Docker, and OASIS material on deletions, archives, rejected records, deprecation windows, download horizons, and formal supersession.

### Design decisions
- Promoted machine-readable retirement notices rather than independent signers because the archive had already built publication, portability, precedence, propagation, replay, and continuity layers and was ready for the explicit end-of-life layer above them.
- Kept the move tight by treating retirement notices not as generic product deprecation chatter but as the structured object that tells buyers when a relied-on evidence source has stopped governing and how to preserve continuity.
- Avoided sprawling into a full migration-governance program; left successor-map brokers and adjacent translation services in the seed bank.

### Next likely moves
- Promote independent exception signers become a credibility premium.
- Promote public replay-result matrices become a buyer shortcut.
- Test whether successor-map brokers deserves a full dossier or should remain nested under retirement notices, continuity, and compatibility shims.

## rev0108 — 2026.03.23.19.03 UTC — proofpack

### Status
Compact continuation revision that turns the archive from propagation assurance toward executable proof of support.

### Added
- New dossier: `02-dossiers/suppression-replay-fixtures-become-a-conformance-artifact.md`.
- New source entries: **[S948]–[S951]**.

### Changed
- Updated README to center the archive on executable support claims, before/after proof bundles, and fixture-backed procurement review.
- Tightened the Speculation Cube so managed-legibility prompts now ask when a portable exception claim hardens into a replayable conformance pack.
- Updated the constellation map so managed legibility now includes replay fixtures as the proving-ground layer after publication, portability, precedence, and propagation.
- Rebuilt the seed bank around retirement notices, independent signers, and public replay-result matrices.
- Expanded the source register with Dependency-Track, Trivy, OpenVEX, and VEX Repository Specification material on audit trails, OCI-attestation discovery, repository packaging, and validator-friendly exception objects.

### Design decisions
- Promoted suppression-replay fixtures rather than retirement notices because the archive had already built publication, portability, precedence, and propagation layers and was ready for the executable-proof layer above them.
- Kept the move tight by treating replay fixtures not as a separate testing domain but as the compact artifact that makes supplier support claims inspectable and comparable.
- Avoided bloating the archive into a full conformance-suite program; the dossier stays focused on small proof bundles and the buyer surfaces they could reshape.

### Next likely moves
- Promote machine-readable retirement notices become a buyer-control surface.
- Promote independent exception signers become a credibility premium.
- Test whether public replay-result matrices deserves a full dossier or should remain nested under public conformance-result registries and scanner competition.

## rev0107 — 2026.03.23.18.54 UTC — syncproof

### Status
Compact continuation revision that turns the archive from exception publication and precedence toward downstream propagation assurance.

### Added
- New dossier: `02-dossiers/suppression-propagation-audits-become-a-procurement-checklist.md`.

### Changed
- Updated README to center the archive on suppression propagation, report exclusion, external metrics, and procurement-facing assurance.
- Tightened the Speculation Cube so managed-legibility prompts now ask when buyers start demanding proof that a judgment propagates into dashboards, reports, and policy gates.
- Updated the constellation map so managed legibility now includes suppression propagation as the assurance layer after portability, precedence, and ingestion.
- Rebuilt the seed bank around retirement notices, independent signers, and suppression-replay fixtures.
- Expanded the source register with procurement, bi-directional VEX exchange, suppression-output visibility, and report-exclusion workflow sources.

### Design decisions
- Promoted suppression-propagation audits rather than retirement notices because the archive had already built portability, precedence, and scanner-ingestion layers and was ready for the buyer-assurance layer above them.
- Kept the move tight by treating procurement not as a separate domain but as the place where propagation reliability becomes legible and enforceable.
- Avoided adding a separate file on replay fixtures; left that as the top seed for the next revision.

### Next likely moves
- Promote suppression-replay fixtures become a conformance artifact.
- Promote machine-readable retirement notices become a buyer-control surface.
- Test whether independent exception signers deserves a full dossier or should remain nested under precedence and credibility.

## rev0106 — 2026.03.23.18.39 UTC — claimorder

### Status
Compact widening revision; shifts the archive from portable exception objects toward the precedence regime that appears once several credible actors can publish machine-readable applicability judgments about the same finding and product.

### Added
- New dossier: `02-dossiers/exception-author-precedence-becomes-a-governance-surface.md`.
- New source entries: **[S940]–[S943]**.

### Changed
- Updated README to reflect the new exception-author-precedence / governance-surface front and refreshed the next-queue summary.
- Extended the Speculation Cube with explicit attention to conflicting signed judgments, source-priority order, and override rights around portable exception handling.
- Updated the constellation map so managed legibility now explicitly includes exception-author precedence between portable exception objects and scanner-visible competition.
- Rebuilt the seed bank around suppression-propagation audits, machine-readable retirement notices, and signer-independence credibility after promoting the exception-author-precedence thesis.
- Expanded the source register with Trivy, VEX Hub, and OpenVEX material on multi-method priority, repository ordering, trust models, third-party statement adoption, and multi-stakeholder merge workflows.

### Why it matters
A growing share of machine-readable exception work no longer turns on whether a judgment exists or can travel. The harder question is whose judgment governs when several of them arrive at once. Once precedence rules decide visible scanner truth, author hierarchy and override legitimacy start behaving like governance surfaces rather than like minor configuration details.

## rev0105 — 2026.03.23.18.28 UTC — caseport

### Status
Compact widening revision; shifts the archive from evidence-continuity and escrow concerns toward the transport layer that lets a reviewed applicability judgment travel as a reusable artifact across registries, provenance chains, repositories, scanners, and audits.

### Added
- New dossier: `02-dossiers/reusable-exception-case-objects-become-a-portability-layer.md`.
- New source entries: **[S934]–[S939]**.

### Changed
- Updated README to reflect the new portable-exception-object / portability-layer front and refreshed the next-queue summary.
- Extended the Speculation Cube with exception-object portability, author precedence, and cumulative-exception semantics around machine-readable applicability judgments.
- Updated the constellation map so managed legibility now explicitly includes portable exception objects between adjudication and scanner-visible competition.
- Rebuilt the seed bank around suppression-propagation audits, machine-readable retirement notices, and exception-author precedence after promoting the portable-exception-object thesis.
- Expanded the source register with OpenVEX, Docker, and Trivy material on standard exception documents, signed attestations, exported VEX files, custom repositories, and repository priority.

### Why it matters
A growing share of vulnerability-management work no longer ends when someone decides a finding is not affected. The harder question is whether that judgment can travel. Once reviewed exception logic moves as a reusable object instead of remaining trapped inside one tool, portability itself becomes a new governance and interoperability layer.

## rev0104 — 2026.03.23.18.10 UTC — escrowmesh

### Status
Compact widening revision; shifts the archive from scanner-visible competition over supplier evidence toward the continuity layer that keeps that evidence retrievable across outages, migrations, retired endpoints, and silent disappearance.

### Added
- New dossier: `02-dossiers/feed-escrow-continuity-services-become-a-new-intermediary-market.md`.
- New source entries: **[S925]–[S933]**.

### Changed
- Updated README to reflect the new feed-escrow-continuity / intermediary-market front and refreshed the next-queue summary.
- Extended the Speculation Cube with internal mirrors, self-hosted repositories, escrow archives, deletion notices, historical replayability, retirement-overlap sufficiency, and continuity-broker trust around machine-readable security evidence.
- Updated the constellation map so managed legibility now explicitly includes evidence survivability and replayable retrieval above feed uptime, applicability adjudication, and scanner competition.
- Rebuilt the seed bank around reusable exception-case objects, suppression-propagation audits, and machine-readable retirement notices after promoting the feed-escrow-continuity thesis.
- Expanded the source register with Anchore, Trivy, Ubuntu, Red Hat, and NVD material on status pages, self-hosting, mirrors, retired-data archives, changelogs, and feed synchronization logic.

### Why it matters
A growing share of supplier security evidence now matters not only while the original endpoint is healthy, but later, under stress, and after change. Once audits, scanners, and incident teams need replayable retrieval rather than mere present-tense access, continuity preservation starts behaving like its own market layer rather than like a small implementation detail.

## rev0103 — 2026.03.23.18.08 UTC — scanrank

### Status
Compact widening revision; shifts the archive from supplier-side applicability adjudication toward the market-ranking layer that appears once buyers start noticing which vendor evidence actually changes mainstream scanner and downstream-platform output.

### Added
- New dossier: `02-dossiers/scanner-ingestion-scoreboards-become-a-vendor-competition-surface.md`.
- New source entries: **[S919]–[S924]**.

### Changed
- Updated README to reflect the new scanner-ingestion-scoreboard / vendor-competition-surface front and refreshed the next-queue summary.
- Extended the Speculation Cube with scanner support matrices, ingestion test fixtures, suppression-propagation fidelity, cross-tool count comparability, and scoreboard visibility around machine-readable security evidence.
- Updated the constellation map so managed legibility now explicitly includes scanner-ingestion performance as a ranking layer above publication, freshness, feed continuity, and applicability adjudication.
- Rebuilt the seed bank around feed-escrow continuity services, reusable exception-case objects, and suppression-propagation audits after promoting the scanner-ingestion-scoreboard thesis.
- Expanded the source register with Docker, Trivy, and Dependency-Track material on VEX support, automatic exception handling, repository-based ingestion, downstream metric propagation, and audit trails.

### Why it matters
A growing share of supplier security evidence now lives or dies commercially on whether buyer toolchains actually honor it. Once visible scanner counts, CI gates, and downstream dashboards change differently across tools, ingestion quality starts behaving like a supplier-quality surface rather than like a mere implementation detail.

## rev0102 — 2026.03.23.17.54 UTC — appealdesk

### Status
Compact widening revision; shifts the archive from feed continuity and supplier evidence delivery toward the adjudication layer that resolves live disagreement when scanner findings and supplier status still do not match.

### Added
- New dossier: `02-dossiers/applicability-appeals-become-a-standing-supplier-support-function.md`.
- New source entries: **[S913]–[S918]**.

### Changed
- Updated README to reflect the new applicability-appeals / supplier-support-function front and refreshed the next-queue summary.
- Extended the principles with false-positive workflows, applicability-dispute triage, supplier-support adjudication, and archived-resolution portability as first-class variables around machine-readable evidence use.
- Extended the Speculation Cube with allowlists, approval links, supplier-support cases, and reusable resolution artifacts around security-status disagreement.
- Updated the constellation map so managed legibility now explicitly includes applicability-adjudication workflow beneath backport proof, VEX freshness, feed continuity, and scanner trust.
- Rebuilt the seed bank around scanner-ingestion scoreboards, feed-escrow continuity services, and reusable exception-case objects after promoting the applicability-appeals thesis.
- Expanded the source register with RHACS exception-management and scanner-difference material, Anchore allowlist documentation, Ubuntu’s false-positive FAQ, and Red Hat support guidance for scanner-to-vendor discrepancy cases.

### Why it matters
A growing share of vulnerability-management work now happens after machine-readable status is already available. Once buyers still need to contest, defer, or validate scanner findings against supplier evidence, the scarce capability shifts toward adjudication: who can review the mismatch, state a rationale, approve an exception, and leave behind evidence that others can trust later?

## rev0101 — 2026.03.23.17.44 UTC — feedduty

### Status
Compact widening revision; shifts the archive from freshness and admissibility of supplier security claims toward the continuity obligations of the feed layer that delivers those claims into scanners, certifications, and procurement workflows.

### Added
- New dossier: `02-dossiers/security-feed-uptime-obligations-become-supplier-grade-commitments.md`.
- New source entries: **[S909]–[S912]**.

### Changed
- Updated README to reflect the new security-feed-uptime / supplier-grade-commitment front and refreshed the next-queue summary.
- Extended the principles with feed-availability commitments, outage-notice quality, mirror coverage, and cache-staleness control as first-class variables around machine-readable evidence delivery.
- Extended the Speculation Cube with status pages, mirror services, fallback distribution, outage-communication quality, and mirror-coverage depth around operated security-data feeds.
- Updated the constellation map so managed legibility now explicitly includes feed continuity as a recurring layer beneath VEX freshness, backport proof, and scanner trust.
- Rebuilt the seed bank around applicability appeals, scanner-ingestion scoreboards, and feed-escrow continuity services after promoting the security-feed-uptime thesis.
- Expanded the source register with Red Hat certification and scanner material, Anchore feed-operations documentation, and NIST’s framing of NVD as cybersecurity infrastructure.

### Why it matters
A growing share of supplier security evidence now matters only if it can actually be retrieved, synchronized, and trusted at decision time. Once scanners, buyers, and assurance programs depend on live evidence channels, feed continuity starts behaving like part of the supplier obligation rather than like optional documentation hygiene.

## rev0100 — 2026.03.23.17.33 UTC — freshclaim

### Status
Compact widening revision; shifts the archive from generic machine-readable vulnerability status toward the freshness and admissibility regime that decides how long a supplier's VEX claim can still count as trustworthy in downstream procurement and assurance workflows.

### Added
- New dossier: `02-dossiers/vex-expiry-governance-becomes-a-procurement-term.md`.
- New source entries: **[S901]–[S908]**.

### Changed
- Updated README to reflect the new VEX-expiry / procurement-term front and refreshed the next-queue summary.
- Extended the Speculation Cube with explicit attention to VEX timestamps, revision histories, supersession discoverability, stale-claim policy, archival retrievability, and feed-uptime reliability.
- Updated the constellation map so managed legibility now explicitly includes VEX freshness and admissibility windows as a recurring layer beneath applicability maintenance, backport proof, and scanner trust.
- Rebuilt the seed bank around applicability appeals, scanner-ingestion scoreboards, and security-feed uptime obligations after promoting the VEX-expiry thesis.
- Expanded the source register with CSAF/OpenVEX/CycloneDX material, Ubuntu and Red Hat publication practice, NIST procurement guidance, and NCSC update-hygiene guidance.

### Why it matters
A growing share of supplier security evidence is turning into a maintained status service rather than a one-time advisory artifact. Once buyers and tools depend on that service, freshness, supersession, and historical retrievability start behaving like contract and assurance terms.

## rev0099 — 2026.03.23.17.18 UTC — patchledger

### Status
Compact widening revision; shifts the archive from generic vulnerability-status maintenance toward the proof layer that lets downstream builds count as fixed even when their visible version surface still looks old to naive tooling.

### Added
- New dossier: `02-dossiers/backport-proof-registries-become-negotiated-trust-surfaces.md`.
- New source entries: **[S895]–[S900]**.

### Changed
- Updated README to reflect the new backport-proof / negotiated-trust front and refreshed the next-queue summary.
- Extended the Speculation Cube with explicit attention to vendor security-data feeds, downstream fix lineage, backport-proof quality, and scanner-ingestion coverage.
- Updated the constellation map so managed legibility now explicitly includes backport-proof publication as a recurring infrastructure layer beneath applicability maintenance, support windows, and scanner overrides.
- Rebuilt the seed bank around VEX-expiry terms, applicability appeals, and scanner-ingestion scoreboards after promoting the backport-proof thesis.
- Expanded the source register with Red Hat, Ubuntu, and SUSE material on backporting, machine-readable security data, and CSAF/VEX publication.

### Why it matters
A growing share of software-security governance now depends on whether institutions can prove that a stable downstream package lineage is fixed even when upstream version numbers suggest otherwise. Once that proof travels through feeds and registries that scanners and buyers actually trust, the proof layer itself becomes infrastructure.

## rev0098 — 2026.03.23.17.09 UTC — rangekeeper

### Status
Compact widening revision; shifts the archive from generic comparability brokerage toward the security-side layer that maintains product applicability, version-range scope, and reusable vulnerability status for large operational workflows.

### Added
- New dossier: `02-dossiers/applicability-range-maintenance-becomes-security-market-infrastructure.md`.
- New source entries: **[S891]–[S894]**.

### Changed
- Updated README to reflect the new applicability-range / security-market front and refreshed the next-queue summary.
- Extended the Speculation Cube with explicit attention to applicability-range maintenance, product-status assertion quality, and vulnerability-status freshness.
- Updated the constellation map so managed legibility now explicitly includes vulnerability applicability maintenance as a recurring layer beneath scope crosswalks, support windows, and public result surfaces.
- Rebuilt the seed bank around VEX expiry, backport-proof registries, and applicability appeals after promoting the applicability-range thesis.
- Expanded the source register with CSAF 2.1, NTIA’s SBOM/VEX framing, and 5G Challenge material showing SBOM/VEX artifacts entering scored infrastructure workflows.

## rev0097 — 2026.03.23.16.58 UTC — mapbroker

### Status
Compact widening revision; shifts the archive from scope assignment itself toward the broker layer that translates differently scoped status objects into the comparison surfaces procurement teams, dashboards, scanners, directories, and trust workflows actually use.

### Added
- New dossier: `02-dossiers/scope-crosswalk-services-become-quiet-comparability-brokers.md`.
- New source entries: **[S888]–[S890]**.

### Changed
- Updated README to reflect the new crosswalk-comparability front and removed a fragile explicit front count.
- Trimmed and extended the Speculation Cube with `scope crosswalk services` and `comparability-broker concentration`, while removing a duplicate bottleneck bullet.
- Updated the constellation map so managed legibility now explicitly includes scope-crosswalk services alongside listing-scope taxonomies, result registries, migration bridges, and other reusable comparison layers.
- Rebuilt the seed bank around override-audit trails, template-diff review, and applicability-range maintenance after promoting the scope-crosswalk thesis.
- Expanded the source register with current NVD material on match criteria, applicability statements, and the scaling behavior of the /cpematch/ layer.

### Design decisions
- Promoted `scope-crosswalk services become quiet comparability brokers` because the archive had already established that status scopes matter, but still lacked a direct dossier on the maintained mapping layer that lets differently scoped records be compared in practice.
- Treated the key bottleneck as **brokered comparability** — not merely whether a favorable status exists, but who maintains the roll-up, applicability, inheritance, or mapping logic that lets downstream actors treat differently scoped records as decision-ready.
- Avoided fragmenting the topic into separate notes on NVD match criteria, CHPL version roll-ups, OpenID profile bundles, OGC comparison filters, or HL7 version maps, and instead folded them into one broader dossier about scope-crosswalk services as quiet comparability brokers.

### Next likely moves
- Promote `applicability-range maintenance becomes security-market infrastructure`.
- Test whether `template-diff review becomes quasi-rulemaking` deserves a separate dossier or should remain nested under canonical style-pack governance.
- Watch whether procurement rules, vulnerability-management products, or trust frameworks begin requiring explicit disclosure of crosswalk provenance, roll-up rules, or mapping-update cadence.
- Keep pruning for overlap with listing-scope taxonomies, compatibility shims, registry completeness, and broader managed-legibility material.

## rev0096 — 2026.03.23.11.32 UTC — scopegate

### Status
Compact widening revision; shifts the archive from upstream template bundles toward the hidden market-boundary work done by status scope itself, where authoritative records decide whether qualification, certification, or comparability attaches to a provider, service, version, profile, or product family.

### Added
- New dossier: `02-dossiers/listing-scope-taxonomies-become-quiet-market-boundaries.md`.
- New source entries: **[S879]–[S887]**.

### Changed
- Updated README to reflect ninety-nine current speculative fronts.
- Extended the principles with listing-scope taxonomy, provider/service/product/profile/version scoping, scope-rollup rules, and scope-crosswalk quality as first-class variables around managed legibility and source-of-record design.
- Expanded the Speculation Cube to better model scope crosswalks, profile-boundary clarity, version-family attribution, and status inheritance across differently scoped records.
- Updated the constellation map so managed legibility now explicitly includes listing-scope taxonomies as a recurring layer beneath registry completeness, public conformance-result registries, portable verdicts, and support-window governance.
- Rebuilt the seed bank around scope-crosswalk services, override-audit trails, and template-diff review after promoting the listing-scope thesis.
- Expanded the source register with European Commission, ASTP/ONC, OpenID, and OGC material on provider/service scoping, product/version certification boundaries, profile-specific certification, and standard/provider/reference-implementation filters.

### Design decisions
- Promoted `listing-scope taxonomies become quiet market boundaries` because the archive had already established that registries, validators, portable reports, and support windows matter, but still lacked a direct dossier on the prior design choice that determines which exact object receives the status line in the first place.
- Treated the key bottleneck as **scope assignment** — not merely whether a favorable status exists, but whether it attaches to the provider, the service, the version, the profile, the product family, or another layer that downstream institutions actually use for comparison and admission.
- Avoided fragmenting the topic into separate notes on provider/service pairs under eIDAS, CHPL product-version boundaries, OpenID profile-specific certification, or OGC provider/standard/reference-implementation filters, and instead folded them into one broader dossier about listing-scope taxonomy as a quiet market boundary.

### Next likely moves
- Promote `scope-crosswalk services become quiet comparability brokers`.
- Test whether `template-diff review becomes quasi-rulemaking` deserves a separate dossier or should remain nested under canonical style-pack governance.
- Watch whether procurement rules, conformance registries, or trust frameworks begin requiring explicit disclosure of inheritance rules, scope roll-ups, or profile-to-product crosswalks.
- Keep pruning for overlap with registry completeness, public conformance-result registries, supported-version windows, and broader source-of-record / interoperability governance material.

## rev0095 — 2026.03.23.12.05 UTC — stylelock

### Status
Compact widening revision; shifts the archive from operator-side trust exceptions toward the upstream template bundles that many ecosystems quietly reuse to turn structured artifacts into the human-facing objects people actually read, compare, and sign off on.

### Added
- New dossier: `02-dossiers/canonical-style-packs-become-governance-dependencies.md`.
- New source entries: **[S871]–[S878]**.

### Changed
- Updated README to reflect ninety-eight current speculative fronts.
- Extended the principles with canonical style-pack maintenance, shared template-bundle governance, label-pack versioning, template-diff reviewability, and shared display logic as first-class variables around managed legibility.
- Expanded the Speculation Cube to better model shared template bundles, label packs, canonical style-pack maintenance, template-diff reviewability, and style-pack fork debt.
- Updated the constellation map so managed legibility now explicitly includes shared stylesheet and template packs as a recurring hidden layer beneath renderers, support windows, and migration bridges.
- Rebuilt the seed bank around listing-scope taxonomies, override-audit trails, and template-diff review after promoting the style-pack thesis.
- Expanded the source register with European Union, FDA / ICH, HL7, OpenPeppol, and GSA material on reusable notice-view templates, maintained stylesheet bundles, and canonical editor/view packages.

### Design decisions
- Promoted `canonical style packs become governance dependencies` because the archive had already established that viewers, renderers, dual-format artifacts, and support windows matter, but still lacked a direct dossier on the shared upstream template bundles that many local tools inherit before any particular service renders a view.
- Treated the key bottleneck as **template custody** — not merely whether a source artifact validates, but who controls the section order, labels, summaries, grouping logic, and release cadence of the canonical pack that makes the artifact legible across an ecosystem.
- Avoided fragmenting the topic into separate notes on eForms templates, eCTD stylesheets, CDA stylesheets, Peppol rendering downloads, or OpenACR editor packages, and instead folded them into one broader dossier about canonical style packs as governance dependency.

### Next likely moves
- Promote `listing-scope taxonomies become quiet market boundaries`.
- Test whether `template-diff review becomes quasi-rulemaking` deserves a separate dossier or should remain nested under canonical style-pack governance.
- Watch whether procurement rules, regulatory submissions, or conformance programs begin requiring explicit version disclosure for style packs, template bundles, or official editor/view packages.
- Keep pruning for overlap with authoritative rendering services, readable/structured divergence, support-window governance, and broader source-of-record / interoperability material.

## rev0094 — 2026.03.23.11.47 UTC — sidepass

### Status
Compact widening revision; shifts the archive from registry completeness and trust-chain maintenance toward the operator-side exception paths that appear when shared trust policy is too slow, too strict, too stale, or too global for the service that still needs to keep running.

### Added
- New dossier: `02-dossiers/local-trust-overrides-become-governance-escape-hatches.md`.
- New source entries: **[S863]–[S870]**.

### Changed
- Updated README to reflect ninety-seven current speculative fronts.
- Extended the principles with custom trust-anchor injection, enterprise-root import, managed distrust exceptions, override-auditability, custom-root custody, and local-policy divergence as first-class variables around managed legibility and trust portability.
- Expanded the Speculation Cube to better model enterprise roots, custom trust stores, per-app trust policies, local trust bundles, override-governance clarity, override-expiry discipline, and local-policy divergence.
- Updated the constellation map so managed legibility now explicitly includes operator-side local trust overrides and custom roots as a recurring hidden layer beneath trust-anchor sunsets, portable verdicts, and signed evidence transport.
- Rebuilt the seed bank around canonical style-pack dependencies, listing-scope taxonomies, and override-audit trails after promoting the local-override thesis.
- Expanded the source register with Mozilla, Android, Google, Apple, Microsoft, European Commission, and OpenID material on enterprise-root inheritance, app-specific custom trust anchors, managed private roots, manually enabled root trust, CTL redirection, validator-local trust anchors, and local-policy choice among valid trust chains.

### Design decisions
- Promoted `local trust overrides become governance escape hatches` because the archive had already established portable trust, trust-anchor sunset, support-window exclusion, and registry dependence, but still lacked a direct dossier on the operator-side exception powers that keep systems alive when the shared trust regime is not ready.
- Treated the key bottleneck as **override custody** — not merely whether trust exists in the abstract, but who can install, scope, expire, audit, and revoke local trust exceptions when continuity pressures conflict with common policy.
- Avoided fragmenting the topic into separate notes on enterprise root import, app-level custom trust anchors, MDM-installed roots, CTL redirection, validator-local trust sources, or federation-local policy, and instead folded them into one broader dossier about local trust override as governance escape hatch.

### Next likely moves
- Promote `canonical style packs become governance dependencies`.
- Test whether `listing-scope taxonomies become quiet market boundaries` deserves a separate dossier or should remain nested under registry completeness and authoritative record fights.
- Watch whether procurement rules, security audits, or regulatory submissions begin requiring disclosure of custom roots, enterprise-root inheritance, local trust bundles, or override-expiry controls.
- Keep pruning for overlap with trust-anchor sunset dates, report-signature trust chains, authoritative rendering services, and broader source-of-record / interoperability governance material.

## rev0093 — 2026.03.23.11.28 UTC — entryfight

### Status
Compact widening revision; shifts the archive from registry visibility and trust-liveness toward the contested completeness of the authoritative records that downstream institutions actually consult, where missing entries, stale statuses, hidden-by-default records, and scope disputes start behaving like governance fights rather than clerical cleanup.

### Added
- New dossier: `02-dossiers/registry-completeness-disputes-become-governance-fights.md`.
- New source entries: **[S854]–[S862]**.

### Changed
- Updated README to reflect ninety-six current speculative fronts.
- Extended the principles with constitutive listings, source-of-record completeness, default-hidden status filters, remediation labels, and registry-correction workflows as first-class variables around managed legibility and public admissibility.
- Expanded the Speculation Cube to better model listing-scope governance, registry-completeness assurance, status-filter defaults, naming-resolution accuracy, record-restoration paths, and source-of-record inventories.
- Updated the constellation map so managed legibility now explicitly includes authoritative registries and source-of-record inventories as a recurring governance layer beneath public ranking surfaces and signed evidence transport.
- Rebuilt the seed bank around canonical style packs, local trust overrides, and listing-scope taxonomies after promoting the completeness thesis.
- Expanded the source register with European Commission, ASTP/ONC, OpenID, OGC, and GSA material on constitutive trusted lists, CHPL status visibility, certification-result disclosure, certified-vs-self-reported implementation directories, and source-of-record procurement governance.

### Design decisions
- Promoted `registry-completeness disputes become governance fights` because the archive had already established that public result registries rank markets, but still lacked a direct dossier on what happens once missingness, hidden statuses, lagged correction, and scope boundaries in those registries start altering legal effect, shortlist formation, and procurement posture.
- Treated the key bottleneck as **authoritative record completeness** — not merely whether conformity evidence exists somewhere, but whether the record ordinary institutions consult is current, correctly scoped, visible by default, and repairable on a meaningful timeline.
- Avoided fragmenting the topic into separate notes on trusted-list constitutive effect, CHPL filter defaults, certified-vs-uncertified implementation pages, self-reported-vs-certified database boundaries, or source-of-record inventory fields, and instead folded them into one broader dossier about completeness disputes as governance fights.

### Next likely moves
- Promote `local trust overrides become governance escape hatches`.
- Test whether `canonical style packs become governance dependencies` deserves a separate dossier or should remain nested under evidence-view authority and rendering governance.
- Watch whether major registries begin publishing explicit service levels for freshness, completeness, correction turnaround, or restoration rights.
- Keep pruning for overlap with public conformance-result registries, authoritative rendering services, report-signature trust chains, and source-of-truth hierarchy material.

## rev0092 — 2026.03.23.11.14 UTC — anchorfade

### Status
Compact widening revision; shifts the archive from evidence-view authority toward the date-bound trust material beneath signed transport, browser trust, federation chains, and update verification, where services start failing because an anchor, key bundle, or rollover overlap quietly fell out of scope.

### Added
- New dossier: `02-dossiers/trust-anchor-sunset-dates-become-hidden-service-interruptions.md`.
- New source entries: **[S846]–[S853]**.

### Changed
- Updated README to reflect ninety-five current speculative fronts.
- Extended the principles with trust-anchor sunset schedules, rollover-overlap governance, trust-bundle refresh cadence, trust-anchor sunset debt, and local trust overrides as first-class variables around managed legibility and portable trust.
- Expanded the Speculation Cube to better model trust-anchor sunset scheduling, rollover overlap, stale trust bundles, and the operators who maintain root-program and trust-bundle continuity.
- Updated the constellation map so managed legibility now explicitly includes trust-anchor sunset and rollover timing as a recurring hidden reliability layer beneath portable verdicts and signed evidence transport.
- Rebuilt the seed bank around registry-completeness disputes, canonical style-pack dependencies, and local trust overrides after promoting the sunset thesis.
- Expanded the source register with European Commission, OpenID, Mozilla, and Google material on trusted-list revalidation cadence, sunset-aware signature-validation libraries, expiring trust chains, browser root-lifecycle policy, concrete distrust rollouts, and release-signing key rollover.

### Design decisions
- Promoted `trust-anchor sunset dates become hidden service interruptions` because the archive had already established portable verdicts, trust-chain dependence, version-window exclusion, and evidence-view authority, but still lacked a direct dossier on what happens when an unchanged artifact stops counting because the anchor that made it admissible crossed a date boundary.
- Treated the key bottleneck as **trust-liveness maintenance** — not merely whether trust was once established, but whether the relying environment still has the right anchors, overlap, refresh state, and bundle currency to keep that trust usable at decision time.
- Avoided fragmenting the topic into separate notes on trusted-list revalidation, browser-root distrust calendars, federation-key rollover, pinned CA-bundle staleness, or signing-key expiry, and instead folded them into one broader dossier about anchor sunset as hidden interruption governance.

### Next likely moves
- Promote `registry-completeness disputes become governance fights`.
- Test whether `canonical style packs become governance dependencies` deserves a separate dossier or should remain nested under evidence-view authority and rendering governance.
- Watch whether procurement rules, submission portals, or validators begin surfacing trust-store freshness, accepted trust anchors, last trust-list refresh, or future-distrust warnings explicitly.
- Keep pruning for overlap with report-signature trust chains, supported-version windows, authoritative rendering services, and broader provenance / trust infrastructure material.

## rev0091 — 2026.03.23.10.56 UTC — proofview

### Status
Compact widening revision; shifts the archive from divergence between paired readable/structured artifacts toward the next authority layer those artifacts create once institutions depend on them: the maintained renderer, stylesheet, view generator, or report-production service that turns a structured source into the human-facing object decision-makers actually inspect.

### Added
- New dossier: `02-dossiers/authoritative-rendering-services-become-evidentiary-choke-points.md`.
- New source entries: **[S841]–[S845]**.

### Changed
- Updated README to reflect ninety-four current speculative fronts.
- Extended the principles with authoritative rendering services, stylesheet custody, renderer-version governance, evidence-view parity, and reproducible renderings as first-class variables around managed legibility.
- Expanded the Speculation Cube to better model renderers, stylesheets, evidence viewers, and the bottlenecks created when human-facing interpretation depends on maintained view-generation layers.
- Updated the constellation map so managed legibility now explicitly includes renderers and evidence viewers as a recurring authority layer between structured originals and human decision.
- Rebuilt the seed bank around registry-completeness disputes, trust-anchor sunset failures, and canonical style-pack dependencies after promoting the rendering thesis.
- Expanded the source register with FDA, HL7, Interoperable Europe, and GSA material on review-tool display names, maintained eCTD stylesheets, clinically safe attested narrative, signed PDF report generation, and viewer-dependent OpenACR reports.

### Design decisions
- Promoted `authoritative rendering services become evidentiary choke points` because the archive had already established wrapper objects, divergence risk, validator dependence, portable verdicts, and support-window governance, but still lacked a direct dossier on the human-facing authority layer that emerges once structured sources are routinely interpreted through maintained viewers and generated reports.
- Treated the key bottleneck as **evidence-view authority** — not merely whether a source object validates or can be signed, but which maintained rendering path humans actually rely on when they review, compare, dispute, archive, or approve it.
- Avoided fragmenting the topic into separate notes on FDA review tools, SPL highlight rendering, signed PDF report generation, or YAML-to-HTML conformance viewers, and instead folded them into one broader dossier about renderers as quiet evidentiary authorities.

### Next likely moves
- Promote `trust-anchor sunset dates become hidden service interruptions`.
- Test whether `registry-completeness disputes become governance fights` deserves a separate dossier or should remain nested under public conformance surfaces and visible admissibility.
- Watch whether procurement rules, submission portals, or courts begin requiring specific viewer versions, reproducible rendering context, or official generated views in addition to signed source artifacts.
- Keep pruning for overlap with hybrid wrapper formats, readable/structured divergence, portable validation reports, and broader semantic-interoperability material.

## rev0090 — 2026.03.23.10.18 UTC — splitview

### Status
Compact widening revision; shifts the archive from durable compromise objects toward the failure mode those objects create once institutions depend on them: readable and structured layers drifting apart while payment, procurement, clinical review, or traceability still depends on both.

### Added
- New dossier: `02-dossiers/readable-structured-divergence-becomes-a-liability-surface.md`.
- New source entries: **[S833]–[S840]**.

### Changed
- Updated README to reflect ninety-three current speculative fronts.
- Extended the principles with authoritative-layer precedence, paired-artifact drift detection, extraction integrity, cross-layer congruence checking, and rendering-source fidelity as first-class variables around paired artifacts.
- Expanded the Speculation Cube to better model divergence risk inside dual-view packages, including precedence rules, congruence checks, extraction integrity, and drift detection.
- Updated the constellation map so managed legibility now explicitly includes cross-layer mismatch and authoritative-layer rules inside paired human-readable and machine-processable artifacts.
- Rebuilt the seed bank around registry-completeness disputes, trust-anchor sunset failures, and authoritative rendering chokepoints after promoting the divergence thesis.
- Expanded the source register with German federal, HL7, FDA, and GSA material on identical embedded invoice content, attested narrative blocks, structured product labeling, dual-form identifiers, and paired HTML/YAML procurement reports.

### Design decisions
- Promoted `readable/structured divergence becomes a liability surface` because the archive had already established hybrid wrappers, validator services, portable verdicts, version-policy exclusion, and compromise objects, but still lacked a direct dossier on what happens when those paired objects stop agreeing with themselves.
- Treated the key bottleneck as **cross-layer responsibility** — not merely whether a package is readable or machine-valid in isolation, but whether institutions can keep both layers aligned well enough to know what should govern a decision, dispute, or enforcement action.
- Avoided fragmenting the topic into separate notes on invoice drift, clinical narrative mismatch, product-identifier inconsistency, or ACR package staleness, and instead folded them into one broader dossier about divergence as a new liability surface.

### Next likely moves
- Promote `authoritative rendering services become evidentiary choke points`.
- Test whether `registry-completeness disputes become governance fights` deserves a separate dossier or should remain nested under public conformance surfaces and visible admissibility.
- Watch whether procurement rules, submission portals, or validator suites begin declaring explicit authoritative-layer precedence or start checking readable/structured congruence automatically.
- Keep pruning for overlap with hybrid wrapper formats, portable validation reports, trust-chain maintenance, and broader semantic-interoperability material.

## rev0089 — 2026.03.23.10.04 UTC — dualform

### Status
Compact widening revision; shifts the archive from migration intermediation toward the paired or containerized artifacts that persist because institutions still need both readable review surfaces and machine-actionable structure at once.

### Added
- New dossier: `02-dossiers/hybrid-wrapper-formats-become-durable-compromise-objects.md`.
- New source entries: **[S825]–[S832]**.

### Changed
- Updated README to reflect ninety-two current speculative fronts.
- Extended the principles with readable/structured coherence, dual-format synchronization, container-profile support, and compromise-object persistence as first-class variables around managed legibility.
- Expanded the Speculation Cube to better model hybrid wrapper formats, readable+structured bundles, evidence containers, and the bottlenecks created by keeping dual-view artifacts synchronized.
- Updated the constellation map so managed legibility now explicitly includes paired human-readable and machine-processable artifacts as a recurring layer between migration bridges and full native support.
- Rebuilt the seed bank around registry-completeness disputes, trust-anchor sunset failures, and readable/structured divergence risks after promoting the wrapper thesis.
- Expanded the source register with German federal, Franco-German, HL7, FDA, ETSI, European Commission, and GSA material on PDF+XML invoices, deterministic clinical documents, structured product labels, signature containers, and HTML/YAML accessibility-report packages.

### Design decisions
- Promoted `hybrid wrapper formats become durable compromise objects` because the archive had already established version-window exclusion, compatibility shims, portable verdicts, and trust maintenance, but still lacked a direct dossier on the paired artifact that often survives precisely because no single pure representation satisfies all institutional needs.
- Treated the key bottleneck as **dual-view admissibility** — not merely whether an object is machine-valid or human-readable in isolation, but whether one governed package can continue to satisfy review, dispute, audit, and automation simultaneously.
- Avoided fragmenting the topic into separate notes on PDF+XML invoices, clinical-document narratives, signed evidence containers, or HTML/YAML report packages, and instead folded them into one broader dossier about durable compromise objects.

### Next likely moves
- Promote `readable/structured divergence becomes a liability surface`.
- Test whether `registry-completeness disputes become governance fights` deserves a separate dossier or should remain nested under public conformance surfaces and visible admissibility.
- Watch whether procurement rules, validator suites, or submission portals begin naming authoritative-layer precedence explicitly when readable and structured layers disagree.
- Keep pruning for overlap with compatibility shims, portable validation reports, signed trust infrastructure, and broader semantic-interoperability material.

## rev0088 — 2026.03.23.09.51 UTC — bridgeware

### Status
Compact widening revision; shifts the archive from moving support windows toward the bridge, wrapper, and migration-intermediation layer that keeps lagging participants admissible while native transition remains incomplete.

### Added
- New dossier: `02-dossiers/compatibility-shims-become-strategic-intermediaries.md`.
- New source entries: **[S818]–[S824]**.

### Changed
- Updated README to reflect ninety-one current speculative fronts.
- Extended the principles with bridge-operator concentration, wrapper-format support, protocol-translation quality, migration-mailroom availability, and shim-mediated admissibility as first-class variables around maintained interoperability.
- Expanded the Speculation Cube to better model bridge operators, wrapper objects, translation-gateway dependence, and the service layer that turns migration into an ongoing intermediation market.
- Updated the constellation map so managed legibility now explicitly includes bridges, wrappers, and migration mailrooms as the connective tissue between live support windows and continued participation.
- Rebuilt the seed bank around registry-completeness disputes, trust-anchor sunset failures, and hybrid wrapper compromise objects after promoting the shim thesis.
- Expanded the source register with HL7, European Commission, and HaDEA material on C-CDA↔FHIR mappings, HL7 V2 and R4/R5 conversion logic, cross-system evidence bridges, public-sector mailrooms, hybrid PDF+XML invoices, and multilingual translation infrastructure.

### Design decisions
- Promoted `compatibility shims become strategic intermediaries` because the archive had already established version-window exclusion, validator dependency, portable verdicts, and trust maintenance, but still lacked a direct dossier on what keeps institutions in the game when they cannot migrate natively on schedule.
- Treated the key bottleneck as **bridge-layer leverage** — not merely whether two standards or versions coexist, but who controls the translators, wrappers, routing services, and managed mappings that allow old and new stacks to remain mutually admissible.
- Avoided fragmenting the topic into separate notes on format converters, protocol bridges, hybrid wrapper artifacts, translation gateways, or public mailrooms, and instead folded them into one broader dossier about shim infrastructure as strategic intermediation.

### Next likely moves
- Promote `hybrid wrapper formats become durable compromise objects`.
- Test whether `registry-completeness disputes become governance fights` deserves a separate dossier or should remain nested under public conformance surfaces and visible admissibility.
- Watch whether procurement templates, certification rules, or network-operator policies begin distinguishing explicitly between native support and bridge-mediated support.
- Keep pruning for overlap with semantic interoperability, reference implementations, validator services, public registry surfaces, and supported-version exclusion.

## rev0087 — 2026.03.23.09.41 UTC — versionwall

### Status
Compact widening revision; shifts the archive from portable trust maintenance toward the moving version floors, support tables, and deprecation calendars that can exclude participants even when their artifacts still exist and may still work.

### Added
- New dossier: `02-dossiers/supported-version-windows-become-quiet-exclusion-regimes.md`.
- New source entries: **[S811]–[S817]**.

### Changed
- Updated README to reflect ninety current speculative fronts.
- Extended the principles with criteria-version effective dates, deprecation calendars, dual-stack grace periods, compatibility-shim availability, and supported-platform policies as first-class variables around maintained admissibility.
- Expanded the Speculation Cube to better model effective-date cliffs, supported-platform floors, deprecation-calendar visibility, dual-stack grace periods, and compatibility-shim dependence.
- Updated the constellation map so live support windows now explicitly bridge portable verdicts, validation freshness, signed trust infrastructure, and quiet market exclusion.
- Rebuilt the seed bank around registry-completeness disputes, trust-anchor sunset failures, and compatibility-shim intermediation after promoting the version-window thesis.
- Expanded the source register with FDA, ASTP/ONC, European Commission, and OpenPeppol material on currently supported versions, requirement-begins dates, platform sunsets, rule-maintenance lag, and removed identifier states.

### Design decisions
- Promoted `supported-version windows become quiet exclusion regimes` because the archive had already established portable verdicts, freshness windows, public result registries, and trust-chain maintenance, but still lacked a direct dossier on what happens when admissibility shifts because the accepted version floor moves.
- Treated the key bottleneck as **live compatibility policy** — not merely whether an artifact once worked or once passed, but whether it still sits inside the version, platform, and ruleset window the receiving institution presently treats as current.
- Avoided fragmenting the topic into separate notes on effective-date rules, current-release tables, code-list removals, software-platform sunsets, or migration grace periods, and instead folded them into one broader dossier about version policy as quiet exclusion governance.

### Next likely moves
- Promote `compatibility shims become strategic intermediaries`.
- Test whether `trust-anchor sunset dates become hidden service interruptions` deserves a separate dossier or should remain nested under portable trust maintenance and version-window governance.
- Watch whether procurement templates, registry browsers, onboarding flows, or validator APIs begin surfacing minimum supported versions, required profile versions, supported platforms, or deprecated / removed status explicitly.
- Keep pruning for overlap with validation expiry, portable validation reports, registry surfaces, trust-chain maintenance, and broader semantic-interoperability material.

## rev0086 — 2026.03.23.09.32 UTC — trustmesh

### Status
Compact widening revision; shifts the archive from public listing status toward the hidden trust-chain layer where signed result objects only remain portable if anchors, revocation state, timestamp evidence, and validation stacks are actually usable at decision time.

### Added
- New dossier: `02-dossiers/report-signature-trust-chains-become-interoperability-bottlenecks.md`.
- New source entries: **[S804]–[S810]**.

### Changed
- Updated README to reflect eighty-nine current speculative fronts.
- Extended the principles with trust-chain portability, trust-anchor distribution, revocation-status reachability, timestamp-authority coverage, and validation-stack dependence as first-class variables around portable conformance evidence.
- Expanded the Speculation Cube to better model signature profiles, trust anchors, revocation responders, timestamp evidence, and trust-chain-aware portable result objects.
- Updated the constellation map so signed report transport now explicitly bridges portable verdict objects, public registries, federated trust, and quiet infrastructure dependence.
- Rebuilt the seed bank around supported-version exclusion windows, registry-completeness disputes, and trust-anchor sunset / rollover failures after promoting the trust-chain thesis.
- Expanded the source register with European Commission, OpenID, W3C, and Interoperable Europe material on trusted lists, signature-validation tooling, federation trust chains, verifiable credentials, and signed conformance reports.

### Design decisions
- Promoted `report-signature trust chains become interoperability bottlenecks` because the archive had already established portable verdicts, freshness windows, public result registries, and validator services, but still lacked a direct dossier on what happens when a portable report cannot actually travel unless the receiving side can validate the signature and trust path behind it.
- Treated the key bottleneck as **portable trust establishment** — not merely whether a signed artifact exists, but whether another institution can resolve, verify, refresh, and continue to rely on the chain that makes the artifact admissible.
- Avoided fragmenting the topic into separate notes on trusted lists, timestamp services, revocation responders, federation anchors, or signed test reports, and instead folded them into one broader dossier about trust-chain maintenance as hidden interoperability governance.

### Next likely moves
- Promote `supported-version windows become quiet exclusion regimes`.
- Test whether `trust-anchor sunset dates become hidden service interruptions` deserves a separate dossier or should remain nested under portable trust maintenance.
- Watch whether registries, wallets, onboarding forms, or procurement templates begin naming acceptable trust anchors, signature profiles, last-validation timestamps, or revocation-check requirements explicitly.
- Keep pruning for overlap with portable validation reports, validation expiry, public registry surfaces, reference implementations, and broader provenance / trust infrastructure material.

## rev0085 — 2026.03.23.09.19 UTC — shortlist

### Status
Compact widening revision; shifts the archive from freshness governance toward the public registry layer where conformance status, surveillance history, and searchable listings begin acting like default market-ordering surfaces.

### Added
- New dossier: `02-dossiers/public-conformance-result-registries-become-market-ranking-surfaces.md`.
- New source entries: **[S797]–[S803]**.

### Changed
- Updated README to reflect eighty-eight current speculative fronts.
- Extended the principles with registry-search usability, listing-status visibility, and corrective-action publicity as first-class variables around maintained conformance.
- Expanded the Speculation Cube to better model registry browsers, listing-status comparability, registry update latency, and the actors who maintain public conformance surfaces.
- Updated the constellation map so public conformance registries now explicitly bridge portable verdict objects, procurement screening, surveillance visibility, and quiet market ordering.
- Rebuilt the seed bank around report-signature trust chains, supported-version exclusion regimes, and registry-completeness disputes after promoting the registry-surface thesis.
- Expanded the source register with OpenID, ASTP, OGC, Section 508, and European Commission material on certified-implementation pages, authoritative product lists, searchable compliance databases, ACR repositories, and trusted-list browsers.

### Design decisions
- Promoted `public conformance-result registries become market-ranking surfaces` because the archive had already established validators, portable report objects, freshness windows, and certification directories, but still lacked a direct dossier on what happens when those public result surfaces become the first place buyers and integrators look.
- Treated the key bottleneck as **visible admissibility** — not merely whether proof exists, but whether it appears in the right searchable registry with the right status, dates, disclosures, and currentness to shape shortlisting before bespoke review begins.
- Avoided fragmenting the topic into separate notes on CHPL visibility, trusted-list browsers, ACR repositories, or compliant-product databases, and instead folded them into one broader dossier about registries as quiet ranking systems.

### Next likely moves
- Promote `report-signature trust chains become interoperability bottlenecks`.
- Test whether `supported-version windows become quiet exclusion regimes` deserves a separate dossier or should remain nested under freshness governance and registry surfaces.
- Watch whether procurement templates, partner-onboarding checklists, or ecosystem rules begin explicitly naming current public listing status, registry presence, or visible corrective-action closure as threshold conditions.
- Keep pruning for overlap with portable validation reports, validation expiry, conformity-assessment material, and broader market-legibility dossiers.

## rev0084 — 2026.03.23.09.05 UTC — bestbefore

### Status
Compact broadening revision; shifts the archive from verdict portability toward the shelf life of admissible proof and the way freshness windows begin entering procurement, onboarding, and certification-maintenance workflows.

### Added
- New dossier: `02-dossiers/validation-expiry-dates-become-procurement-terms.md`.
- New source entries: **[S790]–[S796]**.

### Changed
- Updated README to reflect eighty-seven current speculative fronts.
- Extended the principles with report-date governance, verdict-age ceilings, certificate-validity terms, rerun entitlements, and supported-version windows as first-class variables around maintained conformance.
- Expanded the Speculation Cube to better model report-age ceilings, supported-version windows, rerun entitlements, and the way renewal horizons start shaping admissibility.
- Updated the constellation map so validation freshness now explicitly bridges portable validation reports, validators, certification maintenance, and procurement screening.
- Rebuilt the seed bank around public conformance-result registries, report-signature trust chains, and supported-version exclusion regimes after promoting the freshness thesis.
- Expanded the source register with Section 508, ASTP, OGC, OpenID, and FDA material on updated conformance documentation, annual testing cycles, surveillance, certificate expiry, material-change refresh obligations, and currently supported standards versions.

### Design decisions
- Promoted `validation expiry dates become procurement terms` because the archive had already established validators, portable result objects, and recurring revalidation burdens, but still lacked a direct dossier on how freshness requirements become part of the commercial and institutional contract.
- Treated the key bottleneck as **evidence shelf life** — not merely whether proof exists, but whether it remains current enough to travel into award, renewal, onboarding, and continued use without triggering a rerun.
- Avoided fragmenting the topic into separate notes on annual health IT testing, accessibility report refresh, certificate-expiry calendars, supported-version notices, or change-triggered revocation, and instead folded them into one broader dossier about freshness as admissibility governance.

### Next likely moves
- Promote `public conformance-result registries become market-ranking surfaces`.
- Test whether `report-signature trust chains become interoperability bottlenecks` deserves a separate dossier or should remain nested under portable verdicts and freshness governance.
- Watch whether procurement templates, onboarding forms, or supervisory submissions start naming maximum report age, renewal windows, change-notification duties, or rerun rights explicitly.
- Keep pruning for overlap with validator services, portable validation reports, revalidation burdens, and conformity-assessment material.

## rev0083 — 2026.03.23.08.54 UTC — carryseal

### Status
Compact continuation revision; broadens the archive by promoting a verdict-portability thesis that bridges validator services, procurement evidence, certification disclosure, and regulatory intake acknowledgements.

### Added
- New dossier: `02-dossiers/portable-validation-reports-become-a-quiet-mutual-recognition-surface.md`.
- New source entries: **[S777]–[S789]**.

### Changed
- Updated README to reflect eighty-six current speculative fronts.
- Extended the principles with signed-report portability, validation-report portability, report-signature trust, result-registry coverage, and reusable conformance-record entries.
- Expanded the Speculation Cube to better represent report schemas, signed result packages, result registries, severity-vocabulary interoperability, and validation-freshness windows.
- Rebuilt the seed bank around validation expiry, public result registries, and report-signature trust chains after promoting the portable-report thesis.
- Expanded the constellation map so portable validation reports are treated as a bridge between validators, procurement screening, certification pathways, and quiet mutual recognition.
- Expanded the source register with W3C, Section508.gov, European Commission, OpenID, OGC, and FDA material on machine-readable reports, signed result packages, public conformance records, and traveling validation verdicts.

### Design decisions
- Promoted `portable validation reports become a quiet mutual-recognition surface` because the archive had already established validators, reference implementations, and certification pathways, but still lacked a direct dossier on the structured report objects that let verdicts travel across institutions.
- Treated the key bottleneck as **verdict reusability** — not only whether a test can be run, but whether its result can be verified, compared, published, ingested, and accepted elsewhere without a full rerun.
- Kept the revision small by making one real promotion and only the minimum surrounding framework edits needed to keep the archive coherent.

### Next likely moves
- Promote `validation expiry dates become procurement terms`.
- Revisit `public conformance-result registries become market-ranking surfaces`.
- Test whether `report-signature trust chains become interoperability bottlenecks` should remain nested inside standards governance or become a broader dossier.
- Continue deleting seeds that do not identify a reusable proof object, transport format, or enforceable bottleneck.

## rev0082 — 2026.03.23.08.52 UTC — gatecheck

### Status
Compact continuation revision; broadens the archive by promoting a hosted-validation thesis that bridges standards maintenance, conformance services, and practical certification pathways.

### Added
- New dossier: `02-dossiers/validator-services-become-outsourced-certifiers.md`.
- New source entries: **[S763]–[S776]**.

### Changed
- Updated README to reflect eighty-five current speculative fronts.
- Extended the principles with validator-service governance, machine-verdict portability, hosted-checker dependency, report-schema standardization, and appeal rights around automated conformance verdicts.
- Expanded the Speculation Cube to better represent hosted conformance portals, validation APIs, machine-readable verdict reports, and the actors who operate them.
- Rebuilt the seed bank around rerun/update rights, access-call governance, and portable validation reports after promoting the validator-service thesis.
- Expanded the constellation map so validator services are treated as a bridge between semantic interoperability, conformance testing, and certification pathways.
- Expanded the source register with European Commission, SEMIC, ASTP/ONC, CMS, OGC, OpenID, and W3C material on hosted validators, conformance portals, and machine-verdict pathways.

### Design decisions
- Promoted `validator services become outsourced certifiers` because the archive had already established standards, benchmarks, reference implementations, and formal conformity assessment, but still lacked a direct dossier on the shared checker services that increasingly decide who reaches formal review already looking admissible.
- Treated the key bottleneck as **machine-mediated admissibility** — not only whether a standard exists or a certifier is authorized, but which hosted validator, conformance portal, or public checker ecosystems begin trusting as the first practical verdict.
- Kept the revision small by making one real promotion and only the minimum surrounding framework edits needed to keep the archive coherent.

### Next likely moves
- Promote `portable validation reports become a quiet mutual-recognition surface`.
- Revisit `rerun rights and update rights become procurement terms`.
- Test whether `access-call governance becomes a quiet distributive surface` should remain nested inside shared utilities or become a broader distributive dossier.
- Continue deleting seeds that do not identify a reusable proof object, service gate, or enforceable bottleneck.

## rev0081 — 2026.03.23.08.43 UTC — knownstack

### Status
Compact continuation revision; broadens the archive by promoting a practical-interoperability thesis that bridges standards, conformance, and executable defaults.

### Added
- New dossier: `02-dossiers/reference-implementations-become-interoperability-governors.md`.
- New source entries: **[S754]–[S762]**.

### Changed
- Updated README to reflect eighty-four current speculative fronts.
- Extended the principles with official-SDK maintenance, sample-payload governance, validator coupling, and forkability of practical conformance artifacts.
- Expanded the Speculation Cube to better represent official SDKs, sample payloads, demo servers, validator packages, and the actors who maintain executable interoperability defaults.
- Rebuilt the seed bank around rerun/update rights, access-call governance, and validator services after promoting the reference-implementation thesis.
- Expanded the constellation map so maintained reference stacks are treated as a bridge between semantic interoperability, conformance testing, and benchmark governance.
- Expanded the source register with W3C, HL7, OpenID, OGC, and European Commission material on reference implementations, official SDKs, conformance testbeds, and prototype wallets.

### Design decisions
- Promoted `reference implementations become interoperability governors` rather than another narrow counterfactual-governance variant because it opens a wider standards-and-practice frontier that reaches web standards, health data, digital identity, procurement, signatures, and public-sector interoperability tooling.
- Treated the key bottleneck as **practical conformance** — not only what a specification permits in theory, but which maintained software artifact other institutions start treating as the easiest proof of what the specification means.
- Kept the revision small by making one real promotion and only the minimum surrounding framework edits needed to keep the archive coherent.

### Next likely moves
- Promote `validator services become outsourced certifiers`.
- Revisit `rerun rights and update rights become procurement terms`.
- Test whether `access-call governance becomes a quiet distributive surface` should stay nested inside shared counterfactual utilities or become a broader distributive dossier.
- Continue deleting seeds that do not identify a maintained executable surface or an enforceable bottleneck.


## rev0184 — freshnessrefactor — 2026.05.25

- Performed a focused audit/refactor of the evidence-freshness cluster.
- Added `19-evidence-freshness-model.md`, `20-freshness-refactor-report.md`, and `21-state-vocabulary-refactor.md`.
- Added four dossiers:
  - `cache-age-disclosures-become-reliance-boilerplate.md`
  - `grace-period-registries-become-critical-fallback-infrastructure.md`
  - `certificate-renewal-automation-becomes-operational-resilience-infrastructure.md`
  - `staleness-arbitrage-becomes-a-compliance-fraud-pattern.md`
- Tagged 18 existing dossiers with `refactor_cluster: evidence-freshness`, `freshness_role`, and `consolidation_status`.
- Added freshness-specific index artifacts and rebuilt the operational index.
- Appended rev0184 source register entries S1532–S1540.

## rev0185 — remedylifecycle — 2026.05.25

- Performed a focused audit/refactor of the appeal, complaint, dispute, stay, correction, grievance, and administrative-repair cluster.
- Added `22-dispute-and-remedy-lifecycle.md`, `23-remedy-refactor-report.md`, and `24-remedy-state-vocabulary.md`.
- Added five dossiers:
  - `remedy-clock-orchestration-becomes-administrative-infrastructure.md`
  - `adverse-action-explanation-packets-become-remedy-prerequisites.md`
  - `standing-and-representation-proofs-become-remedy-access-controls.md`
  - `remedy-abuse-rate-limits-become-due-process-design-problems.md`
  - `human-review-capacity-becomes-a-critical-compliance-bottleneck.md`
- Tagged 26 existing dossiers with remedy-lifecycle metadata.
- Added remedy-specific index artifacts and rebuilt the operational index.
- Appended rev0185 source register entries S1541–S1552.


## rev0186 — authoritylifecycle — 2026.05.25

- Performed a focused audit/refactor of the delegated-authority, representation, proxy, standing, scope, and agent-action cluster.
- Added `25-authority-and-delegation-lifecycle.md`, `26-authority-refactor-report.md`, and `27-authority-state-vocabulary.md`.
- Added five dossiers:
  - `authority-scope-crosswalks-become-interoperability-infrastructure.md`
  - `representative-of-record-ledgers-become-service-access-infrastructure.md`
  - `legal-person-wallets-turn-organizational-authority-into-transaction-evidence.md`
  - `capability-token-provenance-becomes-agentic-ai-audit-infrastructure.md`
  - `proxy-abuse-telemetry-becomes-adult-safeguarding-infrastructure.md`
- Tagged 24 existing dossiers with authority-lifecycle metadata.
- Added authority-specific index artifacts and rebuilt the operational index.
- Appended rev0186 source register entries S1553–S1564.
