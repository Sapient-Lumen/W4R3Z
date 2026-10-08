# Archive policy

## Purpose

Keep the archive small enough to survive, structured enough to re-enter, and sharp enough to make real progress on unification.

## Rules

1. Prefer **citations, ids, and compact summaries** over long quotation.
2. Keep **no PDFs, transient build scratch, or other bulky artifacts** in release bundles.
3. Preserve only what changes continuation state: invariants, claims, open questions, bridge tests, load-bearing references, and compact control surfaces.
4. When a concept appears in more than one document, pick one canonical home, update `docs/00-meta/canonical-homes.md`, and link back to that home instead of duplicating substance.
5. Separate `accepted`, `inferred`, `speculative`, and `adversarial-countermodel` material.
6. Distinguish **baseline constraints** from **candidate explanations**, and distinguish **local low-energy success** from **global fundamental explanation**.
7. New documents must wire into `ARCHIVE_INDEX.md` and at least one registry or workstream; do not maintain a second manual docs-only index.
8. If a revision adds citations, record the load-bearing reason each source matters; if a revision leaves a bibliography entry with no live canonical citation home, evict it, and if the same source reappears under two `REF-####` ids, merge it back to one live anchor.
9. If a revision adds a bold idea, either attach a promotion basis or place it in quarantine.
10. If a document can be merged without loss of operative state, merge it.
11. Do not widen broad-credit control by default; a new meta-level split belongs in canon only if it blocks a distinct inflation step, changes a live theory-scoring decision, and pays for itself through mirror compression.
12. Keep every release inspectable in one sitting.
13. `FOLLOWTHROUGH-QUEUE.json` keeps only active next moves; an empty queue is valid when no active move is earned.
14. Trigger-only reopen conditions belong in canonical stop-rule surfaces or `ASSUMPTION-LEDGER.json` as `standby-threshold`, not in the active queue or active assumptions.
15. If the queue is empty, keep only durable standing assumptions active; compress satisfied tactical chains into grouped retired phase history.
16. If a lane is closed and the queue is empty, canonical stop-rule surfaces should keep only admissibility, stop rule, and reopen-threshold language; do not carry faux-forward `next best move` narration or explicit queue-state commentary.
17. If the queue is empty and a lane is standby-only, `README.md`, `SURFACE-STATUS.json`, trajectory surfaces, and program surfaces should stay at claim-and-threshold or preservation level; detailed routing belongs in canonical lane homes or explicit targeted deepen notes, and global queue-state narration should not be repeated inside individual lane summaries.
18. Closed-lane standby surfaces should not sit in default continuation tiers or broad deepen buckets; route them back in only through explicit targeted notes until continuation state changes.
19. Closed-lane canonical audits may keep their substantive test sequence, but should not narrate old passes as if they are still closing active queue items once the queue is empty.
20. `ARCHIVE_INDEX.md` is the sole curated navigator at section-and-router level; exact file coverage belongs in `ARCHIVE_INDEX.generated.md`.
21. Mature core and program surfaces should stay summary-level: do not replay phase narratives, subclass stacks, or identical wired-doc routing once canon and grouped history already carry that work.
22. If a consecutive claim run shares a fixed-condition scaffold, lane-routing note, or repeated reference tail, hoist that shared material into one lane note; if the same run shares more than one of those elements, merge them into one shared lane note and let each claim keep only its actual delta.
23. Keep `CHANGELOG.md` terse; compress older detail into grouped phase summaries once canon and revision receipts absorb operative state.
24. `REVISION-RECEIPT.json` should keep only durable rationale core fields: summary, revision kind, move class, packaged-release state, scope state, and upstream bundle anchor. Do not let it regrow canon-addition prose, touched-surface lists, or repeated check logs.
25. Summary counts and priority subsets in `context-pack.json` must match the durable ledgers and canonical registries exactly.
26. Keep volatile release identity only in `RELEASE-MANIFEST.json`; stable entry surfaces should point there rather than hardcoding bundle names or timestamps, except for the compact exact `START_HERE.md` current-release-identity mirror when lint-enforced.
27. Durable ledgers and vocabularies should be revisionless unless a revision tag itself changes continuation state.
28. The manifest bundle stem is the canonical release-root directory name; the manifest, receipt chain, working-tree root, and packaged bundle must stay mutually consistent.
29. Outside `docs/10-method/compression-and-deduping-protocol.md`, stable, restart, and program surfaces that need the archive's current theory head should name only `docs/40-model/current-head-control-router.md` unless the touched revision changes a subordinate head surface directly.
30. Outside `docs/40-model/spine.md` and `docs/10-method/compression-and-deduping-protocol.md`, mirrors that mention broad ToE credit should name only the canonical broad-credit router unless the touched revision changes a subordinate control lane directly.
31. When broad witness-package pressure is the issue, stable, restart, and program surfaces should route through `docs/40-model/witness-package-burden-router.md` rather than naming subordinate witness surfaces separately. Keep stage-order details and pairwise gate-family scaffolding in their subordinate canonical homes, and do not let the three-book split or workstream mirrors replay the full witness ladder inline.
32. Pairwise witness-package closure gates should keep only pair-specific delta, test, failure modes, and current readout rather than repeating the same archive-level background across the full gate family.
33. If an archive-control claim or open question changes whether canon may grow, route, or reopen, surface it in both `START_HERE.md` and `context-pack.json` in the same revision; growth governance should not live only in registries or a single method file.
34. Keep compact exact `START_HERE.md` restart mirrors as one shared family. When a family source changes, refresh the corresponding mirror in the same revision through the shared generated path and lint it against its canonical source(s); keep member-specific exactness in one shared tooling mirror-spec table rather than per-mirror policy tails, ad hoc parity branches, or hand-maintained mirror drift.
35. Add a new restart-mirror family member only if its source is compact, continuation-critical, and removes real restart rediscovery; do not mint one just to replay another stable surface or regrow control docs.
36. Do not mint a new router unless it absorbs at least two already-live subordinate surfaces, shortens at least two stable / restart / program surfaces or one default restart tier, and gives one clearer ordered burden route than the loose bundle it replaces. Otherwise refine an existing router or keep the change local.
37. If a router stops buying real compression — for example it now wraps one meaningful subordinate surface, duplicates a parent router, or adds more mirror text than it deletes — demote it back into its parent or subordinate home in the same revision that notices the drift.

