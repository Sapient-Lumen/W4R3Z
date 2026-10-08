# rev0045 Mission Deep Read — Rule-ID and Fuzz-Loop Audit

## Heart of the mission

MTGSim is best understood as a deterministic, auditable Magic-like rules reducer. Its core promise is not a finished tabletop client, a deckbuilder, or a race to enumerate every card. The valuable thing is the seam: given a compact state, enumerate legal choices, apply exactly one transition, preserve identity across zones, and emit evidence that lets a tester, search agent, or future Oracle adapter explain why that transition was legal.

That mission is unusually strong because it can serve three different users at once: rules developers who need regression fixtures, researchers who need reproducible action spaces, and future card-ingestion tooling that needs typed hooks before it trusts text parsing.

## What is missing

The largest missing pieces are not card count. They are semantic surfaces that make the engine trustworthy under stress:

1. A first-class event/replacement/prevention bus with last-known-information snapshots and APNAP ordering seams.
2. A reversible or at least fully audited announcement/cost/choice record, especially for casting and activation failures.
3. A projector API that returns compact observations and legal-action masks without binding the engine to one UI.
4. More target-shape vocabulary: target groups, target-change effects, copies, uncounterable spells, and ability-vs-spell counter distinctions.
5. A split between conformance fixtures and stochastic exploration so fuzzing covers many action classes rather than whichever optional loop is cheapest.

## What went wrong in rev0044

Two issues were concrete enough to fix in this revision:

* The counterspell seam was wired to `701.5`, but the current Comprehensive Rules place countering at `701.6`. Worse, `tools/audit_datacube.py` required the wrong identifier, so the audit had begun preserving the mistake.
* The release fuzz game gave `Fuzz Bear` a no-cost optional life-gain ability. That made the fuzzer spend most priority windows activating the same free action and produced a misleadingly large number of invariant checks with no attacks, blocks, or land plays in the sampled release run.

## What should change next

Near-term slices should favor rule-seam depth over breadth:

* Add a rule-source drift audit that checks the small set of hand-curated CR references against the official TXT headings when a new rules source date is declared.
* Make fuzz coverage contractual: every release fuzz profile should report action-kind mix and fail or warn when combat, land play, casting, or stack actions disappear unintentionally.
* Split `src/engine.cpp` and `tests/cpp/test_engine.cpp` along existing seams: stack/targets, combat, SBAs, layers, replacement/prevention, and projector/search.
* Keep card catalogs as metadata fixtures until their behavior is backed by typed effects, costs, replacement hooks, and target schemas.

## Speculative north star

The cloudtainer should become a conformance lab: small, deterministic rules cubes that can be replayed, minimized, compared across engines, and used by agents. Forge and XMage already demonstrate the scale of card-complete engines; MTGSim's distinctive opportunity is stricter auditability, smaller reproducible deltas, and clean machine-action interfaces.


## rev0045 corrections applied

This revision changes the code rather than only recording the critique. Counter metadata and audit probes now use CR `701.6`. Release fuzz now reports aggregate action-kind counters and uses a profile that gives the synthetic life-gain ability a tap cost, seeds hasty token bodies, prefers non-pass actions when legal, and checks blocker actions from the defending player during the declare-blockers step. The validated release fuzz aggregate for 12 seeds × 120 steps was: pass=1134, cast=27, land=29, mana=133, activated=53, attack=40, block=24.
