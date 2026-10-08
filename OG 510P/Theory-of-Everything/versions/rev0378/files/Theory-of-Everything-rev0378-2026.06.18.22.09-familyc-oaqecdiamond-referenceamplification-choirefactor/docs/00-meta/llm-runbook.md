# LLM runbook

## Before making changes

Read:
- `README.md`
- `START_HERE.md`
- `docs/00-meta/archive-policy.md`
- `docs/00-meta/canonical-homes.md`
- `docs/20-constitution/claim-registry.md`
- `docs/20-constitution/invariant-registry.md`
- `docs/20-constitution/open-question-registry.md`
- `docs/30-program/workstreams.md`
- `docs/00-meta/bibliography.md`
- `docs/10-method/source-admission-and-eviction-sieve.md`

## Preferred revision pattern

1. Reopen the current state.
2. Treat the compact exact `START_HERE.md` restart mirrors as one family. When a member source changes, regenerate that family block in the same revision through `make index` and preserve lint coverage against its canonical source(s); keep member-specific exactness in the shared tooling mirror-spec table rather than per-mirror policy prose, ad hoc parity branches, or hand-edited drift.
3. Add a new restart-mirror family member only if its source is compact, continuation-critical, and removes real restart rediscovery rather than replaying another stable surface.
4. Choose the move class, then find the canonical home before adding or expanding any surface.
5. Keep `ARCHIVE_INDEX.md` as the sole curated navigator; leave raw coverage to `ARCHIVE_INDEX.generated.md`.
6. Add or refine one canonical surface, then update the affected registry or workstream, evict any bibliography entry left without a live canonical citation home, and merge any same-source parallel `REF-####` ids back into one surviving anchor.
7. Prune `FOLLOWTHROUGH-QUEUE.json` to active-only state; leave it empty when no active move is earned.
8. Demote trigger-only reopen conditions into `standby-threshold` state instead of leaving them active in the queue or assumption ledger.
9. If the queue is empty, leave only durable standing assumptions active and compress satisfied tactical chains into grouped retired phase history.
10. If a lane is standby-only, keep program-surface status at claim-level posture; do not route its direct audit file paths through workstream / frontier mirrors unless that lane is being touched directly.
11. If a lane is closed and the queue is empty, strip faux-forward `next best move` narration and explicit queue-state commentary out of canonical stop-rule surfaces and leave only admissibility, stop rule, and reopen threshold.
12. If a lane is closed and the queue is empty, keep canonical audits substantive but remove old queue-closing narration such as `closes the next queue item`; preserve the tests, not the stale task voice.
13. If the queue is empty and a lane is standby-only, keep entry/status/program surfaces at claim, threshold, or preservation level; leave detailed routing in canonical lane homes or targeted deepen notes, and keep global queue-state narration out of individual lane summaries.
14. Keep closed-lane standby material out of fixed continuation tiers and broad deepen buckets unless that lane is being touched directly.
15. Keep `context-pack.json` semantically honest: counts must match durable ledgers, priority slices must name themselves as slices, warnings should stay a compact high-risk subset, rebuild commands should stay a compact exact subset backed by `Makefile`, and assumption-state summaries should stay compact exact summaries backed by `ASSUMPTION-LEDGER.json`.
16. Keep `CHANGELOG.md` terse and `REVISION-RECEIPT.json` at durable-rationale core only: summary, revision kind, packaged-release state, scope state, and upstream bundle anchor. Leave canon-addition prose, touched-surface lists, and repeated check logs out once canon and grouped history already carry them.
17. Keep volatile release identity only in `RELEASE-MANIFEST.json`; keep the manifest, upstream bundle chain, working-tree root, and packaged zip aligned, except for the compact exact `START_HERE.md` current-release-identity mirror when lint-enforced.
18. Keep the release tree transient-free; do not ship `__pycache__/`, `.pyc`, swap files, or other build scratch.
19. Keep mature core and program surfaces summary-level: do not replay mini-phase narratives, subclass stacks, or identical wired-doc routing once those are absorbed into canon.
20. If a consecutive claim run shares a fixed-condition scaffold, lane-routing note, or reference tail, hoist that material into one shared lane note; if the same run shares more than one of those elements, merge them into one shared lane note and let each claim keep only the new discriminator or posture delta.
21. Do not widen broad-credit control by default; if a new meta split is proposed, it must block a distinct inflation step, change a live theory verdict, and pay for itself by shortening mirrors.
22. If stable, restart, or program surfaces need the archive's default current-head architecture, route through `docs/40-model/current-head-control-router.md` rather than replaying `spine.md`, `cross-family-pressure-router.md`, `empirical-contact-burden-router.md`, and `broad-toe-credit-router.md` as separate obligations.
23. Outside `docs/40-model/spine.md` and `docs/10-method/compression-and-deduping-protocol.md`, route broad-credit stops through the canonical broad-credit router rather than replaying the completion, three-book, cosmology, witness, and family-C control surfaces separately.
24. If broad witness-package pressure is the issue, route through `docs/40-model/witness-package-burden-router.md` rather than naming subordinate witness surfaces separately in restart or program bullets. Keep stage-order details and pairwise gate-family scaffolding in their subordinate canonical homes, and do not let the three-book split or workstream summaries regrow the full witness ladder inline.
25. Before minting a new router, test it against `docs/10-method/router-economy-and-demotion-rules.md`: it should absorb multiple already-live subordinate surfaces, shorten broad continuation surfaces, and give one clearer ordered route than the loose bundle it replaces.
26. If a router stops buying real compression, demote it instead of preserving stale indirection. Broad mirrors should name the highest router that actually matches the burden in play, not stack parent and child routers by habit.
27. For pairwise witness-package closure gates, keep each gate at pair-specific delta, test, failure modes, and current scoring readout rather than cloning the same archive-level preamble across the gate family.
28. If an archive-control claim or open question changes whether canon may grow, route, or reopen, reflect it in both `START_HERE.md` and `context-pack.json` in the same revision.
29. Run `make index` to refresh the generated restart-mirror family block and raw filesystem index, then run lint, emit the revision receipt, and package.