## Salience budget

A salient archive is not the one that stores the most literature. It is the one that stores the smallest set of distinctions that still lets the next session:
- recover the real problem,
- see what is already constrained,
- see what is still live,
- and choose the next best discriminating move.

## Release discipline

Each release should preserve:
- a stable bundle name whose zip stem and internal top-level directory match,
- a revision receipt,
- a context pack,
- one curated archive index,
- a machine-readable status surface,
- an active-only next-task queue,
- one manifest-anchored release identity surface,
- revisionless durable ledgers that do not masquerade as the current head,
- no transient build artifacts in the packaged tree,
- restart tiers that do not force closed-lane standby material into every default continuation, and
- one compact `START_HERE.md` restart-mirror family aligned with its machine / status / receipt / manifest sources.

## Current-head routing rule

When stable, restart, and program surfaces need the archive's default current-head architecture, route through `docs/40-model/current-head-control-router.md` rather than separately naming `spine.md`, `cross-family-pressure-router.md`, `empirical-contact-burden-router.md`, and `broad-toe-credit-router.md`. Do not stack that parent router with its child routers in broad mirrors unless the touched revision is actually changing the child lane. Open a subordinate head surface only when the touched revision is actually changing that surface.

When stable, restart, and program surfaces need broad bridge-family comparison pressure, route through `docs/40-model/cross-family-pressure-router.md` rather than separately naming `candidate-bridges.md`, `invariant-matrix.md`, and `discriminator-wedges.md`. Open a subordinate cross-family surface only when the touched revision is actually changing that surface.

## Router-economy rule

When a revision is tempted to add another router, first test it against `docs/10-method/router-economy-and-demotion-rules.md`. A new router is earned only if it absorbs multiple already-live subordinate surfaces, shortens broad continuation surfaces, and gives one clearer ordered burden route than the bundle it replaces. If that test fails, refine an existing router or keep the change in the subordinate home instead.

If a router no longer buys real compression, demote it instead of preserving it as stale indirection. Broad surfaces should name the highest router that actually matches the burden in play, not stack parent and child routers out of habit.

