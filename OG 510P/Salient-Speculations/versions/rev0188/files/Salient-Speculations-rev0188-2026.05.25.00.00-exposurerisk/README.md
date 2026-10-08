# Salient Speculations — rev0188 `exposurerisk`

rev0188 performs a focused audit/refactor of the cube's exposure, liability, insurance, indemnity, reserve, warranty, and risk-transfer layer.

## What this revision does

- Adds `31-exposure-liability-lifecycle.md`, a canonical state machine for exposure and financial responsibility.
- Adds `32-exposure-refactor-report.md`, documenting the audit, tagged dossiers, consolidation choices, and promoted gaps.
- Adds `33-exposure-state-vocabulary.md`, normalizing states such as `coverage-position-reserved`, `defense-under-reservation`, `exclusion-flagged`, `sir-open`, `reserve-release-pending`, `indemnity-chain-mapped`, and `subrogation-preserved`.
- Tags 32 existing dossiers with `refactor_cluster: exposure-liability`, `exposure_role`, `exposure_stage`, and `state_family: exposure`.
- Adds five dossiers exposed by the audit: coverage-position state labels, indemnity pass-through maps, subrogation evidence packets, reserve-release evidence, and self-insured retention thresholds.
- Rebuilds the operational index with exposure-family audit files and graph edges.

> Note: older revision metadata is retained below for continuity; the current package is rev0188.

# Salient Speculations — rev0187 `lineagecustody`

rev0187 performs a focused audit/refactor of the cube's provenance, custody, transformation, resolver, traceability, and lineage layer.

## What this revision does

- Adds `28-provenance-and-lineage-lifecycle.md`, a canonical state machine for evidence lineage.
- Adds `29-lineage-refactor-report.md`, documenting the audit, consolidation choices, and promoted gaps.
- Adds `30-lineage-state-vocabulary.md`, normalizing lineage states such as `source-bound`, `snapshot-captured`, `transform-replayable`, `normalization-loss-disclosed`, `wrapper-divergence`, `resolver-successor-declared`, `redaction-boundary-declared`, `derived-use-limited`, `lineage-gap`, and `replay-sufficient`.
- Tags existing dossiers with `refactor_cluster: provenance-lineage`, `lineage_role`, `lineage_stage`, and `state_family: provenance`.
- Adds five dossiers exposed by the audit: resolver-successor maps, transformation-replay bundles, derived-data use rights, provenance-diff services, and custody-break certificates.
- Rebuilds the operational index with lineage-family audit files and graph edges.

> Note: older revision metadata is retained below for continuity; the current package is rev0187.

# Salient Speculations — rev0186 `authoritylifecycle`

rev0186 performs a focused audit/refactor of the cube's delegated-authority, representation, proxy, standing, scope, and agent-action layer.

## What this revision does

- Adds `25-authority-and-delegation-lifecycle.md`, a canonical state machine for delegated authority.
- Adds `26-authority-refactor-report.md`, documenting the audit, consolidation choices, and promoted gaps.
- Adds `27-authority-state-vocabulary.md`, normalizing authority states such as `scope-limited`, `joint-approval-required`, `step-up-required`, `revocation-pending`, `offline-verifiable`, `fallback-accepted`, `nondelegable-action`, and `abuse-watch`.
- Tags 24 existing dossiers with `refactor_cluster: authority-lifecycle`, `authority_role`, `authority_stage`, and `state_family: authority`.
- Adds five dossiers exposed by the audit: authority-scope crosswalks, representative-of-record ledgers, legal-person wallets, capability-token provenance, and proxy-abuse telemetry.
- Rebuilds the operational index with authority-family audit files and graph edges.

> Note: older revision metadata is retained below for continuity; the current package is rev0186.

# Salient Speculations — rev0185 `remedylifecycle`

rev0185 performs a focused audit/refactor of the cube's appeal, complaint, dispute, stay, correction, grievance, and administrative-repair family.

## What this revision does

- Adds `22-dispute-and-remedy-lifecycle.md`, a canonical state machine for remedies.
- Adds `23-remedy-refactor-report.md`, documenting the audit and consolidation choices.
- Adds `24-remedy-state-vocabulary.md`, normalizing remedy states such as `standing-pending`, `manual-review-only`, `source-witness-nonresponse`, `corrected-material`, and `restricted-stay-effect`.
- Tags 26 existing dossiers with `refactor_cluster: remedy-lifecycle`, `remedy_role`, `remedy_stage`, and `state_family: remedy`.
- Adds five dossiers exposed by the audit: remedy-clock orchestration, adverse-action explanation packets, standing/representation proofs, remedy-abuse rate limits, and human-review capacity.
- Rebuilds the operational index with remedy-family audit files and graph edges.

> Note: older revision metadata is retained below for continuity; the current package is rev0185.

# Salient Speculations

Revision: `rev0184`
Timestamp: `2026.05.25.00.00 UTC`
Codename: `freshnessrefactor`

## What this revision does

- Executes the first focused audit/refactor of the cube: the overloaded **evidence-freshness** cluster is now a reusable model rather than an uncontrolled dossier generator.
- Adds `19-evidence-freshness-model.md`, `20-freshness-refactor-report.md`, and `21-state-vocabulary-refactor.md`.
- Tags 18 existing dossiers with `refactor_cluster: evidence-freshness`, `freshness_role`, and `consolidation_status`.
- Adds four dossiers exposed by the audit: cache-age disclosures, grace-period registries, certificate-renewal automation, and staleness arbitrage.
- Rebuilds the operational index with freshness-family audit files and refactor-action logs.

> Note: older revision metadata is retained below for continuity; the current package is rev0184.


