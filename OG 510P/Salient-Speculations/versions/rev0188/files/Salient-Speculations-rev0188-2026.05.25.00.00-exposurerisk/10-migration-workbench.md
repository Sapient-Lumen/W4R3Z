# Migration Workbench

This is the practical workbench for turning the archive into a real datacube.

## Revision strategy

rev0180 created the schema. rev0181 adds an operational index and backfills only high-leverage front matter. The next several revisions should alternate between:

1. **schema work** — metadata, graph edges, source maps, review queues;
2. **frontier work** — new dossiers only when they open a missing lifecycle stage or major new domain;
3. **consolidation work** — merging near-duplicate packet-governance statuses into lifecycle models;
4. **audit work** — abuse, burden, near miss, falsifier, and source coverage.

## High-priority migration targets

### Tier 1 — recent reliance-object lifecycle

These are easiest to annotate because the artifact family is already coherent:

- source-object identity warranties
- transformation-code escrow
- split/merge correction notices
- amendment-recipient registries
- identity-match appeals
- appeal-stay labels
- correction-materiality thresholds
- source-witness nonresponse defaults
- recipient-graph privacy proofs
- non-reliance packet states
- compliance-object forgery
- data-minimization proofs

Target: full YAML, graph edges, lifecycle stage, abuse/burden check.

### Tier 2 — adjacent proof-object domains

These extend the lifecycle model beyond diligence packets:

- digital product passports / product identity
- EUDR due-diligence statements and place-proof
- repair-right evidence
- AI model-documentation packets
- incident-report routing
- portable validation reports
- VEX expiry governance
- NVD enrichment/status afterlife

Target: connect each to artifact types and external enforcement surfaces.

### Tier 3 — non-legibility counterweights

These keep the archive politically realistic:

- data minimization
- recipient-graph privacy
- local trust overrides
- human fallback
- small-supplier evidence brokers
- anti-forgery / anti-laundering
- informal markets and low-capacity environments

Target: add `weakens`, `privacy_layer_for`, `small_actor_layer_for`, and `anti_abuse_layer_for` graph edges.

### Tier 4 — older civilizational fronts

These need lighter metadata and stronger falsifiers:

- ageing and care
- family policy
- coolth
- water allocation
- indoor air
- social connection
- education bifurcation
- second-tier cities
- biological observability

Target: do not force them into packet language. Add domain, bottleneck, enforcement surface, maturity, and falsifier clarity.

## Metadata backfill rule

Do not add a field unless the value is useful.

Bad migration:

```yaml
artifact_type: [infrastructure]
```

Better migration:

```yaml
artifact_type:
  - registry entry
  - notice
  - appeal record
  - state label
```

If a dossier is too broad for precise artifact metadata, classify it at the constellation level and leave detailed fields blank until a sharper child dossier exists.

## Review checklist for every promoted dossier

A promoted dossier should eventually answer:

1. What state changes?
2. Who is allowed to rely on the state?
3. What makes the state enforceable?
4. What artifact carries the state?
5. What happens when the state is wrong, stale, disputed, forged, or nonresponsive?
6. Who pays, who saves, who captures?
7. Who is excluded or burdened?
8. How is the artifact abused?
9. What is a near miss?
10. What would falsify the thesis?

## Consolidation warnings

The archive should slow down promotion when a candidate dossier is merely:

- another status label for the same packet lifecycle;
- another notice type without new recipient-scope logic;
- another appeal type without a new burden or stay consequence;
- another scorecard without a new enforcement surface;
- another registry without a conflict-resolution rule;
- another proof object without a forgery, privacy, or correction story.

## Recommended next revision types

### rev0182 option A — graphfill

Add reviewed graph edges for the top 60 managed-legibility dossiers. Produce a graph visualization and identify isolated clusters.

### rev0182 option B — frontmatter30

Backfill YAML for the 30 most recent/high-leverage dossiers and add a linter report showing coverage gaps.

### rev0182 option C — product-biography consolidation

Build a product-biography lifecycle model parallel to reliance-object lifecycle: product identity → passport → repair event → resale → incident/recall → refurbishment → destruction/recycling → non-reliance.

### rev0182 option D — anti-legibility release

Promote informal-market refuge, graph poisoning, local trust override, and public proof-profile registry dossiers to prevent the archive from over-celebrating legibility.

## Best next move

The strongest next move is **frontmatter30 + graphfill**, not another burst of new dossiers. rev0181 already adds several adjacent frontiers. The archive now needs metadata density.


## rev0182 status

rev0182 chose a hybrid of frontmatter, graphfill, and anti-legibility release.

Completed in this revision:

- expanded YAML front matter to 85 dossiers;
- expanded the graph to 106 edges with no unresolved file-node references;
- added an adversary matrix and graph audit;
- added a product-biography state map;
- promoted six stress-test dossiers rather than another narrow packet-governance run.

Best next move for rev0183: **evidence audit**. Select 20 high-impact dossiers, verify their source claims, and add source-confidence / staleness fields. Do not add another large dossier batch unless the audit reveals a missing state transition.


## rev0183 migration workbench

Completed in rev0183:

- Backfilled minimal YAML front matter for 113 older dossiers.
- Added decision-grade and evidence-grade scoring files.
- Added transfer and consolidation frameworks to prevent uncontrolled dossier proliferation.

Next cleanup targets:

1. Replace inferred minimal metadata on the 30 highest-read older dossiers with reviewed metadata.
2. Consolidate freshness, revalidation, expiry, and history-retention dossiers into an evidence-freshness model.
3. Add lifecycle-role tags to reliance-object dossiers.
4. Downgrade or merge DG-C and DG-D items after manual review.
5. Refresh sources for dossiers with E1/E2 evidence grades but high decision impact.
## rev0184 migration note

The next metadata migration should not simply add more fields everywhere. Use refactor-cluster fields only where a family has become overloaded enough to deserve shared state vocabulary. The successful pattern in rev0184 was:

1. identify a proliferating cluster;
2. extract the shared model;
3. tag affected dossiers;
4. mark some as `model-substate` rather than creating new standalone claims;
5. add only the missing dossiers exposed by the model.


## rev0186 migration backlog: authority-lifecycle

High-priority next cleanup tasks:

1. Review all dossiers with `bottleneck_type: delegated authority` and ensure each has `authority_stage`.
2. Split generic “agent” references into legal agent, software agent, AI agent, broker, representative, guardian, service account, or organizational role.
3. Add `nondelegable-action` and `step-up-required` states where a dossier involves high-risk transactions.
4. Audit whether `scope-crosswalk-services-become-quiet-comparability-brokers.md` should become a parent family for both semantic interoperability and authority-scope crosswalks.
5. Add authority-stage edges to the graph whenever a dossier is a lifecycle prerequisite of another.

## rev0188 migration workbench: exposure

Backlog after the exposure refactor:

1. Audit all dossiers with `domain: insurance / risk transfer / underwriting` for actual exposure-stage fit.
2. Split generic `underwritability` into underwriting inputs, coverage triggers, exclusion states, reserve effects, and renewal consequences.
3. Add reinsurance / aggregate accumulation as a future refactor candidate if enough dossiers emerge.
4. Check whether every dossier using `liability` specifies who pays, who defends, who reserves, and who can recover.