## Router topology map rule

When the question is parent/child router ownership or which subordinate lane should open next, route through `docs/00-meta/router-topology-and-scope-map.md` instead of restating router trees inline. `ROUTER-TOPOLOGY.json` is the machine-readable parent→child and child-order source that lint should trust for broad-summary parent/child checks and router ordered-route parity. Archive policy, runbook, and broad router docs should keep only local stop-rule / scope guidance and let the topology map carry the standing parent→child picture.

## Broad ToE credit routing rule

When stable, restart, and program surfaces need the archive's integrated broad-credit architecture, route through `docs/40-model/broad-toe-credit-router.md` rather than separately naming the completion-bid credit stack, the three-book split, the vacuum-energy burden router, the witness-package burden router, and the family-C burden router. Open a subordinate lane only when the touched revision is actually changing that subordinate control surface.

## Witness-package routing rule

When observer / record minimum, witness borrowing, and witness-package pressure need to move together, stable, restart, and program surfaces should route through `docs/40-model/empirical-contact-burden-router.md` rather than replaying those three broad surfaces separately.
When witness-package debt / borrowing / closure pressure is the issue, stable, restart, and program surfaces should route through `docs/40-model/witness-package-burden-router.md` rather than naming subordinate witness surfaces as separate obligations. Keep stage-order details, shared gate-family scaffolding, and individual pair tests in the subordinate witness surfaces that router already names. Pairwise witness-package closure gates should route broad empirical-contact prerequisites through `docs/40-model/empirical-contact-burden-router.md` plus `docs/40-model/witness-closure-gate-family-frame.md` rather than restating the record-minimum and borrowing surfaces gate by gate. The three-book split and program mirrors may summarize the ladder at one sentence of level, but they should not relist the witness stages or gate files inline.

## Family-B routing rule

When broad live-family readout is the issue, stable, restart, and program surfaces should route through `docs/40-model/current-family-readout-router.md` rather than separately naming `docs/40-model/family-b-burden-router.md` and `docs/40-model/family-c-burden-router.md`. When the issue is only one live family, open that subordinate family router directly rather than replaying both lanes.

When broad thermodynamic-gravity / family-B pressure is the issue, stable, restart, and program surfaces should route through `docs/40-model/family-b-burden-router.md` rather than separately naming the equilibrium assumption audit, non-equilibrium observable / record map, witness-climb audit, and beyond-equilibrium gain gate. When the issue is only one bounded thermodynamic audit or gate, open that subordinate family-B surface directly rather than replaying the whole lane doc-by-doc.

## Family-C screen routing rule

When broad family-C witness-ceiling or identifiability pressure is the issue, stable, restart, and program surfaces should route through `docs/40-model/family-c-burden-router.md` rather than separately naming the witness-closure gate, identifiability stack, and cross-family readout. When the issue is only screen order, route through `docs/40-model/family-c-identifiability-stack.md` rather than replaying the whole post-partial-identification chain doc-by-doc.

## Vacuum-energy proposal-class routing rule

When cosmological-constant / vacuum-energy proposal-class pressure is the issue, stable, restart, and program surfaces should route through `docs/40-model/vacuum-energy-burden-router.md` rather than naming the debt split, proposal-class stack, and audit-family frame as separate stable-surface obligations. Keep `docs/40-model/measure-population-typicality-audit.md` on its explicit standby-only routing path unless that lane is being touched directly.

## Completion-bid comparison stack routing rule

When broad completion-bid control pressure is the issue, stable, restart, and program surfaces should route through `docs/40-model/completion-bid-credit-stack.md` rather than separately relisting the atlas, five-axis sieve, ordered comparison ladder, and shared gate-family frame. When the issue is only post-cash-out stage order, route through `docs/40-model/completion-bid-comparison-stack.md` rather than replaying the recovery → fixation → portability → prediction → discrimination → acquisition → attribution → ranking → allocation → retirement → exclusion → salvage → import → assimilation → convergence → closure ladder doc-by-doc. Pairwise completion-comparison gates should route shared scaffolding through `docs/40-model/completion-bid-comparison-gate-family-frame.md` and keep each gate at pair-specific delta, test, failure modes, and current readout.
