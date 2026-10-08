# Session deep audit — rev0292

This memo records the current working diagnosis for the datacube. It is intentionally not a new moral theory layer. It is a maintenance queue: what is missing, what should change, what looks wasteful, and what can be corrected over time.

## Immediate status

The inherited rev0291 release gate passed. That matters: route records, source-currentness references, remedy profiles, case contracts, policy-action profiles, actor-accountability profiles, local links, local source references, and scorecard rendering were structurally valid.

The pass was still too forgiving in two places. First, handoff surfaces could remain stale even while machine profiles passed. Second, `MANIFEST.json` only had to be compact JSON; it did not have to match the live file list and hashes. Rev0292 fixes those two defects.

## Corrected in rev0292

- `START_HERE.md` no longer opens as the prior policy-action release.
- `README.md` no longer describes the prior release inside the current-release change list.
- `ARCHIVE_INDEX.md` now points at the rev0292 maintenance pass and the deep-audit memo.
- `docs/README.md` no longer opens as an older cube-hardening release.
- `Makefile` now rebuilds `MANIFEST.json` before the release gate checks it.
- `tools/check_archive.py` now reconstructs the expected manifest from the live archive and compares file paths, byte counts, SHA-256 hashes, and root name.
- Active audit-report pointers in `cube-index.json` now point to rev0292 report filenames.

## High-priority missing pieces

### 1. Actor-accountability profiles need less placeholder language

The actor-accountability layer is structurally present for every route, but much of it is still generic. The most important examples are `beneficiary_or_rent_recipient_to_trace`, `burden_bearer_to_be_identified`, and the single repeated `evidence_required` packet. These are useful scaffolds, but they are not yet route-specific accountability answers.

Next correction: split actor profiles into archetypes plus route-specific overrides. Then require each route either to name a concrete beneficiary and burden bearer or to mark why that field is genuinely unknowable at design time.

### 2. Axis vocabulary is too close to prose-label sprawl

The cube has 23 required axes and over two thousand declared axis values. Several large axes have many singleton values. That makes the cube expressive, but it also makes it less cube-like: a value used once is closer to a local note than a reusable axis category.

Next correction: move singleton or near-singleton values into `route_tags` or `route_notes`, and reserve axis vocabularies for reusable distinctions. The target should be stable high-signal axes, not a taxonomy that grows one label per new memo.

### 3. Size thresholds are being satisfied too narrowly

Several guarded files sit within a few bytes of their ceiling. That is not a functional failure, but it is a smell: the archive is optimizing to pass a byte limit rather than becoming simpler. The biggest examples are the calibration frontier map, the founding ideal-taxation answer, default stack, and AI exceptional levy route.

Next correction: add a soft-warning or planning report for files above 90 percent of their ceiling, then prune repeated route-callout language into shared tables.

### 4. The manifest had release-theater risk

Before rev0292, `MANIFEST.json` could be stale and still pass if it was compact JSON. That undermined the promise that the manifest was the exhaustive inventory with hashes.

Corrected now: the checker computes the expected manifest directly from the live tree. Future edits that forget to rebuild the manifest should fail.

### 5. The archive needs a real packaging target

`make package` checks readiness but does not create a zip. This session creates a zip outside the Makefile to satisfy the linked-revision workflow. The Makefile should eventually gain an explicit zip target that names the archive using the required pattern.

Next correction: add a target or script that derives `Project-Name-rev####-YYYY.MM.DD.HH.MM-codename.zip` from `RELEASES.json` and verifies that the filename, root folder, `VERSION`, receipt, and manifest agree.

### 6. Currentness review should be calendar-driven, not memory-driven

The source-currentness registry is disciplined, but it should be turned into an actionable queue. The nearest dates are quarterly universal-service factors, filing-season free-file/refund rails, payment-transition guidance, BOI final-rule status, CBAM implementation status, Maryland digital-ad-tax litigation, worker-classification rulemaking, and OECD global-minimum-tax implementation.

Next correction: add a `tools/currentness_due.py` report that lists sources due within 30, 60, and 90 days and writes a machine-readable refresh queue.

## Medium-priority compaction path

1. Create `axis-archetypes.json` for reusable controlled vocabulary.
2. Move long one-off values out of axes and into route-local tags.
3. Convert repeated actor-accountability evidence packets into shared archetype IDs.
4. Convert repeated policy-action and remedy boilerplate into archetype IDs plus route overrides.
5. Add a profile-density audit that flags fields with very low uniqueness or excessive placeholder use.
6. Add a stale-orientation audit for all top-level handoff files, not only README and START_HERE.
7. Add a packaging audit for filename/root/VERSION/receipt/manifest agreement.

## What not to do

Do not add another prose layer to explain the prior prose layer. The next gains should come from reducing repeated local text, normalizing axis vocabularies, and turning hidden assumptions into small executable checks.