## Hard constraints

- No retained PDFs in release bundles.
- No giant quotes.
- No duplicate conceptual homes.
- No parallel `REF-####` ids for the same source.
- No promotion of a claim without explicit basis.
- No pretending a framework label explains anything by itself.

## Research posture

When uncertain, prefer:
- sharper invariants,
- clearer bridge tests,
- smaller summaries,
- and more honest abstention.

## Restart-mirror family rule

Treat the compact exact `START_HERE.md` restart mirrors as one shared archive-control family rather than restating the same parity invariant once per section.
When a family source changes, refresh the generated family block in the same revision and preserve lint coverage against its canonical source(s); member-specific formatting can vary, but the rule stays generic and tooling should carry those details through one shared declarative mirror-spec table.
Add a new family member only if the source is compact, continuation-critical, and removes real restart rediscovery rather than replaying another stable surface.

## Router-economy rule

If you are tempted to add a new router, stop first and run the test in `docs/10-method/router-economy-and-demotion-rules.md`. A new router is earned only if it absorbs multiple already-live subordinate surfaces, shortens broad continuation surfaces, and clarifies one ordered burden route. If those gains are not real, keep the change in an existing router or subordinate home instead.

If a router no longer shortens continuation, demote it. Broad mirrors should name the highest router that actually matches the burden in play, not a parent plus child stack unless the revision is changing both levels directly.

## Current-head routing rule

If you are touching the archive's default current-head architecture, route through `docs/40-model/current-head-control-router.md` first, then open only the subordinate head surface you are actually changing. Do not restate `spine.md`, `cross-family-pressure-router.md`, `empirical-contact-burden-router.md`, and `broad-toe-credit-router.md` as separate restart or program bullets, and do not stack the parent current-head router with those child routers in broad summaries unless the revision is changing the child lane.

