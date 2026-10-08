# 927 — Cloudtainer deep-read audit: schema drift, source-health coverage, generated-surface budgets, housing gap, and no maintenance by green lint

## One-line thesis

Rev0745 is substantively coherent, but a green lint result still hid schema identity drift, status-vocabulary drift, weak generated-surface budgets, uneven source-currentness coverage, and an under-sourced housing gap; the repair rule is **no maintenance by green lint**.

## Why this matters

The utility / medical-baseline repair is the right live pattern: it joins account state, arrears, climate hazard, medical device dependence, energy assistance, outage continuity, notices, backup power, reconnection, and aftercare instead of pretending that one account code or medical certificate creates safety. The dangerous part is not the new case packet. The dangerous part is that the package could pass offline shape lint while still carrying small governance errors that compound over time.

This audit therefore treats the cloudtainer as a live maintenance surface. The goal is not another broad topical expansion. The goal is to correct the places where the archive can become wasteful or falsely reassuring: schemas that name the wrong artifact, statuses outside their declared vocabulary, source-health coverage that looks systematic but is still sparse, generated files that are too large for ordinary reading but not flagged, and a next-candidate gap whose source anchors were still empty.

The speculative read is that the archive is now large enough for bulk itself to become authority theater. If the generated layer is allowed to grow without sharper budgets, a reader may confuse route mass with evidence quality. If source-health rows remain sparse, a reader may confuse source-key presence with currentness. If gap rows lack source anchors, the backlog can become aspirational rather than executable.

## Pattern pack

### 1. Green lint is a shape proof, not a truth proof

Offline lint should remain deterministic, but it should not be treated as a warrant that sources are current, statuses are meaningful, schemas identify the right artifact, or generated surfaces are proportionate. The repair is to make shape lint stricter where it can be strict: declared status vocabularies, required generated files, package detritus, source-key references, and current-note exposure.

### 2. Schema identity matters even when validation passes

The climate / utility test schema carried the right title and data schema but the wrong `$id` lineage. That kind of error is easy to miss because local validation can still pass. It becomes expensive later when a schema registry, manifest comparison, or human reader assumes that an artifact name and schema identity point to the same doctrine.

### 3. Status labels must be executable

A metadata file that declares status labels but permits undeclared statuses has two vocabularies: the one a reader sees and the one the tool silently accepts. Notes 870 and 871 still used `current` even though the declared labels had moved to `active`, `active_first_citation`, `active_via_dispatcher`, and `active_lineage`. The repair is to normalize those notes and make lint reject future unknown statuses.

### 4. Generated-surface budgets should warn before they become absurd

The generated audit reported no warnings because its thresholds were so high that 650k-950k generated files were treated as normal. That is not a broken build, but it is a waste signal. Generated files are route surfaces; they should become visibly expensive before they turn into a second archive.

### 5. Source-health coverage is useful precisely because it is incomplete

A source-health ledger with partial manual coverage is valuable if it admits that most keys are not yet manually checked. It becomes harmful if readers interpret source-key registration as live source verification. The right next step is not to make ordinary lint browse the web. It is to keep the offline build deterministic while adding explicit review dates, volatility, fallback keys, and unchecked-source prioritization.

### 6. The next substantive gap should be seeded before prose is written

The housing / eviction / rental-assistance / tenant-screening gap is the right next candidate because it links payment, possession, court, record, shelter, appeal, and screening consequences. But it should not enter as another prose layer until the source anchors are live. The anti-theater rule for that future lane is likely **no housing stability by portal status**.

## Failure modes

- **Schema-name drift**: a schema title, file name, `$id`, and generated surface point in different directions.
- **Status-vocabulary drift**: metadata declares a limited vocabulary while old rows silently keep obsolete labels.
- **Source-currentness theater**: a note has source keys, but no one can tell which were checked this revision and which are merely registered.
- **Generated-route obesity**: generated indexes become too large for first-read navigation and still show no warning.
- **Gap-ledger aspiration**: the backlog names a missing domain but lacks enough current source anchors to write the next packet responsibly.
- **Maintenance avoidance**: the archive adds another topical note because that feels productive, while small defects keep accumulating in the tools and metadata.
- **False emergency specificity**: utility medical protection, PSPS notices, LIHEAP assistance, and outage maps are mistaken for joined household continuity.
- **Housing continuity flattening**: rental assistance, court status, possession, tenant-screening records, shelter referral, and legal representation are collapsed into one portal or docket status.

## Repair sequence

1. Fix the climate / utility schema `$id` so the schema identity matches the artifact.
2. Normalize undeclared note statuses and make lint fail on future status labels outside `metadata/note_metadata.json`.
3. Lower generated-surface warning thresholds and add package-level generated-file and total-byte warnings.
4. Seed `GAP-010` with current housing, eviction, rental-assistance, right-to-counsel, and tenant-screening source keys.
5. Add source-health rows for the new gap anchors and refresh the source-health posture of the climate / utility anchors opened during this audit.
6. Keep the next substantive write as a housing continuity packet only after the source anchors are visible.
7. Continue reducing old one-off generated builders only when touching their topic; do not spend the session refactoring stable machinery merely for elegance.

## What should change over time

The archive should keep the common test-matrix registry as the path for new topical matrices, but it does not need an immediate full rewrite of older builders. The better low-waste strategy is opportunistic consolidation: whenever an old test matrix is substantively touched, move it onto the common renderer and delete its one-off builder then.

The generated layer should also grow a compact-reader rule. A large JSON file may be fine for machine routing, but the markdown front door should stay navigable. When a generated route file crosses the warning budget, the repair should be either compaction, a compact companion, or a clearer statement that the file is a machine/debug surface, not the first human reading path.

The source-health ledger should make absence visible. A source key without a manual health row should be treated as an unchecked dependency, not as a failed source and not as a verified source. That distinction keeps the archive honest without making ordinary lint network-dependent.

## Source posture

This audit used current official and research anchors for two reasons. First, the utility / medical-baseline packet remains well-grounded: EIA disconnection data, HHS emPOWER electricity-dependent equipment maps, Connecticut winter / life-threatening medical protections, California PSPS governance, outage-health research, consumer extreme-heat analysis, and New York extreme-heat shutoff protections all support the thesis that account, health, assistance, hazard, and continuity states must be joined. Second, the next housing gap is live enough to seed now: eviction filing patterns, the lack of national eviction data infrastructure, tenant-background-check errors, the end of Treasury ERA2 performance, rental-assistance dashboards, local right-to-counsel representation data, and court-based rental-assistance programs all point to a future packet that must join payment, court, possession, record, and service-continuity states.

Source keys for this note are registered in `sources/source_keys.json`, attached in `sources/source_catalog.json`, and given source-health rows where this audit made a currentness claim.
