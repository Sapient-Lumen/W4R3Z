# Compression and deduping protocol

## Compression rule

When several documents explain the same concept, keep the one that best preserves:
- the canonical definition,
- the current status,
- the decisive citations,
- and the next discriminating move.

Delete or merge the rest.

## Dedupe rule

If a concept appears in more than one location, one location is canonical and the others should only point to it.

## Anti-bloat rule

Before adding a new document, ask:
- Could this be a registry entry instead?
- Could this be one section added to an existing canonical doc?
- Could this be a one-line addition to the trajectory map or workstream?
- Could this live in quarantine rather than canon?

## Maintenance rule

If a concept changes home, update `docs/00-meta/canonical-homes.md` in the same revision. The archive stays small by keeping routing current, not by hoping future editors remember it.

## Broad-credit extension rule

Do not extend the downstream completion-credit ladder by default.
A new tail gate belongs in canon only if **all** of the following are true:
- **Separability:** it blocks a distinct inflation step that is not already handled cleanly by the predecessor gate.
- **Live scoring effect:** it would change how at least one live completion bid, bridge comparison, or archive verdict is actually scored right now.
- **Compression payoff:** adding it lets mirror surfaces get shorter or more honest because they can route to one sharper debt instead of replaying examples.

If one of those tests fails, keep the candidate issue as:
- an example inside the current gate,
- a registry note,
- or an open question,
rather than widening canon with another full surface.

The archive's current broad-credit stop is the physics-native three-book split in `docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md`. Further downstream meta ideas remain admissible, but they should stay non-canonical until they change live theory scoring and actually compress the archive.

## Router-economy rule

When a revision is tempted to add a new router, test it against `docs/10-method/router-economy-and-demotion-rules.md` before widening canon. A router belongs only when it absorbs multiple already-live subordinate surfaces, shortens broad continuation surfaces, and gives one clearer ordered route than the bundle it replaces. If those gains are not real, keep the change inside an existing router or subordinate canonical home.

If a router no longer buys real compression, demote it rather than preserving stale indirection.

## Mirror-locality rule

For the spine-routed completion-credit ladder, exact rung sequencing and tail-growth tests live in `docs/40-model/spine.md` and this file.
Outside those homes, mirrors should name only:
- the router (`docs/40-model/spine.md`),
- the current broad-credit stop (`docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md`).

Do not restate long intermediate gate stacks in mirrors unless the touched revision is actually changing that part of canon.
For broad witness-package control, keep the borrowing ladder, stage order, and shared gate-family scaffolding routed through `docs/40-model/witness-package-burden-router.md` rather than scattering them across mirrors. That includes the three-book stop rule and workstream summaries: they may name the witness lane, but they should not replay the whole closure ladder inline. For pairwise witness-package closure gates, keep shared gate-family scaffolding in `docs/40-model/witness-closure-gate-family-frame.md`, route broad empirical-contact prerequisites through `docs/40-model/empirical-contact-burden-router.md`, and let each gate keep only its pair-specific inflation move, test, and failure modes.
For pairwise post-cash-out completion-comparison gates, keep shared gate-family scaffolding in `docs/40-model/completion-bid-comparison-gate-family-frame.md` and let each gate keep only its pair-specific inflation move, test, failure modes, and current readout.


## Restart-surface parity rule

If an archive-control claim or open question changes whether canon may grow, route, or reopen, expose it in both `START_HERE.md` and `context-pack.json` in the same revision.
Do not leave archive-growth governance visible only inside registries or a single canonical method surface.
Otherwise the archive keeps the rule in canon while hiding it from the handoff surfaces that future continuation actually follows.

## Restart-mirror family rule

If `START_HERE.md` carries a compact exact mirror of a compact, continuation-critical machine / status / receipt / manifest surface, refresh that mirror in the same revision whenever its source changes through the shared generated path and keep it lint-verified against the canonical source(s).
The current restart-mirror family covers restart tiers, current posture, priority restart open questions, operator warnings, followthrough / standby state, assumption state, rebuild commands, entry surfaces, public head status, current revision delta, and current release identity; tooling should carry their member-specific exactness through one shared declarative mirror-spec table and one shared generated family block.
Member-specific formatting can vary — for example inclusive OQ ranges or secondary checks against `Makefile` or `ASSUMPTION-LEDGER.json` — but the family rule stays generic and the mirror-spec table should carry those details instead of repeated control prose or bespoke parity branches.
Add a new family member only if the source is compact, continuation-critical, and removes real restart rediscovery rather than replaying another stable document.
Otherwise the archive bloats control docs by restating the same parity invariant once per mirror.