If you only need broad bridge-family comparison pressure, route through `docs/40-model/cross-family-pressure-router.md` rather than replaying `candidate-bridges.md`, `invariant-matrix.md`, and `discriminator-wedges.md` as separate bullets.

## Router topology map rule

When the question is parent/child router ownership or which subordinate lane should open next, consult `docs/00-meta/router-topology-and-scope-map.md` rather than re-explaining router trees inline. `ROUTER-TOPOLOGY.json` is the machine-readable parent→child and child-order source for lint and should be updated in the same revision when hierarchy ownership changes or a router's ordered route changes. Keep router docs focused on local burden order and stop rules; let the topology map carry the standing parent→child picture.

## Broad ToE credit routing rule

If you are touching the archive's integrated broad-credit architecture, route through `docs/40-model/broad-toe-credit-router.md` first, then open only the subordinate lane you are actually changing. Do not restate the completion-bid credit stack, the three-book split, the vacuum-energy burden router, the witness-package burden router, and the current-family readout router as separate restart or program bullets.

## Witness-package routing rule

If you are touching observer / record minimum, witness borrowing, and witness-package pressure together, route through `docs/40-model/empirical-contact-burden-router.md` first, then open only the subordinate empirical-contact surface you are actually changing. Do not restate those three broad surfaces separately in restart or program mirrors.
If you are touching witness-package debt / borrowing / closure pressure broadly, route through `docs/40-model/witness-package-burden-router.md` first, then open only the subordinate surface you are actually changing. Do not restate the borrowing ladder, stage stack, and shared gate-family frame separately in restart or program mirrors, and do not let the three-book split or workstream summaries smuggle the full witness ladder back in by prose. For pairwise witness-package gates, point shared empirical-contact prerequisites through `docs/40-model/empirical-contact-burden-router.md` plus `docs/40-model/witness-closure-gate-family-frame.md` rather than listing the record-minimum and borrowing surfaces in every gate.

## Family-B routing rule

If you are touching broad thermodynamic-gravity / family-B pressure, route through `docs/40-model/family-b-burden-router.md` first, then open only the subordinate family-B audit or gate you are actually changing. Do not restate the equilibrium assumption audit, non-equilibrium trace map, witness-climb audit, and beyond-equilibrium gain gate as separate restart or program bullets.

## Family-C stack routing rule

If you are touching broad family-C witness-ceiling or identifiability pressure, route through `docs/40-model/family-c-burden-router.md` first, then open only the subordinate surface you are actually changing. If you are touching only family-C screen order, route through `docs/40-model/family-c-identifiability-stack.md` plus the specific current screen you are actually changing; do not restate the whole family-C chain in restart or program mirrors.

## Vacuum-energy proposal-class routing rule

If you are touching cosmological-constant / vacuum-energy proposal-class pressure, route through `docs/40-model/vacuum-energy-burden-router.md` for broad control, then the specific current audit you are actually changing; do not restate the debt split, proposal-class stack, and audit-family frame as separate restart or program bullets, and keep `docs/40-model/measure-population-typicality-audit.md` on its explicit standby-only route unless that lane is directly touched.

## Completion-bid comparison stack routing rule

If you are touching broad completion-bid control, route through `docs/40-model/completion-bid-credit-stack.md` first, then open only the subordinate surface you are actually changing. If you are touching only post-cash-out completion-bid comparison pressure, route through `docs/40-model/completion-bid-comparison-stack.md`, `docs/40-model/completion-bid-comparison-gate-family-frame.md`, and the specific current gate you are actually changing; do not restate the whole recovery → fixation → portability → prediction → discrimination → acquisition → attribution → ranking → allocation → retirement → exclusion → salvage → import → assimilation → convergence → closure ladder in restart or program mirrors, and do not clone shared family preambles across the gate docs.
