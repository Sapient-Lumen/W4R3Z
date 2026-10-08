# 960 — Cloudtainer release-lineage, schema-gap, generated-surface, and maintenance-revision audit: no maintenance by green lint

## One-line thesis

Rev0762 is substantively useful, but the cloudtainer had three false-green maintenance risks: `rev0761` existed in archive metadata while disappearing from the release index, `metadata/gap_ledger.json` violated its own schema for one repaired gap while lint passed, and maintenance-only revisions were again pressured toward fake operational matrix coverage; the repair rule is **no maintenance by green lint**.

## Why this matters

The consumer-finance packet correctly refuses to treat account rows, complaint IDs, credit-report rows, debt notices, and EFT logs as proof that people have usable financial access. The same rule has to apply to the archive itself. A release row is not lineage unless every numbered note's revision appears in the release ledger. A schema file is not governance unless lint checks the fields the schema says are required. A generated surface is not a front door if its size makes readers skip it. A current-note guard is not maintenance if it forces a self-audit note to masquerade as an applied case packet.

The concrete break was small but severe: notes `956` and `957` were present, metadata marked them as `rev0761`, source keys and tests existed, and `make lint` passed; yet `INDEX.md`, `CHANGELOG.md`, and `generated/RELEASES.json` skipped `rev0761`. That means the datacube could reconstruct the notes but not the release. This note records the fix and adds a guard so the same kind of release-lineage dropout fails in later revisions.

## Pattern pack

### 1. No release by current index head

A current revision block can be clean while a prior revision disappears from `INDEX.md` and `CHANGELOG.md`. The repair is to compare all revisions present in `generated/ARCHIVE_INDEX.json` with all revisions emitted in `generated/RELEASES.json`, then verify that each release lists exactly the archive files whose metadata carries that revision.

### 2. No schema by schema file

The package carries JSON schemas, but a schema file only matters if lint enforces the same invariant or a validation pass is run. The observed failure was `GAP-013-child-protection-foster-care-placement-and-family-continuity`: its schema requires `affected_parties`, but the metadata row lacked that field and still passed lint. The low-risk repair is direct: require a non-empty `affected_parties` array in the gap-ledger lint loop.

### 3. No maintenance by fake matrix coverage

The current matrix guard was intended to stop fresh substantive packets from shipping without operational tests. It should not apply to self-audits, source repairs, method notes, or release-lineage notes. Otherwise the archive will manufacture a test-matrix relationship just to make a maintenance revision pass. The repair is to scope the matrix requirement to current notes whose class is `policy_docket` or `applied_case_packet`.

### 4. No generated front door by bulk

`generated/GENERATED_SURFACE_AUDIT.md` already flags the correct pressure: more than one hundred generated files and more than ten megabytes of generated surfaces. That does not mean generated files should be deleted. It means the archive should increasingly distinguish compact reader routes from machine/debug surfaces, and should compress or split `SOURCE_HEALTH`, `SOURCES`, `CONTROL_SURFACES`, `ARCHIVE_INDEX`, `LIFECYCLE_GATES`, and `THREADS` when they become default reading paths by accident.

### 5. No source currentness by source-key presence

The source-key registry is broad, but hundreds of historical source keys still lack manual source-health rows. That is acceptable only if the absence remains visible. The right repair is not network-dependent lint. The right repair is a scheduled source-health backfill queue, priority by volatility and public-service consequence, and explicit fallback/supersession fields for current or fast-changing sources.

### 6. No consumer-finance continuity by regulator row

Online checks reaffirm the consumer-finance packet's direction: complaint databases, FDIC banked/underbanked denominators, Regulation E clocks, OCC complaint routes, refund trackers, and offset programs are all useful lanes, but none proves money restored, account usable, credit corrected, debt withdrawn, or downstream public-service continuity. The archive should keep joining source rows to household outcomes.

## Failure modes

- **Release-lineage dropout**: archive notes and metadata exist, but a revision is absent from `INDEX.md`, `CHANGELOG.md`, and `generated/RELEASES.json`.
- **Schema theater**: a schema declares required fields, but lint validates a smaller hand-coded subset.
- **Maintenance coercion**: a self-audit revision is forced to borrow an unrelated operational matrix instead of being allowed to repair the package.
- **Generated-surface obesity**: source and routing files become so large that readers treat them as black boxes or avoid them entirely.
- **Manual source-health opacity**: source-key presence is mistaken for currentness, even when the generated source-health surface marks many keys as unclassified.
- **Consumer-finance row capture**: CFPB, FDIC, Regulation E, OCC, IRS, and Treasury rows are treated as remedies instead of evidence lanes.

## Anti-theater tests

1. Does every revision named by archive metadata appear in `generated/RELEASES.json`?
2. Does each release list exactly the numbered archive notes whose metadata says they belong to that revision?
3. Does gap-ledger lint enforce the fields that the schema marks as required, especially `affected_parties`?
4. Can a maintenance-only current revision pass without inventing a fake case packet or test matrix?
5. Do generated-surface warnings identify both file count and byte pressure before they become first-reader failure?
6. Can a reader distinguish a registered source key from a manually checked source-health row?
7. Are volatile sources, complaint portals, refund tools, and regulator pages reviewed on a cadence rather than trusted because they once resolved?
8. Does the consumer-finance packet join complaint, account, report, debt, error, payment, and household outcome states before declaring remedy?

## Corrections shipped in this revision

- Restored the missing `rev0761` entries in `INDEX.md` and `CHANGELOG.md`, so `generated/RELEASES.json` can see notes `956` and `957` again.
- Added a release-lineage lint guard that compares archive-index revisions against generated release rows and fails on missing or mismatched release notes.
- Added a non-empty `affected_parties` check to gap-ledger lint and repaired the missing field on `GAP-013`.
- Scoped the current operational-matrix requirement to current substantive notes, allowing maintenance-only revisions to remain honest.
- Added `GAP-026` as the repaired release/schema maintenance gap and `GAP-027` as the open maintenance queue for generated-surface compaction and historical source-health backfill.

## What should change over time

The best next repair is a compact-reader layer: keep the heavy generated JSON for reproducibility, but add smaller route files that answer the first-reader questions without opening megabyte-scale indexes. After that, backfill manual source-health rows for the highest-volatility historical source keys and make unclassified source keys sort to the top of maintenance queues. The code cleanup should be opportunistic: `tools/lint_archive.py` still carries long hand-written test-matrix validation blocks even though `COMMON_TEST_MATRICES` and `validate_test_matrix_pair` exist; remove those copy-forward blocks when touching that area again.

The consumer-finance domain also deserves follow-on packets for account-screening systems, deposit holds and account freezes, garnishment/levy, BNPL and earned-wage-access rails, cash-app/mobile-wallet disputes, remittances, bank-failure/receivership continuity, and state debt-collection or tenant-screening interactions. Those are adjacent to the current packet but not fully joined yet.

## Source posture

This note reuses existing source keys rather than adding another source registry layer. The external posture is simple: CFPB complaint surfaces show complaint routing and response lanes, FDIC survey materials show banked and underbanked denominators, Regulation E and prepaid-account rules show error-resolution duties, OCC pages show national-bank complaint routing, IRS filing/refund pages show filing-scale and refund-status lanes, and Treasury Offset Program pages show offset mechanics. None should be read as proof of completed person-level remedy without joined outcome evidence.
