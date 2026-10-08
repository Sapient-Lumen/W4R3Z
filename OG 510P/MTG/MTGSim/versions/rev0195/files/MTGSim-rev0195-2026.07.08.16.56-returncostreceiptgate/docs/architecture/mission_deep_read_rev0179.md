# rev0179 mission deep read — mission audit shard cap

## Heart of the mission

The heart is **trusted transitions**: one authoritative `GameState` plus one explicit legal choice should produce one deterministic next state and enough typed evidence to validate, replay, branch, fuzz, search, and explain that transition.

This project should not try to beat mature MTG engines by racing to script every printed card. The stronger lane is an auditable reducer core: legal-action frontier, choice queues, typed receipts, state checkpoints, replay bundles, scenario fixtures, fuzz probes, and rule-linked reports. The outside world already has broad card/rules engines; MTGSim's value is making each semantic transition inspectable and reproducible under short cloudtainer budgets.

## What is already good

- Revision practice is disciplined: new semantics land as a narrow seam plus typed record fields, validators, corruption tests, docs, ledger rows, reports, and package evidence.
- The evidence spine is unusually rich for a small engine: `ActionReceiptRecord`, `ActionTraceEntry`, `TransitionResult` seals, `StateCheckpointSeal`, event-spine records, stack placement/resolution records, damage/life/counter/mana/draw/discard records, and replay-bundle diagnostics.
- The harness is aligned with cloudtainer work: deterministic discovery, sharding, budgets, JUnit/JSON/SQLite reports, and report histories.
- rev0178's immediate damage/life result link was the right kind of change: it converted event adjacency into a typed backlink/range contract.

## What is missing

1. **Rules-source refresh/diff as a first-class revision.** The official-rules metadata still remains pinned to 2026-04-17 while online observations record a newer 2026-06-19 Comprehensive Rules source. The current policy of not bundling official rules text is correct; the missing thing is a private-cache diff workflow that maps changed rule IDs to ledger rows, owners, tests, and release notes before more rule breadth is claimed.
2. **Semantic transaction kernels.** Paid actions are much better than before, but replacement/prevention choice, APNAP simultaneous choices, combat declaration batches, and full spell/ability declaration-cost-resolution lifecycles still need reusable proposal/lock/pay/commit/rollback kernels instead of per-seam receipt accretion.
3. **Counterexample shrinking.** Random legal walks are useful, but the next evidence class should emit minimal replay bundles for failures and, eventually, coverage-guided or mutation-guided fuzzing. A failing fuzz seed should become a compact scenario or action trace automatically.
4. **External card-data importer boundary.** The local sample catalog has 56 cards. Scryfall and MTGJSON are card-data sources, not rules authority. The importer boundary should be explicit: external data can populate card identity/oracle-like fields, but MTGSim semantics must remain typed, tested, and rule-ledger-owned.
5. **Monolith decomposition at proven seams.** `src/engine.cpp`, `src/validation.cpp`, and `tests/cpp/test_engine.cpp` are now large enough that compile-time policy has become architecture. Split only where ownership seams are proven: state hashing/replay, damage/life/counter records, payment transactions, replacement effects, APNAP choice queues, and legal-action frontier.

## What should change next

The next high-leverage sequence should be:

1. Rules refresh/diff revision against the current official rules source, keeping the text cache private and committing only metadata hashes/diffs/ledger updates.
2. A small semantic transaction kernel for replacement/prevention/APNAP choices, with one public proposal object, one choice declaration, one result receipt, and rollback proof.
3. Counterexample shrinker: fuzz failure -> replay bundle -> minimal suffix trace -> scenario fixture suggestion.
4. Card import contract: add Scryfall/MTGJSON importer stubs that generate card definitions marked `semantic_status=metadata_only` until engine behavior is explicitly implemented.
5. Decompose the biggest translation units after the above seams stabilize; do not split just to make smaller files if it will hide transaction coupling.

## What has gone wrong or wasteful

### Concrete cloudtainer waste corrected in rev0179

The matrix planner was still using raw `os.cpu_count()` to suggest local shards. In this cloudtainer that is `56`, while the runners already use `MTGSIM_AUTO_JOBS` / `MTGSIM_SANITIZE_AUTO_JOBS` caps to avoid runaway subprocess fan-out. That produced a misleading `target_shards=56` plan for roughly 451 work units and about six seconds of estimated work. rev0179 changes the planner to use the same auto cap as the runners and changes the harness so it does not force CPU-count target shards unless the caller explicitly requested sharding.

### Correctable over time

- **Report duplication dominates the uncompressed datacube.** `reports/` is about 85.7 MiB uncompressed out of about 94.3 MiB. This is not automatically wrong because evidence is the product, but it needs a retention policy: keep current rev-specific reports, compact histories, and perhaps an optional `evidence-full` bundle when deep history matters.
- **The ledger coverage number can mislead.** The ledger-weighted percentage is high, while the conservative full-rules proxy is much lower. Always show them together; one measures local roadmap completion, the other reminds us that Magic is vast.
- **Proof machinery can outrun semantics.** Earlier notes already caught this: field-level witnesses are useful only when attached to a real semantic boundary. The next revisions should prefer transaction kernels over adding another isolated hash/backlink.
- **Official rules freshness is a recurring gap.** The no-redistribution policy is good, but the metadata lag should become a gated workflow rather than a repeated note.
- **Front-door docs carry too much revision history.** README/CHANGELOG are useful as audit surfaces, but the actual project guide should eventually point to a compact mission page plus latest artifact report, with old anchors moved into archive docs.

## Online grounding and speculation

- Wizards' rules page describes the Comprehensive Rules as a reference for all rules and corner cases, not a document meant to be read end-to-end. That supports MTGSim's approach: rule IDs, focused fixtures, and diff-driven maintenance rather than a monolithic manual rewrite.
- Scryfall and MTGJSON provide strong data pipelines, including bulk/card data; they should feed card identity/catalog/import work, not silently define engine semantics.
- Forge and XMage already demonstrate broad open-source rules/card coverage. MTGSim's differentiator should therefore be proof-carrying simulation, not raw implemented-card count.
- Academic complexity results around Magic suggest humility: some Magic questions are computationally extreme, and even legality/forced-outcome reasoning can be hard. MTGSim should make boundedness and unsupported surfaces explicit rather than implying complete play solving.

## rev0179 implementation note

Changed files:

- `tools/plan_test_matrix.py`: added auto-parallelism cap helpers and applied them to C++ and scenario shard suggestions.
- `tools/harness.py`: stopped passing raw CPU-count `--target-shards` when no explicit shard count was requested.
- `tests/python/test_manifest.py`: added a small guard proving release/sanitize shard suggestions respect `MTGSIM_AUTO_JOBS` / `MTGSIM_SANITIZE_AUTO_JOBS`.
- `docs/architecture/mission_deep_read_rev0179.md`: this note.
- Metadata/report surfaces updated to `rev0179`.
