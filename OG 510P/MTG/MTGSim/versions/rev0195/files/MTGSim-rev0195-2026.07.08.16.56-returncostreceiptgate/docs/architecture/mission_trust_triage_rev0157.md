# MTGSim rev0157 — Mission Trust Triage

## Heart of the mission

MTGSim is not trying to be a card encyclopedia, deckbuilder, rules-text mirror, or UI-first game client. The heart is **trusted transitions**: given an authoritative game state and an explicit legal choice, produce exactly one deterministic next state plus typed evidence that another process can validate, replay, branch, fuzz, search, and explain.

That mission makes the transition boundary more important than broad card count. A good revision should make one previously ambiguous mutation more replayable, challengeable, and rollback-safe. rev0156 did that narrowly for selected-mode contract hashes. rev0157 records the next deeper seam instead of adding another field-only receipt.

## What is missing

The current spine is evidence-rich but still transaction-poor. The next kernel needs a first-class declaration/payment object that captures announcement choices before costs are paid:

1. `ChoiceDeclarationRecord` for mode, target, X, alternate/additional costs, divisions, ordering, optionality, and controller choices as one typed pre-payment declaration.
2. A staged paid-action transaction with named declaration, cost-lock, mana-production, mana-payment, nonmana-cost, stack-placement, rollback, and receipt phases.
3. A total-cost plan that distinguishes mana costs, tap costs, sacrifice costs, counters/loyalty costs, additional/alternative costs, cost increases/reductions, and unpayable failures.
4. Explicit replacement/prevention/trigger-order choice protocols, not only deterministic defaults.
5. A research-agent API boundary with stable action schemas, observation/information-state views, chance nodes, reversible branching, and returns/rewards.
6. Coverage-guided fuzzing and semantic counterexample shrinking as a separate evidence class from randomized legal walks.
7. A rules-source refresh path: the bundled metadata is still pinned to the 2026-04-17 Comprehensive Rules source, while the online official Comprehensive Rules observed for this triage are effective 2026-06-19.

## What should change next

The next code-bearing revision should stop patching one more `EventRecord` field and instead introduce a typed declaration/cost-plan seam. The smallest useful vertical slice is a paid cast that declares mode/targets, locks a total cost, attempts payment, proves rollback on failure, and emits exactly one causal receipt only after success.

Acceptance should include at least one failed paid cast whose original card zone, stack, tapped permanents, mana pool, journal count, stack-placement records, and action receipts are unchanged; and one successful paid cast whose declaration, cost plan, payment witnesses, stack placement, and transition receipt all cross-check.

## Things that went wrong or wasteful in this cloudtainer

- **Generic latest aliases drifted.** `reports/audit/datacube_audit_latest.json` in the rev0156 archive pointed at rev0155. `reports/audit/datacube_audit_latest.stdout.json` and `reports/rules/rules_progress_latest.json` were older still. Revision-specific reports were more reliable than generic latest aliases.
- **Cache artifacts entered the archive.** The rev0156 audit itself reported `tools/__pycache__` entries as payload warnings. rev0157 excludes Python bytecode/cache directories from the package.
- **Scenario report paths showed stale roots.** The rev0156 scenario report included command paths under a rev0155 working directory even though the report was named for rev0156. That does not prove semantic failure, but it weakens audit trust and should be corrected by running reports from the staged root or recording explicit provenance.
- **Rules metadata is stale against the live official source.** The ledger and official manifest remain pinned to the 2026-04-17 Comprehensive Rules source until a proper refresh/diff is done. rev0157 documents the observed 2026-06-19 official source but does not silently relabel coverage.
- **The cloud budget favors monolith pain.** `src/engine.cpp`, `tests/cpp/test_engine.cpp`, `src/validation.cpp`, and `tools/audit_datacube.py` are all large enough that broad edits and broad per-case test runs are expensive. Split one proven subsystem at a time, but do not do a risky rewrite.
- **Full per-case subprocess testing can be wasteful here.** In this session the all-in-one release test binary completed all cases quickly, while the full per-case Python runner did not finish before the cloud timeout. Keep the per-case runner for diagnostics, but use all-in-one smoke plus focused per-case filters during exploratory triage.

## External research notes used for this triage

- Official Wizards rules page remains the canonical place for current rules packages; this session observed the official Comprehensive Rules PDF as effective 2026-06-19.
- Scryfall and MTGJSON both publish daily/bulk card data surfaces, so MTGSim should not spend its scarce budget trying to be the primary public card-data lake.
- Forge demonstrates the scale of a mature player-facing/card-scripted MTG engine; MTGSim should define itself as a trusted semantic kernel rather than competing directly on UI/card breadth.
- OpenSpiel is a useful comparison target for research-agent surfaces: chance, observations/information state, returns, serialization, and undo-like branching matter.
- libFuzzer-style coverage-guided fuzzing and OR-Tools-style constraint/search framing are plausible future tools for legal action generation, parser fuzzing, and combat/declaration search under explicit budget limits.

## rev0157 package posture

This is a docs/metadata/triage revision. It preserves the rev0156 code baseline, adds this mission compass, cleans package cache artifacts, updates revision identity, refreshes rule coverage/progress reports against the unchanged metadata ledger, and records a fast release-binary smoke report. It deliberately does **not** implement `ChoiceDeclarationRecord` or the staged cost-plan kernel yet.