This archive is for **surprising, salient, broad speculation** that is still disciplined enough to be worth revisiting.

## What this revision does

- Converts the rev0182 recommendation into action: `15-evidence-confidence-audit.md` audits 24 high-impact dossiers by evidence grade, overconfidence risk, and next verification move.
- Adds `16-decision-grade-rubric.md`, separating decision-grade dossiers from interesting but under-institutionalized trend labels.
- Adds `17-transfer-atlas.md`, mapping which mechanisms can be tested across domains without promoting every metaphor into a dossier.
- Adds `18-consolidation-and-overfit-map.md`, identifying which managed-legibility dossiers should eventually become lifecycle states rather than standalone files.
- Adds five new dossiers only where the audit exposed missing institutional surfaces: crypto-agility registries, notified-body queue position, delegated AI-agent authority logs, data-space access rules, and provenance-nonparticipation labels.
- Backfills minimal YAML front matter for all remaining older dossiers, with `migration_status: inferred-rev0183-minimal` where appropriate.
- Rebuilds the operational index: 203 dossiers, 203 with YAML front matter, expanded graph edges, and new decision-grade score files.

## Archive map

- `00-principles.md` — admission criteria for new speculative material.
- `01-speculation-cube.md` — a compact framework for generating and testing broad hypotheses.
- `02-dossiers/` — higher-confidence speculative dossiers.
- `03-seed-bank.md` — terse, broad, candidate speculations for later promotion or deletion.
- `04-constellations.md` — compact clustering of the archive into recurring bottleneck families.
- `05-cube-schema.md` — controlled schema, maturity scale, and dossier front-matter template.
- `06-reliance-object-lifecycle.md` — canonical lifecycle model for packet/reliance-object governance.
- `07-graph-backbone.md` — typed graph relationships among managed-legibility dossiers.
- `08-operational-index.md` — explanation of the machine-readable index and migration approach.
- `09-research-signal-ledger.md` — current research signal map and speculative implications.
- `10-migration-workbench.md` — practical front-matter, graphfill, and consolidation backlog.
- `11-adversary-falsifier-matrix.md` — adversarial vocabulary and falsifier matrix for proof objects.
- `12-frontmatter-graphfill-report.md` — metadata migration and graphfill coverage report.
- `13-product-biography-lifecycle.md` — product biography state machine parallel to reliance-object lifecycle.
- `14-anti-legibility-model.md` — privacy, fallback, and informal-refuge model for proof-heavy systems.
- `15-evidence-confidence-audit.md` — evidence grades, overconfidence risks, and verification priorities.
- `16-decision-grade-rubric.md` — scoring system for decision-grade versus merely interesting dossiers.
- `17-transfer-atlas.md` — cross-domain transfer map for recurring institutional mechanisms.
- `18-consolidation-and-overfit-map.md` — pruning and consolidation guidance for future revisions.
- `19-evidence-freshness-model.md` — reusable model for cache age, expiry, grace, revocation, and stale-use governance.
- `20-freshness-refactor-report.md` — audit record for the rev0184 evidence-freshness refactor.
- `21-state-vocabulary-refactor.md` — normalized state vocabulary for validity, freshness, dispute, version, and observability states.
- `22-dispute-and-remedy-lifecycle.md` — canonical lifecycle model for appeals, complaints, disputes, corrections, and remedies.
- `23-remedy-refactor-report.md` — audit record for the rev0185 remedy-lifecycle refactor.
- `24-remedy-state-vocabulary.md` — normalized state vocabulary for standing, interim-state, review, outcome, abuse, and closure.
- `25-authority-and-delegation-lifecycle.md` — canonical lifecycle model for delegated authority, proxy representation, and agent action.
- `26-authority-refactor-report.md` — audit record for the rev0186 authority-lifecycle refactor.
- `27-authority-state-vocabulary.md` — normalized state vocabulary for scope, step-up, revocation, fallback, nondelegable actions, and abuse-watch states.
- `INDEX/` — CSV/JSON/TSV operational index files for machine-assisted navigation.
- `SOURCES.md` — short annotated source register.
- `CHANGELOG.md` — revision history.

## rev0183 additions to the center of gravity

This revision adds five missing surfaces:

- **cryptographic-agility registries** — cryptographic transition state becomes procurement, audit, and resilience evidence;
- **notified-body queue position** — conformity-assessment capacity becomes a market-access and industrial-policy bottleneck;
- **delegated AI-agent authority logs** — agent actions require scoped, replayable authority evidence and dispute paths;
- **data-space access rules** — participation profiles, connectors, intermediaries, and policy translation become industrial borders;
- **provenance-nonparticipation labels** — the absence of a content credential becomes a typed trust state, not a generic suspicion flag.

## Editorial stance

This is **not** a warehouse for clever guesses. A speculation belongs here only if it:

1. reframes a major domain rather than merely extending a trend;
2. identifies a real bottleneck, not just a fast-moving technology;
3. has institutional, civilizational, or coordination consequences;
4. can be sharpened with near-term signals and falsifiers;
5. is compressible into a small number of durable claims; and
6. is decision-grade enough to change a design, contract, diligence process, watchlist, or research agenda.

## Current center of gravity

The archive still treats the most important speculative question as:

> **Where are the bottlenecks moving, and which proof/state objects make those bottlenecks operational?**

rev0183 added a second question:

> **Which of these speculations are decision-grade, and which are only interesting?**

rev0184 acts on that warning by consolidating the evidence-freshness family into a shared model. The next useful revision should continue pruning, especially where a dossier merely renames a state already captured by `19-evidence-freshness-model.md`.
